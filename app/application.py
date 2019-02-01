from app.back.back_data import AppData
from .gui.gui import GuiApplication
import threading


class Stm32Flash:
    def data_collect(self):
        threading.Timer(.1, self.data_collect).start()

    def launch(self):
        appdata = AppData()

        ref_property = appdata.serial_ports_available_ref_get()
        self.data_collect()
        app = GuiApplication(ref_property)
