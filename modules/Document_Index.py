# -*- coding: utf-8 -*-
"""
@Createtime: 2025-04-15 10:15:58
@Updatetime: 2025-04-15 10:15:58
@description: 获取文档状态
"""

import requests
import json
import urllib3
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check_document_content(document_content, document_id, logger):
    '''
    检测文档是否有内容
    '''
    try:
        
        soup = BeautifulSoup(document_content, 'html.parser')
        # 标题
        title_element = soup.find('h3', class_='view-page-title')
        document_name = title_element.text.strip() if title_element else None
        if not document_name:
            logger.info(f"文档ID: {document_id}, 文档状态: 标题为空")
            return False
        # 内容
        content_div = soup.find('div', id='document_page_view')
        if content_div is None or content_div.text.strip() == "":
            logger.info(f"文档ID: {document_id}, 文档名称: {document_name}, 文档状态: 内容为空")
            return False
        return True
    except Exception:
        return False

def get_document_status(mmwiki_url, headers, document_id, logger):
    '''
    获取文档状态
    '''

    try:
        urlpath = mmwiki_url + path
        req = requests.get(urlpath, params=params, headers=headers, verify=False)
        req.encoding = req.apparent_encoding
        req_status = req.status_code
        if "很抱歉，文档不存在！" in response.text:
            logger.error("很抱歉，文档不存在！")
            return False
        else:
            logger.info(f"文档ID: {document_id}, 文档名称: {document_name}, 文档状态: 正常, 状态码: {req_status}")
            check_document_content(req.text)
            return True
    except Exception as e:
        logger.error(f"创建文档时发生错误: {str(e)}")
        return False
