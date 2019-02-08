import wx
import wx.adv
from app.gui.window.widgets.base import DynamicFlexibleChoice, StaticFlexibleChoice, InputFile, SettingsCheckBox
import wx.lib.agw.pygauge as PG
import datetime


class Panel(wx.Panel):
    def __init__(self, parent, **kwargs):
        self._size = kwargs['size']
        self._read_action_handler = kwargs['read_handler']
        self._write_action_handler = kwargs['write handler']
        wx.Panel.__init__(self, parent, size=self._size)

        self.interface_values = {
            'port': None,
            'baud': None,
            'path': None,
            'f_erase': None,
            'f_verify': None,
            'f_reset': None,
        }

        # Error Text Field
        self.err_field = wx.StaticText(self, label="", pos=(20, 162))

        # Error Iconio
        self.err_icon = wx.StaticText(self, label="", pos=(230, 153))
        font = wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.NORMAL)

        '''
            family can be:
            wx.DECORATIVE, wx.DEFAULT, wx.MODERN, wx.ROMAN, wx.SCRIPT or wx.SWISS.

            style can be:
            wx.NORMAL, wx.SLANT or wx.ITALIC.

            weight can be:

            wx.NORMAL, wx.LIGHT, or wx.BOLD
        '''

        self.err_icon.SetFont(font)
        self.err_icon.Hide()

        # Choice 1
        kwargs.setdefault('ports_getter', [None, None])
        ports_property = kwargs['ports_getter']
        print('ports property is', ports_property)
        self.dyn_flex_dc = None
        self._action_is_on_going = False
        self.port_box = DynamicFlexibleChoice(self, label='Device port',
                                              property_to_display=ports_property,
                                              pos=(20, 20), width=110, dc=self.dyn_flex_dc)
        self.Bind(self.port_box.event_on_choice, self.evt_choice_port, self.port_box)

        # Choice 2
        # kwargs.setdefault('baud_list', [None, None])
        baud_property = kwargs['baud_list']
        # print(baud_property)
        self.baud_box = StaticFlexibleChoice(self, label='Baudrate',
                                             property_to_display=baud_property,
                                             pos=(240, 20), width=100)
        self.Bind(self.port_box.event_on_choice, self.evt_choice_baud, self.baud_box)

        # File Input
        self.file_path_unit = InputFile(self, label='File path:', pos=(20, 60), callback=self.on_click)

        # Settings sequence
        # self.settings_label = wx.StaticText(self, label="Settings:", pos=(20, 100))
        self.mode = SettingsCheckBox(self, label='Expert Mode', pos=(20, 100), checked=False)
        self.Bind(wx.EVT_CHECKBOX, self.change_mode, self.mode)

        self.erasing = SettingsCheckBox(self, label='Erase', pos=(20, 130), checked=True)
        self.verify = SettingsCheckBox(self, label='Verify', pos=(120, 130), checked=True)
        self.reset = SettingsCheckBox(self, label='Reset', pos=(210, 130), checked=True)

        self.Bind(wx.EVT_CHECKBOX, self.evt_erase_checkbox, self.erasing)
        self.Bind(wx.EVT_CHECKBOX, self.evt_verify_checkbox, self.verify)
        self.Bind(wx.EVT_CHECKBOX, self.evt_reset_checkbox, self.reset)

        self.interface_values['f_erase'] = self.erasing.flag
        self.interface_values['f_verify'] = self.verify.flag
        self.interface_values['f_reset'] = self.reset.flag

        self.reset.Disable()
        self.verify.Disable()
        self.erasing.Disable()

        button_pos_x = 310

        # Execute Write operation
        self.button_write = wx.Button(self, label="Write", pos=(button_pos_x, 155))
        self.Bind(wx.EVT_BUTTON, self.on_press_write, self.button_write)

        # Execute Read operation
        self.button_read = wx.Button(self, label="Read", pos=(button_pos_x, 185))
        self.button_read.Disable()
        self.Bind(wx.EVT_BUTTON, self.on_press_read, self.button_read)

        # Cancel Button
        self.button_cancel = wx.Button(self, label="Cancel", pos=(button_pos_x, 215))
        self.Bind(wx.EVT_BUTTON, self.on_press_cancel, self.button_cancel)
        self.button_cancel.Disable()
        self.button_cancel.Hide()

        # Status progress bar
        self.status_bar = wx.Gauge(self, range=100, pos=(20, 187), size=(230, 20), style=wx.GA_HORIZONTAL)
        self.status_bar.SetValue(0)

        width = 141

        self.status_under_bar_status = wx.StaticText(self, label="", pos=(0, 222), size=(width, 17),
                                                     style=wx.ALIGN_LEFT)
        self.status_under_bar_status.SetBackgroundColour((200, 200, 200))  # set text color

        self.status_under_bar_current = wx.StaticText(self, label="", pos=(width + 1, 222), size=(width, 17),
                                                      style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.status_under_bar_current.SetBackgroundColour((200, 200, 200))  # set text color
        self.update_time_current()

        self.status_under_bar_last_one = wx.StaticText(self, label="", pos=((width + 1) * 2, 222), size=(width, 17),
                                                       style=wx.ALIGN_RIGHT)
        self.status_under_bar_last_one.SetBackgroundColour((200, 200, 200))  # set text color
        # self.status_bar.SetBarColor([wx.Colour(162, 255, 178), wx.Colour(159, 176, 255)])
        # self.status_bar.SetBorderColor(wx.BLACK)
        # self.status_bar.SetBorderPadding(2)

        parent.Bind(wx.EVT_CLOSE, self.on_close)

    @property
    def action_is_on_going(self):
        return self._action_is_on_going

    @action_is_on_going.setter
    def action_is_on_going(self, value):
        pass
        # self._action_is_on_going = value
        # if self._action_is_on_going is False:
        #     self.button_cancel.Disable()
        #     self.button_read.Enable()
        #     self.button_write.Enable()
        # else:
        #     self.button_cancel.Enable()
        #     self.button_read.Disable()
        #     self.button_write.Disable()

    def update_time_current(self):
        self.status_under_bar_current.SetLabel(datetime.datetime.now().strftime("%I:%M:%S %p"))
        pass

    def update_time_last(self):
        self.status_under_bar_last_one.SetLabel(datetime.datetime.now().strftime("%I:%M:%S %p   "))
        pass

    def error_is(self, value):
        ERROR = 404
        OK = 200
        self.err_icon.Show()
        if value is not None:
            if value == ERROR:
                self.err_icon.SetForegroundColour((255, 0, 0))  # set text color
                self.err_icon.SetLabel('\u26A0')
                print('got 404')
                self.status_under_bar_status.SetLabel('   Status: ERROR')
            elif value == OK:
                self.err_icon.SetForegroundColour((0, 255, 0))  # set text color
                print('got 200')
                self.status_under_bar_status.SetLabel('   Status: OK')
                self.err_icon.SetLabel('\u2714')
        else:
            self.err_icon.Hide()
            self.status_under_bar_status.SetLabel('   Status: Updating..')

    def change_mode(self, event):
        if event.IsChecked():
            self.reset.Enable()
            self.verify.Enable()
            self.erasing.Enable()
            self.button_read.Enable()
        else:
            self.reset.Disable()
            self.verify.Disable()
            self.erasing.Disable()
            self.button_read.Disable()

    def on_click(self, event):
        self.file_path_unit.file_dialog.ShowModal()
        self.file_path_unit.Clear()
        path = self.file_path_unit.file_dialog.GetPath()
        if path is not "":
            self.file_path_unit.path_to_file = path
            self.file_path_unit.caption = path
        else:
            self.file_path_unit.caption = "Select a file"
        self.file_path_unit.write(self.file_path_unit.caption)
        self.file_path_unit.file_dialog.Close()
        self.status_bar_update(0)

    def on_press_read(self, event):
        self.status_bar_update(0)
        self._read_action_handler()
        pass

    def on_press_write(self, event):
        self.status_bar_update(0)
        self._write_action_handler()
        pass

    def on_press_cancel(self, event):
        self._write_action_handler()
        pass

    def interface_values_get(self):
        self.interface_values['path'] = self.file_path_unit.path_to_file
        return self.interface_values

    def status_update(self, text, status=None):
        self.err_field.SetLabel(text)
        self.error_is(status)

    def status_bar_update(self, value):
        if value is 0:
            self.err_icon.Hide()
            self.status_update("")
        self.status_bar.SetValue(value)

    def evt_verify_checkbox(self, event):
        self.status_bar_update(0)
        self.interface_values['f_verify'] = event.IsChecked()

    def evt_erase_checkbox(self, event):
        self.status_bar_update(0)
        self.interface_values['f_erase'] = event.IsChecked()

    def evt_reset_checkbox(self, event):
        self.status_bar_update(0)
        self.interface_values['f_reset'] = event.IsChecked()

    def evt_choice_baud(self, event):
        self.status_bar_update(0)
        self.interface_values['baud'] = event.GetString()

    def evt_choice_port(self, event):
        self.status_bar_update(0)
        self.interface_values['port'] = event.GetString()

    def on_close(self, event):
        print("in on close ")
        if event.CanVeto():

            # if wx.MessageBox("You are about to close the app",
            #                  "Please confirm",
            #                  wx.ICON_QUESTION | wx.YES_NO) != wx.YES:

            event.Veto()
                # return

        event.Skip()

        # Add a handler, that informs the main program about closing
