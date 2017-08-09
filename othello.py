#coding:utf-8
import numpy  as np
from pprint import pprint as p
import random
import copy
[ 0,  1,  2,  3,  4,  5,  6,  7,
  8,  9, 10, 11, 12, 13, 14, 15,
 16, 17, 18, 19, 20, 21, 22, 23,
 24, 25, 26, 27, 28, 29, 30, 31, 
 32, 33, 34, 35, 36, 37, 38, 39, 
 40, 41, 42, 43, 44, 45, 46, 47, 
 48, 49, 50, 51, 52, 53, 54, 55, 
 56, 57, 58, 59, 60, 61, 62, 63]

class othello():
    def __init__(self,turn):
        self.B=-1
        self.W=1
        self.N=0
        self.count_B=2
        self.count_W=2
        self.turn=turn
        self.board=np.zeros(64).reshape(8,8)
        self.board[3][3]=self.W
        self.board[3][4]=self.B
        self.board[4][3]=self.B
        self.board[4][4]=self.W
        self.board_onehot=np.zeros(64*3).reshape(3,8,8)
        self.make_onehot()
    def search_legal_puts(self):
        legal_puts=[]
        for x in range(8):
            for y in range(8):
                initial_pos=self.board.copy()
                initial_turn=self.turn
                if self.put(x,y)!=-1:
                    legal_puts.append({"x":x,"y":y,"board_onehot":self.board_onehot,"raw":self})
                self.turn=initial_turn
                self.board=initial_pos
        return legal_puts
    def make_onehot(self):
        W=[]
        N=[]
        B=[]
        for x in range(8):
            for y in range(8):
                if self.board[y][x]==-1:
                    B.append(1)
                    W.append(0)
                    N.append(0)
                elif self.board[y][x]==0:
                    B.append(0)
                    W.append(0)
                    N.append(1)
                elif self.board[y][x]==1:
                    B.append(0)
                    W.append(1)
                    N.append(0)
        self.board_onehot=np.array([B,N,W]).reshape(3,8,8)

    def update_count(self):
        self.count_B=len(np.where(self.board==self.B)[0])
        self.count_W=len(np.where(self.board==self.W)[0])

    def has_no_legal_puts(self):
        if len(self.search_legal_puts())==0:
            return True
        return False
    def winner(self):
        if self.count_B>self.count_W:
            return self.B
        elif self.count_W>self.count_B:
            return self.W
        else:
            return self.N #draw
    def status(self):
        tmp_inst=copy.deepcopy(self)
        if tmp_inst.has_no_legal_puts():
            tmp_inst.turn*=-1
            if tmp_inst.has_no_legal_puts():
                return 2
            else:
                return 1
        return 0
    def put(self,px,py,color=None):
        if color==None:
            color=self.turn

        if self.board[py][px]!=self.N:
            return -1
        
        rev=0
        initial_pos=self.board.copy()
        self.board[py][px]=color

        for x in [-1,0,1]:
            for y in [-1,0,1]:
                old=self.board.copy()
                line_rev=0
                for i in range(1,8):
                    if px+x*i in [-1,8] or py+y*i in [-1,8]:
                        self.board=old
                        line_rev=0
                        break
                    piece=self.board[py+y*i][px+x*i]
                    if piece==color:
                        old=self.board
                        break
                    if piece==self.N:
                        self.board=old
                        line_rev=0
                        break
                    if piece==color*-1:
                        self.board[py+y*i][px+x*i]*=-1
                        line_rev+=1
                rev+=line_rev
        if rev==0:
            self.board=initial_pos
            return -1
        else:
            self.update_count()
            self.make_onehot()
            self.turn*=-1
            return rev


def show(board):
    print("-"*25)
    for _ in board:
        s="|"
        for char in _:
            if char==1:
                s+="● "
            elif char==-1:
                s+="〇"
            else:
                s+="　"
            s+="|"
        print(s) 
        print("-"*25)
    

if __name__ == '__main__':
        
    o=othello(-1)
    mes=""
    while True:
        if o.is_gameset():
            break
        puts=o.search_legal_puts()
        if len(puts)==0:
            mes="passed"
            o.turn*=-1
            continue
        hand=random.choice(puts)
        
        o.put(hand["x"],hand["y"])
        print(o.board_onehot)

        print("\n")
    print(mes)
