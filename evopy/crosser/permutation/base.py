"""
Defines the base class for permutation crossers: PermuCrosser.
This class is a subclass of the Base Crosser class.
"""

import random as rd
import numpy as np
from evopy.crosser.base import BaseCrosser
from evopy.individual import PermuIndividual


class PermuCrosser(BaseCrosser):
    """
    Base class for permutation crossers.

    Parameters:
    """

    BaseCrosser.set_component_type("Permutation")
    BaseCrosser.add_requirement("individual", PermuIndividual)

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseCrosser.__init__(self, options)

    def _cross(self, ind1: PermuIndividual, ind2: PermuIndividual) -> dict:
        size: int = len(ind1)
        start: int = rd.randint(0, size-1)

        path: list[None | int] = [None] * (size * 2)
        seen: list[bool] = [False] * size
        beg: int = size - 1
        end: int = size + 1
        path[size] = start
        seen[start] = True
        idx_1: int = np.flatnonzero(ind1.get_permutation() == start)[0]
        idx_2: int = np.flatnonzero(ind2.get_permutation() == start)[0]

        while end - beg <= size:
            if rd.random() < .5:
                while seen[ind1[idx_1 % size]]:
                    idx_1 += 1
                seen[ind1[idx_1 % size]] = True
                path[end] = ind1[idx_1 % size]
                end += 1
            else:
                while seen[ind2[idx_2 % size]]:
                    idx_2 -= 1
                seen[ind2[idx_2 % size]] = True
                path[beg] = ind2[idx_2 % size]
                beg -= 1

        return {"permutation": np.array(path[beg+1: end])}
