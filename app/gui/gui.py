# !/usr/bin/env python
import wx


class MainWindow(wx.Frame):
    """ We simply derive a new class of Frame. """

    def __init__(self, parent, title='stm32 loader'):
        app = wx.App(False)
        self.style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER
        super().__init__(self, parent, title=title, size=(480, 520), style=self.style)

        self.images = ['tolstoy.jpg', 'feuchtwanger.jpg', 'balzac.jpg', 'pasternak.jpg', 'galsworthy.jpg', 'wolfe.jpg', 'zweig.jpg']
        authors = ['Leo Tolstoy', 'Lion Feuchtwanger', 'Honore de Balzac', 'Boris Pasternak', 'John Galsworthy', 'Tom Wolfe', 'Stefan Zweig' ]

        wx.ComboBox(self, -1, pos=(50, 170), size=(150, 10), choices=authors, style=wx.CB_READONLY)
        app.MainLoop()

