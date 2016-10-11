
_t3_emulated = True

MISSING = object()

_pressed_button_pins = set()

_pin_objects = {}

class Pin:
    IN = object()
    OUT = object()
    PULL_UP = object()
    IRQ_FALLING = object()
    IRQ_RISING = object()

    def __init__(self, number, mode, pull=MISSING):
        if number in (5, 15):
            assert mode == Pin.OUT
        else:
            assert mode == Pin.IN
            assert pull == Pin.PULL_UP
        self._num = number
        self._mode = mode

        _pin_objects[number] = self

    def value(self):
        assert self._mode == Pin.IN
        return self._num not in _pressed_button_pins


class PWM:
    def __init__(self, pin):
        assert pin._num == 15
        self._freq = 0
        self._duty = 0

    def init(self, freq, duty):
        self._freq = freq
        self._duty = duty
        self._update()

    def freq(self, freq=None):
        if freq == None:
            return self._freq
        else:
            self._freq = freq
            self._update()

    def duty(self, duty=None):
        if duty == None:
            return self._duty
        else:
            self._duty = duty
            self._update()

    def deinit(self):
        self._freq = 0
        self._duty = 0
        self._update()

    def _update(self):
        print('@', self._freq, self._duty)
