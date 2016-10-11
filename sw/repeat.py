# T3 Cartridge
# 1/5  0f0000 0f0000 0f0000  000000 0f0000 000000  000000 000000 000000
# 1/5  000f00 000000 000000  000f00 000f00 000000  000f00 000000 000000
# 1/5  000000 000000 000000  000000 00000f 000000  00000f 00000f 00000f
# 1/5  000000 000000 0f0f00  000000 0f0f00 0f0f00  000000 000000 0f0f00

import t3

COMBINATIONS = {
    0: ((1, 1, 1,  0, 1, 0,  0, 0, 0), 196, t3.hls_to_rgb(0, 0.2, 0.9)),  # G
    1: ((1, 0, 0,  1, 1, 0,  1, 0, 0), 262, t3.hls_to_rgb(0.3, 0.2, 0.9)),
    2: ((0, 0, 0,  0, 1, 0,  1, 1, 1), 330, t3.hls_to_rgb(0.6, 0.2, 0.9)),
    3: ((0, 0, 1,  0, 1, 1,  0, 0, 1), 391, t3.hls_to_rgb(0.14, 0.2, 0.9)),
}


def fill(r, g, b):
    for i in range(9):
        t3.display[i] = r, g, b

def display_prompt():
    fill(0, 0, 0)
    t3.display[1, 1] = 20, 20, 20

def flash(r, g, b):
    for i in range(3):
        fill(r, g, b)
        yield 0.2
        fill(0, 0, 0)
        yield 0.1

def get_input():
    vals = t3.up.value, t3.right.value, t3.down.value, t3.left.value
    for i in range(4):
        if vals[i]:
            return i
    return -1

def display_piece(c):
    onoff, note, color = COMBINATIONS[c]
    for i, x in enumerate(onoff):
        if x:
            t3.display[i] = color
        else:
            t3.display[i] = 0, 0, 0
    t3.tone(note)

def main():
    yield from flash(30, 30, 30)

    combination = []
    while True:
        combination.append(t3.randrange(0, 4))

        # Play combination
        yield 0.5
        for c in combination:
            display_piece(c)
            yield 0.4
            fill(0, 0, 0)
            t3.tone(0)
            yield 0.2

        # Expect combination
        for c in combination:
            fill(0, 0, 0)
            while get_input() != -1:
                yield 0.05
            while True:
                display_prompt()
                inp = get_input()
                if inp == -1:
                    yield 0.05
                    continue
                display_piece(inp)
                if inp != c:
                    while get_input() != -1:
                        yield 0.05
                    t3.tone(0)
                    fill(0, 0, 0)
                    yield 0.1
                    yield from flash(100, 0, 0)
                    fill(0, 0, 0)
                    combination = []
                    break
                else:
                    while get_input() != -1:
                        yield 0.05
                    t3.tone(0)
                    break
            if not combination:
                break
        else:
            fill(0, 0, 0)
            yield 0.5
            hue = t3.random_uniform(0.23, 0.37)
            yield from flash(0, 70, 0)
