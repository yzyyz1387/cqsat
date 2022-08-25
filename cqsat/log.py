# python3
# -*- coding: utf-8 -*-
# @Time    : 2022/8/21 2:15
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : log.py
# @Software: PyCharm
import os
import sys
import logging
from pathlib import Path
from .path import *


def log(path: str = LOG) -> logging.Logger:
    """
    日志
    :return:
    """
    Path.mkdir(LOCAL) if not Path.exists(LOCAL) else ...
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s-%(levelname)s: %(message)s')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.formatter = formatter
    console_handler.setLevel(logging.INFO)
    logfile = path
    File_handler = logging.FileHandler(logfile, mode='a', encoding='utf-8')
    File_handler.setFormatter(formatter)
    File_handler.setLevel(logging.DEBUG)
    if not logger.handlers:
        logger.addHandler(File_handler)
        logger.addHandler(console_handler)
        print(logger.handlers)
    return logger
