# python3
# -*- coding: utf-8 -*-
# @Time    : 2022/8/21 2:20
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : path.py
# @Software: PyCharm
from pathlib import Path

from nonebot import get_driver
from nonebot import logger


#  新建一个类，用来存放各种路径

LOCAL = Path() / 'cqsat'
HAM_SAT = LOCAL / 'ham_sat.txt'
TIANGONG = LOCAL / 'tiangong.json'
CONFIG = LOCAL / 'config.yml'
TEMP = LOCAL / 'temp.yaml'
DATA_DICT = LOCAL / 'data.json'
QTH = LOCAL / 'qth.yml'
LOG = LOCAL / 'log.log'
EXERCISE_TEMP = LOCAL / 'exercise_temp.yml'
EXAM_CACHE = LOCAL / 'exam'
EXAM_CACHE_A = EXAM_CACHE / 'A'
EXAM_CACHE_B = EXAM_CACHE / 'B'
EXAM_CACHE_C = EXAM_CACHE / 'C'

path_list = [LOCAL, EXAM_CACHE, EXAM_CACHE_A, EXAM_CACHE_B, EXAM_CACHE_C]
driver = get_driver()
global_config = driver.config


@driver.on_bot_connect
async def _():
    await plugin_init()


async def plugin_init():
    """
    初始化插件
    :return:
    """
    for dir_ in path_list:
        if not dir_.exists():
            dir_.mkdir()
    logger.success('cqsat插件初始化检测完成')
