import configparser
from backend.utils import BAUDRATES
from backend.ports import serial_ports


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AppData(metaclass=_Singleton):

    PROJECT_DEFAULTS = {
        'build_ver': 'dev',
    }

    PRESETS_DEFAULTS = {
        'baud_rate': str(BAUDRATES[8]),
        'file_path': '',
        'device_port': '',
    }

    """
    LEGACY PIECE OF CODE
    """

    def _serial_ports_call(self):
        return self.device_ports_available

    def serial_ports_available_ref_get(self):
        return self._serial_ports_call

    """
    TILL HERE
    """

    @property
    def device_ports_available(self):
        return serial_ports()

    @property
    def baud_rates_available(self):
        bauds = [str(baud) for baud in BAUDRATES]
        return bauds

    @property
    def baud_rate(self):
        if self._baud_rate is not None:
            return self._baud_rate
        else:
            return self.PRESETS_DEFAULTS['baud_rate']

    @baud_rate.setter
    def baud_rate(self, value):
        self.changed = True
        self._baud_rate = value

    @property
    def device_port(self):
        return self._device_port

    @device_port.setter
    def device_port(self, value):
        self.changed = True
        self._device_port = value

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self.changed = True
        self._file_path = value

    def __init__(self):
        self.changed = True

        # Attributes goes here
        self.baud_rate = None
        self.file_path = None
        self.device_port = None

        self.build_ver = None

        self._serial_ports_available = None

        self.load()

    def load(self):
        """
        Loads data form config ini file into project's appdata

        TODO: Implement behaviour, when there is no config detected
              Implement behaviour, when one or several fields are empty
              Implement behaviour, when new sequence is about to be added
              to config file
        """
        config = configparser.ConfigParser()

        self.device_port = self.PRESETS_DEFAULTS['device_port']
        self.file_path = self.PRESETS_DEFAULTS['file_path']
        self.baud_rate = self.PRESETS_DEFAULTS['baud_rate']

        self.build_ver = self.PROJECT_DEFAULTS['build_ver']

        if config.read('config.ini'):
            try:
                sets = config['PRESETS']
                self.device_port = sets.get('device_port')
                self.file_path = sets.get('file_path')
                self.baud_rate = sets.get('baud_rate')
            except KeyError as e:
                pass

            try:
                sets = config['PROJECT']
                self.build_ver = sets.get('build_ver')
            except KeyError as e:
                pass

        self.save()

    def save(self):
        """
        On every settings change perform save of app parameters

        Method checks if certain settings are not None, transfers them into str
        format and saves them into config ini file
        """
        if self.changed:
            print('SAVING')

            self.changed = False
            config = configparser.ConfigParser()
            config['PRESETS'] = {}
            presets = config['PRESETS']

            if self.device_port is not None:
                presets['device_port'] = str(self.device_port)
            if self.file_path is not None:
                presets['file_path'] = str(self.file_path)
            presets['baud_rate'] = str(self.baud_rate)

            config['PROJECT'] = {}
            presets = config['PROJECT']

            if self.build_ver is not None:
                presets['build_ver'] = str(self.build_ver)

            with open('config.ini', 'w') as configfile:
                config.write(configfile)

    def __str__(self):
        output = 'baud : ' + str(self.baud_rate) + '\n' + \
                 'port : ' + str(self.device_port) + '\n' + \
                 'file : ' + str(self.file_path)
        return output


if __name__ == '__main__':
    data = AppData()
    print(data)

