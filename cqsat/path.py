# python3
# -*- coding: utf-8 -*-
# @Time    : 2022/8/21 2:20
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : path.py
# @Software: PyCharm
import os
from pathlib import Path
from typing import Optional

from nonebot import get_driver
from nonebot import logger
from playwright.async_api import async_playwright, Browser

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
TLE_CACHE_PATH = LOCAL / 'tle_cache'
CACHE_CSS = TLE_CACHE_PATH / 'css.cache'
CACHE_OTHER = TLE_CACHE_PATH / 'other.cache'
SHOOTS_OUT_PATH = LOCAL / 'shoots_out'
SHOOTS_URL_BANK = LOCAL / 'shoots_url_bank.json'
MDC_GENERATOR_PATH = LOCAL / 'mdc_generator'
USER_GLOBAL_NO_DISTURB = LOCAL / 'user_no_disturb.yml'


path_list = [LOCAL, EXAM_CACHE, EXAM_CACHE_A, EXAM_CACHE_B, EXAM_CACHE_C, TLE_CACHE_PATH, SHOOTS_OUT_PATH, MDC_GENERATOR_PATH]
driver = get_driver()
global_config = driver.config


@driver.on_bot_connect
async def _():
    await plugin_init()
    await browser_init()


async def plugin_init():
    """
    初始化插件
    :return:
    """
    for dir_ in path_list:
        if not dir_.exists():
            dir_.mkdir()
    logger.success('cqsat插件初始化检测完成')


async def browser_init(**kwargs) -> Optional[Browser]:
    global _browser
    try:
        browser = await async_playwright().start()
        _browser = await browser.chromium.launch(**kwargs)
        return _browser
    except NotImplementedError:
        logger.warning("windows环境下 初始化playwright失败，相关功能将被限制....")
    except Exception as e:
        logger.warning(f"启动chromium发生错误 {type(e)}：{e}")
        try:
            if _browser:
                await _browser.close()
        except NameError:
            logger.info("正在安装浏览器...")
            os.system("playwright install chromium")
    return None