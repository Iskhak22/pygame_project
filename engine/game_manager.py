import pygame
import random
import math
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
        
        # GAME STATES: 'LOBBY', 'PLAYING', 'GAME_OVER'
        self.state = 'LOBBY'
        self.player = Player(1, 1)
        self.level = 1
        self.undo_stack = UndoStack()
        self.enemies = []
        self.bullets = []
        
        self.start_button_rect = pygame.Rect(0, 0, 200, 50)
        self.restart_button_rect = pygame.Rect(0, 0, 200, 50)

    def load_new_level(self):
        self.map_data = MapGenerator.generate_random_level(self.map_width, self.map_height)
        self.player.set_position(1, 1)
        self.enemies = []
        self.bullets = []
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.map_data[y][x] == 5:
                    self.enemies.append(Enemy(x, y))
                    self.map_data[y][x] = 0

    def restart_game(self):
        self.level = 1
        self.player.hp = 100
        self.player.money = 0
        self.player.exp = 0
        self.player.has_gun = False
        self.load_new_level()
        self.state = 'PLAYING'

    def shoot(self, mouse_pos):
        if self.state != 'PLAYING' or not self.player.has_gun: return
        px, py = self.player.x * 20 + 10, self.player.y * 20 + 10
        dx, dy = mouse_pos[0] - px, mouse_pos[1] - py
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.bullets.append({'x': px, 'y': py, 'vx': (dx/dist)*12, 'vy': (dy/dist)*12})

    def update(self):
        if self.state != 'PLAYING': return
        
        now = pygame.time.get_ticks()
        # 1. Update Enemies
        for e in self.enemies:
            e.update(now, (self.player.x, self.player.y), self.map_data, self.enemies)
            if e.x == self.player.x and e.y == self.player.y:
                self.player.hp -= 0.8

        # 2. Update Bullets
        for b in self.bullets[:]:
            b['x'] += b['vx']
            b['y'] += b['vy']
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

        if self.player.hp <= 0:
            self.state = 'GAME_OVER'

    def handle_movement(self, dx, dy):
        if self.state != 'PLAYING': return
        nx, ny = self.player.x + dx, self.player.y + dy
        
        if 0 <= nx < self.map_width and 0 <= ny < self.map_height:
            tile = self.map_data[ny][nx]
            if tile != 1: # Not a wall
                import copy
                # Save current state BEFORE moving for UNDO
                self.undo_stack.push_state(self.player.x, self.player.y, copy.deepcopy(self.map_data))
                
                self.player.set_position(nx, ny)
                
                # --- INTERACTION LOGIC ---
                if tile == 3: # GOLD CHEST
                    self.player.money += 100
                    self.map_data[ny][nx] = 0 # Remove gold from map
                elif tile == 4: # XP CHEST
                    self.player.exp += 40
                    self.map_data[ny][nx] = 0 # Remove XP from map
                elif tile == 6: # GUN PICKUP
                    self.player.has_gun = True
                    self.map_data[ny][nx] = 0 # Remove Gun from map
                elif tile == 2: # EXIT
                    self.level += 1
                    self.load_new_level()

    def undo(self):
        if self.state != 'PLAYING': return
        state = self.undo_stack.pop_state()
        if state:
            self.player.set_position(state['x'], state['y'])
            self.map_data = state['map']

    def render(self):
        if self.state == 'LOBBY':
            self.render_lobby()
        elif self.state == 'GAME_OVER':
            self.render_game_over()
        else:
            self.render_game()
        pygame.display.flip()

    def render_lobby(self):
        self.screen.fill((20, 20, 30))
        self.start_button_rect.center = (self.screen.get_width() // 2, 400)
        pygame.draw.rect(self.screen, (0, 150, 0), self.start_button_rect)
        
        t_surf = self.font.render("DUNGEON DATA STRUCTURES", True, (255, 255, 255))
        n_surf = self.font.render(f"NAME: {self.player.name}_", True, (0, 255, 150))
        b_surf = self.font.render("START", True, (255, 255, 255))
        
        self.screen.blit(t_surf, (self.screen.get_width()//2 - t_surf.get_width()//2, 150))
        self.screen.blit(n_surf, (self.screen.get_width()//2 - n_surf.get_width()//2, 250))
        self.screen.blit(b_surf, (self.start_button_rect.x + 65, self.start_button_rect.y + 12))

    def render_game_over(self):
        self.render_game()
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0,0))
        
        msg_box = pygame.Rect(0, 0, 400, 250)
        msg_box.center = (self.screen.get_width() // 2, self.screen.get_height() // 2)
        pygame.draw.rect(self.screen, (40, 40, 40), msg_box)
        pygame.draw.rect(self.screen, (200, 0, 0), msg_box, 3)
        
        lose_surf = self.big_font.render("YOU LOSE!", True, (255, 50, 50))
        self.restart_button_rect.center = (msg_box.centerx, msg_box.centery + 50)
        pygame.draw.rect(self.screen, (0, 100, 200), self.restart_button_rect)
        res_text = self.font.render("RESTART", True, (255, 255, 255))
        
        self.screen.blit(lose_surf, (msg_box.centerx - lose_surf.get_width()//2, msg_box.centery - 70))
        self.screen.blit(res_text, (self.restart_button_rect.x + 55, self.restart_button_rect.y + 12))

    def render_game(self):
        self.screen.fill((15, 15, 22))
        # 1. Draw Map
        for y in range(self.map_height):
            for x in range(self.map_width):
                rect = pygame.Rect(x*20, y*20, 20, 20)
                t = self.map_data[y][x]
                if t == 1: pygame.draw.rect(self.screen, (40, 40, 50), rect)
                elif t == 2: pygame.draw.rect(self.screen, (200, 40, 40), rect)
                elif t == 3: pygame.draw.rect(self.screen, (139, 69, 19), rect.inflate(-6, -8))
                elif t == 4: pygame.draw.rect(self.screen, (30, 100, 200), rect.inflate(-6, -8))
                elif t == 6: pygame.draw.rect(self.screen, (0, 255, 0), rect.inflate(-10, -10))
        
        # 2. Draw Entities
        for e in self.enemies:
            pygame.draw.circle(self.screen, (220, 30, 30), (e.x*20+10, e.y*20+10), 8)
        for b in self.bullets:
            pygame.draw.circle(self.screen, (255, 255, 0), (int(b['x']), int(b['y'])), 3)
        pygame.draw.ellipse(self.screen, (0, 255, 150), (self.player.x*20+2, self.player.y*20+2, 16, 16))
        
        # 3. Sidebar UI
        ui_x = self.map_width * 20
        pygame.draw.rect(self.screen, (30, 30, 40), (ui_x, 0, self.ui_width, self.map_height*20))
        
        # Stats Labels
        name_label = self.font.render(f"{self.player.name.upper()}", True, (255, 255, 255))
        self.screen.blit(name_label, (ui_x + 20, 20))
        
        # Health & XP Bars
        self.draw_stat_bar(ui_x+20, 85, 200, 25, self.player.hp, 100, (200, 30, 30), "HP")
        self.draw_stat_bar(ui_x+20, 155, 200, 25, self.player.exp % 1000, 1000, (30, 100, 220), "XP")
        
        # Gold & Level Display
        gold_text = self.small_font.render(f"GOLD:  ${self.player.money}", True, (255, 215, 0))
        level_text = self.small_font.render(f"LEVEL: {self.level}", True, (255, 255, 255))
        self.screen.blit(gold_text, (ui_x + 20, 210))
        self.screen.blit(level_text, (ui_x + 20, 240))

    def draw_stat_bar(self, x, y, w, h, cur, mx, col, label):
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, w, h))
        fill = int((max(0, cur)/mx)*w)
        pygame.draw.rect(self.screen, col, (x, y, fill, h))
        pygame.draw.rect(self.screen, (200, 200, 200), (x, y, w, h), 2)
        txt = self.small_font.render(f"{label}: {int(cur)}/{mx}", True, (255, 255, 255))
        self.screen.blit(txt, (x + w//2 - txt.get_width()//2, y + h//2 - txt.get_height()//2))