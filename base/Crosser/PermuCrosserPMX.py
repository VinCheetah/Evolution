from base.Crosser.BaseCrosser import BaseCrosser
from base.Crosser.MultiPointCrosser import MultiPointCrosser
from base.Individual.BaseIndividual import BaseIndividual
from base.Individual.PermuIndividual import PermuIndividual
import random as rd
import numpy as np


class PermuCrosserPMX(MultiPointCrosser, BaseCrosser):

    _component_type: str = "PMX"

    def __init__(self, options, **kwargs):
        options["num_points"] = 2
        options.update(kwargs)

        MultiPointCrosser.__init__(self, options)
        BaseCrosser.__init__(self, options)


    def _cross_points(self, data: dict, ind2: BaseIndividual, *idx) -> dict:
        assert isinstance(ind2, PermuIndividual), f"ind2 is not a PermuIndividual but a {type(ind2)}"
        idx1, idx2 = idx
        permu = data["permutation"]

        indices = np.empty_like(permu)
        indices[permu] = np.arange(len(permu))

        for i in range(idx1, idx1+abs(idx2-idx1)+1):
            i = i % len(permu)
            if permu[i] != ind2._permutation[i]:
                idx = indices[ind2._permutation[i]]
                permu[i], permu[idx] = permu[idx], permu[i]
        return {"permutation": permu}
