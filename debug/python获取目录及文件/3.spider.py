# -*- coding: utf-8 -*-
import os
import sys
from argparse import ArgumentParser


def traversal_files(path,dirs_list,files_list):
    
    for item in os.scandir(path):
        if item.is_dir():
            dirs_list.append(item.path)
        elif item.is_file():
            files_list.append(item.path)

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
    
    dirs_list = []
    files_list = []

    parser = ArgumentParser()
    parser.add_argument("-path", dest="path_name", help="请输入文档根目录,默认脚本所在目录")
    args = parser.parse_args()
    
    if len(sys.argv) <= 1:
        parser.print_help()
    else:
        traversal_files(args.path_name, dirs_list, files_list)
        print(dirs_list)
        print(files_list)
