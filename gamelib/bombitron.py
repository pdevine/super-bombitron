import sys
import pygame

from title import TitleManager
from bombs import BombGridManager
from effects import Credits

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

def main():
    pygame.init()

    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    clock = pygame.time.Clock()

    title = TitleManager(win)
    credits = Credits(win)
    bombGrid = None

    currentLevel = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if title.active:
                title.eventHandler(event)
            else:
                if bombGrid and not bombGrid.finished:
                    bombGrid.eventHandler(event)

        tick = clock.tick(30)

        if title.active:
            title.update(tick)
        else:
            if not bombGrid:
                bombGrid = BombGridManager(win, currentLevel)
                
            bombGrid.update(tick)

            if bombGrid.finished:
                credits.update(tick)
                if credits.finished:
                    title.active = True
                    title.reset()
                    bombGrid = None
                

        win.fill((200, 200, 255))

        if title.active:
            title.draw()
        else:
            if bombGrid and not bombGrid.finished:
                bombGrid.draw()
            elif bombGrid and bombGrid.finished:
                credits.draw()

        pygame.display.flip()



if __name__ == '__main__':
    main()

