"""
Defines the base class for neural network individuals based on the NEAT method.

Individuals in this module are based on neural networks.
"""
from abc import abstractmethod
from typing import Callable, Optional, Any
import random
from evopy.individual.neural_network.base import NNIndividual
from evopy.utils.graphs import creates_cycle, feed_forward_layers
from evopy.utils.innovation import InnovationTracker


class NEATGene:

    _id_counter : int
    __slots__: tuple[str, ...] = ("_id",)

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

    def __copy__(self):
        """
        Create a copy of this NEATGene.
        """
        return self.__class__(*[getattr(self, slot) for slot in self.__slots__])

    def copy(self):
        return self.__copy__()

    def __hash__(self):
        return hash(self._id)
    
    def __eq__(self, other):
        """Two genes are equal if they have the same innovation number (ID)."""
        if not isinstance(other, NEATGene):
            return False
        return self._id == other._id


class NodeGene(NEATGene):
    _id_counter = 0

    bias_init_mean: float = ...
    bias_init_std: float = ...
    bias_max_value: float = ...
    bias_min_value: float = ...

    response_init_mean: float = ...
    response_init_std: float = ...
    response_max_value: float = ...
    response_min_value: float = ...

    activation_options: dict[str, Any] = ...
    activation_default: str = ...

    aggregation_options: dict[str, Any] = ...
    aggregation_default: str = ...

    __slots__ = ("_type", "_bias", "_activation", "_aggregation", "_response", "_id")

    def __init__(self, node_type:str=None,
                 bias: float = None,
                 activation: str = None,
                 aggregation: str = None,
                 response:float = None,
                 gene_id: int = None):
        super().__init__(gene_id)
        self._type: str = node_type or "hidden"
        # Initialize with temporary values, will be set properly below
        self._bias: float = 0.0
        self._activation: Callable = lambda x: x  # temporary
        self._aggregation: Callable = sum  # temporary
        self._response: float = 1.0
        
        # Now set the actual values
        self.set_bias(bias if bias is not None else self._get_bias())
        self.set_activation(activation or self.activation_default)
        self.set_aggregation(aggregation or self.aggregation_default)
        self.set_response(response if response is not None else self._get_response())

    @property
    def type(self):
        return self._type

    @property
    def bias(self):
        return self._bias

    @property
    def activation(self):
        return self._activation

    @property
    def response(self):
        return self._response

    @property
    def aggregation(self):
        return self._aggregation

    def _get_bias(self):
        return random.gauss(self.bias_init_mean, self.bias_init_std)

    def _get_response(self):
        return random.gauss(self.response_init_mean, self.response_init_std)

    def _get_activation(self, activation: str):
        if activation not in self.activation_options:
            raise ValueError(f"Invalid activation option: {activation} / List of activation options: {self.activation_options}")
        return self.activation_options[activation]

    def _get_aggregation(self, aggregation: str):
        if aggregation not in self.aggregation_options:
            raise ValueError(f"Invalid activation option: {aggregation} / List of aggregation options: {self.aggregation_options}")
        return self.aggregation_options[aggregation]

    def set_bias(self, bias: float):
        self._bias = min(self.bias_max_value, max(self.bias_min_value, bias))

    def set_response(self, response: float):
        self._response = min(self.response_max_value, max(self.response_min_value, response))

    def set_activation(self, activation: str | Callable):
        self._activation = activation if isinstance(activation, Callable) else self._get_activation(activation)

    def set_aggregation(self, aggregation: str | Callable):
        self._aggregation = aggregation if isinstance(aggregation, Callable) else self._get_aggregation(aggregation)


class ConnectionGene(NEATGene):

    _id_counter = 0

    weight_init_mean: float = ...
    weight_init_std: float = ...
    weight_max_value: float = ...
    weight_min_value: float = ...

    enabled_default: bool = ...

    __slots__ = ("_in", "_out", "_weight", "_enabled", "_id")

    def __init__(self, in_node, out_node, weight: Optional[float]=None, enabled:Optional[bool]=None, gene_id:Optional[int]=None):
        super().__init__(gene_id)
        self._in: NodeGene = in_node
        self._out: NodeGene = out_node
        self._weight: float = weight if weight is not None else self._get_weight()
        self._enabled: bool = enabled if enabled is not None else (self.enabled_default if hasattr(self, 'enabled_default') and self.enabled_default is not ... else True)

    @property
    def in_node(self):
        return self._in

    @property
    def out_node(self):
        return self._out

    @property
    def enabled(self):
        return self._enabled

    @property
    def weight(self):
        return self._weight

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def switch(self):
        self._enabled = not self._enabled

    def _get_weight(self) -> float:
        return random.gauss(self.weight_init_mean, self.weight_init_std)

    def set_weight(self, weight: float):
        self._weight = min(self.weight_max_value, max(self.weight_min_value, weight))


class FeedForwardNetwork(object):

    def __init__(self, inputs, outputs, node_evals):
        self.input_nodes = inputs
        self.output_nodes = outputs
        self.node_evals = node_evals
        # Initialize values for all nodes that appear in the network
        all_nodes = set(inputs + outputs)
        
        # Add all nodes that are being evaluated
        for node, links in node_evals:
            all_nodes.add(node.id)
            # Add all input nodes referenced in the links
            for input_node_id, _ in links:
                all_nodes.add(input_node_id)
        
        self.values = dict((key, 0.0) for key in all_nodes)

    def activate(self, inputs):
        if len(self.input_nodes) != len(inputs):
            raise RuntimeError("Expected {0:n} inputs, got {1:n}".format(len(self.input_nodes), len(inputs)))

        for k, v in zip(self.input_nodes, inputs):
            self.values[k] = v

        for node, links in self.node_evals:
            node_inputs = []
            for i, w in links:
                if i not in self.values:
                    raise KeyError(f"Node {i} not found in values dictionary. Available keys: {list(self.values.keys())}")
                node_inputs.append(self.values[i] * w)
            s = node.aggregation(node_inputs)
            self.values[node.id] = node.activation(node.bias + node.response * s)

        return [self.values[i] for i in self.output_nodes]


class NEATIndividual(NNIndividual):
    """
    Base class for individuals based on neural networks.

    Parameters:
        * bias_init_mean (float): Initial mean of the bias value.
        * bias_init_std (float): Initial standard deviation of the bias value.
        * bias_max_value (float): Max value of the bias value.
        * bias_min_value (float): Min value of the bias value.
        * response_init_mean (float): Initial mean of the response value.
        * response_init_std (float): Initial standard deviation of the response value.
        * response_max_value (float): Max value of the response value.
        * response_min_value (float): Min value of the response value.
        * weight_init_mean (float): Initial mean of the weight value.
        * weight_init_std (float): Initial standard deviation of the weight value.
        * weight_max_value (float): Max value of the weight value.
        * weight_min_value (float): Min value of the weight value.
        * activation_options (dict[str, Callable]): Activation functions to use.
        * activation_default (str): Default activation function.
        * aggregation_options (dict[str, Callable]): Aggregation functions to use.
        * aggregation_default (str): Default aggregation function.
    """

    component_type: str = "Neat"
    input_ids: list[int] = ...
    output_ids: list[int] = ...
    initial_connection_ids: dict[tuple[int, int], int] = {}  # Map (in_id, out_id) -> innovation_id
    innovation_tracker: InnovationTracker = InnovationTracker()

    @classmethod
    def initialize(cls, options):
        super().initialize(options)
        cls.input_ids = NodeGene.id_generator(cls._input_size)
        cls.output_ids = NodeGene.id_generator(cls._output_size)
        cls.innovation_tracker.reset(NodeGene._id_counter, ConnectionGene._id_counter)
        
        # Pre-assign innovation numbers for initial connections
        cls.initial_connection_ids = {}
        for in_id in cls.input_ids:
            for out_id in cls.output_ids:
                conn_id = cls.innovation_tracker.get_connection_id(in_id, out_id)
                cls.initial_connection_ids[(in_id, out_id)] = conn_id

        cls.innovation_tracker.sync_node_counter(NodeGene._id_counter)
        cls.innovation_tracker.sync_connection_counter(ConnectionGene._id_counter)
        ConnectionGene._id_counter = cls.innovation_tracker.next_connection_id
        
        for attr, target in [("bias", NodeGene), ("response", NodeGene), ("weight", ConnectionGene)]:
            for params in ["_init_mean", "_init_std", "_max_value", "_min_value"]:
                cls.transfer_options(attr+params, options, target=target, protected=False)
        for attr, target in [("activation", NodeGene), ("aggregation", NodeGene)]:
            for params in ["_options", "_default"]:
                cls.transfer_options(attr+params, options, target=target, protected=False)
        ConnectionGene.enabled_default = options.enabled_default


    def __init__(self, options):
        super().__init__(options)
        self._nodes: set[NodeGene] = set()
        self._input_nodes: set[NodeGene] = set()
        self._output_nodes: set[NodeGene] = set()
        self._connections: set[ConnectionGene] = set()

        for gene_id in self.input_ids:
            self.add_random_node("input", gene_id)

        for gene_id in self.output_ids:
            self.add_random_node("output", gene_id)

        for in_node in self._input_nodes:
            for out_node in self._output_nodes:
                # Use pre-assigned innovation number for initial connections
                conn_id = self.initial_connection_ids.get((in_node.id, out_node.id))
                conn = ConnectionGene(in_node, out_node, weight=0.0, enabled=True, gene_id=conn_id)
                if conn_id is not None:
                    ConnectionGene._id_counter = max(ConnectionGene._id_counter, conn_id + 1)
                self.add_connection(conn)

        self.built_network: bool = False
        self._network: FeedForwardNetwork = FeedForwardNetwork([], [], [])

    def __eq__(self, other):
        if not isinstance(other, NEATIndividual):
            return False
        return other.get_id() == self.get_id()

    def _init(self, data: dict):
        super()._init(data)
        self._input_nodes.clear()
        self._output_nodes.clear()
        self._connections.clear()
        self._nodes.clear()
        for node in data["nodes"]:
            self.add_node(node)
        for connection in data["connections"]:
            self.add_connection(connection)

    def get_data(self):
        nodes_copy = set(map(lambda node: node.copy(), self._nodes))
        connections_copy = set(map(lambda connection: connection.copy(), self._connections))
        return super().get_data() | {"nodes": nodes_copy, "connections": connections_copy}

    @property
    def network(self):
        if not self.built_network:
            self.build_network()
        return self._network

    def has_mutate(self):
        super().has_mutate()
        self.built_network = False

    def has_connections(self):
        return len(self._connections) != 0

    def add_node(self, node):
        if node.type == "input":
            self._input_nodes.add(node)
        elif node.type == "output":
            self._output_nodes.add(node)
        self._nodes.add(node)
        self.built_network = False

    def link(self, in_node: NodeGene, out_node: NodeGene) -> ConnectionGene:
        conn = self._create_connection(in_node, out_node)
        self.add_connection(conn)
        return conn

    def _create_connection(self, in_node: NodeGene, out_node: NodeGene, *, weight: Optional[float] = None,
                            enabled: Optional[bool] = None) -> ConnectionGene:
        conn_id = self.__class__.innovation_tracker.get_connection_id(in_node.id, out_node.id)
        ConnectionGene._id_counter = max(ConnectionGene._id_counter, conn_id + 1)
        return ConnectionGene(in_node, out_node, weight=weight, enabled=enabled, gene_id=conn_id)

    def add_random_node(self, node_type=None, node_id=None):
        if node_type is None:
            node_type = random.choice(["input", "output", "hidden"])
        new_node = NodeGene(node_type=node_type, gene_id=node_id)
        self.add_node(new_node)
        return new_node

    def create_split_node(self, connection: ConnectionGene) -> NodeGene:
        tracker = self.__class__.innovation_tracker
        node_id = tracker.get_split_node_id(connection.in_node.id, connection.out_node.id)
        NodeGene._id_counter = max(NodeGene._id_counter, node_id + 1)
        new_node = NodeGene(node_type="hidden", gene_id=node_id)
        new_node.set_bias(0.0)
        new_node.set_response(1.0)
        self.add_node(new_node)
        return new_node

    def remove_node(self, node):
        if node.type == "input":
            self._input_nodes.remove(node)
        elif node.type == "output":
            self._output_nodes.remove(node)
        self._nodes.remove(node)
        dangling = [conn for conn in self._connections if conn.in_node == node or conn.out_node == node]
        for conn in dangling:
            self._connections.remove(conn)
        self.built_network = False

    def add_connection(self, connection):
        self._connections.add(connection)
        self.built_network = False

    def remove_connection(self, connection):
        self._connections.remove(connection)
        self.built_network = False

    def iter_connections(self):
        return iter(self._connections)

    def iter_nodes(self):
        return iter(self._nodes)

    @property
    def nodes(self) -> set[NodeGene]:
        return self._nodes

    @property
    def connections(self) -> set[ConnectionGene]:
        return self._connections

    def get_random_node(self):
        return random.choice(list(self._nodes))

    def get_random_connection(self):
        return random.choice(list(self._connections))

    def build_network(self):
        """ Returns its phenotype (a FeedForwardNetwork). """
        connections = [conn for conn in self._connections if conn.enabled]

        layers = feed_forward_layers(self.input_ids, self.output_ids, connections)
        
        # Create a mapping from node IDs to NodeGene objects
        node_map = {node.id: node for node in self._nodes}
        
        node_evals = []
        for layer in layers:
            for node_id in layer:
                if node_id in node_map:
                    node_gene = node_map[node_id]
                    inputs = []
                    for conn in connections:
                        in_node_id = conn.in_node.id
                        out_node_id = conn.out_node.id
                        if out_node_id == node_id:
                            inputs.append((in_node_id, conn.weight))
                    node_evals.append((node_gene, inputs))
        
        self._network = FeedForwardNetwork(self.input_ids, self.output_ids, node_evals)
        self.built_network = True
