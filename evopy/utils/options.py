# This file contains the Options class which is a subclass of dict.
from evopy.options.default import default

class Options2(dict):

    def __init__(self, name: str = "default", *args, **kwargs):
        super(Options, self).__init__(*args, **kwargs)
        self.name = name
        self.default = default

    def items(self):
        return list((k, v) for k, v in super().items() if k not in ["name", "default"])

    @classmethod
    def get_default(cls):
        from evopy.options.default import default
        return default

    def create(self):
        return self.environment(self)

    def set_default(self, default_opts):
        self.default = default_opts

    def assert_subtype(self, key, cls):
        if not issubclass(self.__getattr__(key), cls):
            self.__setattr__(key, cls)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        if key not in self:
            print(key)
            print(self.default)
            if key not in self.default:
                print(f"Options object has no attribute {key}")
                raise AttributeError(f"Options object has no attribute {key}")
            return self.default[key]
        return self[key]

    def __getattribute__(self, key):
        if key not in object.__getattribute__(self, "__dict__"):
            default_ = object.__getattribute__(self, "default")
            if key not in default_:
                print(f"Options object has no attribute {key}")
                raise AttributeError(f"Options object has no attribute {key}")
            return default_[key]
        return object.__getattribute__(self, key)

    def __repr__(self):
        return f"Options {self.name}({super().__repr__()})"

    def __str__(self):
        return f"Options {self.name}({super().__str__()})"



from evopy.options.default import default

class Options(dict):
    """
    A dictionary-like configuration object with:
    - attribute-style access (opts.foo instead of opts["foo"])
    - fallback to default values if a key is missing
    - a 'name' to identify the configuration
    """

    def __init__(self, name: str = "default", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = name
        self._default = default

    # --- Attribute access ---------------------------------------------------

    def __getattr__(self, key):
        # Called only if normal attribute access fails
        if key in self:
            return self[key]
        if key in self._default:
            return self._default[key]
        raise AttributeError(f"Options object has no attribute '{key}'")

    def __setattr__(self, key, value):
        # Use normal attributes for private ones (starting with _)
        if key.startswith("_"):
            super().__setattr__(key, value)
        else:
            self[key] = value

    def __delattr__(self, key):
        if key in self:
            del self[key]
        else:
            raise AttributeError(f"Options object has no attribute '{key}'")

    # --- Items access -------------------------------------------------------

    def items(self):
        """Return only config keys (excluding internal attributes)."""
        return ((k, v) for k, v in super().items())

    # --- Default handling ---------------------------------------------------

    @classmethod
    def get_default(cls):
        from evopy.options.default import default as d
        return Options("default", **d)

    def set_default(self, default_opts):
        self._default = default_opts

    # --- Utility ------------------------------------------------------------

    def create(self):
        if not hasattr(self, "environment"):
            raise AttributeError("Options has no 'environment' callable.")
        return self.environment(self)

    def assert_subtype(self, key, cls):
        value = getattr(self, key)
        if not isinstance(value, type) or not issubclass(value, cls):
            raise TypeError(f"'{key}' must be a subclass of {cls.__name__}")

    # --- Representation -----------------------------------------------------

    def __repr__(self):
        return f"Options {self._name}({dict.__repr__(self)})"

    def __str__(self):
        return f"Options {self._name}({dict.__str__(self)})"

