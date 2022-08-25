# python3
# -*- coding: utf-8 -*-
# @Time    : 2022/8/21 2:28
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : calculate_sat.py
# @Software: PyCharm
import json
import re
from typing import Dict

from typing import Optional

from ..log import log
from ..utils import *
from ..path import *
import ephem

logger = log()


async def get_tian_gong():
    Path.mkdir(LOCAL) if not Path.exists(LOCAL) else ...
    logger.debug("读取在线数据...")
    tian_gong_ = await http_get('http://www.cmse.gov.cn/gfgg/zgkjzgdcs/')
    selected = re.findall(re.compile(r'<div><font face="Courier New">(.*?)</font></div>'), tian_gong_)
    line1 = selected[0].replace('&nbsp;', ' ')
    line2 = selected[1].replace('&nbsp;', ' ')
    tg_data = {"天宫": [line1, line2]}
    logger.debug("写入本地数据...")
    await write_(TIANGONG, json.dumps(str(tg_data)))
    return tg_data


async def download_ham_sat():
    Path.mkdir(LOCAL) if not Path.exists(LOCAL) else ...
    await get_tian_gong()
    logger.debug("读取在线数据...")
    url = "https://amsat.org/tle/current/nasabare.txt"
    ham_sat_ = await http_get(url)
    if not ham_sat_:
        logger.error(f"从 {url} 下载数据出错")
        return None
    else:
        logger.debug("写入本地数据...")
        await write_(HAM_SAT, str(ham_sat_))
        return ham_sat_


async def data2Tle() -> Dict[str, list]:
    # if not Path.exists(HAM_SAT):
    # FIXME 每次都下载数据，计划进行缓存，根据上次下载的时间来判断是否需要下载数据
    await download_ham_sat()
    content = (await read_all(HAM_SAT))
    logger.info("载入数据...")
    count = 0
    data = {}
    temp = []
    # 将数据分割成行TLE轨道报
    for line in content.split('\n'):
        count += 1
        temp.append(line)
        if count % 3 == 0:
            data[temp[0]] = temp[1:]
            count = 0
            temp = []
    await write_(DATA_DICT, json.dumps(str(data)))
    return data


async def calculate(name: str, location: list, time=ephem.now()) -> Optional[list]:
    """

    :param name: 卫星名
    :param location: QTH[经度，纬度，海拔]
    :param time: 时间
    :return: [方位角，仰角，相对速率]
    """
    logger.debug(f"触发计算：{str(time)}")
    logger.info(f"计算卫星:{name}")
    logger.debug("QTJ:{str(location)}")

    me = ephem.Observer()
    me.lon, me.lat, me.elevation = location[0], location[1], float(location[2])
    if isChinese(name) and name in ['天宫', '天宫号', '中国空间站']:
        tle = (await get_tian_gong())
        name = "天宫"
    elif name.upper() == "TIANGONG":
        tle = (await get_tian_gong())
        name = "天宫"
    else:
        tle = (await data2Tle())
    try:
        sat = ephem.readtle(name, tle[name][0], tle[name][1])
        me.date = time
        sat.compute(me)
        az = str(sat.az * 180.0 / 3.1415926535)
        alt = str(sat.alt * 180.0 / 3.1415926535)
        range_velocity = str(sat.range_velocity)
        logger.debug("方位角： " + az)  # 卫星的方位角
        logger.debug("仰角： " + alt)  # 卫星的仰角
        logger.debug("运动速率： " + range_velocity)  # 卫星相对于观察者的运动速率，为正，表示卫星正在远离观察者。
        return [az, alt, range_velocity]
    except KeyError:
        logger.error("未找到卫星：" + name)
        return None


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(calculate("PO-101"))
