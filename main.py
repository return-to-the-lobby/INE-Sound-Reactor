import os
import sys
import wave
import audioop
from math import log10
from contextlib import redirect_stdout

bit = 64 if sys.maxsize > 4294967296 else 32
image = None
pyinstaller = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

if not pyinstaller:
    import pkgutil
    modules = [module.name for module in pkgutil.iter_modules()]
    if 'pyaudio' not in modules:
        try: from pip import main
        except ImportError: from pip._internal import main
        directory = os.path.join(os.path.dirname(sys.argv[0]), 'Assets', 'Packages')
        if bit == 32:
            main(['install', os.path.join(directory, 'PyAudio-0.2.11-cp310-cp310-win32.whl')])
        else:
            main(['install', os.path.join(directory, 'PyAudio-0.2.11-cp310-cp310-win_amd64.whl')])
        del main
    del pkgutil

import pyaudio
from numpy import median

with redirect_stdout(None):
    import pygame

pygame.init()

audio = pyaudio.PyAudio()
datas = None

def wave_get_properties():
    with wave.open('Assets/beep.wav', 'rb') as file:
        channels = file.getnchannels()
        sample_width = file.getsampwidth()
        frame_rate = file.getframerate()  
    file.close()
    return channels, sample_width, frame_rate

properties = wave_get_properties()
decibels = []
summary_decibel = 0

def pyaudio_stream_callback(input_data, frame_count, time_info, flag):
    images = os.listdir('Assets/Images')
    images.sort()
    images = [os.path.join(os.path.dirname(sys.argv[0]), 'Assets', 'Images', file) for file in images]
    images = [pygame.image.load(image) for image in images]
    print(frame_count, time_info, flag)
    global summary_decibel
    root_mean_square = audioop.rms(input_data, properties[1])
    decibel = 20 * log10(root_mean_square)
    decibel = round(decibel)
    if len(decibels) - 1 < 10:
        decibels.append(decibel)
        return None, pyaudio.paContinue
    elif summary_decibel == 0:
        summary_decibel = median(decibels)
        return None, pyaudio.paContinue
    
    global image
    if decibel <= 10:
        image = images[0]
    elif decibel <= summary_decibel and decibel < summary_decibel + 1 and decibel > 10:
        image = images[1]
    elif decibel > summary_decibel + 1 and decibel <= summary_decibel * 1.5:
        image = images[1]
    elif decibel > summary_decibel * 1.5 and decibel <= summary_decibel * 2:
        image = images[3]
    elif decibel > summary_decibel * 2 and decibel <= summary_decibel * 3:
        image = images[4]
    elif decibel > summary_decibel * 3 and decibel <= summary_decibel * 4:
        image = images[5]
    elif decibel >  summary_decibel * 4 and decibel <= summary_decibel * 5:
        image = images[6]
    else:
        image = images[0]

    print(decibel, summary_decibel)

    return None, pyaudio.paContinue

def pyaudio_stream_open():
    stream = audio.open(
        channels=1,
        rate=properties[2],
        format=audio.get_format_from_width(properties[1]),
        stream_callback=pyaudio_stream_callback,
        input=True,
    )

    stream.start_stream()

pyaudio_stream_open()

pygame.display.set_mode((480, 854))

while 1:
    pygame.display.update([image])
    
    for event in pygame.event.get():
        if event == pygame.QUIT:
            break

pygame.quit()
