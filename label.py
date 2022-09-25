import pygame
from utility.color import *


class LabelFrame:
    """ A board frame to label rows and columns """

    def __init__(self, size=(500, 500)):
        self.surface = pygame.Surface(size)
        self.surface.fill(GRAY_BLUE)
        self.drawLabel()

    def drawLabel(self):
        """ draw label for row and columns"""
        rows = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        for i in range(len(rows)):
            self.drawText(rows[i], 20, (i+1.5)*42)
        for i in range(len(columns)):
            self.drawText(columns[i], (i+1.5)*42, 20)

    def drawText(self, text, x, y, size=22):
        """ draw text onto the surface """
        font = pygame.font.Font('freesansbold.ttf', size)
        FONT_COLOR = (255, 255, 255)
        label = font.render(text, False, FONT_COLOR)
        rect = label.get_rect()
        rect.center = (x, y)
        self.surface.blit(label, rect)
