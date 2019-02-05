import sys
from app.back.back_data import AppData
from .gui.gui import GuiApplication
from app.utils import staying_alive
import threading
import time


class Stm32Flash:

    def __init__(self, **kwargs):
        self._app = None
        self._appdata = AppData()

        kwargs['close_handler'] = self.close

        self._back_thread = threading.Thread(target=self.background_loop_app)
        self._staying_alive = threading.Thread(target=staying_alive)

        self._back_thread.daemon = True
        self._staying_alive.daemon = True

        self.gui_app(**kwargs)

    def input_data_collector(self):
        """
            A function that should trigger gui provided interface functions
            to get commands from front-end part of the app
        """
        while True:
            # print('here')
            if self._app is not None:
                print(self._app.input_data_get())
            time.sleep(.1)

    def background_loop_app(self):
        pass

    def gui_app(self, **kwargs):
        kwargs['ports_property'] = self._appdata.serial_ports_available_ref_get()
        self._app = GuiApplication(**kwargs)

    def launch(self):

        self._back_thread.start()
        self._staying_alive.start()
        if self._app is not None:
            self._app.launch()
            self._app.close()
        # self.data_collect()
        pass

    def close(self):
        print('should be sys exitting by now')
        sys.exit()

