#!/usr/bin/python

# Pygame Minesweeper
# Written by Patrick Devine <pdevine@sonic.net>
#
# This version of Minesweeper is written as free software under the terms
# of the GPL version 2.  More information can be obtained at:
#
# http://www.gnu.org/licenses/gpl-2.0.html
#
# If you enjoy it, consider sending a note of gratitude to the author.
#
# About Pygame Minesweeper
# ------------------------
#
# This program was written over the course of about 4 or 5 evenings
# (maybe 8-9 hours, including a rewrite from Pyglet to Pygame just for
# grins and giggles), spanned over the course of about 4 months.  I wrote
# it mostly because I was interested in seeing how long it would take to 
# implement the basic reveal grid routine (recursion is fun), as well as
# the routine for counting the number of surrounding mines for each tile.
# The surrounding mine number problem was given as a Comp Sci 101 problem
# at Stanford that I had seen on their online course work, and I thought
# it sounded interesting.
#
# Once I'd finished those routines and had a basic working version of the
# game, I put it down and let it languish for a few months.  After
# letting it sit and bit rot for a few months, I realized I might as well
# put some more spit and polish on it and release it into the wild.
#

import pygame

import time
import random
import sys
import os.path

import effects

from util import dataName

tileImage = pygame.image.load(dataName('tile.png'))
blinkImage = pygame.image.load(dataName('tile-red.png'))
tileInverseImage = pygame.image.load(dataName('tile-inverse.png'))
bombImage = pygame.image.load(dataName('bomb.png'))
bombHitImage = pygame.image.load(dataName('bomb-inverse.png'))

flagImage = pygame.image.load(dataName('flag.png'))

GAME_SET_BOMBS = 1
GAME_ON = 2
GAME_OVER = 3
GAME_PAUSED = 4

TILE_WIDTH = tileImage.get_width()
TILE_HEIGHT = tileImage.get_height()

EDGE_WIDTH = 24
EDGE_TOP_HEIGHT = 80
EDGE_BOTTOM_HEIGHT = 24

bombImageDict = {}

for x in range(0, 8):
    bombImageDict[x] = pygame.image.load(dataName('%d.png' % x))

class Tile:
    def __init__(self, win, pos):
        self.win = win

        self.bomb = False
        self.bombCount = 0

        self.revealed = False
        self.flagged = False
        self.paused = False
        self.inverse = False
        self.blink = False

        self.column = pos[0]
        self.row = pos[1]
        self.hitBomb = False

    def draw(self, offset_x, offset_y):
        if self.paused or \
           (not self.revealed and not self.flagged and \
           not self.inverse):
            if not self.blink:
                tile = tileImage
            else:
                tile = blinkImage
        elif self.flagged:
            tile = flagImage
        elif self.revealed:
            if self.bomb and self.hitBomb:
                tile = bombHitImage
            elif self.bomb:
                tile = bombImage
            else:
                tile = bombImageDict.get(self.bombCount)

            if not tile:
                tile = flagImage
        elif self.inverse:
            tile = tileInverseImage

        self.win.blit(tile, (self.column * TILE_WIDTH + offset_x,
                      self.row * TILE_HEIGHT + offset_y))


class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.grid = []

        for y in range(0, height):
            for x in range(0, width):
                self.grid.append(Tile(self.win, (x, y)))

    def __getitem__(self, key):
        return self.grid[key]

    def __setitem__(self, key, value):
        self.grid[key] = value

    def __str__(self, mode='grid'):
        text = ''
        for count, cell in enumerate(self.grid):
            if not count % self.width and count:
                text += "\n"
            if mode == 'grid':
                text += "%d " % int(cell.bomb)
            elif mode == 'count':
                text += "%d " % int(cell.bombCount)
            elif mode == 'reveal':
                text += "%d " % int(cell.revealed)

        return text

    def getPos(self, row, col):
        if -1 in [row, col]:
            return -1

        if row >= self.width or col >= self.width:
            return -1

        if row * self.width + col > self.width * self.height - 1:
            return -1

        return row * self.width + col

    def up(self, pos):
        return max(-1, pos - self.width)

    def down(self, pos):
        if pos + self.width >= self.width * self.height:
            return -1
        else:
            return pos + self.width

    def left(self, pos):
        if not pos % self.width:
            return -1
        else:
            return pos - 1

    def right(self, pos):
        if not (pos + 1) % self.width:
            return -1
        else:
            return pos + 1

    def upleft(self, pos):
        if self.up(pos) == -1 or \
           self.left(pos) == -1:
            return -1
        else:
            return pos - self.width - 1

    def upright(self, pos):
        if self.up(pos) == -1 or \
           self.right(pos) == -1:
            return -1
        else:
            return pos - self.width + 1

    def downleft(self, pos):
        if self.down(pos) == -1 or \
           self.left(pos) == -1:
            return -1
        else:
            return pos + self.width - 1

    def downright(self, pos):
        if self.down(pos) == -1 or \
           self.right(pos) == -1:
            return -1
        else:
            return pos + self.width + 1

class BombGrid(Grid):
    def __init__(self, win, width=10, height=10, totalBombs=9, levelTime=40,
                 blinkTime=-1):
        self.win = win
        self.active = False
        self.autoBlink = blinkTime

        self.width = width
        self.height = height
        self.totalBombs = totalBombs

        self.levelTime = levelTime
        self.bombEffect = \
            effects.Bomb(win, self.levelTime, pos=(40, 40), finalPos=(40, 40))
        self.explosionEffect = effects.Explosion(win, (200, 100))

        self.reset()

        self.x = 0
        self.y = 0

        self.offset_x = int(self.win.get_width() / 2 - width / 2.0 * TILE_WIDTH)
        self.offset_y = self.win.get_height() - int(240 - height / 2.0 * 
                        TILE_HEIGHT) - (height * TILE_HEIGHT)

        self.timerOn = False
        self.timer = 0

        self.ft = pygame.font.SysFont('Arial', 40)
        self.awesomeFt = pygame.font.Font(dataName('badabb__.ttf'), 90)

        self.blinkTime = 300
        self.blinkCount = 300
        self.blinkState = False

    def reset(self):
        Grid.__init__(self, width=self.width, height=self.height)
        self.gridState = GAME_SET_BOMBS
        self.flags = self.totalBombs
        self.winner = False
        self.timer = 0
        self.bombEffect.totalTime = self.levelTime
        self.explosionEffect.reset()

    def update(self, tick):
        if self.timerOn and not self.gridState == GAME_PAUSED:
            self.timer += tick / 1000.0

            self.bombEffect.update(tick)

            if self.bombEffect.totalTime <= self.autoBlink:
                self.blinkCount -= tick
                if self.blinkCount <= 0:
                    self.blinkState = not self.blinkState
                    self.blinkBombs(self.blinkState)
                    self.blinkCount = self.blinkTime

            if self.bombEffect.totalTime <= 0:
                self.revealAll()
                self.gridState = GAME_OVER 
                self.timerOn = False

                if self.checkAllMinesCovered():
                    self.winner = True
                else:
                    self.winner = False
                    self.explosionEffect.explode()

        self.explosionEffect.update(tick)

    def setBombs(self, firstTile):
        self.createBombGrid(firstTile)
        self.createBombCountGrid()

        self.gridState = GAME_ON
        self.flags = self.totalBombs

    def togglePaused(self):
        for tile in self.grid:
            tile.paused = not tile.paused

        if self.gridState == GAME_ON:
            self.gridState = GAME_PAUSED
        else:
            self.gridState = GAME_ON

    def draw(self, offset_x=0, offset_y=0):
        for tile in self.grid:
            tile.draw(offset_x, offset_y)

        flagCountText = "%d/%d" % (self.flags, self.totalBombs)
        flagCountImg = self.ft.render(flagCountText, True, (0, 0, 0))
        self.win.blit(flagCountImg,
            (self.win.get_width() - flagCountImg.get_width() - EDGE_WIDTH, 20))


        if (self.gridState == GAME_OVER and self.winner) or \
           self.gridState == GAME_PAUSED:
            if self.gridState == GAME_OVER:
                gameText = "SUPER!"
            else:
                gameText = "PAUSED"

            gameTextImg = self.awesomeFt.render(gameText, True, (255, 0, 0))
            gameTextBgImg = self.awesomeFt.render(gameText, True, (0, 0, 0))

            gameTextRect = gameTextImg.get_rect()
            gameTextRect.center = (self.win.get_width() / 2,
                                   self.win.get_height() / 2)

            self.win.blit(gameTextBgImg,
                          (gameTextRect.topleft[0] - 5,
                           gameTextRect.topleft[1] + 5))
            self.win.blit(gameTextImg, gameTextRect.topleft)


        self.bombEffect.draw()

        self.explosionEffect.draw()

    def createBombGrid(self, firstTile):
        # place the bombs randomly
        count = 0
        while count < self.totalBombs:
            cell = random.randint(0, self.width * self.height - 1)

            if self.grid[cell].bomb or cell == firstTile:
                continue

            self.grid[cell].bomb = True
            count += 1

    def createBombCountGrid(self):
        for pos in range(0, self.width * self.height):
            self.findSurroundingBombs(pos)

    def findSurroundingBombs(self, pos):
        row = pos / self.width
        col = pos % self.width

        for bombRow in [-1, 0, 1]:
            for bombCol in [-1, 0, 1]:
                bombPos = self.getPos(row + bombRow, col + bombCol)
                if bombPos > -1:
                    if self.grid[bombPos].bomb:
                        self.grid[pos].bombCount += 1

    def revealPos(self, pos):
        if pos == -1 or self.grid[pos].revealed:
            return

        self.grid[pos].revealed = True

        if self.grid[pos].bombCount:
            return

        self.revealPos(self.up(pos))
        self.revealPos(self.left(pos))
        self.revealPos(self.right(pos))
        self.revealPos(self.down(pos))

        self.revealPos(self.upleft(pos))
        self.revealPos(self.upright(pos))
        self.revealPos(self.downleft(pos))
        self.revealPos(self.downright(pos))

    def checkPos(self, pos):
        return pos > -1 and \
           not self.grid[pos].revealed and \
           not self.grid[pos].bombCount

    def countGrid(self):
        return self.__str__(mode='count')

    def revealGrid(self):
        return self.__str__(mode='reveal')

    def eventHandler(self, event):

        if event.type == pygame.MOUSEBUTTONUP:

            button = event.button
            pos = self.getTilePos(event.pos)

            if button == 1:
                if self.gridState == GAME_SET_BOMBS and pos != -1:
                    # start the game over
                    self.setBombs(pos)
                    self.revealPos(pos)
                    self.timerOn = True
                elif self.gridState == GAME_PAUSED:
                    self.togglePaused()
                    return
                elif self.gridState == GAME_OVER:
                    self.reset()
                    self.explosionEffect.reset()
                elif self.gridState == GAME_ON:
                    if pos == -1:
                        self.togglePaused()
                        return

                    if self.grid[pos].flagged:
                        return

                    self.revealPos(pos)
                    if self.grid[pos].bomb:
                        self.grid[pos].hitBomb = True
                        self.revealAll()
                        self.gridState = GAME_OVER 
                        self.timerOn = False
                        self.explosionEffect.explode()

            elif button == 2:
                self.grid[pos].inverse = False

            elif button == 3:
                if self.gridState == GAME_OVER:
                    return

                self.grid[pos].inverse = False

                if self.flags > 0 and not self.grid[pos].revealed:
                    if self.grid[pos].flagged:
                        self.flags += 1
                        self.grid[pos].flagged = False
                    else:
                        self.flags -= 1
                        self.grid[pos].flagged = True


            if self.checkAllMinesCleared() and not self.gridState == GAME_OVER:
                self.gridState = GAME_OVER
                self.winner = True
                self.timerOn = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            button = event.button

            if button in [1, 3]:
                pos = self.getTilePos(event.pos)
                self.grid[pos].inverse = True

        elif event.type == pygame.MOUSEMOTION:
            left, middle, right = event.buttons

            if left or right:
                self.resetInverseTiles()
                pos = self.getTilePos(event.pos)
                self.grid[pos].inverse = True

    def resetInverseTiles(self):
        for tile in self.grid:
            tile.inverse = False

    def getTilePos(self, pos):
        localX = pos[0] - self.offset_x
        localY = pos[1] - self.offset_y

        if localX < 0 or localX > TILE_WIDTH * self.width or \
           localY < 0 or localY > TILE_HEIGHT * self.height:
            pos = -1
        else:
            pos = self.getTileNumber(localX, localY)

        return pos


    def checkAllMinesCleared(self):
        for tile in self.grid:
            if not tile.revealed and \
               not (tile.bomb and tile.flagged):
                return False
        return True

    def checkAllMinesCovered(self):
        for tile in self.grid:
            if tile.bomb and not tile.flagged:
                return False
        return True

    def revealAll(self):
        for tile in self.grid:
            if not tile.flagged and tile.bomb:
                tile.revealed = True

    def blinkBombs(self, blinkState):
        for tile in self.grid:
            if not tile.flagged and not tile.revealed and tile.bomb:
                tile.blink = blinkState

    def getTileNumber(self, x, y):
        column = x / TILE_WIDTH
        row = y / TILE_HEIGHT

        return self.width * row + column

class BombGridManager:
    def __init__(self, win, level):

        columns = level['columns']
        rows = level['rows']

        bombs = level['bombs']
        flags = level['flags']

        levelTime = level['time']
        blinkTime = level['autoblink']

        self.slideTiles = effects.SlideTileGrid(win, columns, rows)
        self.bombGrid = BombGrid(win, width=columns, height=rows,
                                 totalBombs=bombs, levelTime=levelTime,
                                 blinkTime=blinkTime)

        self.offsetX = int(320 - columns / 2.0 * TILE_WIDTH)
        self.offsetY = 480 - int(240 - rows / 2.0 * TILE_HEIGHT) - \
            rows * TILE_HEIGHT

        # XXX - fixme

        self.bombGrid.offsetX = self.offsetX
        self.bombGrid.offsetY = self.offsetY

    def update(self, tick):
        if not self.slideTiles.finished:
            self.slideTiles.update(tick)
        else:
            self.bombGrid.update(tick)

    def draw(self):
        if not self.slideTiles.finished:
            self.slideTiles.draw()
        else:
            self.bombGrid.draw(self.offsetX, self.offsetY)

    def eventHandler(self, event):
        if self.slideTiles.finished:
            self.bombGrid.eventHandler(event)

def main(boardType):
    pygame.init()

    rows, cols, bombs = boardType

    width = TILE_WIDTH * cols + EDGE_WIDTH * 2
    height = TILE_HEIGHT * rows + EDGE_TOP_HEIGHT + EDGE_BOTTOM_HEIGHT
    win = pygame.display.set_mode((width, height))

    bg = BombGrid(win, width=cols, height=rows, totalBombs=bombs)
    bg.active = True

    bg.offset_x = EDGE_WIDTH
    bg.offset_y = EDGE_TOP_HEIGHT

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                bg.eventHandler(event)
                #bg.mouseUp(event.button, event.pos)

        # keep the frame rate low
        tick = clock.tick(30)

        bg.update(tick)

        win.fill((200, 200, 255))

        bg.draw(bg.offset_x, bg.offset_y)

        pygame.display.flip()

def usage():
    buf = '''Usage: minesweeper.py [options]
Options:
  -h                Display this information
  -b                Beginner Mode (9x9 grid, 10 mines)
  -i                Intermediate Mode (16x16 grid, 40 mines)
  -e                Expert Mode (30x16 grid, 99 mines)
'''

    return buf

if __name__ == '__main__':
    import getopt

    boardType = (9, 9, 10)

    optlist, args = getopt.getopt(sys.argv[1:], 'bieh')

    for opt in optlist:
        if opt[0] == '-b':
            boardType = (9, 9, 10)
        elif opt[0] == '-i':
            boardType = (16, 16, 40)
        elif opt[0] == '-e':
            boardType = (16, 30, 99)
        elif opt[0] == '-h':
            print usage()
            boardType = None

    if boardType:
        main(boardType)

