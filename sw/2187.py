# T3 Cartridge
# 1/5  000000 000000 000000  000000 666600 000000  000000 000000 000000

#from enum import Enum
import t3
from t3 import randrange

SIZE = 3
SCREEN_SIZE = 3

#            1   2  3    4    5    6    7    8   9  10
#            2   4  8   16   32   64  128  256 512 1024
HUES = (-1, 56, 30, 0, 300, 240, 180, 157, 130, 93, 70)

#class Direction(Enum):
class Direction():
    up = 1
    right = 2
    down = 3
    left = 4

DIRECTION_TO_T3 = {Direction.up: t3.up, Direction.right: t3.right,
    Direction.down: t3.down, Direction.left: t3.left}

DIRECTION_VALUES = {
    # y start, x start, y next, x next, y vector, x vector
    Direction.up:    (1,              0,  1,  1, -1,  0), # U
    Direction.right: (0,         SIZE-2,  1, -1,  0,  1), # R
    Direction.down:  (SIZE-2,         0, -1,  1,  1,  0), # D
    Direction.left:  (0,              1,  1,  1,  0, -1), # L
}

def log(*args, **kwargs):
    print("###", *args, **kwargs)
    
def fill_grid(grid, value):
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            grid[y][x] = value

def draw(display):
    for y in range(SCREEN_SIZE):
        for x in range(SCREEN_SIZE):
            t3.display[x, y] = display[y][x]

class TwoOneEightSeven():
    def __init__(self):
        self.grid = [[0] * SIZE for y in range(SIZE)]
        self.animation_steps = []
    
    def init_game(self):
        fill_grid(self.grid, 0)
        self.make_animation_step()
        self.add_rand_tile()
        self.make_animation_step()
        self.delta = 0
        self.animate = True
    
    def move_grid(self, direction):
        grid = self.grid
        y_start, x_start, y_next, x_next, y_vec, x_vec = DIRECTION_VALUES[direction]
        y = y_start
        for i in range(SIZE):
            if y not in range(SIZE): continue
            x = x_start
            for j in range(SIZE):
                if x not in range(SIZE): continue
                log(i, '.', y, x, '-', grid[y][x])
                if not grid[y][x]:
                    pass
                elif grid[y][x] and not grid[y+y_vec][x+x_vec]:
                    grid[y+y_vec][x+x_vec] = grid[y][x]
                    grid[y][x] = 0
                elif grid[y][x] == grid[y+y_vec][x+x_vec]:
                    grid[y+y_vec][x+x_vec] += 1
                    grid[y][x] = 0
                
                x += x_next
            y += y_next

    def add_rand_tile(self, force=False):
        free_tiles = []
        for y in range(SIZE):
            for x in range(SIZE):
                if not self.grid[y][x]:
                    free_tiles.append((y, x))
        
        if not free_tiles:
            return False
        
        chance = min((len(free_tiles) / SIZE**2) + 0.3, 1.0)
        log("chance for new tile:", chance)
        if randrange(0, 256) <= chance*256:    
            y, x = free_tiles[randrange(0, len(free_tiles))]
            self.grid[y][x] = 1
            
        return True

    def render_grid(self, delta):
        out = [[-1] * SIZE for y in range(SIZE)]
        animation_index = int(delta * (len(self.animation_steps)-1))
        for y in range(SCREEN_SIZE):
            for x in range(SCREEN_SIZE):
                last_tile = self.animation_steps[animation_index][y][x]
                if delta < 1.0:
                    tile = self.animation_steps[animation_index+1][y][x]
                else:
                    tile = last_tile
                
                d = delta * (len(self.animation_steps)-1) % 1.0
                
                if tile and last_tile:
                    last_hue = HUES[last_tile]
                    new_hue = HUES[tile]
                    
                    if last_hue < new_hue:
                        last_hue += 360
                    
                    # TODO merges should definitely look different
                    # from being replaced with a tile
                    
                    hue = (last_hue + ((new_hue - last_hue) * d)) % 360
                    lit = 0.5
                elif tile:
                    hue = HUES[tile]
                    lit = d/2
                elif last_tile:
                    hue = HUES[last_tile]
                    lit = (1 - d)/2
                else:
                    hue = 0
                    lit = 0
                    
                    out
                out[y][x] = t3.hls_to_rgb(hue/360, lit, 1)
        return out

    def make_animation_step(self):
        self.animation_steps.append([row.copy() for row in self.grid])

    def step(self, newly_pressed):
        for direction in newly_pressed:
            self.animation_steps = []
            
            self.make_animation_step()
            self.move_grid(direction)
            
            self.make_animation_step()
            self.add_rand_tile()
            
            self.make_animation_step()
            
            self.delta = 0
            self.animate = True
        
        if self.animate:
            if self.delta > 1:
                self.delta = 1
                self.animate = False
            draw(self.render_grid(self.delta))
            self.delta += 0.01


def main():
    pressed = set()
    game = TwoOneEightSeven()
    game.init_game()
    while True:
        if t3.b.value:
            break
        
        last_pressed = pressed
        pressed = set()
        for direction in DIRECTION_TO_T3:
            if DIRECTION_TO_T3[direction].value:
                pressed.add(direction)
        
        newly_pressed = pressed - last_pressed
        
        game.step(newly_pressed)
        yield 0.01
