"""
Defines the base class for permutation mutators: PermuMutator.
This class is a subclass of BaseMutator.
"""

import numpy as np
from evopy.mutator.multi_mutator import MultiMutator
from evopy.individual import PermuIndividual


class PermuMutator(MultiMutator):
    """
    Base class for permutation mutators.
    """

    mutation_modes = ["multi", "single", "swap", "reverse", "shuffle"]
    MultiMutator.set_component_type("Permutation")
    MultiMutator.add_requirement("individual", PermuIndividual)

    def __init__(self, options, **kwargs):
        self._mutate_mode = (self.mutation_modes + ["random"])[-1]
        options.update(kwargs)
        MultiMutator.__init__(self, options)

    @MultiMutator.add_mutation_func()
    def _mutate_multi(self, individual: PermuIndividual) -> bool:
        """
        Mutate the individual by moving a subsequence of elements to a new position.
        """
        idx = np.random.randint(0, self._size - 1)
        length = np.random.randint(1, self._size - 2)
        dec = np.random.randint(1, self._size - length - 1)
        reverse = np.random.rand() > 0.5
        return individual.move_elements(idx, dec, length, reverse)

    @MultiMutator.add_mutation_func()
    def _mutate_single(self, individual: PermuIndividual) -> bool:
        """
        Mutate the individual by moving a single element to a new position.
        """
        idx, new_pos = np.random.randint(0, self._size - 1, size=2)
        return individual.move_element(idx, new_pos)

    @MultiMutator.add_mutation_func()
    def _mutate_reverse(self, individual: PermuIndividual) -> bool:
        """
        Mutate the individual by reversing a subsequence of elements.
        """
        idx1, idx2 = np.random.randint(0, self._size - 1, size=2)
        return individual.reverse(min(idx1, idx2), max(idx1, idx2))

    @MultiMutator.add_mutation_func()
    def _mutate_shuffle(self, individual: PermuIndividual) -> bool:
        """
        Mutate the individual by shuffling a subsequence of elements.
        """
        idx1, idx2 = np.random.randint(0, self._size - 1, size=2)
        return individual.shuffle(min(idx1, idx2), max(idx1, idx2))

    @MultiMutator.add_mutation_func()
    def _mutate_swap(self, individual: PermuIndividual) -> bool:
        """
        Mutate the individual by swapping two elements.
        """
        idx1, idx2 = np.random.randint(0, self._size - 1, size=2)
        return individual.swap(idx1, idx2)
