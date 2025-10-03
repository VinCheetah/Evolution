"""
Defines the base class for mutators
"""

from abc import abstractmethod
from typing import Callable

import numpy as np
from evopy.component import BaseComponent
from evopy.population import BasePopulation
from evopy.individual import BaseIndividual


class BaseMutator(BaseComponent):
    """
    Base class for mutators

    Parameters:
        * individual_size (int): The size of an individual
            Min: 0
        * mutation_prob (float): Probability of mutation
            Min: 0
            Max: 1
        * multi_mutation (bool): Whether mutations can be performed multiple times on the same individual
        * multi_mutation_mode (str): The mode of choosing probability to consider mutate the same individual another time. Used only when multi_mutation is True
            Choices: times, squared, linear
    """

    component_name: str = "Mutator"
    component_type: str = "Base"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseComponent.__init__(self, options)
        self._size: int = self._options.individual_size
        self._mutated_individuals: int = 0
        self._mutations: int = 0
        self._mut_prob: float = self._options.mutation_prob
        self._multi_mutation: bool = self._options.multi_mutation
        self._multi_mode: str = self._options.multi_mutation_mode

    @BaseComponent.record_time
    def mutate(self, population: BasePopulation):
        """
        Mutate the population
        Each individual is mutated with a probability 'mut_prob'
        An individual can be mutated multiple times if 'multi_mutation' is True
        The number of mutations per individual can be controlled by 'multi_mode'
        """
        self._mutated_individuals = 0
        self._mutations = 0
        for individual in population:
            has_mutate = self._apply_mutation(individual)
            if has_mutate:
                population.unsorted()
                self._mutated_individuals += 1
                individual.has_mutate()

    def _apply_mutation(self, individual: BaseIndividual) -> bool:
        return self._apply_mut(individual, self._mut_prob, self._mutate)

    def _apply_mut(self, individual: BaseIndividual, mutation_prob: float, mut_func: Callable) -> bool:
        has_mutate = False
        mut_prob = mutation_prob
        while mut_prob > np.random.rand():
            self._mutations += 1
            has_mutate |= mut_func(individual)
            if self._multi_mutation:
                mut_prob = self._update_mut_prob(mut_prob, mutation_prob)
            else:
                break
        return has_mutate

    def _update_mut_prob(self, mut_prob: float, original_mut_prob: float) -> float:
        match self._multi_mode:
            case "times":
                mut_prob = mut_prob * original_mut_prob
            case "squared":
                mut_prob = mut_prob ** 2
            case "linear":
                pass
        return mut_prob

    @abstractmethod
    def _mutate(self, individual: BaseIndividual) -> bool:
        """
        Mutate an individual

        Parameters
        ----------
        individual : BaseIndividual
            The individual to mutate

        Returns
        -------
        bool
            True if the individual has been mutated, False otherwise
        """

    def num_mutation(self):
        """
        Returns the number of mutations performed during the last call to the mutate method.
        """
        return self._mutations

    def num_mutated_individuals(self):
        """
        Returns the number of individuals mutated during the last call to the mutate method.
        """
        return self._mutated_individuals
