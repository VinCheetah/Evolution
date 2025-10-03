""" 
This is the population package.

This package contains the following classes:
- BasePopulation
- SpeciatedPopulation

The BasePopulation class is the base class for all populations.
The SpeciatedPopulation class implements NEAT-style speciation.
"""

from evopy.population.base import BasePopulation
from evopy.population.speciated import SpeciatedPopulation


__all__ = [
    "BasePopulation",
    "SpeciatedPopulation",
]
