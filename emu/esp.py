
def neopixel_write(pin, data, flag):
    assert pin._num == 5
    assert flag
    assert len(data) == 9 * 3, len(data)
    print('*', bytes(data))
