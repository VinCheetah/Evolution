"""
Defines the base class for neural network individuals based on the NEAT method.

Individuals in this module are based on neural networks.
"""

import numpy as np
from evopy.individual.neural_network.base import NNIndividual
from evopy.utils.graphs import creates_cycle, feed_forward_layers
import random


class NEATGene:

    _id_counter : int

    def __init__(self, gene_id=None):
        if gene_id is None or type(gene_id) is not int:
            self._id = self.__class__._id_counter
            self.__class__._id_counter += 1
        else:
            self._id = gene_id

    @classmethod
    def id_generator(cls, num_id):
        ids = list(range(cls._id_counter, cls._id_counter + num_id))
        cls._id_counter += num_id
        return ids

    @property
    def id(self):
        return self._id


class NodeGene(NEATGene):
    _id_counter = 0

    def __init__(self, node_type, bias, activation, gene_id=None):
        super().__init__(gene_id)
        self._type = node_type
        self._bias = bias
        self._activation = activation

    @property
    def type(self):
        return self._type

    @property
    def bias(self):
        return self._bias

    @property
    def activation(self):
        return self._activation

    def set_bias(self, bias):
        self._bias = bias

    def set_activation(self, activation):
        self._activation = activation




class ConnectionGene(NEATGene):
    id_counter = 0

    def __init__(self, in_node, out_node, weight, enabled, gene_id=None):
        super().__init__(gene_id)
        self._in = in_node
        self._out = out_node
        self._weight = weight
        self._enabled = enabled

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def set_weight(self, weight):
        self._weight = weight



class FeedForwardNetwork(object):
    def __init__(self, inputs, outputs, node_evals):
        self.input_nodes = inputs
        self.output_nodes = outputs
        self.node_evals = node_evals
        self.values = dict((key, 0.0) for key in inputs + outputs)

    def activate(self, inputs):
        if len(self.input_nodes) != len(inputs):
            raise RuntimeError("Expected {0:n} inputs, got {1:n}".format(len(self.input_nodes), len(inputs)))

        for k, v in zip(self.input_nodes, inputs):
            self.values[k] = v

        for node, act_func, agg_func, bias, response, links in self.node_evals:
            node_inputs = []
            for i, w in links:
                node_inputs.append(self.values[i] * w)
            s = agg_func(node_inputs)
            self.values[node] = act_func(bias + response * s)

        return [self.values[i] for i in self.output_nodes]


class NEATIndividual(NNIndividual):
    """
    Base class for individuals based on neural networks.
    """

    component_type: str = "NeatNeuralNetwork"
    input_ids = []
    output_ids = []

    @classmethod
    def initialize(cls, options):
        super().initialize(options)
        cls.input_ids = NodeGene.id_generator(cls._input_size)
        cls.output_ids = NodeGene.id_generator(cls._output_size)

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        super().__init__(options, **kwargs)
        self._nodes = {}
        self._input_nodes = {}
        self._output_nodes = {}
        self._connections = {}

        for gene_id in self.input_ids:
            self.add_random_node("input", gene_id)

        for gene_id in self.output_size:
            self.add_random_node("output", gene_id)

        self.built_network: False = False
        self._network: FeedForwardNetwork = FeedForwardNetwork([], [], [])


    def add_node(self, node):
        if node.type == "input":
            self._input_nodes[node.id] = node
        elif node.type == "output":
            self._output_nodes[node.id] = node
        self._nodes[node.id] = node

    def add_random_node(self, node_type=None, node_id=None):
        if node_type is None:
            node_type = random.choice(["input", "output", "hidden"])

        bias = random.random()
        activation = ""

        self.add_node(NodeGene(node_type, bias, activation, node_id))


    def remove_node(self, node):
        del self._nodes[node.id]

    def add_connection(self, connection):
        self._connections[connection.id] = connection

    def build_network(self):
        """ Returns its phenotype (a FeedForwardNetwork). """

        # Gather expressed connections.
        connections = [cg.key for cg in self._connections.values() if cg.enabled]

        layers = feed_forward_layers(self.input_ids, self.output_ids, connections)
        node_evals = []
        for layer in layers:
            for node in layer:
                inputs = []
                for conn_key in connections:
                    in_node, out_node = conn_key
                    if out_node == node:
                        cg = self._connections[conn_key]
                        inputs.append((in_node, cg.weight))

                ng = self._nodes[node]
                aggregation_function = config.genome_config.aggregation_function_defs.get(ng.aggregation)
                activation_function = config.genome_config.activation_defs.get(ng.activation)
                node_evals.append((node, activation_function, aggregation_function, ng.bias, ng.response, inputs))

        self._network = FeedForwardNetwork(self.input_ids, self.output_ids, node_evals)

