import logging
from logging.handlers import TimedRotatingFileHandler
import time
import os

def logger_init():
    # 创建日志对象
    logger = logging.getLogger()
    
    # 如果logger已经有handlers，说明已经初始化过，直接返回
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)

    # 定义日志文件名格式
    log_dir = f"./logs/{time.strftime('%Y%m%d')}"
    log_filename = os.path.join(log_dir, f"log_{time.strftime('%Y%m%d')}.log")
    error_filename = os.path.join(log_dir, f"error_{time.strftime('%Y%m%d')}.log")
    # 检查并创建日志目录
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 创建普通日志文件处理器
    file_handler = TimedRotatingFileHandler(
        filename=log_filename, when="midnight", interval=1, backupCount=30, encoding="utf-8"
    )
    file_fmt = "%(asctime)s - %(levelname)s - %(message)s"
    file_handler.setFormatter(logging.Formatter(file_fmt))
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    # 创建错误日志文件处理器
    error_handler = TimedRotatingFileHandler(
        filename=error_filename, when="midnight", interval=1, backupCount=30, encoding="utf-8"
    )
    error_handler.setFormatter(logging.Formatter(file_fmt))
    error_handler.setLevel(logging.ERROR)
    logger.addHandler(error_handler)
    # 创建控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = "%(asctime)s - %(levelname)s - %(message)s"
    console_handler.setFormatter(logging.Formatter(console_fmt))
    logger.addHandler(console_handler)

    return logger