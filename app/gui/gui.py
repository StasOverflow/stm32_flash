# !/usr/bin/env python
import wx
from .base.base import DynamicFlexibleChoice, StaticFlexibleChoice, InputFile


class MainFrame(wx.Frame):

    def __init__(self, *args, **kwargs):

        kwargs.setdefault('size', (440, 500))
        self._size = kwargs['size']
        for key, value in kwargs.items():
            print("The value of {} is {}".format(key, value))

        wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER, **kwargs)
        panel = Panel(self, *args, **kwargs)
        # frame.Bind(wx.EVT_CLOSE, OnClose)
        # print('binded', self)
        self.Show()


class FileSequence(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.quote = wx.StaticText(self, label="OTHER PANELIO INDICATOR :", pos=(500, 500))
    #     super().__init__(self, parent)
        # super().__init__(parent, "Open", "", "",
        #                          "Python files (*.py)|*.py",
        #                          wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

    # def summon(self):
    #     self.ShowModal()
    #     print(self.GetPath())
    #     self.Destroy()


class Panel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, size=size)

        self.quote = wx.StaticText(self, label="OTHER PANELIO INDICATOR :", pos=(500, 500))
        """
            A multiline TextCtrl - This is here to show 
            how the events work in this program, don't pay 
            too much attention to it
        """
        # self.logger = wx.TextCtrl(self, pos=(300, 20), size=(200, 300), style=wx.TE_MULTILINE | wx.TE_READONLY)

        # A button
        self.button = wx.Button(self, label="Save", pos=(200, 325))
        self.Bind(wx.EVT_BUTTON, self.on_click, self.button)

        # # the edit control - one line version.
        # self.lblname = wx.StaticText(self, label="Your name :", pos=(20, 60))
        # self.editname = wx.TextCtrl(self, value="Enter here your name", pos=(150, 60), size=(140, -1))
        # self.Bind(wx.EVT_TEXT, self.evt_text, self.editname)
        # self.Bind(wx.EVT_CHAR, self.evt_char, self.editname)

        # Choice 1
        # for key, value in kwargs.items():
        #     print("The value of {} is {}".format(key, value))
        kwargs.setdefault('ports_property', [None, None])
        ports_property = kwargs['ports_property']
        print('ports property is', ports_property)
        self.port_box = DynamicFlexibleChoice(self, label='Device port',
                                              property_to_display=ports_property,
                                              pos=(20, 20), width=110)
        self.Bind(self.port_box.event_on_choice, self.evt_combo_box, self.port_box)

        # Choice 2
        kwargs.setdefault('baud_property', [None, None])
        baud_property = kwargs['baud_property']
        self.baud_box = StaticFlexibleChoice(self, label='Baudrate',
                                             property_to_display=baud_property,
                                             pos=(240, 20), width=100)
        self.Bind(self.port_box.event_on_choice, self.evt_combo_box, self.baud_box)

        # File Input
        self.file_input_box = InputFile(self)


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
        parent.Bind(wx.EVT_CLOSE, self.on_close)

        # Dialogio
        self._file_dialog = FileSequence(self)

    def evt_radio_box(self, event):
        pass
        self.logger.AppendText('EvtRadioBox: %d\n' % event.GetInt())

    def evt_combo_box(self, event):
        pass
        self.logger.AppendText('EvtComboBox: %s\n' % event.GetString())

    def on_click(self, event):
        pass
        self._file_dialog.summon()
        self.logger.AppendText(" Click on object with Id %d\n" % event.GetId())

    def evt_text(self, event):
        pass
        self.logger.AppendText('EvtText: %s\n' % event.GetString())

    def evt_char(self, event):
        pass
        self.logger.AppendText('EvtChar: %d\n' % event.GetKeyCode())
        event.Skip()

    def evt_check_box(self, event):
        pass
        self.logger.AppendText('EvtCheckBox: %d\n' % event.IsChecked())

    def on_close(self, event):
        print("in on close ")
        if event.CanVeto():

            if wx.MessageBox("The file has not been saved... continue closing?",
                             "Please confirm",
                             wx.ICON_QUESTION | wx.YES_NO) != wx.YES:

                event.Veto()
                return

        event.Skip()

        # Add a handler, that informs the main program about closing


# def OnClose(frame, event):
#     print("im not even here")
#     dlg = wx.MessageDialog(frame,
#         "Do you really want to close this application?",
#         "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
#     result = dlg.ShowModal()
#     dlg.Destroy()
#     if result == wx.ID_OK:
#         frame.Destroy()

class GuiApplication:

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('close_handler', None)
        self._close_handler = kwargs['close_handler']
        application = wx.App(False)
        for key, value in kwargs.items():
            print("The value of {} is {}".format(key, value))
        frame = MainFrame(*args, **kwargs)
        application.MainLoop()
        print('closing')
        self.close()

    def close(self):
        if callable(self._close_handler):
            self._close_handler()
        else:
            pass


if __name__ == '__main__':
    print('gui is summoned with name = __main__')
    app = GuiApplication()
