# -*- coding: UTF-8 -*-
"""
@Filename: Parallel_Processing.py
@Author: s1g0day
@Create Date: 2025-04-30
@Description: MM-Wiki文档自动上传工具的并行处理模块
"""

import os
import time
import concurrent.futures
from multiprocessing import cpu_count, Pool, Manager

class ThreadPoolManager:
    """线程池管理器"""
    
    def __init__(self, max_workers=None, thread_name_prefix="WikiThread"):
        """
        初始化线程池管理器
        
        Args:
            max_workers: 最大工作线程数，默认为None（使用系统默认值）
            thread_name_prefix: 线程名称前缀
        """
        self.max_workers = max_workers if max_workers else min(32, (cpu_count() or 1) * 4)
        self.thread_name_prefix = thread_name_prefix
        self.executor = None
        self.futures = []
    
    def init_pool(self):
        """初始化线程池"""
        if self.executor is None or self.executor._shutdown:
            self.executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_workers,
                thread_name_prefix=self.thread_name_prefix
            )
        return self.executor
    
    def submit_task(self, func, *args, **kwargs):
        """
        提交任务到线程池
        
        Args:
            func: 要执行的函数
            *args, **kwargs: 函数参数
            
        Returns:
            Future对象
        """
        if self.executor is None:
            self.init_pool()
        
        future = self.executor.submit(func, *args, **kwargs)
        self.futures.append(future)
        return future
    
    def add_callback(self, future, callback):
        """为Future添加回调函数"""
        future.add_done_callback(callback)
    
    def wait_for_tasks(self, timeout=None):
        """
        等待所有任务完成
        
        Args:
            timeout: 超时时间，默认为None（无限等待）
            
        Returns:
            (done, not_done): 已完成和未完成的Future集合
        """
        return concurrent.futures.wait(
            self.futures,
            timeout=timeout,
            return_when=concurrent.futures.ALL_COMPLETED
        )
    
    def cancel_all_tasks(self):
        """取消所有未完成的任务"""
        for future in self.futures:
            if not future.done():
                future.cancel()
    
    def shutdown(self, wait=True):
        """关闭线程池"""
        if self.executor and not self.executor._shutdown:
            self.executor.shutdown(wait=wait)
            self.futures = []

class ProcessPoolManager:
    """进程池管理器"""
    
    def __init__(self, max_workers=None):
        """
        初始化进程池管理器
        
        Args:
            max_workers: 最大工作进程数，默认为None（使用CPU核心数）
        """
        self.max_workers = max_workers if max_workers else max(1, (cpu_count() or 1) - 1)
        self.pool = None
        self.manager = None
        self.results = []
    
    def init_pool(self):
        """初始化进程池和管理器"""
        if self.pool is None:
            self.manager = Manager()
            self.pool = Pool(processes=self.max_workers)
        return self.pool
    
    def submit_task(self, func, *args, **kwargs):
        """
        提交任务到进程池
        
        Args:
            func: 要执行的函数
            *args, **kwargs: 函数参数
            
        Returns:
            AsyncResult对象
        """
        if self.pool is None:
            self.init_pool()
        
        result = self.pool.apply_async(func, args=args, kwds=kwargs)
        self.results.append(result)
        return result
    
    def wait_for_tasks(self, timeout=None):
        """
        等待所有任务完成
        
        Args:
            timeout: 超时时间，默认为None（无限等待）
            
        Returns:
            所有任务的结果列表
        """
        start_time = time.time()
        completed_results = []
        
        for result in self.results:
            remaining_time = None
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    break
                remaining_time = timeout - elapsed
            
            try:
                completed_results.append(result.get(timeout=remaining_time))
            except Exception as e:
                completed_results.append(e)
        
        return completed_results
    
    def shutdown(self, wait=True):
        """关闭进程池"""
        if self.pool:
            self.pool.close()
            if wait:
                self.pool.join()
            else:
                self.pool.terminate()
            self.pool = None
            self.results = []
        if self.manager:
            self.manager.shutdown()
            self.manager = None

# 工具函数
def chunk_list(lst, chunk_size):
    """
    将列表分割成指定大小的块
    
    Args:
        lst: 要分割的列表
        chunk_size: 每个块的大小
        
    Returns:
        分割后的块列表
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def parallel_map(func, items, max_workers=None, use_processes=False):
    """
    并行映射函数到项目列表
    
    Args:
        func: 要应用的函数
        items: 项目列表
        max_workers: 最大工作线程/进程数
        use_processes: 是否使用进程池而不是线程池
        
    Returns:
        结果列表
    """
    if use_processes:
        pool_manager = ProcessPoolManager(max_workers)
    else:
        pool_manager = ThreadPoolManager(max_workers)
    
    try:
        pool_manager.init_pool()
        for item in items:
            if isinstance(item, tuple):
                pool_manager.submit_task(func, *item)
            else:
                pool_manager.submit_task(func, item)
        
        results = pool_manager.wait_for_tasks()
        return results
    finally:
        pool_manager.shutdown()