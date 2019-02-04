import wx
from itertools import cycle
import threading


def execute_every(delay_ms):
    def wrap(func=None):
        def decorator(self=None):
            # With this instruction we change receive bound method instead of a function
            bound_method = func.__get__(self, type(self))
            if delay_ms is not 0:
                wx.CallLater(delay_ms, execute_every(bound_method))
            return bound_method()
        return decorator
    return wrap


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
