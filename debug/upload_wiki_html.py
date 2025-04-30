# -*- coding: UTF-8 -*-
'''
文件类型: html
作用: html转md,将md内base64图片更换为本地图片, 并上传wiki
范围：单目录

Eg: python3 .\mm-2.py -url http://192.168.232.154:8080 -path c:\\Users\\FH287EGHH7823\\Desktop\\md\\2 -pid 2577 -sid 1
'''

import os
import re
import sys
import json
import uuid
import base64
import requests
import html2text
from argparse import ArgumentParser


def requests_test(url, config, datas):

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-TW,zh-CN;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'x-forwarded-for': '202.95.13.51',
        'x-originating-ip': '202.95.13.51',
        'x-remote-addr': '202.95.13.51',
        'x-remote-ip': '202.95.13.51',
    }

    try:
        req = requests.post(url, cookies=config, headers=headers, data=datas, verify=False)
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
        print(url + "连接错误")
        exit()

# 创建文档
def document_save_file(url, config, parent_id, space_id, document_name):

    data = {
    'parent_id': parent_id,
    'space_id': space_id,
    'type': '1',
    'name': document_name,
    }

    urlpath = url + '/document/save'
    req = requests_test(urlpath, config, data)
    req_data = json.loads(req.text)
    if(req_data["code"] == 0):
        print(document_name + ": " + req_data["message"])
    else:
        print(document_name + ": " + req_data["message"])
        document_url = req_data["redirect"]["url"]
        document_url_id = document_url.split('=')[1]
        return document_url_id

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
    req = requests_test(urlpath, config, data)
    req_data = json.loads(req.text)
    if(req_data["code"] == 1):
        print(document_name + ": " + req_data["message"])


# 指定写入目录
def Specify_dir(url, config, parent_id, space_id, markdown_images_data):

    for i in range(len(file_path)):

        # 获取文件后缀
        document_prefix = file_path[i].split('\\')[-1].split('.')[-1]
        if document_prefix == "md":
            document_name = file_path[i].split('\\')[-1].split('.md')[-2]
            # print(document_name)
            
            # 创建文档
            document_id = document_save_file(url, parent_id, space_id, document_name)

            # 写入内容
            page_modify(url, config, document_id, document_name, markdown_images_data)

# 读取html内容并转换为md
def html_md():
    for i in range(len(file_path)):
        filename = file_path[i].split("\\")[-1].split(".html")[0]

        with open(file_path[i], 'r', encoding='utf-8') as file:
            for line in file:
                markdown = html2text.html2text(line)
                html_markdown.append(markdown)
                
                if os.path.exists(md_path_name) == False:
                    os.mkdir(md_path_name)
                
                with open(md_path_name + filename + '.md', 'w', encoding='utf-8') as file2:
                    file2.write(markdown)
    print("完成html转换md")
    

def traversal_file_path(path):
    for item in os.scandir(path):
        if item.is_dir():
            dirs.append(item.path)
        elif item.is_file():
            file_path.append(item.path)

# 转换base64图片
def decode_image(src, filename):

    # 1、信息提取
    result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", src, re.DOTALL)
    if result:
        ext = result.groupdict().get("ext")
        data = result.groupdict().get("data")
    else:
        raise Exception("Do not parse!")

    # 2、base64解码
    img = base64.urlsafe_b64decode(data)

    # 3、二进制文件保存
    
    img_path_name = md_path_name + filename
    
    if os.path.exists(img_path_name) == False:
        os.mkdir(img_path_name)
    
    image_name = img_path_name + "\\{}.{}".format(uuid.uuid4(), ext)
    with open(image_name, "wb") as f:
        f.write(img)

    return image_name

# 保存图片转换后的md文档
def md_images_save(url, config, parent_id, space_id):
    
    # 列出md内文件
    traversal_file_path(md_path_name)
    
    for i in range(len(file_path)):
        # 获取文件后缀
        filext = file_path[i].split("\\")[-1].split(".")[-1]
        if filext == "md":
            
            # 获取文件名
            filename = file_path[i].split("\\")[-1].split(".md")[0]
            
            # 本地路径列表
            markdown_images = []
            with open(file_path[i], 'r', encoding='utf-8') as file_md_path:
                file_md_data = file_md_path.readlines()
                for img_datas in file_md_data:
                    # datas = ""
                    if "](data:image" in img_datas:
                        
                        # 解析base64图片并保存到本地，
                        image_name = decode_image(img_datas, filename)
                        
                        # 以![]( 分割列表
                        img_data_spl = img_datas.split("data:image", 1)[0]
                        
                        # 合成图片本地路径
                        md_image_name = "![](" + image_name + ")"
                        img_datas = img_data_spl.replace("![](", md_image_name)

                    # 将合成后的本地路径添加到列表
                    markdown_images.append(img_datas)
            
            # 将替换后的文档保存到本地
            markdown_images_data = "".join(markdown_images)
            with open(md_path_name + filename + '.md', 'w', encoding='utf-8') as file3:
                file3.write(markdown_images_data)
            
            # 自动上传wiki
            Specify_dir(url, config, parent_id, space_id, markdown_images_data)
            
if __name__ == '__main__':

    print('''
 ____  _        ___  ____              
/ ___|/ | __ _ / _ \|  _ \  __ _ _   _ 
\___ \| |/ _` | | | | | | |/ _` | | | |
 ___) | | (_| | |_| | |_| | (_| | |_| |
|____/|_|\__, |\___/|____/ \__,_|\__, |
         |___/                   |___/ 
                                       
Powered by S1g0Day
    ''')
    

    dirs = []
    file_path = []
    file_content = []
    html_markdown = []
    
    parser = ArgumentParser()
    parser.add_argument("-url", dest="url", required=True, help="请输入url")
    parser.add_argument("-path", dest="path_name", required=True, help="请输入文档根目录,默认脚本所在目录")
    parser.add_argument("-pid", dest="parent_id", required=True, type=int, help="请输入目录ID")
    parser.add_argument("-sid", dest="space_id", required=True, type=int, default="1", help="请输入空间ID")
    args = parser.parse_args()
    
    if len(sys.argv) == 0:
        parser.print_help()
    else:
        config = json.loads(open("config.json", "r").read())
        traversal_file_path(args.path_name)
        md_path_name = args.path_name + "\\md\\"
        html_md()
        file_path.clear()
        md_images_save(args.url, config, args.parent_id, args.space_id)
    