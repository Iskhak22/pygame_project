import pygame
import random
import math
import os
from engine.map_generator import MapGenerator
from entities.player import Player
from entities.enemy import Enemy
from structures.stack import UndoStack

class GameEngine:
    def __init__(self):
        pygame.init()
        self.tile_size = 20
        self.map_width, self.map_height = 45, 35
        self.ui_width = 250
        
        self.screen = pygame.display.set_mode((self.map_width * self.tile_size + self.ui_width, 
                                               self.map_height * self.tile_size))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Consolas', 22, bold=True)
        self.big_font = pygame.font.SysFont('Consolas', 50, bold=True)
        self.small_font = pygame.font.SysFont('Consolas', 16, bold=True)
        
        self.state = 'LOBBY'
        self.player = Player(1, 1)
        self.level = 1
        self.max_level = 3
        self.base_enemy_count = 10
        
        self.undo_stack = UndoStack()
        self.enemies = []
        self.bullets = []
        
        self.start_ticks = 0
        self.final_time = 0
        self.leaderboard_file = "leaderboard.txt"
        
        self.move_cooldown = 150 
        self.last_move_time = 0
        self.last_damage_time = 0 
        
        self.start_button_rect = pygame.Rect(0, 0, 200, 50)
        self.play_again_button_rect = pygame.Rect(0, 0, 200, 50)

    def start_game(self):
        self.level = 1
        self.player.hp = 100
        self.player.money = 0
        self.player.exp = 0
        self.player.has_gun = False
        self.start_ticks = pygame.time.get_ticks()
        self.load_new_level()
        self.state = 'PLAYING'

    def load_new_level(self):
        count = self.base_enemy_count + (self.level - 1)
        self.map_data = MapGenerator.generate_random_level(self.map_width, self.map_height, enemy_count=count)
        self.player.set_position(1, 1)
        self.enemies = []
        self.bullets = []
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.map_data[y][x] == 5:
                    self.enemies.append(Enemy(x, y))
                    self.map_data[y][x] = 0

    def update(self):
        if self.state != 'PLAYING': return
        now = pygame.time.get_ticks()
        
        # 1. Update Enemies & Collision Damage
        for e in self.enemies:
            e.update(now, (self.player.x, self.player.y), self.map_data, self.enemies)
            if e.x == self.player.x and e.y == self.player.y:
                if now - self.last_damage_time > 1000: 
                    self.player.hp -= 15 
                    self.last_damage_time = now
        
        # 2. Update Bullets
        for b in self.bullets[:]:
            b['x'] += b['vx']; b['y'] += b['vy']
            bx, by = int(b['x'] // 20), int(b['y'] // 20)
            if bx < 0 or bx >= self.map_width or by < 0 or by >= self.map_height or self.map_data[by][bx] == 1:
                if b in self.bullets: self.bullets.remove(b)
                continue
            for e in self.enemies[:]:
                if e.x == bx and e.y == by:
                    self.enemies.remove(e)
                    if b in self.bullets: self.bullets.remove(b)
                    self.player.exp += 50
                    break

        # Check for death - NO save_score here!
        if self.player.hp <= 0:
            self.state = 'GAME_OVER'

    def handle_movement(self, dx, dy):
        if self.state != 'PLAYING': return
        nx, ny = self.player.x + dx, self.player.y + dy
        if 0 <= nx < self.map_width and 0 <= ny < self.map_height:
            tile = self.map_data[ny][nx]
            if tile != 1:
                import copy
                self.undo_stack.push_state(self.player.x, self.player.y, copy.deepcopy(self.map_data))
                self.player.set_position(nx, ny)
                
                if tile == 2: # Exit Tile
                    if self.level >= self.max_level:
                        # WIN CONDITION: Calculate time and save ONLY now
                        self.final_time = (pygame.time.get_ticks() - self.start_ticks) // 1000
                        self.save_score()
                        self.state = 'YOU_WIN'
                    else:
                        self.level += 1
                        self.load_new_level()
                elif tile == 3: self.player.money += 100; self.map_data[ny][nx] = 0
                elif tile == 4: self.player.exp += 100; self.map_data[ny][nx] = 0 
                elif tile == 6: self.player.has_gun = True; self.map_data[ny][nx] = 0

    def save_score(self):
        """Saves player name and time to a file only upon winning."""
        with open(self.leaderboard_file, "a") as f:
            f.write(f"{self.player.name},{self.final_time}\n")

    def get_leaderboard(self):
        """Reads file and returns a sorted list of top 5 winning scores."""
        if not os.path.exists(self.leaderboard_file): return []
        scores = []
        try:
            with open(self.leaderboard_file, "r") as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 2:
                        scores.append((parts[0], int(parts[1])))
        except Exception as e:
            print(f"Error reading leaderboard: {e}")
            
        # DSA: Sort by fastest time (Ascending)
        scores.sort(key=lambda x: x[1])
        return scores[:5]

    def handle_continuous_input(self):
        if self.state != 'PLAYING': return
        now = pygame.time.get_ticks()
        if now - self.last_move_time < self.move_cooldown: return
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy = -1
        elif keys[pygame.K_s]: dy = 1
        elif keys[pygame.K_a]: dx = -1
        elif keys[pygame.K_d]: dx = 1
        if dx != 0 or dy != 0:
            self.handle_movement(dx, dy)
            self.last_move_time = now

    def render(self):
        if self.state == 'LOBBY': self.render_lobby()
        elif self.state in ['GAME_OVER', 'YOU_WIN']: self.render_leaderboard_screen()
        else: self.render_game()
        pygame.display.flip()

    def render_game(self):
        self.screen.fill((15, 15, 22))
        for y in range(self.map_height):
            for x in range(self.map_width):
                rect = pygame.Rect(x*20, y*20, 20, 20)
                t = self.map_data[y][x]
                if t == 1: pygame.draw.rect(self.screen, (40, 40, 50), rect)
                elif t == 2: pygame.draw.rect(self.screen, (200, 40, 40), rect)
                elif t == 3: pygame.draw.rect(self.screen, (139, 69, 19), rect.inflate(-6, -8))
                elif t == 4: pygame.draw.rect(self.screen, (30, 200, 255), rect.inflate(-6, -8))
                elif t == 6: pygame.draw.rect(self.screen, (0, 255, 0), rect.inflate(-10, -10))
        
        for e in self.enemies: pygame.draw.circle(self.screen, (220, 30, 30), (e.x*20+10, e.y*20+10), 8)
        for b in self.bullets: pygame.draw.circle(self.screen, (255, 255, 0), (int(b['x']), int(b['y'])), 3)
        pygame.draw.ellipse(self.screen, (0, 255, 150), (self.player.x*20+2, self.player.y*20+2, 16, 16))
        
        ui_x = self.map_width * 20
        pygame.draw.rect(self.screen, (30, 30, 40), (ui_x, 0, self.ui_width, 700))
        self.draw_stat_bar(ui_x+20, 85, 200, 25, self.player.hp, 100, (200, 30, 30), "HP")
        
        xp_text = self.font.render(f"XP POINTS: {self.player.exp}", True, (30, 200, 255))
        self.screen.blit(xp_text, (ui_x + 20, 130))
        
        timer_val = (pygame.time.get_ticks() - self.start_ticks)//1000 if self.state == 'PLAYING' else self.final_time
        self.screen.blit(self.font.render(f"TIME: {timer_val}s", True, (255, 255, 255)), (ui_x+20, 180))
        self.screen.blit(self.small_font.render(f"DIFFICULTY: {self.level}/{self.max_level}", True, (255, 255, 255)), (ui_x+20, 220))
        self.screen.blit(self.small_font.render(f"GOLD: ${self.player.money}", True, (255, 215, 0)), (ui_x+20, 250))

    def render_leaderboard_screen(self):
        self.screen.fill((10, 10, 20))
        color = (0, 255, 0) if self.state == 'YOU_WIN' else (255, 0, 0)
        title_text = "YOU WIN!" if self.state == 'YOU_WIN' else "YOU DIED!"
        title_surf = self.big_font.render(title_text, True, color)
        self.screen.blit(title_surf, (self.screen.get_width()//2 - title_surf.get_width()//2, 50))
        
        lb_rect = pygame.Rect(0, 0, 400, 300); lb_rect.center = (self.screen.get_width()//2, 280)
        pygame.draw.rect(self.screen, (30, 30, 45), lb_rect); pygame.draw.rect(self.screen, (200, 200, 200), lb_rect, 2)
        
        header = self.font.render("--- TOP 5 CHAMPIONS ---", True, (255, 215, 0))
        self.screen.blit(header, (lb_rect.x + 60, lb_rect.y + 20))
        
        scores = self.get_leaderboard()
        for i, (name, time_val) in enumerate(scores):
            entry = self.font.render(f"{i+1}. {name[:10]:<10} {time_val}s", True, (255, 255, 255))
            self.screen.blit(entry, (lb_rect.x + 50, lb_rect.y + 70 + (i * 40)))

        self.play_again_button_rect.center = (self.screen.get_width()//2, 550)
        pygame.draw.rect(self.screen, (0, 100, 200), self.play_again_button_rect)
        self.screen.blit(self.font.render("PLAY AGAIN", True, (255, 255, 255)), (self.play_again_button_rect.x+45, self.play_again_button_rect.y+12))

    def render_lobby(self):
        self.screen.fill((20, 20, 30))
        self.start_button_rect.center = (self.screen.get_width() // 2, 400)
        pygame.draw.rect(self.screen, (0, 150, 0), self.start_button_rect)
        t_surf = self.font.render("DUNGEON DATA STRUCTURES", True, (255, 255, 255))
        n_surf = self.font.render(f"ENTER NAME: {self.player.name}_", True, (0, 255, 150))
        b_surf = self.font.render("START GAME", True, (255, 255, 255))
        self.screen.blit(t_surf, (self.screen.get_width()//2 - t_surf.get_width()//2, 150))
        self.screen.blit(n_surf, (self.screen.get_width()//2 - n_surf.get_width()//2, 250))
        self.screen.blit(b_surf, (self.start_button_rect.x + 40, self.start_button_rect.y + 12))

    def draw_stat_bar(self, x, y, w, h, cur, mx, col, label):
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, w, h))
        fill = int((max(0, cur)/mx)*w) if mx > 0 else 0
        pygame.draw.rect(self.screen, col, (x, y, fill, h))
        pygame.draw.rect(self.screen, (200, 200, 200), (x, y, w, h), 2)
        txt = self.small_font.render(f"{label}: {int(cur)}", True, (255, 255, 255))
        self.screen.blit(txt, (x + w//2 - txt.get_width()//2, y + h//2 - txt.get_height()//2))

    def shoot(self, mouse_pos):
        if self.state != 'PLAYING' or not self.player.has_gun: return
        px, py = self.player.x * 20 + 10, self.player.y * 20 + 10
        dx, dy = mouse_pos[0] - px, mouse_pos[1] - py
        dist = math.hypot(dx, dy)
        if dist > 0: self.bullets.append({'x': px, 'y': py, 'vx': (dx/dist)*12, 'vy': (dy/dist)*12})

    def undo(self):
        if self.state != 'PLAYING': return
        state = self.undo_stack.pop_state()
        if state: self.player.set_position(state['x'], state['y']); self.map_data = state['map']