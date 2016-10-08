import math
import contextlib
import sys
import threading
import subprocess
import ast
import fcntl
import os

import pyglet
import pyglet.window
from pyglet import gl

sys.path.clear()
sys.path.append('.')

_strip = [(0, 0, 0)] * 9
_pressed_button_pins = set()

window = pyglet.window.Window(
    width=500, height=300,
    style=pyglet.window.Window.WINDOW_STYLE_TOOL)
window.set_minimum_size(50, 50)

KEY_TO_PIN_MAP = {
    pyglet.window.key.UP: 12,
    pyglet.window.key.RIGHT: 13,
    pyglet.window.key.DOWN: 14,
    pyglet.window.key.LEFT: 4,
    pyglet.window.key.Z: 0,
    pyglet.window.key.X: 2,
}


@contextlib.contextmanager
def pushed_matrix():
    gl.glPushMatrix()
    try:
        yield
    finally:
        gl.glPopMatrix()


def draw_rect(x, y, w, h, cx=3, cy=3):
    gl.glBegin(gl.GL_TRIANGLE_FAN)
    gl.glVertex2f(int(x+cx), int(y))
    gl.glVertex2f(int(x+w-cx), int(y))
    gl.glVertex2f(int(x+w), int(y+cy))
    gl.glVertex2f(int(x+w), int(y+h-cy))
    gl.glVertex2f(int(x+w-cx), int(y+h))
    gl.glVertex2f(int(x+cx), int(y+h))
    gl.glVertex2f(int(x), int(y+h-cy))
    gl.glVertex2f(int(x), int(y+cy))
    gl.glEnd()



def _dim(dimension, other):
    MAX = 200
    minimum = min(dimension, other)
    maximum = max(dimension, other)
    if minimum < MAX:
        start = (dimension - minimum) / 2
        return minimum // 3, start
    else:
        start = (dimension - MAX) / 2
        return MAX // 3, start

@window.event
def on_draw():
    window.clear()
    w, sx = _dim(window.width, window.height)
    h, sy = _dim(window.height, window.width)
    for i, color in enumerate(_strip):
        y, x = divmod(i, 3)
        px = sx+(2-x)*w
        py = sy+(2-y)*h

        gl.glColor3f(*((c/255)**0.5 for c in color))
        draw_rect(px, py, w-1, h-1)

        if sum(color) > 255:
            textcolor = (0, 0, 0, 100)
        else:
            textcolor = (255, 255, 255, 100)
        pyglet.text.Label(str(i), color=textcolor, x=px, y=py+1).draw()

    def _draw_button(x, y, r, pin):
        with pushed_matrix():
            gl.glTranslatef(x, y, 0)
            gl.glRotatef(45 + r, 0, 0, 1)
            if pin in _pressed_button_pins:
                gl.glColor3f(0.5, 0.7, 0.6)
            else:
                gl.glColor3f(0.1, 0.1, 0.1)
            draw_rect(1, 1, w/2, w/2)

    for i, pin in enumerate([12, 13, 14, 4]):
        _draw_button(sx-w, sy+h*1.5, -i*90, pin)
    for i, pin in enumerate([0, 2]):
        _draw_button(sx+w*3.5, sy+h*1.6, (i+2)*90, pin)


end_loop = False

def tick(dt):
    if end_loop:
        window.close()

# Need to open MicropPython with bi-directional communication
# (button state in; LED state out). Since MicroPython doesn't have threads,
# the inward pipe needs to be opened in nonblocking mode.
# There's no way a pipe can be switched to non-blocking mode MicroPython,
# and subprocess doesn't provide a way to create non-blocking pipes.
# So let's do what subprocess does manually: pipe, fork, dup2, and execvpe.

in_read, in_write = os.pipe()
out_read, out_write = os.pipe()

sys.stdin.flush()
sys.stdout.flush()
if os.fork() == 0:
    os.close(in_write)
    os.close(out_read)

    fl = fcntl.fcntl(in_read, fcntl.F_GETFL)
    fcntl.fcntl(in_read, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    os.dup2(in_read, 0)
    os.dup2(out_write, 1)
    print('# Fork started')
    os.execvpe('micropython', ['micropython', '-m', 'main'],
               {'MICROPYPATH': '.:../emu'})

os.close(in_read)
os.close(out_write)
in_file = os.fdopen(in_write, 'wb')
out_file = os.fdopen(out_read, 'rb')

def run_main():
    while True:
        line = out_file.readline()
        if line == b'':
            break
        if line.startswith(b'* '):
            _strip[:] = ast.literal_eval(line[2:].decode('ascii'))
        else:
            print('*', line)
    end_loop = True


@window.event
def on_key_press(key, mod):
    pin = KEY_TO_PIN_MAP.get(key)
    if pin is not None:
        _pressed_button_pins.add(pin)
        in_file.write('+{}\n'.format(pin).encode('ascii'))
        in_file.flush()
    if key == pyglet.window.key.C:
        window.close()

@window.event
def on_key_release(key, mod):
    pin = KEY_TO_PIN_MAP.get(key)
    if pin is not None:
        _pressed_button_pins.discard(pin)
        in_file.write('-{}\n'.format(pin).encode('ascii'))
        in_file.flush()

pyglet.clock.schedule_interval(tick, 1/60)

thread = threading.Thread(target=run_main)
thread.daemon = True
thread.start()

pyglet.app.run()
