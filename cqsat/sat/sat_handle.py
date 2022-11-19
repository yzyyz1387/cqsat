# python3
# -*- coding: utf-8 -*-
# @Time    : 2022/8/24 0:20
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : sat_handle.py
# @Software: PyCharm
import json
from datetime import datetime, timedelta

import nonebot
from dateutil.parser import ParserError
from dateutil.parser import parse
from nonebot import on_command, require
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, MessageEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.internal.params import ArgStr
from nonebot.params import CommandArg
from nonebot.typing import T_State

from .calculate_sat import download_ham_sat, data2Tle, calculate, get_tian_gong
from ..log import log
from ..path import *
from ..utils import *

logger = log()
Path.mkdir(LOCAL) if not Path.exists(LOCAL) else ...

bind_qth = on_command("绑定位置", aliases={"绑定QTH", "绑Qth", "绑定qth"}, block=True)


@bind_qth.got("QTH", prompt="请输入：\n  地名 \n或者输入：\n   经度 纬度 海拔\n\n参数用空格分隔\n")
async def _(
        event: MessageEvent,
        state: T_State,
        qth: str = ArgStr("QTH")):
    if not Path.exists(LOCAL):
        Path.mkdir(LOCAL)
    qq = event.user_id
    if qth in ["取消", "算了"]:
        await bind_qth.finish("已取消操作...")
    qth_list = str(qth).split(" ")
    logger.info(len(qth_list))
    if len(qth_list) == 1:
        temp_list = await getLlByAd(qth_list[0], type_="str")
        if temp_list:
            qth_list = temp_list
            qth_list.append(1000)
            await bind_qth.send(f"已自动获取到{qth}的经纬度信息, 海拔默认为1000米")
        else:
            await bind_qth.finish(f"没有找到{qth}的经纬度，请重新输入...")
    elif len(qth_list) < 3:
        await bind_qth.reject_arg("QTH",
                                  "你的输入貌似有错误呢，请输入：\n  地名 \n或者输入：\n   经度 纬度 海拔\n\n参数用空格分隔\n")
    # else:
    logger.info(qth_list)
    try:
        if float(qth_list[0]) and float(qth_list[1]) and float(qth_list[2]):
            state["qth"] = qth_list
            qth_data = {qq: qth_list}
            if not Path.exists(QTH):
                await yaml_dump(QTH, qth_data)
            else:
                await yaml_upload(QTH, qth_data)
            await bind_qth.finish(f"绑定成功：\n{qth_list}")
    except ValueError:
        await sub.reject_arg("QTH", "请输入：\n  地名 \n或者输入：\n   经度 纬度 海拔\n\n参数用空格分隔\n")


sub = on_command("订阅卫星", priority=2, block=True)


@sub.got("Sat", prompt="你要订阅那颗卫星？\n多颗卫星用空格分隔")
async def _(
        event: GroupMessageEvent,
        state: T_State,
        sat: str = ArgStr("Sat"), ):
    qq = event.user_id
    group = event.group_id
    sat_s = (await data2Tle())
    if sat in ["取消", "算了"]:
        await sub.finish("已取消操作...")
    try:
        qth = (await yaml_load(QTH))
    except FileNotFoundError:
        qth = {}
        await sub.finish("没有找到QTH文件，请发送【绑定位置】来绑定QTH\n绑定后可以发送【订阅卫星】来订阅卫星")
    if qq in qth:
        if sat == "天宫" or sat == "中国空间站" or sat in ["TIANGONG", "tiangong"]:
            state["sat"] = ["天宫"]
        else:
            user_sat = sat.split(" ")
            if len(user_sat) == 1:
                if sat.upper() in sat_s:
                    state["sat"] = [sat.upper()]
                else:
                    await sub.reject_arg("Sat", f"没有找到{sat},请重新输入：")
            else:
                temp = []
                for sat_ in user_sat:
                    if sat_ == "天宫" or sat == "中国空间站" or sat in ["TIANGONG", "tiangong"]:
                        temp.append("天宫")
                    elif sat_.upper() in sat_s:
                        temp.append(sat_.upper())
                    else:
                        await sub.send(f"没有找到{sat_}")
                state["sat"] = temp
    else:
        await sub.finish("请先发送【绑定位置】来绑定QTH\n绑定后可以发送【订阅卫星】来订阅卫星")


@sub.got("E_angle", prompt="请输入最低仰角：")
async def _(
        event: GroupMessageEvent,
        state: T_State,
        ang: str = ArgStr("E_angle")):
    qq = event.user_id
    group = event.group_id
    # sat = state["sat"]
    if ang in ["取消", "算了"]:
        await sub.finish("已取消操作...")
    try:
        qth = (await yaml_load(QTH))
    except FileNotFoundError:
        qth = {}
        await sub.finish("没有找到QTH文件，请发送【绑定位置】来绑定QTH\n绑定后可以发送【订阅卫星】来订阅卫星")
    try:
        ang = ang.replace("°", "").replace("度", "")
        if not 0 < int(ang) <= 90:
            await sub.reject_arg("E_angle", "仰角输入有误，应该在0-90之间，请重新输入：")
        else:
            state["ang"] = ang
        if not Path.exists(CONFIG):
            data = {group: {qq: {}}}
            for sat in state["sat"]:
                temp = {"仰角": state['ang'], "qth": qth[qq], "last_send": ""}
                data[group][qq][sat] = temp
            await yaml_dump(CONFIG, data)
        else:
            data = (await yaml_load(CONFIG))
            for sat in state["sat"]:
                if qq in qth:
                    if group in data:
                        if qq in data[group]:
                            data[group][qq][sat] = {"仰角": state['ang'], "qth": qth[qq], "last_send": ""}
                        else:
                            data[group][qq] = {sat: {"仰角": state['ang'], "qth": qth[qq], "last_send": ""}}
                    else:
                        data[group] = {qq: {sat: {"仰角": state['ang'], "qth": qth[qq], "last_send": ""}}}
                    await yaml_dump(CONFIG, data)
        await sub.finish("订阅成功:"
                         f"\n卫星：{state['sat']}"
                         f"\n最低仰角：{state['ang']}"
                         f"\nQTH：{qth[qq]}")
    except ValueError:
        await sub.reject_arg("E_angle", "仰角输入有误，应该是0-90之间的数字，请重新输入：")


unsub = on_command("取消订阅", block=True)


@unsub.handle()
async def unsub_(bot: Bot, event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    qq = event.user_id
    group = event.group_id
    if args:
        sat_s = str(args).split(" ")
        data = (await yaml_load(CONFIG))
        for sat in sat_s:
            if isChinese(sat):
                pass
            else:
                sat = sat.upper()
            if group in data:
                if qq in data[group]:
                    if sat in data[group][qq]:
                        del data[group][qq][sat]
                        await yaml_dump(CONFIG, data)
                        await sub.send(f"已取消订阅{sat}")
                    else:
                        await unsub.finish(f"你在本群没有订阅{sat}")
                else:
                    await unsub.finish("你在本群没有订阅卫星")
            else:
                await unsub.finish("本群没有用户订阅卫星\n订阅请发送【订阅卫星】")
    else:
        await unsub.finish("取消订阅命令为：\n   取消订阅+卫星名称\n例如：\n   取消订阅AO-72\n多颗卫星用空格分隔")


refer_sat_subs = on_command("查询订阅", aliases={"我的订阅"}, block=True)


@refer_sat_subs.handle()
async def refer_sat_(bot: Bot, event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    qq = event.user_id
    group = event.group_id
    data = (await yaml_load(CONFIG))
    if group in data:
        if qq in data[group]:
            await refer_sat_subs.send(MessageSegment.at(qq) + ",你在本群订阅了以下卫星：\n")
            reply = ""
            for sat in data[group][qq]:
                reply += sat + "\n"
            await refer_sat_subs.send(reply)
        else:
            await refer_sat_subs.send(f"{qq}在本群没有订阅卫星")
    else:
        await refer_sat_subs.send(f"本群没有用户订阅卫星\n订阅请发送【订阅卫星】")


refer_sat = on_command("卫星列表", block=True)


@refer_sat.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, args: Message = CommandArg()):
    sat_dict = (await data2Tle())
    sat_list = []
    for i in sat_dict.keys():
        sat_list.append(i)
    reply = "\n".join(sat_list)
    await refer_sat.send(f"卫星列表：\n{reply}")


specified = on_command("查询卫星", aliases={"计算卫星"}, block=True)


@specified.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, args: Message = CommandArg()):
    qq = event.user_id
    input_arg = str(args).split(" ")
    sat_dict = (await data2Tle())
    sat = input_arg[0]
    try:
        qth = (await yaml_load(QTH))[qq]
    except KeyError:
        qth = ["0", "0", "0"]
        await specified.finish("你没有设置QTH，请发送【绑定位置】绑定QTH")
    except FileNotFoundError:
        qth = ["0", "0", "0"]
        await specified.finish("你没有设置QTH，请发送【绑定位置】绑定QTH")
    try:
        add = int(input_arg[1])
    except IndexError:
        add = 0
        await specified.send(f"你没有发送时间，将计算 {sat} 现在的状态")
    time = (datetime.utcnow() + timedelta(minutes=add)).strftime("%Y-%m-%d %H:%M:%S")
    send_time = (datetime.now() + timedelta(minutes=add)).strftime("%Y-%m-%d %H:%M:%S")
    if not isChinese(sat):
        sat = sat.upper()
    else:
        sat_dict = (await get_tian_gong())
    if sat in sat_dict:
        out = await calculate(sat, qth, time=time)
        reply = f"对于QTH:：{qth}\n{sat} 在 {send_time} ：\n仰角为：{round(float(out[1]), 2)}°\n方位角:{round(float(out[0]), 2)}°\n相对速率为：{round(float(out[2]), 2)} "
        await specified.send(reply)
    else:
        await specified.send(f"{sat}不存在")


async def aps():
    if not Path.exists(CONFIG):
        return
    elif read_all(CONFIG) == "":
        return
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        # FIXME 目前是每次都下载
        await download_ham_sat()
        data = (await yaml_load(CONFIG))
    except FileNotFoundError:
        data = await download_ham_sat()

    for group in data:
        for qq in data[group]:
            for sat in data[group][qq]:
                try:
                    last = parse(data[group][qq][sat]["last_send"])
                except ParserError:
                    last = parse("2001-11-04 00:00:00")
                except TypeError:
                    last = parse("2001-11-04 00:00:00")
                now_to_calculate = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
                min_add = 10
                if int((parse(now_to_calculate) - last).total_seconds() / 60) >= 60:
                    now = (datetime.utcnow() + timedelta(minutes=min_add)).strftime("%Y-%m-%d %H:%M:%S")
                    result = await calculate(sat, data[group][qq][sat]["qth"], now)
                    sated = []
                    if float(result[1]) > 0:
                        logger.info(f"@{qq} 订阅的 {sat} 将入境，正准备计算最高仰角")
                        i = 0
                        az_list = []
                        alt_list = []
                        time_highest_point = {}
                        result_ = await calculate(sat, data[group][qq][sat]["qth"], now)
                        while float(result_[1]) >= 0:
                            now = (datetime.utcnow() + timedelta(minutes=min_add + int(i))).strftime(
                                "%Y-%m-%d %H:%M:%S")
                            result_ = await calculate(sat, data[group][qq][sat]["qth"], now)
                            i += 1
                            az_list.append(float(result_[0]))
                            alt_list.append(float(result_[1]))
                            logger.debug("方位角信息：")
                            logger.debug(az_list)
                            logger.debug("仰角信息：")
                            logger.debug(alt_list)
                            time_highest_point[now] = float(result_[1])
                        a1 = sorted(time_highest_point.items(), key=lambda x: x[1], reverse=True)
                        if float(a1[0][1]) >= float(data[group][qq][sat]["仰角"]):
                            logger.info("最高仰角大于用户设定的值，正准备提醒用户")
                            if sat not in sated:
                                logger.info("成功预测到卫星。正在尝试发送数据")
                                azimuth = float(result_[0])
                                direction = az2direction(azimuth)
                                azimuth_ = float(result[0])
                                r_direction = az2direction(azimuth_)
                                try:
                                    await nonebot.get_bot().send_group_msg(
                                        group_id=group,
                                        message=MessageSegment.at(qq) + f'\n'
                                                                        f'{sat} 卫星将于 {(parse(a1[0][0]) + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")} 出现最高仰角\n'
                                                                        f'角度为{round(float(a1[0][1]), 1)}°\n'
                                                                        f'入境方位为：{r_direction}\n'
                                                                        f'入境方位角：{round(float(result[0]), 1)}\n出境方位为：{direction}\n '
                                                                        f'出境方位角：{round(azimuth, 1)}°')
                                except ActionFailed:
                                    logger.error("消息发送失败，账号可能被风控")
                                sated.append(sat)
                            data[group][qq][sat]["last_send"] = now_to_calculate
                            await yaml_dump(CONFIG, data)
                        else:
                            logger.info("最高仰角小于用户设定的值，不需要提醒")
                else:
                    logger.info("一小时内该卫星已过境，跳过此卫星")


scheduler = require("nonebot_plugin_apscheduler").scheduler

scheduler.add_job(aps, 'cron', minute="0/1", id="sat")
