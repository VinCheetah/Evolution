from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from numpy.typing import NDArray


class GraphicReprEvaluator(ABC):

    _subaxs: dict = {}
    _curves: dict = {}

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        options.has_graph_repr = True

    @abstractmethod
    def init_plot(self, ax) -> None:
        pass

    @abstractmethod
    def plot(self, ax, individual) -> None:
        pass

    @staticmethod
    def set_limits(ax, x_min=None, x_max=None, y_min=None, y_max=None) -> None:
        if x_min is not None or x_max is not None:
            ax.set_xlim(left=x_min, right=x_max)
        if y_min is not None or y_max is not None:
            ax.set_ylim(bottom=y_min, top=y_max)

    def create_subplots(self, ax, n: int, m: int, height_ratios=None, hspace=None) -> NDArray:
        inner_grid = gridspec.GridSpecFromSubplotSpec(n, m, subplot_spec=ax.get_subplotspec(), height_ratios=height_ratios, hspace=hspace)
        axs = np.empty((n, m), dtype=object)
        for i in range(n):
            for j in range(m):
                axs[i][j] = ax.figure.add_subplot(inner_grid[i, j])
        self._subaxs[ax] = axs
        ax.axis('off')
        return axs

    def get_subaxs(self, ax) -> np.ndarray:
        return self._subaxs[ax]

    def get_curves(self, ax) -> dict:
        return self._curves[ax]

    def set_curves(self, ax, curves: dict) -> None:
        self._curves[ax] = curves

    def to_graph(self, individual):
        fig, ax = plt.subplots()
        self.init_plot(ax)
        self.plot(ax, individual)
        plt.show()
