class AI():
    def __init__(self, playernum, playerdeck, wastecard):
        print(playerdeck)
        self.playernum = playernum
        self.playerdeck = playerdeck
        self.nowcard = wastecard[-1]
        self.wastes = wastecard

    def cpuplay(self):
        now = self.nowcard.split('_')
        for item in self.playerdeck:
            if self.is_playable(item, now):
                return item
        return 0

    def is_playable(self, card, now):
        card_parts = card.split('_')
        if card_parts[0] == 'BLACK' or now[0] == 'BLACK':
            return True
        if len(now) <= 2 and card_parts[0] == now[0]:
            return True
        if len(card_parts) == len(now) and card_parts[-1] == now[-1]:
            return True
        return False

    def find_solution(self, now):
        possible_cards = self.get_possible_cards(now)
        if len(possible_cards) == 1:
            return possible_cards[0]
        elif len(possible_cards) > 1:
            return self.select_best_card(possible_cards)
        return None

    def get_possible_cards(self, now):
        possible_cards = []
        for item in self.playerdeck:
            if self.is_card_match(item, now):
                possible_cards.append(item)
        return possible_cards

    def is_card_match(self, card, now):
        card_parts = card.split('_')
        if card_parts[0] == 'BLACK':
            return True
        if len(card_parts) >= len(now) and card_parts[0] == now[0]:
            return True
        if len(card_parts) == len(now) and card_parts[-1] == now[-1]:
            return True
        return False

    def select_best_card(self, possible_cards):
        color_count = self.bestchoice(possible_cards)
        sorted_colors = sorted(color_count, key=color_count.get, reverse=True)
        for color in sorted_colors:
            for card in possible_cards:
                if card.startswith(color):
                    return card
        return possible_cards[0]

    def bestchoice(self, result):
        color_count = {'RED': 0, 'YELLOW': 0, 'GREEN': 0, 'BLUE': 0}
        for card in self.wastes:
            color = card.split('_')[0]
            if color in color_count:
                color_count[color] += 1
        return color_count

    def check_same_color(self, color):
        return sum(card.startswith(color) for card in self.playerdeck) > 1
