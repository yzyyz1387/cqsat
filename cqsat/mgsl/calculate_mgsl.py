# python3
# -*- coding: utf-8 -*-
# @Time    : 2022/8/23 22:36
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : calculate_mgsl.py
# @Software: PyCharm
import math

index2Char = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
              'V', 'W', 'X', 'Y', 'Z']


# 计算场编号
def getField(lon, lat):
    global index2Char
    field1 = math.floor((180 + lon) / 20)
    field2 = math.floor((90 + lat) / 10)
    # print('场计算：%s-%s' % (field1,field2))
    field = index2Char[field1] + index2Char[field2]
    # print('场代码：%s' % field)
    return field


# 计算方编号
def getSquare(lon, lat):
    square1 = math.floor(math.floor(lon + 180) % 20 / 2)
    square2 = math.floor(lat + 90) % 10
    # print('方计算：%s-%s' % (square1,square2))
    square = str(square1) + str(square2)
    # print('方代码：%s' % square)
    return square


# 计算块编号
def getSubSquare(lon, lat):
    global index2Char
    subSquare1 = math.floor((lon - math.floor(lon / 2) * 2) * 60 / 5)
    subSquare2 = math.floor((lat - math.floor(lat)) * 60 / 2.5)
    # print('块计算:%s-%s' % (subSquare1,subSquare2))
    subSquare = index2Char[subSquare1] + index2Char[subSquare2]
    # print('块代码：%s' % subSquare)
    return subSquare


def getGrid(lon, lat):
    gridPos = getField(lon, lat)
    gridPos += getSquare(lon, lat)
    gridPos += getSubSquare(lon, lat)
    return gridPos


if __name__ == '__main__':
    lon = 75.8656
    lat = 39.3809
    a = getGrid(lon, lat)
    print(a)
