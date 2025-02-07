"""
This is the Mutator package.

This package contains the following classes:
- BaseMutator
- MultiMutator
- PermuMutator
- ChainMutator
    - BinaryChainMutator
    
The BaseMutator class is the base class for all mutators.
"""

from evopy.mutator.base import BaseMutator
from evopy.mutator.multi_mutator import MultiMutator
from evopy.mutator.permutation.base import PermuMutator
from evopy.mutator.chain.base import ChainMutator
from evopy.mutator.chain.binary import BinaryChainMutator


__all__ = [
    "BaseMutator",
    "MultiMutator",
    "PermuMutator",
    "ChainMutator",
    "BinaryChainMutator",
]
