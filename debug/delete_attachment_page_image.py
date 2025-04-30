# -*- coding: utf-8 -*-
# 删除文章所有附件

import requests
import re

from lib.config_loader import Config
from lib.logger_init import logger_init
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import json

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

def delete_attachment_page(documentid, attachmentid):

    params = {
        'attachment_id': attachmentid,
    }
    # 删除文章单个附件
    response = requests.post(mmwiki_url + '/attachment/delete', params=params, cookies=mmwikicookie, headers=headers, verify=False)
    response.encoding = "utf-8"
    res_text_json = json.loads(response.text)

    if res_text_json['code'] == 0:
        logger.info(res_text_json['message'])
    else:
        logger.error(res_text_json['message'])

def delete_attachment_image(documentid):

    params = {
        'document_id': documentid,
    }
    # 获取文章图片
    
    response = requests.get(mmwiki_url + '/attachment/image', params=params, headers=headers, verify=False)
    response.encoding = "utf-8"
    response_text = response.text
    if "很抱歉，文档不存在！" in response.text:
        print("很抱歉，文档不存在！")
    else:
        tbody_tr =  re.findall(r'<tbody>(.*?)</tbody>', response_text, re.S|re.M)[0]
        if "delete?attachment_id" not in tbody_tr:
            print("无附件图片")
        else:
            attachment_id_tr =  re.findall(r'/attachment/delete\?attachment_id=(.*?)\'\);"><i', tbody_tr, re.S|re.M)

def delete_attachment_main(documentid):
    attachment_id_list = len(attachment_id_tr)
    for delete_url_path in attachment_id_tr:
        print("attachment_id: ", delete_url_path)
        delete_attachment_page(documentid, delete_url_path)
    print("共删除 %d 个图片附件" % attachment_id_list)

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
    # 获取图片名文件+ 后缀


    urlpath = delete_attachment_image(document_id)
    # print(urlpath)