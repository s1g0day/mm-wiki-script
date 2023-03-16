'''
selenium版本
    pip show selenium
        Name: selenium
        Version: 4.5.0
脚本作用: 
    python 使用 selenium 模块将先知单篇文章保存到本地并下载图片
    eg: python3 get_page_xianzhi_md.py -p 4441
    eg: python3 get_page_xianzhi_md.py -p 4441 -t 1

问题:
    本脚本存在内容缺失的问题, 尝试使用html2text模块发现部分格式无法完全转换, eg https://xz.aliyun.com/t/8066
'''

import re
import os
import sys
import json
import time
import tomd
import uuid
import random
import urllib3
import requests
import threadpool
from argparse import ArgumentParser
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def convert(regex: str, new: str, src: str):
    return re.sub(regex, new, src, 0, re.MULTILINE)

def format_md(s: str):
    regex = r"\[<"
    t = convert(regex, r"![<", s)
    regex = r"(<pre>)|(</pre>)"
    t = convert(regex, "\n```\n", t)
    regex = r"<li>"
    t = convert(regex, "1. ", t)
    regex = r"</li>"
    t = convert(regex, "", t)
    return t

def download_img(config, src: str, title: str):
    regex = r"<img src=\"(.*)\">"
    img_links = re.findall(regex, src, re.MULTILINE)
    base_dir = title + ".assets"
    dir_name = config["output"] + "\\image\\" +  base_dir
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    count = 0
    total = len(img_links)
    headers = {
        "User-Agent": r'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36''',
        "Referer": "https://xz.aliyun.com/"
    }
    for link in img_links:
        print(f"\r\t\033[33m[+] Downloading images ...{count + 1}/{total}\033[0m", end="")
        try:
            r = requests.get(url=link, headers=headers, timeout=8, verify=False)
            time.sleep(0.5)
            image_uuid = uuid.uuid4()
            basename = f"image-{image_uuid}.png"
            f = open(f"{dir_name}/{basename}", "wb")
            f.write(r.content)
            f.close()
            re_link = convert(r"\.", "\\.", link)
            ref = r'<img src=\"' + re_link + r'\">'
            src = convert(ref, f"image-{image_uuid}", src)
            src = convert(re_link, f"{base_dir}/{basename}", src)
            count += 1
        except:
            print(link + ": 连接错误")
            exit()
    return src

# def nalyze_data1(files_name):
#     with open(files_name, 'r', encoding='utf-8') as file_md_path:
#         file_md_data = file_md_path.readlines()
#         md = front_template + md
#         md = download_img(config, md, title)
#         md = md.replace("<br>","\n")
#         f = open(file_name, "w", encoding="utf-8")
#         f.write(md)
#         print("\n\033[32m[*] Done\033[0m")
#         f.close()
#     return file_name  
def nalyze_data(url, config, source, title):
    # 处理title特殊符号
    title = title[:title.rfind("-")]
    front_template = f'---\ntitle: {title}\n转自: {url}\n\n---\n'
    title = title.replace('"', "'").replace("?", "-").replace("<", "-").replace(">", "-").replace("/", "-").replace("\\", "-").replace(":", "-").replace("*", "-").replace("|", "-")
    title = title.strip()
    
    # print(title)
    pattern = "(?s)<div id=\"topic_content\" class=\"topic-content markdown-body\">(.*)<div class=\"post-user-action\" style=\"margin-top: 34px;\">"
    pattern = re.compile(pattern)
    match = pattern.findall(source)
    content = match[0]
    content = re.findall(r'(?s)(.*)</div>', content)[0]
    if isinstance(content, str):
        content = content.strip()
    file_name = config["output"] + "\\" + title + ".md"
    md = tomd.convert(content)
    md = format_md(md)
    md = front_template + md
    md = download_img(config, md, title)
    md = md.replace("<br>","\n")
    f = open(file_name, "w", encoding="utf-8")
    f.write(md)
    print("\n\033[32m[*] Done\033[0m")
    f.close()
    return file_name
def main(config, url):

    time.sleep(random.random()*2)
   
    # r = requests.get(url)
    # print(r.status_code)
    options = webdriver.ChromeOptions()
    options.use_chromium = True
    options.add_argument("–incognito") # 隐身模式（无痕模式）
    options.add_argument('--headless') # 无头模式
    options.add_argument('--ignore-certificate-errors') # 设置Chrome忽略网站证书错误
    options.add_argument("blink-settings=imagesEnabled=false") # 不加载图片
    options.add_experimental_option("excludeSwitches",["enable-logging"])
    options.binary_location = config["CHROMEPATH"]
    s = Service(config["DRIVERPATH"])
    browser = Chrome(options=options, service=s)
    browser.get(url)
    
    time.sleep(random.random()*4)
    source = browser.page_source
    title = browser.title
    browser.quit()
    if "400 - 先知社区" in title:
        print("文章不存在: ", url)
    else:
        file_name = nalyze_data(url, config, source, title)
        # 打印md文件绝对路径
        print(os.path.abspath(file_name))

    
# 主函数
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
    
    parser = ArgumentParser()
    parser.add_argument("-u", dest="url", required=True, help="请输入文章编号")
    parser.add_argument("-t", dest="thread", type=int, default="1", help="请输入线程")
    args = parser.parse_args()

    if len(sys.argv) <= 1:
        parser.print_help()
    else:
        config = json.loads(open("..\quote\config.json", "r").read())
        output_dir = "output" if config['output'] == "" else config['output']
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        lst_vars_1 = [config, args.url]
        func_var = [(lst_vars_1, None)]
        
        pool = threadpool.ThreadPool(args.thread)
        req = threadpool.makeRequests(main, func_var)
        for r in req:
            pool.putRequest(r)
        pool.wait()

