from base.Crosser.BaseCrosser import BaseCrosser
from base.Crosser.MultiPointCrosser import MultiPointCrosser
from base.Individual.BaseIndividual import BaseIndividual
from base.Individual.ChainIndividual import ChainIndividual
import numpy as np


class ChainCrosser(MultiPointCrosser, BaseCrosser):

    _component_type = "Chain"

    def __init__(self, options, **kwargs):
        options.num_points = 2
        options.update(kwargs)

        MultiPointCrosser.__init__(self, options)
        BaseCrosser.__init__(self, options)

    def _cross_points(self, data: dict, ind2: BaseIndividual, *idx) -> dict:
        assert isinstance(ind2, ChainIndividual)
        idx1, idx2 = idx
        data["chain"][idx1: idx2] = ind2._chain[idx1: idx2].copy()
        return data
