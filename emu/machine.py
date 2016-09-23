
_t3_emulated = True

MISSING = object()

_pressed_button_pins = set()

class Pin:
    IN = object()
    OUT = object()

    def __init__(self, number, mode):
        if number in (4, 5):
            assert mode == Pin.OUT
        else:
            assert mode == Pin.IN
        self._num = number
        self._mode = mode

    def value(self):
        assert self._mode == Pin.IN
        return self._num in _pressed_button_pins
