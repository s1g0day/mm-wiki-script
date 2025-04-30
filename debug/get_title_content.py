# -*- coding: UTF-8 -*-
'''
获取只有标题无内容的数据,需开启空间分享功能
python3 mm-4.py -u http://192.168.232.154:8080 -DM 4300
'''

import re
import sys
import json
import urllib3
import requests
from argparse import ArgumentParser
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def requests_test(url, config, document_id):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-TW,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
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


def get_textarea(url, config, document_id):

    No_content = []
    No_permissions = []
    No_documnts = []
    Symbol_datas = []
    
    req = requests_test(url, config, document_id)
    if "文档不存在" not in req.text:
        if "您没有权限访问该空间" not in req.text:
            res_textarea = re.search(r'<textarea style="display:none;">(?P<textarea>.*?)</textarea>', req.text,re.DOTALL)
            if res_textarea:
                textarea_data = res_textarea.groupdict().get("textarea")
                res_title = re.search(r'<h3 class="view-page-title"><i class="fa fa-file-word-o"></i>(?P<title>.*?)</h3>', req.text,re.DOTALL)

                # 查找文档是否有内容
                if len(textarea_data) == 0:
                    if res_title:
                        title_data = res_title.groupdict().get("title")
                        print("无内容的文档ID: %d, 标题: %s " %(document_id, title_data))
                        # No_content.append(str(document_id))
                else:
                    if res_title:
                        title_data = res_title.groupdict().get("title")
                        print("有内容的文档ID: %d, 标题: %s 文章内容字数: %d" %(document_id, title_data, len(textarea_data)))
                
                # 查找文档标题是否含有特殊符号
                Symbol_blacklist = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '、']
                for Symbol in Symbol_blacklist:
                    if Symbol in title_data:
                        print("文档ID: %d 含有特殊符号, 标题为: %s" %(document_id, title_data))
                        # Symbol_datas.append(str(document_id))
        else:
            print("文档ID: " + str(document_id) + ", 您没有权限访问该空间")
            # no_permissions.append(str(document_id))
    else:
        print("文档ID: " + str(document_id) + ", 很抱歉，文档不存在！")
        # no_documnts.append(str(document_id))
        
def main(url, config, Document_max):
    
    # 判断输入的是最大空间ID还是空间ID区间
    if "-" in Document_max:
        Document_max_list = Document_max.split("-")
        for document_id in range(int(Document_max_list[0]),int(Document_max_list[1])):
            # print(url, document_id)
            get_textarea(url, config, document_id)
    else:
        for document_id in range(int(Document_max)):
            # print(url, document_id)
            get_textarea(url, config, document_id)

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
    args = parser.parse_args()
    
    if len(sys.argv) == 0:
        parser.print_help()
    else:
        config = json.loads(open("config.json", "r").read())
        main(args.url, config, args.Document_max)

