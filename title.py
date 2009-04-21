import sys

import pygame
import random

import effects
import bombs

from bombs import dataName

TILE_IMG = pygame.image.load(dataName('tile.png'))

class TitleBackground:
    def __init__(self, win):
        self.win = win

        self.tiles = [effects.SpinTile(self.win)]

        self.tileAppendSpeed = 500
        self.countDown = self.tileAppendSpeed

        self.active = True

    def toggleActive(self):
        if self.active:
            self.active = False
        else:
            self.active = True
            self.countDown = self.tileAppendSpeed

    def update(self, tick):
        if self.active:
            self.countDown -= tick

            if self.countDown <= 0:
                self.tiles.append(effects.SpinTile(self.win))
                self.countDown = self.tileAppendSpeed

        for tile in self.tiles:
            if tile.dead:
                self.tiles.remove(tile)
                continue

            tile.update(tick)

    def draw(self):
        for tile in self.tiles:
            tile.draw()

class Title:
    def __init__(self, win):
        self.win = win
        self.superImg = pygame.image.load(dataName('super.png'))

        self.bomb = effects.Bomb(self.win, pos=(640, 140), finalPos=(180, 140),
                                 rot=-102)
        self.bomb.totalTime = -1
        self.explosion = effects.Explosion(self.win, (80, 50))

        self.superPause = 1000
        self.superPauseTimer = self.superPause

        self.xSpeed = 15
        self.ySpeed = 15

        self.finalPos = (40, 80)
        self.pos = (-200, 80)
        self.ft = pygame.font.Font(dataName('Galatican.ttf'), 86)

        self.titleText = pygame.Surface((448, 100)).convert_alpha()
        self.titleText.fill((0, 0, 0, 0))

        # blit the images twice to get the offsets correct
        self.titleText.blit(self.ft.render("MBITRON", True, (0, 0, 0)),
                            (113, 0))
        self.titleText.blit(self.ft.render("B", True, (0, 0, 0)),
                            (0, 0))

        self.active = True

    def toggleActive(self):
        if self.active:
            self.active = False
            self.bomb.explode()
            self.bomb.totalTime = 3
        else:
            self.active = True
            self.superPauseTimer = self.superPause
            self.pos = (-200, 80)
            self.explosion.reset()
            self.bomb.reset()

    def update(self, tick):
        if self.active:
            if self.superPauseTimer >= 0:
                self.superPauseTimer -= tick

            if self.pos[0] < self.finalPos[0] + 50:
                self.pos = (self.pos[0] + self.xSpeed, self.pos[1])

            self.bomb.update(tick)
        else:
            self.pos = (self.pos[0], self.pos[1] - self.ySpeed)
            self.bomb.update(tick)
            self.explosion.update(tick)

            if self.bomb.totalTime <= 0:
                self.explosion.explode()

    def draw(self):
        if self.superPauseTimer < 0:
            if self.active:
                self.win.blit(self.superImg,
                    (self.finalPos[0]-25, self.finalPos[1]-70))
            else:
                self.win.blit(self.superImg,
                    (self.finalPos[0]-25, self.pos[1]-70))

        self.win.blit(self.titleText, self.pos)

        if not self.explosion.explosion:
            self.bomb.draw()
        self.explosion.draw()

class Menu:
    def __init__(self, win):
        self.win = win
        self.menuft = pygame.font.Font(dataName('Blox2.ttf'), 50)
        self.selectedft = pygame.font.Font(dataName('Blox2.ttf'), 70)

        self.choice = 0
        self.choices = ['easy', 'intermediate', 'difficult']

        self.horizonPos = 0

        self.active = True
        self.finished = False
        self.setChoices()

    def imageCollide(self, pos):
        for count, (image, rect) in enumerate(self.imageChoices):
            if rect.collidepoint(pos):
                self.choice = count
                self.setChoices()

    def setChoices(self):
        self.imageChoices = []

        for count, item in enumerate(self.choices):
            if count == self.choice:
                text = self.selectedft.render(item.upper(), True, (0, 0, 0))
            else:
                text = self.menuft.render(item, True, (0, 0, 0))

            if count == 1:
                x = self.horizonPos + 320 - text.get_width() / 2
            else:
                x = 320 - self.horizonPos - text.get_width() / 2

            rect = text.get_rect()
            rect.topleft = (x, count * 80 + 200)

            self.imageChoices.append((text, rect))

    def update(self, tick):
        if not self.active:
            if self.horizonPos < 600:
                self.horizonPos += 20
        else:
            self.horizonPos = 0

    def draw(self):
        for count, (image, rect) in enumerate(self.imageChoices):
            if count == 1:
                self.win.blit(image, (rect.x - self.horizonPos, rect.y))
            else:
                self.win.blit(image, (rect.x + self.horizonPos, rect.y))

class TitleManager:
    def __init__(self, win):
        self.active = True

        self.titleBg = TitleBackground(win)
        self.title = Title(win)
        self.menu = Menu(win)

    def update(self, tick):
        self.titleBg.update(tick)
        self.title.update(tick)
        self.menu.update(tick)

        if self.title.explosion.exploded:
            self.active = False

    def draw(self):
        self.titleBg.draw()
        self.title.draw()
        self.menu.draw()

    def eventHandler(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.menu.active:
                self.menu.imageCollide(event.pos)
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.menu.active:
                currentChoice = self.menu.choice
                self.menu.choice = -1
                self.menu.imageCollide(event.pos)
                if self.menu.choice > -1:
                    self.titleBg.toggleActive()
                    self.title.toggleActive()
                    self.menu.active = not self.menu.active
                self.menu.choice = currentChoice
                self.menu.setChoices()

if __name__ == '__main__':
    pygame.init()

    win = pygame.display.set_mode((640, 480))

    clock = pygame.time.Clock()

    titleManager = TitleManager(win)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            titleManager.eventHandler(event)

        tick = clock.tick(30)

        titleManager.update(tick)

        win.fill((200, 200, 255))

        titleManager.draw()

        pygame.display.flip()


