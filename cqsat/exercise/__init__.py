# python3
# -*- coding: utf-8 -*-
# @Time    : 2022/8/31 3:05
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : __init__.py.py
# @Software: PyCharm
import json
import random

from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent, Event, GroupMessageEvent, PrivateMessageEvent
from nonebot.internal.params import ArgStr, ArgPlainText
from nonebot.typing import T_State

from ..utils import *
from . import exam

RESOURCE = Path(__file__).parent.parent / "cqsat_resource"
BANK = RESOURCE / "bank"
IMG = BANK / 'imgs'
do_exercise = on_command("刷题", block=True)


@do_exercise.got("level", prompt="请你要练习哪个等级的题目？（A B C）")
async def _(
        event: Event,
        state: T_State,
        answer=None,
        level: str = ArgStr("level")):
    if isinstance(event, GroupMessageEvent):
        qq = event.user_id
        state["user_notice"] = MessageSegment.at(qq)
    elif isinstance(event, PrivateMessageEvent):
        qq = event.user_id
        state["user_notice"] = ""
    if not Path.exists(EXERCISE_TEMP):
        await yaml_dump(EXERCISE_TEMP, {})
    if level in ["取消", "算了"]:
        await do_exercise.finish("已取消操作...")
    elif level.upper() not in ["A", "B", "C"]:
        await do_exercise.reject("输入错误，请重新输入...")
    elif level.upper() in ["A", "B", "C"]:
        state['level'] = level.upper()
        state['qq'] = qq
    already_done = (await yaml_load(EXERCISE_TEMP))
    if qq in already_done:
        last = already_done[qq]['last']
        last_level = already_done[qq]['level']
        if level.upper() == last_level:
            await do_exercise.send(state["user_notice"] + f"你上次练习{last_level}到了{last}题,将继续练习")
        else:
            await do_exercise.send(state["user_notice"] +
                                   f"你上次练习的是{last_level},进度为 【{last}】 题，该进度已删除\n正开始{level.upper()}类题目的练习")
            last = 1
            temp = {qq: {"level": level, "last": 1}}
            await yaml_upload(EXERCISE_TEMP, temp)
    else:
        last = 1
        temp = {qq: {"level": level, "last": 1}}
        await yaml_upload(EXERCISE_TEMP, temp)
    state['last'] = last
    state["is_send"] = False


@do_exercise.got("answer", prompt="回复任意内容开始...")
async def _(state: T_State, reply: str = ArgPlainText("answer")):
    level = state["level"]
    qq = state["qq"]
    last = state['last']
    ex_bank = json.loads(await read_all(BANK / f"{level}.json"))
    if reply in ["取消", "算了", "退出", "不做了", "怎么退出"]:
        temp = {qq: {"level": level, "last": last}}
        await yaml_upload(EXERCISE_TEMP, temp)
        await do_exercise.finish("已取消操作...")
    if state["is_send"]:
        if reply.upper() in ["A", "B", "C", "D"]:
            for i in range(len(ex_bank) - last):
                if state["this_send"][reply.upper()] != state["this_answer"]:
                    await do_exercise.send("×")
                    state = (await send_ex(ex_bank, last, qq, level, state))
                elif state["this_send"][reply.upper()] == state["this_answer"]:
                    last += 1
                    state["last"] = last
                    await do_exercise.send("√")
                    state = (await send_ex(ex_bank, last, qq, level, state))
        else:
            await do_exercise.reject("输入错误，请重新输入...")
    elif not state["is_send"]:
        state["is_send"] = True
        state = (await send_ex(ex_bank, last, qq, level, state))


async def send_ex(ex_bank, last, qq, level, state):
    temp = {qq: {"level": level, "last": last}}
    await yaml_upload(EXERCISE_TEMP, temp)
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
    reply = (
        f"{last}、{dic_to_send['Q']}\n"
        f"A. {dic_to_send['A']}\n"
        f"B. {dic_to_send['B']}\n"
        f"C. {dic_to_send['C']}\n"
        f"D. {dic_to_send['D']}\n"
    )
    if state["pic_to_send"]:
        await do_exercise.send(MessageSegment.image(f"file:///{(IMG / state['pic_to_send']).absolute()}"))
        await do_exercise.reject(reply)
    else:
        await do_exercise.reject(reply)
    return state

# FIXME 出了点问题但是看不懂13天前写的代码了...
# @do_exercise.got("answer", prompt="回复任意内容开始...")
# async def _(matcher: Matcher, state: T_State, reply: str = ArgPlainText("answer")):
#     level = state["level"]
#     qq = state["qq"]
#     last = state['last']
#     ex_bank = json.loads(await read_all(BANK / f"{level}.json"))
#     if reply in ["取消", "算了", "退出", "不做了", "怎么退出"]:
#         temp = {qq: {"level": level, "last": last}}
#         await yaml_upload(EXERCISE_TEMP, temp)
#         await do_exercise.finish("已取消操作...")
#     if state["is_send"]:
#         if reply.upper() in ["A", "B", "C", "D"]:
#             for i in range(len(ex_bank) - last):
#                 # if state["this_send"][reply.upper()] != state["this_answer"]:
#                 if reply.upper() != state["this_answer"]:
#                     await do_exercise.send("×")
#                     state = (
#                         await send_ex(
#                             matcher,
#                             ex_bank,
#                             last,
#                             qq,
#                             level,
#                             state,
#                             img=IMG,
#                             mode="exec"
#                         )
#                     )
#                 elif reply.upper() == state["this_answer"]:
#                     last += 1
#                     state["last"] = last
#                     await do_exercise.send("√")
#                     state = (
#                         await send_ex(
#                             matcher,
#                             ex_bank,
#                             last,
#                             qq,
#                             level,
#                             state,
#                             img=IMG,
#                             mode="exec"
#                         )
#                     )
#         else:
#             await do_exercise.reject(state["user_notice"] + "输入错误，请重新输入...")
#     elif not state["is_send"]:
#         state["is_send"] = True
#         state = (
#             await send_ex(
#                 matcher,
#                 ex_bank,
#                 last,
#                 qq,
#                 level,
#                 state,
#                 img=IMG,
#                 mode="exec"
#             )
#         )
