import time
from machine import Pin
from neopixel import NeoPixel

np = NeoPixel(Pin(5, Pin.OUT), 9)

def anim_turn_on(n):
    for i in range(0, 255, 10):
        np[n] = i/3, i/2, i
        np.write()
        time.sleep(1/120)

anim_turn_on(2)
anim_turn_on(1)
anim_turn_on(0)
anim_turn_on(4)
anim_turn_on(7)

time.sleep(10000)
