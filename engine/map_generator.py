import random
from collections import deque

class MapGenerator:
    @staticmethod
    def generate_random_level(width, height):
        while True:
            grid = [[1 for _ in range(width)] for _ in range(height)]
            for y in range(1, height - 1):
                for x in range(1, width - 1):
                    if random.random() > 0.18: grid[y][x] = 0

            grid[1][1] = 0
            grid[1][2] = 6 
            grid[height - 2][width - 2] = 2 

            for t, count in [(3, 10), (4, 8), (5, 12)]:
                placed = 0
                while placed < count:
                    rx, ry = random.randint(1, width-2), random.randint(1, height-2)
                    if grid[ry][rx] == 0 and (rx, ry) != (1, 1):
                        grid[ry][rx] = t
                        placed += 1

            if MapGenerator.is_path_valid(grid, (1, 1), (width - 2, height - 2)):
                return grid

    @staticmethod
    def is_path_valid(grid, start, exit_pos):
        q = deque([start])
        v = {start}
        while q:
            cx, cy = q.popleft()
            if (cx, cy) == exit_pos: return True
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid):
                    if grid[ny][nx] != 1 and (nx, ny) not in v:
                        v.add((nx, ny)); q.append((nx, ny))
        return False