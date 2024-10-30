from base.Individual.GraphicReprIndividual import GraphicReprIndividual
from base.Individual.PermuIndividual import PermuIndividual
import matplotlib.pyplot as plt

class SalesManIndividual(PermuIndividual, GraphicReprIndividual):

    _component_type: str = "SalesMan"

    def __init__(self, options, **kwargs):
        options.has_graph_repr = True
        options.update(kwargs)
        PermuIndividual.__init__(self, options)
        self.cities = options.cities

    def plot(self, ax) -> None:
        ax.clear()
        ax.plot(*self.get_graph_repr(), color='tab:blue')

    @classmethod
    def init_plot(cls, ax) -> None:
        cls.set_limits(ax, 0, 1, 0, 1)
        ax.autoscale_view()

    def get_graph_repr(self):
        X = [(self.cities[self[i]][0], self.cities[self[(i+1)%self._size]][0]) for i in range(len(self))]
        Y = [(self.cities[self[i]][1], self.cities[self[(i+1)%self._size]][1]) for i in range(len(self))]
        return X, Y
