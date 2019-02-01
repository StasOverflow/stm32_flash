# !/usr/bin/env python
import wx
from .utils import execute_every

import random


class MainWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)
        the_panel = wx.Panel(self)
        self.quote = wx.StaticText(the_panel, label="Your quote: ", pos=(20, 30))
        self.Show()


@execute_every
def randm_f():
    print("random_function")


class DynamicChoice(wx.Choice):
    def __init__(self, parent, label='Choose a COM port', dynamic_property=None):
        self._dynamic_property = dynamic_property

        # TODO: rework the below
        self.label = wx.StaticText(parent, label=label, pos=(20, 90))

        self.sampleList = ['friends', 'advertising', 'web search', 'Yellow Pagekkkkks']
        super().__init__(parent, pos=(150, 90), size=(95, -1), choices=self.sampleList)
        self._event_on_choice = wx.EVT_CHOICE

        self.data_update()

    @execute_every
    def data_update(self):
        if self.Items != self.choices_data:
            self.Clear()
            self.Append(self.choices_data)

    @property
    def choices_data(self):
        if callable(self._dynamic_property):
            data = self._dynamic_property()
        else:
            data = (None, )
        return data

    @property
    def event_on_choice(self):
        return self._event_on_choice


class Panel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent)
        self.quote = wx.StaticText(self, label="Your quote :", pos=(20, 30))

        """
            A multiline TextCtrl - This is here to show 
            how the events work in this program, don't pay 
            too much attention to it
        """
        self.logger = wx.TextCtrl(self, pos=(300, 20), size=(200, 300), style=wx.TE_MULTILINE | wx.TE_READONLY)

        # A button
        self.button = wx.Button(self, label="Save", pos=(200, 325))
        self.Bind(wx.EVT_BUTTON, self.on_click, self.button)

        # the edit control - one line version.
        self.lblname = wx.StaticText(self, label="Your name :", pos=(20, 60))
        self.editname = wx.TextCtrl(self, value="Enter here your name", pos=(150, 60), size=(140, -1))
        self.Bind(wx.EVT_TEXT, self.evt_text, self.editname)
        self.Bind(wx.EVT_CHAR, self.evt_char, self.editname)

        # ChoiceBox
        prop = args[0]
        self.port_box = DynamicChoice(self, dynamic_property=prop)
        self.Bind(self.port_box.event_on_choice, self.evt_combo_box, self.port_box)

        # Checkbox
        self.insure = wx.CheckBox(self, label="Do you want Insured Shipment ?", pos=(20, 180))
        self.Bind(wx.EVT_CHECKBOX, self.evt_check_box, self.insure)

        # Radio Boxes
        radio_list = ['blue', 'red', 'yellow', 'orange', 'green', 'purple', 'navy blue', 'black', 'gray']
        rb = wx.RadioBox(self, label="What color would you like ?",
                         pos=(20, 210), choices=radio_list,
                         majorDimension=3,
                         style=wx.RA_SPECIFY_COLS)
        self.Bind(wx.EVT_RADIOBOX, self.evt_radio_box, rb)

    def evt_radio_box(self, event):
        self.logger.AppendText('EvtRadioBox: %d\n' % event.GetInt())

    def evt_combo_box(self, event):
        self.logger.AppendText('EvtComboBox: %s\n' % event.GetString())

    def on_click(self, event):
        self.logger.AppendText(" Click on object with Id %d\n" % event.GetId())

    def evt_text(self, event):
        self.logger.AppendText('EvtText: %s\n' % event.GetString())

    def evt_char(self, event):
        self.logger.AppendText('EvtChar: %d\n' % event.GetKeyCode())
        event.Skip()

    def evt_check_box(self, event):
        self.logger.AppendText('EvtCheckBox: %d\n' % event.IsChecked())


class GuiApplication:

    def __init__(self, *args):
        application = wx.App(False)
        frame = wx.Frame(None)
        panel = Panel(frame, *args)
        frame.Show()
        application.MainLoop()


if __name__ == '__main__':
    print('gui is summoned with name = __main__')
    app = GuiApplication()
