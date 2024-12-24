from evopy.mutator import ChainMutator
from evopy.individual import BinaryChainIndividual
import numpy as np


class BinaryChainMutator(ChainMutator):

    _component_type = "BinaryChain"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        super().__init__(options)

    def _mutate(self, individual) -> bool:
        assert isinstance(individual, BinaryChainIndividual)
        idx: int = np.random.randint(0, len(individual)-1)
        individual.flip(idx)
        return True
