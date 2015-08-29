#!/usr/bin/python
# -*- coding: utf-8 -*-

class Getch(object):  
    def __init__(self):  
        import platform
        os = platform.system()
        if os == "Windows":
            self.impl = _GetchWindows()  
        elif os == "Linux":
            self.impl = _GetchUnix()  
        elif os == "Darwin":
            try:
                self.impl = _GetchMacCarbon()  
            except:
                self.impl = _GetchUnix()  

    def __call__(self): return self.impl()  

class _GetchUnix(object):  
    def __init__(self):  
        import tty, sys, termios # import termios now or else you'll get the Unix version on the Mac  
    def __call__(self):  
        import os
        import sys, tty, termios
        #fd = sys.stdin.fileno()  
        #old_settings = termios.tcgetattr(fd)  
        try:  
            #tty.setraw(sys.stdin.fileno())  
            #tty.setraw(fd)  
            os.system("stty cbreak -echo")
            ch = sys.stdin.read(1)  
        finally:  
            #termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  
            os.system("stty -cbreak echo")
        return ch  

class _GetchWindows(object):  
    def __init__(self):  
        import msvcrt  
    def __call__(self):  
        import msvcrt  
        return msvcrt.getch()  

class _GetchMacCarbon:  
    def __init__(self):  
        import Carbon  
        Carbon.Evt #see if it has this (in Unix, it doesn't)  
    def __call__(self):  
        import Carbon  
        if Carbon.Evt.EventAvail(0x0008)[0]==0: # 0x0008 is the keyDownMask  
            return ''  
        else:  
            #  
            # The event contains the following info:  
            # (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]  
            #  
            # The message (msg) contains the ASCII char which is  
            # extracted with the 0x000000FF charCodeMask; this  
            # number is converted to an ASCII character with chr() and  
            # returned  
            #  
            (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]  
            return chr(msg & 0x000000FF)  

if __name__ == '__main__': # a little test  
   print 'Press a key'  
   inkey = Getch()  
   while True:
       k = inkey()
       if k=='x':
           break
       print 'you pressed ',k,ord(k)
