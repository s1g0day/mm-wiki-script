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
from bs4 import BeautifulSoup
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
def save_txt(file_name, text):
    with open(file_name,'a+', encoding='utf-8') as f:
        f.writelines(text)
def get_path(id, text):
    
    soup = BeautifulSoup(text, "html.parser")
     # 查找标题元素并添加检查
    title_element = soup.find("h3", {"class": "view-page-title"})
    if title_element is None:
        print(f"\n文档ID: {str(id)}, 无法解析标题，可能是页面结构已更改或页面加载不完整")
        save_txt('logs/error.txt', f"id:{id} 无法解析标题\n")
        return False
    
    title = title_element.text.replace(" ", "")
    
    # 查找路径元素并添加检查
    path_element = soup.find("p", {"class": "view-page-path"})
    if path_element is None:
        print(f"\n文档ID: {str(id)} 无法解析路径，可能是页面结构已更改或页面加载不完整")
        save_txt('logs/error.txt', f"id:{id} 无法解析路径\n")
        return False
    
    path = path_element.text.replace("\n", "").replace(" ", "")

    if "/" in path:
        path_new = path.split("/")[-1]
        if title == path_new:
            print(f"\n文档ID: {str(id)} 是目录, title:{title} path: {path}")
            save_txt('logs/path.txt', f"id:{id} title:{title} path:{path}\n")
            return False
        else:
            print(f"\n文档ID: {str(id)}, 标题: {title}")
            save_txt('logs/title.txt', f"id:{id} title:{title} path:{path}\n")
            return True
    else:
        path_new = path
        if title == path_new:
            print(f"\n文档ID: {str(id)} 是目录, title:{title} path: {path}")
            save_txt('logs/path.txt', f"id:{id} title:{title} path:{path}\n")
            return False
        else:
            print(f"\n文档ID: {str(id)}, 标题: {title}")
            save_txt('logs/title.txt', f"id:{id} title:{title} path:{path}\n")
            return True
    


def get_image(url, config, document_id):
    """
    获取文档中的图片并验证其是否可访问
    
    Args:
        url: 网站基础URL
        config: 请求配置（包含cookies等）
        document_id: 文档ID
    """
    try:
        # 提取图片地址
        req = requests_test(url, config, document_id)
        
        # 检查文档是否存在和权限问题
        if "文档不存在" in req.text:
            print(f"文档ID: {document_id}, 文档不存在")
            no_documnts.append(str(document_id))
            return
            
        if "您没有权限访问该空间" in req.text:
            print(f"文档ID: {document_id}, 您没有权限访问该空间")
            no_permissions.append(str(document_id))
            return
        
        # 检查是否为目录
        if not get_path(document_id, req.text):
            return
        
        # 提取图片链接
        datas_imgs = extract_image_links(req.text)
        
        if not datas_imgs:
            print(f"文档ID: {document_id}, 无图片")
            no_imgs.append(str(document_id))
            return
        
        # 验证图片是否可访问
        alive_imgs = verify_images(url, config, datas_imgs)
        
        if not alive_imgs:
            print(f"\n文档ID: {document_id}, success")
        else:
            error_text = f"\n文档ID: {document_id}, 存在外链"
            error_imgs.append(str(document_id))
            print(error_text)
            
            # 优化文件写入方式
            try:
                with open('logs/http_imgs.txt', 'a+', encoding='utf-8') as f:
                    f.write(f"{error_text}\n")
                    f.write("\n".join(alive_imgs) + "\n\n")
            except Exception as e:
                print(f"写入日志文件失败: {str(e)}")
    except Exception as e:
        print(f"文档ID: {document_id}, 处理过程中出错: {str(e)}")
        save_txt('logs/error.txt', f"id:{document_id} 处理错误: {str(e)}\n")
def extract_image_links(html_text):
    """
    从HTML文本中提取图片链接
    
    Args:
        html_text: HTML文本内容
        
    Returns:
        list: 图片链接列表
    """
    datas_imgs = []
    
    # 解码HTML实体
    html_text = html.unescape(html_text)
    
    # 移除HTML标签
    pattern = re.compile(r'<[^>]+>', re.S)
    result = pattern.sub('', html_text)
    
    # 按行分割
    lines = result.split("\n")
    
    # 使用更高效的正则表达式一次性匹配所有图片
    img_pattern = re.compile(r'\!\[(?P<ext>.*?)\]\((?P<data>[^\)]+)\)', re.DOTALL)
    
    for line in lines:
        if "](" in line:
            matches = img_pattern.finditer(line)
            for match in matches:
                data = match.groupdict().get("data")
                if data and data.strip():
                    datas_imgs.append(data.strip())
    
    return datas_imgs

def verify_images(base_url, config, image_links):
    """
    验证图片链接是否可访问
    
    Args:
        base_url: 网站基础URL
        config: 请求配置
        image_links: 图片链接列表
        
    Returns:
        list: 不可访问的图片链接列表
    """
    invalid_links = []
    
    for img_link in image_links:
        if img_link.startswith(("http://", "https://")):
            # 外部链接直接添加到结果中
            invalid_links.append(img_link)
        else:
            # 本地图片验证
            result = req_img_test(base_url + img_link, config)
            if result != 200:
                invalid_links.append(result)
    
    return invalid_links

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
    parser.add_argument("-u", dest="url", required=True, help="请输入url")
    parser.add_argument("-id", dest="Document_max", required=True, help="请输入文档ID或范围,eg: 4385 or 784-4385")
    parser.add_argument("-t", dest="thread", required=False, default=1, help="请输入线程,eg: 10")
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
        print("\n%s 检测完成: 一共检查 %s 篇文章, %d 篇无文档, %d 篇无权限访问, %d 篇文档无图片, %d 篇文档图片存在异常, 图片异常的已写入 logs/http_imgs.txt" %(current_date, args.Document_max, len(no_documnts), len(no_permissions), len(no_imgs), len(error_imgs)))
