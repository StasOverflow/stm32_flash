import sys
import glob
import serial
import serial.tools.list_ports_windows


def _serial_ports():
    """ Lists serial_uni port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial_uni ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def serial_ports():
    if sys.platform.startswith('win'):
        devices = serial.tools.list_ports_windows.comports()
        devices_ports = [device_object.device for device_object in devices]
        return devices_ports
    else:
        raise NotImplementedError('This type of platform is not supported')
