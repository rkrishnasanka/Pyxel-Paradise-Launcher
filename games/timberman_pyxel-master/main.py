import os
import pyxel
from time import sleep
from collections import deque as Q
import random
def clip(x, lower, upper):
    if(x>upper):
        return upper
    elif(x<lower):
        return lower
    else:
        return x
def sign(x):
    if(x==0):
        return 0
    if(x>0):
        return 1
    if(x<0):
        return -1
class Point:
    def __init__(self, x, y, wrap=False, width=None, height=None):
        self.x = x
        self.y = y
        self.wrap = wrap
        if(wrap):
            self.wrap = wrap
            self.width = width
            self.height = height
    def add(self, a, b):
        if(self.wrap):
            self.x = (self.x + a)%self.width
            self.y = (self.y + b)%self.height
        else:
            self.x += a
            self.y += b

    def tup(self):
        return (self.x, self.y)
    def x(self):
        return self.x
    def y(self):
        return self.y

class Game:
    
    def reset(self):
        self.gameover = False
        self.dir = -1
        self.alternator = 1
        self.time = 0
        self.score = 0
        self.man_loc = Point(50,150) 
        self.logs = Q()
        self.prob_straight = 0.4
        self.prob_left = 0.5
        self.highscore_file = './hs'
        for i in range(13):
            self.spawn_log()
        self.decay = 0.99 
        self.health = 100
    def __init__(self):
        self.WIDTH = 200
        self.HEIGHT = 200
        self.reset()
        pyxel.init(self.WIDTH, self.HEIGHT, caption='TimberMan', scale = 10)
        pyxel.load('./res.pyxel')
        pyxel.run(self.update, self.draw)    
        sleep(10)
    def alternate(self):
        if(self.alternator < 0):
            self.alternator+= 1

    def game_over(self):
        pyxel.play(0, 0)
        self.gameover = -70
    def spawn_log(self):
        #Probability of spawning a striaght log(decrease as difficulty increases)
        if(random.uniform(0,1) < self.prob_straight):
            #Spawn a straight log
            self.logs.appendleft(0)
        else:
            if random.uniform(0,1) < self.prob_left:
                #Spawn left log
                self.logs.appendleft(-1)

            else:
                #Spawn right log
                self.logs.appendleft(1)

    def handle_keys(self):
        ANIM_TIME = 4
        pyxel.sound(1).speed = 6
        if(self.alternator < 0):
            return 
        if pyxel.btn(pyxel.KEY_RIGHT):
            chopped = self.logs.pop()
            self.dir = 1
            if(self.dir == chopped):
                #Crash - Game Over
                print('Game over a right log fell on your head')
                self.game_over()
            else:
                self.health = min(100, self.health + 20)
                self.score += 1
                self.decay = max(0.8, self.decay  - 0.002)
                pyxel.play(0, 1)
                self.spawn_log()
            
            self.alternator = -1 * ANIM_TIME
        elif pyxel.btn(pyxel.KEY_LEFT):
            chopped = self.logs.pop()
            self.dir = -1
            if(self.dir == chopped):
                #Crash - Game Over
                print('Game over left log fell on your head')
                self.game_over()
            else:
                self.health = min(100, self.health + 20)
                self.score += 1
                pyxel.play(0, 1)
                self.spawn_log()
            self.alternator = -1 * ANIM_TIME
        else:
            return
        print('Chopped :'+str(chopped))
    def get_highscore(self):
        if(os.path.exists(self.highscore_file)):
            with open(self.highscore_file, 'r') as f:
                return int(f.read())
        else:
            open(self.highscore_file,'w')
            return -1
    def set_highscore(self):
        if(os.path.exists(self.highscore_file)):
            with open(self.highscore_file, 'w') as f:
                f.write(str(self.score))

    def update(self):
        self.handle_keys()
        self.time+= 1
        self.health = int(self.health*self.decay)
        if(self.gameover == -1):
            if(self.score > self.get_highscore()):
                self.set_highscore()
            pyxel.quit()
        if(self.health  == 0):
            print('Game over low health')
            if(self.score > self.get_highscore()):
                self.set_highscore()
            exit()
        
    def get_health_color(self):
        if(self.health in range(0, 20)):
                return 8
        if(self.health in range(20, 40)):
                return 9
        if(self.health in range(40, 70)):
                return 10
        if(self.health in range(70, 101)):
                return 11
        
    def draw(self):
        pyxel.cls(col=0)
        LOC_LOG_STRAIGHT = (8,32, 48, 16)
        LOC_LOG_LEFT = (8, 16, 48, 16)
        LOC_LOG_RIGHT = (8, 0, 48, 16)
        LOC_STUMP = (8, 48, 48, 8)
        LOC_MAN_LEFT = ( 11, 51, -36, 55)
        LOC_MAN_CHOP_LEFT = ( 64, 51, -55, 47)
        LOC_MAN_RIGHT = ( 11, 51, 36, 55)
        LOC_MAN_CHOP_RIGHT = ( 64, 51, 55, 47)
        LOC_MAN_HURT_RIGHT = ( 64, 112, 55, 47)
        LOC_MAN_HURT_LEFT = ( 64, 112, -55, 47)

        STUMP_OFFSET = 30
        #Draw Stump
        start_height = self.HEIGHT - 8
        pyxel.blt(self.man_loc.x + STUMP_OFFSET, start_height, 0,*LOC_STUMP, 0)
        
        #Draw STATIC Straight logs
        for i in range(3):
            start_height -= 16
            #Draw Basic Log
            pyxel.blt(self.man_loc.x + STUMP_OFFSET, start_height, 0,*LOC_LOG_STRAIGHT, 0)

        #Draw Dynamic logs from the stack
        loglist = list(self.logs)
        loglist.reverse()
        for log in loglist:
            start_height -= 16
            if log == 0:
                #Draw Basic Log
                pyxel.blt(self.man_loc.x + STUMP_OFFSET, start_height, 0,*LOC_LOG_STRAIGHT, 0)
            elif log == 1:
                #Draw Right Log
                pyxel.blt(self.man_loc.x + STUMP_OFFSET, start_height, 0,*LOC_LOG_RIGHT, 0)
            else:
                #Draw Left Log
                pyxel.blt(self.man_loc.x + STUMP_OFFSET, start_height, 0,*LOC_LOG_LEFT, 0)

        #Draw the Timberman in his respective state/orientation        

        if(self.gameover < 0):
            #Draw Hurt Timberman
            if(self.dir == -1):
                pyxel.blt(self.man_loc.x+STUMP_OFFSET - 20, self.man_loc.y, 1,*LOC_MAN_HURT_RIGHT, 0)
            else:
                pyxel.blt(self.man_loc.x+STUMP_OFFSET + 10, self.man_loc.y, 1,*LOC_MAN_HURT_LEFT, 0)
            self.gameover += 1
            return
            
        if(self.alternator<0):
            #Draw Chopping Timberman
            if(self.dir == -1):
                pyxel.blt(self.man_loc.x+STUMP_OFFSET - 20, self.man_loc.y, 1,*LOC_MAN_CHOP_RIGHT, 0)
            else:
                pyxel.blt(self.man_loc.x+ STUMP_OFFSET + 10, self.man_loc.y, 1,*LOC_MAN_CHOP_LEFT, 0)
        else:
            #Draw Normal Timberman
            if(self.dir == -1):
                pyxel.blt(self.man_loc.x + STUMP_OFFSET - 20, self.man_loc.y, 1,*LOC_MAN_RIGHT, 0)
            else:
                pyxel.blt(self.man_loc.x+ STUMP_OFFSET + 20, self.man_loc.y, 1,*LOC_MAN_LEFT, 0)
        self.alternate()
        
        #Draw the Health Bar
        pyxel.rect(49,20,150 , 40, 7)
        end = int(self.health) + 49
        col = self.get_health_color()
        pyxel.rect(50,20,end, 40, col)


        #Draw the score on the top left
        pyxel.text(10, 20, 'Score:'+str(self.score), 8)

Game()
