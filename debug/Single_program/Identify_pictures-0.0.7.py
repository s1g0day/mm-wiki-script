# -*- coding: UTF-8 -*-
'''
@Createtime: 2023/1/11 9:51
@Updatetime: 2025/4/17 11:51
@description: 识别md文档内图片格式
@Version: 0.0.7
@note:
    图片格式: 本地图片、网络图片、base64图片

    测试base64图片: python3 Identify_pictures.py -path E:\\work\\mm-wiki\\wiki\\1_file\\1_base64
    测试本地图片: python3 Identify_pictures.py -path E:\\work\\mm-wiki\\wiki\\1_file\\2_local
    测试网络图片: python3 Identify_pictures.py -path E:\\work\\mm-wiki\\wiki\\1_file\\3_http
                python3 Identify_pictures.py -path E:\\work\\mm-wiki\\wiki\\1_file\\3_http -proxy socks5://127.0.0.1:7890
    未完成:
        自动识别图片类型,根据图片类型命名后缀
        gif、mp4、压缩包问题处理
'''

import os
import re
import sys
import uuid
import base64
import shutil
import urllib3
import requests
import concurrent.futures
from urllib.parse import unquote
from argparse import ArgumentParser
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def traversal_files(path):

    dirs = []
    files = []
    
    for item in os.scandir(path):
        if item.is_dir():
            dirs.append(item.path)
        elif item.is_file():
            files.append(item.path)

    return dirs,files

def base64_decode_image(md_path_name, img_data, filename):

    # 1、信息提取
    result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", img_data, re.DOTALL)
    if result:
        ext = result.groupdict().get("ext")
        data = result.groupdict().get("data")
        # print(ext)
        # print(data)
    else:
        raise Exception("Do not parse!")

    # 2、base64解码
    img = base64.urlsafe_b64decode(data)

    # 3、二进制文件保存
    
    img_path = md_path_name + "\\image"
    
    if os.path.exists(img_path) == False:
        os.mkdir(img_path)
    
    img_path_name = img_path + "\\" + filename
    
    if os.path.exists(img_path_name) == False:
        os.mkdir(img_path_name)
    
    image_name = img_path_name + "\\image-{}.{}".format(uuid.uuid4(), ext)
    with open(image_name, "wb") as f:
        f.write(img)

    # 覆盖datas的图片内容
    datas = "\n\n![](" + image_name + ")\n\n"

    return datas

def download_pics_proxy(url, files, s):
    if ".gif" in url or ".mp4" in url:
        print("\t\t" + url)
        return url
    else:
        img_data = s.get(url).content

        if not os.path.exists(files):
            os.mkdir(files)
            
        image_name = files + "\\image-{}.{}".format(uuid.uuid4(), 'jpg')
        # print(image_name)
        with open(image_name, 'w+') as f:
            f.buffer.write(img_data)
        return image_name
def download_pics(url, files):
    if ".gif" in url or ".mp4" in url:
        print("\t\t" + url)
        return url
    else:
        img_data = requests.get(url).content
        if not os.path.exists(files):
            os.mkdir(files)
            
        image_name = files + "\\image-{}.{}".format(uuid.uuid4(), 'jpg')
        # print(image_name)
        with open(image_name, 'w+') as f:
            f.buffer.write(img_data)
        return image_name
    
def intern_save_img(md_path_name, img_data, proxy, filename):
    
    img_path = md_path_name + "\\image"
    
    if os.path.exists(img_path) == False:
        os.mkdir(img_path)
    
    img_path_name = img_path + "\\" + filename

    # 设置代理
    if proxy:
        # print("已设置代理: ", proxy)
        s = requests.session()
        s.proxies = {'https': proxy}
        response = s.get(img_data, verify=False)
        if response.status_code == 200:
            # print("请求正常: ", img_data)
            md_datas = download_pics_proxy(img_data, img_path_name, s=s)
            md_datas = "\n\n![](" + md_datas + ")\n\n"
            return md_datas
        else:
            print("\r\t\t[-] 请求异常: ", img_data)
            return img_data
    else:
        # print("无代理访问")
        response = requests.get(img_data, verify=False)
        # print(response)
        if response.status_code == 200:
            # print("请求正常: ", img_data)
            md_datas = download_pics(img_data, img_path_name)
            md_datas = "\n\n![](" + md_datas + ")\n\n"
            return md_datas
        else:
            print("\r\t\t[-] 请求异常: ", img_data)
            return img_data

# 规范本地图片路径
def local_img_path(imgpath):
    # URL解码
    imgpath = unquote(imgpath)
    # 获取md文件所在目录路径
    base_dir = os.path.dirname(file_path)
    # 处理相对路径
    if not os.path.isabs(image_url):
        image_url = os.path.join(base_dir, image_url)
    # 规范化路径
    image_url = os.path.normpath(image_url)

def local_save_img(md_path_name, img_data, filename):
    '''
    判断地址是不是本地图片
    判断图片是否存在
    将图片移动到当前目录
    返回图片md地址
    '''
    img_path = md_path_name + "\\image"
    
    if os.path.exists(img_path) == False:
        os.mkdir(img_path)
    
    img_path_name = img_path + "\\" + filename
    
    # 判断目录是否存在
    if os.path.exists(img_path_name) == False:
        os.mkdir(img_path_name)
    
    # 提取图片地址前两个字符
    x = img_data[:2]
    if re.match(r"^([a-zA-Z]):", x):
        img_data = img_data
    else:
        # 获取图片绝对路径
        img_data = os.path.abspath(md_path_name) + "\\" + img_data

    if os.path.exists(img_data):  # 判断是否能打开
        image_name = img_path_name + "\\image-{}.{}".format(uuid.uuid4(), 'jpg')

        # shutil模块复制文件
        shutil.copy(img_data, image_name)

        # 覆盖datas的图片内容
        datas = "\n\n![](" + image_name + ")\n\n"
        return datas
    else:
        print("\r\t\t[-] 本地图片无法打开: ", img_data)
        return img_data

def Pictures_processing(md_path_name, img_path, proxy, filename, count, base64_images, intern_imgs, local_imgs):
    # 处理base64图片
    if "data:image" in img_path:
        print("\r\t\033[32m[*] %d : base64图片\033[0m" % count)
        datas = base64_decode_image(md_path_name, img_path, filename)
        if datas != None:
            base64_images.append(datas)
    elif "http://" in img_path or "https://" in img_path:
        print("\r\t\033[32m[*] %d : 存在网络图片,需转换为本地\033[0m" % count)
        datas = intern_save_img(md_path_name, img_path, proxy, filename)
        if datas != None:
            intern_imgs.append(datas)
    else:
        print("\r\t\033[32m[*] %d : 本地图片或其他格式\033[0m" % count)
        datas = local_save_img(md_path_name, img_path, filename)
        if datas != None:
            local_imgs.append(datas)

    return datas, base64_images, intern_imgs, local_imgs

def update_md(markdown_text, md_path_name, filename):
    print("\r\t\033[33m[+] 更新md文档\033[0m")
    # 将替换后的文档保存到本地  
    markdown_test_data = "".join(markdown_text)
    with open(md_path_name + "\\" + filename + '.md', 'w', encoding='utf-8') as file3:
        file3.write(markdown_test_data)

def md_img_readline(datas, img_data, md_path_name, proxy, document_name, count, base64_images, intern_imgs, local_imgs):
    if ")](" in img_data:
        # 处理带跳转链接的图片
        img_parts = img_data.split(")](")
        if len(img_parts) >= 2:
            # 提取图片URL或本地路径部分
            img_url = img_parts[0]
            # 处理图片URL或本地路径    
            result_data, base64_images, intern_imgs, local_imgs = Pictures_processing(md_path_name, img_url, proxy, document_name, count, base64_images, intern_imgs, local_imgs)
            
            if result_data == img_data:
                datas = datas
            else:
                datas = result_data
    else:
        result_data, base64_images, intern_imgs, local_imgs = Pictures_processing(md_path_name, img_data, proxy, document_name, count, base64_images, intern_imgs, local_imgs)
        if result_data == img_data:
            datas = datas
        else:
            datas = result_data
    return datas

def images_save(md_path_name, files_name, proxy):

    print("文件名:",files_name)
    # 图片列表
    base64_images = []
    intern_imgs = []
    local_imgs = []

    # md内容
    md_data_images = []

    # 获取文件名和扩展名
    file_name = os.path.basename(files_name)
    file_ext = os.path.splitext(file_name)[1].lower()
    
    if file_ext == '.md':
        # 获取不带扩展名的文件名
        document_name = os.path.splitext(file_name)[0]
        
        with open(files_name, 'r', encoding='utf-8') as file_md_path:
            file_md_data = file_md_path.readlines()
            count = 1
            if file_md_data:
                file_md_list = []
                for datas in file_md_data:
                    if ")![" in datas:
                        dataslist = datas.replace(")![", ")\n![").split("\n")
                        for datastr in dataslist:
                            file_md_list.append(datastr)
                    else:
                        file_md_list.append(datas)
                    
                for datas in file_md_list:
                    # 正则匹配md文档图片![.*](.*)
                    md_img = re.search(r"!\[(?P<des>.*?)\][(](?P<data>.*)[)]", datas, re.DOTALL)
                    
                    if md_img:
                        des = md_img.groupdict().get("des")
                        img_data = md_img.groupdict().get("data")
                        
                        if img_data:
                            # 处理图片
                            datas = md_img_readline(datas, img_data, md_path_name, proxy, document_name, count, base64_images, intern_imgs, local_imgs)
                            count += 1
                    # 将合成后的本地路径添加到列表
                    md_data_images.append(datas)
            else:
                
                print("\r\t\033[33m[+] 无内容\033[0m")
                return

    # # 计算图片数量
    if len(base64_images) != 0:
        print("\r\t\033[33m[+] 共 %s 个base64图片\033[0m" % len(base64_images))
    elif len(intern_imgs) != 0:
        print("\r\t\033[33m[+] 共 %s 个网络图片\033[0m" % len(intern_imgs))
    elif len(local_imgs) != 0:
        print("\r\t\033[33m[+] 共 %s 个本地图片\033[0m" % len(local_imgs))
    else:
        print("\r\t\033[33m[+] 不存在图片,需人工确认\033[0m")
    
    # 将图片修改的md写入文件
    update_md(md_data_images, md_path_name, document_name)


def process_directory(path, proxy, thread_count):
    """递归处理目录及其子目录中的所有文件"""
    all_files = []
    
    # 递归收集所有文件
    def collect_files(current_path):
        dirs, files = traversal_files(current_path)
        for file in files:
            if file.lower().endswith('.md'):
                all_files.append(file)
        for dir_path in dirs:
            collect_files(dir_path)
    
    # 开始收集文件
    collect_files(path)
    
    if all_files:
        print(f"\r\t\033[33m[+] 共发现 {len(all_files)} 个MD文件\033[0m")
        # 使用线程池处理所有文件
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = [executor.submit(images_save, path, file_path, proxy) for file_path in all_files]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    print(f"\r\t\033[31m[-] 处理文件时发生错误: {exc}\033[0m")
    else:
        print("\r\t\033[33m[+] 未找到MD文件\033[0m")

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
    parser.add_argument("-path", dest="path_name", required=True, help="请输入文档根目录,默认脚本所在目录")
    parser.add_argument("-t", dest="thread", type=int, default="1", help="请输入线程")
    parser.add_argument("-proxy", dest="proxy_name", default="", help="请输入socks5 ip及端口,eg socks5://127.0.0.1:7890")
    args = parser.parse_args()
    
    try:
        args = parser.parse_args()
        process_directory(args.path_name, args.proxy_name, int(args.thread))
    except SystemExit:
        parser.print_help()
    except Exception as e:
        # logger.error(f"执行过程中发生错误: {str(e)}")
        parser.print_help()
        sys.exit(1)