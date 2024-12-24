"""
This is the Selector package.

This package contains the following classes:
- BaseSelector
- EliteSelector
- TournamentSelector
- WheelSelector
"""

from evopy.selector.base import BaseSelector
from evopy.selector.elite import EliteSelector
from evopy.selector.tournament import TournamentSelector
from evopy.selector.wheel import WheelSelector


__all__ = [
    "BaseMutator",
    "PermuMutator",
    "ChainMutator",
    "BinaryChainMutator",   
]
