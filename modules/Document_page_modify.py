# -*- coding: utf-8 -*-
"""
@Createtime: 2025-04-14 17:15:58
@Updatetime: 2025-04-14 17:15:58
@description: 文档内容写入
@note:
    作用: 写入文档内容
    特点: 支持多级目录
        文档上传: 上传到目标ID为 `1` 的目录下
"""

import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def page_modify(mmwiki_url, headers, path, document_id, document_name, document_datas, logger):
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
                    logger.info(f"文档ID: {document_id}, 文档名称: {document_name}, 写入成功: {req_data['message']}")
                    return True
                else:
                    logger.error(f"文档ID: {document_id}, 文档名称: {document_name}, 写入失败: {req_data['message']}")
                    return False
            except json.JSONDecodeError:
                logger.error(f"无法解析服务器响应: {req.text}")
                return False
        except Exception as e:
            logger.error(f"写入内容时发生错误: {str(e)}")
            return False