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

#COLORS = (t3.hls_to_rgb(0, 0, 0),) + \
#    tuple(t3.hls_to_rgb(hue/360, 0.5, 1) for hue in HUES)



grid = [[0] * SIZE for y in range(SIZE)]
last_grid = [[0] * SIZE for y in range(SIZE)]

def log(*args, **kwargs):
    print("###", *args, **kwargs)

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

def fill_grid(grid, value):
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            grid[y][x] = value

def move_grid(direction):
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

def add_rand_tile(force=False):
    free_tiles = []
    for y in range(SIZE):
        for x in range(SIZE):
            if not grid[y][x]:
                free_tiles.append((y, x))
    
    if not free_tiles:
        return False
    
    chance = min((len(free_tiles) / SIZE**2) + 0.3, 1.0)
    log("chance for new tile:", chance)
    if randrange(0, 256) <= chance*256:    
        y, x = free_tiles[randrange(0, len(free_tiles))]
        grid[y][x] = 1
        
    return True

def render_grid(delta):
    out = [[-1] * SIZE for y in range(SIZE)]
    for y, row in enumerate(grid):
        for x, tile in enumerate(row):
            last_tile = last_grid[y][x]
            if tile and last_tile:
                last_hue = HUES[last_tile]
                new_hue = HUES[tile]
                
                if last_hue < new_hue:
                    last_hue += 360
                
                hue = (last_hue + ((new_hue - last_hue) * delta)) % 360
                lit = 0.5
            elif tile:
                hue = HUES[tile]
                lit = delta/2
            elif last_tile:
                hue = HUES[last_tile]
                lit = (1 - delta)/2
            else:
                hue = 0
                lit = 0
                
                out
            out[y][x] = t3.hls_to_rgb(hue/360, lit, 1)
    return out

def draw(display):
    for y in range(SCREEN_SIZE):
        for x in range(SCREEN_SIZE):
            t3.display[x, y] = display[y][x]

def main():
    global last_grid # XXX
    pressed = set()
    while True:
        fill_grid(grid, 0)
        fill_grid(last_grid, 0)
        add_rand_tile()
        i = 0
        delta = 0
        animate = True
        while True:
            if t3.b.value:
                break
            
            last_pressed = pressed
            pressed = set()
            for direction in DIRECTION_TO_T3:
                if DIRECTION_TO_T3[direction].value:
                    pressed.add(direction)
            
            newly_pressed = pressed - last_pressed
            
            for direction in newly_pressed:
                #global last_grid
                last_grid = [row.copy() for row in grid] # XXX
                move_grid(direction)
                
                add_rand_tile()
                
                delta = 0
                animate = True
            
            if animate:
                if delta > 1:
                    delta = 1
                    animate = False
                draw(render_grid(delta))
                delta += 0.05
            yield 0.01
        
        yield 0.01
