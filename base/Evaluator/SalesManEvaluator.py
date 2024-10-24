from base.Evaluator.PermuEvaluator import PermuEvaluator
import numpy as np
import numpy.typing as npt
import random as rd


class SalesManEvaluator(PermuEvaluator):

    _component_type: str = "SalesMan"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        self.cities = options.cities or self.create_cities(options.individual_size)
        options.cities = self.cities
        options.weights = self.create_weights()
        options.individual_size = len(self.cities)

        super().__init__(options)

    def create_cities(self, size) -> npt.NDArray:
        return np.array([(rd.random(), rd.random()) for _ in range(size)])

    def create_weights(self) -> npt.NDArray:
        size = len(self.cities)
        distances = [[0] * size for _ in range(size)]
        for i in range(size):
            for j in range(i + 1, size):
                distances[i][j] = distances[j][i] = ((self.cities[i][0] - self.cities[j][0]) ** 2 + (self.cities[i][1] - self.cities[j][1]) ** 2) ** .5
        return np.array(distances)
