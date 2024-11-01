# This file contains the Options class which is a subclass of dict.

class Options(dict):

    def __init__(self, *args, **kwargs):
        super(Options, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def assert_subtype(self, key, cls):
        if not issubclass(self.__getattr__(key), cls):
            self.__setattr__(key, cls)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        if key not in self:
            print(f"Warning: {key} is not a valid attribute")
            raise AttributeError
        return self[key]

    def __repr__(self):
        return f"Options({super().__repr__()})"

    def __str__(self):
        return f"Options({super().__str__()})"
