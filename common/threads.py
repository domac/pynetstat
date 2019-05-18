#!/usr/bin/env python
# -*- coding:utf-8 -*-
from multiprocessing.pool import ThreadPool
import threading
import weakref
import time
from common.logger import Logger


class ThreadHelper(object):
    thread_lock = threading.Lock()

    @staticmethod
    def instance(pool_size=20):
        # New instance after double check
        if not hasattr(ThreadHelper, "_instance"):
            with ThreadHelper.thread_lock:
                if not hasattr(ThreadHelper, "_instance"):
                    ThreadHelper._instance = ThreadHelper()
                    # 此类创建池子在linux win运行均好 全局模块变量linux无法正常运行
                    if not hasattr(threading.current_thread(), "_children"):
                        threading.current_thread(
                        )._children = weakref.WeakKeyDictionary()
                    _thread_pool = ThreadPool(pool_size)
                    ThreadHelper._instance.thread_pool = _thread_pool
                else:
                    Logger.logger.warn(
                        'class ThreadHelper has no attr _instance!!!')
        return ThreadHelper._instance


def get_thread_pool(pool_size=20, singleton=True):
    """
    获取线程池
    :param pool_size:
    :return:
    """
    thread_pool = None
    if singleton:
        thread_helper = ThreadHelper.instance(pool_size)
        if hasattr(thread_helper, 'thread_pool'):
            thread_pool = thread_helper.thread_pool
        else:
            time.sleep(1)
            thread_helper = ThreadHelper.instance()
            if hasattr(thread_helper, 'thread_pool'):
                thread_pool = thread_helper.thread_pool
    else:
        # 此类创建池子在linux win运行均好 全局模块变量linux无法正常运行
        if not hasattr(threading.current_thread(), "_children"):
            threading.current_thread()._children = weakref.WeakKeyDictionary()
        thread_pool = ThreadPool(pool_size)
    return thread_pool


def start_thread(func, args=(), daemon=True):
    thread = threading.Thread(target=func, args=args)
    thread.setDaemon(daemon)
    thread.start()


def func_sleep(func_name, sleep_default_time=60):
    def wrap_func(*args, **kwargs):
        while True:
            try:
                func_name(*args, **kwargs)
            except Exception, e:
                Logger.logger.error(e, exc_info=1)
            time.sleep(sleep_default_time)

    return wrap_func


def get_current_thread_name():
    return threading.currentThread().getName()


def join_current_thread(timeout=3):
    return threading.currentThread().join(timeout=timeout)
