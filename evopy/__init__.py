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

You can create an environment directly with the Environment class and the options.
Otherwise, you can create one using the factory.

Once you have an environment, you can run the algorithm with the 'evolve' method.
"""

from evopy import utils
from evopy import individual
from evopy import population
from evopy import mutator
from evopy import crosser
from evopy import selector
from evopy import elite
from evopy import graphic
from evopy import interface
from evopy import environment
from evopy import factory


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
