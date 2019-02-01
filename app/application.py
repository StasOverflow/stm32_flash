from app.back.back_data import AppData
from .gui.gui import GuiApplication
import threading

from itertools import cycle


class Stm32Flash:
    STRING = (
        ("Ah", 0.5),
        ("Ah", 0.5),
        ("Ah", 0.5),
        ("Ah", 0.5),
        ("Staying_alive", 1),
        ("Staying_alive", 1),

    )
    iterator = cycle(STRING)

    def data_collect(self):
        val = next(self.iterator)
        text = val[0]
        delay = val[1]
        print(text)
        threading.Timer(delay, self.data_collect).start()

    def launch(self):
        appdata = AppData()

        ref_property = appdata.serial_ports_available_ref_get()
        self.data_collect()
        app = GuiApplication(ref_property)
