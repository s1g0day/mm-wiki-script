# -*- coding: utf-8 -*-
"""
@Createtime: 2025-04-27 9:35:00
@Updatetime: 2025-04-27 9:35:00
@description: 获取文档ID及文档数量
"""

import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def Get_document_id(mmwiki_url, headers, path, parent_id, space_id, logger):
    """
    获取指定父目录下的文档ID及文档数量
    """
    try:
        params = {
            'parent_id': f"{parent_id}",
            'space_id': f"{space_id}",
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
                logger.info(f"目录ID: {parent_id} {req_data['message']}, 含父目录共{req_data['data']['total']}个文档")
                if req_data['data']['total'] > 100:
                    logger.info(f"目录ID: {parent_id} 文档数量超过100个, 速度会变慢，请稍等")
                return True
            else:
                logger.error(f"目录ID: {parent_id} {req_data['message']}")
                return False
        except json.JSONDecodeError:
            logger.error(f"无法解析服务器响应: {req.text}")
            return False
    except Exception as e:
        logger.error(f"获取文档时发生错误: {str(e)}")
        return False