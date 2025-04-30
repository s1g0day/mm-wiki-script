# -*- coding: utf-8 -*-
'''
https://juejin.cn/post/6844904077738901511
'''


import os
import sys
from argparse import ArgumentParser

def get_files_list(path):
    '''
    遍历目录树
    '''

    for folder_name,sub_folders,filenames in os.walk(path):
        print('当前文件夹：'+folder_name)

        for sub_folder in sub_folders:
            print('所包含的子文件夹：'+sub_folder)

        for filename in filenames:
            print('文件夹 %s 中所包含的文件：%s' %(folder_name,filename))

        print('')

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
        get_files_list(args.path_name)
        