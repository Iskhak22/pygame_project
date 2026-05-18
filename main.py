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
                        game.start_game()
                    else:
                        if len(game.player.name) < 12: game.player.name += event.unicode
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if game.start_button_rect.collidepoint(event.pos) and game.player.name:
                        game.start_game()

            elif game.state in ['GAME_OVER', 'YOU_WIN']:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if game.play_again_button_rect.collidepoint(event.pos):
                        # Reset for a clean start
                        game.player.name = ""
                        game.state = 'LOBBY'

            elif game.state == 'PLAYING':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    game.shoot(pygame.mouse.get_pos())
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_u: game.undo()

        game.handle_continuous_input()
        game.update()
        game.render()
        game.clock.tick(60)

if __name__ == "__main__":
    main()