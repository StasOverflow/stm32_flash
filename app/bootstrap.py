import time
from .gui.gui import MainWindow


def launch():
    print("henlo, da taim is ", time.time())
    frame = MainWindow(None, 'Small editor')
