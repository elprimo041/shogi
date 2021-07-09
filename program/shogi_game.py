# -*- coding: utf-8 -*-
import copy
import enum
import datetime

class PieceName(enum.Enum):
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

def get_csa_name(name):
    if name == "gyoku":
        csa_name = "OU"
    elif name == "hisya":
        csa_name = "HI"
    elif name == "ryu":
        csa_name = "RY"
    elif name == "kaku":
        csa_name = "KA"
    elif name == "uma":
        csa_name = "UM"
    elif name == "kin":
        csa_name = "KI"
    elif name == "gin":
        csa_name = "GI"
    elif name == "narigin":
        csa_name = "NG"
    elif name == "kei":
        csa_name = "KE"
    elif name == "narikei":
        csa_name = "NK"
    elif name == "kyo":
        csa_name = "KY"
    elif name == "narikyo":
        csa_name = "NY"
    elif name == "hu":
        csa_name = "FU"
    elif name == "to":
        csa_name = "TO"
    else:
        print("unknown piece name:{}".format(name))
    return csa_name

def get_promoted_csa_name(name):
    if name == "HI":
        promoted_csa_name = "RY"
    elif name == "KA":
        promoted_csa_name = "UM"
    elif name == "GI":
        promoted_csa_name = "NG"
    elif name == "KE":
        promoted_csa_name = "NK"
    elif name == "KY":
        promoted_csa_name = "NY"
    elif name == "FU":
        promoted_csa_name = "TO"
    return promoted_csa_name

def is_promote_from_csa_name(csa_name):
    if csa_name in ["RY", "UM", "NG", "NK", "NY", "TO"]:
        return True
    else:
        return False

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
        self.is_end = False
        self.is_checkmate = False
        self.is_repetition_of_moves = False
        self.foul = False
        self.foul_msg = ""
        self.winner = ""
        self.move_all = []
        self.kifu_name = kifu_name_
        self.turn_num = 1
        self.start_time = datetime.datetime.today()
        self.piece_all = self.initialize_piece(sente_)
        self.piece_all_history = [copy.deepcopy(self.piece_all)]

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
        self.piece_all_history.append(copy.deepcopy(piece_all_tmp))
        
        # if self.is_check(piece_all_tmp, copy.copy(self.turn)) == True:
        #     print("王手")
        
        # 詰みの判定
        is_checkmate = True
        for piece in self.piece_all:
            if len(piece.movable_point) != 0:
                is_checkmate = False
                break
        if is_checkmate == True:
            self.is_checkmate = True
            self.end_game()
            
        # 千日手の判定
        self.check_repetition_of_moves()
        if self.is_repetition_of_moves == True:
            self.end_game()
        
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

        piece_all.append(Piece("gyoku", [5,9], True))
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

    def end_game(self):
        self.is_end = True
        if self.is_repetition_of_moves == True:
            if self.is_check(copy.deepcopy(self.piece_all), copy.copy(self.turn)) == True:
                self.foul = True
                self.foul_msg = "連続王手の千日手"
                if (self.sente == True) and (self.turn == True):
                    self.winner = "先手"
                elif (self.sente == True) and (self.turn == False):
                    self.winner = "後手"
                elif (self.sente == False) and (self.turn == True):
                    self.winner = "後手"
                elif (self.sente == False) and (self.turn == False):
                    self.winner = "先手"
        
        else:
            if (self.sente == True) and (self.turn == True):
                self.winner = "後手"
            elif (self.sente == True) and (self.turn == False):
                self.winner = "先手"
            elif (self.sente == False) and (self.turn == True):
                self.winner = "先手"
            elif (self.sente == False) and (self.turn == False):
                self.winner = "後手"
        self.save_kifu()

    def redo(self):
        if self.turn_num == 1:
            return -1
        self.turn = not self.turn
        self.turn_num -= 1
        self.move_all = self.move_all[:-1]
        self.piece_all = self.piece_all_history[-2]
        self.piece_all_history = self.piece_all_history[:-1]           
                
    def get_rel_point(self, piece_, direction_, distance_):
        ##direction_
        ## lh h rh
        ## l  p r
        ## lt t rt
        if "r" in direction_:
            x = piece_.point[0] - int((piece_.owner - 0.5) * 2) * distance_
        elif "l" in direction_:
            x = piece_.point[0] + int((piece_.owner - 0.5) * 2) * distance_
        else:
            x = piece_.point[0]
            
        if "h" in direction_:
            y = piece_.point[1] - int((piece_.owner - 0.5) * 2) * distance_
        elif "t" in direction_:
            y = piece_.point[1] + int((piece_.owner - 0.5) * 2) * distance_
        else:
            y = piece_.point[1]
            
        return [x, y]

    def get_movable_point(self, piece_all_, turn_):                   
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
                        reachable_point.append(self.get_rel_point(piece, "h", 1))

                    elif piece.name == "kyo":
                        dist = 1
                        while True:
                            add_point = self.get_rel_point(piece, "h", dist)
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
                        y = self.get_rel_point(piece, "h", 2)[1]
                        x = piece.point[0] - 1
                        reachable_point.append([x, y])
                        x = piece.point[0] + 1
                        reachable_point.append([x, y])
                        
                    elif piece.name == "gin":
                        reachable_point.append(self.get_rel_point(piece, "h", 1))
                        reachable_point.append(self.get_rel_point(piece, "rh", 1))
                        reachable_point.append(self.get_rel_point(piece, "lh", 1))
                        reachable_point.append(self.get_rel_point(piece, "rt", 1))
                        reachable_point.append(self.get_rel_point(piece, "lt", 1))
                    
                    elif piece.name in ["kin", "narikyo", "narikei", "narigin", "to"]:
                        reachable_point.append(self.get_rel_point(piece, "h", 1))
                        reachable_point.append(self.get_rel_point(piece, "rh", 1))
                        reachable_point.append(self.get_rel_point(piece, "lh", 1))
                        reachable_point.append(self.get_rel_point(piece, "r", 1))
                        reachable_point.append(self.get_rel_point(piece, "l", 1))
                        reachable_point.append(self.get_rel_point(piece, "t", 1))
                        
                    elif piece.name == "gyoku":
                        reachable_point.append(self.get_rel_point(piece, "h", 1))
                        reachable_point.append(self.get_rel_point(piece, "rh", 1))
                        reachable_point.append(self.get_rel_point(piece, "lh", 1))
                        reachable_point.append(self.get_rel_point(piece, "r", 1))
                        reachable_point.append(self.get_rel_point(piece, "l", 1))
                        reachable_point.append(self.get_rel_point(piece, "t", 1))
                        reachable_point.append(self.get_rel_point(piece, "rt", 1))
                        reachable_point.append(self.get_rel_point(piece, "lt", 1))
                        
                    elif piece.name in ["hisya", "ryu"]:
                        if piece.name == "ryu":
                            reachable_point.append(self.get_rel_point(piece, "rh", 1))
                            reachable_point.append(self.get_rel_point(piece, "lh", 1))
                            reachable_point.append(self.get_rel_point(piece, "rt", 1))
                            reachable_point.append(self.get_rel_point(piece, "lt", 1))
                        
                        directions = ["h", "t", "r", "l"]
                        for direc in directions:
                            dist = 1
                            while True:
                                add_point = self.get_rel_point(piece, direc, dist)
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
                            reachable_point.append(self.get_rel_point(piece, "h", 1))
                            reachable_point.append(self.get_rel_point(piece, "t", 1))
                            reachable_point.append(self.get_rel_point(piece, "r", 1))
                            reachable_point.append(self.get_rel_point(piece, "l", 1))
                        
                        directions = ["rh", "lh", "rt", "lt"]
                        for direc in directions:
                            dist = 1
                            while True:
                                add_point = self.get_rel_point(piece, direc, dist)
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
    
    def check_repetition_of_moves(self):
        def get_board(piece_all_):
            board = [[""] * 9 for i in range(9)]
            for piece in piece_all_:
                if piece.is_hold != True:
                    x = piece.point[0] - 1
                    y = piece.point[1] - 1
                    name = piece.name
                    if piece.owner == False:
                        name += "-"
                    board[y][x] = name
            return board        
        
        def get_possession(piece_all_):
            possession_true = {}
            possession_false = {}
            possession_names = ["hu", "kyo", "kei", "gin", "kin", "kaku", "hisya"]
            for name in possession_names:
                possession_true[name] = 0
                possession_false[name] = 0
            for piece in piece_all_:
                if (piece.is_hold == True) and (piece.owner == True):
                    possession_true[piece.name] += 1
                elif (piece.is_hold == True) and (piece.owner == False):
                    possession_false[piece.name] += 1
            return possession_true, possession_false
        
        turn = False        
        board_now = get_board(self.piece_all)
        possession_true_now, _ = get_possession(self.piece_all)
        count = 0
        for piece_all_past in self.piece_all_history[:-1][::-1]:
            if turn == True:                
                board_past = get_board(piece_all_past)
                if board_now == board_past:
                    possession_true_past, _ = get_possession(piece_all_past)
                    if possession_true_now == possession_true_past:
                        count += 1
            turn = not turn
        if count >= 4:
            self.is_repetition_of_moves = True
        
    def is_check(self, piece_all_, turn_):
        turn = not turn_
        for piece in piece_all_:
            if (piece.name == "gyoku") and (piece.owner == (not turn)):
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
        if point_before_[1] != 0 and point_before_[1] != 10:   # 盤面上の駒
            if name_ in ["hu", "kyo", "kei", "gin", "kaku", "hisya"]:       
                if turn_ == True:
                    if point_before_[1] <= 3 or point_after_[1] <= 3:
                        if name_ in ["hu", "kyo"] and point_after_[1] == 1:
                            promote_condition = 1
                        elif name_ == "kei" and point_after_[1] <= 2:
                            promote_condition = 1
                        else:
                            promote_condition = 0
                        
                elif turn_ == False:
                    if point_before_[1] >= 7 or point_after_[1] >= 7:
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

    def convert_kifu_move_to_move(self, kifu_move):
        if kifu_move[0] == "同":
            point_after = self.move_all[-1].point_after
            kifu_move = kifu_move[1:]
        else:
            point_after = [int(kifu_move[0]), int(kifu_move[1])]
            kifu_move = kifu_move[2:]
        if self.sente == False:
            point_after = [10 - i for i in point_after]
        name = PieceName(kifu_move[0]).name
        kifu_move = kifu_move[1:]
        is_promote = False
        if len(kifu_move) >= 1:
            if kifu_move[-2:] == "不成":
                print(11211)
                kifu_move = kifu_move[:-2]
            elif kifu_move[-1] == "成":
                is_promote = True
                kifu_move = kifu_move[:-1]
        if len(kifu_move) >= 1:
            pass
        
        move_candidate_index = []        
        for i in range(len(self.piece_all)):
            if (self.piece_all[i].name == name) and (point_after in self.piece_all[i].movable_point):
                move_candidate_index.append(i)
                
        if len(move_candidate_index) == 0:
            print("無効な移動です")
            return -1
        
        elif len(move_candidate_index) == 1:
            index = move_candidate_index[0]
            point_before = self.piece_all[index].point
            
        else:
            if "打" in kifu_move:
                for i in move_candidate_index:
                    if self.piece_all[i].is_hold == True:
                        point_before = self.piece_all[i].point
                        break
            else:
                if name == "kei":
                    for i in move_candidate_index:
                        directions = ["r", "l"]
                        for direc in directions:
                            rel_point = self.get_rel_point(self.piece_all[i], direc, 1)
                            if rel_point[0] == point_after[0]:
                                point_before = self.piece_all[i].point
                                break
                
                else:
                    directions = ["h", "rh", "lh", "r", "l", "t", "rt", "lt"]
                    candidate_directions = []

                    for i in move_candidate_index:
                        dist = 1
                        flag_end = False
                        while flag_end == False:
                            for direc in directions:
                                rel_point = self.get_rel_point(self.piece_all[i], direc, dist)
                                if rel_point == point_after:
                                    candidate_directions.append(direc)
                                    flag_end = True
                                    break
                            dist += 1
                            
                    if "右" in kifu_move:
                        for i in range(len(candidate_directions)):
                            if "l" not in candidate_directions[i]:
                                candidate_directions[i] = ""                    
                    elif "左" in kifu_move:
                        for i in range(len(candidate_directions)):
                            if "r" not in candidate_directions[i]:
                                candidate_directions[i] = ""
                    
                    if "直" in kifu_move:
                        for i in range(len(candidate_directions)):
                            if candidate_directions[i] != "h":
                                candidate_directions[i] = ""
                    elif "上" in kifu_move:
                        for i in range(len(candidate_directions)):
                            if "h" not in candidate_directions[i]:
                                candidate_directions[i] = "" 
                    elif "引" in kifu_move:
                        for i in range(len(candidate_directions)):
                            if "t" not in candidate_directions[i]:
                                candidate_directions[i] = ""                       
                    elif "寄" in kifu_move:
                        for i in range(len(candidate_directions)):
                            if ("r" not in candidate_directions[i]) and ("l" not in candidate_directions[i]):
                                candidate_directions[i] = ""
                    
                    if candidate_directions.count("") != len(candidate_directions) -1:
                        print("指し手が一意に定まりません")
                        return -1
                    else:
                        tmp = [i for i, x in enumerate(candidate_directions) if x != ""][0]
                        index = move_candidate_index[tmp]
                        point_before = self.piece_all[index].point
                        
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
            if self.foul == True:
                f.write("反則負け")
                f.write("# " + self.foul_msg)
            elif self.is_repetition_of_moves == True:
                f.write("千日手")                
            elif self.is_checkmate == True:
                f.write("詰み")
            else:
                f.write("投了")
                
    def get_legal_move(self):
        legal_move = []
        for piece in self.piece_all:
            if piece.point[1] == 0 or piece.point[1] == 10:
                point_before_str = "00"
            else:
                point_before_str = "{}{}".format(piece.point[0], piece.point[1])
            for point_after in piece.movable_point:
                
                point_after_str = "{}{}".format(point_after[0], point_after[1])
                check_result = self.check_is_able_promote(self.turn, piece.name, piece.point, point_after)
                if check_result == -1:
                    piece_name_after = get_csa_name(piece.name)
                    legal_move.append(point_before_str+point_after_str+piece_name_after)
                elif check_result == 1:
                    piece_name_after = get_promoted_csa_name(get_csa_name(piece.name))
                    legal_move.append(point_before_str+point_after_str+piece_name_after)
                elif check_result == 0:
                    piece_name_after = get_csa_name(piece.name)
                    legal_move.append(point_before_str+point_after_str+piece_name_after)
                    piece_name_after = get_promoted_csa_name(get_csa_name(piece.name))
                    legal_move.append(point_before_str+point_after_str+piece_name_after)
        return legal_move
    
    def get_board(self):
        board = "'  9  8  7  6  5  4  3  2  1\n"
        for j in range(9):
            board += "P{}".format(j+1)
            for i in range(9):
                index = self.get_piece_index(self.piece_all, [9-i, j+1])
                if index == -1:
                    board += " * "
                else:
                    if self.piece_all[index].owner == True:
                        board += "+"
                    else:
                        board += "-"
                    board += get_csa_name(self.piece_all[index].name)
            board += "\n"
            
        possession_piece_name = ["hu", "kyo", "kei", "gin", "kin", "hisya", "kaku"]
        possession_piece_true = {}
        possession_piece_false = {}
        for piece_name in possession_piece_name:
            possession_piece_true[piece_name] = 0
            possession_piece_false[piece_name] = 0
        
        for piece in self.piece_all:
            if piece.is_hold == True:
                if piece.owner == True:
                    possession_piece_true[piece.name] += 1
                else:                    
                    possession_piece_false[piece.name] += 1
                    
        for piece_name in possession_piece_name:
            piece_name_csa = get_csa_name(piece_name)
            if possession_piece_true[piece_name] != 0:
                board += "P+" + "00{}".format(piece_name_csa) * possession_piece_true[piece_name]
                board += "\n"
        for piece_name in possession_piece_name:
            piece_name_csa = get_csa_name(piece_name)
            if possession_piece_false[piece_name] != 0:
                board += "P-" + "00{}".format(piece_name_csa) * possession_piece_false[piece_name]
                board += "\n"
        
        return board
    
    def push(self, csa_move):
        if csa_move == "resign":
            self.end_game()
        else:
            point_before = [int(csa_move[0]), int(csa_move[1])]
            if point_before == [0, 0]:
                for p in self.piece_all:
                    if (csa_move[4:] == get_csa_name(p.name))\
                    and (p.is_hold == True)\
                    and (p.owner == self.turn):
                        point_before = p.point
                        break
                                
            point_after = [int(csa_move[2]), int(csa_move[3])]
            index = self.get_piece_index(self.piece_all, point_before)
            csa_name = get_csa_name(self.piece_all[index].name)
            is_promote_before = is_promote_from_csa_name(csa_name)
            is_promote_after = is_promote_from_csa_name(csa_move[4:])
            if is_promote_before == False and is_promote_after == True:
                is_promote = True
            else:
                is_promote = False
            self.proceed_turn(point_before, point_after, is_promote)
                    
                



def check(is_print=True):
    import shogi_game_cshogi
    import random
    import cshogi
    import time
    import re
    game_original = ShogiGame()
    game_cshogi = shogi_game_cshogi.Game()
    is_same = True
    # board_cshogi = ""
    # board_cshogi_list = str(game_cshogi.board).split("\n")
    # for l in board_cshogi_list:
    #     if l.startswith(("P", "'")):
    #         board_cshogi += l + "\n"
    # legal_move_cshogi = set()
    # for legal_move in game_cshogi.board.legal_moves:
    #     legal_move_cshogi.add(cshogi.move_to_csa(legal_move))
    
    # board_original = game_original.get_board()
    # legal_move_original = set(game_original.get_legal_move())
    
    # if board_original != board_cshogi:
    #     print("board is different")
    #     print(board_original)
    #     print("===============================")
    #     print(board_cshogi)
    #     print("===============================")
    #     is_same = False
    # if legal_move_original != legal_move_cshogi:
    #     print("legal_move is different")
    #     print(legal_move_original)
    #     print("===============================")
    #     print(legal_move_cshogi)
    #     print("===============================")
    #     is_same = False
    # if is_same == False:
    #     print("not start")
    # else:
    #     print("start check")
    board_original = game_original.get_board()
    if is_print:
        print("{}手目".format(game_original.turn_num))
        print(board_original)
        print("===============================")
    while is_same == True:
        move = random.choice(game_original.get_legal_move())
        game_original.push(move)
        is_end_original = game_original.is_end
        is_end_cshogi = game_cshogi.turn_process(move)
        board_cshogi = ""
        board_cshogi_list = str(game_cshogi.board).split("\n")
        
        board_original = "\n".join(game_original.get_board().split("\n")[:10])
        board_original += "\n"
        legal_move_original = set(game_original.get_legal_move())
        
        for l in board_cshogi_list:
            if (l.startswith(("'"))) or (re.findall(r"P\d", l) != []):
                board_cshogi += l + "\n"
        hand_cshogi = [[], []]
        hand_original = [[], []]
        for l in board_cshogi_list:
            if l.startswith("P+"):
                hand_cshogi[0] += re.findall(r"00(..)", l)
            elif l.startswith("P-"):
                hand_cshogi[1] += re.findall(r"00(..)", l)
        for l in game_original.get_board().split("\n"):
            if l.startswith("P+"):
                hand_original[0] += re.findall(r"00(..)", l)
            elif l.startswith("P-"):
                hand_original[1] += re.findall(r"00(..)", l)
        legal_move_cshogi = set()
        for legal_move in game_cshogi.board.legal_moves:
            legal_move_cshogi.add(cshogi.move_to_csa(legal_move))
            
        
        if is_print:
            print("{}手目".format(game_original.turn_num))
            print(move)
            print(board_original)
            print("===============================")
        
        if board_original != board_cshogi or\
            equal_list(hand_cshogi[0], hand_original[0]) == False or\
            equal_list(hand_cshogi[1], hand_original[1]) == False:
            print("board is different")
            is_same = False
        if legal_move_original != legal_move_cshogi:
            print("legal_move is different")
            is_same = False
        if is_end_original != is_end_cshogi:
            print("is_end is different")
            is_same = False
            
        if is_end_original == True:
            print("successfully finished")
            if game_original.foul == True:
                if game_original.winner == "先手":
                    msg = "後手反則負け\n" + game_original.foul_msg
                else:
                    msg = "先手反則負け\n" + game_original.foul_msg                
            elif game_original.is_repetition_of_moves == True:
                msg = "千日手です"
            else:
                msg = "まで、{}手で{}の勝ちです".format(game_original.turn_num - 1, game_original.winner)
            print(msg)
            break
        
        if game_original.turn_num == 1000:
            print("1000手に達したので引き分け")
            break
        
    if is_same == True:
        return game_original.turn_num
    else:
        print(board_original)
        print("先手持駒:{}".format(hand_original[0]))
        print("後手持駒:{}".format(hand_original[1]))
        print("===============================")
        print(board_cshogi)
        print("先手持駒:{}".format(hand_cshogi[0]))
        print("後手持駒:{}".format(hand_cshogi[1]))
        print("===============================")
        print(legal_move_original)
        print("===============================")
        print(legal_move_cshogi)
        print("===============================")
        print(legal_move_original ^ legal_move_cshogi)
        print("===============================")
        print(is_end_original, is_end_cshogi)
        game_original.end_game()
        return -1

def equal_list(lst1, lst2):
    lst = lst1.copy()
    for element in lst2:
        try:
            lst.remove(element)
        except ValueError:
            break
    else:
        if not lst:
            return True
    return False

def check_loop(total_turn_num=100000):
    turn = 0
    while turn < total_turn_num:
        turn_one_game = check(False)
        if turn_one_game != -1:
            turn += turn_one_game
        else:
            break
        
        
def game_test():
    game = ShogiGame()
    while True:
        print(game.get_board())
        csa_move = input("input csa move\n>>")
        if csa_move == "show":
            print(game.get_legal_move())
        elif csa_move == "resign":
            game.push(csa_move)
        elif csa_move in game.get_legal_move():
            game.push(csa_move)
        else:
            print("無効な指し手です")     
                    
def main():
    check_loop()
        

if __name__ == "__main__":
    main()