from base.Evaluator.PermuEvaluator import PermuEvaluator
from base.Evaluator.GraphicReprEvaluator import GraphicReprEvaluator
from base.Individual.Permutation.PermuIndividual import PermuIndividual
import numpy as np
import numpy.typing as npt
import random as rd


class SalesManEvaluator(PermuEvaluator, GraphicReprEvaluator):

    _component_type: str = "SalesMan"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        self.cities = options.cities or self.create_cities(options.individual_size)
        options.cities = self.cities
        options.weights = self.create_weights()
        options.individual_size = len(self.cities)
        PermuEvaluator.__init__(self, options)
        GraphicReprEvaluator.__init__(self, options)

    def create_cities(self, size) -> npt.NDArray:
        return np.array([(rd.random(), rd.random()) for _ in range(size)])

    def create_weights(self) -> npt.NDArray:
        size = len(self.cities)
        distances = [[0] * size for _ in range(size)]
        for i in range(size):
            for j in range(i + 1, size):
                distances[i][j] = distances[j][i] = ((self.cities[i][0] - self.cities[j][0]) ** 2 + (self.cities[i][1] - self.cities[j][1]) ** 2) ** .5
        return np.array(distances)

    def plot(self, ax, individual: PermuIndividual) -> None:
        curves = self.get_curves(ax)
        path = curves["path"]
        X = self.cities[[*individual._permutation, individual._permutation[0]]][:, 0]
        Y = self.cities[[*individual._permutation, individual._permutation[0]]][:, 1]
        path.set_data(X, Y)

    def init_plot(self, ax) -> None:
        ax.clear()
        ax.scatter(*zip(*self.cities), color='tab:blue')
        self.set_limits(ax, 0, 1, 0, 1)
        self.set_curves(ax, {"path": ax.plot([], [],)[0]})
        ax.autoscale_view()
