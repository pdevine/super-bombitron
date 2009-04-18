import pygame
import random

from random import randint
from bombs import dataName

BOMB_IMG = pygame.image.load(dataName('bigbomb2.png'))

class Spark:
    lifetimeRange = (100, 350)
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
    def __init__(self, win, totalTime=10, rot=0, pos=(170, 200), finalPos=(170, 200)):
        self.image = BOMB_IMG.copy()
        self.pos = pos
        self.finalPos = finalPos
        self.win = win

        self.totalTime = totalTime

        self.ft = pygame.font.SysFont('Arial', 40)

        self.startRot = rot
        self.rot = rot

        self.rect = BOMB_IMG.get_rect()
        self.rect.center = self.pos

        self.sparks = SparkManager(win, 
            (self.rect.x + self.image.get_width(), self.rect.y))

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
            timerText = self.ft.render("%d" % self.totalTime, True, color)
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

    def explode(self):
        self.explosion = True

    def update(self, tick):
        if self.explosion and self.fullTextTime > 0:
            self.fullTextTime -= tick
        elif self.explosion and self.fullTextTime <= 0:
            self.shortString = False
            self.clearImageTime -= tick

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

if __name__ == '__main__':
    import pygame
    pygame.init()

    win = pygame.display.set_mode((800, 600))

    clock = pygame.time.Clock()

    bomb = Bomb(win, pos=(570,200), finalPos=(130,200), rot=-81)
    explosion = Explosion(win, (100, 100))

    while True:
        tick = clock.tick()

        bomb.update(tick)
        explosion.update(tick)

        win.fill((255, 255, 255))

        bomb.draw()

        if bomb.totalTime <= 0:
            explosion.explode()

        explosion.draw()

        pygame.display.flip()

