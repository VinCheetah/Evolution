"""
The Individual package.

This package provides the following classes for creating and managing individuals in an evolutionary algorithm:

- `BaseIndividual`: The base class for all individual types.
- `PermuIndividual`: Represents an individual based on permutations.
- `ChainIndividual`: Represents a chain-based individual.
  - `BinaryChainIndividual`: A specific implementation of `ChainIndividual` using binary values.
- `NNIndividual`: Represents an individual based on neural networks.
"""

from .base import BaseIndividual
from .permutation.base import PermuIndividual
from .chain.base import ChainIndividual
from .chain.binary import BinaryChainIndividual
from .neural_network.base import NNIndividual

__all__ = [
    "BaseIndividual",
    "PermuIndividual",
    "ChainIndividual",
    "BinaryChainIndividual",
    "NNIndividual",
]
