import numpy as np
import chainer
from chainer import cuda, Function, gradient_check, report, training, utils, Variable
from chainer import datasets, iterators, optimizers, serializers
from chainer import Link, Chain, ChainList
import chainer.functions as F
import chainer.links as L
import random

from othello import othello ,show
import time
import copy

class thinker(Chain):
    def __init__(self):
        super(thinker,self).__init__(

            l1=L.Linear(192,64),
            l2=L.Linear(64,16),
            l3=L.Linear(16,1),
            


            )
    def __call__(self,x):
        x=x.reshape(1,1,192).astype(np.float32)
        x_l1=F.sigmoid(self.l1(x))
        x_l2=F.sigmoid(self.l2(x_l1))
        x_l3=F.sigmoid(self.l3(x_l2))
        return  x_l3
class AI():
    def __init__(self,turn):
        self.thinker=thinker()
        self.turn=turn
        self.log=[]
    def think(self,o):
        puts=o.search_legal_puts()
        put=max(puts,key=lambda x: 1-self.thinker(x["board_onehot"]).data)
        score=self.thinker(put["board_onehot"]).data
        self.log.append([put["board_onehot"],score])
        return [put["x"],put["y"],score]

class Randomer():
    def __init__(self,turn):
        self.turn=turn
    def think(self,o):
        puts=o.search_legal_puts()
        put=random.choice(puts)
        return [put["x"],put["y"],77777]

class Positioner():
    def __init__(self,turn):
        self.turn=turn
    def think(self,o):
        puts=o.search_legal_puts()
        res={"score":-64}
        for put in puts:
            moved_data=put["raw"]
            turned_moved_data=copy.deepcopy(moved_data)
            turned_moved_data.turn*=-1
            legal_puts=len(moved_data.search_legal_puts())
            turned_legal_puts=len(turned_moved_data.search_legal_puts())
            score=legal_puts-turned_legal_puts
            print(score)
            if legal_puts==0 and turned_legal_puts==0:
                if self.turn==moved_data.W:
                    score=moved_data.count_W-moved_data.count_B
                else:
                    score=moved_data.count_B-moved_data.count_W
            if score>res["score"]:
                res={"x":put["x"],"y":put["y"],"score":score}



        return [res["x"],res["y"],res["score"]]

class Idioter():
    def __init__(self,turn):
        self.turn=turn
    def think(self,o):
        puts=o.search_legal_puts()
        put=puts[-1]
        #if random.randint(1,10)==1:
        #    put=random.choice(puts)

        return [put["x"],put["y"],77777]

def train(AI,data,sample_rate=0.8,win=True):
    def lossfun(model,d,t):
        loss=F.mean_squared_error(model(d),t)
        return loss
    
    opt=optimizers.SGD()
    opt.setup(AI.thinker)
    data=random.sample(data,int(len(data)*sample_rate))
    for log in data:
        for i in range(10):
            if win:
                opt.update(lossfun,AI.thinker,log[0],Variable(log[1]*1.2))
            else:
                opt.update(lossfun,AI.thinker,log[0],Variable(log[1]*0.8))
    
def acc(AI,name):
    win=0
    joe=Randomer(AI.turn*-1)
    for i in range(10): 
        game=othello(random.choice([-1,1]))
        while True:
            status=game.status()
            if status==2:
                break
            if status==1:
                game.turn*=-1
                continue
            if game.turn==AI.turn:
                res=AI.think(game)
                game.put(res[0],res[1])
            elif game.turn==joe.turn:
                res=joe.think(game)
                game.put(res[0],res[1])

        winner_turn=game.winner()
        if winner_turn==AI.turn:
            win+=1
    print(name+":"+str(float(win)/10))
        

def epoch():
    alice=AI(random.choice([1]))
    bob=Idioter(alice.turn*-1)
    winlog_bob=[]
    winlog_alice=[]

    for i in range(50): 
        game=othello(random.choice([1]))
        alice.log=[]
        bob.log=[]
        start=time.time()
        while True:
            status=game.status()
            if status==2:
                break
            if status==1:
                game.turn*=-1
                continue
            if game.turn==alice.turn:
                res=alice.think(game)
                res[2]=float(res[2])
                #print ("alice:"+str(res))
                game.put(res[0],res[1])
            elif game.turn==bob.turn:
                res=bob.think(game)
                res[2]=float(res[2])
                #print ("bob  :"+str(res))
                game.put(res[0],res[1])
        show(game.board)
        winner_turn=game.winner()
        if winner_turn==alice.turn:
            print("winner:alice")
            train(alice,alice.log,0.5+(abs(game.count_W-game.count_B)/64)/20,True)
        elif winner_turn==bob.turn:
            print("winner:bob")
            train(alice,alice.log,0.5+(abs(game.count_W-game.count_B)/64)/20,False)
        else:
            print("draw")
        
    acc(alice,"alice")
#    acc(bob,"bob")

if __name__ == '__main__':
    while True:
        epoch()