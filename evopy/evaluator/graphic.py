""" 
Define the GraphicReprEvaluator
This class is an optional class for an evaluator.
It permits to create a visual representation of the evaluation and the fitness.
"""

from abc import abstractmethod
from matplotlib import gridspec
import matplotlib.pyplot as plt
import numpy as np


class GraphicReprEvaluator:
    """
    This is the GraphicReprEvaluator

    Parameters:
        * has_graph_repr (bool): Whether an evaluator has a graph_repr
            Fixed
        * repr3d (bool): Whether the evaluator should use a 3D representation
    """

    _subaxs: dict = {}
    _curves: dict = {}

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        options.has_graph_repr = True
        self._repr3d: bool = options.repr3d

    @abstractmethod
    def init_plot(self, ax) -> None:
        """
        Initialize the plot of a given ax
        """

    @abstractmethod
    def plot(self, ax, individual) -> None:
        """
        Update the plot of an individual on the given ax
        """

    @staticmethod
    def set_limits(ax, x_min=None, x_max=None, y_min=None, y_max=None) -> None:
        """
        Set the limits of a given ax accordingly to the arguments
        """
        if x_min is not None or x_max is not None:
            ax.set_xlim(left=x_min, right=x_max)
        if y_min is not None or y_max is not None:
            ax.set_ylim(bottom=y_min, top=y_max)

    def create_subplots(
        self, ax, size: tuple[int, int], height_ratios=None, hspace=None
    ) -> np.array:
        """
        Subdivide the given ax into multiple subplots
        """
        inner_grid = gridspec.GridSpecFromSubplotSpec(
            *size, subplot_spec=ax.get_subplotspec(), height_ratios=height_ratios, hspace=hspace
        )
        axs = np.empty(size, dtype=object)
        for i in range(size[0]):
            for j in range(size[1]):
                axs[i][j] = ax.figure.add_subplot(inner_grid[i, j])
        self._subaxs[ax] = axs
        ax.axis("off")
        return axs

    def get_subaxs(self, ax) -> np.ndarray:
        """
        Return the subaxes tab of an ax
        """
        return self._subaxs[ax]

    def get_curves(self, ax) -> dict:
        """
        Return the curves of an ax
        """
        return self._curves[ax]

    def set_curves(self, ax, curves: dict) -> None:
        """
        Set curves to the given ax
        """
        self._curves[ax] = curves

    def to_graph(self, individual):
        """
        Plot an individual and show it
        """
        _, ax = plt.subplots()
        self.init_plot(ax)
        self.plot(ax, individual)
        plt.show()
