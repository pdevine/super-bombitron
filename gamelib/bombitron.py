import sys
import pygame

from title import TitleManager
from bombs import BombGridManager
from effects import Credits
import title

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

def main():
    pygame.init()

    pygame.display.set_caption('Super Bombitron')

    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    clock = pygame.time.Clock()

    menu = TitleManager(win)
    credits = Credits(win)
    bombGrid = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                if menu.active:
                    sys.exit()
                else:
                    menu.menu.startChoices = False
                    menu.active = True
                    menu.reset()

            if menu.active:
                menu.eventHandler(event)
            else:
                if bombGrid and not bombGrid.finished:
                    bombGrid.eventHandler(event)

        tick = clock.tick(30)

        if menu.active:
            menu.update(tick)
            if menu.resetBombs:
                bombGrid = None
                menu.resetBombs = False
        else:
            if not bombGrid:
                bombGrid = BombGridManager(win, menu.currentLevel)

            bombGrid.update(tick)

            if bombGrid.finished:
                credits.update(tick)
                if credits.finished:
                    menu.active = True
                    menu.reset()
                    bombGrid = None
                

        win.fill((200, 200, 255))

        if menu.active:
            menu.draw()
        else:
            if bombGrid and not bombGrid.finished:
                bombGrid.draw()
            elif bombGrid and bombGrid.finished:
                credits.draw()

        pygame.display.flip()



if __name__ == '__main__':
    main()

