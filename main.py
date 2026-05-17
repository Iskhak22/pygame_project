import pygame
import sys
from engine.game_manager import GameEngine

def main():
    pygame.init()
    game = GameEngine()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if game.state == 'LOBBY':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE: game.player.name = game.player.name[:-1]
                    elif event.key == pygame.K_RETURN and game.player.name:
                        game.load_new_level(); game.state = 'PLAYING'
                    else:
                        if len(game.player.name) < 12: game.player.name += event.unicode
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if game.start_button_rect.collidepoint(event.pos) and game.player.name:
                        game.load_new_level(); game.state = 'PLAYING'

            elif game.state == 'GAME_OVER':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if game.restart_button_rect.collidepoint(event.pos):
                        game.restart_game()

            elif game.state == 'PLAYING':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    game.shoot(pygame.mouse.get_pos())
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w: game.handle_movement(0, -1)
                    elif event.key == pygame.K_s: game.handle_movement(0, 1)
                    elif event.key == pygame.K_a: game.handle_movement(-1, 0)
                    elif event.key == pygame.K_d: game.handle_movement(1, 0)
                    elif event.key == pygame.K_u: game.undo()

        game.update()
        game.render()
        game.clock.tick(60)

if __name__ == "__main__":
    main()