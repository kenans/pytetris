from pytetris import *
m = GameMap(10, 10)

for i in range(1, 5):
    m.test_buf[i][5] = 2
m.set_line(1)
m.set_line(3)
m.print_buf()
print 'refresh_lines() returns', m.refresh_lines()
m.print_buf()

