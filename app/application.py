import sys
from app.back.back_data import AppData
from .gui.gui import GuiApplication
from app.utils import staying_alive
import threading
import time


class Stm32Flash:

    VALUE_DICTIONARY = {}

    def __init__(self, **kwargs):
        self._app = None
        self._appdata = AppData()

        self._dict_accessible = True
        kwargs['close_handler'] = self.close
        kwargs['vals'] = self.VALUE_DICTIONARY
        kwargs['dict_accessible'] = self._dict_accessible

        self._input_data = threading.Thread(target=self.input_data_collector)
        self._back_thread = threading.Thread(target=self.background_loop_app)
        self._staying_alive = threading.Thread(target=staying_alive)

        self._input_data.daemon = True
        self._back_thread.daemon = True
        self._staying_alive.daemon = True

        # kwargs['dict_lock'] = self._dict_lock

        self.gui_app(**kwargs)

    def input_data_collector(self):
        """
            A function that should trigger gui provided interface functions
            to get commands from front-end part of the app
        """
        while True:
            if self._app is not None:
                # print(
                    self._app.input_data_get()
                # )
            time.sleep(.1)

    def background_loop_app(self):
        while True:
            time.sleep(1)

    def gui_app(self, **kwargs):
        kwargs['ports_property'] = self._appdata.serial_ports_available_ref_get()
        self._app = GuiApplication(**kwargs)

    def launch(self):

        self._input_data.start()
        self._back_thread.start()
        self._staying_alive.start()
        if self._app is not None:
            self._app.launch()
            self._app.close()
        # self.data_collect()
        pass

    def close(self):
        sys.exit()

