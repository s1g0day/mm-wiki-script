# -*- coding: utf-8 -*-
'''
python3 0.Template.py -p E:\work\现勘\1.16现勘
'''
import os
import sys
import time
import threadpool
from argparse import ArgumentParser

def get_files_list(path):
    print("\r\t\033[33m[+] %s \033[0m" % path) 

def logo():
    print('''
 ____  _        ___  ____              
/ ___|/ | __ _ / _ \|  _ \  __ _ _   _ 
\___ \| |/ _` | | | | | | |/ _` | | | |
 ___) | | (_| | |_| | |_| | (_| | |_| |
|____/|_|\__, |\___/|____/ \__,_|\__, |
         |___/                   |___/ 
                                       
Powered by S1g0Day
    ''')
    
if __name__ == '__main__':
    
    start_time = time.time()    # 程序开始时间
    logo()

    parser = ArgumentParser()
    parser.add_argument("-path", dest="path_name", help="请输入文档根目录,默认脚本所在目录",action="store_true")
    parser.add_argument("-t", dest="thread", type=int, default="1", help="请输入线程")
    args = parser.parse_args()
    
    if len(sys.argv) <= 1:
        parser.print_help()
    else:
        # 写入指定目录
        name_list = [args.path_name]
        name_lists = [(name_list, None)]
        
        pool = threadpool.ThreadPool(int(args.thread))
        req = threadpool.makeRequests(get_files_list, name_lists)
        for r in req:
            pool.putRequest(r)
        pool.wait()
    end_time = time.time()    # 程序结束时间
    run_time = end_time - start_time    # 程序的运行时间，单位为秒
    print(run_time)