
import pygame

from title import TitleManager
from bombs import BombGridManager

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

LEVELS = \
    (((9, 9, 10, 120, ''),
      (9, 9, 10, 90, ''),
      (9, 9, 10, 45, '')
     ),
     ((16, 16, 40, 300, ''),
     ),
     ((30, 16, 99, 500, ''),
     )
    )

LEVEL_ROWS = 0
LEVEL_COLS = 1
LEVEL_BOMBS = 2
LEVEL_TIME = 3

def main():
    pygame.init()

    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    clock = pygame.time.Clock()

    title = TitleManager(win)
    #bombGrid = BombGridManager(win, 9, 9)
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
                level = LEVELS[title.menu.choice][currentLevel]
                bombGrid = BombGridManager(win, level[LEVEL_ROWS],
                                                level[LEVEL_COLS],
                                                level[LEVEL_BOMBS],
                                                level[LEVEL_TIME])
                
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

