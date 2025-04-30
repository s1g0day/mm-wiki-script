# -*- coding: UTF-8 -*-
'''
@Create Date: 2025-04-29 15:12
@Update Date: 2025-04-30 16:12
@Description: 遍历获取wiki内图片存活, 需开启空间分享权限
'''

import re
import os
import sys
import json
import html
import urllib3
import datetime
import requests
import threading
import concurrent.futures
from queue import Queue
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 预编译正则表达式
IMG_PATTERN = re.compile(r'\!\[(?P<ext>.*?)\]\((?P<data>[^\)]+)\)', re.DOTALL)
HTML_TAG_PATTERN = re.compile(r'<[^>]+>', re.S)

def requests_test(url, headers, params=None):
    """发送HTTP请求并处理响应"""
    try:
        if params is None:
            req = requests.get(url, headers=headers, verify=False, timeout=(3.05, 10))
        else:
            req = requests.get(url, params=params, headers=headers, verify=False, timeout=(3.05, 10))
        req.encoding = req.apparent_encoding
        return req if req.status_code != 404 else False
    except requests.RequestException as e:
        logger.error(f"请求错误: {url}, 原因: {str(e)}")
        return False

def save_txt(file_name, text):
    """安全地保存文本到文件"""
    try:
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, 'a+', encoding='utf-8') as f:
            f.writelines(text)
    except IOError as e:
        logger.error(f"文件写入错误: {str(e)}")

def check_document_access(req, doc_id, logger):
    """检查文档访问权限"""
    if not req:
        logger.error(f"文档ID: {doc_id}, 连接错误")
        return False

    if "文档不存在" in req.text:
        logger.info(f"文档ID: {doc_id}, 文档不存在")
        return False
        
    if "您没有权限访问该空间" in req.text:
        logger.info(f"文档ID: {doc_id}, 您没有权限访问该空间")
        return False
    
    return True

def log_progress(logger, current, total, task_name, doc_id=None, interval=10):
    """统一的进度显示函数"""
    if (current+1) % interval == 0 or (current+1) == total:
        msg = f"已{task_name}: {current+1}/{total}"
        if doc_id:
            msg = f"文档ID: {doc_id}, {msg}"
        logger.info(msg)

def extract_image_links(html_text):
    """从HTML文本中提取图片链接"""
    datas_imgs = []
    
    # 解码HTML实体
    html_text = html.unescape(html_text)
    
    # 移除HTML标签
    result = HTML_TAG_PATTERN.sub('', html_text)
    
    # 按行分割并提取图片链接
    for line in result.split("\n"):
        if "](" in line:
            matches = IMG_PATTERN.finditer(line)
            for match in matches:
                data = match.groupdict().get("data")
                if data and data.strip():
                    datas_imgs.append(data.strip())
    
    return datas_imgs

def batch_check_images(url, headers, document_ids, logger, max_workers=5, image_workers=10):
    """批量检查多个文档的图片"""
    image_links_queue = Queue()
    logger.info(f"开始批量检查 {len(document_ids)} 个文档的图片...")
    
    # 标准化输入格式
    normalized_ids = [(item if isinstance(item, (tuple, list)) else (item, '1')) 
                     for item in document_ids]
    
    def extract_document_images(doc_id, doc_type):
        """提取单个文档的图片链接"""
        try:
            urlpath = url + "/page/display"
            params = {'document_id': doc_id}
            req = requests_test(urlpath, headers, params=params)
            
            if not check_document_access(req, doc_id, logger):
                return
            
            datas_imgs = extract_image_links(req.text)
            if datas_imgs:
                image_links_queue.put({
                    'id': doc_id,
                    'data': datas_imgs
                })
                logger.info(f"文档ID: {doc_id}, 提取到 {len(datas_imgs)} 张图片")
            else:
                logger.info(f"文档ID: {doc_id}, 无图片")
        except Exception as e:
            logger.error(f"文档ID: {doc_id}, 提取图片链接时出错: {str(e)}")
    
    # 第一阶段：提取所有文档的图片链接
    logger.info("第一阶段：开始提取所有文档的图片链接...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(extract_document_images, doc_id, doc_type) 
                  for doc_id, doc_type in normalized_ids]
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                future.result()
                log_progress(logger, i, len(futures), "提取")
            except Exception as e:
                logger.error(f"提取文档图片链接时出错: {str(e)}")
    
    # 收集队列中的所有数据
    image_links = []
    while not image_links_queue.empty():
        image_links.append(image_links_queue.get())
    
    if not image_links:
        logger.info("未提取到任何图片，检查结束")
        return
    
    # 统计提取到的图片总数
    total_images = sum(len(item['data']) for item in image_links)
    logger.info(f"第一阶段完成，共从 {len(image_links)} 个文档中提取到 {total_images} 张图片")
    
    # 将第一阶段结果保存到CSV文件
    csv_file = 'logs/image_extraction.csv'
    try:
        os.makedirs(os.path.dirname(csv_file), exist_ok=True)
        with open(csv_file, 'a+', encoding='utf-8', newline='') as f:
            # 检查文件是否为空
            f.seek(0)
            is_empty = not f.read(1)
            f.seek(0)
            
            # 只有在文件为空时才写入表头
            if is_empty:
                f.write("Doc_Id,Img_Url\n")
            
            # 写入图片数据
            for item in image_links:
                doc_id = item['id']
                for link in item['data']:
                    f.write(f"{doc_id},{link}\n")
            
        logger.info(f"第一阶段结果已保存到: {csv_file}")
    except IOError as e:
        logger.error(f"保存CSV文件时出错: {str(e)}")

    # 添加手动确认步骤
    while True:
        confirm = input("\n是否继续进行第二阶段验证？(Y/N): ").strip().upper()
        if confirm in ['Y', 'N']:
            break
        print("请输入 Y 或 N")
    
    if confirm == 'N':
        logger.info("用户选择退出，检查结束")
        return

    # 调用独立的验证函数进行第二阶段验证
    invalid_links = verify_all_images(url, headers, image_links, logger, max_workers, image_workers)
    logger.info(f"批量检查完成，共处理 {len(normalized_ids)} 个文档")
    return invalid_links

def verify_image(base_url, headers, document_id, img_link, logger):
    """验证单个图片链接是否可访问"""
    try:
        if img_link.startswith(("http://", "https://")):
            logger.warning(f"文档ID: {document_id}, 发现外部链接: {img_link}")
            return img_link
        
        full_img_link = urljoin(base_url, img_link.lstrip('/'))
        result = requests_test(full_img_link, headers)
        if not result:
            logger.error(f"文档ID: {document_id}, {full_img_link}, 不可访问")
            return full_img_link
    except Exception as e:
        logger.error(f"文档ID: {document_id}, 验证图片时出错: {str(e)}")
        return img_link
    return None

def verify_all_images(url, headers, image_links, logger, max_workers=5, image_workers=10):
    """验证所有文档的图片链接是否可访问"""
    logger.info("第二阶段：开始验证所有图片链接...")
    invalid_links_dict = {}
    global_lock = threading.Lock()
    total_docs = len(image_links)
    processed_docs = 0
    progress_lock = threading.Lock()
    # 添加终止标志
    stop_event = threading.Event()

    def verify_document_images(doc_id, links):
        """验证单个文档的所有图片链接"""
        # 检查是否需要终止
        if stop_event.is_set():
            return
            
        nonlocal processed_docs
        invalid_links = []
        
        # 预处理：将链接分类为内部链接和外部链接
        external_links = []
        internal_links = []
        for link in links:
            if link.startswith(("http://", "https://")):
                external_links.append(link)
            else:
                internal_links.append(link)
        
        # 直接处理外部链接
        if external_links:
            invalid_links.extend(external_links)
            logger.warning(f"文档ID: {doc_id}, 发现 {len(external_links)} 个外部链接")
        
        # 批量处理内部链接
        if internal_links and not stop_event.is_set():
            # 创建所有完整的URL
            full_urls = [urljoin(url, link.lstrip('/')) for link in internal_links]
            
            # 使用信号量限制并发请求数
            semaphore = threading.Semaphore(10)
            
            def check_url(full_url, original_url):
                # 检查是否需要终止
                if stop_event.is_set():
                    return None
                    
                with semaphore:
                    try:
                        result = requests_test(full_url, headers)
                        if not result:
                            return original_url
                    except Exception as e:
                        logger.error(f"文档ID: {doc_id}, 验证图片时出错: {str(e)}")
                        return original_url
                    return None
            
            # 并发检查所有URL
            with concurrent.futures.ThreadPoolExecutor(max_workers=image_workers) as executor:
                future_to_url = {
                    executor.submit(check_url, full_url, orig_url): orig_url 
                    for full_url, orig_url in zip(full_urls, internal_links)
                }
                
                # 使用as_completed快速处理结果
                for future in concurrent.futures.as_completed(future_to_url):
                    if stop_event.is_set():
                        executor.shutdown(wait=False)
                        break
                        
                    try:
                        result = future.result(timeout=10)
                        if result:
                            invalid_links.append(result)
                    except concurrent.futures.TimeoutError:
                        orig_url = future_to_url[future]
                        logger.error(f"文档ID: {doc_id}, 验证超时: {orig_url}")
                        invalid_links.append(orig_url)
        
        # 更新无效链接字典
        if invalid_links:
            with global_lock:
                invalid_links_dict[doc_id] = invalid_links
                logger.info(f"文档ID: {doc_id}, 发现 {len(invalid_links)}/{len(links)} 张异常图片")
        
        # 更新进度
        with progress_lock:
            nonlocal processed_docs
            processed_docs += 1
            if processed_docs % 10 == 0 or processed_docs == total_docs:
                logger.info(f"已验证: {processed_docs}/{total_docs} 个文档的图片")
    
    try:
        # 使用线程池处理所有文档
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(verify_document_images, item['id'], item['data']) 
                for item in image_links
            ]
            
            # 等待所有任务完成或遇到中断
            done, not_done = concurrent.futures.wait(
                futures,
                return_when=concurrent.futures.FIRST_EXCEPTION,
                timeout=0.1
            )
            
            while not_done:
                try:
                    done, not_done = concurrent.futures.wait(
                        not_done,
                        return_when=concurrent.futures.FIRST_EXCEPTION,
                        timeout=0.1
                    )
                except KeyboardInterrupt:
                    logger.info("\n[!] 检测到 Ctrl+C，正在终止所有任务...")
                    stop_event.set()  # 设置终止标志
                    # 取消所有未完成的任务
                    for future in not_done:
                        future.cancel()
                    # 等待正在执行的任务完成
                    concurrent.futures.wait(not_done, timeout=5)
                    logger.info("已终止所有任务")
                    return invalid_links_dict
    
    except Exception as e:
        logger.error(f"验证过程中发生错误: {str(e)}")
        stop_event.set()
        raise
    
    # 保存结果
    if invalid_links_dict and not stop_event.is_set():
        logger.info(f"检查完成，共发现 {len(invalid_links_dict)} 个文档存在异常图片")
        
        with open('logs/http_imgs.txt', 'a+', encoding='utf-8') as f:
            f.write(f"\n--- 检查时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n\n")
            for doc_id, links in invalid_links_dict.items():
                f.write(f"文档ID: {doc_id}, 存在外链或异常图片\n")
                for link in links:
                    f.write(f"{link}\n")
                f.write("\n")
    else:
        logger.info("检查完成，所有图片均正常")
    
    return invalid_links_dict