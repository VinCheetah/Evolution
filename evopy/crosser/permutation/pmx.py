"""
Defines the PermuCrosserPMX class. 
This class is a subclass of the MultiPointCrosser and BaseCrosser classes.
It is used to perform the PMX crossover operation on PermuIndividuals.
"""

import numpy as np
from evopy.crosser.permutation.base import PermuCrosser
from evopy.crosser.multi_point import MultiPointCrosser
from evopy.individual import PermuIndividual


class PermuCrosserPMX(MultiPointCrosser, PermuCrosser):
    """
    This is the PermuCrosserPMX class.
    This class is a subclass of the MultiPointCrosser and BaseCrosser classes.
    It is used to perform the PMX crossover operation on PermuIndividuals.
    
    Parameters:
        * num_points (int): The number of points to use in the crossover.
            Min: 1
            Fixed: 2
    """

    component_type: str = "PMX"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        options.num_points = 2
        MultiPointCrosser.__init__(self, options)
        PermuCrosser.__init__(self, options)

    def _cross_points(self, data: dict, ind2: PermuIndividual, *idx) -> dict:
        idx1, idx2 = idx
        permutation = data["permutation"]

        indices = np.empty_like(permutation)
        indices[permutation] = np.arange(len(permutation))

        for i in range(idx1, idx1+abs(idx2-idx1)+1):
            i = i % len(permutation)
            if permutation[i] != ind2[i]:
                idx = indices[ind2[i]]
                permutation[i], permutation[idx] = permutation[idx], permutation[i]
        data["permutation"] = permutation
        return data
