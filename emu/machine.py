
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
        if number in (4, 5):
            assert mode == Pin.OUT
        else:
            assert mode == Pin.IN
            assert pull == Pin.PULL_UP
        self._num = number
        self._mode = mode
        self._fall_callback = self._rise_callback = lambda: None

        _pin_objects[number] = self

    def value(self):
        assert self._mode == Pin.IN
        return self._num not in _pressed_button_pins

    def irq(self, *, trigger, handler):
        if trigger == Pin.IRQ_FALLING:
            self._fall_callback = handler
        elif trigger == Pin.IRQ_RISING:
            self._rise_callback = handler
