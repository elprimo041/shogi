# -*- coding: utf-8 -*-
import shogi_GUI
import pygame

# screen_size = 800

####################################
# GUIで操作
####################################

# gui = shogi_GUI.ShogiGUI()

# # スクリーンサイズを指定する場合
# # gui = ShogiGUI(screen_size)


# shogi_GUI.main_loop()


####################################
# 棋譜形式の手の入力で操作
# 入力例
# 76歩
# 58金右
# 投了する場合は"投了"と入力
# 直前の指し手を取り消す場合は"取消"と入力
# 終了する場合は何も入力せずにEnter
####################################

gui_kifu = shogi_GUI.GUI_kifu()

# スクリーンサイズを指定する場合
# gui_kifu = shogi_GUI.GUI_kifu(screen_size)

while True:
    kifu_move = input("次の指し手を入力してください：")
    if kifu_move == "":
        pygame.quit()
        break
    elif kifu_move == "投了":
        gui_kifu.surrender()
        pygame.quit()
        break       
    elif kifu_move == "取消":
        gui_kifu.redo()
    else:
        gui_kifu.move(kifu_move)
    gui_kifu.draw()