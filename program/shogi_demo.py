# -*- coding: utf-8 -*-
import shogi_GUI
import pygame

screen_size = [500, 500]

####################################
# GUIで操作する場合
####################################

#gui = shogi_GUI.ShogiGUI()

# スクリーンサイズを指定する場合
#gui = ShogiGUI(screen_size)


#shogi_GUI.main_loop()


####################################
# 棋譜形式の手の入力で操作する場合
####################################

# gui_kifu = shogi_GUI.GUI_kifu()

# スクリーンサイズを指定する場合
gui_kifu = shogi_GUI.GUI_kifu(screen_size)

while True:
    kifu_move = input("次の指し手を入力してください：")
    if kifu_move == "":
        pygame.quit()
        break
    gui_kifu.move(kifu_move)
    gui_kifu.draw()