"""
Defines the base class for mutators
"""

from abc import abstractmethod
import numpy as np
from evopy.component import BaseComponent
from evopy.population import BasePopulation
from evopy.individual import BaseIndividual


class BaseMutator(BaseComponent):
    """
    Base class for mutators
    """

    BaseComponent.set_component_name("Mutator")
    BaseComponent.set_component_type("Base")

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseComponent.__init__(self, options)
        self._size: int = options.individual_size
        self._mutated_individuals: int = 0
        self._mutations: int = 0
        self._mut_prob: float = options.mutation_prob
        self._multi_mutation: bool = options.multi_mutation
        self._multi_mode: str = options.multi_mutation_mode

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
                            mut_prob = mut_prob**2
                        case "linear":
                            pass
                else:
                    break
            if mutation_occured:
                population.unsorted()
                self._mutated_individuals += 1
                individual.has_mutate()

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
