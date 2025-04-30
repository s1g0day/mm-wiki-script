# -*- coding: utf-8 -*-
"""
@Createtime: 2025-04-08 10:15:58
@Updatetime: 2025-04-24 23:45:13
@description: 递归删除目录下的所有目录和文件
"""

import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def Move_Directory_All(mmwiki_url, headers, path, source_id, target_id, logger):
    """
    递归移动目录下的所有目录和文件
    """
    try:
        params = {
            'source_id': f"{source_id}",
            'target_id': f"{target_id}",
            'move_mode': 'content'
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
            if req_data["code"] == 1:
                moved_count = req_data.get('data', {}).get('moved_documents', 0)
                logger.info(f"[+] {req_data['message']}, 共移动 {moved_count} 个文档")
                return True
            else:
                error_msg = req_data.get('message', '未知错误')
                logger.error(f"[-] 移动失败: {error_msg}")
                return False
        except (KeyError, TypeError) as e:
            logger.error(f"[-] 解析响应数据失败: {str(e)}")
            logger.error(f"[-] 响应内容: {req.text}")
            return False
    except Exception as e:
        logger.error(f"移动文档时发生错误: {str(e)}")
        return False
        
def Move_Directory(mmwiki_url, headers, path, source_id, target_id, only_docs, logger):
    """
    递归移动目录下的所有目录和文件
    """
    try:
        params = {
            'source_id': f"{source_id}",
            'target_id': f"{target_id}",
            'only_docs': only_docs,
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
            if req_data["code"] == 1:
                moved_count = req_data.get('data', {}).get('moved_documents', 0)
                logger.info(f"[+] {req_data['message']}, 共移动 {moved_count} 个文档")
                return True
            else:
                error_msg = req_data.get('message', '未知错误')
                logger.error(f"[-] 移动失败: {error_msg}")
                return False
        except (KeyError, TypeError) as e:
            logger.error(f"[-] 解析响应数据失败: {str(e)}")
            logger.error(f"[-] 响应内容: {req.text}")
            return False
    except Exception as e:
        logger.error(f"移动文档时发生错误: {str(e)}")
        return False