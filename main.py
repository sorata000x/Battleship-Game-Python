"""
Description
    This program implement a battleship game.
Game Play
    The initial positions of the ships (both player and enemy) are pre-configured in a .JSON file (ships.json).
    The player can launch fire at an empty tile by clicking on the enemy's board (right-hand side). After launching
    a fire the tile will change to show if the fire hits or misses, and the enemy will also make a fire. Each ship
    can be sunk after every tile the ship is on is hit. The objective of this game is to sink all enemy ships before
    the enemy sinks all the player's ships.

Note
    ships.json provide ships' position (row, col start from 0) and orientation (vertical=true, horizontal=false).
Reference
    Pygame tutorial:Tiles | https://pygame.readthedocs.io/en/latest/tiles/tiles.html
"""

from gamebase import GameBase
import pygame
from board import Board


def main():
    game = BattleshipGame()
    game.run()


class BattleshipGame(GameBase):
    """ the battleship game base """
    def __init__(self):
        """ set up the battleship game and a board """
        super().__init__(1020, 500)
        self.board = Board((1020, 500))

    def draw(self):
        """ draw the board to screen """
        self._display.blit(self.board.surface, (0, 0))

    def keyDown(self, key):
        """ key down events """
        if key == pygame.K_r:
            self.__init__()
        if key == pygame.K_ESCAPE:
            quit()

    def mouseHover(self, x, y):
        """ mouse hover detect """
        self.board.mouseHover(x, y)

    def mouseButtonDown(self, x, y):
        """ mouse press event """
        self.board.mouseButtonDown(x, y)

    def mouseButtonUp(self, x, y):
        """ mouse release event """
        self.board.mouseButtonUp(x, y)

    def update(self):
        """ updates the game and board """
        super().update()
        # update board
        self.board.update()
        self._display.blit(self.board.surface, (0, 0))
        if self._ticks % 35 == 0:
            self.board.enemyMove()


main()
