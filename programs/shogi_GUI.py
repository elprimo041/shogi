# -*- coding: utf-8 -*-
import shogi_game
import pygame
from pygame.locals import *
import tkinter as tk
from tkinter import messagebox
import sys
import copy

class ShogiGUI():
    def __init__(self, screen_size_ = 300):
        # スクリーンサイズの0.7倍の大きさを盤の大きさとする
        self.SCREEN_SIZE = screen_size_
        board_size_rate = [3330, 3640]
        square_size_rate = [352, 386]
        scaling_rate = board_size_rate[0] / (self.SCREEN_SIZE[0] * 0.7)
        self.BOARD_SIZE = [int(d / scaling_rate) for d in board_size_rate]
        self.SQUARE_SIZE = [int(d / scaling_rate) for d in square_size_rate]
        
        # 持ち駒の数を表すフォントの設定
        pygame.font.init()
        FONT_SIZE = int(self.SQUARE_SIZE[0] * 0.7)
        self.font = pygame.font.Font(None, FONT_SIZE)
        
        # マス目に対する駒の大きさの割合を指定し、画像を読み込んで画像のサイズからマス目の大きさを決定
        self.PIECE_RATE = 0.9        
        image = pygame.image.load("../img/piece/piece_ou.png")
        rect = image.get_rect()
        width = rect[2]
        self.PIECE_SCALE = self.SQUARE_SIZE[0] * self.PIECE_RATE / width
        
        self.COLOR_BG = [40, 50, 80]
        self.COLOR_BORD = [139, 69, 19]        
        self.COLOR_LINE = (0, 0, 0)
        self.WIDTH_LINE = int(self.BOARD_SIZE[0] / 250)
        
        
        pygame.init()                                                                                                       
        self.screen = pygame.display.set_mode((self.SCREEN_SIZE[0], self.SCREEN_SIZE[1]))                                                                      
        pygame.display.set_caption("Shogi")
        
        self.rect_squares = []              # 盤のマスを表すrectの配列
        self.rect_bg = 0                    # 背景のrect
        self.img_pieces = {}                # 駒の画像を表すimgの辞書
        self.rect_promote = 0
        self.rect_not_promote = 0
        self.initialize_bord()

        self.game = shogi_game.ShogiGame()
        
        self.list_possession_piece_true = [[], []]
        self.list_possession_piece_false = [[], []]

    def main_loop(self):
        # loop内で用いる変数        
        piece_all_GUI = copy.deepcopy(self.game.piece_all)
        state_select = 0            # 何も選択していない状態なら0、動かせる駒を選択している状態なら1、成るか確認中の状態なら2     
        square_select = [-1, -1]
        movable_point = []
        name_is_promote = ""
        index_before = [-1, -1]
        point_after = [-1, -1]
        is_promote = False
        flag_move = False
        
        while True:
            self.screen.fill((self.COLOR_BG[0], self.COLOR_BG[1], self.COLOR_BG[2]))
            self.draw_board()
            self.draw_all_piece(piece_all_GUI)
            
            if state_select == 1:
                self.draw_emphasis_square(square_select, movable_point)
            elif state_select == 2:
                self.draw_is_promote(name_is_promote, point_after)
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()                                                                
                    sys.exit()
                
                if event.type == KEYDOWN:
                    if event.key == K_x:
                        for piece in piece_all_GUI:
                            print(piece)
                
                if (event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 1):
                    if state_select == 0:                     
                        for i in range(len(self.rect_squares)):
                            for j in range(len(self.rect_squares[i])):
                                if self.rect_squares[i][j].collidepoint(event.pos):
                                    # 持ち駒を選択したか判定
                                    if i == 0:
                                        if (self.game.turn) == True and (len(self.list_possession_piece_true[0]) > j):
                                            square_select = [i, j]
                                            state_select = 1
                                            name = self.list_possession_piece_true[0][j]                                            
                                            for index_piece in range(len(piece_all_GUI)):
                                                if (piece_all_GUI[index_piece][0] == name) and (piece_all_GUI[index_piece][1] == [0, 0]):
                                                    index_before = index_piece
                                                    movable_point = piece_all_GUI[index_before][3]
                                                    break
                                               
                                    elif i == 10:
                                        if (self.game.turn) == False and (len(self.list_possession_piece_false[0]) > j):
                                            square_select = [i, j]
                                            state_select = 1
                                            name = self.list_possession_piece_false[0][j]
                                            for index_piece in range(len(piece_all_GUI)):
                                                if (piece_all_GUI[index_piece][0] == name) and (piece_all_GUI[index_piece][1] == [10, 0]):
                                                    index_before = index_piece
                                                    movable_point = piece_all_GUI[index_before][3]
                                                    break
                                                
                                    # 盤面上の駒を選択したか判定
                                    elif self.game.get_square_state(piece_all_GUI, [i, j]) == self.game.turn:
                                        square_select = [i, j]
                                        state_select = 1
                                        index_before = self.game.get_piece_index(piece_all_GUI, square_select)
                                        movable_point = piece_all_GUI[index_before][3]
                                    else:
                                        square_select = [-1, -1]
                                                                   
                    elif state_select == 1:                        
                        for i in range(len(self.rect_squares)):
                            for j in range(len(self.rect_squares[i])):
                                if self.rect_squares[i][j].collidepoint(event.pos):
                                    index_movable = -1
                                    
                                    point_after = [i, j]
                                    for k in range(len(movable_point)):
                                        if (movable_point[k][0] == i) and (movable_point[k][1] == j):
                                            index_movable = k
                                    if index_movable != -1:
                                        if movable_point[index_movable][2] == -1:
                                            is_promote = False
                                            flag_move = True
                                        elif movable_point[index_movable][2] == 1:
                                            is_promote = True
                                            flag_move = True
                                        elif movable_point[index_movable][2] == 0:
                                            name_is_promote = piece_all_GUI[index_before][0]
                                            state_select = 2   
                                    elif index_movable == -1:
                                        state_select = 0
                                        square_select = [-1, -1]
                                        
                    elif state_select == 2:
                        if self.rect_promote.collidepoint(event.pos):
                            is_promote = True
                            flag_move = True
                        elif self.rect_not_promote.collidepoint(event.pos):
                            is_promote = False
                            flag_move = True
            
                    if flag_move == True:
                        self.game.proceed_turn(index_before, point_after, is_promote)
                        piece_all_GUI = copy.deepcopy(self.game.piece_all)
                        self.assign_rectangle_to_possession_pieces()
                        state_select = 0
                        flag_move = False
                        
            
            pygame.display.update()        
            if self.game.is_checkmate == True:
                piece_all_GUI = copy.deepcopy(self.game.piece_all)
                self.screen.fill((self.COLOR_BG[0], self.COLOR_BG[1], self.COLOR_BG[2]))
                self.draw_board()
                self.draw_all_piece(piece_all_GUI)
                pygame.display.update()
                root = tk.Tk()
                root.withdraw()
                msg = self.game.winner + "の勝ちです"
                _ = messagebox.showinfo(title = "対局終了", message = msg)
                pygame.quit()                                                                
                sys.exit()
                break
        
    def initialize_bord(self):
        # マス目と背景のrectを設定
        point_bg = [int(self.SCREEN_SIZE[0] / 2 - self.BOARD_SIZE[0] / 2), int(self.SCREEN_SIZE[1] / 2 - self.BOARD_SIZE[1] / 2)]
        self.rect_bg = pygame.Rect(point_bg[0], point_bg[1], self.BOARD_SIZE[0] ,self.BOARD_SIZE[1])      
        for x in range(11):
            rect_one_row = []
            if x == 0 or x == 10:
                if x == 0:
                    top = int(self.rect_bg.centery + self.SQUARE_SIZE[1] * 5)
                elif x == 10:
                    top = int(self.rect_bg.centery - self.SQUARE_SIZE[1] * 6)
                for i in range(7):
                    left = int(self.rect_bg.centerx + self.SQUARE_SIZE[0] * (-4.5+i))
                    rect = pygame.Rect(left, top, self.SQUARE_SIZE[0], self.SQUARE_SIZE[1])
                    rect_one_row.append(rect)
                    
            else:           
                for y in range(10):
                   if y == 0:
                       rect_one_row = [pygame.Rect(0, 0, 0, 0)]
                   else: 
                       left = int(self.rect_bg.centerx - self.SQUARE_SIZE[0] * (x-4.5))
                       top = int(self.rect_bg.centery - self.SQUARE_SIZE[1] * (5.5-y))
                       rect = pygame.Rect(left, top, self.SQUARE_SIZE[0], self.SQUARE_SIZE[1])
                       rect_one_row.append(rect)
            self.rect_squares.append(rect_one_row)
        
        # 画像の読み込み
        piece_name = ["hu", "to", "kyo", "narikyo", "kei", "narikei", "gin", "narigin", "kin",
                      "hisya", "ryu", "kaku", "uma", "ou", "gyoku"]
        for name in piece_name:
            img = pygame.image.load("../img/piece/piece_" + name + ".png")
            img_rect = img.get_rect()
            img = pygame.transform.scale(img, (int(img_rect[2] * self.PIECE_SCALE), int(img_rect[3] * self.PIECE_SCALE)))
            self.img_pieces[name] = img

    def draw_board(self):
        pygame.draw.rect(self.screen, self.COLOR_BORD, self.rect_bg)
        for i in range(len(self.rect_squares)):
            for j in range(len(self.rect_squares[i])):
                if i != 0 and i != 10 and j != 0:
                    pygame.draw.rect(self.screen, self.COLOR_LINE, self.rect_squares[i][j], self.WIDTH_LINE)

    def draw_all_piece(self, piece_all_):
        # 盤面上の駒を描写
        for piece in piece_all_:
            if piece[1][1] != 0:
                self.draw_one_piece(name_ = piece[0], point_ = piece[1], owner_ = piece[2])
        
        # 持ち駒を描写
        for i in range(len(self.list_possession_piece_true[0])):
            name = self.list_possession_piece_true[0][i]
            point = [0, i]
            owner = True
            num = self.list_possession_piece_true[1][i]
            self.draw_one_piece(name_ = name, point_ = point, owner_ = owner, num_ = num)
        for i in range(len(self.list_possession_piece_false[0])):
            name = self.list_possession_piece_false[0][i]
            point = [10, i]
            owner = False
            num = self.list_possession_piece_false[1][i]
            self.draw_one_piece(name_ = name, point_ = point, owner_ = owner, num_ = num)            
        
    def draw_one_piece(self, name_, point_, owner_, num_ = 1):
        img = self.img_pieces[name_]
        rect_img = img.get_rect()
        if owner_ == False:
            img = pygame.transform.rotate(img, 180)
        rect_square = self.rect_squares[point_[0]][point_[1]]   
        left = int(rect_square.centerx - rect_img.width/2)
        top = int(rect_square.centery -  rect_img.height/2)        
        self.screen.blit(img, (left, top))
        if num_ != 1:
            text = self.font.render(str(num_), True, (255, 241, 0))
            if owner_ == True:                    
                left = rect_square.right - rect_square.width * 0.3
                top = rect_square.top
            elif owner_ == False:                    
                left = rect_square.right - rect_square.width * 0.3
                top = rect_square.bottom - rect_square.height * 0.3
            self.screen.blit(text, [left, top])

    def assign_rectangle_to_possession_pieces(self):
        self.list_possession_piece_true = copy.deepcopy([[], []])
        self.list_possession_piece_false = copy.deepcopy([[], []])      
        for i in range(len(self.game.possession_piece_true[0])):
            if self.game.possession_piece_true[1][i] != 0:
                name = self.game.possession_piece_true[0][i]
                num = self.game.possession_piece_true[1][i]
                self.list_possession_piece_true[0].append(name)
                self.list_possession_piece_true[1].append(num)
        for i in range(len(self.game.possession_piece_false[0])):
            if self.game.possession_piece_false[1][i] != 0:
                name = self.game.possession_piece_false[0][i]
                num = self.game.possession_piece_false[1][i]
                self.list_possession_piece_false[0].append(name)
                self.list_possession_piece_false[1].append(num)

    def draw_emphasis_square(self, current_point_, movavle_point_):
        color_current = [255, 255, 0]
        color_movable = [239, 69, 74]  
        rect_current = self.rect_squares[current_point_[0]][current_point_[1]]
        rect_current_emphasis = rect_current.inflate(-self.WIDTH_LINE * 2, -self.WIDTH_LINE * 2)
        pygame.draw.rect(self.screen, color_current, rect_current_emphasis, int(self.WIDTH_LINE * 1.5))
    
        for point in movavle_point_:
            rect_movable = self.rect_squares[point[0]][point[1]]
            rect_movable_emphasis = rect_movable.inflate(-self.WIDTH_LINE * 4, -self.WIDTH_LINE * 4)
            pygame.draw.rect(self.screen, color_movable, rect_movable_emphasis, int(self.WIDTH_LINE * 1.5))

    def draw_is_promote(self, name_, point_):
        is_promote_rect_scale = 0.2
        normal_piece = ["hu", "kyo", "kei", "gin", "hisya", "kaku"]
        promoted_piece = ["to", "narikyo", "narikei", "narigin", "ryu", "uma"]
        for i in range(len(normal_piece)):
            if name_ == normal_piece[i]:
                index = i        
        promote_color = [219, 189, 0]
        not_promote_color = [204, 204, 204]
        window_color = [0, 0, 0]
    
        self.rect_promote = self.rect_squares[point_[0]][point_[1]].copy()
        self.rect_promote.inflate_ip(int(self.SQUARE_SIZE[0] * is_promote_rect_scale), int(self.SQUARE_SIZE[0] * is_promote_rect_scale))
        self.rect_promote.left = int(self.rect_promote.left - self.rect_promote.width * 0.5)
        pygame.draw.rect(self.screen, promote_color, self.rect_promote)
        pygame.draw.rect(self.screen, window_color, self.rect_promote, int(self.WIDTH_LINE * 1.5))
        img_promote = self.img_pieces[promoted_piece[index]]
        img_promote = pygame.transform.scale(img_promote, (int(self.rect_promote[2] * self.PIECE_RATE), int(self.rect_promote[3] * self.PIECE_RATE)))
        rect_img_promote = img_promote.get_rect()
        left = int(self.rect_promote.centerx - rect_img_promote.width / 2)
        top = int(self.rect_promote.centery -  rect_img_promote.height / 2)
        self.screen.blit(img_promote, (left, top))

        self.rect_not_promote = self.rect_squares[point_[0]][point_[1]].copy()
        self.rect_not_promote.inflate_ip(int(self.SQUARE_SIZE[0] * is_promote_rect_scale), int(self.SQUARE_SIZE[0] * is_promote_rect_scale))
        self.rect_not_promote.left = int(self.rect_not_promote.left + self.rect_not_promote.width * 0.5)
        pygame.draw.rect(self.screen, not_promote_color, self.rect_not_promote)
        pygame.draw.rect(self.screen, window_color, self.rect_not_promote, int(self.WIDTH_LINE * 1.5))
        img_not_promote = self.img_pieces[normal_piece[index]]
        img_not_promote = pygame.transform.scale(img_not_promote, (int(self.rect_not_promote[2] * self.PIECE_RATE), int(self.rect_not_promote[3] * self.PIECE_RATE)))
        rect_img_not_promote = img_not_promote.get_rect()
        left = int(self.rect_not_promote.centerx - rect_img_not_promote.width / 2)
        top = int(self.rect_not_promote.centery -  rect_img_not_promote.height / 2)
        self.screen.blit(img_not_promote, (left, top))

def main():
    shogi_GUI = ShogiGUI(screen_size_ = [1000, 1000])
    shogi_GUI.main_loop()
    

if __name__ == "__main__":
    main()        