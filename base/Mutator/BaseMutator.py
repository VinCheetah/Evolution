from base.Component.BaseComponent import BaseComponent
from base.Mutator.AbstractMutator import AbstractMutator
import numpy as np


class BaseMutator(BaseComponent, AbstractMutator):

    _component_name: str = "Mutator"
    _component_type: str = "Base"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseComponent.__init__(self, options)
        self._mutated_individuals: int = 0
        self._mut_prob: float = options.mutation_prob

    def num_mutated_individuals(self):
        return self._mutated_individuals

    @BaseComponent.record_time
    def mutate(self, population):
        """
        Mutate the population
        """
        self._mutated_individuals = 0
        for individual in population:
            if self._mut_prob > np.random.rand():
                mutation_occured = self._mutate(individual)
                if mutation_occured:
                    self._mutated_individuals += 1
                    individual.has_mutate()
