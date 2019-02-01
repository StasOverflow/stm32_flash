from .ports.ports import serial_ports
import random


class AppData:
    """ A class that provides interfaces to all types of data
        for current application
    """

    def __init__(self):
        self._serial_ports_available = None

    @property
    def serial_ports_available(self):
        self._serial_ports_available = serial_ports()
        return self._serial_ports_available

    def _serial_ports_call(self):
        return self.serial_ports_available

    def serial_ports_available_ref_get(self):
        return self._serial_ports_call

