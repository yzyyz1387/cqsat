# python3
# -*- coding: utf-8 -*-
# @Time    : 2023-09-29 16:19
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : shoot_handle.py
# @Software: PyCharm
import re
from datetime import datetime, timedelta

import httpx
from nonebot import on_command, require
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, MessageEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.internal.params import ArgStr
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State

from ..mgsl import getGrid
from .calculate_sat import download_ham_sat, data2Tle, calculate, get_tian_gong
from .sat_shoot_url_bank import *
from ..log import log
from ..path import *
from ..config import *
from ..utils import *

if plugin_config.sat_proxy_url:
    logger.info(plugin_config.sat_proxy_url)

shoot_web = on_command("/s", aliases={"/S"}, block=True)

url_bank = UrlBank()


@shoot_web.handle()
async def query_tevel_(bot: Bot, event: MessageEvent, state: T_State, args: Message = CommandArg()):
    not_found = True
    Iter_msgs = []
    for item in (url_bank.get()):
        tips = ""
        for k, v in item.items():
            if k in ['url', 'cmd']:
                tips += f"{k}:{v}\n"
        Iter_msgs.append(tips)
    if args:
        args = str(args).strip().split(" ")
        for item in (url_bank.get()):
            for arg in args:
                if arg in item["cmd"]:
                    not_found = False
                    url = item["url"]
                    path = SHOOTS_OUT_PATH / item["path"]
                    locator = item.get("locator", "html")
                    time_out = item.get("time_out", 0)
                    proxy = item.get("proxy", None)
                    timeout = item.get("timeout", 30000)
                    until = item.get("until", "load")
                    if path.exists():
                        last_time = datetime.fromtimestamp(path.stat().st_mtime)
                        TIME_NOW = (datetime.now())
                        TIME_DIFF = TIME_NOW - last_time
                        if TIME_DIFF > timedelta(minutes=float(time_out)):
                            logger.info("超时，重新截图")
                            await shoot_scr(url,
                                            locator=locator,
                                            img_output=path,
                                            proxy=proxy,
                                            timeout=timeout,
                                            until=until)
                    else:
                        await shoot_scr(url,
                                        locator=locator,
                                        img_output=path,
                                        proxy=proxy,
                                        timeout=timeout,
                                        until=until)
                    try:
                        await shoot_web.send(MessageSegment.image(f"file:///{Path(path).resolve()}"))
                    except Exception as e:
                        await shoot_web.finish(f"图片发送失败，哪里出错了？\n{e}")

    if not args or not_found:
        await shoot_web.send(f"请输入参数：\n例如：/s t a css\n支持的参数：")
        await send_forward_msg(bot, event, "收录截图列表", Iter_msgs)


bank_handle = on_command("/截图", aliases={"/shoot"}, block=True, permission=SUPERUSER)


@bank_handle.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, args: Message = CommandArg()):
    if args:

        # args: add url=xxx cmd=xxx path=xxx locator=xxx
        # 检查是否有中文、中文符号
        if re.findall(r'[\u4e00-\u9fa5，。？！：；“”‘’（）【】、]', str(args)):
            await bank_handle.finish(
                "参数错误：不得包含中文字符\n/截图add url=xxx cmd=xxx path=xxx locator=xxx time_out=123 ...")
        args = str(args).strip().split(" ")
        keyword_ = {}
        if args[0] == "add":
            for arg in args:
                if "=" in arg:
                    arg = arg.split("=")
                    keyword_[arg[0]] = (arg[1]).replace(" ", "").replace("&#93;", "]").replace("&#91;", "[").replace(
                        "&#61;", "=")
            if keyword_:
                if not keyword_.get("url", None) or not keyword_.get("cmd", None) or not keyword_.get("path", None):
                    await bank_handle.finish("参数错误：\n/截图add url=xxx cmd=xxx path=xxx locator=xxx time_out=123 "
                                             "...\n必须包含url、cmd、path")
                keyword_["cmd"]=keyword_["cmd"].split(",")
                url_bank.add(**keyword_)
                await bank_handle.finish("添加成功")
            else:
                await bank_handle.finish("参数错误：\n/截图add url=xxx cmd=xxx path=xxx locator=xxx time_out=123 "
                                         "...\n必须包含url、cmd、path")
        elif args[0] == "del":
            for arg in args:
                if "=" in arg:
                    arg = arg.split("=")
                    keyword_[arg[0]] = arg[1].replace(" ", "").replace("&#93;", "]").replace("&#91;", "[").replace(
                        "&#61;", "=")
            if keyword_:
                if url_bank.remove(**keyword_):
                    await bank_handle.finish("删除成功")
                else:
                    await bank_handle.finish(f"没有找到{keyword_}")
            else:
                await bank_handle.finish("参数错误：\n/截图del url=xxx cmd=xxx path=xxx"
                                         "...\n必须包含url、cmd、path其中之一")
        elif args[0] == "get":
            data = url_bank.get()
            messages = []
            for i in data:
                reply = ""
                for k, v in i.items():
                    if k in ['cmd', 'url', 'path']:
                        reply += f"{k}:{v}\n"
                messages.append(reply)

            await send_forward_msg(bot, event, "收录截图列表", messages)
        elif args[0] == "default":
            url_bank.default()
            await bank_handle.finish("恢复默认成功")


sat_match = on_command("/约", aliases={"/satmatch", "/匹配"}, block=True)


@sat_match.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, args: Message = CommandArg()):
    qq = event.user_id
    qth = await getQth(qq)
    sat, obs1, obs2, this_png = None, None, None, None
    if not args:
        await sat_match.finish("请输入参数：\n/约 卫星,卫星 网格1 网格2\n例如：/约 iss,so-50 OM44 OM48")
    else:
        args = str(args).strip().split(" ")
        if len(args) == 2:
            if qth is None:
                await sat_match.finish(
                    "你可能只输入了一个网格，此时我会根据你的网格和你输入的网格进行匹配\n但看起来你还没有设置QTH,可以发送【绑定位置】来绑定QH")
            if isChinese(args[1]):
                location = await getLlByAd(args[1])
                if location:
                    qth_input = [location[0], location[1], 0]
                    gird = await getGrid(float(qth_input[0]), float(qth_input[1]))
                    args[1] = gird
                else:
                    await sat_match.finish(f"未查询到{args[1]}的经纬度, 请检查一下吧~")
            sat = args[0].upper()
            obs1 = await getGrid(float(qth[0]), float(qth[1]))
            obs2 = args[1].upper()
            this_png = await sat_match_scr(sat, obs1, obs2)

        elif len(args) >= 3:

            for arg in args[1:]:
                if isChinese(arg):
                    location = await getLlByAd(arg)
                    if location:
                        qth = [location[0], location[1], 0]
                        gird = await getGrid(float(qth[0]), float(qth[1]))
                        args[args.index(arg)] = gird
                    else:
                        await sat_match.finish(f"未查询到{arg}的经纬度, 请检查一下吧~")
            sat = args[0].upper()
            obs1 = args[1].upper()
            obs2 = args[2].upper()
            this_png = await sat_match_scr(sat, obs1, obs2)
        else:
            await sat_match.finish("参数错误：\n/约 卫星,卫星 网格1 网格2\n若只输入了一个网格，会根据绑定的位置和输入的网格进行匹配\n例如：/约 iss,so-50 OM44 OM48")
        try:
            await sat_match.send(f"{obs1} 和 {obs2} 通过 {sat}的通联可能性预测\n" + MessageSegment.image(
                f"file:///{Path(this_png).resolve()}"))
            this_png.unlink()
        except ActionFailed:
            await sat_match.finish("图片发送失败，哪里出错了？")


async def sat_match_scr(sat, obs1, obs2):
    url = f"https://www.satmatch.com/satellite/{sat}/obs1/{obs1}/obs2/{obs2}"
    async with httpx.AsyncClient() as client:
        r = (await client.get(url))
        if r.status_code != 200:
            await sat_match.finish(
                f"有什么出错了~\nerr{r.status_code}\n请检查卫星名/网格的输入吧~\n/约 卫星,卫星 网格1 网格2\n"
                f"若只输入了一个网格，会根据绑定的位置和输入的网格进行匹配\n例如：/约 "
                f"iss,so-50 OM44 OM48")
    logger.info(url)
    this_png = SHOOTS_OUT_PATH / f"satmatch{datetime.now()}.png"
    await shoot_scr(url,
                    img_output=this_png,
                    timeout=0,
                    locator="html",
                    until="networkidle")
    return this_png
