import sys

import pygame
import random

import effects
import bombs
import levels

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

START_CHOICES = ['Play!', 'Level']
RESUME_CHOICES = ['Resume', 'Level', 'New Game!']

class LevelSelect:
    def __init__(self, win):
        self.win = win
        self.awesomeft = pygame.font.Font(dataName('badabb__.ttf'), 70)
        self.backArrow = pygame.image.load(dataName('back-arrow.png'))
        self.forwardArrow = pygame.image.load(dataName('forward-arrow.png'))

        self.currentLevel = 0

        self.setText()

    def setText(self):
        self.text = self.awesomeft.render('Level', True, (0, 0, 0))
        self.levelText = self.awesomeft.render(
                            str(self.currentLevel + 1), True, (0, 0, 0))

    def draw(self):
        self.win.blit(self.text, (200, 200))
        self.win.blit(self.backArrow, (350, 215))
        self.win.blit(self.forwardArrow, (450, 215))
        self.win.blit(self.levelText, (405, 200))
        pass

class Menu:
    def __init__(self, win):
        self.win = win
        self.awesomeft = pygame.font.Font(dataName('badabb__.ttf'), 70)
        self.currentLevel = 0

        self.active = True
        self.finished = False

        self.levelSelect = LevelSelect(self.win)

    def update(self, tick):
        pass

    def draw(self):
        self.levelSelect.draw()
        pass


class TitleManager:
    def __init__(self, win):
        self.active = True
        self.win = win

        self.reset()

    def reset(self):
        self.titleBg = TitleBackground(self.win)
        self.title = Title(self.win)
        if not hasattr(self, 'menu'):
            self.menu = Menu(self.win)
        print "reset"

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
            pass
#            if self.menu.active:
#                print "collide"
#                self.menu.imageCollide(event.pos)
                
        elif event.type == pygame.MOUSEBUTTONUP:
            pass
#            if self.menu.active:
#                currentChoice = self.menu.choice
#                self.menu.choice = -1
#                self.menu.imageCollide(event.pos)
#                if self.menu.choice == 0:
#                    self.titleBg.toggleActive()
#                    self.title.toggleActive()
#                    self.menu.active = not self.menu.active
#                elif self.menu.choice == 1:
#                    if event.button == 1:
#                        self.menu.currentLevel += 1
#                        if self.menu.currentLevel >= len(levels.LEVELS):
#                            self.menu.currentLevel = 0
#                    elif event.button == 3:
#                        self.menu.currentLevel -= 1
#                        if self.menu.currentLevel < 0:
#                            self.menu.currentLevel = len(levels.LEVELS) - 1
#                self.menu.choice = currentChoice
#                self.menu.setChoices()

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


