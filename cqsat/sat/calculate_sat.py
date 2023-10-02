# python3
# -*- coding: utf-8 -*-
# @Time    : 2022/8/21 2:28
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : calculate_sat.py
# @Software: PyCharm
import json
import re
from datetime import datetime, timedelta
from typing import Dict

from typing import Optional

from ..log import log
from ..utils import *
from ..path import *
import ephem

logger = log()


class AccessError(Exception):
    pass


def timeCompare(cache_path: Path, rela_file: Path) -> bool:
    """
    比较时间
    :param cache_path: 缓存文件路径
    :param rela_file: 相关文件路径
    :return: True:小于一天，False:大于一天
    """
    if cache_path.exists() and not rela_file.exists():
        cache_path.unlink()
        return True
    if cache_path.exists():
        modification_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        TIME_NOW = (datetime.now())
        TIME_DIFF = TIME_NOW - modification_time
        if TIME_DIFF > timedelta(days=1):
            cache_path.unlink() if cache_path.exists() else ...
            rela_file.unlink() if rela_file.exists() else ...
            return True
        else:
            return False
    else:
        rela_file.unlink() if rela_file.exists() else ...
        return True


async def get_tian_gong():
    # MAIN_URL = "https://www.cmse.gov.cn/gfgg/zgkjzgdcs"
    # Path.mkdir(LOCAL) if not Path.exists(LOCAL) else ...
    # logger.debug("读取在线数据...")
    # tian_gong_ = await http_get(MAIN_URL)
    # selected = re.findall(re.compile(r'class=TRS_Editor><a href="(.*?)"'), tian_gong_)[0]
    # OEM_url = MAIN_URL + selected
    # selected = re.findall(re.compile(r'<div><font face="Courier New">(.*?)</font></div>'), tian_gong_)
    # line1 = selected[0].replace('&nbsp;', ' ')
    # line2 = selected[1].replace('&nbsp;', ' ')
    # tg_data = {"天宫": [line1, line2]}

    if not timeCompare(CACHE_CSS, TIANGONG):
        logger.debug("读取本地数据...")
        content = (await read_all(TIANGONG))
        tg_data = json.loads(content)
    else:
        CACHE_CSS.unlink() if CACHE_CSS.exists() else ...
        TIANGONG.unlink() if TIANGONG.exists() else ...
        tg_data = await download_css_data()
    logger.debug("css数据读取完成")
    return tg_data


async def download_css_data():
    """
    下载天宫TLE轨道报
    :return:
    """
    CSS_TLE_url = 'https://celestrak.org/NORAD/elements/gp.php?INTDES=2021-035'
    # 注意：此地址短时间内访问过多会被禁止访问，被禁后2小时恢复
    # CSS_TLE_url2 = 'https://celestrak.org/NORAD/elements/gp.php?INTDES=2021'
    CSS_TLE_data = (await http_get(CSS_TLE_url)).replace('\r', '').split('\n')
    line1 = CSS_TLE_data[1]
    line2 = CSS_TLE_data[2]
    tg_data = {"天宫": [line1, line2]}
    logger.debug('下载天宫数据：', tg_data)
    logger.debug("写入本地数据...")
    await write_(TIANGONG, json.dumps(tg_data, ensure_ascii=False))
    CACHE_CSS.touch()
    return tg_data


async def download_ham_sat():
    Path.mkdir(LOCAL) if not Path.exists(LOCAL) else ...
    await get_tian_gong()
    url = "https://amsat.org/tle/current/nasabare.txt"
    if timeCompare(CACHE_OTHER, DATA_DICT):
        logger.debug("读取卫星在线数据...")
        ham_sat_ = (await http_get(url))
        if not ham_sat_:
            logger.error(f"从 {url} 下载数据出错")
            return None
        else:
            logger.debug("写入本地数据...")
            await write_(HAM_SAT, ham_sat_)
            CACHE_OTHER.touch()
            return ham_sat_
    else:
        logger.debug("读取卫星本地数据...")
        ham_sat_ = await read_all(HAM_SAT)
        return ham_sat_


async def data2Tle() -> Dict[str, list]:
    """
    将在线数据转换成TLE轨道报
    :return:
    """
    (await download_ham_sat())
    content = await read_all(HAM_SAT)
    logger.debug("载入卫星TLE数据...")
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
    await write_(DATA_DICT, json.dumps(str(data), ensure_ascii=False))
    data = {k.upper(): v for k, v in data.items()}
    return data


async def calculate(name: str, location: list, time=ephem.now()) -> Optional[list]:
    """

    :param name: 卫星名
    :param location: QTH[经度，纬度，海拔]
    :param time: 时间
    :return: [方位角，仰角，相对速率]
    """
    logger.debug(f"触发计算：{str(time)}")
    logger.debug(f"计算卫星:{name}")
    logger.debug("QTJ:{str(location)}")

    me = ephem.Observer()
    me.lon, me.lat, me.elevation = location[0], location[1], float(location[2])
    tle = (await data2Tle())
    if isChinese(name):
        if name in ['天宫', '天宫号', '中国空间站', '空间站', '天和', '核心舱']:
            tle = (await get_tian_gong())
            name = "天宫"
    else:
        name = name.upper()
        if name in ['TIANGONG', 'CSS', 'TIANHE']:
            tle = (await get_tian_gong())
            name = "天宫"
            if tle[name][1] == "<head>":
                raise AccessError
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
    except AccessError:
        logger.error("访问celestrak被拒绝")
        return None


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()
    # loop.run_until_complete(calculate("PO-101"))
    loop.run_until_complete(get_tian_gong())
