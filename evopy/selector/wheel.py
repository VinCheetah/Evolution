"""
Defines the WheelSelector class.
This class is used to select individuals by wheel.
"""

import random as rd
import numpy as np
from evopy.selector.base import BaseSelector
from evopy.population import BasePopulation


class WheelSelector(BaseSelector):
    """
    This is the Wheel selector.
    Selects individuals by wheel.

    Parameters:
        * wheel_selection_mode (str): The function used to determine the probabilities to pick individuals
            Choices: softmax, linear, power
        * wheel_power (int): The power chosen to determine the probabilities to pick individuals. It is used only for 'power' mode
            Min: 1
    """

    component_type: str = "Wheel"
    _single_select: bool = True

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        super().__init__(options)
        self._mode: str = self._options.wheel_selection_mode
        self._power: int = self._options.wheel_power
        self._min_fit: float
        self._max_fit: float
        self.wheel_values: np.ndarray = ...
        self.fitness_values: np.ndarray = ...
        self.wheel: np.ndarray = ...

    def _init_selection(self, population: BasePopulation):
        """
        Initialize the selection.
        """
        super()._init_selection(population)
        self.fitness_values = population.fitness_values()
        if population.ascending_order:
            self.fitness_values = -self.fitness_values
        self.init_wheel()

    def init_wheel(self):
        """
        Initialize the wheel.
        """
        match self._mode:
            case "softmax":
                self.wheel_values = np.exp(self.fitness_values)
            case "linear":
                self._min_fit = np.min(self.fitness_values)
                self._max_fit = np.max(self.fitness_values)
                self.wheel_values = (self.fitness_values - self._min_fit) / (
                    self._max_fit - self._min_fit
                )
            case "power":
                self._min_fit = np.min(self.fitness_values)
                self._max_fit = np.max(self.fitness_values)
                self.wheel_values = (self.fitness_values - self._min_fit) / (
                    self._max_fit - self._min_fit
                )
                self.wheel_values = np.power(self.wheel_values, self._power)
            case _:
                raise ValueError(f"Wheel selection mode {self._mode} not recognized")
        self.create_wheel()

    def create_wheel(self):
        """
        Create the wheel.
        """
        self.wheel = np.cumsum(self.wheel_values)
        self.wheel /= self.wheel[-1]

    def single_select(self, idx: int, population: BasePopulation):
        """
        Select an individual by wheel.
        """
        chosen = np.searchsorted(self.wheel, rd.random())
        return population[chosen], True
