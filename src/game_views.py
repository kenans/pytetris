#!/usr/bin/python
# -*- coding: utf-8 -*-

class GamePaint(object):
    def __init__(self, handler):
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
