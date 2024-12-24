""" 
Define the base package for the project.

This package contains the following subpackages:
- component
- environment
- individual
- population
- mutator
- crosser
- selector
- elite
- graphic
- interface
- factory
- utils

You can create an environmennt directly with the Environment class and the options.
Otherwise, you can create one using the factory.

Once you have an environment, you can run the algorithm with the 'evolve' method.
"""

from . import utils
from . import individual
from . import population
from . import mutator
from . import crosser
from . import selector
from . import elite
from . import graphic
from . import interface
from . import environment
from . import factory


__all__ = [
    "environment",
    "individual",
    "population",
    "mutator",
    "crosser",
    "selector",
    "elite",
    "graphic",
    "interface",
    "factory",
    "utils",
]
