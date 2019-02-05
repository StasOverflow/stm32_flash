import wx
from app.utils import execute_every


class StaticFlexibleChoice(wx.Choice):
    def __init__(self, parent, label='Sample_Label', property_to_display=None, pos=(1, 1), width=200, height=20):
        self.label = wx.StaticText(parent, label=label, pos=(pos[0], pos[1]+5))
        self._property_to_display = property_to_display

        self.sampleList = self.choices_data
        super().__init__(parent, pos=(pos[0]+width - 40, pos[1]), size=(95, -1), choices=self.sampleList)
        self._event_on_choice = wx.EVT_CHOICE

    @property
    def choices_data(self):
        if callable(self._property_to_display):
            data = self._property_to_display()
        else:
            data = ['Sample data 1', 'Sample data 2']
        return data

    @property
    def event_on_choice(self):
        return self._event_on_choice


class DynamicFlexibleChoice(wx.Choice):

    def __init__(self, parent, label='Sample_Label', property_to_display=None, pos=(1, 1), width=200, height=20):
        self.label = wx.StaticText(parent, label=label, pos=(pos[0], pos[1]+5))
        self._property_to_display = property_to_display

        self.sampleList = self.choices_data
        super().__init__(parent, pos=(pos[0]+width - 40, pos[1]), size=(95, -1), choices=self.sampleList)
        self._event_on_choice = wx.EVT_CHOICE
        self.data_update()

    @property
    def choices_data(self):
        if callable(self._property_to_display):
            data = self._property_to_display()
        else:
            data = ['Sample data 1', 'Sample data 2']
        return data

    @execute_every(500)
    def data_update(self):
        if self.Items != self.choices_data:
            self.Clear()
            self.Append(self.choices_data)

    @property
    def event_on_choice(self):
        return self._event_on_choice


class InputFile(wx.TextCtrl):

    def __init__(self, parent, label='Sample_Label', pos=(1, 1), width=200, height=20):
        self.label = wx.StaticText(parent, label=label, pos=(pos[0], pos[1]+5))

        super().__init__(parent, value="Enter here your name", pos=(80, 120), size=(140, -1))

        # class grbg(wx.FileDialog):
        # def __init__(self, parent):
        #     super().__init__(parent, "Open", "", "",
        #                      "Python files (*.py)|*.py",
        #                      wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        #
        # def summon(self):
        #     self.ShowModal()
        #     print(self.GetPath())
        #     self.Destroy()
