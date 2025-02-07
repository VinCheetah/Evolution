"""
Define the FunctionEvaluator class.
This class is a subclass of the ChainEvaluator class.
This evaluator is used to evaluate a function.
"""

from typing import Union, Callable
import numpy as np
from evopy.evaluator.chain.base import ChainEvaluator
from evopy.evaluator.graphic import GraphicReprEvaluator


class FunctionEvaluator(ChainEvaluator, GraphicReprEvaluator):
    """
    This is the FunctionEvaluator class.

    Parameters:
        * individual_size (int): The size of the individual to be evaluated
            Min: 0
        * function (Callable): The function to be evaluated
        * min_value (float): The minimum value on which to evaluate the function
        * max_value (float): The maximum value on which to evaluate the function
        * allow3D (bool): Whether the function is represented in 3D space
    """

    ChainEvaluator.set_component_type("Function")

    def __init__(self, options, **kwargs):
        ind_size: int = options.individual_size
        if options.allow3D and options.individual_size == 2:
            options.repr3D = True
        options.update(kwargs)
        ChainEvaluator.__init__(self, options)
        GraphicReprEvaluator.__init__(self, options)
        self._graph_num_points = 1000
        self._function: Callable = self._options.function
        self._min_value: Union[float, int] = self._options.min_value
        self._max_value: Union[float, int] = self._options.max_value
        self._x = None

    def _evaluate_chain(self, chain: list) -> float:
        return self._function(*chain)

    def plot(self, ax, individual) -> None:
        if self._options.repr3D:
            self.plot_2d(ax, individual)
            return

        curves = self.get_curves(ax)
        chain = individual.get_chain()
        for idx in range(self.ind_size(individual)):
            curves[f"point-{idx}"].set_data(chain[idx], self._function(*chain))
            y_val = map(lambda x, idx=idx: self._function(*chain[:idx], x, *chain[idx+1:]), self._x)
            curves[f"unfixed-{idx}"].set_ydata(y_val)
        ax.relim()
        ax.autoscale_view()

    def init_plot(self, ax) -> None:
        if self._options.repr3D:
            self.init_plot_2d(ax)
            return

        ax.clear()
        self._x = np.linspace(self._min_value, self._max_value, self._graph_num_points)
        curves = {}
        for idx in range(self._size):
            curves[f"unfixed-{idx}"] = ax.plot(self._x, self._x)[0]
            curve_color = curves[f"unfixed-{idx}"].get_color()
            curves[f"point-{idx}"] = ax.plot(0, 0, marker="o", color=curve_color)[0]
        self.set_curves(ax, curves)

    def plot_2d(self, ax, individual) -> None:
        """
        Plot the individual in 2D.
        """
        chain = individual.get_chain()
        self.get_curves(ax)["point"].set_data(*chain)
        self.get_curves(ax)["point"].set_3d_properties(self._function(*chain))

    def init_plot_2d(self, ax) -> None:
        """
        Initialize the plot for the 2D representation.
        """
        x1 = np.linspace(self._min_value, self._max_value, self._graph_num_points)
        y1 = np.linspace(self._min_value, self._max_value, self._graph_num_points)
        x, y = np.meshgrid(x1, y1)
        ax.plot_surface(x, y, self._function(x, y), cmap='viridis', alpha=0.8)
        mean = (self._min_value + self._max_value) / 2
        point = ax.plot(mean, mean, self._function(mean, mean), color="blue", marker="o")
        self.set_curves(ax, {"point": point[0]})
