"""
Define the SeparatorEvaluator class
This class is a subclass of the ChainEvaluator class.
This evaluator is used to evaluate a chain by separating it into two subsets.
"""

import numpy as np
from typing import Optional
from evopy.evaluator.chain.base import ChainEvaluator
from evopy.evaluator.graphic import GraphicReprEvaluator
from evopy.individual import BinaryChainIndividual


class SeparatorEvaluator(ChainEvaluator, GraphicReprEvaluator):
    """
    This is the SeparatorEvaluator class.
    This class is a subclass of the ChainEvaluator class.
    This evaluator is used to evaluate a chain by separating it into two subsets.

    Parameters:
        * separator_weights (random | list[float]): Weights used to separate the chain into two subsets.
    """

    component_type: str = "Separator"
    requirements = [("individual", BinaryChainIndividual)]

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        weights = options.separator_weights
        if self.is_random(weights):
            weights = self.create_weights(options.individual_size)
        self._weights: np.array = np.array(weights)
        ChainEvaluator.__init__(self, options)
        GraphicReprEvaluator.__init__(self, options)

    def _evaluate_chain(self, chain: list) -> float:
        set_1, set_2 = self._compute_sets_value(chain)
        return abs(set_1 - set_2)

    def create_weights(self, size) -> np.array:
        """
        Create a random array of _weights
        """
        w = np.random.random(size)
        return w / w.sum()

    def _compute_sets_value(self, chain: list):
        """
        Compute the value of the two subsets
        """
        s1, s2 = 0, 0
        for weight, value in zip(self._weights, chain):
            if value == 1:
                s1 += weight
            else:
                s2 += weight
        return s1, s2

    def init_plot(self, ax) -> None:
        ax.clear()
        axs = self.create_subplots(ax, 2, 1)
        ax1, ax2 = axs[0, 0], axs[1, 0]

        rects = ax1.bar(range(len(self._weights)), self._weights, color="grey", edgecolor="black")
        self.set_curves(ax1, {"rects": rects})

        dict2 = {}
        self.set_limits(ax2, y_min=0, y_max=1)
        dict2["bars"] = ax2.bar(
            ["Subset 1", "Subset 2"], [0, 0], color=["skyblue", "salmon"], edgecolor="black"
        )
        for i, somme in enumerate([0, 0]):
            dict2[f"text{i+1}"] = ax2.text(
                i,
                somme - 0.1,
                f"{somme:.8f}",
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
            )
        self.set_curves(ax2, dict2)

    def plot(self, ax, individual: BinaryChainIndividual) -> None:
        axs = self.get_subaxs(ax)
        curves_ax1, curves_ax2 = self.get_curves(axs[0, 0]), self.get_curves(axs[1, 0])

        color_array = np.where(individual.get_chain() == 0, "salmon", "skyblue")
        for rect, color in zip(curves_ax1["rects"], color_array):
            rect.set_color(color)

        s1, s2 = self._compute_sets_value(individual)
        for rect, value in zip(curves_ax2["rects"], [s1, s2]):
            rect.set_height(value)
        text1, text2 = curves_ax2["text1"], curves_ax2["text2"]
        text1.set_text(f"{s1:.8f}")
        text2.set_text(f"{s2:.8f}")
        text1.set_y(s1 - 0.1)
        text2.set_y(s2 - 0.1)
