""" 
Defines the NNEvaluator class
It is the base class for any evaluator of a neural network individual
"""

from abc import abstractmethod
import numpy as np
from evopy.evaluator.single import SingleEvaluator
from evopy.evaluator.graphic import GraphicReprEvaluator
from evopy.individual import NNIndividual


class NNEvaluator(SingleEvaluator, GraphicReprEvaluator):
    """
    This is the NNEvaluator class.
    It is the base class for any evaluator of a neural network individual
    """

    SingleEvaluator.set_component_type("NeuralNetork")
    SingleEvaluator.add_requirement("individual", NNIndividual)

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        GraphicReprEvaluator.__init__(self, options)
        SingleEvaluator.__init__(self, options)
        self._input_size = options.input_size
        self._output_size = options.output_size
        self._layers: list[int] = [self._input_size] + options.hidden + [self._output_size]
        self._num_layers = len(self._layers)

    @abstractmethod
    def _compute_x(self, individual):
        """
        Compute the input for the neural network for the given individual.
        """

    def _compute_output(self, individual):
        """
        Compute the output of the neural network for the given individual.
        """
        return individual.forward(self._compute_x(individual))

    def plot(self, ax, individual) -> None:
        """
        Plot the neural network with the given individual on the given axis.
        """
        edges = self.get_curves(ax)["edges"]
        w_max = np.max(np.abs(individual.weights))
        weights = [weight for layer in individual.weights for vertex in layer for weight in vertex]
        edges.set_linewidth(list(map(lambda w: max(0.1, abs(w) / w_max) * 2, weights)))
        edges.set_color(list(map(lambda w: "green" if w > 0 else "red", weights)))

    def init_plot(self, ax) -> None:
        """
        Initialize the plot of the neural network on the given axis.
        """
        ax.axis("off")
        self.set_limits(ax, 0, 1, 0, 1)
        neuron_positions = [
            [(x, y) for y in np.linspace(0.1, 0.9, layer_size + 2)[1:-1]]
            for x, layer_size in zip(np.linspace(0.1, 0.9, self._num_layers), self._layers)
        ]
        for layer in neuron_positions:
            ax.scatter(*list(zip(*layer)), c="black")

        edges = [
            list(zip(neuron_positions[i][j], neuron_positions[i][k]))
            for i in range(self._num_layers - 1)
            for j in range(self._layers[i])
            for k in range(self._layers[i + 1])
        ]
        lc = ax.collections.LineCollection(edges, color="black", linewidth=0.1)
        self.set_curves(ax, {"edges": ax.add_collection(lc)})
