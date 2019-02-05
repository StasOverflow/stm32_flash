import wx
from app.gui.window.widgets.base import DynamicFlexibleChoice, StaticFlexibleChoice, InputFile, SettingsCheckBox


class Panel(wx.Panel):
    def __init__(self, parent, **kwargs):
        self._size = kwargs['size']
        self._read_action_handler = kwargs['read_handler']
        self._write_action_handler = kwargs['write handler']
        wx.Panel.__init__(self, parent, size=self._size)

        self.interface_values = kwargs['vals']

        # self.storage += 1
        # if self.storage == 10:
        #     self._mah_dict['gjegorz'] = 'vasiliy'

        # Choice 1
        kwargs.setdefault('ports_getter', [None, None])
        ports_property = kwargs['ports_getter']
        print('ports property is', ports_property)
        self.dyn_flex_dc = None
        self.port_box = DynamicFlexibleChoice(self, label='Device port',
                                              property_to_display=ports_property,
                                              pos=(20, 20), width=110, dc=self.dyn_flex_dc)
        self.Bind(self.port_box.event_on_choice, self.evt_combo_box, self.port_box)

        # Choice 2
        # kwargs.setdefault('baud_list', [None, None])
        baud_property = kwargs['baud_list']
        # print(baud_property)
        self.baud_box = StaticFlexibleChoice(self, label='Baudrate',
                                             property_to_display=baud_property,
                                             pos=(240, 20), width=100)
        self.Bind(self.port_box.event_on_choice, self.evt_combo_box, self.baud_box)

        # File Input
        self._file_path = InputFile(self, label='File path:', pos=(20, 60))

        # Settings sequence
        self.settings_label = wx.StaticText(self, label="Settings:", pos=(20, 100))
        self.settings_dc = None
        self.erasing = SettingsCheckBox(self, label='Erase', pos=(20, 125), checked=True)

        self.verify = SettingsCheckBox(self, label='Verify', pos=(120, 125), checked=True)

        # Advanced settings sequence
        self.settings_label = wx.StaticText(self, label="Advanced:", pos=(210, 100))
        self.reset = SettingsCheckBox(self, label='Reset', pos=(210, 125), checked=True)

        button_pos_x = 310

        # Execute Write operation
        self.button_write = wx.Button(self, label="Write", pos=(button_pos_x, 155))
        self.Bind(wx.EVT_BUTTON, self.on_press_write, self.button_write)

        # Execute Read operation
        self.button_read = wx.Button(self, label="Read", pos=(button_pos_x, 185))
        self.Bind(wx.EVT_BUTTON, self.on_press_read, self.button_read)

        # Status progress bar
        self.status_bar = wx.Gauge(self, range=100, pos=(20, 157), size=(230, 20))
        self.status_bar_update(50)

        # Error Text Field
        self.err_field = wx.StaticText(self, label="Sample_text", pos=(20, 188))
        self.status_update('JinjaMe')

        parent.Bind(wx.EVT_CLOSE, self.on_close)

    def on_press_read(self, event):
        self._read_action_handler()
        pass

    def on_press_write(self, event):
        self._write_action_handler()
        pass

    def interface_values_get(self):
        return self.interface_values

    def status_update(self, text):
        self.err_field.SetLabel(text)

    def status_bar_update(self, value):
        self.status_bar.SetValue(value)

    def evt_radio_box(self, event):
        pass
        self.logger.AppendText('EvtRadioBox: %d\n' % event.GetInt())

    def evt_combo_box(self, event):
        pass
        self.logger.AppendText('EvtComboBox: %s\n' % event.GetString())

    def on_click(self, event):
        pass
        # self._file_dialog.summon()
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