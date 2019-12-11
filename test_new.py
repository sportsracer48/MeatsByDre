#!/usr/bin/python3
import pygame as pg
import numpy as np
from pygame.locals import *
from gtts import gTTS
import subprocess
import os
import sys
from itertools import product
from math import atan2, pi, cos, sin
from openal.audio import SoundSink, SoundSource, SoundListener
from openal.loaders import load_wav_file

white = (255,255,255)
black = (0,0,0)

lines = ['GREEN LINE B','GREEN LINE C','GREEN LINE D','GREEN LINE E','RED LINE']
directions = ['OUTBOUND','INBOUND']
nLines = len(lines)
nDirections = len(directions)

tutorials = ['Swipe up or down to change direction. Swipe left or right to change destination.',
             'Tap and hold to repeat the following instructions. Swipe left and right to cycle through subway lines. Swipe up or down to select inbound or outbound. Tap twice to confirm which destination you have selected. Tap once to request a beep. Follow your ears in the direction of the beep.',
             'Tap and hold for instructions.']
instructions = 'Swipe left and right to cycle through subway lines. Swipe up or down to select inbound or outbound. Tap twice to confirm which destination you have selected. Tap once to request a beep. Follow your ears in the direction of the beep. Tap and hold to repeat these instructions.'
instructionFnames = ['tut0','tut1','inst']
if len(sys.argv) > 1:
    mode = int(sys.argv[1])
else:
    mode = 2
tutorial = tutorials[mode]

stop     = 'You have arrived!'
turn     = 'turn around'

#talking
soundProcess = None
try:
    devnull = subprocess.DEVNULL
except:
    devnull = open('/dev/null', 'w')

#beeping
sink = SoundSink()
sink.activate()
listener = SoundListener()
sink.listener = listener
source = SoundSource()
source.reference_distance = 100
source.rolloff_factor     = 1
beepData = load_wav_file(os.path.join('sounds','beep.wav'))
beepTime = 500*beepData.size/beepData.frequency
sink.play(source)

def beep(loc, angle, goal):
    source.position   = [goal[0],0,goal[1]]
    listener.position = [loc[0],0,loc[1]]
    listener.orientation = [-cos(angle),0,-sin(angle),0,1,0]
    source.queue(beepData)


def is_playing():
    if soundProcess is not None:
        return soundProcess.poll() is None
    else:
        return False

def stop_word():
    if is_playing():
        soundProcess.kill()

def speak_word(fname):
    stop_word()
    global soundProcess
    soundProcess = subprocess.Popen(["mpg123",os.path.join("sounds",fname)],
    stdout=devnull,
    stderr=devnull)

def save_sound(fname, string):
    path = os.path.join("sounds", fname)
    if not os.path.isfile(path):
        tts = gTTS(text=string,lang='en')
        tts.save(path)

def init_sounds():
    for line, dir in product(lines, directions):
        string = line+' '+dir
        save_sound(string, string)
    for i, string in enumerate(tutorials):
        save_sound('tut'+str(i), string)
    save_sound('stop', stop)
    save_sound('turn', turn)
    save_sound('inst', instructions)

def main():
    init_sounds()
    speak_word('tut'+str(mode))
    W, H = (640,480)
    pg.init()
    #set to true to close the window
    done = False

    #pg init
    screen = pg.display.set_mode((W,H))
    font = pg.font.SysFont('arial', 20)
    pg.event.set_grab(True)
    pg.mouse.set_visible(False)

    #destination selection
    line      = 0
    direction = 0

    #player status
    goal    = np.array([-895.0,700.0])
    loc     = np.array([500.0,500.0])
    angle   = 0
    speed   = 0.1
    angleSpeed = 0.005

    #limits and cutoffs
    distRange   = 100
    arrived     = False

    #timing and swiping
    startTimeout      = 500
    swipeTimeout      = 100
    swipe             = np.array([0,0])
    minSwipeLen       = 500
    doubleClickTimeout = 350
    holdTimeout        = 500
    clock         = pg.time.Clock()
    startTime     = pg.time.get_ticks()
    lastMove      = -10000
    lastClick     = -10000
    lastBeep      = -10000

    mouseHeld   = False
    instructing = False
    needToBeep  = False

    while not done:
        dt   = clock.tick()
        time = pg.time.get_ticks()-startTime

        #input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            elif event.type == pg.MOUSEMOTION:
                if time > startTimeout:
                    lastMove   = time
                    swipe     += event.rel
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    done = True
            elif event.type == pg.MOUSEBUTTONDOWN:
                mouseHeld = True
                if time-lastClick < doubleClickTimeout:
                    speak_word(lines[line]+' '+directions[direction])
                    needToBeep = False
                else:
                    lastClick = time
                    needToBeep= True
            elif event.type == pg.MOUSEBUTTONUP:
                mouseHeld = False

        #instructions
        if time-lastClick >= holdTimeout and mouseHeld and not instructing:
            instructing = True
            needToBeep  = False
            speak_word(instructionFnames[mode])
        if instructing and not mouseHeld:
            instructing = False
            stop_word()

        #motion
        walking = False
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] and not keys[pg.K_RIGHT]:
            angle += angleSpeed*dt
        if keys[pg.K_RIGHT] and not keys[pg.K_LEFT]:
            angle -= angleSpeed*dt
        if keys[pg.K_UP] and not keys[pg.K_DOWN]:
            loc   += np.array([cos(angle),sin(angle)])*speed*dt
            walking = True
        if keys[pg.K_DOWN] and not keys[pg.K_UP]:
            loc   -= np.array([cos(angle),sin(angle)])*speed*dt

        #swipes
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
                loc     = np.array([500.0,500.0])
                angle   = 0
                speak_word(lines[line]+' '+directions[direction])
            swipe = np.array([0,0])

        #beeps
        heading     = [cos(angle), sin(angle)]
        goalHeading = goal - loc
        dp = np.dot(heading,goalHeading)
        if not mouseHeld and time-lastClick >= doubleClickTimeout and needToBeep:
            if dp<0:
                speak_word('turn')
            if time-lastBeep > beepTime:
                beep(loc, angle, goal)
                lastBeep = time
            needToBeep = False
        sink.update()
        dist = np.linalg.norm(goal - loc)
        if dist<distRange:
            if not arrived:
                speak_word('stop')
                arrived = True
        else:
            arrived = False

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

        if walking:
            u = np.array((cos(angle),-sin(angle)))
            for dx in np.linspace(1,0,5):
                opacity = int((1-dx)*255)
                col = pg.Color(opacity,opacity,opacity)
                beginPt = np.array((W//2, H//2+4*h))-u*dx*15
                endPt   = beginPt + np.array((50*cos(angle), -50*sin(angle)))
                arrow1End = endPt + np.array((-15*cos(angle+pi/4), 15*sin(angle+pi/4)))
                arrow2End = endPt + np.array((-15*cos(angle-pi/4), 15*sin(angle-pi/4)))
                pg.draw.line(screen, col, beginPt, endPt, 2)
                pg.draw.line(screen, col, endPt, arrow1End, 2)
                pg.draw.line(screen, col, endPt, arrow2End, 2)
        else:
            beginPt = np.array((W//2, H//2+4*h))
            endPt   = beginPt + np.array((50*cos(angle), -50*sin(angle)))
            arrow1End = endPt + np.array((-15*cos(angle+pi/4), 15*sin(angle+pi/4)))
            arrow2End = endPt + np.array((-15*cos(angle-pi/4), 15*sin(angle-pi/4)))
            pg.draw.line(screen, white, beginPt, endPt, 2)
            pg.draw.line(screen, white, endPt, arrow1End, 2)
            pg.draw.line(screen, white, endPt, arrow2End, 2)
        pg.display.update()

if __name__ == '__main__':
    main()
    stop_word()
