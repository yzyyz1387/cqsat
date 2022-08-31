# python3
# -*- coding: utf-8 -*-
# @Time    : 2022/8/23 22:36
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : __init__.py.py
# @Software: PyCharm

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot.params import CommandArg
from nonebot.typing import T_State

from .calculate_mgsl import getGrid
from ..utils import *

grid_ca = on_command("我的网格", block=True)


@grid_ca.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    qq = event.user_id
    qth = await getQth(qq)
    if qth:
        await grid_ca.finish(f"你的网格是:{await getGrid(float(qth[0]), float(qth[1]))}")
    else:
        await grid_ca.finish(
            "你还没有设置QTH,请发送【绑定位置】\n查询具体位置的网格请发送【查询网格 经度 纬度】\n 经纬度用空格隔开")


grid_refer = on_command("查询网格", aliases={"计算网格"}, block=True)


@grid_refer.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, args: Message = CommandArg()):
    qq = event.user_id
    qth = await getQth(qq)
    if args:
        args = str(args).strip().split(" ")
        if len(args) == 1 and isChinese(args[0]):
            user_input = args[0]
            location = await getLlByAd(user_input)
            if location:
                await grid_refer.finish(f"{user_input}的经纬度：{location[0], location[1]}\n"
                                        f"{'-' * 10}\n"
                                        f"网格是:{await getGrid(float(location[0]), float(location[1]))}\n"
                                        f"{'-' * 10}")
            else:
                await grid_refer.finish(f"未查询到{user_input}的经纬度")
        elif len(args) >= 2:
            await grid_refer.finish(f"{args[0], args[1]}网格是:\n{'-'*10}{await getGrid(float(args[0]), float(args[1]))}\n{'-'*10}")
        else:
            await grid_refer.finish("你的输入貌似有误，检查一下吧")
    else:
        if qth:
            await grid_refer.finish(
                f"你没有发送经纬度，为你计算你的网格\n{'-' * 10}\n你的网格：{await getGrid(float(qth[0]), float(qth[1]))}\n{'-' * 10}"
                f"\n计算指定位置请发送：\n【计算网格 北京】\n【查询网格 经度 纬度】\n (经纬度用空格隔开)")
        else:
            await grid_refer.finish("错误：请输入参数\n命令示例：\n【计算网格 北京】\n【计算网格 75.8656 (空格) 39.3809】")
