import wx


def execute_every(func):
    def decorator(self=None):
        # With this instruction we change receive bound method instead of a function
        bound_method = func.__get__(self, type(self))
        wx.CallLater(1000, execute_every(bound_method))
        return bound_method()
    return decorator
