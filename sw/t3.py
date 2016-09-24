import urandom
import time
import machine
import sys

from machine import Pin
from neopixel import NeoPixel

# Display

def _get_index(subscript):
    try:
        x, y = subscript
    except TypeError:
        return int(subscript)
    else:
        return 2-x + 3*y


class _Display:
    def __init__(self):
        self._np = NeoPixel(Pin(5, Pin.OUT), 9)

    def __setitem__(self, subscript, value):
        self._np[_get_index(subscript)] = value

    def __getitem__(self, subscript):
        return self._np[_get_index(subscript)]

    def anim_pixel(self, subscript, r, g, b, steps=20):
        index = _get_index(subscript)
        np = self._np
        start = np[index]
        end = r, g, b
        for i in range(0, steps):
            j = steps-i
            np[index] = [int((s * j + e * i) / steps)
                         for s, e in zip(start, end)]
            yield 1/60
        np[index] = end

display = _Display()


# Color helpers
# (from CPython's colorsys module)

def _v(m1, m2, hue):
    hue = hue % 1.0
    if hue < 1/6:
        return int((m1 + (m2-m1)*hue*6.0) * 255)
    if hue < 0.5:
        return int(m2 * 255)
    if hue < 2/3:
        return int((m1 + (m2-m1)*(2/3-hue)*6.0) * 255)
    return int(m1 * 255)

def hls_to_rgb(h, l, s):
    if s == 0.0:
        return l, l, l
    if l <= 0.5:
        m2 = l * (1.0+s)
    else:
        m2 = l+s-(l*s)
    m1 = 2.0*l - m2
    print(_v(m1, m2, h+1/3), _v(m1, m2, h), _v(m1, m2, h-1/3))
    return (_v(m1, m2, h+1/3), _v(m1, m2, h), _v(m1, m2, h-1/3))

# Random helper

def random_uniform(a, b):
    byte = urandom.getrandbits(8)
    return a + (byte / 256) * (b - a)

def randrange(a, b):
    values = range(a, b)
    byte = urandom.getrandbits(8)
    return values[byte % len(values)]

# Listdir helper

try:
    from uos import listdir
except ImportError:
    from uos import ilistdir
    def listdir():
        return [directory for directory, _, _ in ilistdir()]

# Task helpers

_task_i = 0
_tasks = []

def start_task(gen):
    global _task_i
    _tasks.append([0, _task_i, gen])
    _task_i += 1

_stdin_line = ''
_prev_buttons = 0
_button_handler = None

def _sys_task():
    global _stdin_line
    global _prev_buttons
    while True:
        display._np.write()
        yield 1/120

        if hasattr(machine, '_t3_emulated'):
            rd = sys.stdin.read(1)
            if rd is not None:
                _stdin_line += rd
                if '\n' in _stdin_line:
                    cmd, sep, _stdin_line = _stdin_line.partition('\n')
                    print('>', cmd)
                    if cmd.startswith('+'):
                        machine._pin_objects[int(cmd[1:])]._fall_callback()
                    elif cmd.startswith('-'):
                        machine._pin_objects[int(cmd[1:])]._rise_callback()

        now_buttons = _pressed_buttons
        button_change = now_buttons ^ _prev_buttons
        if button_change and _button_handler:
            _button_handler(_ButtonChangeInfo(_prev_buttons, now_buttons))
        _prev_buttons = now_buttons

start_task(_sys_task())

def run():
    while _tasks:
        _tasks.sort()
        wait, i, task = _tasks[0]
        time.sleep(wait)
        for entry in _tasks:
            entry[0] -= wait
        try:
            wait = next(task)
        except StopIteration:
            _tasks.pop(0)
        else:
            _tasks[0][0] = wait

# Buttons

_pressed_buttons = 0
_changed_buttons = 0

class _Button:
    def __init__(self, number, pin_number):
        self.number = number
        self.mask = 1 << number
        self.pin = Pin(pin_number, Pin.IN, pull=Pin.PULL_UP)
        self.pin.irq(
            trigger=Pin.IRQ_FALLING,
            handler=self._fell)
        self.pin.irq(
            trigger=Pin.IRQ_RISING,
            handler=self._rose)

    def _fell(self):
        global _pressed_buttons
        _pressed_buttons |= self.mask

    def _rose(self):
        global _pressed_buttons
        _pressed_buttons &= ~self.mask

    @property
    def value(self):
        return bool(_pressed_buttons & self.mask)

left = _Button(0, 15)
right = _Button(1, 13)
up = _Button(2, 12)
down = _Button(3, 14)
a = _Button(4, 0)
b = _Button(5, 2)

class _ButtonChangeInfo:
    def __init__(self, prev, now):
        self._prev = prev
        self._now = now
        changes = prev ^ now
        self.pressed = _ButtonInfo(changes & now)
        self.released = _ButtonInfo(changes & ~now)
        self.held = _ButtonInfo(now)

class _ButtonInfo:
    def __init__(self, value):
        self._value = value

    def __getitem__(self, button):
        return bool(self._value & button.mask)

def set_button_handler(handler):
    global _button_handler
    _button_handler = handler
