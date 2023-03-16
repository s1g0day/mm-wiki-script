# -*- coding: utf-8 -*-
'''
https://blog.csdn.net/sinat_29957455/article/details/82778306
'''


import os
import sys
from argparse import ArgumentParser

def get_file_path(root_path, dirs_list, files_list):

    #获取该目录下所有的文件名称和目录名称
    dir_or_files = os.listdir(root_path)
    for dir_file in dir_or_files:
        #获取目录或者文件的路径
        dir_file_path = os.path.join(root_path,dir_file)
        #判断该路径为文件还是路径
        if os.path.isdir(dir_file_path):
            dirs_list.append(dir_file_path)
            #递归获取所有文件和目录的路径
            get_file_path(dir_file_path, dirs_list, files_list)
        else:
            files_list.append(dir_file_path)

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
        get_file_path(args.path_name, dirs_list, files_list)
        for i in range(len(dirs_list)):
            file_path1 = dirs_list[i]
            print(file_path1)
            for j in range(len(files_list)):
                file_path2 = files_list[j]
                if file_path1 in file_path2:
                    print("\r\t\033[33m[+] %s \033[0m" % file_path2)