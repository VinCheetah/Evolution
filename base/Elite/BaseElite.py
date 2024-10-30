from base.Component.BaseComponent import BaseComponent
from base.Elite.AbstractElite import AbstractElite
from base.Individual.BaseIndividual import BaseIndividual
from base.Population.BasePopulation import BasePopulation
import numpy as np
import numpy.typing as npt


class BaseElite(BaseComponent, AbstractElite):

    _component_name: str = "Elite"
    _component_type: str = "Base"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseComponent.__init__(self, options)
        self._elite_size: int = options.elite_size
        self._elite: list[BaseIndividual] = []
        self._elite_scores: npt.NDArray[np.float_] = np.array([])

    def update(self, population: BasePopulation) -> bool:
        prev_top = None if len(self) == 0 else self.best
        population.sort()
        outsiders_scores = np.array([self._compute_score(ind) for ind in population])
        complete_scores = np.concatenate((outsiders_scores, self._elite_scores))
        sorted_idx = population._argsort_scores(complete_scores)

        self._elite = [(population[i].copy() if i < population.size else self[i-population.size]) for i in sorted_idx[:self._elite_size]]
        self._elite_scores = complete_scores[sorted_idx[:self._elite_size]]
        assert prev_top is None or self.best.fitness <= prev_top.fitness, f"Elite score decreased from {prev_top.fitness} to {self.best.fitness}"
        for i in range(self._elite_size):
            assert self._elite_scores[i] == self._elite[i].fitness, f"Elite n°{i} has score of {self._elite_scores[i]}, but score n°{i} is {self._compute_score(self._elite[i])}"
        return self.best != prev_top

    def __getitem__(self, idx) -> BaseIndividual:
        return self._elite[idx]

    def __len__(self) -> int:
        return len(self._elite)

    @property
    def best(self) -> BaseIndividual:
        return self[0]

    def show(self):
        msg = f"Elite:"
        for ind in self._elite:
            msg += f"\n{ind._id}: {ind.fitness:.3f}"
        return msg

    def _compute_score(self, ind) -> float:
        return ind.fitness
