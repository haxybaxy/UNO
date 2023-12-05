import sys
import pygame
from pygame.locals import *
import engine
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, FONT_NAME, FPS


class UnoGame:
    def __init__(self):
        pygame.init()
        self.screen_width, self.screen_height = SCREEN_WIDTH, SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.render_background('./assets/background.png')
        self.playing = 3 #this is locked at 3 because otherwise the reverse card would just be skip
        self.clock = pygame.time.Clock()
        self.font = FONT_NAME

    def render_background(self, path): #pygame refreshing is constant time
        self.background = pygame.image.load(path)
        self.screen.fill(BACKGROUND_COLOR)
        self.screen.blit(self.background, (-30, -30))
        pygame.display.update()

    def render_text(self, message, size, color, y_pos): #pygame render is constant time here also
        font = pygame.font.SysFont(FONT_NAME, size)
        text = font.render(message, True, color)
        rect = text.get_rect(center=(SCREEN_WIDTH / 2, y_pos))
        self.screen.blit(text, rect)
        return rect

    def text_handle(self, message, textFont, textSize, textColor): #constant time
        newFont = pygame.font.SysFont(textFont, textSize)
        newText = newFont.render(message, K_0, textColor)
        return newText

    def menu_logic(self, options, action_functions): #O(N) because we have to iterate through every option we have on the menu
        while True:
            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = pygame.mouse.get_pressed()[0]

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            for i, option in enumerate(options):
                rect = self.render_text(option, 50, (0, 0, 0), 180 + i * 60)

                if rect.collidepoint(mouse_pos):
                    # Change color to highlight
                    self.render_text(option, 50, (255, 24, 0), 180 + i * 60)

                    if mouse_clicked:
                        action_functions[i]()
                        self.render_background('./assets/background.png')

            pygame.display.update()
            self.clock.tick(FPS)

    def start_game(self):
        self.render_background('assets/default.png')
        game = engine.engine(self.playing)
        game.start()


    def main_menu(self):
        options = ["Play UNO!", "Exit"]
        actions = [self.start_game, sys.exit]
        self.menu_logic(options, actions)


if __name__ == '__main__':
    uno_game = UnoGame()
    uno_game.main_menu()
