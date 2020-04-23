# -*- coding: utf-8 -*-
import enum

class PieceName(enum.Enum):
    hu = "歩"
    hisya = "飛車"

class PieceID(enum.Enum):
    hu = 1
    hisya = 2


dic = {"hu":0, "hisya":0}

print(dic["hu"])
dic["hu"] -= 1
print(dic)

print(type(dic.keys()))

for i in range(10):
    print(i)
