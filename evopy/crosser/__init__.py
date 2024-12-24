"""
This is the Crosser package.

This package contains the following classes:
- BaseCrosser
- PermuCrosser
    - PermuCrosserPMX
- ChainCrosser
    - MeanChainCrosser
    
It also contains the optional classes for a crosser:
- MultiPointCrosser

The BaseCrosser class is the base class for all crossers.
"""

from evopy.crosser.base import BaseCrosser
from evopy.crosser.multi_point import MultiPointCrosser
from evopy.crosser.permutation.base import PermuCrosser
from evopy.crosser.permutation.pmx import PermuCrosserPMX
from evopy.crosser.chain.base import ChainCrosser
from evopy.crosser.chain.mean import MeanChainCrosser


__all__ = [
    "BaseCrosser",
    "MultiPointCrosser",
    "PermuCrosser",
    "PermuCrosserPMX",
    "ChainCrosser",
    "MeanChainCrosser",
]
