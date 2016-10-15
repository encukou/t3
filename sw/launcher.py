import t3
import sys

import launcher_manifest


def delay(n, other):
    yield n
    yield from other


def main_menu():
    items = launcher_manifest.data
    current_item_no = 0
    current_frame = -1

    while True:
        name, frames = items[current_item_no]
        current_frame += 1
        current_frame %= len(frames)
        wait, pixels = frames[current_frame]
        t3.display.show_image(pixels)

        buttons = yield wait / 1000

        if buttons.pressed[t3.a]:
            selected_name = name
            break

        if buttons.pressed[t3.left]:
            current_item_no -= 1
        if buttons.pressed[t3.right]:
            current_item_no += 1
        current_item_no %= len(items)

    with open('selected-game', 'w') as f:
        f.write(selected_name)
    for i in range(9):
        t3.display[i] = 0, 2, 2
        t3.display._write()
    t3.machine.reset()
