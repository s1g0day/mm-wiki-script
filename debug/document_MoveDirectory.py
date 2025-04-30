# -*- coding: utf-8 -*-
"""
@Createtime: 2025-04-08 10:15:58
@Updatetime: 2025-04-08 16:15:58
@description: 获取空间下所有文档ID及数量（可指定父目录）
"""

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

cookies = {
    'mmwikissid': '1f87b2e619d5991769110409ff0a2491',
    'mmwikipassport': 'n8sckEYYgdC1h4iJgdgGgEgXhwrShzech7iGiFlHy41Di45JiAuxyda=',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    # 'Cookie': 'mmwikissid=1f87b2e619d5991769110409ff0a2491; mmwikipassport=n8sckEYYgdC1h4iJgdgGgEgXhwrShzech7iGiFlHy41Di45JiAuxyda=',
}

params = {
    'source_id': '123',
    'target_id': '456',
}

response = requests.post(
    'http://192.168.1.1:8080/document/MoveDirectory',
    params=params,
    cookies=cookies,
    headers=headers,
    verify=False,
)
json_data = response.json()
print(json_data['code'])