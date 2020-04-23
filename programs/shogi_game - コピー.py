# -*- coding: utf-8 -*-
import copy
import enum

class PieceName(enum.Enum):
    ou = "王"
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
    def __init__(self, name_, point_, owner_):
        self.ID = PieceID[name_]
        self.point = point_
        self.owner = owner_
        self.is_promote = False
        self.movavle_point = []
        
    def move(self, point_after_):
        self.point = point_after_
        
    def name(self):
        return PieceID(self.ID).name
    
    def promote(self):
        self.ID = self.ID * -1
        
    def status(self):
        print("name : {}".format(self.name()))
        print("point : {}".format(self.point))
        print("owner : {}".format(self.owner))
        print("movable point : {}".format(self.movavle_point))
        
class ShogiGame():
    def __init__(self, sente_ = True):
        self.sente = sente_
        self.turn = sente_
        self.is_checkmate = False
        self.winner = ""
        # 持ち駒を表す配列[[名前の配列][駒数の配列]]
        self.possession_piece_true = []
        self.possession_piece_false = []
        self.piece_all = self.initialize_piece()

    def proceed_turn(self, index_before_, point_after_, is_promote_):
        # 駒の移動
        piece_all_before = copy.deepcopy(self.piece_all)
        piece_all_after = copy.deepcopy(piece_all_before)       
        piece_all_after = self.move_piece(piece_all_before, index_before_, point_after_, is_promote_)

        # 持ち駒の整理
        self.possession_piece_true, self.possession_piece_false = self.arrange_possession_piece(piece_all_after)
        
        # 移動可能位置の更新
        self.turn = not(self.turn)
        turn_tmp = copy.deepcopy(self.turn)               
        movavle_point_all_piece = self.get_movable_point(piece_all_after, turn_tmp)       
        for i in range(len(movavle_point_all_piece)):
            piece_all_after[i][3] = movavle_point_all_piece[i]
        piece_all_after = self.remove_prohibited_move(piece_all_after, turn_tmp)
        
        # 詰みの判定
        is_checkmate = True
        for piece in piece_all_after:
            if len(piece[3]) != 0:
                is_checkmate = False
                break
        if is_checkmate == True:
            self.is_checkmate = True
            if (self.sente == True) and (self.turn == True):
                self.winner = "後手(False)"
            elif (self.sente == True) and (self.turn == False):
                self.winner = "先手(True)"
            elif (self.sente == False) and (self.turn == True):
                self.winner = "先手(False)"
            elif (self.sente == False) and (self.turn == False):
                self.winner = "後手(True)"
        self.piece_all = piece_all_after
        
    def initialize_piece(self):
        # [名前, [位置], どちらの駒か, [動ける場所, promote_condition]
        # 例えば["kei", [5,5], True, [[4,3,0], [6,3,0]]]
        # なら現在True側の桂が5五にいて移動可能位置が4三桂成り、4三桂成らず、6三桂成り、6三桂成らず
        # [0, 0]はTrue側の持ち駒、[10, 0]はFalse側の持ち駒を表す
        pieces = []
        pieces.append(["gyoku", [5,1], False, []])
        pieces.append(["hu", [1,3], False, []])
        pieces.append(["hu", [2,3], False, []])
        pieces.append(["hu", [3,3], False, []])
        pieces.append(["hu", [4,3], False, []])
        pieces.append(["hu", [5,3], False, []])
        pieces.append(["hu", [6,3], False, []])
        pieces.append(["hu", [7,3], False, []])
        pieces.append(["hu", [8,3], False, []])
        pieces.append(["hu", [9,3], False, []])
        pieces.append(["kyo", [1,1], False, []])
        pieces.append(["kyo", [9,1], False, []])
        pieces.append(["kei", [2,1], False, []])
        pieces.append(["kei", [8,1], False, []])
        pieces.append(["gin", [3,1], False, []])
        pieces.append(["gin", [7,1], False, []])
        pieces.append(["kin", [6,1], False, []])
        pieces.append(["kin", [4,1], False, []])        
        pieces.append(["hisya", [8,2], False, []])
        pieces.append(["kaku", [2,2], False, []])

        pieces.append(["ou", [5,9], True, []])
        pieces.append(["hu", [1,7], True, []])
        pieces.append(["hu", [2,7], True, []])
        pieces.append(["hu", [3,7], True, []])
        pieces.append(["hu", [4,7], True, []])
        pieces.append(["hu", [5,7], True, []])
        pieces.append(["hu", [6,7], True, []])
        pieces.append(["hu", [7,7], True, []])
        pieces.append(["hu", [8,7], True, []])
        pieces.append(["hu", [9,7], True, []])
        pieces.append(["kyo", [1,9], True, []])
        pieces.append(["kyo", [9,9], True, []])
        pieces.append(["kei", [2,9], True, []])
        pieces.append(["kei", [8,9], True, []])
        pieces.append(["gin", [3,9], True, []])
        pieces.append(["gin", [7,9], True, []])
        pieces.append(["kin", [6,9], True, []])
        pieces.append(["kin", [4,9], True, []])        
        pieces.append(["hisya", [2,8], True, []])
        pieces.append(["kaku", [8,8], True, []])        
        movavle_point_all_piece = self.get_movable_point(pieces, self.turn)
        for i in range(len(movavle_point_all_piece)):
            pieces[i][3] = movavle_point_all_piece[i]  
        
        possession_piece_name = ["hu", "kyo", "kei", "gin", "kin", "hisya", "kaku"]
        self.possession_piece_true.append(possession_piece_name)
        self.possession_piece_true.append([0] * 7)
        self.possession_piece_false.append(possession_piece_name)
        self.possession_piece_false.append([0] * 7)               
        return pieces

    def get_movable_point(self, piece_all_, turn_):
        movavle_point_all_piece = []
        gold_pieces = ["kin", "narikyo", "narikei", "narigin", "to"]        
        
        for i in range(len(piece_all_)):
            piece = piece_all_[i]
            reachable_point = []            # 盤面のサイズや移動先のマスの状態を考慮しない移動可能なマス
            movavle_point = []              # 盤面のサイズや移動先のマスの状態を考慮した移動可能なマス
            
            if turn_ == piece[2]:           # 手番側のコマかを判定                
                if piece[1][1] != 0:        # 持ち駒ではない場合                    
                    if piece[0] == "hu":    # 歩
                        x = piece[1][0]
                        if piece[2] == True:    
                            y = piece[1][1] - 1
                        else:
                            y = piece[1][1] + 1 
                        reachable_point.append([x, y])
                    
                    elif piece[0] == "kyo":   # 香
                        count = 1
                        x = piece[1][0]
                        while True:                            
                            if piece[2] == True:    
                                y = piece[1][1] - count
                            else:
                                y = piece[1][1] + count
                            state = self.get_square_state(piece_all_, [x, y])
                            if state == -1:
                                reachable_point.append([x,y])
                                count += 1
                            elif state == turn_ or state == -2:
                                break
                            elif state != turn_:
                                reachable_point.append([x,y])
                                break
                    
                    elif piece[0] == "kei":   # 桂
                        x = piece[1][0] - 1
                        if piece[2] == True:    
                            y = piece[1][1] - 2
                        else:
                            y = piece[1][1] + 2 
                        reachable_point.append([x, y])
                        
                        x = piece[1][0] + 1
                        reachable_point.append([x, y])
                    
                    elif piece[0] == "gin":   # 銀
                        # 前
                        x = piece[1][0]
                        if piece[2] == True:    
                            y = piece[1][1] - 1
                        else:
                            y = piece[1][1] + 1 
                        reachable_point.append([x, y])
                        
                        # 斜め
                        x = piece[1][0] - 1
                        y = piece[1][1] - 1
                        reachable_point.append([x, y])
                        y = piece[1][1] + 1
                        reachable_point.append([x, y])
                        
                        x = piece[1][0] + 1
                        y = piece[1][1] - 1
                        reachable_point.append([x, y])
                        y = piece[1][1] + 1
                        reachable_point.append([x, y])                    
                        
                    elif piece[0] in gold_pieces: # 金
                        # 前と斜め前
                        if piece[2] == True:    
                            y = piece[1][1] - 1
                        else:
                            y = piece[1][1] + 1 
                        x = piece[1][0]
                        reachable_point.append([x, y])
                        x = piece[1][0] - 1
                        reachable_point.append([x, y])                    
                        x = piece[1][0] + 1
                        reachable_point.append([x, y])    
                        
                        # 後ろ
                        if piece[2] == True:    
                            y = piece[1][1] + 1
                        else:
                            y = piece[1][1] - 1 
                        x = piece[1][0]
                        reachable_point.append([x, y])                    
                        
                        # 横
                        y = piece[1][1]
                        x = piece[1][0] + 1
                        reachable_point.append([x, y])
                        x = piece[1][0] - 1
                        reachable_point.append([x, y])
                                             
                    elif piece[0] == "ou" or piece[0] == "gyoku":     # 王と玉
                        x = piece[1][0]
                        y = piece[1][1] - 1
                        reachable_point.append([x, y])                    
                        y = piece[1][1] + 1
                        reachable_point.append([x, y])                  
                        x = piece[1][0] + 1
                        y = piece[1][1]
                        reachable_point.append([x, y]) 
                        y = piece[1][1] - 1
                        reachable_point.append([x, y])                    
                        y = piece[1][1] + 1
                        reachable_point.append([x, y])      
                        x = piece[1][0] - 1
                        y = piece[1][1]
                        reachable_point.append([x, y]) 
                        y = piece[1][1] - 1
                        reachable_point.append([x, y])                    
                        y = piece[1][1] + 1
                        reachable_point.append([x, y])    
                    
                    elif piece[0] == "hisya" or piece[0] == "ryu":   # 飛車と龍
                        if piece[0] == "ryu":                 
                            x = piece[1][0] + 1
                            y = piece[1][1] - 1
                            reachable_point.append([x, y])                    
                            y = piece[1][1] + 1
                            reachable_point.append([x, y])      
                            x = piece[1][0] - 1
                            y = piece[1][1] - 1
                            reachable_point.append([x, y])                    
                            y = piece[1][1] + 1
                            reachable_point.append([x, y]) 
                        
                        count = 1
                        while True:
                            x = piece[1][0]   
                            y = piece[1][1] + count
                            state = self.get_square_state(piece_all_, [x, y])
                            if state == -1:
                                reachable_point.append([x,y])
                                count += 1
                            elif state == turn_ or state == -2:
                                break
                            elif state != turn_:
                                reachable_point.append([x,y])
                                break
                            
                        count = 1
                        while True:
                            x = piece[1][0]   
                            y = piece[1][1] - count
                            state = self.get_square_state(piece_all_, [x, y])
                            if state == -1:
                                reachable_point.append([x,y])
                                count += 1
                            elif state == turn_ or state == -2:
                                break
                            elif state != turn_:
                                reachable_point.append([x,y])
                                break  
                            
                        count = 1
                        while True:
                            x = piece[1][0] + count   
                            y = piece[1][1]
                            state = self.get_square_state(piece_all_, [x, y])
                            if state == -1:
                                reachable_point.append([x,y])
                                count += 1
                            elif state == turn_ or state == -2:
                                break
                            elif state != turn_:
                                reachable_point.append([x,y])
                                break                
                        count = 1
                        while True:
                            x = piece[1][0] - count 
                            y = piece[1][1]
                            state = self.get_square_state(piece_all_, [x, y])
                            if state == -1:
                                reachable_point.append([x,y])
                                count += 1
                            elif state == turn_ or state == -2:
                                break
                            elif state != turn_:
                                reachable_point.append([x,y])
                                break  
                            
                    elif piece[0] == "kaku" or piece[0] == "uma":   # 角と馬
                        if piece[0] == "uma":                 
                            x = piece[1][0] + 1
                            y = piece[1][1]
                            reachable_point.append([x, y])
                            x = piece[1][0] - 1
                            reachable_point.append([x, y])
                            x = piece[1][0]
                            y = piece[1][1] + 1
                            reachable_point.append([x, y])      
                            x = piece[1][0]
                            y = piece[1][1] - 1
                            reachable_point.append([x, y])  
                        
                        count = 1
                        while True:
                            x = piece[1][0] + count 
                            y = piece[1][1] + count
                            state = self.get_square_state(piece_all_, [x, y])
                            if state == -1:
                                reachable_point.append([x,y])
                                count += 1
                            elif state == turn_:
                                break
                            elif state != turn_:
                                reachable_point.append([x,y])
                                break
                            
                        count = 1
                        while True:
                            x = piece[1][0] + count   
                            y = piece[1][1] - count
                            state = self.get_square_state(piece_all_, [x, y])
                            if state == -1:
                                reachable_point.append([x,y])
                                count += 1
                            elif state == turn_:
                                break
                            elif state != turn_:
                                reachable_point.append([x,y])
                                break  
    
                        count = 1
                        while True:
                            x = piece[1][0] - count   
                            y = piece[1][1] - count
                            state = self.get_square_state(piece_all_, [x, y])
                            if state == -1:
                                reachable_point.append([x,y])
                                count += 1
                            elif state == turn_:
                                break
                            elif state != turn_:
                                reachable_point.append([x,y])
                                break 
                            
                        count = 1
                        while True:
                            x = piece[1][0] - count 
                            y = piece[1][1] + count
                            state = self.get_square_state(piece_all_, [x, y])
                            if state == -1:
                                reachable_point.append([x,y])
                                count += 1
                            elif state == turn_:
                                break
                            elif state != turn_:
                                reachable_point.append([x,y])
                                break  

                    for point in reachable_point:    
                        if (point[0] >= 1) and (point[0] <= 9) and (point[1] >= 1) and (point[1] <= 9):
                            square_state = self.get_square_state(piece_all_, point)
                            if square_state != turn_:
                                promote_condition = self.check_is_able_promote(turn_, piece[0], piece[1], point)
                                point.append(promote_condition)
                                movavle_point.append(point)                                                                        

                else:                       # 持ち駒の場合
                    if piece[0] == "hu" or piece[0] == "kyo":    # 歩か香
                        if piece[2] == True:
                            for x in range(1, 10):
                                for y in range(2, 10):
                                    reachable_point.append([x, y])
                        elif piece[2] == False:
                            for x in range(1, 10):
                                for y in range(1, 9):
                                    reachable_point.append([x, y])
                                    
                    elif piece[0] == "kei":                       # 桂
                        if piece[2] == True:
                            for x in range(1, 10):
                                for y in range(3, 10):
                                    reachable_point.append([x, y])                    
                        elif piece[2] == False:
                            for x in range(1, 10):
                                for y in range(1, 8):
                                    reachable_point.append([x, y])

                    elif piece[0] in ["gin", "kin", "hisya", "kaku"]:     # 金銀飛車角
                        for x in range(1, 10):
                            for y in range(1, 10):
                                reachable_point.append([x, y])                    
                    
                    for point in reachable_point:    
                        if self.get_square_state(piece_all_, point) == -1:
                            point.append(-1)
                            movavle_point.append(point)
                
            movavle_point = list(map(list, set(map(tuple, movavle_point))))       # 重複を削除
            movavle_point_all_piece.append(movavle_point)
        return movavle_point_all_piece      

    def remove_prohibited_move(self, piece_all_, turn_):
        # 王手放置を除去
        piece_all_consider_check = copy.deepcopy(piece_all_)
        for i in range(len(piece_all_)):
            movavle_point_consider_check = []
            for point_after in piece_all_[i][3]:                
                piece_all_tmp = copy.deepcopy(piece_all_)
                piece_all_tmp = self.move_piece(piece_all_tmp, i, point_after, False)     
                if self.is_check(piece_all_tmp, not(turn_)) == False:
                    movavle_point_consider_check.append(point_after)
            piece_all_consider_check[i][3] = movavle_point_consider_check
        
        # 二歩を除去
        piece_all_consider_nihu = copy.deepcopy(piece_all_consider_check)
        line_exist_owners_hu = []        
        for piece in piece_all_:
            if (piece[0] == "hu") and (piece[1][1] != 0) and (piece[2] == turn_):
                line_exist_owners_hu.append(piece[1][0])
        for i in range(len(piece_all_consider_check)):
            if (piece_all_consider_check[i][0] == "hu") and (piece_all_consider_check[i][1][1] == 0):
                movavle_point_consider_nihu = []
                for point_after in piece_all_consider_check[i][3]:                     
                    if point_after[0] not in line_exist_owners_hu:
                        movavle_point_consider_nihu.append(point_after)
                piece_all_consider_nihu[i][3] = movavle_point_consider_nihu
        return piece_all_consider_nihu
        
    def arrange_possession_piece(self, piece_all_):
        possession_piece_true_tmp = copy.deepcopy(self.possession_piece_true)
        possession_piece_false_tmp = copy.deepcopy(self.possession_piece_false)
        for i in range(len(possession_piece_true_tmp[1])):
            possession_piece_true_tmp[1][i] = 0
            possession_piece_false_tmp[1][i] = 0
            
        for i in range(len(piece_all_)):
            if piece_all_[i][1] == [0, 0]:
                name = piece_all_[i][0]
                index = possession_piece_true_tmp[0].index(name)
                possession_piece_true_tmp[1][index] += 1
            elif piece_all_[i][1] == [10, 0]:
                name = piece_all_[i][0]
                index = possession_piece_false_tmp[0].index(name)
                possession_piece_false_tmp[1][index] += 1
        return possession_piece_true_tmp, possession_piece_false_tmp

    def is_check(self, piece_all_, turn_):
        if turn_ == True:
            index_king = 0
        elif turn_ == False:
            index_king = 20
        movavle_point_all_piece = self.get_movable_point(piece_all_, turn_)
        for movavle_point_one_piece in movavle_point_all_piece:
            for movavle_point in movavle_point_one_piece:
                if movavle_point[:2] == piece_all_[index_king][1]:
                    return True
        return False
        
    def move_piece(self, piece_all_, index_before_, point_after_, is_promote_):
        normal_piece = ["hu", "kyo", "kei", "gin", "hisya", "kaku"]
        promoted_piece = ["to", "narikyo", "narikei", "narigin", "ryu", "uma"]
        point_after_ = point_after_[:2]
        index_point_after = self.get_piece_index(piece_all_, point_after_)
        state_point_after = self.get_square_state(piece_all_, point_after_)
        turn = piece_all_[index_before_][2]
        
        # 駒の移動と成り
        piece_all_[index_before_][1] = point_after_[:2]
        if is_promote_ == True:
            name_before = piece_all_[index_before_][0]
            name_after = promoted_piece[normal_piece.index(name_before)]
            piece_all_[index_before_][0] = name_after
        
        # 相手駒の取得
        if state_point_after == (not turn):
            if piece_all_[index_point_after][0] in promoted_piece:
                name_before = piece_all_[index_point_after][0]
                name_after = normal_piece[promoted_piece.index(name_before)]
                piece_all_[index_point_after][0] = name_after             
            if turn == True:
                piece_all_[index_point_after][1] = [0, 0]
                piece_all_[index_point_after][2] = True
            elif turn == False:
                piece_all_[index_point_after][1] = [10, 0]
                piece_all_[index_point_after][2] = False
        return piece_all_

    def check_is_able_promote(self, turn_, name_, point_before_, point_after_):
        # 成る条件を満たしていない場合-1を返す
        # 成るか確認が必要な場合は0を返す
        # 成るしかないときは1を返す
        
        # 持ち駒の場合
        if point_before_[1] == 0:
            return -1
        
        # 盤面上の駒の場合        
        promote_condition = -1
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
        for i in range(len(piece_all_)):
            if piece_all_[i][1] == point_:
                index = i
        return index

    def get_square_state(self, piece_all_, point_):
        # 盤面外なら-2,空なら-1,駒があるならどちらの駒かをTrueかFalseで返す
        if min(point_) <= 0 or max(point_) >= 10:
            return -2
        point_index = self.get_piece_index(piece_all_, point_)
        if point_index == -1:
            return -1
        else:
            return piece_all_[point_index][2]
        
        
        
        
def main():
    hu = Piece("hu", [1, 1], True)
    hu.status()
    hu.promote()
    hu.status()
    
    

if __name__ == "__main__":
    main()