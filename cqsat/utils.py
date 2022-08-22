# python3
# -*- coding: utf-8 -*-
# @Time    : 2022/8/21 2:09
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : utils.py
# @Software: PyCharm
from typing import Union

import httpx
import yaml

from .log import log

logger = log()


async def http_get(url: str) -> str:
    """
    获取链接中的内容
    :param url: 链接
    :return:
    """
    try:
        async with httpx.AsyncClient() as client:
            return (await client.get(url)).text
    except Exception as e:
        logger.error(e)
        return ""


async def http_post(url: str, data: dict) -> str:
    """
    发送post请求
    :param url: 链接
    :param data: 参数
    :return:
    """
    try:
        async with httpx.AsyncClient() as client:
            return (await client.post(url, data=data)).text
    except Exception as e:
        logger.error(e)
        return ""


async def write_(path: str, data: str) -> None:
    """
    写入文件
    :param path: 文件路径
    :param data: 数据
    :return:
    """
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)
        f.close()


async def read_(path: str):
    """
    读取文件
    :param path: 文件路径
    :return:
    """
    with open(path, 'r', encoding='utf-8') as f:
        return f


async def read_all(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


async def yaml_load(path: str) -> dict:
    """
    读取yaml文件
    :param path: 文件路径
    :return:
    """
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=yaml.FullLoader)


async def yaml_dump(path: str, data: dict) -> None:
    """
    写入yaml文件
    :param path: 文件路径
    :param data: 数据
    :return:
    """
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)
        f.close()


def az2direction(azimuth: Union[float, int]):
    """
    将方位角转换为方位
    :param azimuth: 方位角
    :return: 方位
    """
    if 0 <= azimuth < 45:
        return "北偏东"
    elif 45 <= azimuth < 90:
        return "东偏北"
    elif 90 <= azimuth < 135:
        return "东偏南"
    elif 135 <= azimuth < 180:
        return "南偏东"
    elif 180 <= azimuth < 225:
        return "南偏西"
    elif 225 <= azimuth < 270:
        return "西偏南"
    elif 270 <= azimuth < 315:
        return "西偏北"
    elif 315 <= azimuth < 360:
        return "北偏西"


def isChinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


