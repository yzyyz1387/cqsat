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
async def getField(long: float, latitude: float):
    global index2Char
    field1 = math.floor((180 + long) / 20)
    field2 = math.floor((90 + latitude) / 10)
    # print('场计算：%s-%s' % (field1,field2))
    field = index2Char[field1] + index2Char[field2]
    # print('场代码：%s' % field)
    return field


# 计算方编号
async def getSquare(long: float, latitude: float):
    square1 = math.floor(math.floor(long + 180) % 20 / 2)
    square2 = math.floor(latitude + 90) % 10
    # print('方计算：%s-%s' % (square1,square2))
    square = str(square1) + str(square2)
    # print('方代码：%s' % square)
    return square


# 计算块编号
async def getSubSquare(long: float, latitude: float):
    global index2Char
    subSquare1 = math.floor((long - math.floor(long / 2) * 2) * 60 / 5)
    subSquare2 = math.floor((latitude - math.floor(latitude)) * 60 / 2.5)
    # print('块计算:%s-%s' % (subSquare1,subSquare2))
    subSquare = index2Char[subSquare1] + index2Char[subSquare2]
    # print('块代码：%s' % subSquare)
    return subSquare


async def getGrid(long: float, latitude: float):
    """
    计算网格
    :param long: 经度
    :param latitude: 纬度
    :return:
    """
    gridPos = await getField(long, latitude)
    gridPos += await getSquare(long, latitude)
    gridPos += await getSubSquare(long, latitude)
    return gridPos


if __name__ == '__main__':
    lon = 75.8656
    lat = 39.3809
    a = getGrid(lon, lat)
    print(a)
