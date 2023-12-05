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
        self.playernum = playernum #initialization of pygame variables
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.background = pygame.image.load('assets/default.png') #Draw background
        self.screen.blit(self.background, (-100, -70))

        self.colors = {1: 'RED', 2: 'YELLOW', 3: 'GREEN', 4: 'BLUE', 5: 'BLACK'} #Make the deck
        self.skill = {11: '_SKILL_0', 12: '_SKILL_1', 13: '_SKILL_2', 14: '_SKILL_3', 15: '_SKILL_4'} #Add the skill cards

        self.deck_stack = [] #Deck is where you take new cards from
        self.ground_stack = [] #Ground is where you throw the cards

        self.player = [[0] for i in range(0, self.playernum)]
        self.now_turn = 0
        self.players_queue = deque(range(playernum))
        self.is_reverse = False
        pygame.display.update()

    def sort_player_hand(self, player_index): # O(nlogn) since we are using timsort which is the default sorting algotithm in python
        # Define the sorting key based on colors
        def sort_key(card_name):
            color = card_name.split('_')[0]
            # Use the index of the color in the colors dict as the sort key
            for color_idx, color_name in self.colors.items():
                if color == color_name:
                    return color_idx
            return 5  # Assign a higher number for black or any unknown color

        # Sort the player's hand using the defined key
        self.player[player_index].sort(key=sort_key)
    def set_deck(self): #Method for making the cards, runtime is O(n), since we are iterating through every card
        predefined_deck = []  # The cards are an array while you shuffle them

        for color_idx, color in self.colors.items():
            if color_idx >= 1 and color_idx <= 4:  # Restrict to first four colors to avoid black
                # Add zero cards
                predefined_deck.append(color + '_0')
                # Add two of each number card from 1 to 9
                predefined_deck.extend(color + f"_{num}" for num in range(1, 10) for _ in range(2))
                # Add two of each skill card
                predefined_deck.extend(
                    color + self.skill[card_number] for card_number in range(11, 14) for _ in range(2))

        # Adding black (wild and wild draw four) cards, four of each
        predefined_deck.extend("BLACK" + self.skill[card_number] for card_number in range(14, 16) for _ in range(4))

        # Shuffle the predefined deck
        random.shuffle(predefined_deck)

        # Assign the shuffled deck to become the stack
        self.deck_stack = predefined_deck

    def distribute_cards(self): #O(n) since we are iterating through the number of players
        self.set_deck()
        for player in range(self.playernum):
            self.player[player] = [self.deck_stack.pop() for _ in range(7)]
            self.sort_player_hand(player) #O(nlogn) isnt larger than the linear time complexity

    def create_deck(self): #O(1) Renders take a constant amount of time always
        deck = render.Card('BACK', (350, 300))
        self.deck_graphic = pygame.sprite.RenderPlain(deck)

    def create_player_hands(self): #O(Players*Cards), rendering the player's hands
        rotations = [0, 180, 270]
        for i, player_deck in enumerate(self.player):
            temp_hand = []
            for card_name in player_deck:
                if i == 0:
                    card = render.Card(card_name, (400, 300)) #real player's deck
                else:
                    card = render.Card('BACK', (400, 300))
                    card.rotation(rotations[i])  # rotate the cards to display them properly
                temp_hand.append(card) #method renders the card then gives it to the player


            if i == 0:
                self.user_hand = temp_hand
            else:
                setattr(self, f'cpu{i}_card', temp_hand)

    def setup_window(self): #O(n) as we have to iterate through the players, method sets up the initial window
        self.distribute_cards()
        self.create_deck()
        self.create_player_hands()

        booting = True
        while booting:
            player_configs = [
                (self.user_hand, (200, 500), 70, '0', 0),
                (self.cpu1_card, (270, 100), 40, '1', 0),
                (self.cpu2_card, (45, 100), 70, '2', 1),
            ]

            for hand, position, offset, lastcard_index, axis in player_configs:
                sprites = position_cards(hand, position, offset, axis=axis)
                group = pygame.sprite.RenderPlain(*sprites)
                setattr(self, f'lastcard{lastcard_index}', sprites[-1].getposition())

                if lastcard_index == '0':
                    self.user_hand = group
                elif lastcard_index == '1':
                    self.cpu1_group = group
                else:  # '2'
                    self.cpu2_group = group

            booting = not all([
                is_positioned(self.user_hand, (200, 500), 70, len(self.user_hand)),
                is_positioned(self.cpu1_group, (270, 100), 40, len(self.cpu1_card)),
                is_positioned(self.cpu2_group, (45, 100), 70, len(self.cpu2_card), axis=1),
            ])
            pygame.display.update()
    def check_card(self, sprite): #O(1) since we are not iterating, only checking values in the card.
        if len(self.ground_stack) == 0: #This method checks the car on the ground (top of stack)
            return True
        else:
            name = sprite.get_name()
            name = name.split('_')
            w_name = self.ground_stack[-1]
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

    def special_handle(self, sprite): #O(1) since we are also just checking values of a card
        name = sprite.get_name().split('_') #This method helps check the card if its a special one
        if name[1] == 'SKILL':
            if name[2] == '0':#Skip card
                pygame.time.wait(500)
                self.now_turn = self.next_turn()
            elif name[2] == '1':  # Reverse skill
                self.reverse_direction()  # Reverse the play direction, which the direction we add to our queue
                pygame.time.wait(500)
                self.now_turn = self.next_turn() #moving in the opposite direction
            elif name[2] == '2':
                pygame.time.wait(500)
                self.give_card(2) #draw 2 card
                self.now_turn = self.next_turn()
            elif name[2] == '3':
                if self.now_turn == 0:
                    self.wild_card() #wild card
                elif self.now_turn == 1:
                    pygame.time.wait(500)
                    self.most_repeated_color(self.player[1])
                elif self.now_turn == 2:
                    pygame.time.wait(500)
                    self.most_repeated_color(self.player[2])
            elif name[2] == '4':
                self.give_card(4) #draw 4 card
                if self.now_turn == 0:
                    self.wild_card()
                elif self.now_turn == 1:
                    pygame.time.wait(500)
                    self.most_repeated_color(self.player[1])
                elif self.now_turn == 2:
                    pygame.time.wait(500)
                    self.most_repeated_color(self.player[2])
        return True

    def most_repeated_color(self, card_deck): #O(n), we are iterating through every card
        color_counts = {'RED': 0, 'YELLOW': 0, 'GREEN': 0, 'BLUE': 0} #this method checks which color teh cpu has most in the deck so it can play wen a wild card is played

        for item in card_deck:
            color = item.split('_')[0]
            if color in color_counts:
                color_counts[color] += 1

        most_common_color = max(color_counts, key=color_counts.get)
        temp = render.Card(most_common_color, (430, 300))
        self.ground_stack.append(most_common_color)
        self.ground_graphic.add(temp)

    def wild_card(self): #O(1), this just renders the popup screen to choose a color
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
                            self.ground_stack.append(temp_name)
                            self.ground_graphic.add(temp)
                            self.print_window()
                            loop = False
        return 0

    def pop_from_deck(self, now_turn): #O(1), popping from a stack)
        item = self.deck_stack.pop(0)

        if now_turn == 0:
            # Logic for user
            temp = render.Card(item, (400, 300))
            current_pos = self.lastcard0

            if current_pos[0] >= 620:
                x, y = 200, current_pos[1] + 80
            else:
                x, y = current_pos[0] + 70, current_pos[1]

            temp.setposition(x, y)
            self.lastcard0 = (x, y)
            self.user_hand.add(temp)


        elif now_turn == 1:
            # graphics and logic for cpu1
            temp = render.Card('BACK', (350, 300))
            temp.rotation(180)
            current_pos = self.lastcard1

            if current_pos[0] >= 510:
                x, y = 270, current_pos[1] + 40
            else:
                x, y = current_pos[0] + 40, current_pos[1]

            temp.setposition(x, y)
            self.lastcard1 = (x, y)
            self.cpu1_group.add(temp)
            self.player[1].append(item)

        elif now_turn == 2:
            # graphics and logic for cpu1
            temp = render.Card('BACK', (350, 300))
            temp.rotation(270)
            current_pos = self.lastcard2

            if current_pos[1] >= 410:
                x, y = current_pos[0] + 40, 170
            else:
                x, y = current_pos[0], current_pos[1] + 40

            temp.setposition(x, y)
            self.lastcard2 = (x, y)
            self.cpu2_group.add(temp)
            self.player[2].append(item)

    def set_last(self, lastcard, compare_pos): #O(1) time, just graphics to render where to put one card
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
        elif self.now_turn == 2:
            if y > 200 and x == 400:
                x, y = 540, y - 40
            else:
                y -= 40
            self.lastcard2 = (x, y)

    def put_ground(self, sprite): #O(1), pushing to stack
        self.ground_graphic.add(sprite)
        self.ground_stack.append(sprite.get_name())
        self.set_last(self.lastcard0, sprite.getposition())

    def next_turn(self): #O(n) since we have to iterate through the players
        player_info = {
            0: ("ME", (165, 420)),
            1: ("CPU1", (235, 18)),
            2: ("CPU2", (45, 30))
        }
        current_player = self.players_queue[0]

        for player, (name, position) in player_info.items():
            if player == current_player:
                color = (255, 255, 255)
            else:
                color = (255, 255, 0)
            text = render.text_handle(name, FONT_NAME, 30, color)
            self.screen.blit(text, position)

        if not self.is_reverse:
            self.players_queue.rotate(-1)
        else:
            self.players_queue.rotate(1)

        return self.players_queue[0]

    def reverse_direction(self): #O(1) time
        self.is_reverse = not self.is_reverse

    def give_card(self, card_num): #O(n) because popping is O(1) and we are doing it n times
        next_player = self.players_queue[1] if len(self.players_queue) > 1 else self.players_queue[0]
        for i in range(card_num):
            self.pop_from_deck(next_player)
        self.print_window()

    def print_window(self): #O(n) everything in here is O(1) except teh fact that we have to iterate through the amount of players.
        # Blit the background
        self.screen.blit(self.background, (-100, -70))
        # Draw the deck, user, and computer hands
        self.deck_graphic.draw(self.screen)

        #Player information: name, hands, and position
        player_info = {
            0: ("ME", self.user_hand, (165, 420)),
            1: ("CPU", self.cpu1_group, (235, 18)),
            2: ("CPU2", self.cpu2_group, (45, 30))
        }
        for player, (name, group, position) in player_info.items():
            if group:  # Draw only if the group exists
                group.draw(self.screen)
                text = text_handle(name, FONT_NAME, 30, (0, 0, 0))
                self.screen.blit(text, position)

        # Draw the ground group
        self.ground_graphic.draw(self.screen)

        # Update the display
        pygame.display.update()

    def start(self): #O(n^2), since O(n^2) + O(n) is still O(n)
        self.deck_stack.clear()
        self.player = [[0] for i in range(0, self.playernum)]
        self.ground_graphic = pygame.sprite.RenderPlain()
        self.setup_window() #O(n)
        self.print_window() #O(n)
        self.driver() #O(n^2)

    def driver(self): #O(n^2) worst case since we are iterating through every sprite each time we go through one
        while True:
            # Check for winning conditions for all players
            if len(self.user_hand) == 0 or any(len(self.player[i]) == 0 for i in range(1, self.playernum)):
                self.win_loss()
                return

            # Replenish the deck if empty
            if len(self.deck_stack) == 0:
                self.set_deck()

            # Handle turns for cpus
            if self.now_turn in [1, 2]:
                pygame.time.wait(700)
                ai = CPU.AI(self.now_turn, self.player[self.now_turn], self.ground_stack)
                temp = ai.cpuplay()

                if temp == 0 or temp is None:
                    self.pop_from_deck(self.now_turn)
                    self.print_window()
                else:
                    current_group = self.cpu1_group if self.now_turn == 1 else self.cpu2_group #
                    last_card_pos = self.lastcard1 if self.now_turn == 1 else self.lastcard2

                    for sprite in current_group:
                        if sprite.getposition() == last_card_pos:
                            current_group.remove(sprite)
                    self.player[self.now_turn].remove(temp)
                    self.set_last(last_card_pos, (0, 0))
                    self.ground_stack.append(temp)
                    t_card = render.Card(temp, (430, 300))
                    self.ground_graphic.add(t_card)
                    self.special_handle(t_card)

                self.print_window()
                self.now_turn = self.next_turn()  # Move to next turn
                pygame.display.update()

            # Event listener
            for event in pygame.event.get(): #Event listener loop is O(1), but the whole thing here is O(n^2)
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    return
                if event.type == MOUSEBUTTONUP and self.now_turn == 0:
                    mouse_pos = pygame.mouse.get_pos()
                    for sprite in self.user_hand: #O(n^2) because for every sprite we are iterating through the values in temp
                        if sprite.get_rect().collidepoint(mouse_pos) and self.check_card(sprite):
                            self.user_hand.remove(sprite)
                            for temp in self.user_hand:
                                temp.move(sprite.getposition())
                            sprite.setposition(430, 300)
                            self.put_ground(sprite)
                            self.print_window()
                            self.special_handle(sprite)
                            self.now_turn = self.next_turn()  # Move to next turn
                            break
                    for sprite in self.deck_graphic: #O(n)
                        if sprite.get_rect().collidepoint(mouse_pos):
                            self.pop_from_deck(self.now_turn)
                            self.print_window()
                            self.now_turn = self.next_turn()  # Move to next turn
                            break

            pygame.display.update()

    def win_loss(self): #O(1) time since this is just rendering and the loop is an event listener
        pygame.draw.rect(self.screen, (173, 216, 230), pygame.Rect(200, 200, 400, 200))
        pygame.draw.rect(self.screen, (191, 239, 255), pygame.Rect(210, 210, 380, 180))

        message_color = (0, 0, 139)
        replay_text = text_handle("Press SPACE to REPLAY", FONT_NAME, 35, message_color)

        if not self.user_hand:
            result_text = "You win!"
            text_position = (230, 220)
        else:
            result_text = "You lost..."
            text_position = (212, 220)

        result_message = text_handle(result_text, FONT_NAME, 80, message_color)
        self.screen.blit(result_message, text_position)
        self.screen.blit(replay_text, (228, 330))
        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN and event.key == K_SPACE:
                    self.start()
                    return
