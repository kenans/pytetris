#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import math
import os
import drawhandler
import getkey
import threading


UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

class BlockTool(object):
    PICS = {
            0: [[0, 0], [0, 1], [0, 2], [1, 0]],
            1: [[0, 0], [0, 1], [0, 2], [-1, 0]],
            2: [[0, 0], [0, 1], [1, 0], [-1, 0]],
            3: [[0, 0], [0, 1], [0, 2], [0, -1]],
            4: [[0, 0], [-1, 0], [0, 1], [1, 1]],
            5: [[0, 0], [1, 0], [0, 1], [-1, 1]],
            6: [[0, 0], [0, 1], [1, 0], [1, 1]]
            }
    STATE_COUNT = {
            0: 4,
            1: 4,
            2: 4, 
            3: 2,
            4: 2, 
            5: 2,
            6: 1
            }
    @classmethod
    def load_pic(cls, block_id):
        return sorted(cls.PICS[block_id], key = lambda(x):x[1])
    @classmethod
    def state_count(cls, block_id):
        return cls.STATE_COUNT[block_id]
    @staticmethod
    def rotate_pic(pic, ang = 90, clockwise = True):
        new_pic = []
        for point in pic:
            x = point[0]
            y = point[1]
            new_pic.append([y, -x])
        return sorted(new_pic, key = lambda(x):x[1])
    @staticmethod
    def get_bottom_edge(pic):
        return (item for item in pic if [item[0], item[1] - 1] not in pic)
    @staticmethod
    def get_up_edge(pic):
        return (item for item in pic if [item[0], item[1] + 1] not in pic)
    @staticmethod
    def get_left_edge(pic):
        return (item for item in pic if [item[0] - 1, item[1]] not in pic)
    @staticmethod
    def get_right_edge(pic):
        return (item for item in pic if [item[0] + 1, item[1]] not in pic)
        
class Block(object):
    def __init__(self, block_id = 0, x = 0, y = 0, speed = 1):
        self.block_id = block_id
        self.pic = BlockTool.load_pic(block_id)
        self.state = 0
        self.x = x
        self.y = y
        self.speed = speed
    def reinit(self, x = 0, y = 0):
        pass
    def drop(self):
        self.y -= self.speed
    def move(self, direction = DOWN):
        if direction is DOWN:
            self.y -= self.speed
        elif direction is LEFT:
            self.x -= self.speed
        elif direction is RIGHT:
            self.x += self.speed
    def rotate(self):
        #BlockTool.rotate_pic(self.pic, ang, clockwise)
        self.state += 1
        if self.state is BlockTool.state_count(self.block_id):
            self.pic = BlockTool.load_pic(self.block_id)
            self.state = 0
        else:
            self.pic = BlockTool.rotate_pic(self.pic)

class GameMap(object):
    def __init__(self):
        self.x_min = 0
        self.x_max = 25
        self.y_min = 0
        self.y_max = 30
        self.point_buf = []
        self.point_dic = {}
        self.buf = [[1] + [0] * (self.y_max - self.y_min + 1 - 2) + [1]] * (self.x_max - self.x_min + 1 - 2)
        self.buf.insert(0, [1] * (self.y_max - self.y_min + 1))
        self.buf.append([1] * (self.y_max - self.y_min + 1))
    def full_line(self):
        pass
    def clear_full_lines(self):
        pass
    def attach_block(self, b):
        self.__attach_points(b.pic, b.x, b.y)
    def __attach_points(self, pic, x, y):
        for point in pic:
            self.point_buf.append([point[0] + x, point[1] + y])
            self.buf[point[0]][point[1]] = 2
        self.point_buf.sort(key = lambda(point): point[1])

class GamePaint(object):
    def __init__(self, handler = drawhandler.ConsolePaintHandler()):
        self.handler = handler
    def draw_blocks(self, blocks):
        for block in blocks:
            self.draw_block(block)
    def draw_block(self, b):
        self.handler.draw_points(b.pic, b.x, b.y)
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
        # point_buf
        self.handler.draw_points(m.point_buf, 0, 0)
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
    b = Block(block_id = 0)
    b.x = 1
    b.y = 0
    # game_paint.repaint()
    # game_paint.draw_map(m)
    # game_paint.draw_block(b)
    # game_paint.paint()
    for i in range(len(BlockTool.PICS)):
        b = Block(i)
        b.x = 10
        b.y = 20
        #threading.Thread(target = GameTeris().key_thread, args = (b)).start()
        while True:
            # game_paint.repaint()
            # game_paint.draw_map(m)
            # game_paint.draw_block(b)
            # game_paint.paint()
            # time.sleep(0.5)
            # b.rotate()
            game_paint.repaint()
            game_paint.draw_map(m)
            game_paint.draw_block(b)
            game_paint.paint()
            print m.point_buf
            time.sleep(0.5)
            if at_bottom(b, m):
                m.attach_block(b)
                break
            else:
                b.drop()

def at_bottom(block, m):
    # for point in BlockTool.get_bottom_edge(block.pic):
    #     if [block.x, block.y + point[1] - 1] in BlockTool.get_up_edge(m.point_buf) or \
    #        block.y + point[1] - 1 is 0:
    #         return True
    # return False
    # for point in block.pic:
    #     if [block.x, block.y + point[1] - 1] in m.point_buf or \
    #        block.y + point[1] - 1 is 0:
    #         return True
    # return False
    for point in block.pic:
        if m.buf[block.x + point[0]][block.y + point[1] - 1] is not 0:
            return True
    return False

if __name__ == '__main__':
    main()
