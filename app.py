import os
import sys
import eel
import retry
import random

pyinstaller = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

@retry.retry(OSError)
def start():
    port = random.randint(80, 65535)
    return eel.start('index.html', port=port)

eel.init(os.path.join(sys._MEIPASS, 'scripts') if pyinstaller else 'scripts')
start()
