# -*- coding: utf-8 -*-
'''
转自：https://github.com/Deali-Axy/Markdown-Image-Parser/blob/master/spider.py
解析markdown文档，然后获取到其中的所有图片，再把图片按md文件分好目录保存。
'''


import os
import sys
from argparse import ArgumentParser


def get_files_list(dir):
    """
    获取一个目录下所有文件列表，包括子目录
    :param dir:
    :return:
    """
    dirs_list = []
    files_list = []
    for root, dirs, files in os.walk(dir, topdown=False):
        for file in files:
            files_list.append(os.path.join(root, file))

    return files_list

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
    
    parser = ArgumentParser()
    parser.add_argument("-path", dest="path_name", help="请输入文档根目录,默认脚本所在目录")
    args = parser.parse_args()
    
    if len(sys.argv) <= 1:
        parser.print_help()
    else:
        files_list = get_files_list(args.path_name)
        for files in files_list:
            print(files)
