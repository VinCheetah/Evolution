from base.Population.AbstractPopulation import AbstractPopulation
from base.Component.BaseComponent import BaseComponent
from base.Individual.BaseIndividual import BaseIndividual
from base.utils.options import Options



from typing import Any
import numpy as np
import random as rd
from copy import deepcopy
from numpy.typing import NDArray




class BasePopulation(BaseComponent, AbstractPopulation):

    _component_name: str = "Population"
    _component_type: str = "Base"

    def __init__(self, options: Options):
        BaseComponent.__init__(self, options)

        self._individual_type: type[BaseIndividual] = options.individual
        self._init_size: int = options.size_population
        self._keep_sorted: bool = options.keep_sorted
        self._ascending_order: bool = options.ascending_order
        self._complete_population: bool = options.complete_population
        self._strict_size: bool = options.strict_size
        self._immigration_rate: float = options.immigration_rate

        self._sorted: bool = False
        self._selected: list[BaseIndividual]
        self._population: list[BaseIndividual]
        self._immigrated: int = 0
        self._init_population()

    def update(self, selection):
        self._population = selection
        self._selected_mean = np.mean([ind._fitness for ind in selection])
        for ind in self._population:
            ind.new_generation()
        self.sort()

    def num_immigrated_individuals(self) -> int:
        return self._immigrated

    def _init_evaluation(self):
        if self._complete_population and self._init_size > len(self._population):
            self._sorted = False
            self.log("info", f"Population has been filled with {self._init_size - self.size} random ind")
            for _ in range(self._init_size - self.size):
                self.add_individual(self._individual_type.create(self._options))
            self.update_order()

    def migrate(self):
        self._immigrated = int(self.size * self._immigration_rate)
        if self._immigrated > 0:
            self._sorted = False
            self.log("info", f"Population has been filled with {self._immigrated} random ind (immigration)")
            for _ in range(self._immigrated):
                self.add_individual(self._individual_type.create(self._options))
            self.update_order()

    @property
    def size(self):
        return len(self._population)

    def init(self):
        pass

    def _init_population(self) -> None:
        self._population = [self._individual_type.create(self._options) for _ in range(self._init_size)]
        self._sorted = False

    def update_order(self):
        if self._keep_sorted:
            self.sort()

    def show(self):
        msg = "\nPopulation:\n"
        for ind in self._population:
            msg += f"{ind.report()}\n"
        return msg

    def add_individual(self, individual) -> None:
        if individual._is_valid and self._keep_sorted:
                if self._sorted:
                    idx = self._rank_of_fitness(individual._fitness)
                    self._population.insert(idx, individual)
                else:
                    self._population.append(individual)
                    self.sort()
        else:
            self._sorted = False
            self._population.append(individual)

    def add_individual_from_data(self, data, origin):
        individual = self._individual_type.from_data(self._options, data, origin)
        self.add_individual(individual)

    def _rank_of_fitness(self, fit: float) -> np.intp:
        fitness_values = self._fitness_values()
        if self._ascending_order:
            return np.searchsorted(fitness_values, fit)
        else:
            fitness_values = fitness_values[::-1]
            return self.size - np.searchsorted(fitness_values, fit) - 1

    def sort(self) -> None:
        self._population = self.sort_sample(self._population)
        self._sorted = True
        self.log("info", "Population is sorted")

    def sort_sample(self, sample: list):
        sample_scores = self._fitness_values(sample)
        sorted_idx = self._argsort_scores(sample_scores)
        return [sample[i] for i in sorted_idx]

    def _argsort_scores(self, scores: np.ndarray) -> np.ndarray:
        c_scores = scores
        if not self._ascending_order:
            c_scores = - scores
        return np.argsort(c_scores)

    def _fitness_values(self, sample=None) -> np.ndarray:
        sample = sample if sample is not None else self._population
        return np.array([ind.fitness for ind in sample])

    def keep_sorted(self) -> None:
        self._keep_sorted = True
        if not self._sorted:
            self.sort()

    @property
    def best(self) -> BaseIndividual:
        return self.get_best_ind()

    def get_best_ind(self, sample=None, allow_invalid=False):
        """
        Get the best individual from the population or from the sample
        """
        if sample is None and self._sorted:
            return self._population[0]
        sample = sample if sample is not None else self._population
        extrem_fun = min if self._ascending_order else max
        top = extrem_fun(sample, key=lambda ind: ind.fitness)
        if not allow_invalid and not top._is_valid:
            raise ValueError("No valid individual in the sample")
        return top

    def get_worst_ind(self, sample=None, allow_invalid=False):
        """
        Get the best individual from the population or from the sample
        """
        if sample is None and self._sorted:
            if allow_invalid:
                return self._population[-1]
            for i in range(self.size):
                if self._population[-1-i]._is_valid:
                    return self._population[-1-i]
        sample = sample if sample is not None else self._population
        extrem_fun = max if self._ascending_order else min
        worst = extrem_fun(sample, key=lambda ind: ind.fitness)
        if not allow_invalid and not worst._is_valid:
            raise ValueError("No valid individual in the sample")
        return worst

    def get_random(self, sample=None, n=1) -> list[BaseIndividual]:
        """
        Get n random individuals from the population or from the sample
        """
        sample = sample if sample is not None else self._population
        return rd.choices(self._population, k=n)

    def get_best_inds(self, sample=None, n=1) -> list[BaseIndividual]:
        """
        Get the n top individuals from the population or from the sample
        """
        if sample is None and self._sorted:
            return self._population[:n]
        sample = sample if sample is not None else self._population
        self.sort_sample(sample)
        return sample[:n]

    def exist_valid(self, sample=None) -> bool:
        """
        Check if the sample or the population has valid individuals
        """
        sample = sample if sample is not None else self._population
        fitness_values = self._fitness_values(sample)
        return not all(np.isnan(fitness_values))

    def exist_invalid(self, sample=None) -> bool:
        """
        Check if the sample or the population has invalid individuals
        """
        sample = sample if sample is not None else self._population
        fitness_values = self._fitness_values(sample)
        return any(np.isnan(fitness_values))

    def __iter__(self):
        return iter(self._population)

    def  __getitem__(self, idx):
        return self._population[idx]
