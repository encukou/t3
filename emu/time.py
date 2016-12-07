from utime import *


# Newer versions of MicroPython change the order of arguments for ticks_diff
# from (old_time, new_time) to (new_time, old_time).
# t3 uses the old semantics for now (but that's subject to change when
# the author switches to a new MicroPython release for ESP8266).
# Meanwhile, use the absolute value of the time difference, since we don't
# really run into wraparound situations or scheduling.
# See here for details: https://forum.micropython.org/viewtopic.php?t=2589

_old_ticks_diff = ticks_diff

def ticks_diff(a, b):
    return abs(_old_ticks_diff(a, b))
