# -*- coding: utf-8 -*-
import copy
import enum
import datetime
import sys

class PieceName(enum.Enum):
    ou = "玉"
    gyoku = "玉"
    hisya = "飛"
    ryu = "竜"
    kaku = "角"
    uma = "馬"
    kin = "金"
    gin = "銀"
    narigin = "成銀"
    kei = "桂"
    narikei = "成桂"
    kyo = "香"
    narikyo = "成香"
    hu = "歩"
    to = "と"

class PieceID(enum.IntEnum):
    ou = 1
    gyoku = -1
    hisya = 2
    ryu = -2
    kaku = 3
    uma = -3
    kin = 4
    gin = 5
    narigin = -5
    kei = 6
    narikei = -6
    kyo = 7
    narikyo = -7
    hu = 8
    to = -8


class Piece():
    def __init__(self, name_, point_, owner_, is_promote_ = False, is_hold_ = False):
        self.ID = PieceID[name_]
        self.name = self.get_name()
        self.point = point_
        self.owner = owner_
        self.is_promote = False
        self.is_hold = is_hold_
        self.movable_point = []
        
    def move(self, point_after_):
        self.point = point_after_
        self.is_hold = False
           
    def promote(self):
        self.ID = self.ID * -1          
        self.name = self.get_name()

    def captured(self):
        self.ID = abs(self.ID)
        self.name = self.get_name()
        self.owner = not self.owner
        self.is_hold = True

    def get_name(self):
        return PieceID(self.ID).name
        
    def status(self, print_movavle_ = True):
        print("name : {}".format(self.name))
        print("point : {}".format(self.point))
        print("is_hold : {}".format(self.is_hold))
        print("owner : {}".format(self.owner))
        if print_movavle_ == True:
            print("movable point : {}".format(self.movable_point))

class Move():
    def __init__(self, name_, point_before_, point_after_, is_promote_, turn_num_, sente_):
        self.name = name_
        self.point_before = point_before_
        self.point_after = point_after_
        self.is_promote = is_promote_
        self.turn_num = turn_num_
        self.sente = sente_
        if (turn_num_ % 2) == 0:
            self.turn = sente_
        else:
            self.turn = not sente_

    def inverse_point(self, point_):
        self.point_before = [10 - i for i in self.point_before]
        self.point_after = [10 - i for i in self.point_after]
        
    def convert_move_to_kifu(self, previous_point_after_):
        num_kanji = {1:"一", 2:"二", 3:"三", 4:"四", 5:"五",
                     6:"六", 7:"七", 8:"八", 9:"九"}
        if self.sente == False:
            point_before_ = self.inverse_point(self.point_before)
            point_after_ = self.inverse_point(self.point_after)
        else:
            point_before_ = self.point_before
            point_after_ = self.point_after
        
        kifu = str(self.turn_num)
        kifu += " "
        if self.sente == self.turn:
            kifu += "▲"
        else:
            kifu += "△"
        
        if point_after_ == previous_point_after_:
            kifu += "同"
        else:
            kifu += str(point_after_[0])
            kifu += num_kanji[point_after_[1]]
        kifu += PieceName[self.name].value
        if self.is_promote == True:
            kifu += "成"
        if point_before_[0] == 0:
            kifu += "打"
        kifu += "({}{})".format(point_before_[0], point_before_[1])
        return kifu
        
class ShogiGame():
    def __init__(self, sente_ = True, kifu_name_ = ""):
        self.sente = sente_
        self.turn = sente_
        self.is_checkmate = False
        self.winner = ""
        self.move_all = []
        self.kifu_name = kifu_name_
        self.turn_num = 1
        self.start_time = datetime.datetime.today()
        self.piece_all = self.initialize_piece(sente_)

    def proceed_turn(self, point_before_, point_after_, is_promote_):
        piece_all_tmp = copy.deepcopy(self.piece_all)
        # 移動の保存
        index_move = self.get_piece_index(piece_all_tmp, point_before_)
        name = piece_all_tmp[index_move].name
        self.move_all.append(Move(name, point_before_, point_after_, is_promote_, self.turn_num, self.sente))
        
        # 駒の移動
        self.piece_all = self.move_piece(piece_all_tmp, point_before_, point_after_, is_promote_)
        
        # 移動可能位置の更新
        self.turn = not(self.turn)
        self.turn_num += 1
        piece_all_tmp = copy.deepcopy(self.piece_all)
        piece_all_tmp = self.get_movable_point(piece_all_tmp, self.turn)
        piece_all_tmp = self.remove_prohibited_move(piece_all_tmp, copy.copy(self.turn))
        self.piece_all = copy.deepcopy(piece_all_tmp)
        
        # if self.is_check(piece_all_tmp, copy.copy(self.turn)) == True:
        #     print("王手")
        
        # 詰みの判定
        is_checkmate = True
        for piece in self.piece_all:
            if len(piece.movable_point) != 0:
                is_checkmate = False
                break
        if is_checkmate == True:
            self.save_kifu()
            self.is_checkmate = True
            if (self.sente == True) and (self.turn == True):
                self.winner = "後手(False)"
            elif (self.sente == True) and (self.turn == False):
                self.winner = "先手(True)"
            elif (self.sente == False) and (self.turn == True):
                self.winner = "先手(False)"
            elif (self.sente == False) and (self.turn == False):
                self.winner = "後手(True)"
        
    def initialize_piece(self, turn_):
        piece_all = []
        piece_all.append(Piece("gyoku", [5,1], False))
        piece_all.append(Piece("hu", [1,3], False))
        piece_all.append(Piece("hu", [2,3], False))
        piece_all.append(Piece("hu", [3,3], False))
        piece_all.append(Piece("hu", [4,3], False))
        piece_all.append(Piece("hu", [5,3], False))
        piece_all.append(Piece("hu", [6,3], False))
        piece_all.append(Piece("hu", [7,3], False))
        piece_all.append(Piece("hu", [8,3], False))
        piece_all.append(Piece("hu", [9,3], False))
        piece_all.append(Piece("kyo", [1,1], False))
        piece_all.append(Piece("kyo", [9,1], False))
        piece_all.append(Piece("kei", [2,1], False))
        piece_all.append(Piece("kei", [8,1], False))
        piece_all.append(Piece("gin", [3,1], False))
        piece_all.append(Piece("gin", [7,1], False))
        piece_all.append(Piece("kin", [6,1], False))
        piece_all.append(Piece("kin", [4,1], False))        
        piece_all.append(Piece("hisya", [8,2], False))
        piece_all.append(Piece("kaku", [2,2], False))

        piece_all.append(Piece("ou", [5,9], True))
        piece_all.append(Piece("hu", [1,7], True))
        piece_all.append(Piece("hu", [2,7], True))
        piece_all.append(Piece("hu", [3,7], True))
        piece_all.append(Piece("hu", [4,7], True))
        piece_all.append(Piece("hu", [5,7], True))
        piece_all.append(Piece("hu", [6,7], True))
        piece_all.append(Piece("hu", [7,7], True))
        piece_all.append(Piece("hu", [8,7], True))
        piece_all.append(Piece("hu", [9,7], True))
        piece_all.append(Piece("kyo", [1,9], True))
        piece_all.append(Piece("kyo", [9,9], True))
        piece_all.append(Piece("kei", [2,9], True))
        piece_all.append(Piece("kei", [8,9], True))
        piece_all.append(Piece("gin", [3,9], True))
        piece_all.append(Piece("gin", [7,9], True))
        piece_all.append(Piece("kin", [6,9], True))
        piece_all.append(Piece("kin", [4,9], True))        
        piece_all.append(Piece("hisya", [2,8], True))
        piece_all.append(Piece("kaku", [8,8], True))

        piece_all = self.get_movable_point(piece_all, turn_)            
        return piece_all

    def get_movable_point(self, piece_all_, turn_):
        def rel_point(piece_, direction_, distance_):
            ##direction_
            ## lh h rh
            ## l  p r
            ## lt t rt
            if "r" in direction_:
                x = piece.point[0] - int((piece.owner - 0.5) * 2) * distance_
            elif "l" in direction_:
                x = piece.point[0] + int((piece.owner - 0.5) * 2) * distance_
            else:
                x = piece.point[0]
                
            if "h" in direction_:
                y = piece.point[1] - int((piece.owner - 0.5) * 2) * distance_
            elif "t" in direction_:
                y = piece.point[1] + int((piece.owner - 0.5) * 2) * distance_
            else:
                y = piece.point[1]
                
            return [x, y]
                    
        for i in range(len(piece_all_)):
            piece = piece_all_[i]
            reachable_point = []            # 盤面のサイズや移動先のマスの状態を考慮しない移動可能なマス
            movable_point = []              # 盤面のサイズや移動先のマスの状態を考慮した移動可能なマス            
            if piece.owner == turn_:
                if piece.is_hold == True:      # 持ち駒
                    if piece.name == "hu" or piece.name == "kyo":
                        div = 1
                    elif piece.name == "kei":
                        div = 2
                    else:
                        div = 0
                        
                    if piece.owner == True:
                        y_range = range(1 + div, 10)
                    else:
                        y_range = range(1, 10 - div)
                    
                    for x in range(1, 10):
                        for y in y_range:
                            reachable_point.append([x, y])
                    
                    for p in reachable_point:
                        if self.get_square_state(piece_all_, p) == -1:
                            movable_point.append(p)
        
                else:                       # 盤面上の駒
                    if piece.name == "hu":
                        reachable_point.append(rel_point(piece, "h", 1))

                    elif piece.name == "kyo":
                        dist = 1
                        while True:
                            add_point = rel_point(piece, "h", dist)
                            state = self.get_square_state(piece_all_, add_point)
                            if state == -1:
                                reachable_point.append(add_point)
                                dist += 1
                            elif state == piece.owner or state == -2:
                                break
                            elif state == (not(piece.owner)):
                                reachable_point.append(add_point)
                                break                              
                    
                    elif piece.name == "kei":
                        y = rel_point(piece, "h", 2)[1]
                        x = piece.point[0] - 1
                        reachable_point.append([x, y])
                        x = piece.point[0] + 1
                        reachable_point.append([x, y])
                        
                    elif piece.name == "gin":
                        reachable_point.append(rel_point(piece, "h", 1))
                        reachable_point.append(rel_point(piece, "rh", 1))
                        reachable_point.append(rel_point(piece, "lh", 1))
                        reachable_point.append(rel_point(piece, "rt", 1))
                        reachable_point.append(rel_point(piece, "lt", 1))
                    
                    elif piece.name in ["kin", "narikyo", "narikei", "narigin", "to"]:
                        reachable_point.append(rel_point(piece, "h", 1))
                        reachable_point.append(rel_point(piece, "rh", 1))
                        reachable_point.append(rel_point(piece, "lh", 1))
                        reachable_point.append(rel_point(piece, "r", 1))
                        reachable_point.append(rel_point(piece, "l", 1))
                        reachable_point.append(rel_point(piece, "t", 1))
                        
                    elif piece.name in ["ou", "gyoku"]:
                        reachable_point.append(rel_point(piece, "h", 1))
                        reachable_point.append(rel_point(piece, "rh", 1))
                        reachable_point.append(rel_point(piece, "lh", 1))
                        reachable_point.append(rel_point(piece, "r", 1))
                        reachable_point.append(rel_point(piece, "l", 1))
                        reachable_point.append(rel_point(piece, "t", 1))
                        reachable_point.append(rel_point(piece, "rt", 1))
                        reachable_point.append(rel_point(piece, "lt", 1))
                        
                    elif piece.name in ["hisya", "ryu"]:
                        if piece.name == "ryu":
                            reachable_point.append(rel_point(piece, "rh", 1))
                            reachable_point.append(rel_point(piece, "lh", 1))
                            reachable_point.append(rel_point(piece, "rt", 1))
                            reachable_point.append(rel_point(piece, "lt", 1))
                        
                        directions = ["h", "t", "r", "l"]
                        for d in directions:
                            dist = 1
                            while True:
                                add_point = rel_point(piece, d, dist)
                                state = self.get_square_state(piece_all_, add_point)
                                if state == -1:
                                    reachable_point.append(add_point)
                                    dist += 1
                                elif state == piece.owner or state == -2:
                                    break
                                elif state == (not(piece.owner)):
                                    reachable_point.append(add_point)
                                    break                                     

                    elif piece.name in ["kaku", "uma"]:
                        if piece.name == "uma":
                            reachable_point.append(rel_point(piece, "h", 1))
                            reachable_point.append(rel_point(piece, "t", 1))
                            reachable_point.append(rel_point(piece, "r", 1))
                            reachable_point.append(rel_point(piece, "l", 1))
                        
                        directions = ["rh", "lh", "rt", "lt"]
                        for d in directions:
                            dist = 1
                            while True:
                                add_point = rel_point(piece, d, dist)
                                state = self.get_square_state(piece_all_, add_point)
                                if state == -1:
                                    reachable_point.append(add_point)
                                    dist += 1
                                elif state == piece.owner or state == -2:
                                    break
                                elif state == (not(piece.owner)):
                                    reachable_point.append(add_point)
                                    break
                            
                    for p in reachable_point:
                        state = self.get_square_state(piece_all_, p)
                        if (state == -1) or (state == (not piece.owner)):
                            movable_point.append(p)
        
            piece_all_[i].movable_point = movable_point
        return piece_all_
                 
    def remove_prohibited_move(self, piece_all_, turn_):
        # 王手放置を除去
        for piece in piece_all_:
            movable_point_consider_check = []
            for point_after in piece.movable_point:
                piece_all_after = copy.deepcopy(piece_all_)
                piece_all_after = self.move_piece(piece_all_after, piece.point, point_after, False)
                if self.is_check(piece_all_after, turn_) == False:
                    movable_point_consider_check.append(point_after)
            piece.movable_point = movable_point_consider_check
        
        # 二歩を除去
        line_exist_owners_hu = []        
        for piece in piece_all_:
            if (piece.name == "hu") and (piece.is_hold == False) and (piece.owner == turn_):
                line_exist_owners_hu.append(piece.point[0])
        for piece in piece_all_:
            movable_point_consider_nihu = []
            if (piece.name != "hu") or (piece.is_hold == False) or piece.owner == (not(turn_)):
                movable_point_consider_nihu = piece.movable_point
            else:
                for point_after in piece.movable_point:
                    if point_after[0] not in line_exist_owners_hu:
                        movable_point_consider_nihu.append(point_after)
            piece.movable_point = movable_point_consider_nihu
            
        return piece_all_
        
    def is_check(self, piece_all_, turn_):
        turn = not turn_
        for piece in piece_all_:
            if (piece.name in ["ou", "gyoku"]) and (piece.owner == (not turn)):
                point_king = piece.point
                break

        piece_all_ = self.get_movable_point(piece_all_, turn)
        for piece in piece_all_:
            for point_after in piece.movable_point:
                if point_after == point_king:
                    return True
        return False
        
    def move_piece(self, piece_all_, point_before_, point_after_, is_promote_):
        # 駒の取得
        index_move = self.get_piece_index(piece_all_, point_before_)
        if self.get_square_state(piece_all_, point_after_) == (not piece_all_[index_move].owner):
            index_captured = self.get_piece_index(piece_all_, point_after_)
            piece_all_[index_captured].captured()
            piece_all_ = self.assign_possession_pieces(piece_all_)
        
        # 駒の移動と成り
        piece_all_[index_move].move(point_after_)
        if is_promote_ == True:
            piece_all_[index_move].promote()
        piece_all_[index_move].hold = False
        
        return piece_all_

    def check_is_able_promote(self, turn_, name_, point_before_, point_after_):
        # 成る条件を満たしていない場合-1を返す
        # 成るか確認が必要な場合は0を返す
        # 成るしかないときは1を返す
        
        promote_condition = -1 
        if point_before_[0] != 0:   # 盤面上の駒
            if name_ in ["hu", "kyo", "kei", "gin", "hisya", "kaku"]:       
                if turn_ == True and point_after_[1] <= 3:
                    if name_ in ["hu", "kyo"] and point_after_[1] == 1:
                        promote_condition = 1
                    elif name_ == "kei" and point_after_[1] <= 2:
                        promote_condition = 1
                    else:
                        promote_condition = 0
                        
                elif turn_ == False and point_after_[1] >= 7:
                    if name_ in ["hu", "kyo"] and point_after_[1] == 9:
                        promote_condition = 1
                    elif name_ == "kei" and point_after_[1] >= 8:
                        promote_condition = 1
                    else:
                        promote_condition = 0 
        return promote_condition
        
    def get_piece_index(self,piece_all_, point_):
        # 与えられたマスにある駒のインデックスを検索する
        # 与えられたマスが空白の場合-1を返す
        index = -1
        for piece in piece_all_:
            if piece.point == point_:
                index = piece_all_.index(piece)
                break
        return index

    def get_square_state(self, piece_all_, point_):
        # 盤面外なら-2,空なら-1,駒があるならどちらの駒かをTrueかFalseで返す
        if min(point_) <= 0 or max(point_) >= 10:
            return -2
        point_index = self.get_piece_index(piece_all_, point_)
        if point_index == -1:
            return -1
        else:
            return piece_all_[point_index].owner
          
    def assign_possession_pieces(self, piece_all_):
        possession_piece_name = ["hu", "kyo", "kei", "gin", "kin", "hisya", "kaku"]
        count_true = 0
        count_false = 0
               
        for piece_name in possession_piece_name:
            flag_true = False
            flag_false = False
            
            for i in range(len(piece_all_)):
                if (piece_all_[i].name == piece_name) and (piece_all_[i].is_hold == True):
                    if piece_all_[i].owner == True:
                        flag_true = True
                        piece_all_[i].point = [count_true, 10]
                    elif piece_all_[i].owner == False:
                        flag_false = True
                        piece_all_[i].point = [count_false, 0]                        
              
            count_true += flag_true
            count_false += flag_false
            
        
        return piece_all_

    def convert_kifu_to_move(self, kifu):
        if kifu[0] == "同":
            point_after = self.move_all[-1].point_after
            kifu = kifu[1:]
        else:
            point_after = [int(kifu[0]), int(kifu[1])]
            kifu = kifu[2:]
        if self.sente == False:
            point_after = [10 - i for i in point_after]
        name = PieceName(kifu[0]).name
        kifu = kifu[1:]
        is_promote = False
        if len(kifu) >= 1:
            if kifu[-1] == "成":
                is_promote = True
                kifu = kifu[:-1]
        
        move_candidate_index = []        
        for i in range(len(self.piece_all)):
            if (self.piece_all[i].name == name) and (point_after in self.piece_all[i].movable_point):
                move_candidate_index.append(i)
        if len(move_candidate_index) == 1:
            point_before = self.piece_all[i].point
            
        self.proceed_turn(point_before, point_after, is_promote)
            
            
    def save_kifu(self):
        end_time = datetime.datetime.today()
        if self.kifu_name == "":
            self.kifu_name = self.start_time.strftime("%Y-%m-%d-%H-%M-%S") + ".kifu"
        elif ".kifu" not in self.kifu_name:
            self.kifu_name += ".kifu"
        with open("../kifu/" + self.kifu_name, "w", encoding='utf-8') as f:
            f.write("開始日時：" + self.start_time.strftime("%Y/%m/%d %H:%M:%S\n"))
            f.write("終了日時：" + end_time.strftime("%Y/%m/%d %H:%M:%S\n"))
            f.write("手数----指手----\n")
            previous_point_after = []
            for move in self.move_all:
                if self.sente == False:
                    move.inverse_point()
                row = move.convert_move_to_kifu(previous_point_after)
                f.write(row + "\n")
                previous_point_after = move.point_after
            f.write("詰み")
            
        
def main():
    game = ShogiGame()
    kifu_tmp = "76歩"
    
    game.convert_kifu_to_move(kifu_tmp)
    
    # game.proceed_turn([7,7], [7,6], False)
    # game.proceed_turn([3,3], [3,4], False)
    # game.proceed_turn([8,8], [2,2], True)
    
    # game.save_kifu()
    
    
        
        
if __name__ == "__main__":
    main()