#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging.config

import conf

from util import singleton


@singleton
class Logger():
    def __init__(self):
        file_name = conf.LOG_CONF_FILE
        try:
            logging.config.fileConfig(file_name)
        except IOError as io_err:
            dir_name = os.path.dirname(io_err.filename)
            os.makedirs(dir_name)
            logging.config.fileConfig(file_name)
        self.logger = logging.getLogger('allInfo')

    def get_logger(self):
        return self.logger
