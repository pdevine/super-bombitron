
import pygame
import random

from math import sqrt, sin, cos, atan2, log

from random import randint
from util import dataName

BOMB_IMG = pygame.image.load(dataName('bigbomb2.png'))
TILE_IMG = pygame.image.load(dataName('tile.png'))
TILE_WIDTH = 20
TILE_HEIGHT = 20

pygame.font.init()
AWESOME_FT = pygame.font.Font(dataName('badabb__.ttf'), 30)

class ImageCount:
    def __init__(self, win, text, pos):
        self.win = win
        self.image = AWESOME_FT.render(text, True, (0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def draw(self, count=0):
        self.win.blit(self.image, self.rect.topleft)

        text = AWESOME_FT.render(str(count), True, (0, 0, 0))
        countRect = text.get_rect()
        countRect.center = self.rect.center
        self.win.blit(text, (countRect.topleft[0], countRect.topleft[1]+25))

class FlagCount(ImageCount):
    def __init__(self, win):
        ImageCount.__init__(self, win, 'Flags', (470, 20))

class BombCount(ImageCount):
    def __init__(self, win):
        ImageCount.__init__(self, win, 'Bombs', (550, 20))


class Spark:
    lifetimeRange = (150, 450)
    colors = [(255, 0, 0), (255, 255, 100), (255, 255, 0), (10, 10, 10)]

    def __init__(self, win, pos):
        self.win = win

        self.dead = False

        self.color = random.choice(self.colors)
        self.pos = pos
        self.lifetime = randint(*self.lifetimeRange)

        self.velocity = [randint(-2, 2), randint(-3, 1)]

    def update(self, tick):
        self.lifetime -= tick
        if self.lifetime <= 0:
            self.dead = True

        self.pos = (self.pos[0] + self.velocity[0],
                    self.pos[1] + self.velocity[1])

    def draw(self):
        pygame.draw.circle(self.win, self.color, self.pos, 2)

class SparkManager:
    def __init__(self, win, pos):
        self.win = win
        self.pos = pos
        self.sparks = []

        self.sparkInterval = 100
        self.sparkTimer = self.sparkInterval

    def update(self, tick):
        self.sparkTimer -= tick

        if self.sparkTimer <= 0:
            self.sparks.append(Spark(self.win, self.pos))
            self.sparkTimer = self.sparkInterval

        for spark in self.sparks:
            spark.update(tick)

            if spark.dead:
                self.sparks.remove(spark)

    def draw(self):
        for spark in self.sparks:
            spark.draw()

class Bomb:
    def __init__(self, win, totalTime=10, rot=0, pos=(170, 200),
                 finalPos=(170, 200)):
        self.image = BOMB_IMG.copy()
        self.pos = pos
        self.finalPos = finalPos
        self.win = win

        self.totalTime = totalTime

        self.startRot = rot
        self.rot = rot

        self.rect = BOMB_IMG.get_rect()
        self.rect.center = self.pos

        self.sparks = SparkManager(win, 
            (self.rect.x + self.image.get_width(), self.rect.y))

    def explode(self):
        self.rect.center = self.finalPos
        self.sparks.pos = self.rect.topright
        self.rot = 0
        self.image = BOMB_IMG.copy()

    def reset(self):
        self.rect.center = self.pos
        self.rot = self.startRot

    def update(self, tick):
        self.totalTime -= tick / 1000.0
        self.sparks.update(tick)

        center = self.rect.center
        self.image = pygame.transform.rotate(BOMB_IMG, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = center

        if self.rect.centerx < self.finalPos[0]:
            self.rot -= 3
            self.rect.x += 3
            if self.rect.centerx > self.finalPos[0]:
                self.rect.centerx = self.finalPos[0]
                self.sparks.pos = self.rect.topright
        elif self.rect.centerx > self.finalPos[0]:
            self.rot += 3
            self.rect.centerx -= 3
            if self.rect.centerx < self.finalPos[0]:
                self.rect.centerx = self.finalPos[0]
                self.sparks.pos = self.rect.topright

    def draw(self):
        self.win.blit(self.image, self.rect.topleft)

        if self.totalTime > 10 + 1:
            color = (255, 255, 255)
        else:
            color = (255, 0, 0)

        if self.totalTime >= 0:
            timerText = AWESOME_FT.render("%d" % self.totalTime, True, color)
            self.win.blit(timerText,
                (centerImage(self.image, timerText) + self.rect.x,
                 self.rect.y+27))

        if self.rect.centerx == self.finalPos[0]:
            self.sparks.draw()

class Explosion:
    def __init__(self, win, pos):
        self.win = win
        self.pos = pos

        self.image = pygame.image.load(dataName('small-explosion.png'))
        self.ft = pygame.font.Font(dataName('badabb__.ttf'), 60)

        self.reset()

    def reset(self):
        self.tick = 0
        self.fullTextTime = 600
        self.clearImageTime = 1200
        self.shortString = True
        self.explosion = False
        self.exploded = False

    def explode(self):
        self.explosion = True

    def update(self, tick):
        if self.explosion and self.fullTextTime > 0:
            self.fullTextTime -= tick
        elif self.explosion and self.clearImageTime > 0 and \
           self.fullTextTime <= 0:
            self.shortString = False
            self.clearImageTime -= tick
        elif self.clearImageTime <= 0:
            self.exploded = True

    def draw(self):
        if not self.explosion or self.clearImageTime <= 0:
            return

        self.win.blit(self.image, self.pos)

        if self.shortString:
            explodeText = "KA-"
        else:
            explodeText = "KA-BOOM!"

        textBg = self.ft.render(explodeText, True, (0, 0, 0))
        text = self.ft.render(explodeText, True, (255, 255, 255))

        self.win.blit(textBg, (self.pos[0]+25, self.pos[1]+85))
        self.win.blit(text, (self.pos[0]+20, self.pos[1]+80))


def centerImage(image1, image2):
    return image1.get_width() / 2 - image2.get_width() / 2

class FallingTile:
    def __init__(self, win, pos):
        self.win = win

        self.image = TILE_IMG.copy()
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.vec_y = 0

        self.finished = False
        self.fallRate = randint(25, 55)

    def update(self, tick):
        self.vec_y += tick / 1000.0 * self.fallRate
        self.rect.y += self.vec_y

        if self.rect.top > 480:
            self.finished = True

    def draw(self):
        self.win.blit(self.image, self.rect.topleft)


class FallingTileGrid:
    def __init__(self, win, width, height):
        self.win = win
        self.width = width
        self.height = height
        self.reset()

    def reset(self):
        self.active = False
        self.finished = False
        self.tiles = []

        offsetX = int(320 - self.width / 2.0 * TILE_WIDTH) + 10
        offsetY = 480 - int(240 - self.height / 2.0 * TILE_HEIGHT)

        for row in range(self.width):
            for col in range(self.height):
                self.tiles.append(
                    FallingTile(self.win,
                        (offsetX + row * 20, offsetY - col * 20)))

    def copyGrid(self, grid):
        for count, tile in enumerate(grid):
            self.tiles[count].image = tile.currentTile.copy()

    def update(self, tick):
        # set the finished flag to true but turn it back off
        # if we're not done
        self.finished = True

        for tile in self.tiles:
            tile.update(tick)

            if not tile.finished:
                self.finished = False

    def draw(self):
        for tile in self.tiles:
            tile.draw()


class SlideTile:
    def __init__(self, win, pos, finalPos):
        self.win = win

        self.finished = False

        self.image = TILE_IMG.copy()
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.velocityX = 0
        self.velocityY = 0

        self.finalPos = finalPos

    def update(self, tick):
        opp = self.finalPos[0] - self.rect.center[0]
        adj = self.finalPos[1] - self.rect.center[1]

        rad = atan2(opp, adj)

        self.velocityX = 8 * sin(rad)
        self.velocityY = 15 * cos(rad)

        distance = sqrt(pow(self.finalPos[0] - self.rect.center[0], 2) + \
                        pow(self.finalPos[1] - self.rect.center[1], 2))

        if distance < 100 and distance > 11:
            braking = log(distance, 10) - 1
            self.velocityX *= braking
            self.velocityY *= braking
        elif distance <= 11:
            self.velocityX = 0
            self.velocityY = 0
            self.rect.bottom = self.finalPos[1]
            self.finished = True

        self.rect.x += self.velocityX
        self.rect.y += self.velocityY

    def draw(self):
        self.win.blit(self.image, self.rect.topleft)
    
class SlideTileGrid:
    def __init__(self, win, width, height):
        self.win = win
        self.width = width
        self.height = height

        self.reset()

    def reset(self):
        self.finished = False
        self.tiles = []

        offsetX = int(320 - self.width / 2.0 * TILE_WIDTH) + 10
        offsetY = 480 - int(240 - self.height / 2.0 * TILE_HEIGHT) + 20

        for row in range(self.width):
            for col in range(self.height):

                self.tiles.append(
                    SlideTile(self.win, (offsetX + row * 20, 0 - col * 60),
                                   (offsetX + row * 20, offsetY - col * 20)))

    def update(self, tick):
        # set the finished flag to true but turn it back off
        # if we're not done
        self.finished = True

        for tile in self.tiles:
            tile.update(tick)

            if not tile.finished:
                self.finished = False

    def draw(self):
        for tile in self.tiles:
            tile.draw()

class SpinTile:
    def __init__(self, win):
        self.win = win

        self.rot = 0
        self.rotSpeed = random.choice([3, -3])

        self.pos = (random.randint(20, 620), 0)
        self.image = TILE_IMG.copy()

        self.rect = TILE_IMG.get_rect()
        self.rect.center = self.pos

        self.dead = False

    def update(self, tick):
        center = self.rect.center
        self.image = pygame.transform.rotate(TILE_IMG, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = center

        self.rot += self.rotSpeed
        self.rect.y += 4

        if self.rect.top > 640:
            self.dead = True
    
    def draw(self):
        self.win.blit(self.image, self.rect.topleft)


class Credits:
    def __init__(self, win):
        self.win = win
        self.y = 500

        credits = [
            ('Concept', 'Patrick Devine'),
            ('Programming', 'Patrick Devine'),
            ('Artwork', 'Patrick Devine'),
            ('Production', 'Patrick Devine'),
            ('Fonts', 'urbanfonts.com'),
            ('Play testing', 'Shandy Brown'),
            ('Moral Support', 'Linda Jiang, Saoirse Devine'),
            ('Tools', 'pygame, python, inkscape, gimp'),
        ]

        secondCredits = [
            'A Patrick Devine Production',
            'copyright 2009',
            'bombitron.com',
        ]

        self.creditList = []

        for count, entry in enumerate(credits):
            work, person = entry
            credit = \
                (AWESOME_FT.render(work, True, (255, 0, 0)), count * 150)
            self.creditList.append(credit)

            credit = \
                (AWESOME_FT.render(person, True, (0, 0, 0)), count * 150 + 30)
            self.creditList.append(credit)

        lastPlace = self.creditList[-1][1] + 100

        for count, entry in enumerate(secondCredits):
            credit = \
                (AWESOME_FT.render(entry, True, (255, 0, 0)),
                 (count + 2) * 30 + lastPlace)

            self.creditList.append(credit)

        self.finished = False

    def update(self, tick):
        self.y -= 2
        # look at the last credit's position and see if it's scrolled
        # off the screen

        if self.y + self.creditList[-1][1] + 30 < 0:
            self.finished = True
            

    def draw(self):
        for credit in self.creditList:
            text, pos = credit
            self.win.blit(text, (100, self.y + pos))


if __name__ == '__main__':
    import pygame
    pygame.init()

    win = pygame.display.set_mode((640, 480))

    clock = pygame.time.Clock()

    bomb = Bomb(win, pos=(570,200), finalPos=(130,200), rot=-81)
    explosion = Explosion(win, (100, 100))

    while False:
        tick = clock.tick(30)

        bomb.update(tick)
        explosion.update(tick)

        win.fill((255, 255, 255))

        bomb.draw()

        if bomb.totalTime <= 0:
            explosion.explode()

        explosion.draw()

        pygame.display.flip()

    credits = Credits(win)

    while credits.finished == False:
        tick = clock.tick(30)

        credits.update(tick)

        win.fill((200, 200, 255))

        credits.draw()

        pygame.display.flip()


    tiles = SlideTileGrid(win, 16, 16)

    while not tiles.finished:
        tick = clock.tick(30)

        tiles.update(tick)

        win.fill((200, 200, 255))

        tiles.draw()

        pygame.display.flip()

    tiles = FallingTileGrid(win, 16, 16)

    while True:
        tick = clock.tick(30)

        tiles.update(tick)

        win.fill((200, 200, 255))

        tiles.draw()

        pygame.display.flip()


