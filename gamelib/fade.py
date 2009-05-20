
import pygame

class Tile:
    def __init__(self, win):
        self.win = win
        self.tilestrip = pygame.image.load('../data/tile-fade.png')

        self.fadeTime = 100
        self.count = 0

        self.surfaces = []

        self.x = 100
        self.y = 100

        self.dir = 1

        for count in range(5):
            rect = pygame.Rect(count * 20, 0, 20, 20)
            self.surfaces.append(self.tilestrip.subsurface(rect))

    def update(self, tick):
        self.fadeTime -= tick
        if self.fadeTime <= 0:
            self.fadeTime = 100
            self.count += self.dir
            if self.count >= len(self.surfaces):
                self.dir = -1
                self.count -= 2
            elif self.count <= 0:
                self.dir = 1
                self.count = 0

    def draw(self):
        self.win.blit(self.surfaces[self.count], (self.x, self.y))
def main():

    clock = pygame.time.Clock()

    win = pygame.display.set_mode((640, 480))

    tile = Tile(win)

    while True:
        tick = clock.tick(30)

        tile.update(tick)

        win.fill((200, 200, 255))

        tile.draw()

        pygame.display.flip()


if __name__ == '__main__':
    main()


