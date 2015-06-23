#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import os
import drawhandler
import getkey
import threading

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

class BlockLoader(object):
    def __init__(self):
        self.pics = {}
    def load(self):
        path = os.path.join('..', 'resource')
        f_list = os.listdir(path)
        for f_name in f_list:
            f_path = os.path.join(path, f_name)
            with open(f_path, 'r') as f:
                self.pics[f_name] = [line.strip('\r\n') for line in f.readlines()]
        return self.pics
    def load2(self):
        path = os.path.join('..', 'resource')
        f_list = os.listdir(path)
        for f_name in f_list:
            f_path = os.path.join(path, f_name)
            with open(f_path, 'r') as f:
                key = f_name.split('_')[0]
                if not self.pics.has_key(key):
                    self.pics[key] = []
                item = [line.strip('\r\n') for line in f.readlines()]
                self.pics[key].append(item)
        return self.pics

class Block(object):
    def __init__(self):
        self.block_id = 1
        self.face_direction = 1 # 1, 2, 3, 4
        self.speed = 1
        self.x = 0
        self.y = 0
    def reinit(self, x = 0, y = 0):
        pass
    def drop(self):
        self.y -= self.speed
    def move(self, direction):
        if direction is DOWN:
            self.y -= self.speed
        elif direction is LEFT:
            self.x -= self.speed
        elif direction is RIGHT:
            self.x += self.speed
    def rotate(self, clockwise = True):
        if clockwise:
            self.face_direction += 1
        else:
            self.face_direction -= 1
        if self.face_direction == 5:
            self.face_direction = 1
        elif self.face_direction == 0:
            self.face_direction = 4

class GameMap(object):
    def __init__(self):
        self.x_min = 0
        self.x_max = 25
        self.y_min = 0
        self.y_max = 30
    def full_line(self):
        pass
    def clear_full_lines(self):
        pass

class GamePaint(object):
    def __init__(self, handler = drawhandler.ConsolePaintHandler()):
        self.handler = handler
        #self.pics = BlockLoader().load()
        self.pics = BlockLoader().load2()
    def draw_block(self, b):
        #pic = self.pics[str(b.block_id) + '_' + str(b.face_direction)]
        pic = self.pics[str(b.block_id)][0]
        self.handler.draw_pic(pic, b.x, b.y)    
    def draw_map(self, m):
        # p11        p12
        #
        # p22        p21
        p11 = [m.x_min, m.y_max]
        p12 = [m.x_max, m.y_max]
        p21 = [m.x_max, m.y_min]
        p22 = [m.x_min, m.y_min]
        self.handler.draw_line(p11, p12)
        self.handler.draw_line(p12, p21)
        self.handler.draw_line(p21, p22)
        self.handler.draw_line(p11, p22)
    def repaint(self):
        self.handler.clear_buf()
    def paint(self):
        self.handler.paint()

class Game(object):
    def __init__(self):
        pass
    def game_start(self):
        pass
    def game_pause(self):
        pass
class GameTeris(Game):
    def __init__(self):
        self.current_block = Block()
    def main_thread(self):
        while self.start:
            # Should drop ?
            if self.__block_drop(self.current_block):
                self.current_block.drop()
            # Move & Rotate
            key = GetKey()
            self.current_block.move(key)
            self.current_block.rotate(key)
            # Current block dead ?
            if self.__block_dead(self.current_block):
                # Game over ?
                if self.__game_over(self):
                    pass
                # At least full line ?
                if self.game_map.full_line():
                    self.game_map.clear_full_lines()
                self.current_block.init()
            # Delay
            time.sleep(1.0)
    def key_thread(self, block):
        getch = getkey.Getch()
        while True:#self.start == True:
            key = None
            c = getch()
            if c == 'w':
                block.rotate()
            elif c == 'd':
                block.move(RIGHT)
            elif c == 'a':
                block.move(LEFT)
            elif c == 's':
                block.move(DOWN)
            time.sleep(100)
    def __game_over(self):
        pass
    def __block_dead(self, block):
        pass
    def __block_drop(self, block):
        # Should return True periodically, like every 1s
        pass

def main():
    handler = drawhandler.ConsolePaintHandler()
    game_paint = GamePaint(handler)
    m = GameMap()
    b = Block()
    b.block_id = 1
    b.face_direction = 1
    b.x = 10
    b.y = 15
    #threading.Thread(target = GameTeris().key_thread, args = (b)).start()
    for i in range(6):
        game_paint.repaint()
        game_paint.draw_map(m)
        game_paint.draw_block(b)
        game_paint.paint()
        b.rotate()
        b.drop()
        time.sleep(1)

if __name__ == '__main__':
    main()
