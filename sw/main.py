import t3

if not hasattr(t3.machine, '_t3_emulated'):
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    ap = network.WLAN(network.AP_IF)
    ap.active(False)

def args(*a):
    return a


def delay(n, other):
    yield n
    yield from other


def anim_starter(func, anims):
    for i, args in enumerate(anims):
        if args is not None:
            t3.start_task(func(*args))
            yield 1/10


def bluish():
    hue = t3.random_uniform(0.43, 0.67)
    sat = 0.26
    lightness = 0.4
    return t3.hls_to_rgb(hue, sat, lightness)


def reddish():
    hue = t3.random_uniform(-0.07, 0.07)
    sat = 0.26
    lightness = 0.4
    return t3.hls_to_rgb(hue, sat, lightness)


t3.start_task(anim_starter(t3.display.anim_pixel, (
    args((1, 0), *bluish()),
    args((0, 0), *bluish()),
    args((2, 0), *bluish()),
    args((1, 1), *bluish()),
    args((1, 2), *bluish()),
)))


t3.start_task(delay(0.7, anim_starter(t3.display.anim_pixel, (
    (2, 0, 0, 0),
    (0, 0, 0, 0),
    (1, 0, 0, 0),
    None,
    (7, 0, 0, 0),
))))


t3.start_task(delay(1, anim_starter(t3.display.anim_pixel, (
    args(8, *reddish()),
    args(0, *reddish()),
    None,
    None,
    args(4, *reddish()),
))))


t3.start_task(delay(1.7, anim_starter(t3.display.anim_pixel, (
    (8, 0, 0, 0),
    (0, 0, 0, 0),
    None,
    None,
    (4, 0, 0, 0, 25),
))))


class MenuItem:
    def __init__(self, name):
        self.name = name

    def get_next(self):
        while not self.next.ensure_loaded():
            self.next.next.prev = self
            self.next = self.next.next
            if self.next is self:
                raise RuntimeError('No usable files')
        return self.next

    def get_prev(self):
        while not self.prev.ensure_loaded():
            self.prev.prev.next = self
            self.prev = self.prev.prev
            if self.prev is self:
                raise RuntimeError('No usable files')
        return self.prev

    def ensure_loaded(self):
        try:
            return self.data
        except AttributeError:
            try:
                self.data = self.load()
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.data = None
            return self.data

    def load(self):
        with open(self.name) as f:
            if f.readline().strip() != '# T3 Cartridge':
                return None
            items = []
            for line in f:
                if not line.startswith('# '):
                    break
                parts = line[1:].strip().split()
                parts_duration = parts[0].split('/')
                duration = float(parts_duration[0])
                for part in parts_duration[1:]:
                    duration /= float(part)
                pixels = [(int(p[:2], 16), int(p[2:4], 16), int(p[4:], 16))
                          for p in parts[1:]]
                items.append((duration, pixels))
            return items

    def __repr__(self):
        return '<{}: {}>'.format(type(self).__name__, self.name)


def main_menu():
    items = list(MenuItem(n) for n in t3.listdir() if n.endswith('.py'))
    for item, prev, nxt in zip(items, [items[-1]] + items, items[1:] + [items[0]]):
        item.prev = prev
        item.next = nxt
    current_item = items[0].get_next()
    current_frame = -1

    loop = True
    def button_handler(buttons):
        nonlocal current_item, loop
        if buttons.pressed[t3.left]:
            current_item = current_item.get_prev()
        if buttons.pressed[t3.right]:
            current_item = current_item.get_next()
        if buttons.pressed[t3.a]:
            loop = False
            t3.set_button_handler(None)
            ns = {}
            module = __import__(current_item.name[:-3])
            t3.start_task(module.main())

    t3.set_button_handler(button_handler)

    while loop:
        current_frame += 1
        current_frame %= len(current_item.data)
        wait, pixels = current_item.data[current_frame]
        for i, pixel in enumerate(pixels):
            t3.display[i] = pixel
        yield wait


t3.start_task(delay(2.7, main_menu()))


t3.start_task(t3._sys_task())


t3.run()

# 1/5  000000 000000 000000  000000 000000 000000  000000 000000 000000
