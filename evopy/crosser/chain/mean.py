""" 
Defines the MeanChainCrosser class.
This class is a subclass of the ChainCrosser class.
The crossover operation is performed by taking the mean of the two chains.
"""

import builtins
import numpy as np
from evopy.crosser.chain.base import ChainCrosser
from evopy.individual import ChainIndividual


class MeanChainCrosser(ChainCrosser):
    """ 
    MeanChainCrosser class.
    This class is a subclass of the ChainCrosser class.
    The crossover operation is performed by taking the mean of the two chains.
    """

    _component_type = "MeanChain"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        ChainCrosser.__init__(self, options)
        self._type_value = options.type_value

    def _cross(self, ind1: ChainIndividual, ind2: ChainIndividual) -> dict:
        match self._type_value:
            case builtins.int:
                chain = np.round((ind1.get_chain() + ind2.get_chain()) / 2).astype(int)
            case builtins.float:
                chain = (ind1.get_chain() + ind2.get_chain()) / 2
            case _:
                raise ValueError(f"Invalid type value {self._type_value}")
        return {"chain": chain}
