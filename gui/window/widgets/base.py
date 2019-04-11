import wx
from app.utils import execute_every


class StaticFlexibleChoice(wx.Choice):
    def __init__(self, parent, property_list, label='Sample_Label',
                 property_to_display=None, pos=(1, 1), width=200, height=20):

        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.width = width
        self.height = height
        self.label = wx.StaticText(parent, label=label, pos=(self.pos_x, self.pos_y+5))
        self._property = dict(zip(property_list, list(map(int, property_list))))

        super().__init__(parent, pos=(self.pos_x+width - 40, self.pos_y), size=(95, -1), choices=self.choices_data)
        self.SetSelection(4)
        # print('selecting ', self.choices_data[3])
        self._event_on_choice = wx.EVT_CHOICE

    @property
    def choices_data(self):
        if self._property is not None:
            data = list(self._property.keys())
        else:
            data = ['Sample data 1', 'Sample data 2']
        return data

    @property
    def event_on_choice(self):
        return self._event_on_choice


class DynamicFlexibleChoice(wx.Choice):

    def __init__(self, parent, property_list, property_to_display=None,
                 label='Sample_Label', pos=(1, 1), width=200, height=20, dc=None):

        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.width = width
        self.height = height
        self.parent = parent

        self.label = wx.StaticText(parent, label=label, pos=(pos[0], pos[1]+5))
        self._property_to_display = property_list
        # self.SetSelection(property_to_display)
        super().__init__(parent, pos=(pos[0]+70, pos[1]), size=(95, -1), choices=self.choices_data)

        if property_to_display is not None:
            self.SetStringSelection(property_to_display)
        self._event_on_choice = wx.EVT_CHOICE
        self.data_update()

    @property
    def choices_data(self):
        if callable(self._property_to_display):
            data = self._property_to_display()
            print(data)
        else:
            data = ['']
        return data

    @execute_every
    def data_update(self):
        if self.GetItems() != self.choices_data:
            self.Clear()
            self.Append(self.choices_data)

    @property
    def event_on_choice(self):
        return self._event_on_choice


class InputFile(wx.TextCtrl):

    def __init__(self, parent, label='Sample_Label', pos=(1, 1),
                 initial_path='', width=395, height=40, callback=None):
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
                                         "Binary files (*.bin)|*.bin|Hex files (*.hex)|*.hex|Any file (*.*)|*.*",
                                         wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
                                         size=(480, 266))
        self.caption = 'Select a file' if initial_path is '' else initial_path
        self.path_to_file = initial_path

        # print(self.file_dialog.Size)
        self.Clear()

        self.write(self.caption)

        self.button = wx.Button(parent, label="...", pos=(pos[0]+335, pos[1]-1), size=(40, 27))
        if callback is not None and callable(callback):
            parent.Bind(wx.EVT_BUTTON, callback, self.button)


class SettingsCheckBox(wx.CheckBox):

    def __init__(self, parent, label='Sample_Label', pos=(1, 1), width=200, height=20, checked=False):

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
