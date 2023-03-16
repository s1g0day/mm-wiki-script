'''
selenium版本
    pip show selenium
        Name: selenium
        Version: 4.5.0

脚本作用: 
    python 先使用 selenium、html2text 模块将单篇文章保存到本地，然后使用外部文件自动下载图片并更新md文档
    eg: python3 get_page_seebug_md.py -u https://paper.seebug.org/1339/
    eg: python3 get_page_seebug_md.py -u https://paper.seebug.org/1339/ -t 1

问题:
    受博客园主题影响可能会使用不同的html标签, 目前仅识别两种(默认主题和某个主题),未验证通用,可根据实际情况补充pattern_list值
'''


import re
import os
import json
import time
import random
import urllib3
import html2text
import threadpool
from argparse import ArgumentParser
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import sys
sys.path.append("..")
import quote.Identify_pictures

def nalyze_data(url, config, source, title):
    # 处理title特殊符号
    # title = title[:title.rfind("-")]
    front_template = f'---\ntitle: {title}\n转自: {url}\n\n---\n'
    title = title.replace('"', "'").replace("?", "-").replace("<", "-").replace(">", "-").replace("/", "-").replace("\\", "-").replace(":", "-").replace("*", "-").replace("|", "-")
    title = title.strip()

    pattern_list = ["(?s)<section class=\"post-content\">(.*)<nav class=\"pagination\" role=\"navigation\" style=\"padding: 3rem;\">"]
    for pattern in pattern_list:
        pattern = re.compile(pattern)
        match = pattern.findall(source)
        if match:
            content = match[0]
            # print(match)
            content = re.findall(r'(?s)(.*)\n<hr>\n<p><img src="', content)[0]
            if isinstance(content, str):
                content = content.strip()
            file_name = config["output"] + "\\" + title + ".md"
            # print(content)
            md = html2text.html2text(content)
            md = front_template + md
            f = open(file_name, "w", encoding="utf-8")
            f.write(md)
            f.close()
            return file_name

def main(config, url):
    
    time.sleep(random.random()*2)
    # url = 'https://www.cnblogs.com/backlion/p/' + str(page_id) + '.html'

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
    
    if "404 页面不存在" in title:
        print("页面不存在", url)
    else:
        print("开始下载文章")
        file_name = nalyze_data(url, config, source, title)

        # 打印md文件绝对路径
        file_path = os.path.abspath(file_name)
        md_path_name = file_path.rsplit("\\",1)[0]

        print("文章下载完成，开始下载图片")
        quote.Identify_pictures.images_save(md_path_name, file_name)
        print("\n图片下载完成, 该文章存储到: ",file_path)

    
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
    parser.add_argument("-u", dest="url", type=str, help="请输入文章URL")
    parser.add_argument("-t", dest="thread", type=int, default="1", help="请输入线程, 默认1个线程")
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

