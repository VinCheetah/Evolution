from matplotlib.pyplot import ylim
from base.Individual.BinaryChainIndividual import BinaryChainIndividual
from base.Individual.GraphicReprIndividual import GraphicReprIndividual
from numpy.typing import NDArray
import numpy as np

class SeparatorIndividual(BinaryChainIndividual, GraphicReprIndividual):

    _component_type: str = "Separator"

    weights: NDArray

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        GraphicReprIndividual.__init__(self, options)
        BinaryChainIndividual.__init__(self, options)
        self.set1_value: float = 0
        self.set2_value: float = 0

    @classmethod
    def set_weights(cls, weights: NDArray):
        cls.weights = weights


    def copy(self):
        copy = super().copy()
        copy.set1_value = self.set1_value
        copy.set2_value = self.set2_value
        return copy

    @classmethod
    def init_plot(cls, ax) -> None:
        ax.clear()
        cls.create_subplots(ax, 2, 1)
        axs = cls.get_subaxs(ax)
        ax1, ax2 = axs[0, 0], axs[1, 0]
        bars = ax1.bar(range(len(cls.weights)), cls.weights, color="grey", edgecolor="black")
        cls.set_curves(ax1, {"bars": bars})

        dict2 = {}
        cls.set_limits(ax2, y_min=0, y_max=1)
        dict2["bars"] = ax2.bar(["Subset 1", "Subset 2"], [0, 0], color=["skyblue", "salmon"], edgecolor="black")
        for i, somme in enumerate([0, 0]):
            dict2[f"text{i+1}"] = ax2.text(i, somme - 0.1, f"{somme:.8f}", ha="center", va="bottom", fontsize=8, fontweight="bold")
        cls.set_curves(ax2, dict2)

    def plot(self, ax) -> None:
        axs = self.get_subaxs(ax)
        ax1, ax2 = axs[0, 0], axs[1, 0]
        s1, s2 = self.set1_value, self.set2_value
        curves_ax1 = self.get_curves(ax1)
        color_array = np.where(self._chain == 0, 'salmon', 'skyblue')
        for bar, color in zip(curves_ax1["bars"], color_array):
            bar.set_color(color)

        curves_ax2 = self.get_curves(ax2)
        for bar, value in zip(curves_ax2["bars"], [s1, s2]):
            bar.set_height(value)
        text1, text2 = curves_ax2["text1"], curves_ax2["text2"]
        text1.set_text(f'{s1:.8f}')
        text2.set_text(f'{s2:.8f}')
        text1.set_y(s1 - 0.1)
        text2.set_y(s2 - 0.1)
