# python3
# -*- coding: utf-8 -*-
# @Time    : 2022/8/21 2:09
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : utils.py
# @Software: PyCharm
from typing import Union, Optional, TextIO

import httpx
import yaml

from .log import log
from .path import *

logger = log()


async def http_get(url: str, type_: str = "text") -> Union[str, dict]:
    """
    获取链接中的内容
    :param type_: text 或 json
    :param url: 链接
    :return:
    """
    try:
        async with httpx.AsyncClient() as client:
            result = (await client.get(url))
            if type_ == "json":
                return result.json()
            else:
                return result.text
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


async def read_(path: Union[Path, str]) -> TextIO:
    """
    读取文件
    :param path: 文件路径
    :return:
    """
    with open(path, 'r', encoding='utf-8') as f:
        return f


async def read_all(path: Union[Path, str]) -> str:
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


async def yaml_upload(path: str, data: dict) -> None:
    """
    更新yaml文件
    :param path: 文件路径
    :param data: 数据
    :return:
    """
    raw = await yaml_load(path)
    raw.update(data)
    await yaml_dump(path, raw)


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


async def getQth(qq: int) -> Optional[list]:
    """
    获取QTH
    :param qq: QQ号
    :return: None 或 [经度， 纬度， 海拔]
    """
    qth_dict = await yaml_load(QTH)
    if qq in qth_dict:
        return qth_dict[qq]
    else:
        return None


async def getLlByAd(address: str, type_: str = "float") -> Optional[list]:
    """
    根据地名获取经纬度
    :param type_: float 或 str
    :param address: 地名
    :return: None 或 [经度， 纬度]
    """
    temp_dic: dict = await http_get(f"https://apis.map.qq.com/jsapi?qt=geoc&addr={address}", type_="json")
    if temp_dic and temp_dic["info"]["error"] == 0:
        if type_ == "float":
            return [float(temp_dic["detail"]["pointx"]), float(temp_dic["detail"]["pointy"])]
        elif type_ == "str":
            return [temp_dic["detail"]["pointx"], temp_dic["detail"]["pointy"]]
    else:
        return None
