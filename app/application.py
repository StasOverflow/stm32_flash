import sys
from app.back.back_data import AppData
from .gui.gui import GuiApplication
from app.utils import staying_alive
import threading
import time
import stm32_flash
from copy import deepcopy


class Stm32Flash:

    VALUE_DICTIONARY = {}

    def __init__(self, **kwargs):
        self._app = None
        self._appdata = AppData()
        self._ports = self._appdata.serial_ports_available

        self.error_message = None
        self.interface_data = None

        self._dict_accessible = True
        kwargs['close_handler'] = self.close
        kwargs['vals'] = self.VALUE_DICTIONARY
        kwargs['dict_accessible'] = self._dict_accessible
        kwargs['read_handler'] = self.read_action_handler
        kwargs['write handler'] = self.write_action_handler

        self._port_poller = threading.Thread(target=self.port_poll)
        self._input_data_thread = threading.Thread(target=self.input_data_collector)
        self._back_thread = threading.Thread(target=self.background_loop_app)
        self._staying_alive = threading.Thread(target=staying_alive)
        self._error_handler = threading.Thread(target=self.error_handler)

        self._error_handler.daemon = True
        self._input_data_thread.daemon = True
        self._back_thread.daemon = True
        self._staying_alive.daemon = True
        self._port_poller.daemon = True

        # kwargs['dict_lock'] = self._dict_lock

        self.gui_app(**kwargs)

    @property
    def error_message(self):
        return self._error_message

    @error_message.setter
    def error_message(self, msg):
        self._error_message = msg

    def error_handler(self):
        self.error_message = 1
        while True:
            self.error_message += 1
            self._app.frame.panel.status_update(str(self.error_message))
            time.sleep(.2)

    def error_message_update(self, string):
        # self.
        pass

    def ports(self):
        return self._ports

    def input_data_collector(self):
        """
            A function that should trigger gui provided interface functions
            to get commands from front-end part of the app
        """
        while True:
            if self._app is not None:
                self.interface_data = deepcopy(self._app.input_data_get())
            time.sleep(.1)

    def background_loop_app(self):
        if self._app is not None:
            while True:
                time.sleep(1)

    def port_poll(self):
        while True:
            self._ports = self._appdata.serial_ports_available
            time.sleep(0.1)

    def gui_app(self, **kwargs):
        kwargs['ports_getter'] = self.ports
        kwargs['baud_list'] = stm32_flash.baud_list_get()
        self._app = GuiApplication(**kwargs)

    def launch(self):
        if self._app is not None:

            self._input_data_thread.start()
            self._back_thread.start()
            self._staying_alive.start()
            self._port_poller.start()
            self._error_handler.start()
            if self._app is not None:
                self._app.launch()
                self._app.close()
        # self.data_collect()

    def close(self):
        sys.exit()

    def read_action_handler(self):
        print('read pressed')
        pass

    def write_action_handler(self):
        print('write pressed')
        pass

