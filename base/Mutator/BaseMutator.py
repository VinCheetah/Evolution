from base.Component.BaseComponent import BaseComponent
from base.Mutator.AbstractMutator import AbstractMutator
from base.Population.BasePopulation import BasePopulation
import numpy as np


class BaseMutator(BaseComponent, AbstractMutator):

    _component_name: str = "Mutator"
    _component_type: str = "Base"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseComponent.__init__(self, options)
        self._mutated_individuals: int = 0
        self._mutations: int = 0
        self._mut_prob: float = options.mutation_prob
        self._multi_mutation: bool = options.multi_mutation
        self._multi_mode: str = options.multi_mutation_mode

    def num_mutated_individuals(self):
        return self._mutated_individuals

    def num_mutation(self):
        return self._mutations

    @BaseComponent.record_time
    def mutate(self, population: BasePopulation):
        """
        Mutate the population
        """
        self._mutated_individuals = 0
        self._mutations = 0
        for individual in population:
            mut_prob = self._mut_prob
            mutation_occured = False
            while mut_prob > np.random.rand():
                self._mutations += 1
                mutation_occured = self._mutate(individual) | mutation_occured
                if self._multi_mutation:
                    match self._multi_mode:
                        case "times":
                            mut_prob = mut_prob * self._mut_prob
                        case "squared":
                            mut_prob = mut_prob ** 2
                        case "linear":
                            pass
                else:
                    break
            if mutation_occured:
                population._sorted = False
                self._mutated_individuals += 1
                individual.has_mutate()

            if self._mut_prob > np.random.rand():
                mutation_occured = self._mutate(individual)
                if mutation_occured:
                    population._sorted = False
                    self._mutated_individuals += 1
                    individual.has_mutate()
