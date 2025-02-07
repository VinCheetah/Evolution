"""
Defines the base class for the Elite component.
The elite component is responsible for storing the best individuals ever seen by the algorithm.
"""

import numpy as np
from evopy.component import BaseComponent
from evopy.individual import BaseIndividual
from evopy.population import BasePopulation


class BaseElite(BaseComponent):
    """
    Base class for the Elite component.

    Parameters:
        * elite_size (int): The number of individuals in the elite set.
            Min: 0
    """

    BaseComponent.set_component_name("Elite")
    BaseComponent.set_component_type("Base")

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseComponent.__init__(self, options)
        self._elite_size: int = options.elite_size
        self._elite: list[BaseIndividual] = []
        self._elite_scores: np.ndarray = np.array([])

    def update(self, population: BasePopulation):
        """
        Update the elite with the best individuals from the population
        """
        population.sort()
        outsiders_scores = np.array([self._compute_score(ind) for ind in population])
        complete_scores = np.concatenate((outsiders_scores, self._elite_scores))
        sorted_idx = population.argsort_scores(complete_scores)

        self._elite = [
            (population[i].copy() if i < population.size else self[i - population.size])
            for i in sorted_idx[: self._elite_size]
        ]
        self._elite_scores = complete_scores[sorted_idx[: self._elite_size]]

    @property
    def best(self) -> BaseIndividual:
        """
        Return the best individual in the elite
        """
        return self[0]

    def show(self):
        """
        Return a string representation of the elite
        """
        msg = "Elite:"
        for ind in self._elite:
            msg += f"\n{ind.get_id()}: {ind.fitness:.3f}"
        return msg

    def _compute_score(self, ind) -> float:
        """
        Compute the score of an individual, used to sort the elite
        """
        return ind.fitness

    def __getitem__(self, idx) -> BaseIndividual:
        return self._elite[idx]

    def __len__(self) -> int:
        return len(self._elite)
