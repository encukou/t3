import time
import machine

from machine import Pin, PWM
from esp import neopixel_write

try:
    from uos import urandom as rand_bytes
except ImportError:
    import urandom as urandom
    def rand_bytes(n):
        return bytes([urandom.getrandbits(8) for i in range(n)])

# Display

def _get_index(subscript):
    try:
        x, y = subscript
    except TypeError:
        return int(subscript) * 3
    else:
        return (2-x + 3*y) * 3


class _Display:
    def __init__(self):
        self._pin = Pin(5, Pin.OUT)
        self._buf = bytearray(9 * 3)

    def __setitem__(self, subscript, value):
        r, g, b = value
        idx = _get_index(subscript)
        self._buf[idx:idx+3] = bytes((g, r, b))

    def __getitem__(self, subscript):
        idx = _get_index(subscript)
        g, r, b = self._buf[idx:idx+3]
        return r, g, b

    def anim_pixel(self, subscript, r, g, b, steps=20):
        start = self[subscript]
        end = r, g, b
        for i in range(0, steps):
            j = steps-i
            self[subscript] = [int((s * j + e * i) / steps)
                               for s, e in zip(start, end)]
            yield 1/60
        self[subscript] = end

    def show_image(self, data):
        self._buf[:] = data

    def _write(self):
        neopixel_write(self._pin, self._buf, True)

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
    byte = rand_bytes(1)[0]
    return a + (byte / 256) * (b - a)

def randrange(a, b):
    values = range(a, b)
    byte = rand_bytes(1)[0]
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

TASK_TIME = const(0)
TASK_NUM = const(1)
TASK_START = const(2)
TASK_BTN_TRIGGER = const(3)
TASK_BTN_MASK = const(4)
TASK_CORO = const(5)

def start_task(coro):
    global _task_i
    next(coro)
    _tasks.append([0, _task_i, time.ticks_ms(), 0, 0, coro])
    _task_i += 1

def run():
    global _pressed_buttons
    display._write()
    ticks_last = draw_last = btn_last = time.ticks_ms()
    last_buttons = 0
    while _tasks:
        ticks_now = time.ticks_ms()
        diff = time.ticks_diff(ticks_last, ticks_now)
        ticks_last = ticks_now

        for task in _tasks:
            task[TASK_TIME] -= diff

        if time.ticks_diff(draw_last, ticks_now) > 50:
            draw_last = ticks_now
            display._write()
            continue

        if time.ticks_diff(btn_last, ticks_now) > 20:
            btn_last = ticks_now
            if hasattr(machine, '_t3_emulated'):
                machine._update_buttons()
            _pressed_buttons = 0
            mask = 0
            for btn in a, b, left, right, up, down:
                if btn.pin.value():
                    if last_buttons & btn.mask:
                        mask |= btn.mask << _btn_count
                else:
                    _pressed_buttons |= btn.mask
                    if (~last_buttons) & btn.mask:
                        mask |= btn.mask
            last_buttons = _pressed_buttons

            if mask:
                for task in _tasks:
                    if task[TASK_BTN_TRIGGER] & mask and task[TASK_TIME] > 0:
                        task[TASK_TIME] = 0
                    task[TASK_BTN_MASK] |= mask

        _tasks.sort()
        task = _tasks[0]
        wait = task[TASK_TIME]
        if wait > 0:
            if time.ticks_diff(draw_last, ticks_now) > 16:
                draw_last = ticks_now
                display._write()
            else:
                if wait > 10:
                    wait = 10
                time.sleep_ms(wait)
            continue
        else:
            start = task[TASK_START]
            coro = task[TASK_CORO]
            btn_mask = task[TASK_BTN_MASK]
            btn_mask |= _pressed_buttons << (2 * _btn_count)
            ticks = time.ticks_diff(start, ticks_now)
            try:
                wait = coro.send(_YieldInfo(ticks, btn_mask))
            except StopIteration:
                _tasks.pop(0)
            else:
                if isinstance(wait, (int, float)):
                    task[TASK_TIME] = int(wait * 1000)
                    task[TASK_BTN_TRIGGER] = 0
                else:
                    task[TASK_TIME] = wait.timeout_ms
                    task[TASK_BTN_TRIGGER] = wait.btn_mask
                task[TASK_BTN_MASK] = 0

class _YieldInfo:
    def __init__(self, elapsed_ms, mask):
        self.elapsed_ms = elapsed_ms
        self._mask = mask

    @property
    def pressed(self):
        return _ButtonInfo(self._mask)

    @property
    def released(self):
        return _ButtonInfo(self._mask >> _btn_count)

    @property
    def held(self):
        return _ButtonInfo(self._mask >> (_btn_count * 2))

    @property
    def elapsed(self):
        return self.elapsed_ms / 1000

# Buttons

_pressed_buttons = 0
_button_map = {}

class _Button:
    def __init__(self, number, pin_number):
        self.number = number
        self.mask = 1 << number
        self.pin = Pin(pin_number, Pin.IN, pull=Pin.PULL_UP)
        _button_map[pin_number] = number

    @property
    def value(self):
        return bool(_pressed_buttons & self.mask)

left = _Button(0, 4)
right = _Button(1, 13)
up = _Button(2, 12)
down = _Button(3, 14)
a = _Button(4, 0)
b = _Button(5, 2)
_btn_count = 6

class _ButtonInfo:
    def __init__(self, value):
        self._value = value

    def __getitem__(self, button):
        return bool(self._value & button.mask)

class wait_for_input:
    timeout_ms = 2147483648
    btn_mask = -1

    def __init__(self, *, timeout=None, buttons=None):
        if timeout is not None:
            self.timeout_ms = int(timeout * 1000)
        if buttons is not None:
            self.btn_mask = 0
            for btn in buttons:
                self.btn_mask |= btn.mask
                self.btn_mask |= btn.mask << _btn_count

# Sound

_pwm = PWM(Pin(15, Pin.OUT))

def tone(pitch, duty=512):
    if pitch == 0:
        _pwm.deinit()
    else:
        _pwm.init(pitch, duty)

tone(0)
