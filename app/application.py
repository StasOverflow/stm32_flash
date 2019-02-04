import sys
from app.back.back_data import AppData
from .gui.gui import GuiApplication
from app.gui.base.utils import staying_alive
import threading


class Stm32Flash:

    def __init__(self, **kwargs):
        self._appdata = AppData()

        kwargs.setdefault('close_handler', self.close)
        self._close_handler = kwargs['close_handler']

        self._data_thread = threading.Thread(target=self.input_data_collector)
        self._back_thread = threading.Thread(target=self.background_loop_app)

        self._data_thread.daemon = True
        self._back_thread.daemon = True

        self._data_thread.start()
        self._back_thread.start()
        self.gui_app()

    def input_data_collector(self):
        """
            A function that should trigger gui provided interface functions
            to get commands from front-end part of the app
        """
        pass

    def background_loop_app(self):
        staying_alive()

    def gui_app(self):
        ports_property = self._appdata.serial_ports_available_ref_get()
        app = GuiApplication(ports_property=ports_property, close_handler=self._close_handler)

    def launch(self):
        # self.data_collect()
        pass

    def close(self):
        sys.exit()

