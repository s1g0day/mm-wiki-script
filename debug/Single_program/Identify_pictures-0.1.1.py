# -*- coding: UTF-8 -*-
'''
@Createtime: 2023/1/11 9:51
@Updatetime: 2025/4/17 23:00
@Version: 0.1.1
@description: 识别md文档内图片格式
@note:
    图片格式: 本地图片、网络图片、base64图片

    测试base64图片: python3 Identify_pictures.py -path E:\\work\\mm-wiki\\wiki\\1_file\\1_base64
    测试本地图片: python3 Identify_pictures.py -path E:\\work\\mm-wiki\\wiki\\1_file\\2_local
    测试网络图片: python3 Identify_pictures.py -path E:\\work\\mm-wiki\\wiki\\1_file\\3_http
                python3 Identify_pictures.py -path E:\\work\\mm-wiki\\wiki\\1_file\\3_http -proxy 127.0.0.1:7890
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
from moviepy.video.io.VideoFileClip import VideoFileClip
from lib.hander_random import requests_headers
from lib.logger_init import logger_init
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#/ 初始化日志
logger = logger_init()

def traversal_files(path):
    """
    递归遍历目录及文件

    Args:
        path: 目录路径
    """
    dirs = []
    files = []
    
    for item in os.scandir(path):
        if item.is_dir():
            dirs.append(item.path)
        elif item.is_file():
            files.append(item.path)

    return dirs,files

def ensure_image_dir(md_path_name, filename, ext='jpg'):
    """
    确保图片保存目录存在，如果不存在则创建，并生成唯一的图片文件名
    
    Args:
        md_path_name: MD文件所在目录
        filename: 文件名（用于创建子目录）
        ext: 图片扩展名，默认为jpg
    
    Returns:
        str: 完整的图片文件路径
    """
    # 创建主图片目录
    img_path = os.path.join(md_path_name, "image")
    if not os.path.exists(img_path):
        os.mkdir(img_path)
    
    """
    # 创建文件专属的图片子目录
    # 限制文件夹名称长度，防止超出 Windows 路径长度限制
    if len(filename) > 50:  # 可以根据需要调整长度
        filename = filename[:47] + "..."
    
    img_path_name = os.path.join(img_path, filename)
    if not os.path.exists(img_path_name):
        os.makedirs(img_path_name, exist_ok=True)
    """
    # 生成唯一的图片文件名，确保扩展名格式正确
    ext = ext.lstrip('.')  # 移除扩展名开头的点号
    image_name = os.path.join(img_path, f"image-{uuid.uuid4()}.{ext}")

    # 规范化路径
    image_name = os.path.normpath(image_name)
    return image_name

def base64_decode_image(md_path_name, files_name, img_data, filename):
    # 1、信息提取
    result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", img_data, re.DOTALL)
    if result:
        ext = result.groupdict().get("ext")
        data = result.groupdict().get("data")
    else:
        raise Exception("Do not parse!")
    
    # 2、base64解码
    img = base64.urlsafe_b64decode(data)
    
    # 3、二进制文件保存
    image_name = ensure_image_dir(md_path_name, filename, ext)
    with open(image_name, "wb") as f:
        f.write(img)
    
    # 覆盖datas的图片内容
    datas = f"\n\n![]({image_name})\n\n"

    return datas

def convert_mp4_to_gif(mp4_path, md_path_name, filename, output_dir=None, fps=10, resize_factor=0.5, max_size_mb=50):
    """
    将MP4文件转换为GIF
    
    Args:
        mp4_path: MP4文件路径
        output_dir: 输出目录，默认为MP4文件所在目录
        fps: GIF帧率，默认10
        resize_factor: 尺寸缩放因子，默认0.5（减小文件大小）
        max_size_mb: MP4文件大小限制，单位MB，默认50MB
    
    Returns:
        str: 生成的GIF文件路径
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(mp4_path):
            logger.error(f"[-] MP4文件不存在: {mp4_path}")
            return None
        
        # 检查文件大小
        file_size_mb = os.path.getsize(mp4_path) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            logger.error(f"[-] MP4文件过大: {file_size_mb:.2f}MB，超过限制{max_size_mb}MB")
            return None
        
        # 使用ensure_image_dir生成GIF保存路径
        gif_path = ensure_image_dir(md_path_name, filename, 'gif')
        
        # 加载视频
        logger.info(f"[*] 正在加载视频: {mp4_path}")
        video_clip = VideoFileClip(mp4_path)
        
         # 调整大小
        if resize_factor != 1:
            width = int(video_clip.w * resize_factor)
            height = int(video_clip.h * resize_factor)
            target_resolution = (width, height)
            video_clip = VideoFileClip(mp4_path, target_resolution=target_resolution)
        
        # 转换为GIF
        logger.info(f"[*] 正在转换为GIF，帧率: {fps}")
        video_clip.write_gif(gif_path, fps=fps)
        
        # 关闭视频
        video_clip.close()
        # 删除临时MP4文件
        os.remove(mp4_path)
        
        # 检查生成的GIF大小
        gif_size_mb = os.path.getsize(gif_path) / (1024 * 1024)
        logger.info(f"[+] 转换完成: {gif_path}，GIF大小: {gif_size_mb:.2f}MB")
        return gif_path
        
    except Exception as e:
        logger.error(f"[-] 转换过程中发生错误: {str(e)}")
        return None

def download_pics_common(url, md_path_name, files_name, filename, proxy=None):
    """统一的图片下载处理函数"""
    def try_download(use_proxy=False):
        """尝试下载函数"""
        try:
            if use_proxy and proxy:
                s = requests.session()
                s.proxies = {'https': proxy}
                response = s.get(url, timeout=(5, 15), verify=False)
            else:
                response = requests.get(url, timeout=(5, 15), verify=False)
            
            if response.status_code == 200:
                if ".mp4" in url:
                    logger.info(f"[*] {files_name} 包含mp4: {url}")
                    temp_mp4_path = ensure_image_dir(md_path_name, filename, 'mp4')
                    with open(temp_mp4_path, 'wb') as f:
                        f.write(response.content)
                    return temp_mp4_path if os.path.exists(temp_mp4_path) else url
                else:
                    ext = 'gif' if ".gif" in url else 'jpg'
                    if ext == 'gif':
                        logger.info(f"[*] {files_name} 包含gif, 直接下载: {url}")
                    
                    image_name = ensure_image_dir(md_path_name, filename, ext)
                    with open(image_name, 'wb') as f:
                        f.write(response.content)
                    return os.path.normpath(image_name)
            return None
        except Exception as e:
            logger.error(f"[-] {files_name} 下载失败 {'(使用代理)' if use_proxy else '(不使用代理)'}: {url}, 错误: {str(e)}")
            return None

    try:
        # 初始化 result 变量
        result = None

        # 1. 如果设置了代理，则尝试使用代理
        if proxy:
            logger.info(f"[*] {files_name} 尝试使用代理下载: {url}")
            result = try_download(use_proxy=True)
            if result:
                return result
        
        # 2. 如果使用代理失败，则尝试不使用代理下载
        result = try_download(use_proxy=False)
        if result:
            return result
        
        # 3. 如果所有尝试都失败，返回原URL
        logger.error(f"[-] {files_name} 所有下载尝试均失败: {url}")
        return url

    except Exception as e:
        logger.error(f"[-] {files_name} 下载过程发生错误: {url}, 错误: {str(e)}")
        return url

def intern_save_img(md_path_name, files_name, img_data, filename, proxy):
    """处理网络图片下载"""
    path = download_pics_common(img_data, md_path_name, files_name, filename, proxy)
    return f"\n\n![]({path})\n\n"

def local_img_path(md_path_name, img_data):
    """
    规范化本地图片路径
    
    Args:
        md_path_name: MD文件所在目录
        img_data: 图片路径
        
    Returns:
        str: 规范化后的绝对路径
    """
    try:
        # 处理特殊字符
        img_data = img_data.split('?')[0]  # 移除URL参数部分
        img_data = img_data.replace(',', '_')  # 替换逗号为下划线
        
        # 判断是否为绝对路径
        if os.path.isabs(img_data) or re.match(r"^([a-zA-Z]):", img_data[:2]):
            abs_path = img_data
        else:
            abs_path = os.path.join(os.path.abspath(md_path_name), img_data)
        
        # 规范化路径
        return os.path.normpath(abs_path)
    except Exception as e:
        logger.error(f"路径处理错误: {str(e)}, 原始路径: {img_data}")
        return img_data

def check_img_exist(md_path_name, filename, img_name):
    """
    检查图片是否已经在目标目录
    """
    filepath = os.path.dirname(img_name)
    img_dir = os.path.join(md_path_name, "image", filename)

    if filepath == img_dir:
        return True
    else:
        return False
def local_save_img(md_path_name, files_name, img_data, filename):
    '''
    判断地址是不是本地图片
    判断图片是否存在
    将图片移动到当前目录
    返回图片md地址
    '''
    # 使用改进的路径处理函数
    img_data = local_img_path(md_path_name, img_data)
    logger.info(f"[*] {files_name} 处理后的图片路径: {img_data}")
    # 判断是否能打开
    if os.path.exists(img_data):
        logger.info(f"[*] {files_name} 图片文件存在: {img_data}")
        # 获取图片扩展名
        ext = os.path.splitext(img_data)[1].lower()
        # 处理MP4文件
        if ext == '.mp4':
            logger.info(f"[*] {files_name} 包含本地mp4: {img_data}")
            try:
                
                if check_img_exist(md_path_name, filename, img_data):
                    datas = f"\n\n![]({img_data})\n\n"
                    return datas
                else:
                    # 复制MP4到临时位置
                    logger.info(f"[*] {files_name} 图片路径与目标目录不同，开始处理: {img_data}")
                    temp_mp4_path = ensure_image_dir(md_path_name, filename, 'mp4')
                    shutil.copy(img_data, temp_mp4_path)
                    
                    # 转换为GIF
                    # gif_path = convert_mp4_to_gif(temp_mp4_path, md_path_name, filename)
                    gif_path = temp_mp4_path
                    if gif_path:
                        datas = f"\n\n[{img_data}]({gif_path})\n\n"
                        return datas
            except Exception as e:
                logger.error(f"[-] {files_name} MP4转GIF失败: {str(e)}")
                datas = f"\n\n![]({img_data})\n\n"
                return datas
        # 处理其他图片文件
        if check_img_exist(md_path_name, filename, img_data):
            datas = f"\n\n![]({img_data})\n\n"
            return datas
        else:
            # 如果不存在，则生成新的路径并复制文件
            logger.info(f"[*] {files_name} 图片路径与目标目录不同，开始处理: {img_data}")
            image_name = ensure_image_dir(md_path_name, filename, ext)
            # shutil模块复制文件
            shutil.copy(img_data, image_name)

            # 覆盖datas的图片内容
            datas = f"\n\n![]({image_name})\n\n"
            return datas
    else:
        logger.error(f"[-] {files_name} 本地图片无法打开: {img_data}")
        logger.error(f"[-] 完整路径: {os.path.abspath(img_data)}")
        datas = f"\n\n![]({img_data})\n\n"
        return datas

def Pictures_processing(md_path_name, files_name, img_path, filename, count, base64_images, intern_imgs, local_imgs, proxy):
    """
    识别图片格式
    本地图片、网络图片、base64图片
    """
    if "data:image" in img_path:
        logger.info(f"[*] {files_name} {count} : base64图片")
        datas = base64_decode_image(md_path_name, files_name, img_path, filename)
        if datas != None:
            base64_images.append(datas)
    elif "http://" in img_path or "https://" in img_path:
        logger.info(f"[*] {files_name} {count} : 存在网络图片,需转换为本地")
        img_path = unquote(img_path)
        datas = intern_save_img(md_path_name, files_name, img_path, filename, proxy)
        if datas != None:
            intern_imgs.append(datas)
    else:
        logger.info(f"[*] {files_name} {count} : 本地图片或其他格式")
        img_path = unquote(img_path)
        datas = local_save_img(md_path_name, files_name, img_path, filename)
        if datas != None:
            local_imgs.append(datas)

    return datas, base64_images, intern_imgs, local_imgs

def update_md(markdown_text, files_name):
    logger.info("[+] 更新md文档")
    # 将替换后的文档保存到本地  
    markdown_test_data = "".join(markdown_text)
    with open(files_name, 'w', encoding='utf-8', errors='ignore') as file3:
        file3.write(markdown_test_data)

def md_img_readline(md_path_name, files_name, datas, img_data, document_name, count, base64_images, intern_imgs, local_imgs, proxy):
    if ")](" in img_data:
        # 处理带跳转链接的图片
        img_parts = img_data.split(")](")
        if len(img_parts) >= 2:
            # 提取图片URL或本地路径部分
            img_url = img_parts[0]
            # 处理图片URL或本地路径    
            result_data, base64_images, intern_imgs, local_imgs = Pictures_processing(md_path_name, files_name, img_url, document_name, count, base64_images, intern_imgs, local_imgs, proxy)
            
            if result_data == img_data:
                datas = datas
            else:
                datas = result_data
    else:
        result_data, base64_images, intern_imgs, local_imgs = Pictures_processing(md_path_name, files_name, img_data, document_name, count, base64_images, intern_imgs, local_imgs, proxy)
        if result_data == img_data:
            datas = datas
        else:
            datas = result_data
    return datas

def images_save(md_path_name, files_name, proxy):

    logger.info(f"{'*' * 12}文件名: {files_name}{'*' * 12}")
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
                            datas = md_img_readline(md_path_name, files_name, datas, img_data, document_name, count, base64_images, intern_imgs, local_imgs, proxy)
                            count += 1
                    # 将合成后的本地路径添加到列表
                    md_data_images.append(datas)
            else:
                logger.info("\033[33m[+] 无内容\033[0m")
                return

    # # 计算图片数量
    if len(base64_images) != 0:
        logger.info(f"[+] {files_name} 共 {len(base64_images)} 个base64图片")
    elif len(intern_imgs) != 0:
        logger.info(f"[+] {files_name} 共 {len(intern_imgs)} 个网络图片")
    elif len(local_imgs) != 0:
        logger.info(f"[+] {files_name} 共 {len(local_imgs)} 个本地图片")
    else:
        logger.info("[+] 不存在图片,需人工确认")
    
    # 将图片修改的md写入文件
    update_md(md_data_images, files_name)

def process_directory(path, proxy, thread_count):
    """递归处理目录及其子目录中的所有文件"""
    all_files = []
    
    # 递归收集所有文件
    def collect_files(current_path):
        try:
            dirs, files = traversal_files(current_path)
            for file in files:
                if file.lower().endswith('.md'):
                    all_files.append(file)
            for dir_path in dirs:
                collect_files(dir_path)
        except Exception as e:
            logger.error(f"收集文件时出错: {current_path}, 错误: {str(e)}")
    
    # 开始收集文件
    collect_files(path)
    
    if all_files:
        logger.info("[+] 开始处理MD文件")
        total_files = len(all_files)
        logger.info(f"[+] 共发现 {total_files} 个MD文件")
        
        completed_files = 0
        executor = None
        
        def process_file(file_path):
            nonlocal completed_files
            try:
                images_save(path, file_path, proxy)
            except Exception as exc:
                logger.error(f"[-] 处理文件时发生错误: {exc}")
            finally:
                completed_files += 1
                progress = (completed_files / total_files) * 100
                logger.info(f"[+] 处理进度: {completed_files}/{total_files} ({progress:.1f}%)")
        
        try:
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=thread_count)
            futures = [executor.submit(process_file, file_path) for file_path in all_files]
            
            done, not_done = concurrent.futures.wait(
                futures, 
                return_when=concurrent.futures.FIRST_EXCEPTION,
                timeout=0.1
            )
            
            while not_done:
                done, not_done = concurrent.futures.wait(
                    not_done, 
                    return_when=concurrent.futures.FIRST_EXCEPTION,
                    timeout=0.1
                )
                
        except KeyboardInterrupt:
            logger.info("\n[!] 检测到 Ctrl+C，正在终止所有任务...")
            if executor:
                for future in futures:
                    future.cancel()
                executor.shutdown(wait=False)
            raise
        except Exception as e:
            logger.error(f"执行过程中发生错误: {str(e)}")
            if executor:
                executor.shutdown(wait=False)
            raise
        finally:
            if executor:
                executor.shutdown(wait=False)
            
        logger.info("[+] 所有文件处理完成")
    else:
        logger.info("[+] 未找到MD文件")

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument("-path", dest="path_name", required=True, help="请输入文档根目录,默认脚本所在目录")
    parser.add_argument("-t", dest="thread", type=int, default="1", help="请输入线程")
    parser.add_argument("-proxy", dest="proxy_name", default="", help="请输入socks5 ip及端口,eg socks5://127.0.0.1:7890")
    args = parser.parse_args()
    
    try:
        args = parser.parse_args()
        if args.path_name:
            args.path_name = os.path.normpath(args.path_name)
            if not os.path.exists(args.path_name):
                logger.error(f"指定的路径不存在: {args.path_name}")
                sys.exit(1)
            try:
                process_directory(args.path_name, args.proxy_name, int(args.thread))
            except KeyboardInterrupt:
                logger.info("\n[!] 程序已终止")
                sys.exit(0)
    except Exception as e:
        logger.error(f"执行过程中发生错误: {str(e)}")
        parser.print_help()
        sys.exit(1)