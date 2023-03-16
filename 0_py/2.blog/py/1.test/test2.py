# -*- coding: utf-8 -*-
'''

'''
import os
import sys
import time
import json
import urllib3
import requests
import threadpool
from argparse import ArgumentParser
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def send_requests(url, *sharepwd):
    print(url) 

    proxies = {
    	# 用sock协议时只能用socks5h 不能用socks5,或者用http协议
        'http':'socks5h://127.0.0.1:7890',
        'https':'socks5h://127.0.0.1:7890'
    }

    cookies = {
        'ptcz': 'd66a89619f5fe13a4d72422b13e8171b8f74ac9a9594b5ae0a5df966e115ae35',
        'web_wx_rc': 'XAAPJUXGX',
        'uin': 'o1249727084',
        'skey': '@HK81sWvtk',
        'p_uin': 'o1249727084',
        'pt4_token': 'FXijuiypyb6t*s*fOVDa464tBVI3fpe76i65sZTxsxY_',
        'p_skey': '3lrERClOEFUaqBrOsCItzD4Wo*E1LpJZ6CUbsApuFFE_',
        'wyctoken': '1062628123',
    }
    if sharepwd != None:
        cookies.update({"sharepwd": "srsx6h"})
    
    headers = {
        'authority': 'share.weiyun.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'zh-TW,zh-CN;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
        'cache-control': 'no-cache',
        # 'cookie': 'ptcz=d66a89619f5fe13a4d72422b13e8171b8f74ac9a9594b5ae0a5df966e115ae35; sharepwd=srsx6h; web_wx_rc=XAAPJUXGX; uin=o1249727084; skey=@HK81sWvtk; p_uin=o1249727084; pt4_token=FXijuiypyb6t*s*fOVDa464tBVI3fpe76i65sZTxsxY_; p_skey=3lrERClOEFUaqBrOsCItzD4Wo*E1LpJZ6CUbsApuFFE_; wyctoken=1062628123',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'x-forwarded-for': '114.29.255.8',
        'x-originating-ip': '114.29.255.8',
        'x-remote-addr': '114.29.255.8',
        'x-remote-ip': '114.29.255.8',
    }

    try:
        req = requests.get(url=url, proxies=proxies, cookies=cookies, headers=headers, verify=False)
        req.encoding = req.apparent_encoding	# apparent_encoding比"utf-8"错误率更低
        status_code = req.status_code
        if status_code == 404:
            exit()
        else:
            print("\r\t\033[33m[+] %s \033[0m" % url)
            return req
    except:
        return
    time.sleep(2)

def get_download_url(req):
    source_list = req.text.split('\n')
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

def pass_url(url, sharepwd):
    print('2')
    req = send_requests(url, sharepwd)
    source_list = req.text.split('\n')
    for sourc in source_list:
        if "window.syncData" in sourc:
            syncData = sourc.replace(";", "").split("    window.syncData = ")[1]
            syncData_json = json.loads(syncData)
            syncData_file_list = syncData_json['shareInfo']['file_list']
            syncData_file_id = syncData_file_list[0]['file_id']
            syncData_file_name = syncData_file_list[0]['file_name']
            syncData_file_size = syncData_file_list[0]['file_size']
            syncData_pdir_key = syncData_file_list[0]['pdir_key']
            share_key = syncData_json['shareInfo']['share_key']


def main(url, *sharepwd):
    print('1')
    req = send_requests(url)
    source_list = req.text.split('\n')
    for sourc in source_list:
        if "window.syncData" in sourc:
            syncData = sourc.replace(";", "").split("    window.syncData = ")[1]
            syncData_json = json.loads(syncData)
            print(syncData_json['shareInfo'])
            if "error" in syncData_json:
                print(syncData_json['error']['msg'])
            elif syncData_json['shareInfo']['down_cnt'] == None:
                print("请输入密码")
                # sharepwd = {'sharepwd': 'srsx6h'}
                # pass_url(url, sharepwd)
            else:
                syncData_file_list = syncData_json['shareInfo']['file_list']
                print(syncData_file_list)
                if len(syncData_file_list) != 0:
                    syncData_file_id = syncData_file_list[0]['file_id']
                    syncData_file_name = syncData_file_list[0]['file_name']
                    syncData_file_size = syncData_file_list[0]['file_size']
                    syncData_pdir_key = syncData_file_list[0]['pdir_key']
                    share_key = syncData_json['shareInfo']['share_key']
                else:
                    print("请输入密码或文件不存在")

def logo():
    print('''
 ____  _        ___  ____              
/ ___|/ | __ _ / _ \|  _ \  __ _ _   _ 
\___ \| |/ _` | | | | | | |/ _` | | | |
 ___) | | (_| | |_| | |_| | (_| | |_| |
|____/|_|\__, |\___/|____/ \__,_|\__, |
         |___/                   |___/ 
                                       
Powered by S1g0Day
    ''')
    
if __name__ == '__main__':
    
    start_time = time.time()    # 程序开始时间
    logo()

    parser = ArgumentParser()
    parser.add_argument("-u", dest="url_name", help="请输入单个url")
    parser.add_argument("-path", dest="path_name", help="请输入url文件")
    parser.add_argument("-t", dest="thread", type=int, default="1", help="请输入线程")
    args = parser.parse_args()
    
    if len(sys.argv) <= 1:
        parser.print_help()
    elif args.url_name:
        main(args.url_name)
    elif args.path_name:
        name_list = []
        with open(args.path_name, 'r', encoding='utf-8') as files:
            files = files.readlines()
            for i in files:
                name_list.append(i.rstrip())
        pool = threadpool.ThreadPool(int(args.thread))
        req = threadpool.makeRequests(main, name_list)
        for r in req:
            pool.putRequest(r)
        pool.wait()
    else:
        print("未指定url参数")
    end_time = time.time()    # 程序结束时间
    run_time = end_time - start_time    # 程序的运行时间，单位为秒
    print(run_time)