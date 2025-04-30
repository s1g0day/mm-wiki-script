# -*- coding: utf-8 -*-
"""
@Createtime: 2025-04-26 22:14:00
@Updatetime: 2025-04-26 22:14:00
@description: 文档排序
"""

import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def Sort_Documents(mmwiki_url, headers, path, parent_id, space_id, recursive, logger):
    """
    对指定父目录下的文档和目录进行排序
    """
    try:
        params = {
            'parent_id': f"{parent_id}",
            'space_id': f"{space_id}",
            'recursive': recursive,
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
                logger.info(f"目录ID: {parent_id} {req_data['message']}, {req_data['data']['count']}个文档")
                return True
            else:
                logger.error(f"目录ID: {parent_id} {req_data['message']}")
                return False
        except json.JSONDecodeError:
            logger.error(f"无法解析服务器响应: {req.text}")
            return False
    except Exception as e:
        logger.error(f"删除文档时发生错误: {str(e)}")
        return False