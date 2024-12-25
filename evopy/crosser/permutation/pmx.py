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
    """

    PermuCrosser.set_component_type("PMX")

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        MultiPointCrosser.__init__(self, options, num_points=2)
        PermuCrosser.__init__(self, options)

    def _cross_points(self, data: dict, ind2: PermuIndividual, *idx) -> dict:
        idx1, idx2 = idx
        permu = data["permutation"]

        indices = np.empty_like(permu)
        indices[permu] = np.arange(len(permu))

        for i in range(idx1, idx1+abs(idx2-idx1)+1):
            i = i % len(permu)
            if permu[i] != ind2[i]:
                idx = indices[ind2[i]]
                permu[i], permu[idx] = permu[idx], permu[i]
        data["permutation"] = permu
        return data
