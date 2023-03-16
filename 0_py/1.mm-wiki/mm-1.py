# -*- coding: UTF-8 -*-
'''
文件类型: md
作用: 上传某个文件夹内所有md文件, 将其保存到空间ID为 `1` 、目录id为 `4314` 的单个目录下
缺点: 暂时无法自动保存文件内的图片
范围: 单目录
# Eg: python3 .\mm-1.py -url http://192.168.232.154:8080 -pid 3268 -sid 11 -t 2 -path C:\\Users\\FH287EGHH7823\\Downloads\\文档
'''

import os
import sys
import json
import urllib3
import requests
import threadpool

from argparse import ArgumentParser
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def requests_test(url, urlpath, config, datas):
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-TW,zh-CN;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # 'Cookie': cookie,
        'Origin': url,
        'Pragma': 'no-cache',
        # 'Referer': url + '/document/add?space_id=' + str(space_id) + '&parent_id=' + str(parent_id),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'x-forwarded-for': '114.29.255.8',
        'x-originating-ip': '114.29.255.8',
        'x-remote-addr': '114.29.255.8',
        'x-remote-ip': '114.29.255.8',
    }
    # req = requests.post(urlpath, cookies=config, headers=headers, data=datas, verify=False)
    # print(req.text)
    try:
        req = requests.post(urlpath, cookies=config, headers=headers, data=datas, verify=False)
        req.encoding = req.apparent_encoding	# apparent_encoding比"utf-8"错误率更低
        status_code = req.status_code
        log = "status_code: " + str(status_code)
        if status_code == 404:
            # print("error_code: ",status_code)
            exit()
        else:
            # print(log)
            return req
    except:
        print(url + " 连接错误")
        exit()

# 创建文档
def document_save_file(url, config, parent_id, space_id, document_name):

    data = {
    'parent_id': parent_id,
    'space_id': space_id,
    'type': '1',
    'name': document_name,
    }
    print("创建文档")
    urlpath = url + '/document/save'
    req = requests_test(url, urlpath, config, data)
    req_data = json.loads(req.text)
    if(req_data["code"] == 0):
        print(document_name + ": " + req_data["message"])
        return "err"
    else:
        print(document_name + ": " + req_data["message"])
        document_url = req_data["redirect"]["url"]
        document_id = document_url.split('=')[1]
        return document_id

# 写入文件内容
def page_modify(url, config, document_id, document_name, document_datas):
    data = {
        'document_id': document_id,
        'name': document_name,
        'document_page_editor-markdown-doc': document_datas,
        'comment': '',
        'is_notice_user': '0',
        'is_follow_doc': '1',
    }

    urlpath = url + '/page/modify'
    req = requests_test(url, urlpath, config, data)
    req_data = json.loads(req.text)
    if(req_data["code"] == 1):
        print(document_name + ": " + req_data["message"])


# 读取文件内容
def read_file(file_path):
    file_content = []
    try:
        files = open(file_path, 'r', encoding='utf-8')
        file_content.append(files.read())
    finally:
        if files:
            files.close()
    return file_content
    
# 读取文件目录
def traversal_files(path):

    dirs = []
    file_path = []
    
    for item in os.scandir(path):
        if item.is_dir():
            dirs.append(item.path)
        elif item.is_file():
            file_path.append(item.path)
    
    return dirs,file_path

# 指定写入目录
def Specify_dir(url, config, path_name, parent_id, space_id):

    # 遍历目录及读取文件内容
    dirs, file_path = traversal_files(path_name)
    # print("file_path",len(file_path))
    for i in range(len(file_path)):
        # 获取文件内容
        # print("file_path",file_path[i])
        file_content = read_file(file_path[i])
        # print(file_content)
        # 获取文件后缀
        document_prefix = file_path[i].split('\\')[-1].split('.')[-1]
        if document_prefix == "md":
            document_name = file_path[i].split('\\')[-1].split('.md')[-2]
            # print(document_name)
            # 创建文档
            # print(document_save_file(url, cookie, parent_id, space_id, document_name))
            document_id = document_save_file(url, config, parent_id, space_id, document_name)
            if "err" not in document_id:
                # 写入内容
                page_modify(url, config, document_id, document_name, file_content)
            
    dirs.clear()
    file_path.clear()
    file_content.clear()

if __name__== "__main__":

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
    parser.add_argument("-cookie", dest="cookie", required=True, help="请输入cookie")
    parser.add_argument("-path", dest="path_name", required=True, help="请输入文档根目录,默认脚本所在目录")
    parser.add_argument("-pid", dest="parent_id", required=True, type=int, help="请输入目录ID")
    parser.add_argument("-sid", dest="space_id", type=int, default="1", help="请输入空间ID")
    parser.add_argument("-t", dest="thread", type=int, default="1", help="请输入线程")
    args = parser.parse_args()

    if len(sys.argv) <= 1:
        parser.print_help()
    else:
        config = json.loads(open("config.json", "r").read())
  
        # 写入指定目录
        name_list = [args.url, config, args.path_name, args.parent_id, args.space_id]
        name_lists = [(name_list, None)]
        
        pool = threadpool.ThreadPool(int(args.thread))
        req = threadpool.makeRequests(Specify_dir, name_lists)
        for r in req:
            pool.putRequest(r)
        pool.wait()

