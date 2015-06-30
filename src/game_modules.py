#!/usr/bin/python
# -*- coding: utf-8 -*-

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
