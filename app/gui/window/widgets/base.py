import wx
from app.utils import execute_every


class StaticFlexibleChoice(wx.Choice):
    def __init__(self, parent, label='Sample_Label', property_to_display=None, pos=(1, 1), width=200, height=20):

        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.width = width
        self.height = height
        self.label = wx.StaticText(parent, label=label, pos=(self.pos_x, self.pos_y+5))
        self._property_to_display = property_to_display

        self.sampleList = self.choices_data
        super().__init__(parent, pos=(self.pos_x+width - 40, self.pos_y), size=(95, -1), choices=self.sampleList)
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

    def __init__(self, parent,
                 label='Sample_Label',
                 property_to_display=None,
                 pos=(1, 1), width=200, height=20, dc=None):

        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.width = width
        self.height = height
        self.parent = parent

        self.label = wx.StaticText(parent, label=label, pos=(pos[0], pos[1]+5))
        self._property_to_display = property_to_display

        self.sampleList = self.choices_data
        super().__init__(parent, pos=(pos[0]+70, pos[1]), size=(95, -1), choices=self.sampleList)
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

    def __init__(self, parent, label='Sample_Label', pos=(1, 1), width=395, height=40):
        print('pos is ', pos)
        self.label = wx.StaticText(parent, label=label, pos=(pos[0], pos[1]+5))

        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.width = width
        self.height = height
        self.parent = parent

        super().__init__(parent, value="Enter here your name",
                         pos=(pos[0]+70, pos[1]), size=(260, 25),
                         style=wx.TE_READONLY)

        self.file_dialog = wx.FileDialog(parent, "Open", "", "",
                                         "Binary files (*.bin)|*.bin|Hex files (*.hex)|*.hex",
                                         wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
                                         size=(480, 266))
        self.path_to_file = "Select a file"
        print(self.file_dialog.Size)
        self.Clear()

        self.write(self.path_to_file)

        self.button = wx.Button(parent, label="...", pos=(pos[0]+335, pos[1]-1), size=(40, 27))
        parent.Bind(wx.EVT_BUTTON, self.on_click, self.button)

    def on_click(self, event):
        self.file_dialog.ShowModal()
        self.Clear()
        self.path_to_file = self.file_dialog.GetPath()
        self.write(self.path_to_file)
        self.file_dialog.Close()


class SettingsCheckBox(wx.CheckBox):

    def __init__(self, parent, label='Sample_Label', pos=(1, 1), width=200, height=20, checked=False, dc=None):

        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.width = width
        self.height = height
        self.parent = parent

        super().__init__(parent, label=label, pos=pos)
        self.SetValue(checked)

    @property
    def flag(self):
        return self.IsChecked()