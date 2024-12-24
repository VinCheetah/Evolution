"""
Defines the base class for neural network individuals.

Individuals in this module are based on neural networks.
"""

import numpy as np
from evopy.individual import BaseIndividual


class NNIndividual(BaseIndividual):
    """
    Base class for individuals based on neural networks.
    """

    _component_type = "NeuralNetworkIndividual"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseIndividual.__init__(self, options, **kwargs)

        self.input_size = options.input_size
        self.hidden_layers = options.hidden_layers
        self.output_size = options.output_size
        self.weights = []
        self.biases = []

        self.initialize_parameters()

    @classmethod
    def _create(cls, options, **kwargs) -> "NNIndividual":
        """
        Create a new NNIndividual instance.
        """
        options.update(kwargs)
        return cls(options)

    def initialize_parameters(self):
        """Initialize weights and biases for each layer based on the architecture."""
        layer_sizes = [self.input_size] + self.hidden_layers + [self.output_size]

        for i in range(len(layer_sizes) - 1):
            weight_matrix = np.random.randn(layer_sizes[i], layer_sizes[i + 1])
            bias_vector = np.random.randn(layer_sizes[i + 1])
            self.weights.append(weight_matrix)
            self.biases.append(bias_vector)

        # How to iter on weights

    def edge_idx(self, layer, nstart, nend):
        """Get the index of the edge between two neurons in the neural network."""
        idx = 0
        for i in range(layer):
            idx += self.weights[i].shape[1]
        idx += nstart * self.weights[layer].shape[1] + nend
        return idx

    def edge_neurons(self, idx):
        """Get the neurons connected by the edge at the given index."""
        for i, layer in enumerate(self.weights):
            if idx < layer.size:
                return i, idx // layer.shape[1], idx % layer.shape[1]
            idx -= layer.size
        raise ValueError("Index {idx} out of range")

    def forward(self, x):
        """Compute the output of the neural network for input x."""
        for weight, bias in zip(self.weights, self.biases):
            x = np.dot(x, weight) + bias  # Linear transformation
            x = np.tanh(x)  # Activation function
        return x

    def mutate(self, mutation_rate=0.1):
        """Apply mutation to weights and biases."""
        for layer, bias in zip(self.weights, self.biases):
            if np.random.rand() < mutation_rate:
                layer += np.random.randn(*layer.shape) * 0.1
            if np.random.rand() < mutation_rate:
                bias += np.random.randn(*bias.shape) * 0.1
        self.has_mutate()  # Update the mutation origin and ID

    def get_data(self) -> dict:
        """Override to include neural network specific data in copy."""
        data = super().get_data()
        data.update({"weights": self.weights.copy(), "biases": self.biases.copy()})
        return data

    def _init(self, data):
        """Initialize individual from given data."""
        super()._init(data)
        self.weights = data.get("weights", self.weights)
        self.biases = data.get("biases", self.biases)

    def __len__(self):
        """Define the length as the total number of weights."""
        return sum(weight.size for weight in self.weights)

    def repr(self):
        """Implement to visualize or describe the neural network structure."""
        return f"Neural Network: {[self.input_size] + self.hidden_layers + [self.output_size]}"
