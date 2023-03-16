# -*- coding: UTF-8 -*-
'''
文件类型: md
作用: 上传某个文件夹内所有md文件, 将其保存到空间ID为 `1` 、目录id为 `4314` 的单个目录下
缺点: 暂时无法自动保存文件内的图片
范围: 单目录
# Eg: python3 .\mm-1.py -url http://192.168.232.154:8080 -pid 3268 -sid 11 -t 2 -path C:\\Users\\FH287EGHH7823\\Downloads\\文档\\1.内网渗透
'''

import os
import sys
import json
import urllib3
import requests
import threadpool
from argparse import ArgumentParser
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 指定写入目录
def main(url, config, path_name, parent_id, space_id):

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
            # document_id = document_save_file(url, config, parent_id, space_id, document_name)
            # if "err" not in document_id:
                # 写入内容
                # print(file_content)
                # page_modify(url, config, document_id, document_name, file_content)
            for j in file_content:
                print(j)
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
    # parser.add_argument("-cookie", dest="cookie", required=True, help="请输入cookie")
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

