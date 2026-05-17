import pygame

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.move_speed = 500 
        self.last_move_time = pygame.time.get_ticks()

    def update(self, current_time, player_pos, grid, other_enemies):
        px, py = player_pos
        if current_time - self.last_move_time > self.move_speed:
            self.move_towards(px, py, grid, other_enemies)
            self.last_move_time = current_time

    def move_towards(self, px, py, grid, other_enemies):
        dx = 1 if px > self.x else -1 if px < self.x else 0
        dy = 1 if py > self.y else -1 if py < self.y else 0
        
        # Try horizontal then vertical
        if self.is_valid(self.x + dx, self.y, grid, other_enemies):
            self.x += dx
        elif self.is_valid(self.x, self.y + dy, grid, other_enemies):
            self.y += dy

    def is_valid(self, nx, ny, grid, other_enemies):
        if nx < 0 or nx >= len(grid[0]) or ny < 0 or ny >= len(grid): return False
        if grid[ny][nx] == 1 or grid[ny][nx] == 2: return False
        for e in other_enemies:
            if e != self and e.x == nx and e.y == ny: return False
        return True