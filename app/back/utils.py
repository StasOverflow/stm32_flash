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
