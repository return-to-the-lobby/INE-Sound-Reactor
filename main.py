import os
import sys
import wave
import math
import audioop

bit = 64 if sys.maxsize > 2 ** 32 else 32
pyinstaller = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

if not pyinstaller:
    import pkgutil, subprocess
    if not pkgutil.find_loader('pyaudio'):
        pop = subprocess.Popen(
            ['pip', 'install', 
            os.path.join(
                os.path.dirname(sys.argv[0]), 
                'Assets', 'Packages', 
                f'PyAudio-0.2.11-cp310-cp310-win{"32" if not bit == 64 else "_amd64"}.whl',
            )],
        )
        pop.wait()
        pop.terminate()
    del pkgutil, subprocess

import numpy
import pygame
import pyaudio

pygame.init()

audio = pyaudio.PyAudio()

def get_device_properties():
    file = wave.open('Assets/beep.wav', 'rb')
    return file.getnchannels(), file.getsampwidth(), file.getframerate()

image = None
properties = get_device_properties()
initial_decibels = []
median_decibel = 0

def stream_callback(input_data, frame_count, time_info, flag):
    global image, median_decibel
    del frame_count, time_info, flag
    images = os.listdir('Assets/Images')
    images.sort()
    images = [os.path.join(os.path.dirname(sys.argv[0]), 'Assets', 'Images', file) for file in images]
    images = [pygame.image.load(image) for image in images]

    default = None, pyaudio.paContinue

    root_mean_square = audioop.rms(input_data, properties[1])
    if root_mean_square < 1: 
        return default

    decibel = 20 * math.log10(root_mean_square)
    decibel = round(decibel)

    if len(initial_decibels) - 1 < 10:
        initial_decibels.append(decibel)
        return default
    elif median_decibel == 0:
        median_decibel = numpy.median(initial_decibels)
        return default
    
    if decibel <= 10:
        image = images[0]   
    elif decibel <= median_decibel and decibel < median_decibel + 1 and decibel > 10:
        image = images[1]
    elif decibel > median_decibel + 1 and decibel <= median_decibel * 1.5:
        image = images[1]
    elif decibel > median_decibel * 1.5 and decibel <= median_decibel * 2:
        image = images[3]
    elif decibel > median_decibel * 2 and decibel <= median_decibel * 3:
        image = images[4]
    elif decibel > median_decibel * 3 and decibel <= median_decibel * 4:
        image = images[5]
    elif decibel >  median_decibel * 4 and decibel <= median_decibel * 5:
        image = images[6]
    else:
        image = images[0]

    return default

stream = audio.open(
    channels=1,
    rate=properties[2],
    format=audio.get_format_from_width(properties[1]),
    stream_callback=stream_callback,
    input=True,
)
stream.start_stream()

while 1:
    if image is None:
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(1)

    screen = pygame.display.set_mode((500, 700))
    screen.fill('white')
    screen.blit(image, image.get_rect())
    pygame.display.flip()
