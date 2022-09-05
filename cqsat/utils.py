# python3
# -*- coding: utf-8 -*-
# @Time    : 2022/8/21 2:09
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : utils.py
# @Software: PyCharm
import json
import random
from typing import Union, Optional, TextIO

import httpx
import yaml
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.matcher import Matcher

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


async def send_ex(
        matcher: Matcher,
        ex_bank: dict,
        last: int,
        qq: int,
        level: str,
        state: dict,
        img: Path,
        mode: str = "exec"
):
    """
    发送题目
    :param img: Path
    :param matcher: Matcher
    :param ex_bank: 题录字典
    :param last: 发送的题目
    :param qq: qq
    :param level: 等级
    :param state: state
    :param mode: exec 或 exam
    :return:
    """
    state_for_time = EXAM_CACHE / matcher.state["level"].upper() / f"{matcher.state['qq']}_state.txt"
    logger.info(f"发送题目：{last}")
    if mode == "exec":
        temp = {qq: {"level": level, "last": last}}
        await yaml_upload(EXERCISE_TEMP, temp)
    ex_list = state["ex_list"]
    IMG = img
    last = str(last)
    this_ex = ex_bank[last]
    pic = this_ex["P"]
    if pic:
        state["pic_to_send"] = pic
    else:
        state["pic_to_send"] = None
    this_answer = this_ex["A"]
    state["this_answer"] = this_answer
    this_answer_group = []
    for i in this_ex:
        if i in ["A", "B", "C", "D"]:
            this_answer_group.append(this_ex[i])
    this_answer_group = random.sample(this_answer_group, len(this_answer_group))
    dic_to_send = {"Q": this_ex["Q"], "A": this_answer_group[0], "B": this_answer_group[1], "C": this_answer_group[2],
                   "D": this_answer_group[3]}
    state['this_send'] = dic_to_send
    for i in dic_to_send:
        if dic_to_send[i] == this_answer:
            answer = i
            state["this_answer"] = answer
    reply = (
        f"{last if not ex_list else ex_list.index(int(last)) + 1}、{dic_to_send['Q']}\n"
        f"A. {dic_to_send['A']}\n"
        f"B. {dic_to_send['B']}\n"
        f"C. {dic_to_send['C']}\n"
        f"D. {dic_to_send['D']}\n"
    )
    state_2 = {"this_config": state["this_config"], "correct": state["correct"], "wrong": state["wrong"]}

    await write_(state_for_time, json.dumps(state_2))
    if state["pic_to_send"]:
        await matcher.send(MessageSegment.image(f"file:///{(IMG / state['pic_to_send']).absolute()}"))
        await matcher.reject(state["user_notice"] + reply)
    else:
        await matcher.reject(state["user_notice"] + reply)
    return state
