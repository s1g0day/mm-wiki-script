'''
作用: 循环遍历读取目录及文件列表
'''

import os

# 读取文件内容
def read_file(file_path):
    try:
        file = open(file_path, 'r', encoding='utf-8')
        file_content.append(file.read())
    finally:
        if file:
            file.close()

# 读取文件目录
def traversal_files(path):
    for item in os.scandir(path):
        if item.is_dir():
            dirs.append(item.path)
        elif item.is_file():
            read_file(item.path)
            file_path.append(item.path)
    
    print(file_path)


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
    

    dirs = []
    file_path = []
    file_content = []
    path = 'C:\\Users\\FH287EGHH7823\\Desktop\\md\\2'
    traversal_files(path)
