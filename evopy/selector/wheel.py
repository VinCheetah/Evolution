from evopy.selector import BaseSelector
from evopy.population.base import BasePopulation
import numpy as np
import random as rd


class WheelSelector(BaseSelector):

    _component_type: str = "Tournament"
    _single_select: bool = True

    def __init__(self, options):
        super().__init__(options)
        self._mode: str = options.wheel_selection_mode
        self._power: int = options.wheel_power

    def _init_selection(self, population: BasePopulation):
        super()._init_selection(population)
        self.fitness_values = population._fitness_values()
        if population._ascending_order:
            self.fitness_values = -self.fitness_values
        self.init_wheel(population)

    def init_wheel(self, population: BasePopulation):
        match self._mode:
            case "softmax":
                self.wheel_values = np.exp(self.fitness_values)
            case "linear":
                self._min_fit = np.min(self.fitness_values)
                self._max_fit = np.max(self.fitness_values)
                self.wheel_values = (self.fitness_values - self._min_fit) / (self._max_fit - self._min_fit)
            case "power":
                self._min_fit = np.min(self.fitness_values)
                self._max_fit = np.max(self.fitness_values)
                self.wheel_values = (self.fitness_values - self._min_fit) / (self._max_fit - self._min_fit)
                self.wheel_values = np.power(self.wheel_values, self._power)
            case _:
                raise ValueError(f"Wheel selection mode {self._mode} not recognized")
        self.create_wheel()

    def create_wheel(self):
        self.wheel = np.cumsum(self.wheel_values)
        self.wheel /= self.wheel[-1]

    def single_select(self, idx: int, population: BasePopulation):
        chosen = np.searchsorted(self.wheel, rd.random())
        return population[chosen], True
