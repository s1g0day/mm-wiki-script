'''
作用: 上传图片
使用 multipart/form-data 发送数据
安装MultipartEncoder模块
    pip3 install requests_toolbelt

只用于上传png图片,注入gif、mp4等均不识别
使用
需拿到脚本实际测试
'''
import requests
import json
import uuid
from requests_toolbelt.multipart.encoder import MultipartEncoder


def upload_img(url, config, documentid, img_path, random_uuid):

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-TW,zh-CN;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundaryoN1ZujCelggmkbA2',
        'Origin': url,
        'Pragma': 'no-cache',
        'Referer': url + '/page/edit?document_id=' + str(documentid),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'x-forwarded-for': '202.95.13.51',
        'x-originating-ip': '202.95.13.51',
        'x-remote-addr': '202.95.13.51',
        'x-remote-ip': '202.95.13.51',
    }

    params = {
        'document_id': documentid,
        'guid': random_uuid,
    }

    multipart_encoder = MultipartEncoder(
        fields={#这里根据需要进行参数格式设置
                'editormd-image-file': (str(random_uuid) + '-image.png', open(img_path, 'rb'), 'image/png')
                })
    headers['Content-Type'] = multipart_encoder.content_type
    #请求头必须包含Content-Type: multipart/form-data; boundary=${bound}
    #这里也可以自定义boundary

    response = requests.post(url=url + '/image/upload', params=params, cookies=config, headers=headers, data=multipart_encoder, verify=False)
    response.encoding = 'utf-8'
    response_text_json = json.loads(response.text)
    if response_text_json['success'] == 1:
        img_urlpath = "![image](" + response_text_json['url'] + ")"
        return img_urlpath
    else:
        return img_path
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
    img_path = "123123.png"
    document_id = '3'
    random_uuid = uuid.uuid1()
    url = 'http://192.168.232.154:8080'
    config = json.loads(open("config.json", "r").read())
    urlpath = upload_img(url, config, document_id, img_path, random_uuid)
    print(urlpath)

    