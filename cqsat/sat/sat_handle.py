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

from ..mgsl import getGrid
from .calculate_sat import download_ham_sat, data2Tle, calculate, get_tian_gong
from ..log import log
from ..path import *
from ..utils import *

logger = log()
Path.mkdir(LOCAL) if not Path.exists(LOCAL) else ...

bind_qth = on_command("绑定位置", aliases={"绑定QTH", "绑Qth", "绑定qth"}, block=True)


@bind_qth.got("QTH", prompt="请输入：\n  地名 \n或者输入：\n   经度 纬度 海拔\n\n参数用空格分隔\n\n发送【取消】来取消操作")
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


@sub.got("Sat", prompt="你要订阅那颗卫星？\n多颗卫星用空格分隔\n发送【取消】来取消操作")
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
                if sat in sat_s or sat.upper() in sat_s:
                    state["sat"] = [sat.upper()]
                else:
                    await sub.reject_arg("Sat",
                                         f"没有找到{sat},请重新输入：\n\n输入【算了】取消操作\n输入【卫星列表】查看收录卫星")
            else:
                temp = []
                for sat_ in user_sat:
                    if sat_ == "天宫" or sat == "中国空间站" or sat in ["TIANGONG", "tiangong"]:
                        temp.append("天宫")
                    elif sat_.upper() in sat_s:
                        temp.append(sat_.upper())
                    else:
                        await sub.send(f"没有找到{sat_}，\n输入【卫星列表】查看收录卫星")
                state["sat"] = temp
    else:
        await sub.finish("请先发送【绑定位置】来绑定QTH\n绑定后可以发送【订阅卫星】来订阅卫星")


@sub.got("E_angle", prompt="请输入最低仰角：\n发送【取消】来取消操作")
async def _(
        event: GroupMessageEvent,
        state: T_State,
        ang: str = ArgStr("E_angle")):
    # sat = state["sat"]
    if ang in ["取消", "算了"]:
        await sub.finish("已取消操作...")
    try:
        ang = ang.replace("°", "").replace("度", "")
        if not 0 < int(ang) <= 90:
            await sub.reject_arg("E_angle", "仰角输入有误，应该在0-90之间，请重新输入：")
        else:
            state["ang"] = ang
    except ValueError:
        await sub.reject_arg("E_angle", "仰角输入有误，应该是0-90之间的数字，请重新输入：")


@sub.got("no_disturb", prompt="是否对上述卫星开启夜间免打扰模式？\n发送【是/否】\n发送【取消】来取消操作")
async def _(event: GroupMessageEvent,
            state: T_State,
            no_disturb: str = ArgStr("no_disturb")):
    nd_time_range = [20, 8]
    qq = event.user_id
    group = event.group_id
    if no_disturb in ["取消", "算了"]:
        await sub.finish("已取消操作...")
    elif no_disturb in ["是", "开启", "开", "y", "Y", "yes", "Yes", "YES"]:
        state["no_disturb"] = True
    elif no_disturb in ["否", "不开启", "不开", "不", "n", "N", "no", "No", "NO"]:
        state["no_disturb"] = False
    else:
        await sub.reject_arg("no_disturb", "输入有误，请重新输入：\n发送【是/否】\n发送【取消】来取消操作")
    try:
        qth = (await yaml_load(QTH))
    except FileNotFoundError:
        qth = {}
        await sub.finish("没有找到QTH文件，请发送【绑定位置】来绑定QTH\n绑定后可以发送【订阅卫星】来订阅卫星")
    try:
        if not Path.exists(CONFIG):
            data = {group: {qq: {}}}
            for sat in state["sat"]:
                temp = {
                    "仰角": state['ang'],
                    "qth": qth[qq],
                    "last_send": "",
                    "no_disturb": state["no_disturb"],
                }

                data[group][qq][sat] = temp
                data[group][qq]["nd_time_range"] = nd_time_range
            await yaml_dump(CONFIG, data)
        else:
            data = (await yaml_load(CONFIG))
            for sat in state["sat"]:
                if qq in qth:
                    if group in data:
                        if qq in data[group]:
                            data[group][qq][sat] = {"仰角": state['ang'], "qth": qth[qq], "last_send": "",
                                                    "no_disturb": state["no_disturb"]}
                        else:
                            data[group][qq] = {sat: {"仰角": state['ang'], "qth": qth[qq], "last_send": "",
                                                     "no_disturb": state["no_disturb"]}}
                    else:
                        data[group] = {qq: {sat: {"仰角": state['ang'], "qth": qth[qq], "last_send": "",
                                                  "no_disturb": state["no_disturb"]}}}
                    data[group][qq]["nd_time_range"] = nd_time_range
                    await yaml_dump(CONFIG, data)
        gird = await getGrid(float(qth[qq][0]), float(qth[qq][1]))
        await sub.send(f"订阅成功:\n"
                       f"卫星：{state['sat']}\n"
                       f"最低仰角：{state['ang']}\n"
                       f"QTH：{qth[qq]}({gird})\n"
                       f"夜间免打扰：{'是' if state['no_disturb'] else '否'}"
                       f"\n免打扰时间：{nd_time_send(nd_time_range)}")
    except Exception as e:
        logger.error(f"订阅失败：{e}")
        # do sth.


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
            messages = []
            for k, v in data[group][qq].items():
                if k == "nd_time_range":
                    continue
                reply = ""
                reply += k
                reply += f"\n最低仰角：{v['仰角']}"
                reply += f"\n免打扰：{'开' if v.get('no_disturb', False) else '关'}"
                nd_time_range = data[group][qq]["nd_time_range"]
                reply += f"\n免打扰时段：{nd_time_send(nd_time_range)}"
                messages.append(reply)
            await send_forward_msg(bot, event, "订阅卫星列表", messages)
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
    sat_list = [sat_list[i:i + 50] for i in range(0, len(sat_list), 50)]
    messages = []
    for sat in sat_list:
        reply = "\n".join(sat)
        messages.append(reply)
    await send_forward_msg(bot, event, "收录卫星列表", messages)


specified = on_command("查询卫星", aliases={"计算卫星"}, block=True)


@specified.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, args: Message = CommandArg()):
    qq = event.user_id
    input_arg = str(args).split(" ")
    sat_dict = (await data2Tle())
    sat = input_arg[0]
    sat_ = ""
    out = []
    if not sat:
        await specified.finish("请发送 计算卫星 卫星名称 分钟数（可选）\n例如：\n计算卫星 AO-73 10\n计算卫星 AO-73")
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

    # if sat in ["天宫", "天宫号", "中国空间站"] or sat.upper():
    if isChinese(sat):
        if sat in ['天宫', '天宫号', '中国空间站', '空间站', '天和', '核心舱']:
            sat_dict = (await get_tian_gong())
            sat = '天宫'
        elif sat == '国际空间站':
            pass
    elif sat.upper() in ['TIANGONG', 'CSS', 'TIANHE']:
        sat = '天宫'
        sat_dict = (await get_tian_gong())
    else:
        sat = sat.upper()
    reply = '{sat}不存在'
    if sat in sat_dict:
        if sat_dict[sat][1] == "<head>":
            await specified.finish("通过celestrak下载天宫数据时被禁止，这通常是过量访问导致的，可尝试删除 cqsat/tle_cache/css.cache "
                                   "文件，若不成功，可在两小时后再次删除此文件再试")
        out = await calculate(sat, qth, time=time)
        if out:
            reply = f"对于QTH:：{qth}\n{sat} 在 {send_time} ：\n仰角为：{round(float(out[1]), 2)}°\n方位角:{round(float(out[0]), 2)}°\n相对速率为：{round(float(out[2]), 2)} "
        else:
            reply = '哪里出错了 QWQ'
    await specified.send(reply)


async def aps():
    if not Path.exists(CONFIG):
        return
    elif (await read_all(CONFIG)) == "":
        return
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        data = (await yaml_load(CONFIG))
    except FileNotFoundError:
        # data = await data2Tle()
        # FIXME ?
        data = {100001: {4444444: {}}}
    for group in data:
        for qq in data[group]:
            if not USER_GLOBAL_NO_DISTURB.exists():
                temp = {qq: {"enable": False, "range": [20, 8]}}
                await yaml_dump(USER_GLOBAL_NO_DISTURB, temp)
            user_glb_no_disturb = (await yaml_load(USER_GLOBAL_NO_DISTURB))
            if qq in user_glb_no_disturb:
                usr_glb_no_disturb = user_glb_no_disturb[qq].get("enable", False)
                if usr_glb_no_disturb:
                    if if_no_disturb(user_glb_no_disturb[qq]["range"]):
                        logger.debug(f"{qq}: 全局免打扰模式开启，现在是免打扰时间，不发送数据")
                        continue
            for sat in data[group][qq]:
                if sat == "nd_time_range":
                    continue
                try:
                    last = parse(data[group][qq][sat]["last_send"])
                except ParserError:
                    last = parse("2001-11-04 00:00:00")
                except TypeError:
                    last = parse("2001-11-04 00:00:00")
                now_to_calculate = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
                min_add = 10
                if int((parse(now_to_calculate) - last).total_seconds() / 60) >= 30:
                    now = (datetime.utcnow() + timedelta(minutes=min_add)).strftime("%Y-%m-%d %H:%M:%S")
                    qth = (await yaml_load(QTH))[qq]
                    result = await calculate(sat, qth, now)
                    sated = []
                    if float(result[1]) > 0:
                        logger.debug(f"@{qq} 订阅的 {sat} 将入境，正准备计算最高仰角")
                        i = 0
                        az_list = []
                        alt_list = []
                        time_highest_point = {}
                        result_ = await calculate(sat, qth, now)
                        while float(result_[1]) >= 0:
                            now = (datetime.utcnow() + timedelta(minutes=min_add + int(i))).strftime(
                                "%Y-%m-%d %H:%M:%S")
                            result_ = await calculate(sat, qth, now)
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
                            no_disturb = data[group][qq][sat].get("no_disturb", True)
                            if no_disturb:
                                user_nd_time_range = data[group][qq][sat].get("nd_time_range", [20, 8])
                                if if_no_disturb(user_nd_time_range):
                                    continue
                            logger.debug("最高仰角大于用户设定的值，正准备提醒用户")
                            if sat not in sated:
                                logger.debug("成功预测到卫星。正在尝试发送数据")
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
                            logger.debug("最高仰角小于用户设定的值，不需要提醒")
                else:
                    logger.debug("半小时内该卫星已过境，跳过此卫星")
                    pass


scheduler = require("nonebot_plugin_apscheduler").scheduler

scheduler.add_job(aps, 'cron', minute="0/1", id="sat")

# 定时任务


set_nd_time_range = on_command("设置免打扰", block=True, aliases={"免打扰设置"})


@set_nd_time_range.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    qq = event.user_id
    group = event.group_id
    if CONFIG.exists():
        data = (await yaml_load(CONFIG))
        if group in data:
            if qq in data[group]:
                if args:
                    nd_time_range = str(args).split(" ")
                    try:
                        nd_time_range = [int(nd_time_range[0]), int(nd_time_range[1])]
                        if nd_time_range[0] < 0 or nd_time_range[1] > 24:
                            await set_nd_time_range.finish("输入有误，请输入0-24之间的数字")
                        else:
                            data[group][qq]["nd_time_range"] = nd_time_range
                            await yaml_dump(CONFIG, data)
                            reply = f"{nd_time_send(nd_time_range)}"
                            await set_nd_time_range.finish(
                                f"设置成功，免打扰时间为：{reply}")
                    except ValueError:
                        await set_nd_time_range.finish("输入有误，请输入0-24之间的数字")
                else:
                    data[group][qq]["no_disturb"] = not data[group][qq].get("no_disturb", True)
                    await yaml_dump(CONFIG, data)
                    await set_nd_time_range.finish(f"免打扰：{'开启' if data[group][qq]['no_disturb'] else '关闭'}\n\n"
                                                   f"若需要设置时间请发送【设置免打扰】+开始时间 结束时间\n例如：\n设置免打扰 20 8")
            else:
                data[group][qq]["no_disturb"] = not data[group][qq].get("no_disturb", True)
                await yaml_dump(CONFIG, data)
                await set_nd_time_range.finish(f"免打扰：{'开启' if data[group][qq]['no_disturb'] else '关闭'}\n\n"
                                               f"若需要设置时间请发送【设置免打扰】+开始时间 结束时间\n例如：\n设置免打扰 20 8")
                await set_nd_time_range.finish("Tips：你在本群没有订阅卫星")
        else:
            await set_nd_time_range.finish("本群没有用户订阅卫星\n订阅请发送【订阅卫星】")


def if_no_disturb(range_: list[int]) -> bool:
    """
    判断是否在免打扰时段
    :param range_: List[int] eg. [20, 8]
    :return: bool
    """
    now = datetime.now().hour
    if range_[0] > range_[1]:
        if now >= range_[0] or now <= range_[1]:
            logger.debug(f"{now}: 夜间免打扰模式开启，现在是免打扰时间，不发送数据")
            return True
    if range_[0] < range_[1]:
        if range_[0] <= now <= range_[1]:
            logger.debug(f"{now}: 夜间免打扰模式开启，现在是免打扰时间，不发送数据")
            return True
    if range_[0] == range_[1] == now:
        logger.debug(f"{now}: 夜间免打扰模式开启，现在是免打扰时间，不发送数据")
        return True
    return False


user_global_no_disturb = on_command("全局免打扰", block=True, aliases={"全局免打扰模式", "设置全局免打扰"})


@user_global_no_disturb.handle()
async def _(bot: Bot, matcher: Matcher, event: MessageEvent, state: T_State, args: Message = CommandArg()):
    qq = event.user_id
    if not USER_GLOBAL_NO_DISTURB.exists():
        temp = {qq: {"enable": False, "range": [20, 8]}}
        await yaml_dump(USER_GLOBAL_NO_DISTURB, temp)
    if not args:
        data = (await yaml_load(USER_GLOBAL_NO_DISTURB))

        if qq in data:
            data[qq]["enable"] = not data[qq]["enable"]
            await yaml_dump(USER_GLOBAL_NO_DISTURB, data)
            await matcher.finish(f"卫星订阅全局免打扰：{'开启' if data[qq]['enable'] else '关闭'}")
        else:
            data[qq] = {"enable": True, "range": [20, 8]}
            await yaml_dump(USER_GLOBAL_NO_DISTURB, data)
            await matcher.finish(
                f"首次设置：\n卫星订阅全局免打扰：{'开启' if data[qq]['enable'] else '关闭'}\n默认免打扰时间：20:00-8:00")

    else:
        if USER_GLOBAL_NO_DISTURB.exists():
            data = (await yaml_load(USER_GLOBAL_NO_DISTURB))
            if "enable" not in data[qq]:
                data[qq]["enable"] = not data[qq].get("enable", True)
                await yaml_dump(USER_GLOBAL_NO_DISTURB, data)
                await matcher.send(f"卫星订阅全局免打扰：{'开启' if data[qq]['enable'] else '关闭'}")
            await nd_args_range(matcher, event, args)


async def nd_args_range(matcher: Matcher, event: MessageEvent, args):
    """
    处理全局免打扰的时间参数并写入文件
    :param matcher: Matcher
    :param event: MessageEvent
    :param args: 输入参数
    :return:
    """
    qq = event.user_id
    data = (await yaml_load(USER_GLOBAL_NO_DISTURB))
    if qq in data:
        if args:
            nd_time_range = str(args).split(" ")
            try:
                nd_time_range = [int(nd_time_range[0]), int(nd_time_range[1])]
                if nd_time_range[0] < 0 or nd_time_range[1] > 24:
                    await matcher.finish("输入有误，请输入0-24之间的数字")
                else:
                    data[qq]["range"] = nd_time_range
                    await yaml_dump(USER_GLOBAL_NO_DISTURB, data)
                    reply = f"{nd_time_send(nd_time_range)}"
                    await matcher.finish(
                        f"设置成功，全局免打扰时间为：{reply}")
            except ValueError:
                await matcher.finish("输入有误，请输入0-24之间的数字")
        else:
            await matcher.finish("请发送【全局免打扰】+开始时间 结束时间\n例如：\n全局免打扰 20 8")
    else:
        data[qq]["range"] = {"enable": True, "range": [20, 8]}
        await yaml_dump(USER_GLOBAL_NO_DISTURB, data)
        await matcher.finish(
            f"首次设置：\n卫星订阅全局免打扰：{'开启' if data[qq]['enable'] else '关闭'}\n默认免打扰时间：20:00-8:00")


def nd_time_send(nd_time_range):
    if nd_time_range[0] == nd_time_range[1]:
        send = str(nd_time_range[0]) + ":00"
    else:
        send = str(nd_time_range[0]) + ":00-" + str(nd_time_range[1]) + ":00"
    return send
