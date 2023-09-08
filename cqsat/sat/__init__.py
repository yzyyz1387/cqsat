# python3
# -*- coding: utf-8 -*-
# @Time    : 2022/8/24 0:21
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : __init__.py.py
# @Software: PyCharm
from . import calculate_sat, sat_handle
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="HAM助手",
    description="业余无线电相关工具",
    usage="可刷题、模拟考试，追踪卫星等",
    type="application",
    homepage="https://github.com/yzyyz1387/nonebot_plugin_cqsat",
    supported_adapters=None,
)
