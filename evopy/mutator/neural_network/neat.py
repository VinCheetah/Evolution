import random
import numpy as np

from evopy.individual import NEATIndividual
from evopy.mutator.neural_network.base import NeuralNetworkMutator
from evopy.mutator.successive import SuccessiveMutator
from evopy.utils.graphs import creates_cycle


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
        super().__init__(options)
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

        # Check if connection already exists
        for conn in individual.iter_connections():
            if (conn.in_node, conn.out_node) == (in_node, out_node):
                if not conn.enabled:
                    conn.enable()
                    individual.built_network = False
                    return True
                return False

        enabled_connections = [conn for conn in individual.iter_connections() if conn.enabled]
        if creates_cycle(enabled_connections, (in_node, out_node)):
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

        original_weight = conn.weight
        conn.disable()

        new_node = individual.create_split_node(conn)
        conn1 = individual._create_connection(conn.in_node, new_node, weight=1.0, enabled=True)
        individual.add_connection(conn1)
        conn2 = individual._create_connection(new_node, conn.out_node, weight=original_weight, enabled=True)
        individual.add_connection(conn2)
        return True

    def _del_node(self, individual: NEATIndividual) -> bool:
        """ Delete a random hidden node if possible. """
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
        individual.built_network = False
        return True
