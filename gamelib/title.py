import sys

import pygame
import random

import effects
import bombs
import levels

from bombs import dataName

TILE_IMG = pygame.image.load(dataName('tile.png'))
AWESOME_FONT = pygame.font.Font(dataName('badabb__.ttf'), 70)

TEXT_RECT_POS = (180, 270)
BACK_RECT_POS = (345, 290)
FORWARD_RECT_POS = (455, 290)
PLAY_RECT_POS = (320, 230)

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

        self.backArrow = pygame.image.load(dataName('back-arrow.png'))
        self.forwardArrow = pygame.image.load(dataName('forward-arrow.png'))

        self.backRedArrow = pygame.image.load(dataName('back-red-arrow.png'))
        self.forwardRedArrow = \
            pygame.image.load(dataName('forward-red-arrow.png'))

        self.backImage = self.backArrow
        self.forwardImage = self.forwardArrow

        self.backRect = self.backArrow.get_rect()
        self.forwardRect = self.forwardArrow.get_rect()

        self.currentLevel = 0

        self.reset()

    def reset(self):
        self.textSpeed = 0
        self.finished = False
        self.setText()

        self.backRect.topleft = BACK_RECT_POS
        self.forwardRect.topleft = FORWARD_RECT_POS


    def setText(self):
        self.text = AWESOME_FONT.render('Level', True, (0, 0, 0))
        self.textRect = self.text.get_rect()
        self.textRect.topleft = TEXT_RECT_POS

        self.levelText = AWESOME_FONT.render(
                            str(self.currentLevel + 1), True, (0, 0, 0))
        self.levelRect = self.levelText.get_rect()
        self.levelRect.center = (415, 305)

    def eventHandler(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for rect in [self.backRect, self.forwardRect]:
                if rect.collidepoint(event.pos):
                    rect.left -= 2
                    rect.bottom += 2

        elif event.type == pygame.MOUSEBUTTONUP:
            self.backRect.topleft = BACK_RECT_POS
            self.forwardRect.topleft = FORWARD_RECT_POS

            if self.backRect.collidepoint(event.pos):
                if self.currentLevel == 0:
                    self.currentLevel = len(levels.LEVELS) - 1
                else:
                    self.currentLevel -= 1

                self.setText()

            elif self.forwardRect.collidepoint(event.pos):
                if self.currentLevel == len(levels.LEVELS) - 1:
                    self.currentLevel = 0
                else:
                    self.currentLevel += 1

                self.setText()

        elif event.type == pygame.MOUSEMOTION:
            if self.backRect.collidepoint(event.pos):
                self.backImage = self.backRedArrow
            elif self.forwardRect.collidepoint(event.pos):
                self.forwardImage = self.forwardRedArrow
            else:
                self.backImage = self.backArrow
                self.forwardImage = self.forwardArrow

    def update(self, tick):
        if self.finished:
            self.textSpeed -= 2
            for rect in [self.textRect, self.backRect,
                         self.forwardRect, self.levelRect]:
                rect.right += self.textSpeed

    def draw(self):
        self.win.blit(self.text, self.textRect.topleft)
        self.win.blit(self.backImage, self.backRect.topleft)
        self.win.blit(self.forwardImage, self.forwardRect.topleft)
        self.win.blit(self.levelText, self.levelRect.topleft)

class Menu(object):
    def __init__(self, win):
        self.win = win
        self.currentLevel = 0

        self.active = True

        self.levelSelect = LevelSelect(self.win)
        self.reset()

    def reset(self):
        self.setText()
        self._finished = False
        self.levelSelect.reset()

    def getFinished(self):
        return self._finished

    def setFinished(self, *args):
        self._finished = True
        self.levelSelect.finished = True
        print "finished!"

    finished = property(getFinished, setFinished)

    def setText(self, active=False):
        if not active:
            self.text = AWESOME_FONT.render("Play!", True, (0, 0, 0))
        else:
            self.text = AWESOME_FONT.render("Play!", True, (255, 0, 0))

        self.textRect = self.text.get_rect()
        self.textRect.center = PLAY_RECT_POS
        self.textSpeed = 0

    def eventHandler(self, event):
        self.levelSelect.eventHandler(event)

        if self.finished:
            return

        if event.type == pygame.MOUSEMOTION:
            if self.textRect.collidepoint(event.pos):
                self.setText(active=True)
            else:
                self.setText()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.textRect.collidepoint(event.pos):
                self.textRect.left -= 2
                self.textRect.bottom += 2
        elif event.type == pygame.MOUSEBUTTONUP:
            self.textRect.center = PLAY_RECT_POS

    def update(self, tick):
        self.levelSelect.update(tick)

        if self._finished:
            self.textSpeed += 2
            self.textRect.right += self.textSpeed

    def draw(self):
        self.win.blit(self.text, self.textRect.topleft)
        self.levelSelect.draw()


class TitleManager:
    def __init__(self, win):
        self.active = True
        self.win = win
        self.currentLevel = 0

        self.reset()

    def reset(self):
        self.titleBg = TitleBackground(self.win)
        self.title = Title(self.win)
        if not hasattr(self, 'menu'):
            self.menu = Menu(self.win)
        else:
            self.menu.reset()
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
        if self.menu.active:
            self.menu.eventHandler(event)

        if event.type == pygame.MOUSEBUTTONUP:
            if self.menu.textRect.collidepoint(event.pos):
                self.currentLevel = self.menu.levelSelect.currentLevel
                self.titleBg.toggleActive()
                self.title.toggleActive()
                self.menu.finished = True
                #self.active = False

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


