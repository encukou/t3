import math
import contextlib
import sys
import threading

import pyglet
import pyglet.window
from pyglet import gl

from neopixel import _strip
from machine import _pressed_button_pins

sys.path.clear()
sys.path.append('.')


window = pyglet.window.Window(
    width=500, height=300,
    style=pyglet.window.Window.WINDOW_STYLE_TOOL)
window.set_minimum_size(50, 50)

KEY_TO_PIN_MAP = {
    pyglet.window.key.UP: 12,
    pyglet.window.key.RIGHT: 13,
    pyglet.window.key.DOWN: 14,
    pyglet.window.key.LEFT: 15,
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
    for i, color in enumerate(_strip._committed):
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

    for i, pin in enumerate([12, 13, 14, 15]):
        _draw_button(sx-w, sy+h*1.5, -i*90, pin)
    for i, pin in enumerate([0, 2]):
        _draw_button(sx+w*3.5, sy+h*1.6, (i+2)*90, pin)


@window.event
def on_key_press(key, mod):
    pin = KEY_TO_PIN_MAP.get(key)
    if pin is not None:
        _pressed_button_pins.add(pin)
    if key == pyglet.window.key.C:
        window.close()

@window.event
def on_key_release(key, mod):
    pin = KEY_TO_PIN_MAP.get(key)
    _pressed_button_pins.discard(pin)


end_loop = False

def tick(dt):
    if end_loop:
        window.close()

def run_main():
    try:
        import main
    finally:
        global end_loop
        end_loop = True

pyglet.clock.schedule_interval(tick, 1/60)

thread = threading.Thread(target=run_main)
thread.daemon = True
thread.start()

pyglet.app.run()
