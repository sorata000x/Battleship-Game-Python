import pygame


class Mouse(pygame.sprite.Sprite):
    """ A mouse sprite for detecting mouse click on sprite """
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, 3, 3)

    def __repr__(self):
        return f'[{self.rect.x}, {self.rect.y}]'
