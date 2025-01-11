# Change the game so that when the worm reaches the edge, instead of ending the game,
#   the worm should continue moving with appearing from the opposite side, still having the same direction.
# Include a yellow apple in the game that will appear only for a limited amount of time.
#   It is aimed to be eaten by the worm and to decrease its length by 1.
#   Make sure that this doesn't affect the score (number of red apples that the worm has eaten).
# Firstly decrease the speed of the game. Then every 30 seconds increase the speed of the game.
# Add a blue apple that will appear only for a limited amount of time.
#   It is aimed to be eaten by the worm and to decrease the speed of the game to the previous speed value.
# 20 seconds after starting the game add a second worm. The original worm should avoid the second one.
#   If the original worm touches the second worm with the head, its body grows for one segments.
#   If the second worm touches the original, than its body grows for one segment.
#   The movement of the second worm is random.
# Add 2 elements that blink (3 each time) at randomly selected positions with dimensions of 1 cell.
#   The first one appears every 5 seconds, and it lasts 5 seconds.
#   The second one appears only once, lasting 7 seconds.
#   If the original worm eats any of these elements, the player gets additional points (3 for each eaten element).
#   These points should be included in the end result in a way that you will choose.
#   You need to provide an explanation for the formula that you will use for calculating the result.
#   The result should be shown on the screen after the game ends.
# Add two buttons "Start from the beginning" and "Quit" to the game over screen.
#   When the user clicks the first button, the game should start over (without showing the starting screen).
#   When the player clicks the second button, the game should terminate.

import random
import pygame
import sys
from pygame.locals import (
    QUIT,
    KEYDOWN,
    KEYUP,
    K_ESCAPE,
    K_LEFT,
    K_RIGHT,
    K_UP,
    K_DOWN,
    K_a,
    K_s,
    K_d,
    K_w,
)

FPS = 15
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 155, 0)
DARKGRAY = (40, 40, 40)
BGCOLOR = BLACK

UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"

HEAD = 0  # syntactic sugar: index of the worm's head


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font("freesansbold.ttf", 18)
    pygame.display.set_caption("Wormy")

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def runGame():
    # Set a random start point.
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [
        {"x": startx, "y": starty},
        {"x": startx - 1, "y": starty},
        {"x": startx - 2, "y": starty},
    ]
    direction = RIGHT

    # Start the apple in a random place.
    apple = getRandomLocation()

    while True:  # main game loop
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()

        # check if the worm has hit itself or the edge
        if (
            wormCoords[HEAD]["x"] == -1
            or wormCoords[HEAD]["x"] == CELLWIDTH
            or wormCoords[HEAD]["y"] == -1
            or wormCoords[HEAD]["y"] == CELLHEIGHT
        ):
            return  # game over
        for wormBody in wormCoords[1:]:
            if (
                wormBody["x"] == wormCoords[HEAD]["x"]
                and wormBody["y"] == wormCoords[HEAD]["y"]
            ):
                return  # game over

        # check if worm has eaten an apply
        if wormCoords[HEAD]["x"] == apple["x"] and wormCoords[HEAD]["y"] == apple["y"]:
            # don't remove worm's tail segment
            apple = getRandomLocation()  # set a new apple somewhere
        else:
            del wormCoords[-1]  # remove worm's tail segment

        # move the worm by adding a segment in the direction it is moving
        if direction == UP:
            newHead = {"x": wormCoords[HEAD]["x"], "y": wormCoords[HEAD]["y"] - 1}
        elif direction == DOWN:
            newHead = {"x": wormCoords[HEAD]["x"], "y": wormCoords[HEAD]["y"] + 1}
        elif direction == LEFT:
            newHead = {"x": wormCoords[HEAD]["x"] - 1, "y": wormCoords[HEAD]["y"]}
        elif direction == RIGHT:
            newHead = {"x": wormCoords[HEAD]["x"] + 1, "y": wormCoords[HEAD]["y"]}
        wormCoords.insert(0, newHead)
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords)
        drawApple(apple)
        drawScore(len(wormCoords) - 3)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render("Press a key to play.", True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font("freesansbold.ttf", 100)
    titleSurf1 = titleFont.render("Wormy!", True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render("Wormy!", True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3  # rotate by 3 degrees each frame
        degrees2 += 7  # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {
        "x": random.randint(0, CELLWIDTH - 1),
        "y": random.randint(0, CELLHEIGHT - 1),
    }


def showGameOverScreen():
    gameOverFont = pygame.font.Font("freesansbold.ttf", 150)
    gameSurf = gameOverFont.render("Game", True, WHITE)
    overSurf = gameOverFont.render("Over", True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress()  # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            return


def drawScore(score):
    scoreSurf = BASICFONT.render("Score: %s" % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawWorm(wormCoords):
    for coord in wormCoords:
        x = coord["x"] * CELLSIZE
        y = coord["y"] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)


def drawApple(coord):
    x = coord["x"] * CELLSIZE
    y = coord["y"] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE):  # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE):  # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == "__main__":
    main()
