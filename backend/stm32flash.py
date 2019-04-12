import os
import sys
from backend.app_data import AppData
from gui.gui import GuiApplication
import threading
import time
from copy import deepcopy
from backend.flasher.stm32loader import Stm32Loader


class Stm32Flash:
    ACTION_READ = 1
    ACTION_WRITE = 2

    VALUE_DICTIONARY = {}
    ACTION_TYPE = (
        (ACTION_READ, 'ACTION_READ'),
        (ACTION_WRITE, 'ACTION_WRITE'),
    )

    BAUDRATE_LIST = {
        '9600': 9600,
        '19200': 19200,
        '38400': 38400,
        '57600': 57600,
        '115200': 115200,
        '128000': 128000,
        '230400': 230400,
        '256000': 256000,
    }

    def __init__(self, **kwargs):
        self._app = None
        self.app_data = AppData()
        self._ports = self.app_data.device_ports_available

        self._error_message = None
        self.interface_data = None

        self.write_action = False
        self.read_action = False

        kwargs['close_handler'] = self.close
        kwargs['vals'] = self.VALUE_DICTIONARY
        kwargs['read_handler'] = self.read_action_handler
        kwargs['write handler'] = self.write_action_handler

        self._input_data_thread = threading.Thread(target=self.input_data_collector)
        self._back_thread = threading.Thread(target=self.background_loop_app)

        self._input_data_thread.daemon = True
        self._back_thread.daemon = True

        self.on_duty = False

        self.gui_app(**kwargs)

    @property
    def on_action(self):
        return self._app.action_is_on_going

    @property
    def error_message(self):
        return self._error_message

    def error_message_set(self, msg=None, code=None):
        self._error_message = msg
        if self.error_message is not None:
            self._app.frame.panel.status_update(self._error_message)
            self._app.frame.panel.error_is(code)

    def read_thread_handler(self):
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
                if self.on_action is False:
                    self.interface_data = deepcopy(self._app.input_data_get())
            time.sleep(0.2)

    def background_loop_app(self):
        # print('after update')
        while True:
            if self._app is not None:
                pass

            self.app_data.save()
            self._app.frame.panel.update_time_current()
            time.sleep(0.3)

    def gui_app(self, **kwargs):
        kwargs['ports_getter'] = self.ports
        kwargs['baud_list'] = self.BAUDRATE_LIST
        self._app = GuiApplication(**kwargs)

    def launch(self):
        if self._app is not None:

            self._input_data_thread.start()
            self._back_thread.start()

            self._app.launch()
            self._app.close()
        # self.data_collect()

    def close(self):
        sys.exit()

    def handler_init(self, action):
        if not self.on_duty:
            self.on_duty = True
            file_path = self.app_data.file_path
            port = self.app_data.device_port
            baud_rate = self.app_data.baud_rate
            baud_rate = int(baud_rate) if baud_rate is not None else None
            if port is not None:
                pass
                if baud_rate is not None:
                    if os.path.exists(file_path):
                        permission_to_execute = True
                    else:
                        permission_to_execute = False
                        self.error_message_set('Specify a path to file', 404)
                else:
                    permission_to_execute = False
                    self.error_message_set('Specify a baudrate', 404)
            else:
                permission_to_execute = False
                self.error_message_set('Specify a device port', 404)

            if permission_to_execute:
                self.on_duty = True
                reset = self.interface_data['f_reset']
                erase = True if self.interface_data['f_erase'] is False else False
                verify = self.interface_data['f_verify']

                self._app.action_is_on_going = False

                self.error_message_set(('Started ' + ('writing' if action == self.ACTION_WRITE else 'reading') +
                                        ' operation'), None)
                message = 'Done ' + ('writing' if action == self.ACTION_WRITE else 'reading')

                kw_dict = {
                    'port': port,
                    'file_path': file_path,
                    'action': action,
                    'baud_rate': baud_rate,
                    'device': port,
                    'reset': reset,
                    'execute_flag': 1,
                    'callback': self.status_bar_update,
                    'verify': verify,
                    'erase': erase,
                    'message': message,
                }

                t = threading.Thread(target=self.launch_da_thread, kwargs=kw_dict)

                t.daemon = True
                t.start()

    def read_action_handler(self):
        self.handler_init(self.ACTION_READ)

    def write_action_handler(self):
        self.handler_init(self.ACTION_WRITE)

    def launch_da_thread(self, **kwargs):
        port = kwargs['port']
        file_path_passed = kwargs['file_path']
        action = kwargs['action']
        baud_rate_passed = kwargs['baud_rate']
        callback = kwargs['callback']
        message = kwargs['message']
        loader = Stm32Loader(logger=self._app.frame.panel.status_update)

        argums = list()
        argums.append('-p')
        argums.append(port)
        argums.append('-b')
        argums.append(str(baud_rate_passed))
        if action == self.ACTION_READ:
            argums.append('-r')
            argums.append('-v')
        else:
            argums.append('-e')
            argums.append('-w')
            argums.append('-v')

        argums.append('-B')
        argums.append('-R')
        argums.append('-g')
        argums.append('0x08000000')
        try:
            argums.append(file_path_passed)
            loader.parse_arguments(argums, callback=callback)
            loader.connect()
            try:
                loader.read_device_details()
                loader.perform_commands()
            finally:
                loader.reset()
                self.status_bar_update(100)
                time.sleep(1)
                self.error_message_set(message, 200)
        finally:
            self.on_duty = False
            self._app.frame.panel.update_time_last()
        self.on_duty = False

    def status_bar_update(self, value):
        self._app.frame.panel.status_bar_update(value)

