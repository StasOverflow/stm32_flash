import wx
from itertools import cycle
import threading


def print_kwargs(**kwargs):
    for key, value in kwargs.items():
        print("The value of {} is {}".format(key, value))


def execute_every(func):
    # def wrap(func=None):
    def decorator(self=None):
        # With this instruction we change receive bound method instead of a function
        bound_method = func.__get__(self, type(self))
        # if  is not 0:
        wx.CallLater(500, execute_every(bound_method))
        return bound_method()
    return decorator
    # return wrap


def staying_alive():
    string = (
        ("Ah", 0.5),
        ("Ah", 0.5),
        ("Ah", 0.5),
        ("Ah", 0.5),
        ("Staying_alive", 1),
        ("Staying_alive", 1),

    )
    iterator = cycle(string)

    def do_cycle():
        val = next(iterator)
        text = val[0]
        delay = val[1]
        print(text)
        threading.Timer(delay, do_cycle).start()

    return do_cycle()


def get_dict_attr(obj, attr):
    """ Looks up attr in a given object's __dict__,
        and returns the associated value if its there.

        If attr is not a key in that __dict__, the object's
        MRO's __dict__s are searched. If the key is not found,
        an AttributeError is raised.
    """

    for obj in [obj] + obj.__class__.mro():
        # print(obj.__dict__)
        if attr in obj.__dict__:
            return obj.__dict__[attr]
    raise AttributeError


BAUDRATES = (1200, 1800, 2400, 4800, 9600, 19200, 38400,
             57600, 115200, 128000, 230400, 256000, 460800,
             500000, 576000, 921600, 1000000, 1500000, 2000000)
