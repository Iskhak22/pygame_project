import pygame

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.move_speed = 400  # Milliseconds between moves
        self.last_move_time = pygame.time.get_ticks()

    def update(self, current_time, player_pos, grid, other_enemies):
        px, py = player_pos
        # Relentless pursuit logic
        if current_time - self.last_move_time > self.move_cooldown(px, py):
            self.move_towards(px, py, grid, other_enemies)
            self.last_move_time = current_time

    def move_cooldown(self, px, py):
        # Slightly speed up if far away to keep pressure on
        dist = abs(self.x - px) + abs(self.y - py)
        return max(200, self.move_speed - (dist * 2))

    def move_towards(self, px, py, grid, other_enemies):
        # Calculate potential moves
        dx = 1 if px > self.x else -1 if px < self.x else 0
        dy = 1 if py > self.y else -1 if py < self.y else 0
        
        # Try to move in the direction of the greatest distance first
        if abs(px - self.x) > abs(py - self.y):
            if self.is_valid(self.x + dx, self.y, grid, other_enemies):
                self.x += dx
            elif self.is_valid(self.x, self.y + dy, grid, other_enemies):
                self.y += dy
        else:
            if self.is_valid(self.x, self.y + dy, grid, other_enemies):
                self.y += dy
            elif self.is_valid(self.x + dx, self.y, grid, other_enemies):
                self.x += dx

    def is_valid(self, nx, ny, grid, other_enemies):
        # Basic bounds and wall check
        if nx < 0 or nx >= len(grid[0]) or ny < 0 or ny >= len(grid): return False
        if grid[ny][nx] == 1: return False
        # Don't overlap with other enemies
        for e in other_enemies:
            if e != self and e.x == nx and e.y == ny: return False
        return True