import sys
import random
import pygame
from pygame.locals import *
import render
import CPU
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_NAME
from handlers import text_handle, position_cards, is_positioned
from collections import deque


class engine():
    def __init__(self, playernum):
        self.lastcard0 = None
        self.user_group = None
        self.deck_group = None
        self.playernum = playernum
        self.background = pygame.image.load('assets/default.png')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(self.background, (-100, -70))
        self.colors = {1: 'RED', 2: 'YELLOW', 3: 'GREEN', 4: 'BLUE', 5: 'BLACK'}
        self.skill = {11: '_SKILL_0', 12: '_SKILL_1', 13: '_SKILL_2', 14: '_SKILL_3', 15: '_SKILL_4'}
        self.deck = []
        self.player = [[0] for i in range(0, self.playernum)]
        self.ground = pygame.sprite.RenderPlain()
        self.rotate = 0
        self.now_turn = 0
        self.waste_card = []
        self.players_queue = deque(range(playernum))
        self.is_reverse = False
        pygame.display.update()

    def set_deck(self):
        # Assuming self.color is a dictionary mapping color indices to color names
        for color_idx, color in self.colors.items():
            if color_idx >= 1 and color_idx <= 4:  # Restrict to first four colors
                # Add zero cards
                self.deck.append(color + '_0')
                # Add two of each number card from 1 to 9
                self.deck.extend(color + f"_{num}" for num in range(1, 10) for _ in range(2))
                # Add two of each skill card
                self.deck.extend(
                    color + self.skill[card_number] for card_number in range(11, 14) for _ in range(2))

        # Adding black (wild and wild draw four) cards, four of each
        self.deck.extend("BLACK" + self.skill[card_number] for card_number in range(14, 16) for _ in range(4))

        # Shuffling the deck
        random.shuffle(self.deck)

    def distribute_cards(self):
        self.set_deck()
        for player in range(self.playernum):
            self.player[player] = [self.deck.pop() for _ in range(7)]

    def create_deck(self):
        deck = render.Card('BACK', (350, 300))
        self.deck_group = pygame.sprite.RenderPlain(deck)

    def create_player_groups(self):
        rotations = [0, 180, 270, 90]
        for i, player_deck in enumerate(self.player):
            card_group = []
            for card_name in player_deck:
                if i == 0:
                    card = render.Card(card_name, (400, 300))
                else:
                    card = render.Card('BACK', (400, 300))
                    card.rotation(rotations[i])
                card_group.append(card)

            if i == 0:
                self.user_group = card_group
            else:
                setattr(self, f'com{i}_card', card_group)

    # driver function

    def next_turn(self):
        # Display player info if needed
        player_info = {
            0: ("ME", (165, 420)),
            1: ("CPU", (235, 18)),
            # Add more player info if more than 2 players
        }
        current_player = self.players_queue[0]
        if current_player in player_info:
            player_name, position = player_info[current_player]
            text = render.text_handle(player_name, FONT_NAME, 30, (0, 0, 0))
            self.screen.blit(text, position)

        # Move to the next player
        if not self.is_reverse:
            self.players_queue.rotate(-1)
        else:
            self.players_queue.rotate(1)

        return self.players_queue[0]

    def reverse_direction(self):
        # Toggle the direction of play
        self.is_reverse = not self.is_reverse

    def printWindow(self):
        # Blit the background
        self.screen.blit(self.background, (-100, -70))

        # Draw the deck, user, and computer groups
        self.deck_group.draw(self.screen)
        self.user_group.draw(self.screen)
        self.com1_group.draw(self.screen)

        # Player information: name, group, and position
        player_info = {
            0: ("ME", self.user_group, (165, 420)),
            1: ("CPU", self.com1_group, (235, 18)),
        }

        for player, (name, group, position) in player_info.items():
            if group:  # Draw only if the group exists
                group.draw(self.screen)
                text = text_handle(name, FONT_NAME, 30, (0, 0, 0))
                self.screen.blit(text, position)

        # Draw the ground group
        self.ground.draw(self.screen)

        # Update the display
        pygame.display.update()

    def check_card(self, sprite):
        if len(self.waste_card) == 0:
            return True
        else:
            name = sprite.get_name()
            name = name.split('_')
            w_name = self.waste_card[-1]
            w_name = w_name.split('_')
            if w_name[0] == 'BLACK': return True
            if name[0] == 'BLACK': return True
            if len(name) < 3 or len(w_name) < 3:
                if w_name[0] == name[0]: return True
                if len(name) > 1 and len(w_name) > 1:
                    if w_name[1] == name[1]: return True
            else:
                if w_name[0] == name[0]: return True
                if w_name[2] == name[2]: return True

        return False

    def card_skill(self, sprite):
        name = sprite.get_name().split('_')
        if name[1] == 'SKILL':
            if name[2] == '0':
                pygame.time.wait(500)
                self.now_turn = self.next_turn()
            elif name[2] == '1':  # Reverse card
                self.reverse_direction()  # Reverse the play direction
                pygame.time.wait(500)
                self.now_turn = self.next_turn()  # Move to next turn
            elif name[2] == '2':
                pygame.time.wait(500)
                self.give_card(2)
                self.now_turn = self.next_turn()
            elif name[2] == '3':
                if self.now_turn == 0:
                    self.pick_color()
                elif self.now_turn == 1:
                    pygame.time.wait(500)
                    self.most_num_color(self.player[1])
            elif name[2] == '4':
                self.give_card(4)
                if self.now_turn == 0:
                    self.pick_color()
                elif self.now_turn == 1:
                    pygame.time.wait(500)
                    self.most_num_color(self.player[1])
        return True

    def most_num_color(self, card_deck):
        color_counts = {'RED': 0, 'YELLOW': 0, 'GREEN': 0, 'BLUE': 0}

        for item in card_deck:
            color = item.split('_')[0]
            if color in color_counts:
                color_counts[color] += 1

        most_common_color = max(color_counts, key=color_counts.get)
        temp = render.Card(most_common_color, (430, 300))
        self.waste_card.append(most_common_color)
        self.ground.add(temp)
        self.printWindow()

    def pick_color(self):
        color_popup = render.Popup('pickcolor', (400, 300))
        popup_group = pygame.sprite.RenderPlain(color_popup)
        red = render.Popup('RED', (306, 320))
        yellow = render.Popup('YELLOW', (368, 320))
        green = render.Popup('GREEN', (432, 320))
        blue = render.Popup('BLUE', (494, 320))
        colors = [red, yellow, green, blue]
        color_group = pygame.sprite.RenderPlain(*colors)

        loop = True
        while loop:
            popup_group.draw(self.screen)
            color_group.draw(self.screen)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONUP:
                    mouse_pos = pygame.mouse.get_pos()
                    for sprite in color_group:
                        if sprite.get_rect().collidepoint(mouse_pos):
                            temp_name = sprite.get_name()
                            temp = render.Card(temp_name, (430, 300))
                            self.waste_card.append(temp_name)
                            self.ground.add(temp)
                            self.printWindow()
                            loop = False
        return 0

    def give_card(self, card_num):
        # Get the next player in the queue without changing the turn order
        next_player = self.players_queue[1] if len(self.players_queue) > 1 else self.players_queue[0]

        # Give cards to the next player
        for i in range(card_num):
            self.pop_from_deck(next_player)

    def pop_from_deck(self, now_turn):
        item = self.deck.pop(0)

        if now_turn == 0:
            temp = render.Card(item, (400, 300))
            current_pos = self.lastcard0

            if current_pos[0] >= 620:
                x, y = 200, current_pos[1] + 80
            else:
                x, y = current_pos[0] + 70, current_pos[1]

            temp.setposition(x, y)
            self.lastcard0 = (x, y)
            self.user_group.add(temp)

        elif now_turn == 1:
            temp = render.Card('BACK', (350, 300))
            temp.rotation(180)
            current_pos = self.lastcard1

            if current_pos[0] >= 510:
                x, y = 270, current_pos[1] + 40
            else:
                x, y = current_pos[0] + 40, current_pos[1]

            temp.setposition(x, y)
            self.lastcard1 = (x, y)
            self.com1_group.add(temp)
            self.player[1].append(item)

    def render_player_names(self):
        player_info = {
            0: ("ME", (165, 420)),
            1: ("CPU", (235, 18)),
            # Add more player info if more than 2 players
        }

        current_player = self.players_queue[0]

        for player, (name, position) in player_info.items():
            if player == current_player:
                color = (255, 242, 0)  # Highlight color for the current player
            else:
                color = (255, 255, 255)  # Normal color for other players

            text = render.text_handle(name, FONT_NAME, 30, color)
            self.screen.blit(text, position)

    def set_last(self, lastcard, compare_pos):
        x, y = lastcard
        i_x, i_y = compare_pos

        if self.now_turn == 0:
            if x >= i_x + 60 and y == i_y:
                x -= 70
            elif y > i_y:
                if x <= 200:
                    x, y = 620, y - 80
                else:
                    x -= 70

            self.lastcard0 = (x, y)

        elif self.now_turn == 1:
            if y > 100 and x == 270:
                x, y = 510, y - 40
            else:
                x -= 40

            self.lastcard1 = (x, y)

    def put_ground(self, sprite):
        self.ground.add(sprite)
        self.waste_card.append(sprite.get_name())
        self.set_last(self.lastcard0, sprite.getposition())
        self.printWindow()

    def set_window(self):
        self.distribute_cards()
        self.create_deck()
        self.create_player_groups()

        setting = True
        while setting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            user_sprites = position_cards(self.user_group, (200, 500), 70)
            self.user_group = pygame.sprite.RenderPlain(*user_sprites)
            self.lastcard0 = user_sprites[-1].getposition()

            com1_sprites = position_cards(self.com1_card, (270, 100), 40)
            self.com1_group = pygame.sprite.RenderPlain(*com1_sprites)
            self.lastcard1 = com1_sprites[-1].getposition()

            setting = not all([
                is_positioned(self.user_group, (200, 500), 70, len(self.user_group)),
                is_positioned(self.com1_group, (270, 100), 40, len(self.com1_card)),

            ])

            self.printWindow()
            pygame.display.update()

    # driver function
    def startGame(self):
        self.deck.clear()
        self.player = [[0] for i in range(0, self.playernum)]
        self.ground = pygame.sprite.RenderPlain()
        self.rotate = 0
        self.set_window()
        self.playGame()

    # driver function
    def playGame(self):
        while True:
            # Check for winning conditions
            if len(self.user_group) == 0 or (self.playernum == 2 and len(self.player[1]) == 0):
                self.restart()
                return

            # Replenish the deck if empty
            if len(self.deck) == 0:
                self.set_deck()

            self.render_player_names()

            # AI's turn
            if self.now_turn == 1:
                pygame.time.wait(700)
                ai = CPU.AI(2, self.player[1], self.waste_card)
                temp = ai.cpuplay()

                if temp == 0 or temp is None:
                    self.pop_from_deck(1)
                else:
                    for sprite in self.com1_group:
                        if sprite.getposition() == self.lastcard1:
                            self.com1_group.remove(sprite)
                    self.player[1].remove(temp)
                    self.set_last(self.lastcard1, (0, 0))
                    self.waste_card.append(temp)
                    t_card = render.Card(temp, (430, 300))
                    self.ground.add(t_card)
                    self.card_skill(t_card)

                self.printWindow()
                self.now_turn = self.next_turn()  # Move to next turn
                pygame.display.update()

            # Event handling
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    return
                if event.type == MOUSEBUTTONUP and self.now_turn == 0:
                    mouse_pos = pygame.mouse.get_pos()
                    for sprite in self.user_group:
                        if sprite.get_rect().collidepoint(mouse_pos) and self.check_card(sprite):
                            self.user_group.remove(sprite)
                            for temp in self.user_group:
                                temp.move(sprite.getposition())
                            sprite.setposition(430, 300)
                            self.put_ground(sprite)
                            self.card_skill(sprite)
                            self.now_turn = self.next_turn()  # Move to next turn
                            break
                    for sprite in self.deck_group:
                        if sprite.get_rect().collidepoint(mouse_pos):
                            self.pop_from_deck(self.now_turn)
                            self.now_turn = self.next_turn()  # Move to next turn
                            break

            pygame.display.update()

    def restart(self):
        # Light blue outer rectangle
        pygame.draw.rect(self.screen, (173, 216, 230), pygame.Rect(200, 200, 400, 200))
        # Slightly lighter inner rectangle for contrast
        pygame.draw.rect(self.screen, (191, 239, 255), pygame.Rect(210, 210, 380, 180))

        if len(self.user_group) == 0:
            close_text = text_handle("You win!", FONT_NAME, 80, (0, 0, 139))  # Dark blue color
            press_text = text_handle("Press SPACE to REPLAY", FONT_NAME, 35, (0, 0, 139))  # Dark blue color
            self.screen.blit(close_text, (230, 220))
        else:
            close_text = text_handle("You lost...", FONT_NAME, 80, (0, 0, 139))  # Dark blue color
            press_text = text_handle("Press SPACE to REPLAY", FONT_NAME, 35, (0, 0, 139))  # Dark blue color
            self.screen.blit(close_text, (212, 220))

        pygame.display.update()

        self.screen.blit(press_text, (228, 330))
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        self.startGame()
                        return
        return 0
