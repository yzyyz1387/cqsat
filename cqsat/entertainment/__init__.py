# python3
# -*- coding: utf-8 -*-
# @Time    : 2023-09-24 21:36
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : __init__.py
# @Software: PyCharm
import random

from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent, Event, GroupMessageEvent, PrivateMessageEvent, \
    Bot, Message
from nonebot.internal.params import ArgStr, ArgPlainText
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State

from ..media_utils import convert_to_silk_wav, MergeTwoMp3
from ..config import *
from ..utils import *
from ..path import *

RESOURCE = Path(__file__).parent.parent / "cqsat_resource"
VOICES = RESOURCE / "voices"

voice_synthesis = on_command("/v", block=True, aliases={"/合成", "/vt"})


@voice_synthesis.handle()
async def _(event: Event, state: T_State, args: Message = CommandArg()):
    if args and "-p" in str(args).strip():
        state["prefix"] = True
    if "-n" in str(args):
        try:
            msg = MsgText(event.json()).replace(' ', '').replace('禁', '')
            noise = int(''.join(map(str, list(map(lambda x: int(x), filter(lambda x: x.isdigit(), msg))))))
        except:
            noise = 0
        state["noise"] = noise


# @itsevin
# from https://github.com/itsevin/nonebot_plugin_record/blob/main/nonebot_plugin_record/__init__.py
@voice_synthesis.got("recording", prompt="请发送语音\n发送【取消】取消操作")
async def _(bot: Bot, event: MessageEvent, state: T_State):
    mdc_list = [item for item in (VOICES / 'suffix').iterdir() if item.is_file()]
    prefixes_path = (VOICES / 'prefix' / 'unknown_pre.mp3').absolute() if state.get("prefix", False) else None
    if event.get_message()[0].type == "record":
        if plugin_config.nonebot_plugin_go_cqhttp is True:
            path_amr = "./accounts/" + bot.self_id + "/data/voices/" + event.get_message()[0].data["file"]
        else:
            path_amr = plugin_config.go_cqhttp_path + "data/voices/" + event.get_message()[0].data["file"]

        out_this_path = MDC_GENERATOR_PATH / path_amr.split("/")[-1].replace(".amr", "")
        wav_file = await convert_to_silk_wav(path_amr, out_this_path)
        output_voice_path = await MergeTwoMp3(
            voice=Path(wav_file),
            mdc=(random.choice(mdc_list)).absolute(),
            prefix=prefixes_path,
            snr=state.get("noise", 0))
        await voice_synthesis.finish(MessageSegment.record(f"file:///{output_voice_path}"))
    else:
        await voice_synthesis.finish("请回复语音，操作已退出...")
