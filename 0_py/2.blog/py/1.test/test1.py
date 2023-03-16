'''
selenium版本
    pip show selenium
        Name: selenium
        Version: 4.5.0

脚本作用: 
    python 先使用 selenium、html2text 模块将单篇文章保存到本地，然后使用外部文件自动下载图片并更新md文档
    eg: python3 get_page_cnblogs_md.py -u https://www.cnblogs.com/backlion/p/10537813.html
    eg: python3 get_page_cnblogs_md.py -u https://www.cnblogs.com/backlion/p/10537813.html -t 1

问题:
    受博客园主题影响可能会使用不同的html标签, 目前仅识别两种(默认主题和某个主题),未验证通用,可根据实际情况补充pattern_list值
'''


import re
import os
import sys
import json
import time
import random
import urllib3
import requests
import threadpool
from argparse import ArgumentParser
from selenium import webdriver
from selenium.webdriver import Chrome
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 点击下载
# def click_download(browser):

#     download_xpath_wait = ui.WebDriverWait(browser,5)
#     download_xpath = '//*[@id="app"]/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/span'
#     download_xpath_wait.until(lambda driver: browser.find_element(By.XPATH, download_xpath))
#     browser.find_element(By.XPATH, download_xpath).click()
#     time.sleep(random.random()*2)

# 获取下载地址
def click_download(browser, source):
    get_password_xpath_cookie = browser.get_cookies()[0]
    print(get_password_xpath_cookie)
    source_list = source.split('\n')
    for sourc in source_list:
        if "window.syncData" in sourc:
            syncData = sourc.replace(";", "").split("    window.syncData = ")[1]
            syncData_json = json.loads(syncData)
            syncData_file_list = syncData_json['shareInfo']['file_list']
            print(syncData_file_list)
            if len(syncData_file_list) != 0:
                syncData_file_id = syncData_file_list[0]['file_id']
                syncData_file_name = syncData_file_list[0]['file_name']
                syncData_file_size = syncData_file_list[0]['file_size']
                syncData_pdir_key = syncData_file_list[0]['pdir_key']
                share_key = syncData_json['shareInfo']['share_key']
                WeiyunShareBatchDownload_post = {
                        "req_header": "{\"seq\":16754204984581680,\"type\":1,\"cmd\":12024,\"appid\":30113,\"version\":3,\"major_version\":3,\"minor_version\":3,\"fix_version\":3,\"wx_openid\":\"\",\"user_flag\":0,\"device_info\":\"{\\\"browser\\\":\\\"chrome\\\"}\"}",
                        "req_body": "{\"ReqMsg_body\":{\"ext_req_head\":{\"token_info\":{\"token_type\":0,\"login_key_type\":1,\"login_key_value\":\"@pzoxTX8Yw\"},\"language_info\":{\"language_type\":2052}},\".weiyun.WeiyunShareBatchDownloadMsgReq_body\":{\"share_key\":\"6daXHRGN\",\"pwd\":\"\",\"file_owner\":null,\"download_type\":0,\"file_list\":[{\"pdir_key\":\"022ca306036332249d3a53e09c90a90f\",\"file_id\":\"21078640-c337-4dec-85a4-2fe366a2ce86\",\"filename\":\"ID276独家首发很多人都在找的恒达源码恒达全新IU天恒二开带两个后台模板.zip\",\"file_size\":251401776}]}}}"
                    }
            else:
                print("文件不存在")

    # pattern_list = ["(?s)<div id=\"topic_content\" class=\"topic-content markdown-body\">(.*)<div class=\"post-user-action\" style=\"margin-top: 34px;\">"]
    # pattern_list = ["(?s)<script>\n\twindow.syncData = (.*)}};\n</script>"]
    # for pattern in pattern_list:
    #     pattern = re.compile(pattern)
    #     match = pattern.findall(source)
    #     if match:
    #         content = match[0]
    #         content = re.findall(r'(?s)(.*)</div>', content)[0]
    #         if isinstance(content, str):
    #             content = content.strip()
    #         file_name = config["output"] + "\\" + title + ".md"
    #         md = html2text.html2text(content)
    #         md = front_template + md
    #         f = open(file_name, "w", encoding="utf-8")
    #         f.write(md)
    #         f.close()
    #         return file_name
    # print(browser.find_element(By.CLASS_NAME,'act-txt'))

def nalyze_data(url, browser, source):
    if 'form-input' in source:
        print('请输入分享密码')

        password_xpath_wait = ui.WebDriverWait(browser,5)
        password_xpath = '//*[@id="app"]/div/div[2]/div/div/div[1]/div/div[1]/div/div/div/div/div/div/div/div[2]/div/div/div[1]/div[2]/div/input'
        password_xpath_wait.until(lambda driver: browser.find_element(By.XPATH, password_xpath))
        browser.find_element(By.XPATH, password_xpath).send_keys('srsx6h')
        time.sleep(random.random()*2)
        queren_xpath_wait = ui.WebDriverWait(browser,5)
        queren_xpath = '//*[@id="app"]/div/div[2]/div/div/div[1]/div/div[1]/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/button'
        queren_xpath_wait.until(lambda driver: browser.find_element(By.XPATH, queren_xpath))
        browser.find_element(By.XPATH, queren_xpath).click()
        time.sleep(random.random()*2)
        
        
        # 下载文件
        # click_download(browser)
        click_download(browser, source)

    elif 'act-txt' in source:
        print('开始下载')
        
        # 下载文件
        # click_download(browser)
        click_download(browser, source)


def main(config, url):
    
    time.sleep(random.random()*2)
    options = webdriver.ChromeOptions()
    options.use_chromium = True
    
    options.add_argument("–incognito") # 隐身模式（无痕模式）
    # options.add_argument('--headless') # 无头模式
    options.add_argument('--ignore-certificate-errors') # 设置Chrome忽略网站证书错误
    # options.add_argument("blink-settings=imagesEnabled=false") # 不加载图片
    options.add_experimental_option("excludeSwitches",["enable-logging"])
    options.add_experimental_option("detach", True) #不自动关闭浏览器
    options.binary_location = config["CHROMEPATH"]
    
    s = Service(config["DRIVERPATH"])
    browser = Chrome(options=options, service=s)
    browser.get(url)
    browser.implicitly_wait(10)
    
    getcookie = browser.get_cookies()[0]
    # time.sleep(random.random()*6)
    browser.delete_all_cookies() # 先清除原有的cookie

    cookies = {
        'ptcz': '10d2c5310f5a62f7b14adc1ad4a16ca1b1fd95a2a8dd66afe8dc2cf62c5abd8c',
        'web_wx_rc': 'QWKCZ',
        'uin': 'o1249727084',
        'skey': '@HK81sWvtk',
        'p_uin': 'o1249727084',
        'pt4_token': 'cKIOM1z6IhPaubR2Cf1MGCPuxUbxFFbMVNxUumbIX98_',
        'p_skey': 'j1Xj0RqpdiT6Bz8ZB6sh7li5fRejCAeTbuHdERJs26M_',
        'wyctoken': '1998239996',
    }
    for k in cookies:
        if k == "wyctoken":
            cookie_dict = {
                'domain': getcookie.get('domain'),#//这里是固定的每个网站都不同
                'name': getcookie.get('name'),
                'value': getcookie.get('value'),
                "expires": getcookie.get('value'),
                'path': '/',
                'httpOnly': False,
                'HostOnly': False,
                'Secure': False
                }
        else:
            cookie_dict = {
                'domain': getcookie.get('domain'),#//这里是固定的每个网站都不同
                'name': str(k),
                'value': str(cookies[k]),
                "expires": str(cookies[k]),
                'path': '/',
                'httpOnly': False,
                'HostOnly': False,
                'Secure': False
                }
        browser.add_cookie(cookie_dict)
    browser.refresh() # 带着cookie 重新加载
    # print(browser.get_cookies())
    time.sleep(random.random()*6)
    
    source = browser.page_source
    
    if "链接已删除，请联系分享者重新分享" in source:
        print("链接已删除", url)
    else:
        print("开始下载文章")
        file_name = nalyze_data(url, browser, source)

    time.sleep(3)
    # browser.quit()
    
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
    print(int(time.time()))
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
