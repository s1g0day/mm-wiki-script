# -*- coding: UTF-8 -*-
# 获取文章所有附件图片ID

import requests
import json
import re

from lib.config_loader import Config
from lib.logger_init import logger_init
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logger_init()

config = Config.from_json('config/config.json')
mmwiki_url = config.TASK.TARGET_BASE_URL
mmwikicookie = config.TASK.COOKIE
headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': mmwikicookie,
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Pragma': 'no-cache',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

# 获取文章所有附件ID
def get_attachment_page_id(documentid):

    params = {
    'document_id': documentid,
    }
    # 获取文章所有附件
    response = requests.get(mmwiki_url + '/attachment/page', params=params, headers=headers, verify=False)
    response.encoding = "utf-8"
    response_text = response.text
    if "很抱歉，文档不存在！" in response.text:
        logger.error("很抱歉，文档不存在！")
    else:
        tbody_tr =  re.findall(r'<tbody>(.*?)</tbody>', response_text, re.S|re.M)[0]
        attachment_id_tr =  re.findall(r'/attachment/delete\?attachment_id=(.*?)\'\);"><i', tbody_tr, re.S|re.M)
        if attachment_id_tr:
            logger.info(attachment_id_tr)
        else:
            logger.error("没有找到附件ID")

# 获取文章所有附件图片ID
def get_attachment_img_id(documentid):

    params = {
    'document_id': documentid,
    }
    # 获取文章所有附件
    response = requests.get(mmwiki_url + '/attachment/image', params=params, headers=headers, verify=False)
    response.encoding = "utf-8"
    response_text = response.text
    if "很抱歉，文档不存在！" in response.text:
        logger.error("很抱歉，文档不存在！")
    else:
        tbody_tr =  re.findall(r'<tbody>(.*?)</tbody>', response_text, re.S|re.M)[0]
        attachment_id_tr =  re.findall(r'/attachment/delete\?attachment_id=(.*?)\'\);"><i', tbody_tr, re.S|re.M)
        if attachment_id_tr:
            logger.info(attachment_id_tr)
        else:
            logger.error("没有找到附件ID")


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

    document_id = '3730'
    img_id = get_attachment_img_id(document_id)
    page_id = get_attachment_page_id(documentid)
    print(f"img_id: {img_id}")
    print(f"page_id: {page_id}")