""" 
This is the Environment package.
Environment is the class that gather all the components of the algorithm.

This package contains the following classes:
- BaseEnvironment
- ChainEnvironment
    - BinaryChainEnvironment
- PermuEnvironment

It also contains the following optional classes:
- GraphicEnvironment
- InterfaceEnvironment
"""

from evopy.environment.base import BaseEnvironment
from evopy.environment.chain.base import ChainEnvironment
from evopy.environment.chain.binary import BinaryChainEnvironment
from evopy.environment.permutation.base import PermuEnvironment
from evopy.environment.graphic import GraphicEnvironment
from evopy.environment.interface import InterfaceEnvironment


__all__ = [
    "BaseEnvironment",
    "ChainEnvironment",
    "BinaryChainEnvironment",
    "PermuEnvironment",
    "GraphicEnvironment",
    "InterfaceEnvironment",
]
