# -*- coding: utf-8 -*-
import shogi_game
import pygame
from pygame.locals import *
import tkinter as tk
from tkinter import messagebox
import sys
import copy

class ShogiGUI():
    def __init__(self, screen_size_ = 800):
        # スクリーンサイズの縦幅の0.75倍の大きさを盤の大きさとする
        self.SCREEN_SIZE = [int(screen_size_ * 4 / 3), screen_size_]
        board_size_rate = [3330, 3640]
        square_size_rate = [352, 386]
        scaling_rate = board_size_rate[1] / (self.SCREEN_SIZE[1] * 0.75)
        self.BOARD_SIZE = [int(d / scaling_rate) for d in board_size_rate]
        self.SQUARE_SIZE = [int(d / scaling_rate) for d in square_size_rate]
        
        # 持ち駒の数を表すフォントの設定
        pygame.font.init()
        FONT_SIZE = int(self.SQUARE_SIZE[0] * 0.7)
        self.font = pygame.font.Font(None, FONT_SIZE)
        
        # マス目に対する駒の大きさの割合を指定し、画像を読み込んで画像のサイズからマス目の大きさを決定
        self.PIECE_RATE = 0.9        
        image = pygame.image.load("../image/piece/piece_gyoku.png")
        rect = image.get_rect()
        width = rect.w
        self.PIECE_SCALE = self.SQUARE_SIZE[0] * self.PIECE_RATE / width
        
        self.COLOR_BG = [40, 50, 80]
        self.COLOR_BORD = [139, 69, 19]        
        self.COLOR_LINE = (0, 0, 0)
        self.WIDTH_LINE = int(self.BOARD_SIZE[0] / 400)
        
        
        pygame.init()                                                                                                       
        self.screen = pygame.display.set_mode((self.SCREEN_SIZE[0], self.SCREEN_SIZE[1]))                                                                      
        pygame.display.set_caption("Shogi")
        
        self.rect_squares = []              # 盤のマスを表すrectの配列
        self.rect_bg = None                 # 背景のrect
        self.img_pieces = {}                # 駒の画像を表すimgの辞書
        self.img_other = {}
        self.rect_promote = None
        self.rect_not_promote = None
        self.rect_surrender = None
        self.rect_redo = None
        self.initialize_bord()

        self.game = shogi_game.ShogiGame()

    def main_loop(self):
        # loop内で用いる変数        
        piece_all = copy.deepcopy(self.game.piece_all)    
        piece_select = None
        point_after = None
        is_promote = False
        flag_confirm_promote = False
        flag_move = False
        root = tk.Tk()
        root.withdraw()
        
        while True:
            self.screen.blit(self.img_other["bg"], (0, 0))
            self.draw_board()
            self.draw_button()
            
            
            if piece_select != None:
                self.draw_emphasis_square(piece_select)
            
            self.draw_all_piece(piece_all)    
            
            if flag_confirm_promote == True:
                self.draw_is_promote(piece_select.name, point_after)
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()                                                                
                    sys.exit()
                
                # デバック用
                # if event.type == KEYDOWN and event.key == K_x:
                #     for piece in piece_all:
                #         piece.status()
                #         print("--------------------------")
                        
                if (event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 1):
                    if self.rect_surrender.collidepoint(event.pos):
                        ret = messagebox.askyesno("確認", "投了しますか？")
                        if ret == True:
                            self.game.end_game()
                        
                    elif self.rect_redo.collidepoint(event.pos):
                        self.game.redo()
                        piece_all = copy.deepcopy(self.game.piece_all)
                        self.screen.blit(self.img_other["bg"], (0, 0))
                        self.draw_board()
                        self.draw_all_piece(piece_all)
                    
                    elif piece_select == None:                # 何も選択していない状態        
                        for y in range(len(self.rect_squares)):
                            for x in range(len(self.rect_squares[y])):
                                if self.rect_squares[y][x].collidepoint(event.pos):
                                    piece_select = None
                                    for piece in piece_all:
                                        if (piece.point == [x, y]) and (piece.owner == self.game.turn):
                                            piece_select = piece
                                            break
                                            
                                                                   
                    elif flag_confirm_promote == False:     # コマを選択している状態                  
                        for y in range(len(self.rect_squares)):
                            for x in range(len(self.rect_squares[y])):
                                if self.rect_squares[y][x].collidepoint(event.pos):                                  
                                    if [x, y] in piece_select.movable_point:
                                        promote_condition = self.game.check_is_able_promote(
                                            self.game.turn, piece_select.name, piece_select.point, [x, y])
                                        point_after = [x, y]
                                        if promote_condition == -1:
                                            is_promote = False
                                            flag_move = True                                           
                                        elif promote_condition == 1:
                                            is_promote = True
                                            flag_move = True
                                        elif promote_condition == 0:
                                            flag_confirm_promote = True
                                    else:
                                        piece_select = None
                                        point_after = None
                                        for piece in piece_all:
                                            if (piece.point == [x, y]) and (piece.owner == self.game.turn):
                                                piece_select = piece                                           
                                                break
                                        
                    else:                                   # 成るか確認している状態
                        if self.rect_promote.collidepoint(event.pos):
                            is_promote = True
                            flag_move = True
                            flag_confirm_promote = False
                        elif self.rect_not_promote.collidepoint(event.pos):
                            is_promote = False
                            flag_move = True
                            flag_confirm_promote = False
            
                    if flag_move == True:
                        self.game.proceed_turn(piece_select.point, point_after, is_promote)
                        piece_all = copy.deepcopy(self.game.piece_all)
                        piece_select = None
                        flag_move = False
                        
            
            pygame.display.update()        
            if self.game.is_end == True:
                piece_all = copy.deepcopy(self.game.piece_all)
                self.screen.blit(self.img_other["bg"], (0, 0))
                self.draw_board()
                self.draw_all_piece(piece_all)
                pygame.display.update()
                if self.game.foul == True:
                    if self.game.winner == "先手":
                        msg = "後手反則負け\n" + self.game.foul_msg
                    else:
                        msg = "先手反則負け\n" + self.game.foul_msg                
                elif self.game.is_repetition_of_moves == True:
                    msg = "千日手です"
                else:
                    msg = "まで、{}手で{}の勝ちです".format(self.game.turn_num - 1, self.game.winner)
                _ = messagebox.showinfo(title = "対局終了", message = msg)
                pygame.quit()                                                                
                sys.exit()
                break
        
    def initialize_bord(self):
        # マス目と背景のrectを設定
        point_bg = [int(self.SCREEN_SIZE[0] / 2 - self.BOARD_SIZE[0] / 2), int(self.SCREEN_SIZE[1] / 2 - self.BOARD_SIZE[1] / 2)]
        self.rect_bg = pygame.Rect(point_bg[0], point_bg[1], self.BOARD_SIZE[0] ,self.BOARD_SIZE[1])      
        for y in range(11):
            rect_one_row = []
            if y == 0 or y == 10:
                if y == 0:
                    top = int(self.rect_bg.centery - self.SQUARE_SIZE[1] * 6)
                elif y == 10:                    
                    top = int(self.rect_bg.centery + self.SQUARE_SIZE[1] * 5)
                for i in range(7):
                    left = int(self.rect_bg.centerx + self.SQUARE_SIZE[0] * (-4.5+i))
                    rect = pygame.Rect(left, top, self.SQUARE_SIZE[0], self.SQUARE_SIZE[1])
                    rect_one_row.append(rect)
                    
            else:           
                for x in range(10):
                   if x == 0:
                       rect_one_row = [pygame.Rect(0, 0, 0, 0)]
                   else: 
                       left = int(self.rect_bg.centerx - self.SQUARE_SIZE[0] * (x-4.5))
                       top = int(self.rect_bg.centery - self.SQUARE_SIZE[1] * (5.5-y))
                       rect = pygame.Rect(left, top, self.SQUARE_SIZE[0], self.SQUARE_SIZE[1])
                       rect_one_row.append(rect)
            self.rect_squares.append(rect_one_row)
        
        # 画像の読み込み
        piece_name = ["hu", "to", "kyo", "narikyo", "kei", "narikei", "gin", "narigin", "kin",
                      "hisya", "ryu", "kaku", "uma", "gyoku"]
        for name in piece_name:
            img = pygame.image.load("../image/piece/piece_" + name + ".png")
            img_rect = img.get_rect()
            img = pygame.transform.scale(img, (int(img_rect[2] * self.PIECE_SCALE), int(img_rect[3] * self.PIECE_SCALE)))
            self.img_pieces[name] = img
            
        img = pygame.image.load("../image/board.png")
        img = pygame.transform.scale(img, (self.BOARD_SIZE[0], self.BOARD_SIZE[1]))
        self.img_other["board"] = img
        
        img = pygame.image.load("../image/bg.png")
        img = pygame.transform.scale(img, (self.SCREEN_SIZE[0], self.SCREEN_SIZE[1]))
        self.img_other["bg"] = img
        
        img = pygame.image.load("../image/surrender.png")
        img = pygame.transform.scale(img, (self.SQUARE_SIZE[0]*2, self.SQUARE_SIZE[0]))
        self.img_other["surrender"] = img
        img_rect = img.get_rect()
        left = int(self.SCREEN_SIZE[0] - img_rect.w * 1.5)
        top = int(img_rect.h * 0.5)
        self.rect_surrender = pygame.Rect(left, top, img_rect.w, img_rect.h)      
        
        img = pygame.image.load("../image/redo.png")
        img = pygame.transform.scale(img, (self.SQUARE_SIZE[0]*2, self.SQUARE_SIZE[0]))
        self.img_other["redo"] = img
        top = int(img_rect.h * 1.8)
        self.rect_redo = pygame.Rect(left, top, img_rect.w, img_rect.h)
        
        img = pygame.image.load("../image/emphasis_current.png").convert_alpha(self.screen)
        img = pygame.transform.scale(img, (int(self.SQUARE_SIZE[0] * 0.9), int(self.SQUARE_SIZE[1] * 0.9)))
        self.img_other["emphasis_current"] = img      

        img = pygame.image.load("../image/emphasis_movable.png").convert_alpha(self.screen)
        img = pygame.transform.scale(img, (int(self.SQUARE_SIZE[0] * 0.9), int(self.SQUARE_SIZE[1] * 0.9)))
        self.img_other["emphasis_movable"] = img

    def draw_board(self):
        self.screen.blit(self.img_other["board"], (self.rect_bg.left, self.rect_bg.top))
        for i in range(len(self.rect_squares)):
            for j in range(len(self.rect_squares[i])):
                if i != 0 and i != 10 and j != 0:
                    pygame.draw.rect(self.screen, self.COLOR_LINE, self.rect_squares[i][j], self.WIDTH_LINE)

    def draw_button(self):
        left = self.rect_surrender.left
        top = self.rect_surrender.top
        self.screen.blit(self.img_other["surrender"], (left, top))
        top = self.rect_redo.top
        self.screen.blit(self.img_other["redo"], (left, top))

    def draw_all_piece(self, piece_all_):
        possession_piece_name = ["hu", "kyo", "kei", "gin", "kin", "hisya", "kaku"]
        possession_piece_true = {}
        possession_piece_false = {}
        for piece_name in possession_piece_name:
            possession_piece_true[piece_name] = 0
            possession_piece_false[piece_name] = 0
        
        # 盤面上の駒を描写
        for piece in piece_all_:
            if piece.is_hold == False:
                self.draw_one_piece(piece)
            else:
                if piece.owner == True:
                    possession_piece_true[piece.name] += 1
                else:                    
                    possession_piece_false[piece.name] += 1
                    
        for piece_name in possession_piece_name:
            for piece in piece_all_:
                if (piece.name == piece_name) and (piece.is_hold == True):
                    if (piece.owner == True) and (possession_piece_true[piece_name] != 0):
                        num = possession_piece_true[piece_name]
                        self.draw_one_piece(piece, num)
                        possession_piece_true[piece_name] = 0
                    elif (piece.owner == False) and (possession_piece_false[piece_name] != 0):
                        num = possession_piece_false[piece_name]
                        self.draw_one_piece(piece, num)
                        possession_piece_false[piece_name] = 0                       
                         
    def draw_one_piece(self, piece, num_ = 1):
        img = self.img_pieces[piece.name]
        rect_img = img.get_rect()
        if piece.owner == False:
            img = pygame.transform.rotate(img, 180)
        rect_square = self.rect_squares[piece.point[1]][piece.point[0]]
        left = int(rect_square.centerx - rect_img.width/2)
        top = int(rect_square.centery -  rect_img.height/2)        
        self.screen.blit(img, (left, top))
        if num_ != 1:
            text = self.font.render(str(num_), True, (255, 241, 0))
            if piece.owner == True:                
                left = rect_square.right - rect_square.width * 0.3
                top = rect_square.top
            elif piece.owner == False:                    
                left = rect_square.right - rect_square.width * 0.3
                top = rect_square.bottom - rect_square.height * 0.3
            self.screen.blit(text, [left, top])

    def draw_emphasis_square(self, piece):
        rect_current = self.rect_squares[piece.point[1]][piece.point[0]]
        img = self.img_other["emphasis_current"]
        left = rect_current.left - int(-self.SQUARE_SIZE[0] * 0.05)
        top = rect_current.top - int(-self.SQUARE_SIZE[1] * 0.05)
        self.screen.blit(img, (left, top))
        
        img = self.img_other["emphasis_movable"]
        for point in piece.movable_point:
            rect_movable = self.rect_squares[point[1]][point[0]]
            left = rect_movable.left - int(-self.SQUARE_SIZE[0] * 0.05)
            top = rect_movable.top - int(-self.SQUARE_SIZE[1] * 0.05)
            self.screen.blit(img, (left, top))

    def draw_is_promote(self, name_, point_):
        is_promote_rect_scale = 0.2
        promote_color = [219, 189, 0]
        not_promote_color = [204, 204, 204]
        window_color = [0, 0, 0]        
        
        piece_tmp = shogi_game.Piece(name_, [1,1], True)
        piece_tmp.promote()
        name_normal = name_
        name_promote = piece_tmp.name
        
        self.rect_promote = self.rect_squares[point_[1]][point_[0]].copy()
        self.rect_promote.inflate_ip(int(self.SQUARE_SIZE[0] * is_promote_rect_scale), int(self.SQUARE_SIZE[0] * is_promote_rect_scale))
        self.rect_promote.left = int(self.rect_promote.left - self.rect_promote.width * 0.5)
        pygame.draw.rect(self.screen, promote_color, self.rect_promote)
        pygame.draw.rect(self.screen, window_color, self.rect_promote, int(self.WIDTH_LINE * 1.5))
        img_promote = self.img_pieces[name_promote]
        img_promote = pygame.transform.scale(img_promote, (int(self.rect_promote[2] * self.PIECE_RATE), int(self.rect_promote[3] * self.PIECE_RATE)))
        rect_img_promote = img_promote.get_rect()
        left = int(self.rect_promote.centerx - rect_img_promote.width / 2)
        top = int(self.rect_promote.centery -  rect_img_promote.height / 2)
        self.screen.blit(img_promote, (left, top))

        self.rect_not_promote = self.rect_squares[point_[1]][point_[0]].copy()
        self.rect_not_promote.inflate_ip(int(self.SQUARE_SIZE[0] * is_promote_rect_scale), int(self.SQUARE_SIZE[0] * is_promote_rect_scale))
        self.rect_not_promote.left = int(self.rect_not_promote.left + self.rect_not_promote.width * 0.5)
        pygame.draw.rect(self.screen, not_promote_color, self.rect_not_promote)
        pygame.draw.rect(self.screen, window_color, self.rect_not_promote, int(self.WIDTH_LINE * 1.5))
        img_not_promote = self.img_pieces[name_normal]
        img_not_promote = pygame.transform.scale(img_not_promote, (int(self.rect_not_promote[2] * self.PIECE_RATE), int(self.rect_not_promote[3] * self.PIECE_RATE)))
        rect_img_not_promote = img_not_promote.get_rect()
        left = int(self.rect_not_promote.centerx - rect_img_not_promote.width / 2)
        top = int(self.rect_not_promote.centery -  rect_img_not_promote.height / 2)
        self.screen.blit(img_not_promote, (left, top))

class GUI_kifu(ShogiGUI):
    def __init__(self, screen_size_ = 800):
        super().__init__(screen_size_)
        self.draw()
        
    def draw(self):
        piece_all = copy.deepcopy(self.game.piece_all)
        self.screen.blit(self.img_other["bg"], (0, 0))
        self.draw_board()
        self.draw_all_piece(piece_all)
        pygame.display.update()
    
    def move(self, kifu_move):
        self.game.convert_kifu_move_to_move(kifu_move)
        self.draw()
        
    def surrender(self):
        self.game.end_game()
    
    def redo(self):
        self.game.redo()
        
def main():
    shogi_GUI = ShogiGUI(screen_size_ = 800)
    shogi_GUI.main_loop()

if __name__ == "__main__":
    main()        