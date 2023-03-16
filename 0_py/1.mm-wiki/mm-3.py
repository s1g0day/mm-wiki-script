# -*- coding: UTF-8 -*-
'''
遍历获取wiki内图片存活, 需开启空间分享权限
python3 mm-3.py -u http://192.168.232.154:8080 -DM 3468 -t 3
python3 mm-3.py -u http://192.168.232.154:8080 -DM 2597-4336 -t 3
'''

import re
import sys
import json
import html
import urllib3
import datetime
import requests
import threadpool
from argparse import ArgumentParser
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def requests_test(url, config, document_id):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-TW,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # 'Cookie': 'mmwikissid=9306ece1fa5983913b1889ecf412d6a6; mmwikipassport=n8sckEYYgdC1i4aHiAiHgFQFy7hQydaGiF5ChwWcuwgZuwcQhdgHuEg=',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }

    params = {
        'document_id': document_id,
    }

    try:
        req = requests.get(url + '/page/display', params=params, cookies=config, headers=headers, verify=False)
        req.encoding = req.apparent_encoding	# apparent_encoding比"utf-8"错误率更低
        status_code = req.status_code
        if status_code == 404:
            print("error_code: ", str(status_code))
            exit()
        else:
            # print("status_code: " + str(status_code))
            return req
    except:
        print(url + "连接错误")
        exit()

def req_img_test(url, config):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-TW,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # 'Cookie': 'mmwikissid=9306ece1fa5983913b1889ecf412d6a6; mmwikipassport=n8sckEYYgdC1i4aHiAiHgFQFy7hQydaGiF5ChwWcuwgZuwcQhdgHuEg=',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }

    try:
        req = requests.get(url, cookies=config, headers=headers, timeout=8, verify=False)
        req.encoding = req.apparent_encoding	# apparent_encoding比"utf-8"错误率更低
        status_code = req.status_code
        if status_code == 404:
            # print("error_code: ", str(status_code))
            img_error = url + "连接错误"
            # print("img_error",img_error)
            return img_error
        else:
            # print("status_code: " + str(status_code))
            return status_code
    except:
        img_error = url + "连接错误"
        # print("img_error",img_error)
        return img_error


def get_image(url, config, document_id):
    # datas 存储`![]()`括号内图片地址
    datas_imgs = []
    alive_imgs = []
    # 提取图片地址
    req = requests_test(url, config, document_id)
    
    if "文档不存在" not in req.text:
        if "您没有权限访问该空间" not in req.text:
            html_text = html.unescape(req.text)
            pattern = re.compile(r'<[^>]+>',re.S)
            result = pattern.sub('', html_text)
            result = result.split("\n")
            for datas in result:
                if "](" in datas:
                    result = re.search("\!\[(?P<ext>.*?)\]\((?P<data>.*)\)", datas, re.DOTALL)
                    if result:
                        ext = result.groupdict().get("ext")
                        data = result.groupdict().get("data")
                        if data != "":
                            datas_imgs.append(data)
            # 验证图片存活
            if len(datas_imgs) != 0:
                for img_ink in datas_imgs:
                    if "http://" in img_ink or "https://" in img_ink:
                        alive_img = img_ink
                    else:
                        # 本地图片验证
                        alive_img = req_img_test(url+img_ink, config)
                         
                    if alive_img != 200:
                        alive_imgs.append(alive_img)
                if len(alive_imgs) == 0:
                    print("\n文档ID: " + str(document_id) + ", success")
                else:
                    errot_text = "\n文档ID: " + str(document_id) + ", 存在外链"
                    error_imgs.append(str(document_id))
                    print(errot_text)
                    
                    with open('http_imgs.txt','a+') as f:
                        f.writelines(errot_text + "\n")
                        for img in alive_imgs:
                            f.writelines(img + "\n")
            else:
                print("文档ID: " + str(document_id) + ", 无图片")
                no_imgs.append(str(document_id))
        else:
            print("文档ID: " + str(document_id) + ", 您没有权限访问该空间")
            no_permissions.append(str(document_id))
    else:
        print("文档ID: " + str(document_id) + ", 很抱歉，文档不存在！")
        no_documnts.append(str(document_id))

def all_thread_id(url, config, document_id, thread):
    name_list = [url, config, document_id]
    name_lists = [(name_list, None)]
    
    pool = threadpool.ThreadPool(int(thread))
    req = threadpool.makeRequests(get_image, name_lists)
    for r in req:
        pool.putRequest(r)
    pool.wait()
    # time.sleep()

def main(url, config, Document_max, thread):
    
    # 判断输入的是最大空间ID还是空间ID区间
    if "-" in Document_max:
        Document_max_list = Document_max.split("-")
        for document_id in range(int(Document_max_list[0]),int(Document_max_list[1])):
            all_thread_id(url, config, document_id, thread)
            
    else:
        for document_id in range(int(Document_max)):
            all_thread_id(url, config, document_id, thread)


if __name__ == "__main__":

    print('''
 ____  _        ___  ____              
/ ___|/ | __ _ / _ \|  _ \  __ _ _   _ 
\___ \| |/ _` | | | | | | |/ _` | | | |
 ___) | | (_| | |_| | |_| | (_| | |_| |
|____/|_|\__, |\___/|____/ \__,_|\__, |
         |___/                   |___/ 
                                       
Powered by S1g0Day
    ''')
    
    parser = ArgumentParser()
    parser.add_argument("-url", dest="url", required=True, help="请输入url")
    parser.add_argument("-DM", dest="Document_max", required=True, help="请输入文档ID或范围,eg: 4385 or 784-4385")
    parser.add_argument("-t", dest="thread", required=True, help="请输入文档ID或范围,eg: 4385 or 784-4385")
    args = parser.parse_args()
    
    # 该ID无文档
    no_documnts = []
    # 该ID无权限
    no_permissions = []
    # 该ID无图片
    no_imgs = []
    # 该ID图片存在异常
    error_imgs = []

    
    if len(sys.argv) == 0:
        parser.print_help()
    else:
        config = json.loads(open("config.json", "r").read())
        main(args.url, config, args.Document_max, args.thread)
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        print("\n%s 检测完成: 一共检查 %s 篇文章, %d 篇无文档, %d 篇无权限访问, %d 篇文档无图片, %d 篇文档图片存在异常, 图片异常的已写入 http_imgs.txt" %(current_date, args.Document_max, len(no_documnts), len(no_permissions), len(no_imgs), len(error_imgs)))
