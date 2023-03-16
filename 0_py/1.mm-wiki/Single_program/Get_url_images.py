import requests
from lxml import etree
import time
import os
import re

requests = requests.session()

website_url = ''
website_name = ''

'''
爬取的页面
'''
def html_url(url):
    try:
        head = set_headers()
        text = requests.get(url,headers=head)
        # print(text)
        html = etree.HTML(text.text)
        img = html.xpath('//img/@src')
        # 保存图片
        for src in img:
            src = auto_completion(src)
            file_path = save_image(src)
            if file_path == False:
                print('请求的图片路径出错，url地址为：%s'%src)
            else :
                print('保存图片的地址为：%s'%file_path)
    except requests.exceptions.ConnectionError as e:
        print('网络地址无法访问，请检查')
        print(e)
    except requests.exceptions.RequestException as e:
        print('访问异常：')
        print(e)


'''
保存图片
'''
def save_image(image_url):
    if not image_url:
        return False
    size = 0
    number = 0
    while size == 0:
        try:
            img_file = requests.get(image_url)
        except requests.exceptions.RequestException as e:
            raise e

        # 不是图片跳过
        if check_image(img_file.headers['Content-Type']):
            return False
        file_path = image_path(img_file.headers)
        # 保存
        with open(file_path, 'wb') as f:
            f.write(img_file.content)
        # 判断是否正确保存图片
        size = os.path.getsize(file_path)
        if size == 0:
            os.remove(file_path)
        # 如果该图片获取超过十次则跳过
        number += 1
        if number >= 10:
            break
    return (file_path if (size > 0) else False)

'''
自动完成url的补充
'''
def auto_completion(url):
    global website_name,website_url
    #如果是http://或者https://开头直接返回
    if re.match('http://|https://',url):
        return url
    elif re.match('//',url):
        if 'https://' in website_name:
            return 'https:'+url
        elif 'http://' in website_name:
            return 'http:' + url
    elif re.match('/',url):
        return website_name+url
    elif re.match('./',url):
        return website_url+url[1::]

'''
图片保存的路径
'''
def image_path(header):
    # 文件夹
    file_dir = './save_image/'
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    # 文件名
    file_name = str(time.time())
    # 文件后缀
    suffix = img_type(header)

    return file_dir + file_name + suffix


'''
获取图片后缀名
'''
def img_type(header):
    # 获取文件属性
    image_attr = header['Content-Type']
    pattern = 'image/([a-zA-Z]+)'
    suffix = re.findall(pattern,image_attr,re.IGNORECASE)
    if not suffix:
        suffix = 'png'
    else :
        suffix = suffix[0]
    # 获取后缀
    if re.search('jpeg',suffix,re.IGNORECASE):
        suffix = 'jpg'
    return '.' + suffix


# 检查是否为图片类型
def check_image(content_type):
    if 'image' in content_type:
        return False
    else:
        return True
#设置头部
def set_headers():
    global website_name, website_url
    head = {
        'Host':website_name.split('//')[1],
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
    }
    return head



if __name__ == '__main__':

    #当前的url，不包含文件名的比如index.html，用来下载当前页的页面图片(./)
    website_url = 'http://192.168.232.154:8080/'
    #域名，用来下载"/"开头的图片地址
    #感兴趣的朋友请帮我完善一下这个自动完成图片url的补充
    website_name = 'http://192.168.232.154:8080/'
    url = 'http://192.168.232.154:8080/page/display?document_id=279'
    html_url(url)