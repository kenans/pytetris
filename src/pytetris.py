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
        self.pic_bottom = BlockTool.get_bottom_edge(self.pic)
        self.pic_up = BlockTool.get_up_edge(self.pic)
        self.pic_left = BlockTool.get_left_edge(self.pic)
        self.pic_right = BlockTool.get_right_edge(self.pic)
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
        self.state += 1
        if self.state is BlockTool.state_count(self.block_id):
            self.pic = BlockTool.load_pic(self.block_id)
            self.state = 0
        else:
            self.pic = BlockTool.rotate_pic(self.pic)

class GameMap(object):
    NOTHING = 0
    WALLS   = 1
    BLOCKS  = 2
    def __init__(self):
        self.x_min = 0
        self.x_max = 10
        self.y_min = 0
        self.y_max = 30
        self.__row_count = self.y_max - self.y_min + 1
        self.__col_count = self.x_max - self.x_min + 1
        #self.point_buf = []
        self.__buf = []
        self.__init_buf()
    def is_full_line(self, line_num):
        if self.__buf[line_num][1: -1].count(2) == self.__col_count - 2:
            return True
        return False
    def full_lines(self):
        return (row for row in range(self.__row_count) if self.is_full_line(row))
    def has_full_line(self):
        for row in range(self.__row_count):
            if self.is_full_line(row):
                return True
        return False
    def set_line(self, line_num):
        for col in range(1, self.__col_count - 1):
            self.__buf[line_num][col] = 2
    def clear_line(self, line_num):
        for col in range(1, self.__col_count - 1):
            self.__buf[line_num][col] = 0
    def clear_full_lines(self):
        for line_num in self.full_lines():
            self.clear_line(line_num)
    def attach_block(self, b):
        self.__attach_points(b.pic, b.x, b.y)
    def print_buf(self):
        for line in self.__buf:
            print line
    def buf_at_col(self, col):
        return [line[col] for line in self.__buf]
    def buf_at_row(self, row):
        return self.__buf[row]
    def buf(self, x, y):
        return self.__buf[y][x]
    def buf_size(self):
        return self.__col_count, self.__row_count  # x_max, y_max
    def __attach_points(self, pic, x, y):
        for point in pic:
            self.__buf[point[1] + y][point[0] + x] = 2  # buf[y][x]
            # self.point_buf.append([point[0] + x, point[1] + y])
        #self.point_buf.sort(key = lambda(point): point[1])
    def __init_buf(self):
        self.__buf = [[1] + [0] * (self.__col_count - 2) + [1] for i in range(self.__row_count - 2)]
        self.__buf.insert(0, [1] * (self.__col_count))
        self.__buf.append([1] * (self.__col_count))
        self.test_buf = self.__buf

class GamePaint(object):
    def __init__(self, handler = drawhandler.ConsolePaintHandler()):
        self.handler = handler
    def draw_blocks(self, blocks):
        for block in blocks:
            self.draw_block(block)
    def draw_block(self, b):
        self.handler.draw_points(b.pic, b.x, b.y)
    def draw_map(self, m):
        x_max, y_max = m.buf_size()
        for x in range(x_max):
            for y in range(y_max): 
                if m.buf(x, y) is not 0:
                    self.handler.draw_point([x, y])
        # # p11        p12
        # #
        # # p22        p21
        # p11 = [m.x_min, m.y_max]
        # p12 = [m.x_max, m.y_max]
        # p21 = [m.x_max, m.y_min]
        # p22 = [m.x_min, m.y_min]
        # self.handler.draw_line(p11, p12)
        # self.handler.draw_line(p12, p21)
        # self.handler.draw_line(p21, p22)
        # self.handler.draw_line(p11, p22)
        # # point_buf
        # self.handler.draw_points(m.point_buf, 0, 0)
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

def key_thread(block):
    getch = getkey.Getch()
    while True:#self.start == True:
        key = None
        c = getch()
        #print 'pressed:', c
        if c == 'w':
            block.rotate()
        elif c == 'd':
            block.move(RIGHT)
        elif c == 'a':
            block.move(LEFT)
        elif c == 's':
            block.move(DOWN)
        elif c == 'q':
            break
        time.sleep(0.1)

def get_current_block():
    
    pass

def main():
    handler = drawhandler.ConsolePaintHandler()
    game_paint = GamePaint(handler)
    m = GameMap()
    # game_paint.repaint()
    # game_paint.draw_map(m)
    # game_paint.draw_block(b)
    # game_paint.paint()
    for i in range(len(BlockTool.PICS)):
        b = Block(i)
        b.x = 5
        b.y = 20
        #threading.Thread(target = key_thread, args = (b,)).start()
        while True:
            # game_paint.repaint()
            # game_paint.draw_map(m)
            # game_paint.draw_block(b)
            # game_paint.paint()
            # time.sleep(0.5)
            # b.rotate()
            # -----------------------
            game_paint.repaint()
            game_paint.draw_map(m)
            game_paint.draw_block(b)
            game_paint.paint()
            # print m.point_buf
            time.sleep(0.5)
            if at_bottom(b, m):
                m.attach_block(b)
                break
            else:
                b.drop()

def at_bottom(block, m):
    for point in block.pic:
        if m.buf(block.x + point[0], block.y + point[1] - 1) is not 0:
            return True
    return False
def at_left(block, m):
    for point in block.pic:
        if m.buf(block.x + point[0] - 1, block.y + point[1]) is not 0:
            return True
    return False
def at_right(block, m):
    for point in block.pic:
        if m.buf(block.x + point[0] + 1, block.y + point[1]) is not 0:
            return True
    return False
def can_rotate(block, m):
    rotated_pic = BlockTool.rotate_pic(block.pic)
    for point in block.rotated_pic:
        if m.buf(block.x + point[0], block.y + point[1]) is not 0:
            return False
    return True

if __name__ == '__main__':
    main()
