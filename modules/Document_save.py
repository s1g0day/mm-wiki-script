# -*- coding: utf-8 -*-
"""
@Createtime: 2025-04-14 17:15:58
@Updatetime: 2025-04-14 17:15:58
@description: 文档创建
@note:
    作用: 创建文档
    特点: 支持多级目录
        文档上传: 上传到目标ID为 `1` 的目录下
        文档上传失败: 会跳过该文档，不影响文档上传
"""

import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_document(mmwiki_url, headers, path, parent_id, space_id, document_name, document_type, logger):
    '''
    创建文档
    type:
    1: 文档
    2: 文件夹
    '''
    try:
        params = {
            'parent_id': f"{parent_id}",
            'space_id': f"{space_id}",
            'type': f"{document_type}",
            'name': f"{document_name}",
        }
        urlpath = mmwiki_url + path
        req = requests.post(urlpath, params=params, headers=headers, verify=False)
        req.encoding = req.apparent_encoding
        # 检查是不是json
        if not req.text.startswith('{'):
            logger.error("服务器返回非JSON响应")
            # logger.error(f"服务器返回: {req.text}")
            return False
        try:
            req_data = json.loads(req.text)
            if(req_data["code"] == 1):
                document_url = req_data["redirect"]["url"]
                document_id = document_url.split('=')[1]
                logger.info(f"文档ID: {document_id}, 文档名称: {document_name}, 创建成功: {req_data['message']}")
                return document_id
            else:
                logger.info(f"文档名称: {document_name}, 创建失败: {req_data['message']}")
                return False
        except json.JSONDecodeError:
            logger.error(f"无法解析服务器响应: {req.text}")
            return False
    except Exception as e:
        logger.error(f"创建文档时发生错误: {str(e)}")
        return False
