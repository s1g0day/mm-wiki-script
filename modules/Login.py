# -*- coding: utf-8 -*-
"""
@Createtime: 2025-04-14 17:15:58
@Updatetime: 2025-04-24 13:32:11
@description: MM-Wiki登录
@note:
    作用: 登录MM-Wiki
"""
import requests
import json

def serverStatus(mmwiki_url, mmwikicookie, headers, path, logger):
    logger.info('检测cookie状态...')
    data = {
        'arr': '',
    }
    server_url = mmwiki_url + path
    logger.info(f"登录URL: {server_url}")
    logger.info(f"使用Cookie: {mmwikicookie}")
    
    try:
        req = requests.post(server_url, headers=headers, data=data, verify=False)
        req.encoding = req.apparent_encoding
        # 检查是不是json
        if not req.text.startswith('{'):
            logger.error("服务器返回非JSON响应")
            # logger.error(f"服务器返回: {req.text}")
            return False
        try:
            req_data = json.loads(req.text)
            if(req_data["code"] == 1):
                return True
            else:
                return False
        except json.JSONDecodeError:
            logger.error(f"无法解析服务器响应: {req.text}")
            return False
    except Exception as e:
        logger.error(f"登录请求异常: {str(e)}")
        return False

def login(mmwiki_url, headers, path, username, password, logger):
    """
    登录MM-Wiki
    Args:
        mmwiki_url: Wiki基础URL
        headers: 请求头
        path: 登录接口路径
        username: 用户名
        password: 密码
        logger: 日志对象
    Returns:
        dict/None: 成功返回包含Cookie的headers，失败返回None
    """
    logger.info('开始登录...')
    
    
    # 先获取初始cookie
    try:
        session = requests.Session()
        init_req = session.get(f'{mmwiki_url}', verify=False)
        request_cookie = init_req.request.headers.get('Cookie')
        
        if not request_cookie:
            logger.error("未获取到初始Cookie")
            return None
            
        logger.info(f"获取到初始Cookie: {request_cookie}")
        headers['Cookie'] = request_cookie
        
    except requests.exceptions.RequestException as e:
        logger.error(f"获取初始Cookie时网络错误: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"获取初始Cookie时发生未知错误: {str(e)}")
        return None

    data = {
        'username': username,
        'password': password
    }
    
    login_url = f'{mmwiki_url}{path}'
    logger.info(f"登录URL: {login_url}")
    
    try:
        req = session.post(login_url, headers=headers, data=data, verify=False)
        req.encoding = req.apparent_encoding
        
        if not req.text.startswith('{'):
            logger.error(f"服务器返回非JSON响应: {req.text[:100]}")
            return None
            
        req_data = json.loads(req.text)
        
        if req_data["code"] != 1:
            logger.error(f"登录失败: {req_data.get('message', '未知错误')}")
            return None
            
        # 获取登录后的cookie
        cookies = req.cookies.get_dict()
        mmwikipassport = cookies.get('mmwikipassport')
        
        if not mmwikipassport:
            logger.error("未获取到登录Cookie(mmwikipassport)")
            return None
            
        # 更新headers中的Cookie
        headers['Cookie'] = f"{request_cookie}; mmwikipassport={mmwikipassport}"
        logger.info(f"最终Cookie: {headers['Cookie']}")
        
        return headers
        
    except json.JSONDecodeError as e:
        logger.error(f"解析响应JSON失败: {str(e)}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"登录请求网络错误: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"登录过程发生未知错误: {str(e)}")
        return None

    