import pygame
from utility.color import *
from tile import TileGrid
from label import LabelFrame
from ship import PlayerFleet, EnemyFleet
from utility.mouse import Mouse


class Board:
    """ a board that displays all the elements (tile grid, grid labels, ships) """
    def __init__(self, size):
        # ------ Info ---------
        self.size = size
        # ------ Surface ------
        self.surface = pygame.Surface(size)
        # ------ Element ------
        self.tileGridL = TileGrid((420, 420), (40, 40))       # left grid (player)
        self.tileGridR = TileGrid((420, 420), (560, 40))      # right grid (enemy)
        self.playerFleet = PlayerFleet(self.tileGridL)
        self.enemyFleet = EnemyFleet(self.tileGridR, self.playerFleet)
        self.confirmButton = self.Button(800, 400)
        # ------ State --------
        self.enemyShown = True
        self.playerTurn = True
        self.score = 0
        # ------ Draw ---------
        self.draw()

    # ------ Graphic ----------
    def draw(self):
        """ draw elements onto the board """
        # ------- Background -----------------
        self.surface.fill(NAVY_BLUE)
        # ------- Left board (player) --------
        self.surface.blit(LabelFrame().surface, (0, 0))
        self.tileGridL.sprites.add(*self.playerFleet)
        self.tileGridL.draw(self.surface)
        # ------- Right board (enemy) --------
        if self.enemyShown:
            self.surface.blit(LabelFrame().surface, (520, 0))
            self.tileGridR.sprites.add(*self.enemyFleet)
            self.tileGridR.draw(self.surface)
        # ------- Confirm Button -------------
        if self.playerFleet.shipsPlaced() and not self.enemyShown:
            self.confirmButton.draw(self.surface)

    # ------ Update -----------
    def update(self):
        self.enemyFleet.checkSunk()
        self.draw()
        self.checkGameOver()

    def checkGameOver(self):
        """ display message and score if one of side (player or enemy) has won """
        if self.enemyFleet.allSink():           # Player win
            ScoreBoard(self.size[0]/2, self.size[1]/2, 'YOU WIN', self.score).draw(self.surface)
        if self.playerFleet.allSink():          # Player lose
            ScoreBoard(self.size[0]/2, self.size[1]/2, 'YOU LOSE', self.score).draw(self.surface)

    # ------ Mouse Event ------
    def mouseHover(self, x, y):
        if self.enemyShown:
            self.tileGridR.mouseHover(x-560, y-40)
        else:       # move selected ship with mouse when placing ship
            self.playerFleet.move(x-40, y-40)

    def mouseButtonDown(self, x, y):
        if self.enemyShown:     # game start
            self.playerMove(x, y)
        else:       # configure ship
            mouse = Mouse(x, y)
            # ------- Confirm Button ---------
            if pygame.sprite.collide_rect(self.confirmButton, mouse):
                self.playerFleet.createShipsJSON()    # record ship position
                self.enemyShown = True
            # ------- Grab ship --------
            self.playerFleet.grab(x-40, y-40)

    def mouseButtonUp(self, x, y):
        # ------ Release ship --------
        if not self.enemyShown:
            self.playerFleet.release()

    # ------ Game Play --------
    def playerMove(self, x, y):
        if self.playerTurn:
            grid = self.tileGridR.findGrid((x - 560, y - 40))
            if self.tileGridR.gridInRange(grid):
                hitShip = None
                for name, ship in self.enemyFleet.shipList.items():
                    if ship.collide(self.tileGridR.findGrid((x - 560, y - 40))):
                        hitShip = ship
                        self.score += 15
                if self.tileGridR.collide(x - 560, y - 40, hitShip):
                    self.playerTurn = False

    def enemyMove(self):
        """ let enemy make a move and update information """
        if self.playerTurn:     # only move when not player's turn
            return False
        grid = self.enemyFleet.fire()       # Fire randomly
        # See if hit any ship
        hitShip = self.playerFleet.getShipAt(grid[0], grid[1])
        if hitShip is not None:
            self.enemyFleet.markHit()
            hitShip = self.playerFleet.getShipAt(grid[0], grid[1])
            if self.score >= 5:     # lose score if hit by enemy
                self.score -= 5
        coord = self.tileGridL.findCoord(grid)      # Mark for fired tile
        if self.tileGridL.collide(coord[0], coord[1], hitShip):     # pass to tile grid for collision with tile
            self.playerTurn = True      # make it players turn
        return True

    # ------ Element ----------
    class Button (pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = pygame.Surface((100, 50))
            self.image.fill(WHITE)
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.drawText('OK', self.rect.size[0]/2, self.rect.size[1]/2)

        def draw(self, screen):
            screen.blit(self.image, self.rect)

        def drawText(self, text, x, y, size=22):
            """ Draw text onto the surface """
            font = pygame.font.Font('freesansbold.ttf', size)
            FONT_COLOR = (255, 255, 255)
            label = font.render(text, False, FONT_COLOR)
            rect = label.get_rect()
            rect.center = (x, y)
            self.image.blit(label, rect)


class ScoreBoard(pygame.sprite.Sprite):
    def __init__(self, cx, cy, message, score):
        """
        :param cx: center x position
        :param cy: center y position
        :param message: message to display
        :param score: total score to display
        """
        super().__init__()
        # ----- Info ---------
        self.message = message
        self.score = score
        # ----- Surface ------
        self.size = (300, 200)
        self.image = pygame.Surface(self.size)
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = cx, cy

    def draw(self, screen):
        """ draw the surface onto screen """
        self.drawText(self.message, self.size[0] / 2, self.size[1] * 2 / 6, 30)
        self.drawText(f'SCORE: {self.score}', self.size[0] / 2, self.size[1] * 2 / 3)
        screen.blit(self.image, self.rect)

    def drawText(self, text, x, y, size=22):
        """ Draw text onto the surface """
        font = pygame.font.Font('freesansbold.ttf', size)
        FONT_COLOR = (255, 255, 255)
        label = font.render(text, False, FONT_COLOR)
        rect = label.get_rect()
        rect.center = (x, y)
        self.image.blit(label, rect)
