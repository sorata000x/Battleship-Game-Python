"""
Reference
    Battleship
        https://www.datagenetics.com/blog/december32011/index.html
    Calling parent class __init__ with multiple inheritance, what's the right way?
        https://stackoverflow.com/questions/9575409/calling-parent-class-init-with-multiple-inheritance-whats-the-right-way
"""

import pygame
import json
from utility.mouse import Mouse
from random import randrange, choice
from utility.exception import ShipPositionException


class Fleet:
    """ base class of fleets """
    def __init__(self, targetGrid, player):
        """
        :param: targetGird: TileGrid of fleet is going to be located on
        :param: player: String of either 'Player' or 'Enemy' indicate side
        """
        self.targetGrid = targetGrid
        self.player = player
        # ------- Fleet ----------
        self.shipList = {}
        self._initShipList()
        self.readShipsJSON()

    # -------- Initialization ---------
    def _initShipList(self):
        """ initialize ship list """
        self.shipList = {
            # Place ships somewhere out of the board
            'Carrier': PlayerShip(Ship.CARRIER, 999, 999, self.targetGrid),
            'Battleship': PlayerShip(Ship.BATTLESHIP, 999, 999, self.targetGrid),
            'Cruiser': PlayerShip(Ship.CRUISER, 999, 999, self.targetGrid),
            'Submarine': PlayerShip(Ship.SUBMARINE, 999, 999, self.targetGrid),
            'Destroyer': PlayerShip(Ship.DESTROYER, 999, 999, self.targetGrid)
        }

    # -------- JSON file --------------
    # NOT TESTED
    def createShipsJSON(self):
        """ Write current ship position into JSON file"""
        json_object = {}
        shipsPos = {}
        for name, ship in self.shipList.items():
            shipsPos[name] = ship.getPosList()
        json_object[self.player] = shipsPos
        with open('ships.json', 'w') as outfile:
            json.dump(json_object, outfile)

    def readShipsJSON(self):
        """ Read and process ship info from ships.json file """
        with open('ships.json', 'r') as openfile:
            json_object = json.load(openfile)
        self.processShipsJSON(json_object[self.player])

    def processShipsJSON(self, ships_info):
        """ Process ship info read from ships.json file """
        for name, info in ships_info.items():
            self.shipList[name].update(tuple(info[0]), info[1])
        self.validateShip()

    # -------- Check ------------------
    def validateShip(self):
        """ Validate ship position """
        posList = []
        for name, ship in self.shipList.items():
            posList += ship.getPosList()
        verifiedPos = []
        for pos in posList:     # Check is in range
            if pos in verifiedPos or not self.targetGrid.gridInRange(pos):
                raise ShipPositionException('Incorrect ship position in file.')
            else:
                verifiedPos.append(pos)

    def allSink(self):
        """ Check if all ship have sunk """
        for name, ship in self.shipList.items():
            if not ship.sink():
                return False
        return True

    def getShipAt(self, row, col):
        for name, ship in self.shipList.items():
            if ship.isAt(row, col):
                return ship
        return None


class PlayerFleet(Fleet, pygame.sprite.LayeredUpdates):
    """ fleet control by player """
    def __init__(self, targetGrid):
        """
        :param targetGrid: TileGrid of fleet is going to be located on
        """
        Fleet.__init__(self, targetGrid, 'Player')      # __init__ Fleet
        pygame.sprite.LayeredUpdates.__init__(self)     # __init__ pygame.sprite.LayeredUpdates
        for name, ship in self.shipList.items():
            self.add(ship)

    # ------ Ship Configuration ------
    def shipsPlaced(self):
        """ Check if all ship in the fleet are placed in the grid. """
        for name, ship in self.shipList.items():
            if not ship.placed:
                return False
        return True

    def move(self, x, y):
        """ move selected ship to one position """
        for name, ship in self.shipList.items():
            if ship.selected:
                ship.move(x - ship.relative_x - ship.rect.x, y - ship.relative_y - ship.rect.y)

    def grab(self, x, y):
        """ select ship at the location. """
        mouse = Mouse(x, y)
        for name, ship in self.shipList.items():
            print(f'ship: info:{ship}x:{ship.rect.x}y:{ship.rect.y}, mouse: {mouse}')
            if pygame.sprite.collide_rect(ship, mouse):
                print("blob")

                ship.grab(x, y)

    def release(self):
        """ release selected ship. """
        for name, ship in self.shipList.items():
            if ship.selected:
                grid = self.targetGrid.findGrid((ship.rect[0] + self.targetGrid.tileSize[0] / 2,
                                                 ship.rect[1] + self.targetGrid.tileSize[1] / 2), (40, 40))
                nx, ny = (self.targetGrid.findCoord(grid, (40, 40))[0],
                          self.targetGrid.findCoord(grid, (40, 40))[1])
                ship.drop(nx, ny)
                for pos in ship.getPosList():
                    if not self.targetGrid.gridInRange((pos[0], pos[1])):
                        ship.reset()


class EnemyFleet(Fleet, pygame.sprite.LayeredUpdates):
    """ enemy fleet control by AI """
    DIRECTION = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    def __init__(self, targetGrid, playerFleet):
        """
        :param targetGrid: TileGrid of fleet is going to be located on
        """
        Fleet.__init__(self, targetGrid, 'Enemy')
        pygame.sprite.LayeredUpdates.__init__(self)
        # ------ Info -------
        self.fired = list()
        self.targets = []  # list of potential targets
        self.start = None
        self.playerFleet = playerFleet
        # ------ Mode -------
        self.hunt = True
        self.target = False

    # ------ Graphic -------
    def checkSunk(self):
        """ display ship of if has sunk """
        for name, ship in self.shipList.items():
            if ship.sink():
                self.add(ship)

    # ------ AI ------------
    def fire(self):
        """ decide how to find the where to fire and return the finding result. """
        self.removeFiredTargets()
        if self.hunt:
            return self.randomFire()
        if self.target:
            return self.targetFire()

    def randomFire(self):
        """ randomly fired at empty location """
        randGrid = [(randrange(0, 10, 2), randrange(0, 10, 2)), (randrange(0, 8, 2) + 1, randrange(0, 8, 2) + 1)]
        fire = choice(randGrid)     # randomly select even row and odd col
        while fire in self.fired:       # prevent firing at same place
            randGrid = [(randrange(0, 10, 2), randrange(0, 10, 2)), (randrange(0, 8, 2) + 1, randrange(0, 8, 2) + 1)]
            fire = choice(randGrid)
        self.fired.append(fire)
        return fire

    def targetFire(self):
        """ make a fire from the target list """
        if len(self.targets) == 0:
            return self.randomFire()
        fire = self.targets.pop(-1)
        self.fired.append(fire)
        if len(self.targets) == 0:
            self.hunt, self.target = True, False
        return fire

    def markHit(self):
        """ add potential targets to list. """
        if self.target:
            self.removeTargets()    # remove unwanted targets
            if self.start is None:
                sx, sy = 99, 99
            else:
                sx, sy = self.start
            lx, ly = self.fired[-1]
            x, y = lx-sx, ly-sy
            if (x, y) in self.DIRECTION:
                newTarget = (lx + x, ly + y)
            else:
                sx, sy = self.fired[-2]
                lx, ly = self.fired[-1]
                x, y = lx - sx, ly - sy
                newTarget = (lx + x, ly + y)
            if self.targetGrid.gridInRange(newTarget):
                self.targets.append(newTarget)
        else:
            self.hunt, self.target = False, True
            if self.start is not None:
                sx, sy = self.start
                if self.fired[-1] == (sx + 1, sy):
                    lx, ly = self.fired[-1]
                    newTarget = (lx+1, ly)
                    if self.targetGrid.gridInRange(newTarget):
                        self.targets.append(newTarget)
                    self.start = self.fired[-1]
                else:
                    self.start = self.fired[-1]
                    for (x, y) in self.DIRECTION:
                        lx, ly = self.fired[-1]
                        newTarget = (lx + x, ly + y)
                        if self.targetGrid.gridInRange(newTarget):
                            self.targets.append(newTarget)
            else:
                self.start = self.fired[-1]
                for (x, y) in self.DIRECTION:
                    lx, ly = self.fired[-1]
                    newTarget = (lx+x, ly+y)
                    if self.targetGrid.gridInRange(newTarget):
                        self.targets.append(newTarget)

    def removeTargets(self):
        """ remove unwanted targets (algorithm improve). """
        sx, sy = self.start
        if self.fired[-1] == (sx, sy-1):
            if (sx-1, sy) in self.targets:
                self.targets.remove((sx-1, sy))
            if (sx+1, sy) in self.targets:
                self.targets.remove((sx+1, sy))
        elif self.fired[-1] == (sx-1, sy):
            if (sx, sy+1) in self.targets:
                self.targets.remove((sx, sy+1))
        elif self.fired[-1] == (sx, sy+1):
            if (sx+1, sy) in self.targets:
                self.targets.remove((sx+1, sy))

    def removeFiredTargets(self):
        """ removed targets that are already fired """
        for target in self.targets:
            if target in self.fired:
                self.targets.remove(target)
        if self.start:
            targetShip = self.playerFleet.getShipAt(self.start[0], self.start[1])
            if targetShip is not None and targetShip.sink():
                self.targets = []
                self.start = None
                self.hunt, self.target = True, False


class Ship(pygame.sprite.Sprite):
    """ base class for all the ships """
    # ----- Size of ship type -----
    CARRIER = 5
    BATTLESHIP = 4
    CRUISER = 3
    SUBMARINE = 3.5
    DESTROYER = 2
    # ----- Orientation ---------
    VERTICAL = True
    HORIZONTAL = False

    def __init__(self, shipType, row, col, targetGrid):
        """
        :param targetGrid (TileGrid) : tile grid of the ship is located on.
        """
        pygame.sprite.Sprite.__init__(self)
        # -------- Info ---------
        self.shipType = shipType
        self.row, self.col = row, col
        self.targetGrid = targetGrid
        self.orientation = self.VERTICAL
        self.hp = self.shipType if shipType != self.SUBMARINE else 3
        # -------- Surface ---------
        self.image = pygame.image.load(f'image/ship/{self._getShipFileName()}')
        if self.shipType == self.SUBMARINE:
            self.shipType = 3
        width = targetGrid.tileSize[0]
        height = self.shipType * targetGrid.tileSize[1] + (self.shipType - 1) * targetGrid.spacing
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = targetGrid.findCoord((row, col))

    def _getShipFileName(self):
        """ get the file name based on ship type. """
        match self.shipType:
            case self.CARRIER:
                return 'carrier.png'
            case self.BATTLESHIP:
                return 'battleship.png'
            case self.CRUISER:
                return 'cruiser.png'
            case self.SUBMARINE:
                return 'submarine.png'
            case self.DESTROYER:
                return 'destroyer.png'

    def getName(self):
        """ get the file name based on ship type. """
        match self.shipType:
            case self.CARRIER:
                return 'Carrier'
            case self.BATTLESHIP:
                return 'Battleship'
            case self.CRUISER:
                return 'Cruiser'
            case self.SUBMARINE:
                return 'Submarine'
            case self.DESTROYER:
                return 'Destroyer'

    def getPosList(self):
        """ get the positions of the tile the ship is on. """
        posList = []
        for i in range(int(self.shipType)):
            if self.orientation == self.VERTICAL:
                posList.append([self.row + i, self.col])
            else:
                posList.append([self.row, self.col + i])
        return posList

    def getHP(self):
        return self.hp

    def sink(self):
        """ check if the ship is sunk (hp==0). """
        return self.hp == 0

    def collide(self, grid):
        """ check if the ship is on the grid. """
        posList = self.getPosList()
        for pos in posList:
            if tuple(pos) == tuple(grid):
                return True
        return False

    def hit(self):
        """ decrease hp if being hit. """
        self.hp -= 1

    def update(self, grid, orient):
        """ change the grid and orientation """
        self.row, self.col = grid
        self.orientation = orient

    def isAt(self, row, col):
        for pos in self.getPosList():
            if pos == [row, col]:
                return True
        return False

    def __repr__(self):
        return f'name: {self.getName()}, position {self.getPosList()}'


class PlayerShip(Ship):
    def __init__(self, shipType, row, col, targetGrid):
        """
        :param targetGrid (TileGrid) : tile grid of the ship is located on.
        """
        Ship.__init__(self, shipType, row, col, targetGrid)
        # -------- Info ---------
        self.origin = targetGrid.findCoord((row, col))
        self.relative_x, self.relative_y = None, None
        self.selected = False
        self.placed = False

    def update(self, grid, orient):
        """ change the grid and orientation """
        oldOrient = self.orientation
        super().update(grid, orient)
        newCoord = self.targetGrid.findCoord(grid)
        self.rect.x, self.rect.y = (newCoord[0], newCoord[1])
        if orient != oldOrient:
            self.rotate()

    # INCOMPLETE
    def rotate(self):
        # TODO
        # self.orientation = not self.orientation
        # self.image = pygame.transform.flip(self.image, True, True)
        self.image = pygame.transform.rotate(self.image, 90)  # try this

    def grab(self, x, y):
        """ picked up """
        self.selected = True
        self.relative_x = x - self.rect.x
        self.relative_y = y - self.rect.y

    def drop(self, x, y):
        """ release """
        self.rect.x, self.rect.y = x, y
        self.row, self.col = self.targetGrid.findGrid((x, y))
        self.selected = False
        self.placed = True

    def move(self, dx, dy):
        """ move by a distance """
        self.rect.x = self.rect.x + dx
        self.rect.y = self.rect.y + dy
        self.row, self.col = self.targetGrid.findGrid((self.rect.x, self.rect.y))

    def reset(self):
        """ put back to original position """
        self.rect.x, self.rect.y = self.origin
        self.row, self.col = self.targetGrid.findGrid((self.rect.x, self.rect.y))
        self.selected = False
        self.placed = False
