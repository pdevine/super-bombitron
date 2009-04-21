import sys

import pygame
import random

import effects
import bombs

from bombs import dataName

TILE_IMG = pygame.image.load(dataName('tile.png'))

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

class TitleBackground:
    def __init__(self, win):
        self.win = win

        self.tiles = [SpinTile(self.win)]

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
                self.tiles.append(SpinTile(self.win))
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
            if self.horizonPos < 500:
                self.horizonPos += 20
            else:
                self.finished = True
        else:
            self.horizonPos = 0

    def draw(self):
        for count, (image, rect) in enumerate(self.imageChoices):
            if count == 1:
                self.win.blit(image, (rect.x - self.horizonPos, rect.y))
            else:
                self.win.blit(image, (rect.x + self.horizonPos, rect.y))

if __name__ == '__main__':
    pygame.init()

    win = pygame.display.set_mode((640, 480))


    clock = pygame.time.Clock()

    titleBg = TitleBackground(win)
    title = Title(win)
    menu = Menu(win)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                if menu.active:
                    menu.imageCollide(event.pos)
                
            elif event.type == pygame.MOUSEBUTTONUP:
                if menu.active:
                    currentChoice = menu.choice
                    menu.choice = -1
                    menu.imageCollide(event.pos)
                    if menu.choice > -1:
                        titleBg.toggleActive()
                        title.toggleActive()
                        menu.active = not menu.active
                    menu.choice = currentChoice
                    menu.setChoices()

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    menu.choice += 1
                    menu.setChoices()
                elif event.key == pygame.K_UP:
                    menu.choice -= 1
                    menu.setChoices()
                else:
                    titleBg.toggleActive()
                    title.toggleActive()
                    menu.active = not menu.active

        tick = clock.tick(30)

        titleBg.update(tick)
        title.update(tick)
        menu.update(tick)

        win.fill((200, 200, 255))

        titleBg.draw()
        title.draw()
        menu.draw()

        pygame.display.flip()


