# -*- coding: UTF-8 -*-
'''
文件类型: html
作用: html转md,将md内base64图片更换为本地图片
范围：单目录

Eg: python3 .\mm-1.py -path E:\work\mm-wiki\md\1_file\2_html
'''

import os
import re
import uuid
import base64
import html2text
from argparse import ArgumentParser


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
    
    image_name = img_path_name + "\\" + "{}.{}".format(uuid.uuid4(), ext)
    with open(image_name, "wb") as f:
        f.write(img)

    return image_name

# 保存图片转换后的md文档
def md_images_save():

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
            print(markdown_images_data)
            # with open(md_path_name + filename + '.md', 'w', encoding='utf-8') as file3:
                # file3.write(markdown_images_data)

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
    parser.add_argument("-path", dest="path_name", required=True, help="请输入文档根目录,默认脚本所在目录")

    args = parser.parse_args()
    
    traversal_file_path(args.path_name)
    md_path_name = args.path_name + "\\md\\"
    html_md()
    file_path.clear()
    md_images_save()
