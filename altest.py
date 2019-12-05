import os
import sys
import time
from openal.audio import SoundSink, SoundSource, SoundListener
from openal.loaders import load_wav_file
from math import sin, cos, pi

sink = SoundSink()
fname = 'sounds/beep.wav'
sink.activate()

listener = SoundListener()
sink.listener = listener
theta = 0
source = SoundSource(position=[5, 0, 5])
source.looping = True
#source.reference_distance = 1
#source.rolloff_factor     = 10000

data = load_wav_file(fname)
source.queue(data)

sink.play(source)
for i in range(4):
    source.position = [5*cos(theta),
                       5*sin(theta),
                       0]
    theta += pi/2
    sink.update()
    print("playing at %r" % source.position)
    time.sleep(2)
print("done")
