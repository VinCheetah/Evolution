from evopy.individual import BaseIndividual
from evopy.mutator import BaseMutator
from typing import Callable


class SuccessiveMutator(BaseMutator):

    def __init__(self, options):
        super().__init__(options)
        self.successive_functions: list[tuple[float, Callable]] = []

    def _apply_mutation(self, individual: BaseIndividual) -> bool:
        has_mutated = False
        for prob, func in self.successive_functions:
            has_mutated |= self._apply_mut(individual, prob, func)
        return has_mutated

    def _mutate(self, individual: BaseIndividual) -> bool:
        """
        Unused function
        """
        pass
