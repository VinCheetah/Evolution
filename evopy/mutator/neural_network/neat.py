from sympy import Min

from evopy.individual import NEATIndividual
from evopy.mutator.neural_network.base import NeuralNetworkMutator


import random
import numpy as np

from evopy.mutator.successive import SuccessiveMutator
from evopy.population import BasePopulation
from evopy.individual import BaseIndividual


class NEATMutator(SuccessiveMutator, NeuralNetworkMutator):
    """
    Implements NEAT-style mutations for NEATIndividuals.

    Parameters:
        * add_connection_prob (float): Probability of adding a new connection.
            Min: 0
            Max: 1
        * del_connection_prob (float): Probability of deleting a connection.
            Min: 0
            Max: 1
        * add_node_prob (float): Probability of adding a new node.
            Min: 0
            Max: 1
        * del_node_prob (float): Probability of deleting a node.
            Min: 0
            Max: 1
        * toggle_connection_prob (float): Probability of toggling a connection.
            Min: 0
            Max: 1
        * weight_mutation_prob (float): Probability of mutating a weight.
            Min: 0
            Max: 1
        * reset_weight_prob (float): Probability of resetting a weight.
            Min: 0
            Max: 1
        * weight_mutation_power (float): Order of variation of the mutation.
            Min: 0
    """

    component_type: str = "NEAT"

    def __init__(self, options):
        """
        NEAT mutation probabilities and parameters.
        """
        super(NeuralNetworkMutator, self).__init__(options)
        self.add_connection_prob: float = self._options.add_connection_prob
        self.del_connection_prob: float = self._options.del_connection_prob
        self.add_node_prob: float = self._options.add_node_prob
        self.del_node_prob: float = self._options.del_node_prob
        self.toggle_connection_prob: float = self._options.toggle_connection_prob
        self.weight_mutation_prob: float = self._options.weight_mutation_prob
        self.reset_weight_prob: float = self._options.reset_weight_prob
        self.weight_mutation_power: float = self._options.weight_mutation_power

        self.successive_functions = [
            (self.add_connection_prob, self._add_connection),
            (self.del_connection_prob, self._del_connection),
            (self.add_node_prob, self._add_node),
            (self.del_node_prob, self._del_node),
            (self.weight_mutation_prob, self._mutate_weights),
            (self.toggle_connection_prob, self._toggle_connection),
        ]

    # --- NEAT mutation operations ---

    def _mutate_weights(self, individual: NEATIndividual) -> bool:
        """ Perturb existing connection weights. """
        if not individual.has_connections():
            return False

        mutated = False
        for conn in individual.iter_connections():
            if random.random() < self.reset_weight_prob:
                conn.set_weight(0)
            else:
                perturb = np.random.normal(0, self.weight_mutation_power)
                conn.set_weight(perturb + conn.weight)
            mutated = True
        return mutated

    def _add_connection(self, individual: NEATIndividual) -> bool:
        """ Add a new connection between two nodes if possible. """
        in_node = individual.get_random_node()
        out_node = individual.get_random_node()

        if in_node == out_node:
            return False

        for conn in individual.iter_connections():
            if (conn.in_node, conn.out_node) == (in_node, out_node):
                return False

        individual.link(in_node, out_node)
        return True

    def _del_connection(self, individual: NEATIndividual) -> bool:
        """ Delete a connection between two nodes if possible. """
        if not individual.has_connections():
            return False

        connection = individual.get_random_connection()
        individual.remove_connection(connection)
        return True

    def _add_node(self, individual: NEATIndividual) -> bool:
        """ Add a node by splitting an existing connection. """
        if not individual.has_connections():
            return False

        conn = individual.get_random_connection()
        if not conn.enabled:
            return False

        conn.switch()
        # Create new node
        new_node = individual.add_random_node(node_type="hidden")
        # Create two new _connections
        individual.link(conn.in_node, new_node)
        individual.link(new_node, conn.out_node)
        return True

    def _del_node(self, individual: NEATIndividual) -> bool:
        """ Delete a node by splitting an existing connection. """
        node = individual.get_random_node()
        if node.type != "hidden":
            return False
        individual.remove_node(node)
        return True

    def _toggle_connection(self, individual: NEATIndividual) -> bool:
        """ Enable or disable a random connection. """
        if not individual.has_connections():
            return False
        conn = individual.get_random_connection()
        conn.switch()
        return True
