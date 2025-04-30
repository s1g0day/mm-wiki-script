# -*- coding: utf-8 -*-
"""
@Createtime: 2023-07-28 16:46:31
@UpdateTime: 2023-07-28 17:26:07
@description: 对比两个文件夹的差异
"""

import os
import sys
import shutil
from datetime import datetime
from argparse import ArgumentParser


def traversal_files(path, dirs_list, files_list):
    """递归遍历目录及其子目录中的所有文件和文件夹"""
    for item in os.scandir(path):
        if item.is_dir():
            dirs_list.append(item.path)
            traversal_files(item.path, dirs_list, files_list)
        elif item.is_file():
            files_list.append(item.path)

def compare_folders(folder_a, folder_b, output_dir):
    """比较两个文件夹的差异并复制不同的文件"""
    dirs_a, files_a = [], []
    dirs_b, files_b = [], []
    
    traversal_files(folder_a, dirs_a, files_a)
    traversal_files(folder_b, dirs_b, files_b)
    
    # 过滤出.md文件（忽略大小写）
    md_files_a = [f for f in files_a if os.path.splitext(f)[1].lower() == '.md']
    md_files_b = [f for f in files_b if os.path.splitext(f)[1].lower() == '.md']
    
    files_a_dict = {os.path.basename(f): f for f in md_files_a}
    files_b_dict = {os.path.basename(f): f for f in md_files_b}
    
    diff_file_names = set(files_a_dict.keys()) - set(files_b_dict.keys())
    diff_files = [files_a_dict[name] for name in diff_file_names]
    
    # 创建输出目录
    if diff_files:
        copy_dir = os.path.join(output_dir, "diff_files")
        os.makedirs(copy_dir, exist_ok=True)
        
        # 复制文件
        for file_path in diff_files:
            dest_path = os.path.join(copy_dir, os.path.basename(file_path))
            shutil.copy2(file_path, dest_path)
    
    return diff_files

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
    parser.add_argument("-a", dest="folder_a", help="第一个文件夹路径")
    parser.add_argument("-b", dest="folder_b", help="第二个文件夹路径")
    args = parser.parse_args()
    
    if not (args.folder_a and args.folder_b):
        parser.print_help()
    else:
        # 获取脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 创建日志文件
        log_file = os.path.join(current_dir, f"diff_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        with open(log_file, 'w', encoding='utf-8') as f:
            if not os.path.exists(args.folder_a):
                error_msg = f"错误：路径A不存在: {args.folder_a}"
                print(error_msg)
                f.write(error_msg + '\n')
                sys.exit(1)
            if not os.path.exists(args.folder_b):
                error_msg = f"错误：路径B不存在: {args.folder_b}"
                print(error_msg)
                f.write(error_msg + '\n')
                sys.exit(1)
            
            diff_files = compare_folders(args.folder_a, args.folder_b, current_dir)
            
            if diff_files:
                f.write("\n在文件夹A中但不在文件夹B中的文件：\n")
                for file in sorted(diff_files):
                    f.write(f"- {file}\n")
                    print(f"- {file}")
                summary = f"\n共找到 {len(diff_files)} 个不同的文件"
                f.write(summary + '\n')
                print(summary)
            else:
                msg = "\n文件夹A中的所有文件都存在于文件夹B中"
                f.write(msg + '\n')
                print(msg)
