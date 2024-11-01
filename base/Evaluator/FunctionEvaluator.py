from matplotlib import colors
from base.Evaluator.GraphicReprEvaluator import GraphicReprEvaluator
from base.Evaluator.SingleEvaluator import SingleEvaluator
from base.Individual.Chain.ChainIndividual import ChainIndividual
import numpy as np


class FunctionEvaluator(SingleEvaluator, GraphicReprEvaluator):

    _component_type: str = "Function"

    def __init__(self, options, **kwargs):
        #if options.individual_size == 2:
        #    options.repr3D = True
        options.update(kwargs)
        SingleEvaluator.__init__(self, options)
        GraphicReprEvaluator.__init__(self, options)
        self._graph_num_points = 1000
        self._individual_size = options.individual_size
        self._function = options.function
        self._min_value = options.min_value
        self._max_value = options.max_value

    def _evaluate(self, individual: ChainIndividual) -> float:
        return self._function(*individual._chain)

    def plot(self, ax, individual) -> None:
        curves = self.get_curves(ax)
        for i in range(self._individual_size):
            func = lambda x: self._function(*individual._chain[:i], x, *individual._chain[i+1:])
            curves[f"point-{i}"].set_data(individual._chain[i], self._function(*individual._chain))
            curves[f"unfixed-{i}"].set_ydata(func(self.X))
        ax.relim()
        ax.autoscale_view()

        #elif self._individual_size == 2:
        #    self.get_curves(ax)["point"].set_data(*individual._chain)
        #    self.get_curves(ax)["point"].set_3d_properties(self._function(*individual._chain))
        #else:
        #    raise ValueError("Invalid individual size")

    def init_plot(self, ax) -> None:
        ax.clear()
        #self.set_limits(ax, self._min_value, self._max_value, -10, 10)
        self.X = np.linspace(self._min_value, self._max_value, self._graph_num_points)
        Y = np.zeros(self._graph_num_points)
        curves = {}
        for i in range(self._individual_size):
            curves[f"unfixed-{i}"] = ax.plot(self.X, self.X)[0]
            curves[f"point-{i}"] = ax.plot(0, 0, marker="o", color=curves[f"unfixed-{i}"].get_color())[0]
        self.set_curves(ax, curves)


        #elif self._individual_size == 2:
        #    x = np.linspace(self._min_value, self._max_value, 100)
        #    y = np.linspace(self._min_value, self._max_value, 100)
        #    X, Y = np.meshgrid(x, y)
        #    Z = self._function(X, Y)
        #    ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
        #    self.set_curves(ax, {"point": ax.plot(self._min_value, self._min_value, self._function(self._min_value, self._min_value), color="blue", marker="o")[0]})
