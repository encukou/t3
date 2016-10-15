import math
import contextlib
import sys
import threading
import subprocess
import ast
import fcntl
import os
import time

import click
import pyglet
import pyglet.window
from pyglet import gl

_strip = bytearray(9 * 3)
_pressed_button_pins = set()

class EmulatorWindow(pyglet.window.Window):
    def __init__(self, **kwargs):
        kwargs.setdefault('width', 500)
        kwargs.setdefault('height', 300)
        kwargs.setdefault('style', pyglet.window.Window.WINDOW_STYLE_TOOL)
        super().__init__(**kwargs)
        self.set_minimum_size(50, 50)

    def on_key_press(self, key, mod):
        pin = KEY_TO_PIN_MAP.get(key)
        if pin is not None:
            _pressed_button_pins.add(pin)
            in_file.write('+{}\n'.format(pin).encode('ascii'))
            in_file.flush()
        if key == pyglet.window.key.C:
            self.close()

    def on_key_release(self, key, mod):
        pin = KEY_TO_PIN_MAP.get(key)
        if pin is not None:
            _pressed_button_pins.discard(pin)
            in_file.write('-{}\n'.format(pin).encode('ascii'))
            in_file.flush()

    def on_draw(self):
        self.clear()
        w, sx = _dim(self.width, self.height)
        h, sy = _dim(self.height, self.width)
        for i in range(9):
            y, x = divmod(i, 3)
            px = sx+(2-x)*w
            py = sy+(2-y)*h

            g, r, b = _strip[i*3:i*3+3]
            color = r, g, b

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


end_loop = False

def tick(dt):
    pass

def do_fork(micropython_binary, delay=0):
    # Need to open MicropPython with bi-directional communication
    # (button state in; LED state out). Since MicroPython doesn't have threads,
    # the inward pipe needs to be opened in nonblocking mode.
    # There's no way a pipe can be switched to non-blocking mode MicroPython,
    # and subprocess doesn't provide a way to create non-blocking pipes.
    # So let's do what subprocess does manually: pipe, fork, dup2, and execvpe.

    global in_file, out_file

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
        time.sleep(delay)
        print('# Fork started')
        os.execvpe('micropython', ['micropython', '-m', 'main'],
                {'MICROPYPATH': '.:../emu'})

    os.close(in_read)
    os.close(out_write)
    in_file = os.fdopen(in_write, 'wb')
    out_file = os.fdopen(out_read, 'rb')

def run_main_factory(micropython_binary):
    def run_main():
        while True:
            try:
                line = out_file.readline()
            except BrokenPipeError:
                line = b''
            if line == b'':
                if os.path.exists('selected-game'):
                    print('# Resetting')
                    do_fork(micropython_binary=micropython_binary, delay=1)
                    continue
                else:
                    pyglet.app.exit()
                    break
            if line.startswith(b'* '):
                _strip[:] = ast.literal_eval(line[2:].decode('ascii'))
            else:
                print('*', line)
    return run_main


def main(*, micropython_binary='micropython'):
    EmulatorWindow()

    pyglet.clock.schedule_interval(tick, 1/60)

    do_fork(micropython_binary=micropython_binary)

    thread = threading.Thread(target=run_main_factory(micropython_binary))
    thread.daemon = True
    thread.start()

    pyglet.app.run()

click.core._verify_python3_env = lambda: None
@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--micropython-binary', envvar='MICROPYTHON_BINARY',
              default='micropython',
              help='The MicroPython binary to use '
                '[env variable: $MICROPYTHON_BINARY; '
                'default: micropython] '
             )
@click.argument('game', default=None, required=False)
def cli(game, micropython_binary):
    """Run the T3 "emulator"

    GAME: Name of the game to launch. If not given, the launcher is started.
    """
    print(game)
    if game:
        with open('selected-game', 'w') as f:
            f.write(game)
    else:
        try:
            os.unlink('selected-game')
        except FileNotFoundError:
            pass

    main(micropython_binary=micropython_binary)

if __name__ == '__main__':
    cli()
