"""
Defines the base class for components, providing logging and timing utilities.
"""

from time import time
from functools import wraps
from evopy.utils.logger import create_logger, logg_levels_str


class BaseComponent:
    """Base class for components, providing logging and timing utilities."""

    _logger = create_logger()

    _component_name: str = "Component"
    _component_type: str = "Base"
    init_requires_environment: bool = False

    def __init__(self, options):
        """
        Initialize the component with options.

        Args:
            options (dict): Configuration options for the component.
        """
        self._options = options
        self._duration: float = 0

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
    def _set_options(cls):
        """Set class-level options. To be implemented by subclasses."""

    def _get_params(self):
        """Retrieve the parameters of the component. To be implemented by subclasses."""

    def __repr__(self):
        """Representation of the component."""
        return f"{self._component_name}({self._component_type})"

    def __str__(self) -> str:
        """String representation of the component."""
        return f"{self._component_name}({self._component_type})"

    def _get_level_from_str(self, level):
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
