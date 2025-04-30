# -*- coding: UTF-8 -*-
#Filename: auto_v2.py
#Author: anonymous
#Create Date: 2025-03-21
#Update Date: 2025-03-22
#Version: 0.0.3
#Description: 自动上传文档到MM-Wiki

'''
文件类型: md
作用: 上传某个文件夹内所有md文件, 将其保存到空间ID为 `1` 、目录id为 `4314` 的单个目录下
缺点: 暂时无法自动保存文件内的图片
范围: 单目录
# Eg: python3 .\mm-1.py -url http://192.168.232.154:8080 -pid 3268 -sid 11 -t 2 -path C:\\Users\\FH287EGHH7823\\Downloads\\文档\\1.内网渗透
'''

import os
import sys
import json
import urllib3
import requests
from urllib.parse import unquote
from argparse import ArgumentParser
from lib.config_loader import Config
from lib.logger_init import logger_init
from modules.Modify_Image import image_upload

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


#/ 初始化日志
logger = logger_init()

class ThreatbookAuto:
    def __init__(self):
        self.config = Config.from_json('config/config.json')
        self.mmwiki_url = self.config.TASK.TARGET_BASE_URL
        self.mmwikicookie = self.config.TASK.COOKIE

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

    def document_save_file(self, parent_id, space_id, document_name):
        '''
        创建文档
        '''
        try:
            params = {
                'parent_id': f"{parent_id}",
                'space_id': f"{space_id}",
                'type': '1',
                'name': f"{document_name}",
            }
            urlpath = self.mmwiki_url + self.config.TASK.API.document_save.PATH
            req = requests.post(urlpath, params=params, headers=self.headers, verify=False)
            req_data = json.loads(req.text)
            if(req_data["code"] == 0):
                logger.info(f"文档名称: {document_name}, 创建失败: {req_data['message']}")
                return False
            else:
                document_url = req_data["redirect"]["url"]
                document_id = document_url.split('=')[1]
                logger.info(f"文档ID: {document_id}, 文档名称: {document_name}, 创建成功: {req_data['message']}")
                return document_id
        except Exception as e:
            logger.error(f"创建文档时发生错误: {str(e)}")
            return False

    def page_modify(self, document_id, document_name, document_datas):
        '''
        写入文件内容
        '''
        try:
            params = {
                'document_id': document_id,
                'name': document_name,
                'document_page_editor-markdown-doc': document_datas,
                'comment': '',
                'is_notice_user': '0',
                'is_follow_doc': '1',
            }
            logger.info(f"写入内容: {document_id} -> {document_name}")
            urlpath = self.mmwiki_url + self.config.TASK.API.page_modify.PATH
            req = requests.post(urlpath, params=params, headers=self.headers, verify=False)
            # 检查是不是json
            if not req.text.startswith('{'):
                logger.error("服务器返回非JSON响应")
                # logger.error(f"服务器返回: {req.text}")
                return
            try:
                req_data = json.loads(req.text)
                if(req_data["code"] == 1):
                    logger.info(f"文档ID: {document_id}, 文档名称: {document_name}, 写入成功: {req_data['message']}")
                else:
                    logger.error(f"文档ID: {document_id}, 文档名称: {document_name}, 写入失败: {req_data['message']}")
            except json.JSONDecodeError:
                logger.error(f"无法解析服务器响应: {req.text}")
        except Exception as e:
            logger.error(f"写入内容时发生错误: {str(e)}")

    def modify_image_path(self, space_id, document_id, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as files:
                document_datas = files.readlines()
                for i, datas in enumerate(document_datas):
                    if '![' in datas and '](' in datas and ')' in datas:
                        # 使用更精确的分割方法提取图片URL
                        start_index = datas.find('](') + 2
                        # 查找最后一个右括号
                        end_index = datas.rfind(')')
                        if start_index > 1 and end_index > start_index:
                            image_url = datas[start_index:end_index]
                            """
                            # 获取图片名称
                            image_name = image_url.split('image-')[-1] if 'image-' in image_url else os.path.basename(image_url)
                            # 上传图片
                            img_urlpath = upload_image(self.mmwiki_url, self.headers, self.config.TASK.API.image_upload.PATH, document_id, image_url, image_name, logger)
                            """
                            # URL解码
                            image_url = unquote(image_url)
                            # 获取md文件所在目录路径
                            base_dir = os.path.dirname(file_path)
                            # 处理相对路径
                            if not os.path.isabs(image_url):
                                image_url = os.path.join(base_dir, image_url)
                            # 规范化路径
                            image_url = os.path.normpath(image_url)
                            # 上传图片
                            img_urlpath = image_upload(self.mmwiki_url, self.headers, self.config.TASK.API.image_upload.PATH, document_id, image_url, logger)
                            if img_urlpath:
                                # 替换文档中的图片URL
                                modified_content = datas[:start_index] + img_urlpath + datas[end_index:]
                                document_datas[i] = modified_content
            document_datas = ''.join(document_datas)
            return document_datas
        except Exception as e:
            logger.error(f"修改图片路径时发生错误: {str(e)}")
            return False
        
    def traversal_files(self, path):
        '''
        遍历文件目录
        '''
        dirs = []
        file_path = []
        
        for item in os.scandir(path):
            if item.is_dir():
                dirs.append(item.path)
            elif item.is_file():
                file_path.append(item.path)
        
        return dirs,file_path
   
    def login(self):
        logger.info('开始登录...')
        data = {
            'arr': '',
        }
        login_url = self.mmwiki_url + self.config.TASK.API.serverStatus.PATH
        logger.info(f"登录URL: {login_url}")
        logger.info(f"使用Cookie: {self.mmwikicookie}")
        
        try:
            response = requests.post(login_url, headers=self.headers, data=data, verify=False)
            response.encoding = response.apparent_encoding
            json_data = json.loads(response.text)
            if json_data['code'] == 0:
                logger.info(f"登录失败: {json_data['message']}")
                return False
            else:
                logger.info(f"登录成功: {json_data['message']}")
                return True
        except Exception as e:
            logger.error(f"登录请求异常: {str(e)}")
            return False

    def run(self, path_name, parent_id, space_id):
        if self.login():
             # 遍历目录及读取文件内容
            dirs, file_path = self.traversal_files(path_name)
            for i in range(len(file_path)):
                # 获取文件名和扩展名
                file_name = os.path.basename(file_path[i])
                file_ext = os.path.splitext(file_name)[1].lower()
                
                if file_ext == '.md':
                    # 获取不带扩展名的文件名
                    document_name = os.path.splitext(file_name)[0]
                    # 创建文档
                    document_id = self.document_save_file(parent_id, space_id, document_name)
                    if document_id:
                        # 将文件中的本地图片修改wiki图片路径
                        file_content = self.modify_image_path(space_id, document_id, file_path[i])
                        if file_content:
                            # 写入内容
                            self.page_modify(document_id, document_name, file_content)
                  
            dirs.clear()
            file_path.clear()


if __name__ == "__main__":
    
    parser = ArgumentParser(description='MM-Wiki文档自动上传工具')
    parser.add_argument("-path", dest="path_name", required=True, help="请输入文档根目录路径（支持包含空格的路径）")
    parser.add_argument("-pid", dest="parent_id", required=True, type=int, help="请输入目录ID")
    parser.add_argument("-sid", dest="space_id", type=int, default=1, help="请输入空间ID，默认为1")
    
    try:
        args = parser.parse_args()
        # 规范化路径
        path_name = os.path.normpath(args.path_name)
        if not os.path.exists(path_name):
            logger.error(f"指定的路径不存在: {path_name}")
            sys.exit(1)
            
        auto = ThreatbookAuto()
        auto.run(path_name, args.parent_id, args.space_id)
    except SystemExit:
        parser.print_help()
    except Exception as e:
        logger.error(f"执行过程中发生错误: {str(e)}")
        parser.print_help()
        sys.exit(1)