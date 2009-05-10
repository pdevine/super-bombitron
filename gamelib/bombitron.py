import sys
import pygame
import levels

from title import TitleManager
from bombs import BombGridManager

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

def main():
    pygame.init()

    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    clock = pygame.time.Clock()

    title = TitleManager(win)
    bombGrid = None

    currentLevel = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if title.active:
                title.eventHandler(event)
            else:
                if bombGrid:
                    bombGrid.eventHandler(event)

        tick = clock.tick(30)

        if title.active:
            title.update(tick)
        else:
            if not bombGrid:
                difficulty = title.menu.choices[title.menu.choice]
                level = levels.LEVELS[difficulty][currentLevel]

                bombGrid = BombGridManager(win, level)
                
            bombGrid.update(tick)

        win.fill((200, 200, 255))

        if title.active:
            title.draw()
        else:
            if bombGrid:
                bombGrid.draw()

        pygame.display.flip()



if __name__ == '__main__':
    main()

