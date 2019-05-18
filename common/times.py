#!/usr/bin/env python
# -*- coding:utf-8 -*-

import threading
import time
from common.logger import Logger


def func_sleep(func_name, sleep_time):
    def wrap_func():
        while True:
            try:
                flag = func_name()
                if flag:
                    break

            except Exception, e:
                Logger.logger.error(e, exc_info=1)
            time.sleep(sleep_time)

    return wrap_func


def exec_time(func):
    def wrap_func(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        Logger.logger.info("%s take %sms for {%s}" %
                           (threading.currentThread().getName(),
                            int((time.time() - start) * 1000), func.__name__))
        return result

    return wrap_func