""" 
This is the Environment package.
Environment is the class that gather all the components of the algorithm.

This package contains the following classes:
- BaseEnvironment
- GraphicEnvironment
- InterfaceEnvironment

It also contains the following mixins:
- ChainMixin
    - BinaryChainMixin
- PermuMixin

Mixins are used to require and suggest types of components to the environment.
"""

from evopy.environment.base import BaseEnvironment
from evopy.environment.graphic import GraphicEnvironment
from evopy.environment.interface import InterfaceEnvironment
from evopy.environment.mixins.chain.base import ChainMixin
from evopy.environment.mixins.chain.binary import BinaryChainMixin
from evopy.environment.mixins.permutation.base import PermuMixin


__all__ = [
    "BaseEnvironment",
    "GraphicEnvironment",
    "InterfaceEnvironment",
    "ChainMixin",
    "BinaryChainMixin",
    "PermuMixin"
]
