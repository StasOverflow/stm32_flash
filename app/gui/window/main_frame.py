import wx
from .widgets.widgets import Panel


class MainFrame(wx.Frame):

    def __init__(self, *args, **kwargs):
        kwargs['size'] = (440, 500)
        kwargs['pos'] = (0, 0)
        # self._size = kwargs['size']

        wx.Frame.__init__(self, None,
                          style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER,
                          size=kwargs['size'], pos=kwargs['pos'])
        panel = Panel(self, **kwargs)
        # frame.Bind(wx.EVT_CLOSE, OnClose)
        # print('binded', self)
        self.Show()
