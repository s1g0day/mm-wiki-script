# -*- coding: utf-8 -*-
"""
@Createtime: 2025-03-22 15:17:45
@Updatetime: 2025-03-24 17:17:45
@description: 图片上传
@note:
    作用: 上传图片
    特点: 支持图片上传
        图片上传: 上传到目标ID为 `1` 的目录下
        图片路径: 上传后，图片路径会自动修改为 `/image/xxx.png`
        图片上传失败: 会跳过该图片，不影响文档上传
"""
import requests
import json
import os
import time
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib.parse import unquote

def local_img_path(md_path_name, files_name, img_data, logger):
    """
    规范化本地图片路径
    
    Args:
        md_path_name: MD文件所在目录
        files_name: 当前处理的文件名
        img_data: 图片路径
        
    Returns:
        str: 规范化后的绝对路径
    """
    try:
        # 检查是否是网络路径
        if img_data.startswith(('http://', 'https://')):
            logger.info(f"跳过网络路径: {img_data}")
            return False
        # 处理特殊字符
        img_data = img_data.split('?')[0]  # 移除URL参数部分
        img_data = img_data.replace(',', '_')  # 替换逗号为下划线
        
        # 获取文件所在目录
        file_dir = os.path.dirname(files_name)
        # 尝试多个可能的路径
        possible_paths = [
            # 原始路径
            img_data,
            # 相对于MD文件的路径
            os.path.join(md_path_name, img_data),
            # 相对于当前文件的路径
            os.path.join(file_dir, img_data),
            # 处理以斜杠开头的路径
            os.path.join(md_path_name, img_data.lstrip('/')),
            # 处理以反斜杠开头的路径
            os.path.join(md_path_name, img_data.lstrip('\\')),
            # 处理以 ./ 开头的路径
            os.path.join(file_dir, img_data.lstrip('./')),
            # 处理以 .\ 开头的路径
            os.path.join(file_dir, img_data.lstrip('.\\')),
        ]
        
        # 检查所有可能的路径
        for path in possible_paths:
            normalized_path = os.path.normpath(path)
            if os.path.exists(normalized_path):
                return normalized_path
                
        # 如果都找不到，返回False
        # logger.error(f"尝试的路径: {possible_paths}")
        return False
    except Exception as e:
        logger.error(f"路径处理错误: {str(e)}, 原始路径: {img_data}")
        return False
        
def upload_image(mmwiki_url, headers, path, document_id, image_url, image_name, logger):
    '''
    上传图片：只用于上传png图片
    图片名称：使用md文档图片名称
    '''
    try:
        # 检查文件是否是图片
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}
        file_extension = image_url.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            logger.error(f"图片文件类型不支持: {image_url}")
            return False
        params = {
            'document_id': document_id,
            'guid': image_name,
        }
        # 使用动态生成的boundary
        multipart_encoder = MultipartEncoder(
            fields={
                'editormd-image-file': ('image-' +str(image_name), open(image_url, 'rb'), 'image/png')
            }
        )
        headers['Content-Type'] = multipart_encoder.content_type
        urlpath = mmwiki_url + path
        response = requests.post(urlpath, params=params, headers=headers, data=multipart_encoder)
        response.encoding = response.apparent_encoding
        # 检查是不是json
        if not response.text.startswith('{'):
            logger.error("服务器返回非JSON响应")
            return False
        try:
            response_text_json = response.json()
            if response_text_json['success'] == 1:
                img_urlpath = f"{response_text_json['url']}"
                logger.info(f"文档ID: {document_id}, 图片上传成功: {img_urlpath}")
                return img_urlpath
            else:
                logger.error(f"文档ID: {document_id}, 图片上传失败: {response_text_json['message']}")
                return False
        except Exception as e:
            logger.error(f"上传图片时发生错误: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"上传图片时发生错误: {str(e)}")
        return False

def image_upload(mmwiki_url, headers, path, document_id, image_url, logger):
    '''
    上传图片：只用于上传png图片
    图片名称：使用wiki上传接口的图片名称规则
    '''
    try:                
        # 检查文件是否是图片
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}
        file_extension = image_url.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            logger.error(f"图片文件类型不支持: {image_url}")
            return False
        image_name = int(time.time() * 1000)
        params = {
            'document_id': document_id,
            'guid': image_name,
        }
        # 使用动态生成的boundary
        multipart_encoder = MultipartEncoder(
            fields={
                'editormd-image-file': (f"image-{str(image_name)}.png", open(image_url, 'rb'), 'image/png')
            }
        )
        headers['Content-Type'] = multipart_encoder.content_type
        urlpath = mmwiki_url + path
        response = requests.post(urlpath, params=params, headers=headers, data=multipart_encoder)
        response.encoding = response.apparent_encoding
        # 检查是不是json
        if not response.text.startswith('{'):
            logger.error("服务器返回非JSON响应")
            return False
        try:
            response_text_json = response.json()
            if response_text_json['success'] == 1:
                img_urlpath = response_text_json['url']
                logger.info(f"文档ID: {document_id}, 图片上传成功: {img_urlpath}")
                return img_urlpath
            else:
                logger.error(f"文档ID: {document_id}, 图片上传失败: {response_text_json['message']}")
                return False
        except Exception as e:
            logger.error(f"上传图片时发生错误: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"上传图片时发生错误: {str(e)}")
        return False

def modify_image_path(mmwiki_url, headers, path, space_id, document_id, path_name, file_path, logger):
    try:
        with open(file_path, 'r', encoding='utf-8') as files:
            document_datas = files.readlines()
            for i, datas in enumerate(document_datas):
                if '![' in datas and '](' in datas and ')' in datas:
                    try:
                        # 使用更精确的分割方法提取图片URL
                        start_index = datas.find('](') + 2
                        # 查找最后一个右括号
                        end_index = datas.rfind(')')
                        if start_index > 1 and end_index > start_index:
                            image_url = datas[start_index:end_index]
                            """
                            # 获取图片名称
                            image_name = image_url.split('image-')[-1] if 'image-' in image_url else os.path.basename(image_url)
                            # 上传图片
                            img_urlpath = upload_image(mmwiki_url, headers, path, document_id, image_url, image_name, logger)
                            """
                            # URL解码
                            image_url = unquote(image_url)
                            # 规范化路径
                            normalized_img_path = local_img_path(path_name, file_path, image_url, logger)
                            if not normalized_img_path:
                                logger.error(f"[-] {file_path} 图片无法访问: {image_url}")
                                continue
                            else:
                                # 上传图片
                                img_urlpath = image_upload(mmwiki_url, headers, path, document_id, image_url, logger)
                                # 替换文档中的图片URL
                                modified_content = datas[:start_index] + img_urlpath + datas[end_index:]
                                document_datas[i] = modified_content
                    except Exception as e:
                        logger.error(f"处理单个图片时发生错误: {str(e)}")
                        continue
        document_datas = ''.join(document_datas)
        return document_datas
    except Exception as e:
        logger.error(f"修改图片路径时发生错误: {str(e)}")
        return False