'''
删除文章所有附件
'''

import requests
import re
import delete_img

def delete_attachment_img(url, cookies, documentid):
    
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
    'document_id': documentid,
}
    # 获取文章或有附件
    
    response = requests.get(url + '/attachment/image', params=params, cookies=cookies, headers=headers, verify=False)
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
            attachment_id_list = len(attachment_id_tr)
            for delete_url_path in attachment_id_tr:
                print("attachment_id: ", delete_url_path)
                delete_img.delete_img(url, cookies, documentid, delete_url_path)
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


    document_id = '2821'
    url =  'http://192.168.232.154:8080/'
    cookies = {
        "mmwikissid": "ec4e222bbeae62cd4e373f1c0e69c8ff",
        "mmwikipassport": "n8sckEYYgdC1id0Wi4sxh4QSy7rAhdgXuwrCiF6EgAiXhw6Egwmziz1="
    }
    urlpath = delete_attachment_img(url, cookies, document_id)
    # print(urlpath)