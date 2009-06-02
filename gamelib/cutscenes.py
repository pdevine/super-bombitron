import pygame

from effects import Bomb
from effects import Explosion

from util import dataName

class Title(object):
    def __init__(self, win, text):
        self.win = win
        awesomeFt = pygame.font.Font(dataName('badabb__.ttf'), 55)

        self.textFg = awesomeFt.render(text, True, (0, 255, 0))
        self.textBg = awesomeFt.render(text, True, (0, 0, 0))

        self.rect = self.textFg.get_rect()
        self.rect.center = (320, 80)

        self.textTime = 3

    def update(self, tick):
        self.textTime -= tick / 1000.0

    def draw(self):
        if self.textTime > 0:
            self.win.blit(self.textBg, (self.rect.topleft[0] + 5,
                                        self.rect.topleft[1] + 5))
            self.win.blit(self.textFg, self.rect.topleft)

class Cutscene(object):
    def __init__(self):
        self.active = True
        self.objects = []

    def update(self, tick):
        for obj in self.objects:
            obj.update(tick)

    def draw(self):
        for obj in self.objects:
            obj.draw()

class Cutscene1(Cutscene):
    def __init__(self, win):
        Cutscene.__init__(self)

        self.win = win

        self.text = Title(self.win, "The Meeting")

        self.bombs = [
            Bomb(self.win, 6, pos=(-10,230), finalPos=(73,230), rot=84),
            Bomb(self.win, -1, pos=(570,230), finalPos=(190,230), rot=-21,
                 showSparks=False, showCaution=True),
            Bomb(self.win, -1, pos=(626,230), finalPos=(246,230), rot=-21,
                 showSparks=False, showCaution=True),
            Bomb(self.win, -1, pos=(682,230), finalPos=(302,230), rot=-21,
                 showSparks=False, showCaution=True),
        ]

        self.explosions = [
            Explosion(self.win, (0,100)),
            Explosion(self.win, (50,200)),
            Explosion(self.win, (150,50)),
            Explosion(self.win, (200,120))
        ]

        self.totalTime = 4

    def update(self, tick):
        Cutscene.update(self, tick)

        self.text.update(tick)

        for bomb in self.bombs:
            bomb.update(tick)

        if self.bombs[0].totalTime < 0:
            self.totalTime -= tick / 1000.0

            for explosion in self.explosions:
                explosion.update(tick)

            self.explosions[0].explode()

            if self.totalTime < 3.0:
                self.explosions[1].explode()
            if self.totalTime < 2.0:
                self.explosions[2].explode()
            if self.totalTime < 1.0:
                self.explosions[3].explode()

            if self.explosions[3].exploded:
                self.active = False

    def draw(self):
        if self.bombs[0].totalTime >= 0:
            self.text.draw()
            for bomb in self.bombs:
                bomb.draw()
        else:
            for explosion in self.explosions:
                explosion.draw()

if __name__ == '__main__':
    import pygame
    pygame.init()

    win = pygame.display.set_mode((640, 480))

    clock = pygame.time.Clock()

    cs = Cutscene1(win)

    while True:
        tick = clock.tick(30)

        cs.update(tick)
        win.fill((200, 200, 255))

        cs.draw()

        pygame.display.flip()


