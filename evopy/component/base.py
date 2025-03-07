"""
Defines the base class for components, providing logging and timing utilities.
"""

from time import time
from functools import wraps
from evopy.utils.options import Options
from evopy.utils.logger import create_logger, logg_levels_str
from evopy.utils.evo_types import Random, Unknown
from typing import Optional


class BaseComponent:
    """Base class for components, providing logging and timing utilities.

    Parameters:
    """

    _logger = create_logger()
    _requirements: dict[str, list] = {}
    component_type: str = "Base"
    component_name: str = "Component"
    init_requires_environment: bool = False

    def __init__(self, options: Options=None):
        """
        Initialize the component with options.

        Args:
            options (Options): Configuration options for the component.
        """
        self._options: Options = options
        self.component_name: str = self.get_latest("component_name")
        self.component_type: str = self.get_latest("component_type")
        self.init_requires_environment: bool = self.get_latest("init_requires_environment")
        self._duration: float = 0

    def get_latest(self, key: str):
        for subclass in self.__class__.__mro__:
            if hasattr(subclass, key):
                return getattr(subclass, key)

    @staticmethod
    def record_time(function):
        """
        Decorator to record the execution time of a method.

        Args:
            function (callable): The function to be wrapped.

        Returns:
            callable: The wrapped function.
        """

        @wraps(function)
        def wrapper(*args, **kwargs):
            start = time()
            result = function(*args, **kwargs)
            setattr(args[0], "_duration", time() - start)
            return result

        return wrapper

    def get_duration(self) -> float:
        """
        Get the duration of the last method call.
        """
        return self._duration

    @staticmethod
    def show_time(function):
        """
        Decorator to display the execution time of a method.

        Args:
            function (callable): The function to be wrapped.

        Returns:
            callable: The wrapped function.
        """

        @wraps(function)
        def wrapper(*args, **kwargs):
            start = time()
            result = function(*args, **kwargs)
            print(f"{function.__name__} : {time() - start:.3f} seconds")
            return result

        return wrapper

    @classmethod
    def add_requirement(cls, name, component_class):
        """
        Add a requirement to the component.

        Args:
            name (str): Name of the requirement.
            component_class (type): Required component.
        """
        if name not in cls._requirements:
            cls._requirements[name] = []
        if component_class not in cls._requirements[name]:
            cls._requirements[name] = []
        cls._requirements[name].append(component_class)

    @classmethod
    def get_requirements(cls) -> dict:
        """
        Get the requirements of the component.

        Returns:
            dict: Requirements of the component.
        """
        return cls._requirements

    @classmethod
    def del_requirements(cls, component_name: str):
        """
        Delete a requirement from the component.

        Args:
            component_name (str): Name of the requirement.
        """
        del cls._requirements[component_name]

    @classmethod
    def set_component_type(cls, component_type: str):
        """
        Set the component type.

        Args:
            component_type (str): Type of the component.
        """
        cls._component_type = component_type

    @classmethod
    def set_component_name(cls, component_name: str):
        """
        Set the component name.

        Args:
            component_name (str): Name of the component.
        """
        cls._component_name = component_name

    @classmethod
    def _set_options(cls):
        """Set class-level options. To be implemented by subclasses."""

    def _get_params(self):
        """Retrieve the parameters of the component. To be implemented by subclasses."""

    def __repr__(self):
        """Representation of the component."""
        return f"{self._component_name}({self._component_type})"

    @classmethod
    def __str__(cls) -> str:
        """String representation of the component."""
        return f"{cls._component_name}({cls._component_type})"

    @staticmethod
    def _get_level_from_str(level):
        """
        Convert a log level string to the corresponding logging level.

        Args:
            level (str): Log level as a string.

        Returns:
            int: Log level as an integer.

        Raises:
            ValueError: If the log level string is invalid.
        """
        level = level.lower()
        if level not in logg_levels_str:
            error = f"Log level should be one of {', '.join(logg_levels_str)}. Got '{level}'"
            raise ValueError(error)
        return logg_levels_str[level]

    def log(self, level, msg):
        """
        Log a message at the specified level.

        Args:
            level (str): Log level as a string.
            msg (str): Message to log.
        """
        log_level = self._get_level_from_str(level)
        msg = f"{self._component_name}({self._component_type}) -- {msg}"
        self._logger.log(log_level, msg)

    @staticmethod
    def is_random(value):
        return isinstance(value, Random)

    @staticmethod
    def is_unknown(value):
        return isinstance(value, Unknown)