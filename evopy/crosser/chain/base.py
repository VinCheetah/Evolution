""" 
Defines the ChainCrosser class.

This class is a subclass of the MultiPointCrosser and BaseCrosser classes.
It is used to perform the crossover operation on ChainIndividuals.
"""

from evopy.crosser.base import BaseCrosser
from evopy.crosser.multi_point import MultiPointCrosser
from evopy.individual import ChainIndividual


class ChainCrosser(MultiPointCrosser, BaseCrosser):
    """ 
    Base crosser class for ChainIndividuals.
    """

    _component_type = "Chain"
    _requirements = {
        "individual": ChainIndividual,
    }

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        MultiPointCrosser.__init__(self, options, num_points=2)
        BaseCrosser.__init__(self, options)

    def _cross_points(self, data: dict, ind2: ChainIndividual, *idx) -> dict:
        idx1, idx2 = idx
        data["chain"][idx1: idx2] = ind2.get_chain()[idx1: idx2].copy()
        return data
