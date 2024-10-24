from base.Individual.PermuIndividual import PermuIndividual
import matplotlib.pyplot as plt

class SalesManIndividual(PermuIndividual):

    _component_type: str = "SalesMan"

    def __init__(self, options, **kwargs):
        options.has_graph_repr = True
        options.update(kwargs)
        PermuIndividual.__init__(self, options)
        self.cities = options.cities

    def get_graph_repr(self):
        X = [(self.cities[self[i]][0], self.cities[self[(i+1)%self._size]][0]) for i in range(len(self))]
        Y = [(self.cities[self[i]][1], self.cities[self[(i+1)%self._size]][1]) for i in range(len(self))]
        return X, Y

    def to_graph(self):
        plt.plot(*self.get_graph_repr())
        plt.show()
