import eel
import retry
import random

@retry.retry(OSError)
def start():
    port = random.randint(80, 65535)
    return eel.start('index.html', port=port)

eel.init('scripts')
start()
