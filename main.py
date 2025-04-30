# -*- coding: UTF-8 -*-
"""
@Filename: main.py
@Author: s1g0day
@Create Date: 2025-03-21 15:20
@Update Date: 2025-04-30 10:00
@Version: 0.0.11
@Description: MM-Wiki文档自动上传工具
@Note:
    文件类型: md
    作用: 上传某个文件夹内所有md文件, 将其保存到空间ID为 `1` 、目录id为 `4314` 的单个目录下
    特点: 支持多级目录、支持图片上传
        图片上传: 上传到目标ID为 `1` 的目录下
        图片路径: 上传后，图片路径会自动修改为 `/image/xxx.png`
        图片上传失败: 会跳过该图片，不影响文档上传
    # Eg: python3 .\main.py -mode add -pid 3268 -sid 11 -path C:\\Users\\Downloads\\文档\\1.内网渗透
"""

import os
import sys
import json
import concurrent.futures
from argparse import ArgumentParser
from lib.logo import logo
from lib.config_loader import Config
from lib.logger_init import logger_init
from lib.Parallel_Processing import ThreadPoolManager, ProcessPoolManager, parallel_map
from modules.Login import serverStatus, login
from modules.Document_save import create_document
from modules.Document_page_modify import page_modify
from modules.Modify_Image import modify_image_path
from modules.Document_Delete_all import delete_all_documents
from modules.Document_MoveDirectory import Move_Directory
from modules.Document_GetId import Get_document_id
from modules.Document_Sort import Sort_Documents
from modules.Getimg_Isalive import batch_check_images

# 初始化日志
logger = logger_init()

class ThreatbookAuto:
    def __init__(self, max_workers):
        self.config = Config.from_json('config/config.json')
        self.mmwiki_url = self.config.TASK.TARGET_BASE_URL
        self.mmwikicookie = self.config.TASK.COOKIE
        self.max_workers = max_workers  # 设置线程池大小，可以根据需要调整
        self.completed_files = 0
        self.total_files = 0
        self.total_md_files = 0  # 总MD文件数
        self.processed_files = 0  # 已处理文件数
        
        # 使用线程池管理器
        self.thread_pool = ThreadPoolManager(
            max_workers=min(20, self.max_workers * 2),
            thread_name_prefix="WikiUploader"
        )

        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'Cookie': self.mmwikicookie,
        }
        
    def traversal_files(self, path):
        '''
        遍历文件目录
        '''
        dirs = []
        files = []
        
        for item in os.scandir(path):
            if item.is_dir():
                dirs.append(item.path)
            elif item.is_file():
                files.append(item.path)
        
        return dirs,files

    def count_md_files(self, path):
        """递归计算所有MD文件数量"""
        count = 0
        for item in os.scandir(path):
            if item.is_dir():
                count += self.count_md_files(item.path)
            elif item.is_file() and item.name.lower().endswith('.md'):
                if "readme" not in item.name.lower():  # 跳过readme文件
                    count += 1
        return count
    def _update_progress(self, future):
        """更新总进度显示"""
        try:
            result = future.result()
            self.processed_files += 1
            progress = (self.processed_files / self.total_md_files) * 100
            logger.info(f"总进度: {self.processed_files}/{self.total_md_files} ({progress:.1f}%)")
        except Exception as e:
            logger.error(f"任务执行失败: {str(e)}")
    
    def process_directory(self, path_name, parent_id, space_id):
        """递归处理目录及文件"""
        # 首次运行时计算总MD文件数
        if self.total_md_files == 0:
            self.total_md_files = self.count_md_files(path_name)
            logger.info(f"[+] 共发现 {self.total_md_files} 个MD文件需要处理")
            
        dirs, files = self.traversal_files(path_name)
        current_dir_name = os.path.basename(path_name)

        # 定义要排除的目录名称
        exclude_dirs = ['resource', 'image', 'images', 'img', 'imgs', 'picture', 'pictures', 'pic', 'pics']
        
        # 首先处理子目录
        for dir_path in dirs:
            dir_name = os.path.basename(dir_path)
            if dir_name.lower() in exclude_dirs:
                logger.info(f"跳过图片目录: {dir_path}")
                continue
            document_type = '2'  # 目录类型
            # 创建目录
            new_parent_id = create_document(self.mmwiki_url, self.headers, self.config.TASK.API.document_save.PATH, parent_id, space_id, dir_name, document_type, logger)
            if new_parent_id:
                # 递归处理子目录内的内容
                self.process_directory(dir_path, new_parent_id, space_id)
                
        # 然后处理当前目录下的文件
        md_files = [f for f in files if f.lower().endswith('.md')]
        total_files = len(md_files)
        if total_files > 0:
            logger.info(f"[+] 当前目录共发现 {total_files} 个 MD 文件")
        
        # 处理当前目录下的所有文件（使用线程池）
        self.completed_files = 0
        
        try:
            # 初始化线程池
            self.thread_pool.init_pool()
            
            # 提交任务到线程池
            for file_path in md_files:
                future = self.thread_pool.submit_task(
                    self.process_file, 
                    path_name, 
                    file_path, 
                    parent_id, 
                    space_id, 
                    current_dir_name
                )
                self.thread_pool.add_callback(future, self._update_progress)
            
            # 等待所有任务完成，使用小的超时值以便能够响应中断
            done, not_done = self.thread_pool.wait_for_tasks(timeout=0.1)
            
            while not_done:
                done, not_done = concurrent.futures.wait(
                    not_done,
                    return_when=concurrent.futures.FIRST_EXCEPTION,
                    timeout=0.1
                )
                
        except KeyboardInterrupt:
            logger.info("\n[!] 检测到 Ctrl+C，正在终止所有任务...")
            self.thread_pool.cancel_all_tasks()
            raise
        except Exception as e:
            logger.error(f"处理文件时发生错误: {str(e)}")
            self.thread_pool.cancel_all_tasks()
            raise
    
    def get_image_main(self, space_id, Document_max):
        """使用多线程处理图片获取任务"""
        document_ids = []
        
        # 解析文档ID范围
        start_id = 0
        end_id = 0

        if "-" in Document_max:
            start_id, end_id = map(int, Document_max.split("-"))
        else:
            end_id = int(Document_max)
        
        # 收集需要处理的文档ID
        for document_id in range(start_id, end_id + 1):
            Doc_status = Get_document_id(
                self.mmwiki_url, 
                self.headers, 
                self.config.TASK.API.document_getId.PATH, 
                document_id, 
                space_id, 
                logger
            )
            document_type = '2' if Doc_status else '1'
            document_ids.append((document_id, document_type))

        # 使用批量检查函数
        try:
            batch_check_images(
                self.mmwiki_url, 
                self.headers, 
                document_ids, 
                logger, 
                max_workers=self.max_workers,  # 文档级并行度
                image_workers=10  # 图片级并行度
            )
        except KeyboardInterrupt:
            logger.info("\n[!] 检测到 Ctrl+C，正在终止所有任务...")
            raise
        except Exception as e:
            logger.error(f"处理图片时发生错误: {str(e)}")
            raise
    
    def run(self, path_name, parent_id, space_id, mode, target_id, delete_parent, only_docs, recursive, Document_max):
        try:
            if mode == "login":
                headers = login(self.mmwiki_url, self.headers, self.config.TASK.API.login.PATH, self.config.TASK.USERNAME, self.config.TASK.PASSWORD, logger)
                if headers:
                    # 更新配置文件中的Cookie
                    self.config.TASK.COOKIE = headers['Cookie']
                    self.config.save()
                    logger.info("登录成功，配置文件已更新")
            elif mode == "status":
                if serverStatus(self.mmwiki_url, self.mmwikicookie, self.headers, self.config.TASK.API.serverStatus.PATH, logger):
                    logger.info("登录成功")
                else:
                    logger.error("登录失败，请检查配置文件或网络连接")
            elif mode == "add":
                self.process_directory(path_name, parent_id, space_id)
            elif mode == "delall":
                delete_all_documents(self.mmwiki_url, self.headers, self.config.TASK.API.delete_all.PATH, parent_id, space_id, delete_parent, logger)
            elif mode == "move":
                Get_document_id(self.mmwiki_url, self.headers, self.config.TASK.API.document_getId.PATH, parent_id, space_id, logger)
                Move_Directory(self.mmwiki_url, self.headers, self.config.TASK.API.document_moveDirectory.PATH, parent_id, target_id, only_docs, logger)
            elif mode == "sort":
                Get_document_id(self.mmwiki_url, self.headers, self.config.TASK.API.document_getId.PATH, parent_id, space_id, logger)
                Sort_Documents(self.mmwiki_url, self.headers, self.config.TASK.API.document_sort.PATH, parent_id, space_id, recursive, logger)
            elif mode == "alive":
                self.get_image_main(space_id, Document_max)
            else:
                logger.error("无效的执行模式")
        except KeyboardInterrupt:
            logger.info("\n[!] 程序已终止")
            sys.exit(0)

if __name__ == "__main__":
    logo()
    parser = ArgumentParser(description='MM-Wiki文档自动上传工具')
    parser.add_argument("-path", dest="path_name", help="请输入文档根目录路径（支持包含空格的路径）")
    parser.add_argument("-id", dest="Document_max", help="请输入文档ID或范围,eg: 4385 or 784-4385")
    parser.add_argument("-sid", dest="space_id", type=int, default=1, help="请输入空间ID，默认为1")
    parser.add_argument("-pid", dest="parent_id", type=int, help="请输入目录ID")
    parser.add_argument("-t", dest="thread", type=int, default=1, help="线程池大小，默认为1")
    parser.add_argument("-m", dest="mode", choices=['status', 'login','add', 'delall', 'move', 'sort', 'alive'], required=True, 
                      help="执行模式：status-检测cookie，login-仅登录，add-写入文档，delall-删除目录下所有文档，move-移动目录,sort-排序,alive-检测图片链接是否可访问")
    parser.add_argument("-tid", dest="target_id", type=int, help="移动模式的目标目录ID")
    parser.add_argument("-delete_parent", dest="delete_parent", choices=['true', 'false'], default='true',
                      help="删除模式是否删除父目录：true-父目录(默认)，false-不删除")
    parser.add_argument("-recursive", dest="recursive", choices=['true', 'false'], default='true',
                      help="是否递归排序子目录：true-递归子目录(默认)，false-不递归")
    parser.add_argument("-only_docs", dest="only_docs", choices=['true', 'false'], default='false',
                      help="移动模式是否仅移动文档：true-仅移动文档，false-移动所有内容(默认)")

    try:
        args = parser.parse_args()
        
        # 如果是写入模式，检查必要参数
        if args.mode == "add":
            if not args.path_name or not args.parent_id:
                logger.error("写入模式需要指定 path 和 pid 参数")
                sys.exit(1)
            # 规范化路径
            path_name = os.path.normpath(args.path_name)
            if not os.path.exists(path_name):
                logger.error(f"指定的路径不存在: {path_name}")
                sys.exit(1)
        elif args.mode == "delall":
            if not args.parent_id:
                logger.error("删除模式需要指定 pid 参数")
                sys.exit(1)
        elif args.mode == "move":
            if not args.parent_id or not args.target_id:
                logger.error("移动模式需要指定 pid 和 tid 参数")
                sys.exit(1)
        elif args.mode == "alive":
            if not args.Document_max:
                logger.error("写入模式需要指定 id 参数")
                sys.exit(1)
        auto = ThreatbookAuto(max_workers=args.thread)
        auto.run(args.path_name, args.parent_id, args.space_id, args.mode, args.target_id, args.delete_parent, args.only_docs, args.recursive, args.Document_max)
    # except SystemExit:
    #     parser.print_help()
    except Exception as e:
        logger.error(f"执行过程中发生错误: {str(e)}")
        parser.print_help()
        sys.exit(1)