"""
Defines the BinaryChainMutator class, which is a subclass of ChainMutator.
This class is used to mutate BinaryChainIndividuals.
"""

import numpy as np
from evopy.mutator.chain.base import ChainMutator
from evopy.individual import BinaryChainIndividual


class BinaryChainMutator(ChainMutator):
    """
    This is the BinaryChainMutator class.
    This mutator flip the value of a single element in the chain.

    Parameters:
    """

    ChainMutator.set_component_type("BinaryChain")
    ChainMutator.add_requirement("individual", BinaryChainIndividual)

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        super().__init__(options)

    def _mutate(self, individual) -> bool:
        assert isinstance(individual, BinaryChainIndividual)
        idx: int = np.random.randint(0, len(individual) - 1)
        individual.flip(idx)
        return True
