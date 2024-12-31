"""
Defines the BasePopulation class, which is the base class for all populations.
It is a container of individuals.
"""

import random as rd
import numpy as np
from evopy.component import BaseComponent
from evopy.individual import BaseIndividual


class BasePopulation(BaseComponent):
    """
    Base class for all populations. It is a container of individuals.
    """

    BaseComponent.set_component_name("Population")
    BaseComponent.set_component_type("Base")

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseComponent.__init__(self, options)

        self._individual_type: BaseIndividual = options.individual
        self._init_size: int = options.size_population
        self._keep_sorted: bool = options.keep_sorted
        self.ascending_order: bool = options.ascending_order
        self._complete_population: bool = options.complete_population
        self._strict_size: bool = options.strict_size
        self._immigration_rate: float = options.immigration_rate

        self._sorted: bool = False
        self._population: list[BaseIndividual]
        self._immigrated: int = 0
        self._selected_mean: float = 0.
        self._init_population()

    def update(self, selection):
        """
        Update the population with the selected individuals
        """
        self._population = selection
        self._selected_mean = np.mean([ind.fitness for ind in selection])
        for ind in self._population:
            ind.new_generation()
        self.sort()

    def get_selected_mean(self):
        """
        Get the mean of the fitness of the selected individuals
        """
        return self._selected_mean

    def get_init_size(self) -> int:
        """
        Get the initial size of the population
        """
        return self._init_size

    def num_immigrated_individuals(self) -> int:
        """
        Get the number of immigrated individuals
        """
        return self._immigrated

    def init_evaluation(self):
        """
        Initialize the evaluation of the individuals
        """
        if self._complete_population and self._init_size > len(self._population):
            self._sorted = False
            self.log(
                "info", f"Population has been filled with {self._init_size - self.size} random ind"
            )
            for _ in range(self._init_size - self.size):
                self.add_individual(self._individual_type.create(self._options))
            self.update_order()

    def migrate(self):
        """
        Migrate individuals to the population
        """
        self._immigrated = int(self.size * self._immigration_rate)
        if self._immigrated > 0:
            self._sorted = False
            self.log(
                "info",
                f"Population has been filled with {self._immigrated} random ind (immigration)",
            )
            for _ in range(self._immigrated):
                self.add_individual(self._individual_type.create(self._options))
            self.update_order()

    @property
    def size(self):
        """
        Get the size of the population
        """
        return len(self._population)

    def get_population(self):
        """
        Get the population of individuals as a list
        """
        return self._population

    def unsorted(self):
        """
        Set the population as unsorted
        """
        self._sorted = False

    def is_sorted(self):
        """
        Check if the population is sorted
        """
        return self._sorted

    def _init_population(self) -> None:
        """
        Initialize the population with the initial size
        """
        self._population = [
            self._individual_type.create(self._options) for _ in range(self._init_size)
        ]
        self._sorted = False

    def update_order(self):
        """
        Update the order of the population
        """
        if self._keep_sorted:
            self.sort()

    def show(self):
        """
        Show the population
        """
        msg = "\nPopulation:\n"
        for ind in self._population:
            msg += f"{ind.report()}\n"
        return msg

    def add_individual(self, individual) -> None:
        """
        Add an individual to the population
        """
        if individual.is_valid and self._keep_sorted:
            if self._sorted:
                idx = self._rank_of_fitness(individual.fitness)
                self._population.insert(idx, individual)
            else:
                self._population.append(individual)
                self.sort()
        else:
            self._sorted = False
            self._population.append(individual)

    def add_individual_from_data(self, data, origin):
        """
        Add an individual to the population from data
        """
        individual = self._individual_type.from_data(self._options, data, origin)
        self.add_individual(individual)

    def _rank_of_fitness(self, fit: float) -> np.intp:
        """
        Get the rank of the fitness in the population
        """
        fitness_values = self.fitness_values()
        if self.ascending_order:
            return np.searchsorted(fitness_values, fit)
        fitness_values = fitness_values[::-1]
        return self.size - np.searchsorted(fitness_values, fit) - 1

    def sort(self) -> None:
        """
        Sort the population by fitness
        """
        self._population = self.sort_sample(self._population)
        self._sorted = True
        self.log("info", "Population is sorted")

    def sort_sample(self, sample: list):
        """
        Sort a sample of individuals by fitness
        """
        sample_scores = self.fitness_values(sample)
        sorted_idx = self.argsort_scores(sample_scores)
        return [sample[i] for i in sorted_idx]

    def argsort_scores(self, scores: np.ndarray) -> np.array:
        """
        Get the indices of the sorted scores
        """
        c_scores = scores
        if not self.ascending_order:
            c_scores = -scores
        return np.argsort(c_scores)

    def fitness_values(self, sample=None) -> np.array:
        """
        Get the fitness values of the sample or the population
        """
        sample = sample if sample is not None else self._population
        return np.array([ind.fitness for ind in sample])

    def keep_sorted(self) -> None:
        """
        Keep the population sorted
        """
        self._keep_sorted = True
        if not self._sorted:
            self.sort()

    @property
    def best(self) -> BaseIndividual:
        """
        Get the best individual from the population
        """
        return self.get_best_ind()

    def get_best_ind(self, sample=None, allow_invalid=False):
        """
        Get the best individual from the population or from the sample
        """
        if sample is None and self._sorted:
            return self._population[0]
        sample = sample if sample is not None else self._population
        extrem_fun = min if self.ascending_order else max
        top = extrem_fun(sample, key=lambda ind: ind.fitness)
        if not allow_invalid and not top.is_valid:
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
                if self._population[-1 - i].is_valid:
                    return self._population[-1 - i]
        sample = sample if sample is not None else self._population
        extrem_fun = max if self.ascending_order else min
        worst = extrem_fun(sample, key=lambda ind: ind.fitness)
        if not allow_invalid and not worst.is_valid:
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
        fitness_values = self.fitness_values(sample)
        return not all(np.isnan(fitness_values))

    def exist_invalid(self, sample=None) -> bool:
        """
        Check if the sample or the population has invalid individuals
        """
        sample = sample if sample is not None else self._population
        fitness_values = self.fitness_values(sample)
        return any(np.isnan(fitness_values))

    def __iter__(self):
        return iter(self._population)

    def __getitem__(self, idx):
        return self._population[idx]
