# python3
# -*- coding: utf-8 -*-
# @Time    : 2022/8/21 2:09
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : __init__.py.py
# @Software: PyCharm
from . import (
    exercise,
    entertainment,
    mgsl,
    sat,
    config,
    hf,
    log,
    path,
    utils,
    media_utils
               )
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="HAM助手",
    description="业余无线电相关工具",
    usage="可刷题、模拟考试，追踪卫星等",
    type="application",
    homepage="https://github.com/yzyyz1387/cqsat",
    supported_adapters=None,
)
