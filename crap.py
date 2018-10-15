#!/usr/bin/python

# Simple RGBMatrix example, using only Clear(), Fill() and SetPixel().
# These functions have an immediate effect on the display; no special
# refresh operation needed.
# Requires rgbmatrix.so present in the same directory.

import sys
import time
from rgbmatrix import Adafruit_RGBmatrix
import numpy
import random
import cProfile
import life as clife

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


life         = numpy.zeros((width, height), dtype=numpy.uint8)
secondlife   = numpy.zeros((width, height), dtype=numpy.uint8)
alivelife    = numpy.zeros((width, height), dtype=numpy.uint8)
life_history = numpy.zeros((width, height), dtype=numpy.int16)


def fill_from_strings(strings):
    y = 0 
    for s in strings:
        x = 0
        for c in s:
            if c not in [" ", "0"]:
                life[x,y] = 1
            x += 1
        y += 1

def fill_with_crap():
    for y in range(0, width):
        for x in range(0, height):
            life[x][y] = random.randint(0, 1)


a_list = [0] * 3072
def show(life, life_history):
    if life.sum(axis=1).sum() < 1:
        exit(1)
    
    global a_list
    i = 0
    for y in range(0, height):
        for x in range(0, width):
            if life[x][y]:
                a_list[i] = 0
                i += 1
                a_list[i] = 255 - min(life[x][y] * 32, 255)
                i += 1
                a_list[i] = min(life[x][y] * 32, 255)
                i += 1
            else:
                a_list[i] = life_history[x][y]
                i += 1
                a_list[i] = life_history[x][y]
                i += 1
                a_list[i] = life_history[x][y]
                i += 1

    rgb_matrix.SetBuffer(a_list)

def fastshow(life, life_history):
    buf = numpy.zeros((life.shape[0], life.shape[1], 3), dtype=numpy.uint8)
    r = buf[:,:, 0]
    g = buf[:,:, 1]
    b = buf[:,:, 2]

    alive = (life > 0)
    r[alive] = 0
    b[alive] = numpy.clip(life[alive], 0, 7)*32
    g[alive] = 255 - b[alive]

    dead = (life == 0)
    r[dead] = life_history[dead]
    g[dead] = life_history[dead]
    b[dead] = life_history[dead]

    rgb_matrix.SetBuffer(list(buf.flat))


def tick():
    global life, secondlife, life_history, alivelife
    # step += 1
    # if step == 256:
    #     step = 0
    #     for i in range(0, 5):
    #         life[random.randint(0, width - 1)][random.randint(0, height - 1)] = 1

    # Random life injection
    if len(sys.argv) == 1: 
        life[random.randint(0, width - 1)][random.randint(0, height - 1)] = 1
    secondlife, life = life, clife.life(life, secondlife)

    #           zero if dead       increment if alive
    alivelife = (alivelife * life) + life

    life_history[life > 0] += 64
    life_history[life == 0] -= 8
    numpy.clip(life_history, 0, 128, out=life_history)

    fastshow(alivelife, life_history)

if len(sys.argv) > 1:
    fill_from_strings(sys.argv[1:])
else:
    fill_with_crap()

# life[1,1] = 1
# life[1,2] = 1
# life[2,1] = 1
# life[2,2] = 1
while True:
    if life.sum(axis=1).sum() < 1:
        exit(1)
    #cProfile.run('tick()')
    tick()
    time.sleep(0.03)

rgb_matrix.Clear()
