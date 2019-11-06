#! /usr/bin/python3
import pygame
import numpy as np
from pygame.locals import *
from gtts import gTTS
import subprocess
import os
from itertools import product
from math import atan2, pi, cos, sin


white = (255,255,255)
black = (0,0,0)

lines = ['GREEN LINE B','GREEN LINE C','GREEN LINE D','GREEN LINE E','RED LINE']
directions = ['OUTBOUND','INBOUND']
tutorial = 'Swipe up or down to change direction. Swipe left or right to change destination.'
stop     = 'You have arrived!'
nLines = len(lines)
nDirections = len(directions)

soundProcess = None

def speak_word(word):
    global soundProcess
    if soundProcess is not None:
        soundProcess.kill()
    soundProcess = subprocess.Popen(["mpg123",os.path.join("sounds",word)],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL)
def init_sounds():
    for line, dir in product(lines, directions):
        string = line+' '+dir
        path = os.path.join("sounds",string)
        if not os.path.isfile(path):
            tts = gTTS(text=string,lang='en')
            tts.save(path)
    path = os.path.join('sounds','tutorial')
    if not os.path.isfile(path):
        tts = gTTS(text = tutorial, lang='en')
        tts.save(path)
    path = os.path.join('sounds','stop')
    if not os.path.isfile(path):
        tts = gTTS(text = stop, lang='en')
        tts.save(path)

def main():
    init_sounds()
    speak_word('tutorial')
    W, H = (640,480)
    pygame.init()
    #set to true to close the window
    done = False

    #pygame init
    screen = pygame.display.set_mode((W,H))
    beep = pygame.mixer.Sound(os.path.join('sounds','beep.ogg'))
    font = pygame.font.SysFont('arial', 20)
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)

    #destination selection
    line      = 0
    direction = 0

    #player status
    goal    = np.random.random(size = 2)*1000
    loc     = np.array([500.0,500.0])
    angle   = 0
    speed   = 0.05
    angleSpeed = 0.0002

    #limits and cutoffs
    minBeepTime = 600
    angleRange  = pi/24
    distRange   = 100
    arrived = False
    minVolume = 0.05

    #timing and swiping
    startTimeout = 500
    swipeTimeout = 100
    swipe        = np.array([0,0])
    minSwipeLen  = 500
    lastMove     = pygame.time.get_ticks()
    startTime    = lastMove
    lastBeep     = lastMove


    #main loop
    while not done:
        #handel input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.MOUSEMOTION:
                if (pygame.time.get_ticks()-startTime) > startTimeout:
                    lastMove   = pygame.time.get_ticks()
                    swipe     += event.rel
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
            elif event.type == pygame.MOUSEBUTTONUP:
                speak_word(lines[line]+' '+directions[direction])
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            angle += angleSpeed
        if keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            angle -= angleSpeed
        if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
            loc   += np.array([cos(angle),sin(angle)])*speed
        if keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
            loc   -= np.array([cos(angle),sin(angle)])*speed

        #detect swipes
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
                goal    = np.random.random(size = 2)*1000
                speak_word(lines[line]+' '+directions[direction])
            swipe = np.array([0,0])

        #do radar
        goalHeading = goal - loc
        dist        = np.linalg.norm(goalHeading)
        #are we there yet?
        if dist<distRange:
            if not arrived:
                speak_word('stop')
            arrived = True
        #do beeps
        elif (pygame.time.get_ticks()-lastBeep) > dist+minBeepTime:
            arrived = False
            lastBeep    = pygame.time.get_ticks()
            goalAngle   = (atan2(goalHeading[1],goalHeading[0])-angle) % (2*pi)
            if goalAngle > pi:
                goalAngle -= 2*pi
            #print(angle, goalAngle, dist)
            if abs(goalAngle)<.1:
                channel = beep.play()
                channel.set_volume(1,1)
            elif goalAngle > 0:
                channel = beep.play()
                volume = max((pi-goalAngle)/pi, minVolume)
                channel.set_volume(volume,0)
            else:
                channel = beep.play()
                volume = max((pi+goalAngle)/pi, minVolume)
                channel.set_volume(0,volume)


        #render screen
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
