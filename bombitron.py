
import pygame

from title import TitleManager
from bombs import BombGridManager

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

def main():
    pygame.init()

    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    clock = pygame.time.Clock()

    title = TitleManager(win)
    bombGrid = BombGridManager(win, 9, 9)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if title.active:
                title.eventHandler(event)

        tick = clock.tick(30)

        if title.active:
            title.update(tick)
        else:
            bombGrid.update(tick)

        win.fill((200, 200, 255))

        if title.active:
            title.draw()
        else:
            bombGrid.draw()

        pygame.display.flip()



if __name__ == '__main__':
    main()

