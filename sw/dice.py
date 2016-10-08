# T3 Cartridge
# 1/5  000000 000000 000000  000000 0f0f0f 000000  000000 000000 000000
# 1/5  0f0f0f 000000 000000  000000 000000 000000  000000 000000 0f0f0f
# 1/5  0f0f0f 000000 000000  000000 0f0f0f 000000  000000 000000 0f0f0f
# 1/5  0f0f0f 000000 0f0f0f  000000 000000 000000  0f0f0f 000000 0f0f0f
# 1/5  0f0f0f 000000 0f0f0f  000000 0f0f0f 000000  0f0f0f 000000 0f0f0f
# 1/5  0f0f0f 0f0f0f 0f0f0f  000000 000000 000000  0f0f0f 0f0f0f 0f0f0f

import t3

FACES = {
    0: 0b000010000,
    1: 0b100000001,
    2: 0b100010001,
    3: 0b101000101,
    4: 0b101010101,
    5: 0b111000111,
    6: 0b111010111,
    7: 0b111101111,
    9: 0b111111111,
}

def main():
    num_values = 6
    velocity = 2
    value = 0
    while True:
        if t3.a.value:
            velocity = 2
        velocity *= 0.97
        if velocity < 0.05:
            velocity = 0
        value += velocity
        value %= num_values
        face = FACES[int(value)]
        for i in range(8, -1, -1):
            if (face >> i) & 1:
                if velocity:
                    t3.display[i] = t3.hls_to_rgb(value/10, 0.15, 0.1)
                else:
                    t3.display[i] = t3.hls_to_rgb(value/10, 0.26, 0.9)
            else:
                t3.display[i] = 0, 0, 0
        yield 0.01
