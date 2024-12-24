from evopy.mutator import BaseMutator
from evopy.individual import PermuIndividual
import numpy as np


class PermuMutator(BaseMutator):

    mutation_modes = ["multi", "single", "swap", "reverse", "shuffle"]

    def __init__(self, options, **kwargs):
        self._mutate_mode = (self.mutation_modes + ["random"])[-1]
        options.update(kwargs)
        super().__init__(options)
        self._individual_size: int = options.individual_size

    def _mutate(self, individual) -> bool:
        mode = np.random.choice(self.mutation_modes) if self._mutate_mode == "random" else self._mutate_mode
        match mode:
            case "multi":
                return self._mutate_multi(individual)
            case "single":
                return self._mutate_single(individual)
            case "swap":
                return self._mutate_swap(individual)
            case "reverse":
                return self._mutate_reverse(individual)
            case "shuffle":
                return self._mutate_shuffle(individual)
            case _:
                raise ValueError(f"Unknown mutation mode {self._mutate_mode} (random: {self._mutate_mode == 'random'})")

    def _mutate_multi(self, individual: PermuIndividual) -> bool:
        idx = np.random.randint(0, self._individual_size-1)
        length = np.random.randint(1, self._individual_size - 2)
        dec = np.random.randint(1, self._individual_size - length - 1)
        reverse = np.random.rand() > 0.5
        return individual.move_elements(idx, dec, length, reverse)

    def _mutate_single(self, individual: PermuIndividual) -> bool:
        idx, new_pos = np.random.randint(0, self._individual_size-1, size=2)
        return individual.move_element(idx, new_pos)

    def _mutate_reverse(self, individual: PermuIndividual) -> bool:
        idx1, idx2 = np.random.randint(0, self._individual_size-1, size=2)
        return individual.reverse(min(idx1, idx2), max(idx1, idx2))

    def _mutate_shuffle(self, individual: PermuIndividual) -> bool:
        idx1, idx2 = np.random.randint(0, self._individual_size-1, size=2)
        return individual.shuffle(min(idx1, idx2), max(idx1, idx2))

    def _mutate_swap(self, individual: PermuIndividual) -> bool:
        idx1, idx2 = np.random.randint(0, self._individual_size-1, size=2)
        return individual.swap(idx1, idx2)
