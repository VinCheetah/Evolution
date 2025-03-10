""" 
Defines the MultiMutator class.
It is a subclass of BaseMutator.
This class permits to enable multiple mutators at the same time.
"""

from random import choice
from functools import wraps
from evopy.mutator.base import BaseMutator


class MultiMutator(BaseMutator):
    """
    MultiMutator class.
    This class permits to enable multiple mutators at the same time.

    Parameters:
    """

    component_type: str = "Multi"
    _functions = []

    def _mutate(self, individual) -> bool:
        random_mutator = choice(self._functions)
        return random_mutator(self, individual)

    @staticmethod
    def add_mutation_func():
        """
        Decorator to add a function to the list of functions to be called by the MultiMutator.
        """

        def decorator(method):
            MultiMutator._functions.append(method)

            @wraps(method)
            def wrapper(*args, **kwargs):
                return method(*args, **kwargs)

            return wrapper
        return decorator
    