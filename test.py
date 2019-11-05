import pygame
import numpy as np
from pygame.locals import *
from gtts import gTTS
import subprocess
import os
from itertools import product


white = (255,255,255)
black = (0,0,0)

lines = ['GREEN LINE B','GREEN LINE C','GREEN LINE E','RED LINE']
directions = ['OUTBOUND','INBOUND']
nLines = len(lines)
nDirections = len(directions)

def speak_word(word):
    subprocess.Popen(["mpg123",os.path.join("sounds",word)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def main():
    for line, dir in product(lines, directions):
        string = line+' '+dir
        path = os.path.join("sounds",string)
        if not os.path.isfile(path):
            tts = gTTS(text=string,lang='en')
            tts.save(os.path.join("sounds",string))
    W, H = (640,480)
    pygame.init()
    screen = pygame.display.set_mode((W,H))
    done = False

    #print(pygame.font.get_fonts())
    font = pygame.font.SysFont('arial', 20)

    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)

    swipeTimeout = 100
    lastMove     = pygame.time.get_ticks()
    swipe        = np.array([0,0])
    minSwipeLen  = 500

    line      = 0
    direction = 0

    while not done:
        #pygame.mouse.set_pos(W//2,H//2)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.MOUSEMOTION:
                lastMove   = pygame.time.get_ticks()
                swipe     += event.rel
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
            elif event.type == pygame.MOUSEBUTTONUP:
                speak_word(lines[line]+' '+directions[direction])

        time = pygame.time.get_ticks()
        if time-lastMove > swipeTimeout:
            sx, sy = swipe
            len = np.linalg.norm(swipe)
            if len > minSwipeLen:
                if abs(sx) > abs(sy):
                    line += np.sign(sx)
                    line %= nLines
                else:
                    direction += np.sign(sy)
                    direction %= nDirections
                speak_word(lines[line]+' '+directions[direction])
            swipe = np.array([0,0])


        screen.fill(black)

        lineStr      = lines[line]
        directionStr = directions[direction]
        text = font.render(lineStr, True, white)
        textRec = text.get_rect()
        h = textRec.height
        textRec.center = (W//2, H//2)
        screen.blit(text,textRec)

        text = font.render(directionStr, True, white)
        textRec = text.get_rect()
        textRec.center = (W//2, H//2+h)
        screen.blit(text,textRec)

        pygame.display.update()

if __name__ == '__main__':
    main()
