from base.utils.logger import create_logger, logg_levels_str
import logging as lg
from time import time
from functools import wraps


class BaseComponent:

    _logger = create_logger()

    _component_name: str = "Component"
    _component_type: str = "Base"

    def __init__(self, options):
        self._options = options
        self._duration: float = 0
        pass
        # self.__attrs_post_init__()

    @staticmethod
    def record_time(fonction):
        @wraps(fonction)
        def wrapper(*args, **kwargs):
            start = time()
            resultat = fonction(*args, **kwargs)
            setattr(args[0], "_duration", time() - start)
            return resultat
        return wrapper

    @staticmethod
    def show_time(fonction):
        @wraps(fonction)
        def wrapper(*args, **kwargs):
            debut = time()
            resultat = fonction(*args, **kwargs)
            print(f"{fonction.__name__} : {time() - debut:.3f}")
            return resultat
        return wrapper

    def __attrs_post_init__(self):
        pass

    @classmethod
    def _set_options(cls):
        pass

    def _get_params(self):
        pass

    def __repr__(self):
        return f"{self._component_name}({self._component_type})"

    def __str__(self) -> str:
        return f"{self._component_name}({self._component_type})"

    def _get_level_from_str(self, level):
        level = level.lower()
        assert level in logg_levels_str, ValueError(f"Logg level should be in {', '.join(logg_levels_str)}. Got {level}")
        return logg_levels_str[level]

    def log(self, level, msg):
        log_level = self._get_level_from_str(level)
        msg = self._component_name + "(" + self._component_type + ")" + " -- " + msg
        self._logger.log(log_level, msg)

    def _valid_create_args(self, *args, **kwargs):
        return None
