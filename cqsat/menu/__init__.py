# python3
# -*- coding: utf-8 -*-
# @Time    : 2023-10-04 2:38
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : __init__.py.py
# @Software: PyCharm
from pathlib import Path

import markdown
import nonebot
from dateutil.parser import ParserError
from dateutil.parser import parse
from nonebot import on_command, require
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, MessageEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed

from ..path import MENU_PATH
from ..utils import shoot_scr

# FIXME
menu_md = ["""
### 查看相关网页截图
- 发送`/s` 即可查看相关网站的截图 例如 `/s t a`
  - t https://www.df2et.de/tevel/ 
  - a https://amsat.org/status/index.php
  - ...

### 计算卫星过境交集
- 此功能可以预测两个网格之间的卫星过境通联交集
- 发送`/约  卫星1,卫星2 网格1 网格2` 即可查看卫星过境交集 例如 `/计算 so-50,iss OM44 OM48`
 
### 娱乐信令
- 发送`/v` ，根据提示回复一条语音，即可对该语音加上信令音
- 可选参数
  - `-p` 加前置音 例如：`/v -p`
  - `-n[数字]` 加噪音 例如：`/v -n5`
  - 使用示例: `/v -n5 -p` 
  
### 针对卫星夜间免打扰：
- 发送 `订阅卫星` 重新订阅一遍，在订阅的时候设置，**此版本前订阅的将默认开启**，默认时间为20:00--08:00
- 设置订阅时间：发送 `设置免打扰 时间起  时间止` 例如：`设置免打扰 20 8`
- 开启/关闭 本群免打扰：发送 `设置免打扰`

### 全局免打扰：
- 设置全局免打扰时间： `全局免打扰 时间 时间`，例：`全局免打扰 20 8`
- 开启/关闭全局免打扰： `全局免打扰

### 网格 【私聊、群内】
- 发送 `我的网格` 查询用户绑定qth的网格
- 发送 `计算网格 +地名` 计算指定地址的网格，如 `计算网格 北京`
- 发送 `计算网格+经度+  +纬度` 计算指定位置的网格 经纬度用空格分隔
  - 不加经纬度相当于 `我的网格` 指令
  
  
""",
           """
### 考题
#### 刷题 【私聊、群内】
- 发送 `刷题` 开始顺序刷题
- 发送 `取消` 、 `退出` 取消当前刷题

#### 考试
- 发送`HAM考试` 、`h考试` 开始考试
- 考试过程中发送 `时间` 可查看考试剩余时间
- 考试过程中发送 `退出` 可退出考试
- 做完题目自动交卷
- 规定时间内未做完题目自动交卷
- 交卷后可查看考试结果及分析
- 发送 `我的错题` 可查看错题
- 发送 `查题 + 级别 + 题号` 可查看指定题目
  - 例如 `查题 A 1` 查看A类考试第一题
           """]


def md2html(md_list: list):
    from markdown.extensions.toc import TocExtension
    html_list = []
    for md in md_list:
        html = markdown.markdown(md, extensions=[TocExtension(baselevel=2)])
        html_list.append(html)
    return html_list


def save_html(html, file_name):
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(html)


call_menu = on_command("/cq", aliases={"/Cq", "/CQ"}, priority=1)


@call_menu.handle()
async def _(bot: Bot, event: MessageEvent):
    html_list = md2html(menu_md)
    for html in html_list:
        save_html(html, MENU_PATH / "menu.html")
        path = Path(MENU_PATH / 'menu.html').resolve()
        await shoot_scr("file:///" + str(path).replace("\\", "/"), img_output= MENU_PATH / "menu.png")
        with open(MENU_PATH / "menu.png", "rb") as f:
            img = f.read()
        await bot.send(event, message=MessageSegment.image(img))
