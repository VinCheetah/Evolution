from base.Evaluator.SingleEvaluator import SingleEvaluator
from base.Individual.Chain.BinaryChainIndividual import BinaryChainIndividual
from base.Evaluator.GraphicReprEvaluator import GraphicReprEvaluator
import numpy as np
from numpy.typing import NDArray


class SeparatorEvaluator(SingleEvaluator, GraphicReprEvaluator):

    _component_type = "Separator"

    def __init__(self, options):
        if options.separator_weights is None:
            options.separator_weights = self.create_weights(options.individual_size)
        elif not type(self.weights) is NDArray:
            options.separator_weights = np.array(options.separator_weights)
        SingleEvaluator.__init__(self, options)
        GraphicReprEvaluator.__init__(self, options)
        self.weights: NDArray = options.separator_weights

    def _evaluate(self, individual) -> float:
        assert isinstance(individual, BinaryChainIndividual)
        set_1, set_2 = self._compute_sets_value(individual)
        return abs(set_1 - set_2)

    def _compute_sets_value(self, individual: BinaryChainIndividual):
        s1, s2 = 0, 0
        for i in range(len(individual)):
            if individual[i] == 1:
                s1 += self.weights[i]
            else:
                s2 += self.weights[i]
        return s1, s2

    def create_weights(self, size) -> NDArray:
        w = np.random.random(size)
        return w / w.sum()

    def init_plot(self, ax) -> None:
        ax.clear()
        axs = self.create_subplots(ax, 2, 1)
        ax1, ax2 = axs[0, 0], axs[1, 0]

        bars = ax1.bar(range(len(self.weights)), self.weights, color="grey", edgecolor="black")
        self.set_curves(ax1, {"bars": bars})

        dict2 = {}
        self.set_limits(ax2, y_min=0, y_max=1)
        dict2["bars"] = ax2.bar(["Subset 1", "Subset 2"], [0, 0], color=["skyblue", "salmon"], edgecolor="black")
        for i, somme in enumerate([0, 0]):
            dict2[f"text{i+1}"] = ax2.text(i, somme - 0.1, f"{somme:.8f}", ha="center", va="bottom", fontsize=8, fontweight="bold")
        self.set_curves(ax2, dict2)

    def plot(self, ax, individual: BinaryChainIndividual) -> None:
        axs = self.get_subaxs(ax)
        ax1, ax2 = axs[0, 0], axs[1, 0]
        curves_ax1 = self.get_curves(ax1)
        color_array = np.where(individual._chain == 0, 'salmon', 'skyblue')
        for bar, color in zip(curves_ax1["bars"], color_array):
            bar.set_color(color)
        s1, s2 = self._compute_sets_value(individual)
        curves_ax2 = self.get_curves(ax2)
        for bar, value in zip(curves_ax2["bars"], [s1, s2]):
            bar.set_height(value)
        text1, text2 = curves_ax2["text1"], curves_ax2["text2"]
        text1.set_text(f'{s1:.8f}')
        text2.set_text(f'{s2:.8f}')
        text1.set_y(s1 - 0.1)
        text2.set_y(s2 - 0.1)
