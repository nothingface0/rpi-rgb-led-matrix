#!/usr/bin/python

# Simple RGBMatrix example, using only Clear(), Fill() and SetPixel().
# These functions have an immediate effect on the display; no special
# refresh operation needed.
# Requires rgbmatrix.so present in the same directory.

import time
from rgbmatrix import Adafruit_RGBmatrix
import numpy
import random
import cProfile

# Rows and chain length are both required parameters:
rgb_matrix = Adafruit_RGBmatrix(32, 1)
width = 32
height = 32
step = 0

# this function does all the work
# def play_life(a):
#     xmax, ymax = a.shape
#     b = a.copy() # copy grid & Rule 2
#     for x in range(xmax):
#         for y in range(ymax):
#             n = numpy.sum(a[max(x - 1, 0):min(x + 2, xmax), max(y - 1, 0):min(y + 2, ymax)]) - a[x, y]
#             if a[x, y]:
#                 if n < 2 or n > 3:
#                     b[x, y] = 0 # Rule 1 and 3
#             elif n == 3:
#                 b[x, y] = 1 # Rule 4
#     return(b)

def new_life(a):
    """
    This is life.
    """
    xmax, ymax = a.shape
    new_a = numpy.array(a, dtype=numpy.uint8)

    def get(x, y):
        return 1 if a[x & 31, y & 31] else 0
    
    def alive_neighbours(x, y):
        # neighbours which alive
        return (get(x-1, y)
              + get(x,   y-1)
              + get(x-1, y-1)
              + get(x+1, y+1)
              + get(x+1, y-1)
              + get(x-1, y+1)
              + get(x,   y+1)
              + get(x+1, y))
            
    for x in range(0, xmax):
        for y in range(0, ymax):
            n = alive_neighbours(x, y)
            if n < 2:
                new_a[x, y] = 0
            elif n == 3:
                new_a[x, y] = min(255, a[x, y] + 32)
            elif n < 4:
                new_a[x, y] = 0 if not a[x, y] else min(255, a[x, y] + 32)
            elif n > 3:
                new_a[x, y] = 0
                
    return new_a


life = numpy.zeros((width, height), dtype=numpy.uint8)
life_history = numpy.zeros((width, height), dtype=numpy.uint8)

def fill_with_crap():
    for y in range(0, width):
        for x in range(0, height):
            life[x][y] = random.randint(0, 1)


a_list = [0] * 3072
def show():
    if life.sum(axis=1).sum() < 1:
        exit(1)
    
    global a_list
    i = 0
    for y in range(0, height):
        for x in range(0, width):
            if life[x][y]:
                a_list[i] = 0
                i += 1
                a_list[i] = 255 - life[x][y]
                i += 1
                a_list[i] = life[x][y]
                i += 1
            else:
                a_list[i] = life_history[x][y]
                i += 1
                a_list[i] = life_history[x][y]
                i += 1
                a_list[i] = life_history[x][y]
                i += 1

    rgb_matrix.SetBuffer(a_list)

    # for y in range(0, width):
    #     for x in range(0, height):
    #         if life[x][y]:
    #             rgb_matrix.SetPixel(x, y, 0, 255 - life[x][y], life[x][y])
    #         else:
    #             rgb_matrix.SetPixel(x, y, life_history[x][y], life_history[x][y], life_history[x][y])


def tick():
    global life, life_history
    # step += 1
    # if step == 256:
    #     step = 0
    #     for i in range(0, 5):
    #         life[random.randint(0, width - 1)][random.randint(0, height - 1)] = 1

    # Random life injection
    life[random.randint(0, width - 1)][random.randint(0, height - 1)] = 1
    life = new_life(life)
    for x in range(0, width):
        for y in range(0, height):
            if life[x][y]:
                life_history[x][y] = min(128, life_history[x][y] + 64)
            else:
                life_history[x][y] = max(0, life_history[x][y] - 8)

    show()

fill_with_crap()
# life[1,1] = 1
# life[1,2] = 1
# life[2,1] = 1
# life[2,2] = 1
while True:
    # cProfile.run('tick()')
    tick()
    time.sleep(0.1)

rgb_matrix.Clear()
