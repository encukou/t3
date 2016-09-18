import os
import time
from machine import Pin
from neopixel import NeoPixel

np = NeoPixel(Pin(5, Pin.OUT), 9)

tasks = []

task_i = 0

class Task:
    def __init__(self, gen):
        global task_i
        self.gen = gen
        tasks.append([0, task_i, self])
        task_i += 1

def draw():
    while True:
        np.write()
        yield 1/120

Task(draw())

def anim_pixel(n, r, g, b, steps=15):
    start = np[n]
    end = r, g, b
    for i in range(0, steps):
        np[n] = [int((start[c] * (steps-i) + end[c] * i) / steps)
                 for c in range(3)]
        yield 1/60
    np[n] = end

def delay(n, other):
    yield n
    yield from other

def anim_starter(func, anims):
    for i, args in enumerate(anims):
        if args is not None:
            Task(func(*args))
            yield 1/10

Task(anim_starter(anim_pixel, (
    (2, 100//3, 100//2, 100),
    (1, 100//3, 100//2, 100),
    (0, 100//3, 100//2, 100),
    (4, 100//3, 100//2, 100),
    (7, 100//3, 100//2, 100),
)))

Task(delay(0.7, anim_starter(anim_pixel, (
    (2, 0, 0, 0),
    (1, 0, 0, 0),
    (0, 0, 0, 0),
    None,
    (7, 0, 0, 0),
))))

Task(delay(1, anim_starter(anim_pixel, (
    (4, 100, 100/2, 100/3, 30),
    None,
    None,
    (8, 100, 100/2, 100/3, 30),
    (0, 100, 100/2, 100/3, 30),
))))

Task(delay(1.7, anim_starter(anim_pixel, (
    (4, 0, 0, 0, 60),
    None,
    None,
    (8, 0, 0, 0),
    (0, 0, 0, 0),
))))

def main_menu():
    for i in range(9):
        np[i] = 0, 0, 10
    return
    yield

Task(delay(2.7, main_menu()))

while tasks:
    tasks.sort()
    wait, i, task = tasks[0]
    time.sleep(wait)
    for entry in tasks:
        entry[0] -= wait
    try:
        wait = next(task.gen)
    except StopIteration:
        tasks.pop(0)
    else:
        tasks[0][0] = wait
