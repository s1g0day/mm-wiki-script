# -*- coding: UTF-8 -*-
'''
识别md文档内图片格式
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
import requests
import threadpool
import urllib3

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
    
    img_path_name = img_path + "\\image\\" + filename
    
    # 判断目录是否存在
    if os.path.exists(img_path_name) == False:
        os.mkdir(img_path_name)
        
    # 判断是否是windows绝对路径
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

def Pictures_processing(md_path_name, img_data, proxy, filename, count, base64_images, intern_imgs, local_imgs):
    # 处理base64图片
    if "data:image" in img_data:
        print("\r\t\033[32m[*] %d : base64图片\033[0m" % count)
        datas = base64_decode_image(md_path_name, img_data, filename)
        if datas != None:
            base64_images.append(datas)
    elif "http://" in img_data or "https://" in img_data:
        print("\r\t\033[32m[*] %d : 存在网络图片,需转换为本地\033[0m" % count)
        datas = intern_save_img(md_path_name, img_data, proxy, filename)
        if datas != None:
            intern_imgs.append(datas)
    else:
        print("\r\t\033[32m[*] %d : 本地图片或其他格式\033[0m" % count)
        datas = local_save_img(md_path_name, img_data, filename)
        if datas != None:
            local_imgs.append(datas)

    return datas, base64_images, intern_imgs, local_imgs

def update_md(markdown_text, md_path_name, filename):
    # print(markdown_text)
    print("\r\t\033[33m[+] 更新md文档\033[0m")
    # 将替换后的文档保存到本地
    # for a in markdown_text:
        # with open(md_path_name + "\\" + filename + '.md', 'a+', encoding='utf-8') as file3:
            # file3.write(a)   
    markdown_test_data = "".join(markdown_text)
    with open(md_path_name + "\\" + filename + '.md', 'w', encoding='utf-8') as file3:
        file3.write(markdown_test_data)

def md_img_readline(datas, img_data, md_path_name, proxy, filename, count, base64_images, intern_imgs, local_imgs):
    if ")](" in img_data:
        img_data_spl = img_data.split(")](", 1)[0]
        result_data, base64_images, intern_imgs, local_imgs = Pictures_processing(md_path_name, img_data_spl, proxy, filename, count, base64_images, intern_imgs, local_imgs)
        if result_data == img_data:
            datas = datas
        else:
            datas = result_data
    else:
        result_data, base64_images, intern_imgs, local_imgs = Pictures_processing(md_path_name, img_data, proxy, filename, count, base64_images, intern_imgs, local_imgs)
        if result_data == img_data:
            datas = datas
        else:
            datas = result_data
    count += 1
    return datas, count, base64_images, intern_imgs, local_imgs
def images_save(md_path_name, files_name, proxy):

    print("文件名:",files_name)
    # 图片列表
    base64_images = []
    intern_imgs = []
    local_imgs = []

    # md内容
    md_data_images = []

    # 获取文件完整路径和后缀
    filext = files_name.split("\\")[-1].split(".")[-1]
    # print(filext)
    
    if filext == "md":
    
        # 获取文件名
        filename = files_name.split("\\")[-1].split(".md")[0]
        # print(filename)
        
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
                        # print(des)
                        # print(img_data)
                        
                        if img_data:
                            if ")](" in img_data:
                                img_data_spl = img_data.split(")](", 1)[0]
                                result_data, base64_images, intern_imgs, local_imgs = Pictures_processing(md_path_name, img_data_spl, proxy, filename, count, base64_images, intern_imgs, local_imgs)
                                if result_data == img_data:
                                    datas = datas
                                else:
                                    datas = result_data
                            else:
                                result_data, base64_images, intern_imgs, local_imgs = Pictures_processing(md_path_name, img_data, proxy, filename, count, base64_images, intern_imgs, local_imgs)
                                if result_data == img_data:
                                    datas = datas
                                else:
                                    datas = result_data
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
    update_md(md_data_images, md_path_name, filename)


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
    
    if len(sys.argv) <= 1:
        parser.print_help()
    else:
        func_vars = []
        dirs,files = traversal_files(args.path_name)
        for i in files:
            lst_vars = [args.path_name, i, args.proxy_name]
            func_var = (lst_vars, None)
            func_vars.append(func_var)
        if func_vars:
            pool = threadpool.ThreadPool(int(args.thread))
            req = threadpool.makeRequests(images_save, func_vars)
            for r in req:
                pool.putRequest(r)
            pool.wait()
        else:
            print("\r\t\033[33m[+] 指定目录为空\033[0m")