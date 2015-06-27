#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import time
import random
import threading

import getkey
import drawhandler

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
        self.reinit(block_id, x, y, speed) 
    def reinit(self, block_id = 0, x = 0, y = 0, speed = 1):
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
    def __init__(self, x_max = 10, y_max = 30, x_min = 0, y_min = 0):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.__row_count = self.y_max - self.y_min + 1
        self.__col_count = self.x_max - self.x_min + 1
        self.__buf = []
        self.__init_buf()
    # -- Buf APIs 
    def attach_block(self, b):
        self.__attach_points(b.pic, b.x, b.y)
    def buf(self, x, y):
        return self.__buf[y][x]
    def buf_size(self):
        return self.__col_count, self.__row_count  # x_max, y_max
    # -- Old APIs
    def is_full_line(self, line_num):
        if self.__buf[line_num][1: -1].count(2) is self.__col_count - 2:
            return True
        return False
    def is_empty_line(self, line_num):
        if self.__buf[line_num][1: -1].count(0) is self.__col_count - 2:
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
    # -- New APIs
    def get_full_lines(self):
        for line_num in range(1, self.__row_count):
            zero_count = self.__buf[line_num][1: -1].count(0)
            if zero_count is self.__col_count - 2:  # empty line, stop yielding
                raise StopIteration
            elif zero_count is 0:                   # full line, yield it
                yield line_num
    def refresh_lines(self):
        # Refresh all lines, returns -1 if game over, 0 otherwise
        count = 1
        for line_num in range(1, self.__row_count):    # Scan bottom-up
            zero_count = self.__buf[line_num][1: -1].count(0)
            if zero_count is self.__col_count - 2:  # empty line, padding, return 0
                for i in range(count, line_num):
                    self.clear_line(i)
                return line_num - count
            elif zero_count is not 0 and line_num is not self.__row_count - 2:
                # neither empty nor full(not last line), count it, goes down
                self.__buf[count] = self.__buf[line_num][:]
                count += 1
            elif zero_count is not 0 and line_num is self.__row_count - 2:
                return -1
        return line_num - count
    # -- Private Methods
    def __attach_points(self, pic, x, y):
        for point in pic:
            self.__buf[point[1] + y][point[0] + x] = 2  # buf[y][x]
    def __init_buf(self):
        self.__buf = [[1] + [0] * (self.__col_count - 2) + [1] for i in range(self.__row_count - 2)]
        self.__buf.insert(0, [1] * (self.__col_count))
        self.__buf.append([1] * (self.__col_count))
        self.test_buf = self.__buf
    # -- Debug Methods
    def print_buf(self):
        for line in self.__buf:
            print line
    def buf_at_col(self, col):
        return [line[col] for line in self.__buf]
    def buf_at_row(self, row):
        return self.__buf[row]

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
    def print_score(self, score):
        mes = 'score: ' + str(score)
        print mes
    def repaint(self):
        self.handler.clear_buf()
    def paint(self):
        self.handler.paint()

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
    def __game_over(self):
        pass
    def __block_dead(self, block):
        pass
    def __block_drop(self, block):
        # Should return True periodically, like every 1s
        pass

end = False
score = 0
def key_thread(block, m):
    getch = getkey.Getch()
    global end
    while not end:#self.start == True:
        key = None
        c = getch()
        if end:
            break
        #print 'pressed:', c
        if c == 'w' and can_rotate(block, m):
            block.rotate()
        elif c == 'd' and not at_right(block, m):
            block.move(RIGHT)
        elif c == 'a' and not at_left(block, m):
            block.move(LEFT)
        elif c == 's' and not at_bottom(block, m):
            block.move(DOWN)
        time.sleep(0.1)

def display_thread(b, m):
    game_paint = GamePaint(drawhandler.ConsolePaintHandler(m.x_max, m.x_min, m.y_max, m.y_min))
    global end, score
    while not end:
        game_paint.repaint()
        game_paint.draw_map(m)
        game_paint.draw_block(b)
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

def main():
    global score
    m = GameMap(12, 20)
    b = Block()
    threading.Thread(target = key_thread, args = (b, m, )).start()
    threading.Thread(target = display_thread, args = (b, m, )).start()
    over = False
    while not over:
        i = random.randint(0, len(BlockTool.PICS) - 1)
        b.reinit(block_id = i, x = 5, y = 17)
        if at_bottom(b, m):
            over = True
        while True:
            time.sleep(0.5)
            if at_bottom(b, m):
                m.attach_block(b)
                count = m.refresh_lines()
                if count is -1:
                    over = True
                elif count is not 0:
                    score += 2 * count - 1
                break
            else:
                b.drop()
    global end
    end = True

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
    for point in rotated_pic:
        if m.buf(block.x + point[0], block.y + point[1]) is not 0:
            return False
    return True

if __name__ == '__main__':
    try:
        main()
    except e:
        print '\ngame crashed, see log.txt'
        global end
        end = True

