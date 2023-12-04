import sys
import random
import pygame
from pygame.locals import *
import render
import CPU
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_NAME


def text_handle(message, textFont, textSize, textColor):
    newFont = pygame.font.SysFont(textFont, textSize)
    newText = newFont.render(message, K_0, textColor)
    return newText


def position_cards(card_group, start_position, offset, axis=0):
    positioned_cards = []
    for i, card in enumerate(card_group):
        position = list(start_position)
        position[axis] += offset * i
        card.update(tuple(position))
        positioned_cards.append(card)
    return positioned_cards


def is_positioned(group, start_position, offset, count, axis=0):
    last_card = group.sprites()[-1].getposition()
    expected_position = list(start_position)
    expected_position[axis] += offset * (count - 1)
    return last_card == tuple(expected_position)
