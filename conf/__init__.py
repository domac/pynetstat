#!/usr/bin/env python
# -*- coding: utf8 -*-
import ConfigParser
import os

from util.os_util import DEBUG

CONF_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_CONF_FILE = CONF_DIR + '/logging.ini'
CONFIG_INIT_FILE = CONF_DIR + '/config.init'


class Configure():
    config_dict = {}
    last_modify_time = None

    def __init__(self, config_path='config.ini', debug=False):
        if debug:
            config_path = 'config_debug.ini'

        self.config_path = CONF_DIR + '/' + config_path
        config = ConfigParser.ConfigParser()
        config.readfp(open(self.config_path, "r"))
        self.config = config
        Configure.last_modify_time = os.stat(self.config_path).st_mtime

    def get_config(self, alias):
        self.reload()
        return dict(item for item in self.config.items(alias))

    def get_config_all(self):
        self.reload()
        config_all = {}
        for section in self.config.sections():
            config_all[section] = self.get_config(section)
        return config_all

    def reload(self):
        _last_modify_time = os.stat(self.config_path).st_mtime
        if _last_modify_time != Configure.last_modify_time:
            config = ConfigParser.ConfigParser()
            config.readfp(open(self.config_path, "r"))
            self.config = config
            Configure.last_modify_time = os.stat(self.config_path).st_mtime


cfg = Configure(debug=DEBUG)