# !/usr/bin/env python
import wx
from .window.main_frame import MainFrame


class GuiApplication:

    def __init__(self, *args, **kwargs):
        self._close_handler = kwargs['close_handler']
        print(self._close_handler)
        self.application = wx.App(False)
        self.frame = MainFrame(*args, **kwargs)

    def launch(self):
        self.application.MainLoop()
        self.close()
        self.frame.Destroy()

    def close(self):
        if callable(self._close_handler):
            print('close handler summoning')
            self._close_handler()
        else:
            pass

    def input_data_get(self):
        return self.frame.input_data_get()


if __name__ == '__main__':
    print('gui is summoned with name = __main__')
    app = GuiApplication()
