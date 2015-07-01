#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytetris

def main():
    game = pytetris.GameTetris()
    game.game_start()
    game.main_thread()

if __name__ == '__main__':
    main()
