# python3
# -*- coding: utf-8 -*-
# @Time    : 2022/8/21 2:20
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : path.py
# @Software: PyCharm
from pathlib import Path


LOCAL = Path() / 'cqsat'
HAM_SAT = LOCAL / 'ham_sat.txt'
TIANGONG = LOCAL / 'tiangong.txt'
CONFIG = LOCAL / 'config.yml'
TEMP = LOCAL / 'temp.yaml'
DATA_DICT = LOCAL / 'data.txt'
QTH = LOCAL / 'qth.yml'
