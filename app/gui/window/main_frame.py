import wx
from .widgets.panel_widgets import Panel


class MainFrame(wx.Frame):

    def __init__(self, *args, **kwargs):
        kwargs['size'] = (425, 260)
        kwargs['pos'] = (0, 0)
        # self._size = kwargs['size']

        style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER
        style = style ^ wx.MAXIMIZE_BOX
        wx.Frame.__init__(self, None, title="STM32 flasher",
                          style=style,
                          size=kwargs['size'], pos=kwargs['pos'])
        # icon = wx.Icon()
        # icon.CopyFromBitmap(wx.Bitmap("st.png", wx.BITMAP_TYPE_ANY))
        # self.SetIcon(icon)

        self.Center()
        self.panel = Panel(self, **kwargs)
        # frame.Bind(wx.EVT_CLOSE, OnClose)
        # print('binded', self)
        self.Show()
        self.storage = 0

    def input_data_get(self):
        return self.panel.interface_values_get()

    @property
    def action_is_on_going(self):
        return self.panel.action_is_on_going

    @action_is_on_going.setter
    def action_is_on_going(self, value):
        self.panel.action_is_on_going = value


