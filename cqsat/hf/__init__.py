# python3
# -*- coding: utf-8 -*-
# @Time    : 2023-10-04 10:22
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : __init__.py.py
# @Software: PyCharm

from jinja2 import Environment, FileSystemLoader
from nonebot import on_command, require
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, MessageEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.internal.params import ArgStr
from nonebot.params import CommandArg
from nonebot.typing import T_State
import xml.etree.ElementTree as ET

from ..log import log
from ..path import *
from ..config import *
from ..utils import *

hf_url = "https://www.hamqsl.com/solarxml.php"


def parse_xml(xml):
    root = ET.fromstring(xml)
    calculated_conditions = root.find('solardata/calculatedconditions')
    data_dict = {}
    index = 0
    for i in calculated_conditions:
        data_dict.update({i.attrib['name']: {}}) if data_dict.get(i.attrib['name']) is None else None
        data_dict[i.attrib['name']].update({i.attrib['time']: i.text})
        index += 1
    for i in data_dict:
        condition_dict = {"Good": "好", "Fair": "良", "Poor": "差"}
        data_dict[i]['day'] = condition_dict[data_dict[i]['day']]
        data_dict[i]['night'] = condition_dict[data_dict[i]['night']]
    return data_dict


def render_(data_dict):
    env = Environment(loader=FileSystemLoader(Path(__file__).parent))
    template = env.get_template('index.html')
    html = template.render(data=data_dict)
    with open('hf.html', 'w', encoding='utf-8') as f:
        f.write(html)
        f.close()
    return Path('hf.html').resolve()


get_hf_xml = on_command("/hf", aliases={"/HF"}, block=True)


@get_hf_xml.handle()
async def get_hf_xml_(bot: Bot, event: MessageEvent, state: T_State, args: Message = CommandArg()):
    if not args:
        xml = await http_get(hf_url)
        data_dict = parse_xml(xml)
        path = render_(data_dict)
        out = SHOOTS_OUT_PATH / "hf.png"
        await shoot_scr(
            url="file:///" + str(path).replace("\\", "/"),
            locator='table',
            img_output=out,
        )
        await get_hf_xml.finish(MessageSegment.image(f"file:///{Path(out).resolve()}"))
