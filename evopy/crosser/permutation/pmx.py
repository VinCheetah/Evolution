from evopy.crosser import BaseCrosser, MultiPointCrosser
from evopy.individual import BaseIndividual, PermuIndividual
import numpy as np


class PermuCrosserPMX(MultiPointCrosser, BaseCrosser):

    _component_type: str = "PMX"
    
    _requirements = {
        "individual": PermuIndividual,
    }   

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        options.num_points = 2
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
            if permu[i] != ind2[i]:
                idx = indices[ind2[i]]
                permu[i], permu[idx] = permu[idx], permu[i]
        data["permutation"] = permu
        return data
