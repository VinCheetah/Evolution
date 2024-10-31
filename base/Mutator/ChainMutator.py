from typing import ChainMap
from base.Mutator.BaseMutator import BaseMutator
from base.Individual.Chain.ChainIndividual import ChainIndividual
import numpy as np
import builtins


class ChainMutator(BaseMutator):

    _component_type = "Chain"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        super().__init__(options)

    def _mutate(self, individual: ChainIndividual) -> bool:
        idx = np.random.randint(0, len(individual)-1)
        match individual._type_value:
            case builtins.int:
                new_val = np.random.randint(individual._min_value, individual._max_value)
            case builtins.float:
                new_val = np.random.uniform(individual._min_value, individual._max_value)
            case _:
                raise NotImplementedError
        previous = individual[idx]
        individual[idx] = new_val
        return previous != new_val
