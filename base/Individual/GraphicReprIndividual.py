from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

class GraphicReprIndividual(ABC):

    _subaxs: dict = {}
    _curves: dict = {}

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        options.has_graph_repr = True

    @classmethod
    @abstractmethod
    def init_plot(cls, ax) -> None:
        pass

    @abstractmethod
    def plot(self, ax) -> None:
        pass

    @staticmethod
    def set_limits(ax, x_min=None, x_max=None, y_min=None, y_max=None) -> None:
        if x_min is not None or x_max is not None:
            ax.set_xlim(left=x_min, right=x_max)
        if y_min is not None or y_max is not None:
            ax.set_ylim(bottom=y_min, top=y_max)

    @classmethod
    def create_subplots(cls, ax, n: int, m: int, height_ratios=None, hspace=None) -> None:
        inner_grid = gridspec.GridSpecFromSubplotSpec(n, m, subplot_spec=ax.get_subplotspec(), height_ratios=height_ratios, hspace=hspace)
        axs = np.empty((n, m), dtype=object)
        for i in range(n):
            for j in range(m):
                axs[i][j] = ax.figure.add_subplot(inner_grid[i, j])
        cls._subaxs[ax] = axs
        ax.axis('off')

    @classmethod
    def get_subaxs(cls, ax) -> np.ndarray:
        return cls._subaxs[ax]

    @classmethod
    def get_curves(cls, ax) -> dict:
        return cls._curves[ax]

    @classmethod
    def set_curves(cls, ax, curves: dict) -> None:
        cls._curves[ax] = curves

    def to_graph(self):
        fig, ax = plt.subplots()
        self.plot(ax)
        plt.show()
