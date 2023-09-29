# python3
# -*- coding: utf-8 -*-
# @Time    : 2023-09-30 1:01
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : sat_shoot_url_bank.py
# @Software: PyCharm
import json

from ..utils import *
from ..path import *
from ..config import *

if plugin_config.sat_proxy_url:
    logger.info(plugin_config.sat_proxy_url)

url_bank = [
    {
        "url": "https://www.df2et.de/tevel/",
        "cmd": ["t", "查询小火车", "小火车"],
        "path": "tevel.png",
        "locator": "html",
        "time_out": 10
    },
    {
        "url": "https://amsat.org/status/index.php",
        "cmd": ["a", "amsat"],
        "path": "amsat.png",
        "locator": "xpath=/html/body/center[4]",
        "time_out": 10

    },
    {
        "url": "https://www.github.com/yzyyz1387/cqsat",
        "cmd": ["home", "cqsat"],
        "path": "cqsat.png",
        "locator": "html",
        "time_out": 5,
        "proxy": plugin_config.sat_proxy_url,
        "timeout": 90000,
    },
    {
        "url": "https://sathunt.com/",
        "cmd": ['css', 'cs'],
        "path": "css.png",
        "locator": "html",
        "time_out": 0,
        "proxy": plugin_config.sat_proxy_url,
        "until": "networkidle",
    }

]


class UrlBank:
    def __init__(self):
        if SHOOTS_URL_BANK.exists():
            self.url_bank = json_load(SHOOTS_URL_BANK)
        else:
            self.url_bank = url_bank
            json_upload(SHOOTS_URL_BANK, self.url_bank)

    def get(self):
        return json_load(SHOOTS_URL_BANK) if SHOOTS_URL_BANK.exists() else self.url_bank

    def add(self, **kwargs):
        self.url_bank.append(kwargs)
        json_upload(SHOOTS_URL_BANK, url_bank)

    def remove(self, **kwargs):
        url = kwargs.get("url", " ")
        cmd = kwargs.get("cmd", " ")
        path = kwargs.get("path", " ")
        result = False
        for item in self.url_bank:
            if url in item["url"] or cmd in item["cmd"] or path in item["path"]:
                logger.info(f"删除{item}")
                self.url_bank.remove(item)
                json_upload(SHOOTS_URL_BANK, self.url_bank)
                result = True
            else:
                result = False
        return result

    @staticmethod
    def default():
        json_upload(SHOOTS_URL_BANK, url_bank)
        return True
