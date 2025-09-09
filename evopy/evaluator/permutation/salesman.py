"""
Define the SalesManEvaluator class.
This class is a subclass of the PermuEvaluator and GraphicReprEvaluator classes.
"""

import random as rd
import numpy as np
from evopy.evaluator.permutation.base import PermuEvaluator
from evopy.evaluator.graphic import GraphicReprEvaluator
from evopy.individual import PermuIndividual
from evopy.utils.evo_types import Random


class SalesManEvaluator(PermuEvaluator, GraphicReprEvaluator):
    """
    This is the SalesManEvaluator class.
    This class is a subclass of the PermuEvaluator and GraphicReprEvaluator classes.
    """

    component_type = "SalesMan"

    @classmethod
    def fixed_options(cls, options):
        
        if cls.is_random(options.cities):
            return cls.create_cities()

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        super().__init__(options)
        self.cities = options.cities if options.cities == Random else self.create_cities(options.individual_size)
        options.cities = self.cities
        self.weights = options.weights = self.create_weights()
        options.individual_size = len(self.cities)

    def _evaluate_permu(self, permutation: list):
        tot = 0
        for idx in range(len(permutation) - 1):
            tot += self.weights[permutation[idx]][permutation[idx + 1]]
        tot += self.weights[permutation[-1]][permutation[0]]
        return tot

    def create_cities(self, size) -> np.array:
        """
        Create a random array of cities, in a 2D space of size 1x1
        """
        return np.array([(rd.random(), rd.random()) for _ in range(size)])

    def create_weights(self) -> np.array:
        """
        Create the distance matrix between the cities.
        """
        size = len(self.cities)
        distances = [[0] * size for _ in range(size)]
        for i in range(size):
            c1x, c1y = self.cities[i]
            for j in range(i + 1, size):
                c2x, c2y = self.cities[j]
                distances[i][j] = distances[j][i] = ((c1x - c2x)** 2 + (c1y - c2y)** 2)** 0.5
        return np.array(distances)

    def plot(self, ax, individual: PermuIndividual) -> None:
        curves = self.get_curves(ax)
        path = curves["path"]
        permutation = individual.get_permutation()
        x = self.cities[[*permutation, permutation[0]]][:, 0]
        y = self.cities[[*permutation, permutation[0]]][:, 1]
        path.set_data(x, y)

    def init_plot(self, ax) -> None:
        ax.clear()
        ax.scatter(*zip(*self.cities), color="tab:blue")
        self.set_limits(ax, 0, 1, 0, 1)
        self.set_curves(ax, {"path": ax.plot([], [])[0]})
        ax.autoscale_view()
