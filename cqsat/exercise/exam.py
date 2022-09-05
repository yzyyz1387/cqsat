# python3
# -*- coding: utf-8 -*-
# @Time    : 2022/9/5 3:42
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : exam.py
# @Software: PyCharm
import datetime
import json
import random

from nonebot import on_command, require, Bot
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent, Message, GroupMessageEvent, PrivateMessageEvent, \
    Event
from nonebot.internal.params import ArgStr, ArgPlainText
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.typing import T_State

from ..path import *
from ..utils import *

RESOURCE = Path(__file__).parent.parent / "cqsat_resource"
BANK = RESOURCE / "bank"
IMG = BANK / 'imgs'
do_exam = on_command("ham考试", aliases={"Ham考试", "HAM考试", "H考试", "h考试"}, block=True)


@do_exam.got("level", prompt="请你要进行哪个等级的考试？（A B C）")
async def _(
        matcher: Matcher,
        event: Event,
        state: T_State,
        answer=None,
        level: str = ArgStr("level")):
    global USER_PATH
    if isinstance(event, GroupMessageEvent):
        qq = event.user_id
        state["user_notice"] = MessageSegment.at(qq)
    elif isinstance(event, PrivateMessageEvent):
        qq = event.user_id
        state["user_notice"] = ""
    if level in ["取消", "算了", "不考了", "退出考试", "退出"]:
        await do_exam.finish("已取消操作...")
    elif level.upper() not in ["A", "B", "C"]:
        await do_exam.reject("输入错误，请重新输入...")
    elif level.upper() in ["A", "B", "C"]:
        USER_PATH = EXAM_CACHE / level.upper() / f"{qq}.yml"
        if not Path.exists(USER_PATH):
            await yaml_dump(USER_PATH, {"done": 0, "best": 0, "wrong": {}, "Accuracy": []})
        state['level'] = level.upper()
        state['qq'] = qq
    user_history = (await yaml_load(USER_PATH))
    already_done = user_history["done"]
    if already_done != 0:
        best = user_history["best"]
        wrong = user_history["wrong"]
        wrong_to_send = ""
        if wrong:
            for i in wrong:
                wrong_to_send += f"{i}: {wrong[i]}次\n"
        else:
            wrong_to_send = "无"
        await do_exam.send(state["user_notice"] + f"你在此前已经完成过{already_done}次考试，最高分为{best}分，错题情况如下：\n{wrong_to_send}")

    state['last'] = 0
    state["correct"] = 0
    state["wrong"] = {}
    state["ex_list"] = None
    state["time_is_up"] = None
    state["is_send"] = False


@do_exam.got("answer", prompt="回复任意内容开始...")
async def _(matcher: Matcher, state: T_State, reply: str = ArgPlainText("answer")):
    global ex_list
    scheduler = require("nonebot_plugin_apscheduler").scheduler
    level = state["level"]
    qq = state["qq"]
    USER_PATH = EXAM_CACHE / level.upper() / f"{qq}.yml"
    last = state['last']
    exam_config_dict = {
        "A": [30, 30, 25],
        "B": [50, 60, 40],
        "C": [80, 90, 60]
    }
    this_config = exam_config_dict[level]
    state["this_config"] = this_config
    if not state["time_is_up"]:
        time_up = datetime.datetime.now() + datetime.timedelta(minutes=this_config[1])
        await do_exam.send(f"考试于{time_up.strftime('%H:%M:%S')}结束")
        state["time_is_up"] = time_up
        scheduler.add_job(
            finish_matcher_cause_time,
            "date",
            run_date=time_up,
            args=[matcher],
            id=f"{qq}_exam"
        )

    ex_bank = json.loads(await read_all(BANK / f"{level}.json"))
    if not state["ex_list"]:
        ex_list = random.sample(range(1, len(ex_bank)), this_config[0])
        state["ex_list"] = ex_list
    else:
        pass
    if last == 0:
        last = ex_list[0]
        state['last'] = last
    if reply in ["取消", "算了", "退出", "不做了", "怎么退出"]:
        scheduler.remove_job(f"{qq}_exam")
        await do_exam.finish("已取消操作...")
    if reply in ["时间", "还有多久结束", "还剩多久结束", "查看时间"]:
        time_is_up = state["time_is_up"]
        time_left = time_is_up - datetime.datetime.now()
        time_left = time_left.seconds // 60
        await do_exam.send(state["user_notice"] + f"距离考试结束还有{time_left}分钟")

    if state["is_send"]:
        if reply.upper() in ["A", "B", "C", "D"]:
            if ex_list.index(int(last)) < len(ex_list) - 1:
                for i in range(this_config[0]):
                    # if state["this_send"][reply.upper()] != state["this_answer"]:
                    if reply.upper() != state["this_answer"]:
                        await do_exam.send(f"× 应为 {state['this_answer']}"+ "\n"+ state["user_notice"])
                        last_ = last
                        last = ex_list[ex_list.index(last) + 1]
                        state["last"] = last
                        wrong = state["wrong"]
                        wrong[last_] = 0
                        wrong[last_] += 1
                        state["wrong"] = wrong
                        state = (
                            await send_ex(
                                matcher,
                                ex_bank,
                                last,
                                qq,
                                level,
                                state,
                                img=IMG,
                                mode="exam"
                            )
                        )
                    elif reply.upper() == state["this_answer"]:
                        last = ex_list[ex_list.index(last) + 1]
                        state["last"] = last
                        await do_exam.send("√")
                        state["correct"] += 1
                        state = (
                            await send_ex(
                                matcher,
                                ex_bank,
                                last,
                                qq,
                                level,
                                state,
                                img=IMG,
                                mode="exam"
                            )
                        )
            else:
                if reply.upper() == state["this_answer"]:
                    await do_exam.send("√")
                    state["correct"] += 1
                elif reply.upper() != state["this_answer"]:
                    await do_exam.send(f"× 应为 {state['this_answer']}")
                    wrong = state["wrong"]
                    wrong[last] = 0
                    wrong[last] += 1
                    state["wrong"] = wrong

                user_history = await yaml_load(USER_PATH)
                user_history["done"] += 1
                user_history["best"] = max(user_history["best"], state["correct"])
                for i in user_history["wrong"]:
                    if i in state["wrong"]:
                        user_history["wrong"][i] += state["wrong"][i]
                        state["wrong"].pop(i)
                user_history["wrong"].update(state["wrong"])
                logger.info(user_history)
                user_history["Accuracy"].append(state["correct"] / this_config[0])
                await yaml_dump(USER_PATH, user_history)
                await do_exam.send(state["user_notice"] + "已完成本次考试")
                await do_exam.send(state["user_notice"] + "\n" +
                                   f"本次考试共【{this_config[0]}】题\n"
                                   f"正确【{state['correct']}】题\n"
                                   f"错误【{len(state['wrong'])}】题\n"
                                   f"{'-' * 10}\n"
                                   f"{'祝贺你考试通过！' if state['correct'] >= this_config[2] else '很遗憾本次考试未通过...再接再厉！'}\n"
                                   f"{'-' * 10}\n"
                                   f"正确率为【{round(state['correct'] / this_config[0] * 100, 2)}%】\n"
                                   f"你 {level.upper()} 类题目的平均正确率为【{round(sum(user_history['Accuracy']) / len(user_history['Accuracy']), 2) * 100}%】 "
                                   )
                cache_path = EXAM_CACHE / state["level"].upper() / f"{state['qq']}_state.txt"
                if cache_path.exists():
                    cache_path.unlink()
                else:
                    logger.warning(f"cache文件不存在，无法删除")

        else:
            await do_exam.reject("输入错误，请重新输入上方题目的答案...")
    elif not state["is_send"]:
        state["is_send"] = True
        state = (
            await send_ex(
                matcher,
                ex_bank,
                last,
                qq,
                level,
                state,
                img=IMG,
                mode="exam"
            )
        )


async def finish_matcher_cause_time(matcher: Matcher):
    """
    停止考试
    :param matcher: Matcher
    :return:
    """
    cache_path = EXAM_CACHE / matcher.state["level"].upper() / f"{matcher.state['qq']}_state.txt"
    state = (await read_all(cache_path))
    state = json.loads(state)
    await matcher.send("时间到，考试结束！")
    if state["correct"] + len(state["wrong"]) != state['this_config'][0]:
        await matcher.send(f"你还有【{state['this_config'][0] - state['correct'] - len(state['wrong'])}】题未做")

    await matcher.send(
        f"本次考试共【{state['this_config'][0]}】题\n"
        f"正确【{state['correct']}】题\n"
        f"错误【{len(state['wrong'])}】题\n"
        f"{'-' * 10}\n"
        f"{'祝贺你考试通过！' if state['correct'] >= state['this_config'][2] else '很遗憾本次考试未通过...再接再厉！'}\n"
        f"{'-' * 10}\n"
    )
#      删除cache
    if cache_path.exists():
        cache_path.unlink()
    else:
        logger.warning(f"cache文件不存在，无法删除")


my_wrong = on_command("我的错题", aliases={"我的错题本"}, priority=5, block=True)


@my_wrong.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    u_path = f"{event.user_id}.yml"
    wrong_a = (await yaml_load(EXAM_CACHE_A / u_path))["wrong"] if (EXAM_CACHE_A / u_path).exists() else {}
    wrong_b = (await yaml_load(EXAM_CACHE_B / u_path))["wrong"] if (EXAM_CACHE_B / u_path).exists() else {}
    wrong_c = (await yaml_load(EXAM_CACHE_C / u_path))["wrong"] if (EXAM_CACHE_C / u_path).exists() else {}
    r_a = ""
    if wrong_a:
        for i in wrong_a:
            r_a += f"{i}: {wrong_a[i]}次\n"
    r_b = ""
    if wrong_b:
        for i in wrong_b:
            r_b += f"{i}: {wrong_b[i]}次\n"
    r_c = ""
    if wrong_c:
        for i in wrong_c:
            r_c += f"{i}: {wrong_c[i]}次\n"
    await my_wrong.send(
        f"你的错题有【{len(wrong_a) + len(wrong_b) + len(wrong_c)}】道题目\n"
        f"{'-' * 10}\n"
        f"A类：{r_a if r_a else 0}\n"
        f"{'-' * 10}\n"
        f"B类：{r_b if r_b else 0}\n"
        f"{'-' * 10}\n"
        f"C类：{r_c if r_c else 0}\n"
                        )


refer_question = on_command("查题", aliases={"查询题目"}, priority=5, block=True)

@refer_question.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, args:Message=CommandArg()):
    if not args:
        await refer_question.finish("请发送【查题 级别 题号】\n例如：\n  查题 A 1\n级别和题号之间用空格分割")
    else:
        a_list = str(args).split(" ")
        if len(a_list) != 2:
            await refer_question.finish("请发送【查题 级别 题号】\n例如：\n  查题 A 1\n级别和题号之间用空格分割")
        else:
            for i in a_list:
                if i.isdigit():
                    num = i
                    a_list.pop(a_list.index(i))
                    level = a_list[0].upper()
                else:
                    await refer_question.finish("请发送【查题 级别 题号】\n例如：\n  查题 A 1\n级别和题号之间用空格分割")
            if level not in ["A", "B", "C"]:
                await refer_question.finish("级别错误，应该为A、B、C其中一个")
            else:
                ex_bank = json.loads(await read_all(BANK / f"{level}.json"))
                if int(num) > len(ex_bank):
                    await refer_question.finish("题号错误，题库中没有这么多题目")
                else:
                    if ex_bank[num]["P"]:
                        await refer_question.send(MessageSegment.image(f"file:///{(IMG / ex_bank[num]['P']).absolute()}"))
                    await refer_question.send(f"{level} 类第 {num}题:\n{ex_bank[num]['Q']}\n：A、{ex_bank[num]['A']}\nB、{ex_bank[num]['B']}\nC、{ex_bank[num]['C']}\nD、{ex_bank[num]['D']}\n答案: 【A】")