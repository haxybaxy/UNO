import pygame

class BaseSprite(pygame.sprite.Sprite):
    """ A base class for common sprite functionalities. """
    def __init__(self, name, position, image_scale=None):
        super().__init__()
        self.name = name
        self.image = pygame.image.load(f'./assets/{name}.png')
        if image_scale:
            self.image = pygame.transform.scale(self.image, image_scale)
        self.position = position
        self.rect = self.image.get_rect(center=position)

    def update_position(self, new_position):
        self.position = new_position
        self.rect.center = new_position

    def get_name(self):
        return self.name

    def get_rect(self):
        return self.rect

    def getposition(self):
        return self.position

    def setposition(self, x, y):
        i_x = x
        i_y = y
        self.position = (i_x, i_y)
        self.rect = self.image.get_rect()
        self.rect.center = self.position

class Card(BaseSprite):
    def __init__(self, name, position):
        super().__init__(name, position, image_scale=(80, 100))
        self.orig_pos = position
        self.user_rotation = 30

    def update(self, dest_loc):
        x, y = self.position
        vx, vy = (dest_loc[0] - x, dest_loc[1] - y)
        vx, vy = (x / (x ** 2 + y ** 2) ** 0.5, y / (x ** 2 + y ** 2) ** 0.5)

        speed = 5

        x = x + speed * vx
        y = y + speed * vy

        if x >= dest_loc[0]:
            x = dest_loc[0]
        if y >= dest_loc[1]:
            y = dest_loc[1]

        self.position = (x, y)
        self.rect = self.image.get_rect()
        self.rect.center = self.position


    def rotation(self, rotate):
        self.image = pygame.transform.rotate(self.image, rotate)
        self.rect = self.image.get_rect(center=self.position)

    def move(self, compare_pos):
        x, y = self.position
        i_x = compare_pos[0]
        i_y = compare_pos[1]

        if x > i_x + 60 and y == i_y:
            x -= 70

        elif y > i_y:
            if x <= 200:
                x = 620
                y = y - 80
            else:
                x -= 70
        self.position = (x, y)
        self.rect = self.image.get_rect()
        self.rect.center = self.position


class Popup(BaseSprite):
    def __init__(self, name, position):
        super().__init__(name, position)
