# python3
# -*- coding: utf-8 -*-
# @Time    : 2023-09-24 23:44
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : config.py
# @Software: PyCharm
from typing import Optional

from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    nonebot_plugin_go_cqhttp: Optional[bool] = False
    go_cqhttp_path: Optional[str] = './'
    sat_proxy_url: Optional[str] = None


global_config = get_driver().config
plugin_config = Config.parse_obj(get_driver().config.dict())
