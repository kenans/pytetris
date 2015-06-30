#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import time
import random
import threading

import getkey
import drawhandler

from game_modules import *
from game_views import *

class Game(object):
    def __init__(self):
        self.__start = False
        self.__pause = False
    def game_start(self):
        self.__start = True
    def game_end(self):
        self.__start = False
    def game_pause(self):
        self.__pause = True
    def started(self):
        return self.__start

class GameTeris(Game):
    def __init__(self):
        self.current_block = Block()
        self.m = GameMap(12, 20)
        self.b = Block()
        threading.Thread(target = self.key_thread).start()
        threading.Thread(target = self.display_thread).start()
    def main_thread(self):
        global score
        over = False
        while not over:
            i = random.randint(0, len(BlockTool.PICS) - 1)
            self.b.reinit(block_id = i, x = 5, y = 17)
            if self.at_bottom():
                over = True
            while True:
                time.sleep(0.5)
                if self.at_bottom():
                    self.m.attach_block(self.b)
                    count = self.m.refresh_lines()
                    if count is -1:
                        over = True
                    elif count is not 0:
                        score += 2 * count - 1
                    break
                else:
                    self.b.drop()
        global end
        end = True
    def key_thread(self):
        getch = getkey.Getch()
        global end
        while not end:#self.start == True:
            key = None
            c = getch()
            if end:
                break
            #print 'pressed:', c
            if c == 'w' and self.can_rotate():
                self.b.rotate()
            elif c == 'd' and not self.at_right():
                self.b.move(RIGHT)
            elif c == 'a' and not self.at_left():
                self.b.move(LEFT)
            elif c == 's' and not self.at_bottom():
                self.b.move(DOWN)
            time.sleep(0.1)
    def display_thread(self):
        game_paint = GamePaint(
                drawhandler.ConsolePaintHandler(
                    self.m.x_max, self.m.x_min, self.m.y_max, self.m.y_min))
        global end, score
        while not end:
            game_paint.repaint()
            game_paint.draw_map(self.m)
            game_paint.draw_block(self.b)
            game_paint.paint()
            game_paint.print_score(score)
            time.sleep(0.05)
        game_paint.repaint()
        print '\nGame Over'
        print 'final score:', score
        print 'highest score:', get_score()
        if get_score() < score:
            log_score(score)
        print 'press Enter to exit...'
    def at_bottom(self):
        for point in self.b.pic:
            if self.m.buf(self.b.x + point[0], self.b.y + point[1] - 1) is not 0:
                return True
        return False
    def at_left(self):
        for point in self.b.pic:
            if self.m.buf(self.b.x + point[0] - 1, self.b.y + point[1]) is not 0:
                return True
        return False
    def at_right(self):
        for point in self.b.pic:
            if self.m.buf(self.b.x + point[0] + 1, self.b.y + point[1]) is not 0:
                return True
        return False
    def can_rotate(self):
        rotated_pic = BlockTool.rotate_pic(self.b.pic)
        for point in rotated_pic:
            if self.m.buf(self.b.x + point[0], self.b.y + point[1]) is not 0:
                return False
        return True

end = False
score = 0
def get_score():
    try:
        with open("log", "rU") as f:
            lines = f.readlines()
            if lines != []:
                return int(lines[0])
            else:
                return 0
    except:
        return 0
def log_score(score):
    with open("log", "w") as f:
        f.write(str(score))

if __name__ == '__main__':
    game = GameTeris()
    game.main_thread()
