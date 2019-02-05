# !/usr/bin/env python
import wx
from .window.main_frame import MainFrame


class GuiApplication:

    def __init__(self, *args, **kwargs):
        self._close_handler = kwargs['close_handler']
        print(self._close_handler)
        application = wx.App(False)
        frame = MainFrame(*args, **kwargs)
        application.MainLoop()
        self.close()
        frame.Destroy()

    def close(self):
        if callable(self._close_handler):
            self._close_handler()
        else:
            pass


if __name__ == '__main__':
    print('gui is summoned with name = __main__')
    app = GuiApplication()
