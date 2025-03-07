""" 
Defines the ChainMutator class, which is used to mutate ChainIndividuals.
This class is a subclass of BaseMutator.
"""

import builtins
import numpy as np
from evopy.mutator.base import BaseMutator
from evopy.individual import ChainIndividual


class ChainMutator(BaseMutator):
    """
    Mutator for ChainIndividuals.
    This mutator changes the value of a single element in the chain.

    Parameters:
    """

    component_type: str = "Chain"
    requirements = [("individual", ChainIndividual)]

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        super().__init__(options)

    def _mutate(self, individual: ChainIndividual) -> bool:
        if len(individual) > 1:
            idx = np.random.randint(0, len(individual) - 1)
        else:
            idx = 0
        match individual.get_type():
            case builtins.int:
                new_val = np.random.randint(*individual.get_bounds())
            case builtins.float:
                new_val = np.random.uniform(*individual.get_bounds())
            case _:
                raise NotImplementedError
        previous = individual[idx]
        individual[idx] = new_val
        return previous != new_val
