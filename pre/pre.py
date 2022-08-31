# python3
# -*- coding: utf-8 -*-
# @Time    : 2022/8/31 3:11
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : pre.py
# @Software: PyCharm
import json
from pathlib import Path

RESOURCE = Path.cwd().parent / "cqsat_resource"
BANK = RESOURCE / "bank"


def txt2json(level: str) -> None:
    """
    将题库txt文件转换为json文件
    :param level: 难度
    :return:
    """
    with open(f"{level}.txt", 'r', encoding='utf-8') as f:
        data = f.read()
    data = data.split('\n')
    data = list(filter(None, data))
    count = 0
    temp = []
    sum_ = []
    dic = {}
    for i in range(len(data)):
        print(count)
        if count == 6:
            temp.append(data[i])
            count = 0
            sum_.append(temp)
            temp = []
        else:
            temp.append(data[i])
            count += 1
    s2 = []
    for i in range(len(sum_)):
        question = sum_[i]
        temp = []
        for j in question:
            j = j.replace("[", "")
            j = j.split("]")
            temp.append(j)
        s2.append(temp)
    for i in range(len(s2)):
        temp_dic = {}
        for j in s2[i]:
            count2 = str(i + 1)
            temp_dic[j[0]] = j[1]
            dic[count2] = temp_dic
    with open(BANK / f"{level}.json", 'w', encoding='utf-8') as f:
        json.dump(dic, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    txt2json("A")
    txt2json("B")
    txt2json("C")
