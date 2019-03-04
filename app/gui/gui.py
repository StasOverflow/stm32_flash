import wx
from .window.main_frame import MainFrame


class GuiApplication:

    def __init__(self, *args, **kwargs):
        self._close_handler = kwargs['close_handler']
        print(self._close_handler)
        self._action_is_on_going = False
        self.application = wx.App(False)
        self.frame = MainFrame(*args, **kwargs)

    def launch(self):
        self.application.MainLoop()
        self.close()
        self.frame.Destroy()

    def close(self):
        if callable(self._close_handler):
            self._close_handler()
        else:
            pass

    def input_data_get(self):
        return self.frame.input_data_get()

    @property
    def action_is_on_going(self):
        return self.frame.action_is_on_going

    @action_is_on_going.setter
    def action_is_on_going(self, value):
        self.frame.action_is_on_going = value


if __name__ == '__main__':
    app = GuiApplication()
