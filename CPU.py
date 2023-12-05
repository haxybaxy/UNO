class AI():
    def __init__(self, playernum, playerdeck, wastecard):#O(1)
        print(playerdeck)
        self.playernum = playernum
        self.playerdeck = playerdeck
        self.nowcard = wastecard[-1]
        self.wastes = wastecard

    def cpuplay(self): #O(N) since we are iterating through every card to check if we can play it
        now = self.nowcard.split('_')
        for item in self.playerdeck:
            if self.is_playable(item, now):
                return item
        return 0

    def is_playable(self, card, now): #O(1) checking if teh card is playable
        card_parts = card.split('_')
        if card_parts[0] == 'BLACK' or now[0] == 'BLACK':
            return True
        if len(now) <= 2 and card_parts[0] == now[0]:
            return True
        if len(card_parts) == len(now) and card_parts[-1] == now[-1]:
            return True
        return False

    def find_solution(self, now): #O(n) since the function below is O(n)
        possible_cards = self.get_possible_cards(now)#O(n)
        if len(possible_cards) == 1:
            return possible_cards[0]
        elif len(possible_cards) > 1:
            return self.select_best_card(possible_cards)#O(n)
        return None

    def get_possible_cards(self, now): #O(n) iterating through all cards that we can play
        possible_cards = []
        for item in self.playerdeck:
            if self.is_card_match(item, now):
                possible_cards.append(item)
        return possible_cards

    def is_card_match(self, card, now): #O(1) just checking
        card_parts = card.split('_')
        if card_parts[0] == 'BLACK':
            return True
        if len(card_parts) >= len(now) and card_parts[0] == now[0]:
            return True
        if len(card_parts) == len(now) and card_parts[-1] == now[-1]:
            return True
        return False

    def select_best_card(self, possible_cards): #O(colors*cards) but since the colors are always the same its only O(n)
        color_count = self.bestchoice(possible_cards)
        sorted_colors = sorted(color_count, key=color_count.get, reverse=True)
        for color in sorted_colors:
            for card in possible_cards:
                if card.startswith(color):
                    return card
        return possible_cards[0]

    def bestchoice(self, result): #O(n)
        color_count = {'RED': 0, 'YELLOW': 0, 'GREEN': 0, 'BLUE': 0}
        for card in self.wastes:
            color = card.split('_')[0]
            if color in color_count:
                color_count[color] += 1
        return color_count

    def check_same_color(self, color): #O(1)
        return sum(card.startswith(color) for card in self.playerdeck) > 1
