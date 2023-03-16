# -*- coding: UTF-8 -*-
'''
文件类型: html
作用: html转md
python3 html_md.py -path E:\work\mm-wiki\md\1_file\html
'''

import os
import html2text
from argparse import ArgumentParser

def read_file(path_name, filename):
    with open(path_name, 'r', encoding='utf-8') as file:
        for line in file:
            markdown = html2text.html2text(line)
            html_markdown.append(markdown)
            
            if os.path.exists(md_path_name) == False:
                os.mkdir(md_path_name)
            
            with open(md_path_name + filename + '.md', 'w', encoding='utf-8') as file2:
                file2.write(markdown)

def traversal_files(path):
    for item in os.scandir(path):
        if item.is_dir():
            dirs.append(item.path)
        elif item.is_file():
            files.append(item.path)


def html_md():
    for i in range(len(files)):
        filename = files[i].split("\\")[-1].split(".html")[0]
        read_file(files[i], filename)
    print("完成html转换md")

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
    files = []
    html_markdown = []
    
    parser = ArgumentParser()
    parser.add_argument("-path", dest="path", help="请输入文档根目录,默认脚本所在目录")
    args = parser.parse_args()
    
    traversal_files(args.path)
    md_path_name = args.path + "\\md\\"
    html_md()
