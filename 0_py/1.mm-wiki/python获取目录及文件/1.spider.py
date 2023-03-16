# -*- coding: utf-8 -*-
'''
转自：https://github.com/Deali-Axy/Markdown-Image-Parser/blob/master/spider.py
解析markdown文档，然后获取到其中的所有图片，再把图片按md文件分好目录保存。
'''


import os
import sys
import uuid
import misaka
import requests
from bs4 import BeautifulSoup
from argparse import ArgumentParser


def get_files_list(dir):
    """
    获取一个目录下所有文件列表，包括子目录
    :param dir:
    :return:
    """
    dirs_list
    files_list = []
    for root, dirs, files in os.walk(dir, topdown=False):
        for file in files:
            files_list.append(os.path.join(root, file))

    return files_list

def get_pics_list(md_content):
    """
    获取一个markdown文档里的所有图片链接
    :param md_content:
    :return:
    """
    md_render = misaka.Markdown(misaka.HtmlRenderer())
    html = md_render(md_content)
    soup = BeautifulSoup(html, features='html.parser')
    pics_list = []
    for img in soup.find_all('img'):
        pics_list.append(img.get('src'))

    return pics_list


def download_pics(url, file):
    img_data = requests.get(url).content
    filename = os.path.basename(file)
    dirname = os.path.dirname(file)
    targer_dir = os.path.join(dirname, f'{filename}.assets')
    if not os.path.exists(targer_dir):
        os.mkdir(targer_dir)

    with open(os.path.join(targer_dir, f'{uuid.uuid4().hex}.jpg'), 'w+') as f:
        f.buffer.write(img_data)


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
    path_list = []

    parser = ArgumentParser()
    parser.add_argument("-path", dest="path_name", help="请输入文档根目录,默认脚本所在目录")
    args = parser.parse_args()
    
    if len(sys.argv) <= 1:
        parser.print_help()
    else:
        # files_list = get_files_list(os.path.abspath(os.path.join('.', 'files')))
        files_list = get_files_list(args.path_name)
        for file in files_list:
            print(f'正在处理：{file}')

            # with open(file, encoding='utf-8') as f:
            #     md_content = f.read()

            # pics_list = get_pics_list(md_content)
            # print(f'发现图片 {len(pics_list)} 张')

            # for index, pic in enumerate(pics_list):
            #     print(f'正在下载第 {index + 1} 张图片...')
            #     download_pics(pic, file)
            # print(f'处理完成。')
