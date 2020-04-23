# -*- coding: utf-8 -*-
import copy
import tkinter as tk
from tkinter import messagebox
# class Test():
#     def __init__(self):
#         self.a = [[1,2],[3,4]]
#         self.boo = True
#     def print_a(self):
#         self.ppp(not self.boo)
#         print(self.boo)
        
#     def ppp(self, bbb):
#         print(bbb)
        
# t = Test()
# t.print_a()
# # tmp = copy.deepcopy(t.a)
# # tmp[0][1] = 10
# # t.print_a()

root = tk.Tk()
root.withdraw() #小さなウィンドウを表示させない
tmp = messagebox.showinfo(title = "対局終了", message = "test")
print(22)