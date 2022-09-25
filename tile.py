import pygame
from utility.color import *
from utility.mouse import Mouse
from gamebase import ImageSprite


class TileGrid (pygame.sprite.Sprite):
    """ a surface of tiles separated by space """

    def __init__(self, size, pos, spacing=2):
        super().__init__()
        # --------- Info ----------
        self.size = size            # size of whole grid
        self.dim = (10, 10)         # dimension; number of row and column
        self.spacing = spacing      # space between each tile
        # ------- Surface ---------
        self.image = pygame.Surface((size[0]+spacing, size[1]+spacing))   # a surface for tiles includes spacing
        self.image.fill(WHITE_BLUE)             # fill with the color of spaces between tiles
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        # -------- Tiles ----------
        self.sprites = pygame.sprite.LayeredUpdates()       # group of tile sprite
        self.tileList = []          # store the list of tile sprite as Tile object
        self.tileSize = (self.size[0]/self.dim[0]-self.spacing, self.size[1]/self.dim[1]-self.spacing)
        self.drawTile()

    def draw(self, screen):
        """ Draw the board onto the screen """
        self.sprites.draw(self.image)
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def drawTile(self):
        """ Creates and draw tiles onto the surface as sprites """
        for row in range(10):
            for col in range(10):
                x, y = self.findCoord((row, col), (0, 0))
                tile = self.Tile('image/water.png', x, y, self.tileSize)
                self.tileList.append(tile)
                self.sprites.add(tile)
        self.sprites.draw(self.image)

    def mouseHover(self, x, y):
        """ display effect when mouse hovering on a square """
        for tile in self.tileList:
            bx, by = tile.x, tile.y
            ex, ey = bx+tile.size[0], by+tile.size[1]
            if bx <= x <= ex and by <= y <= ey:
                tile.highLight(HIGH_LIGHT_BLUE)
            else:
                tile.reset()
        self.sprites.draw(self.image)

    def collide(self, x, y, hitShip):
        """ check if mouse click on valid position of tile grid """
        valid = False
        mouse = Mouse(x, y)
        for tile in self.tileList:
            if not tile.fixed and pygame.sprite.collide_rect(tile, mouse):
                tile.reset()
                self.sprites.draw(self.image)
                if hitShip is not None:
                    tile.hit()
                    hitShip.hit()
                else:
                    tile.miss()
                self.Tile.number += 1
                self.sprites.change_layer(tile, 2)
                valid = True

                break
        self.sprites.draw(self.image)
        return valid

    def findGrid(self, coord, offset=(0, 0)):
        """ find corresponding row and col of coordinate """
        row = int((coord[1]-offset[1]) // (self.spacing + self.tileSize[1]))
        col = int((coord[0]-offset[0]) // (self.spacing + self.tileSize[0]))
        return row, col

    def findCoord(self, grid, offset=(0, 0)):
        """ find corresponding x and y of grid """
        x = grid[1] * (self.spacing + self.tileSize[0]) + self.spacing + offset[1]
        y = grid[0] * (self.spacing + self.tileSize[1]) + self.spacing + offset[0]
        return x, y

    def gridInRange(self, grid):
        """ verify if the row and col number is valid"""
        return 0 <= grid[0] < self.dim[0] and 0 <= grid[1] < self.dim[1]

    class Tile(ImageSprite):
        # ----- Debug -------
        number = 0
        debug = True
        # ----- Constant -----
        NULL = 0
        MISS = 1
        HIT = 2

        def __init__(self, file, x, y, size):
            super().__init__(x, y, file)
            # ---------- INFO ------------
            self.file = file
            self.x, self.y = x, y
            self.size = size
            # --------- SURFACE ----------
            self.image = pygame.image.load(file)        # tile image
            self.image = pygame.transform.scale(self.image, size)       # resize image
            self.originImg = self.image         # memorize the original image
            self.rect = self.image.get_rect()       # tile rectangle
            self.rect.x, self.rect.y = x, y        # internal position
            # ---------- STATE -----------
            self.fixed = False      # is still selectable or not
            self.state = self.NULL

        def highLight(self, color):
            """ display highlight effect """
            if not self.fixed:
                self.image = pygame.Surface(self.size)
                self.image.fill(color)

        def reset(self):
            """ reset to original tile (still water) """
            if not self.fixed:
                self.image = self.originImg

        def miss(self):
            """ display miss effect (water splash) """
            if not self.fixed:
                self.image = pygame.image.load('image/miss.png')
                self.image = pygame.transform.scale(self.image, self.size)
                self.state = self.MISS
                self.fixed = True
                if self.debug:
                    self.drawText(f'{self.number//2}', self.size[1]/2, self.size[0]/2)

        def hit(self):
            """ display hit effect (explosion) """
            if not self.fixed:
                self.image = pygame.image.load('image/hit.png')
                self.image = pygame.transform.scale(self.image, self.size)
                self.state = self.HIT
                self.fixed = True
                if self.debug:
                    self.drawText(f'{self.number//2}', self.size[1]/2, self.size[0]/2)

        def drawText(self, text, x, y, size=22):
            """ Draw text onto the surface """
            font = pygame.font.Font('freesansbold.ttf', size)
            FONT_COLOR = (255, 255, 255)
            label = font.render(text, False, FONT_COLOR)
            rect = label.get_rect()
            rect.center = (x, y)
            self.image.blit(label, rect)
