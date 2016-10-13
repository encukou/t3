# T3 Cartridge
# 1/5  0f0000 000000 000000  000000 000000 000000  000000 000000 000000
# 1/5  0f0000 000000 000000  000000 0f0000 000000  000000 000000 000000
# 1/5  0f0000 000000 000000  000000 0f0000 000000  000000 000000 0f0000
# 1/5  000000 000000 00000f  000000 000000 000000  000000 000000 000000
# 1/5  000000 000000 00000f  000000 00000f 000000  000000 000000 000000
# 1/5  000000 000000 00000f  000000 00000f 000000  00000f 000000 000000
# 1/5  000000 0f0000 000000  000000 000000 000000  000000 000000 000000
# 1/5  000000 0f0000 000000  000000 0f0000 000000  000000 000000 000000
# 1/5  000000 0f0000 000000  000000 0f0000 000000  000000 0f0000 000000
# 1/5  000000 000000 000000  000000 000000 00000f  000000 000000 000000
# 1/5  000000 000000 000000  000000 00000f 00000f  000000 000000 000000
# 1/5  000000 000000 000000  00000f 00000f 00000f  000000 000000 000000

import t3

BLACK = 0, 0, 0
HEAD = 10, 10, 5

COLORS = (
    (0, 0, 20),
    (20, 0, 0),
    (0, 20, 0),
    (20, 20, 0),
    (20, 0, 20),
    (0, 20, 20),
    (20, 20, 20),
)
N_COLORS = len(COLORS)

LINES = (
    ((0, 0), (1, 1), (2, 2)),
    ((0, 2), (1, 1), (2, 0)),
    ((0, 0), (0, 1), (0, 2)),
    ((1, 0), (1, 1), (1, 2)),
    ((2, 0), (2, 1), (2, 2)),
    ((0, 0), (1, 0), (2, 0)),
    ((0, 1), (1, 1), (2, 1)),
    ((0, 2), (1, 2), (2, 2)),
)

class PlayerChooser:
    def __init__(self):
        self.no_players = 1
        self.player_colors = [0, 1]
        self.cpu_first = False

    def choose(self):
        def update_screen():
            pc = self.player_colors
            if self.no_players == 1:
                colors = (BLACK, HEAD, BLACK,
                          BLACK if self.cpu_first else COLORS[pc[1]],
                          COLORS[pc[0]],
                          COLORS[pc[1]] if self.cpu_first else BLACK,
                          BLACK, COLORS[pc[0]], BLACK)
            else:
                colors = (HEAD, BLACK, HEAD,
                          COLORS[pc[0]], BLACK, COLORS[pc[1]],
                          COLORS[pc[0]], BLACK, COLORS[pc[1]])
            for i, color in enumerate(colors):
                t3.display[i] = color

        update_screen()
        while True:
            buttons = yield t3.wait_for_input()

            if buttons.pressed[t3.left] or buttons.pressed[t3.right]:
                self.no_players = 3-self.no_players

            if buttons.pressed[t3.up] or buttons.pressed[t3.down]:
                direction = 1 if buttons.pressed[t3.up] else -1
                if self.no_players == 1:
                    self.player_colors[0] = (self.player_colors[0] + direction) % N_COLORS
                    if self.player_colors[0] == self.player_colors[1]:
                        if self.player_colors[0] == 1:
                            self.player_colors[1] = 0
                        else:
                            self.player_colors[1] = 1
                else:
                    self.player_colors[1] = (self.player_colors[1] + direction) % N_COLORS
                    if self.player_colors[0] == self.player_colors[1]:
                        self.player_colors[1] = (self.player_colors[1] + direction) % N_COLORS

            if buttons.pressed[t3.b] and self.no_players == 1:
                self.cpu_first = not self.cpu_first

            update_screen()

            if buttons.pressed[t3.a]:
                break

        if self.no_players == 1:
            if self.cpu_first:
                return CPUPlayer(self.player_colors[1]), HumanPlayer(self.player_colors[0])
            else:
                return HumanPlayer(self.player_colors[0]), CPUPlayer(self.player_colors[1])
        else:
            return HumanPlayer(self.player_colors[0]), HumanPlayer(self.player_colors[1])


class Player:
    def __init__(self, color):
        self.color = color


def permutations(line):
    a, b, c = line
    perms = [
        (a, b, c),
        (a, c, b),
        (b, a, c),
        (b, c, a),
        (c, a, b),
        (c, b, a),
    ]
    while perms:
        n = t3.randrange(0, len(perms))
        yield perms[n]
        del perms[n]


class CPUPlayer(Player):
    def choose(self, field):
        yield 0.1
        # Finish own line
        for line in LINES:
            for a, b, c in permutations(line):
                if self.color == field[a] == field[b] and field[c] == -1:
                    return c
        # Mess up opponent's lines
        for line in LINES:
            for a, b, c in permutations(line):
                if -1 != field[a] == field[b] and field[c] == -1:
                    return c
        # Play in the center, corners, or sides
        for p in ((1, 1),
                  (0, 0), (0, 2), (2, 0), (2, 2),
                  (0, 1), (2, 1), (1, 0), (1, 2)):
            if field[p] == -1:
                return p
        for x in range(3):
            for y in range(3):
                if field[x, y] == -1:
                    return x, y


class HumanPlayer(Player):
    def choose(self, field):
        for x in 1, 0, 2:
            for y in 1, 0, 2:
                if field[x, y] == -1:
                    break
            if field[x, y] == -1:
                break
        xy = [x, y]

        _tries = ((0, 1, 2, 0), (1, 0, 2, 1), (2, 1, 0, 2))

        while True:
            for time, color in (
                        (1/10, (0, 0, 0)),
                        (1/10, COLORS[self.color]),
                        (1/10, (0, 0, 0)),
                        (1/10, COLORS[self.color]),
                    ):
                draw_field(field)
                t3.display[xy[0], xy[1]] = color
                buttons = yield time
                for btn, axis, direction in (
                            (t3.left, 0, -1),
                            (t3.right, 0, 1),
                            (t3.down, 1, 1),
                            (t3.up, 1, -1),
                        ):
                    if buttons.pressed[btn]:
                        while True:
                            xy[axis] = (xy[axis] + direction) % 3
                            for xy[1-axis] in _tries[xy[1-axis]]:
                                if field[xy[0], xy[1]] == -1:
                                    break
                            if field[xy[0], xy[1]] == -1:
                                break
                if buttons.pressed[t3.a]:
                    return xy


def draw_field(field):
    for x in range(3):
        for y in range(3):
            color = field[x, y]
            if color == -1:
                t3.display[x, y] = 0, 0, 0
            else:
                t3.display[x, y] = COLORS[color]


def victory_anim(field, line):
    while True:
        draw_field(field)
        for x, y in line:
            t3.start_task(t3.display.anim_pixel((x, y), 70, 70, 70, 10))
            if (yield 1/8).pressed[t3.b]:
                return
        if (yield 1/5).pressed[t3.b]:
            return
        for x, y in line:
            t3.start_task(t3.display.anim_pixel((x, y), *COLORS[field[x, y]],
                                                steps=10))
        if (yield 1/3).pressed[t3.b]:
            return


def tie_anim(field):
    for i in range(5):
        draw_field(field)
        yield 1/5
        for i in range(9):
            t3.display[i] = 0, 0, 0
        yield 1/10

def main():
    chooser = PlayerChooser()
    players = yield from chooser.choose()

    while True:
        field = {(x, y): -1 for x in range(3) for y in range(3)}
        for i in range(9):
            player = players[0]
            x, y = yield from player.choose(field)
            field[x, y] = player.color

            draw_field(field)

            for a, b, c in LINES:
                if -1 != field[a] == field[b] == field[c]:
                    yield from victory_anim(field, (a, b, c))
                    yield 1/5
                    break
            else:
                players = players[1], players[0]
                continue

            players = yield from chooser.choose()
            break
        else:
            yield from tie_anim(field)
