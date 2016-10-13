import t3
import sys

if not hasattr(t3.machine, '_t3_emulated'):
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    ap = network.WLAN(network.AP_IF)
    ap.active(False)

def delay(n, other):
    yield n
    yield from other


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

    while True:
        current_frame += 1
        current_frame %= len(current_item.data)
        wait, pixels = current_item.data[current_frame]
        for i, pixel in enumerate(pixels):
            t3.display[i] = pixel

        buttons = yield wait

        if buttons.pressed[t3.left]:
            current_item = current_item.get_prev()
        if buttons.pressed[t3.right]:
            current_item = current_item.get_next()
        if buttons.pressed[t3.a]:
            selected_name = current_item.name[:-3]
            break

    with open('selected-game', 'w') as f:
        f.write(selected_name)
    for i in range(9):
        t3.display[i] = 0, 2, 2
        t3.display.write_now()
    t3.machine.reset()


# 1/5  000000 000000 000000  000000 000000 000000  000000 000000 000000
