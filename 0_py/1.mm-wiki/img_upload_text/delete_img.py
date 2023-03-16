'''
删除文章单个附件
'''

import requests
import json

def delete_img(url, cookies, documentid, attachmentid):

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-TW,zh-CN;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Origin': url,
        'Pragma': 'no-cache',
        'Referer': url + '/page/edit?document_id=' + str(documentid),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'x-forwarded-for': '202.95.13.51',
        'x-originating-ip': '202.95.13.51',
        'x-remote-addr': '202.95.13.51',
        'x-remote-ip': '202.95.13.51',
    }

    params = {
        'attachment_id': attachmentid,
    }
    # 获取文章或有附件
    response = requests.post(url + '/attachment/delete', params=params, cookies=cookies, headers=headers, verify=False)
    response.encoding = "utf-8"
    res_text_json = json.loads(response.text)

    if res_text_json['code'] == 0:
        print(res_text_json['message'])
    else:
        print(res_text_json['message'])

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


    document_id = '2821'
    attachment_id = '7169'

    url = 'http://192.168.232.154:8080'
    cookies = {
        "mmwikissid": "ec4e222bbeae62cd4e373f1c0e69c8ff",
        "mmwikipassport": "n8sckEYYgdC1id0Wi4sxh4QSy7rAhdgXuwrCiF6EgAiXhw6Egwmziz1="
    }
    
    
    urlpath = delete_img(url, cookies, document_id, attachment_id)
    # print(urlpath)