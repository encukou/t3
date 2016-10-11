import sys

NUM_PIXELS = 9

class _NeoPixel():
    def __init__(self):
        self._data = [(0, 0, 0) for i in range(NUM_PIXELS)]
        self._committed = [(0, 100, 0) for i in range(NUM_PIXELS)]

    def __getitem__(self, n):
        return self._data[n]

    def __setitem__(self, n, data):
        r, g, b = data
        self._data[n] = r, g, b

    def write(self):
        self._committed = list(tuple(x) for x in self._data)
        print('*', self._committed)

_strip = _NeoPixel()


def NeoPixel(pin, num):
    assert pin._num == 5
    assert num == NUM_PIXELS
    return _strip
