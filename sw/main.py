import os
import time
import random
from machine import Pin
from neopixel import NeoPixel

np = NeoPixel(Pin(5, Pin.OUT), 9)

pin_left = Pin(13, Pin.IN)
pin_right = Pin(15, Pin.IN)
pin_a = Pin(0, Pin.IN)

tasks = []

task_i = 0

def hls_to_rgb(h, l, s):
    """From CPython's colorsys module"""
    if s == 0.0:
        return l, l, l
    if l <= 0.5:
        m2 = l * (1.0+s)
    else:
        m2 = l+s-(l*s)
    m1 = 2.0*l - m2
    return (_v(m1, m2, h+1/3), _v(m1, m2, h), _v(m1, m2, h-1/3))


def _v(m1, m2, hue):
    hue = hue % 1.0
    if hue < 1/6:
        return m1 + (m2-m1)*hue*6.0
    if hue < 0.5:
        return m2
    if hue < 2/3:
        return m1 + (m2-m1)*(2/3-hue)*6.0
    return m1



def args(*a):
    return a


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

def anim_pixel(n, r, g, b, steps=20):
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

def bluish():
    hue = random.uniform(0.43, 0.67)
    sat = 0.26
    lightness = 0.4
    return tuple(c*255 for c in hls_to_rgb(hue, sat, lightness))

def reddish():
    hue = random.uniform(-0.07, 0.07)
    sat = 0.26
    lightness = 0.4
    return tuple(c*255 for c in hls_to_rgb(hue, sat, lightness))

Task(anim_starter(anim_pixel, (
    args(1, *bluish()),
    args(2, *bluish()),
    args(0, *bluish()),
    args(4, *bluish()),
    args(7, *bluish()),
)))

Task(delay(0.7, anim_starter(anim_pixel, (
    (2, 0, 0, 0),
    (0, 0, 0, 0),
    (1, 0, 0, 0),
    None,
    (7, 0, 0, 0),
))))

Task(delay(1, anim_starter(anim_pixel, (
    args(8, *reddish()),
    args(0, *reddish()),
    None,
    None,
    args(4, *reddish()),
))))

Task(delay(1.7, anim_starter(anim_pixel, (
    (8, 0, 0, 0),
    (0, 0, 0, 0),
    None,
    None,
    (4, 0, 0, 0, 25),
))))

class MenuItem:
    def __init__(self, name):
        self.name = name

    def get_next(self):
        while not self.next.ensure_loaded():
            self.next.next.prev = self
            self.next = self.next.next
            if self.next is self:
                raise RuntimeError('No usable files')
        return self.next

    def get_prev(self):
        while not self.prev.ensure_loaded():
            self.prev.prev.next = self
            self.prev = self.prev.prev
            if self.prev is self:
                raise RuntimeError('No usable files')
        return self.prev

    def ensure_loaded(self):
        try:
            return self.data
        except AttributeError:
            try:
                self.data = self.load()
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.data = None
            return self.data

    def load(self):
        with open(self.name) as f:
            if f.readline().strip() != '# T3 Cartridge':
                return None
            items = []
            for line in f:
                if not line.startswith('# '):
                    break
                parts = line[1:].strip().split()
                parts_duration = parts[0].split('/')
                duration = float(parts_duration[0])
                for part in parts_duration[1:]:
                    duration /= float(part)
                pixels = [(int(p[:2], 16), int(p[2:4], 16), int(p[4:], 16))
                          for p in parts[1:]]
                items.append((duration, pixels))
            return items

    def __repr__(self):
        return '<{}: {}>'.format(type(self).__name__, self.name)

def main_menu():
    items = list(MenuItem(n) for n in os.listdir() if n.endswith('.py'))
    for item, prev, nxt in zip(items, [items[-1]] + items, items[1:] + [items[0]]):
        item.prev = prev
        item.next = nxt
    current_item = items[0].get_next()
    current_frame = -1
    left_prev = pin_left.value()
    right_prev = pin_left.value()
    a_prev = pin_a.value()
    while True:
        current_frame += 1
        current_frame %= len(current_item.data)
        wait, pixels = current_item.data[current_frame]
        for i, pixel in enumerate(pixels):
            np[i] = pixel
        yield wait

        left = pin_left.value()
        right = pin_right.value()
        a = pin_a.value()

        if left and not left_prev:
            current_item = current_item.get_prev()
        if right and not right_prev:
            current_item = current_item.get_next()
        if a and not a_prev:
            ns = {}
            with open(current_item.name) as f:
                exec(f.read(), ns)
            Task(ns['main']())
            return

        left_prev = left
        right_prev = right
        a_prev = a


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

# 1/5  000000 000000 000000  000000 000000 000000  000000 000000 000000
