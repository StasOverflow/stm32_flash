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
