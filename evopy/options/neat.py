# Auto-generated preset
import numpy as np
from evopy.crosser.neural_network.neat import NEATCrosser
from evopy.evaluator.neural_network.neat import NEATEvaluator
from evopy.individual.neural_network.neat import NEATIndividual
from evopy.mutator.neural_network.neat import NEATMutator
from evopy.population.speciated import SpeciatedPopulation
from evopy.selector import EliteSelector, TournamentSelector
from evopy.selector.wheel import WheelSelector
from evopy.utils.options import Options

neat = Options('neat',
    size_population = 100,
    evaluator = NEATEvaluator,
    crosser = NEATCrosser,
    mutator = NEATMutator,
    individual = NEATIndividual,
    population = SpeciatedPopulation,
    selector = TournamentSelector,
    # Network topology
    input_size = 1,
    output_size = 1,
    # Node parameters
    response_max_value = 3.0,
    response_min_value = -3.0,
    response_init_mean = 1.0,
    response_init_std = 0.5,
    bias_max_value = 3.0,
    bias_min_value = -3.0,
    bias_init_mean = 0.0,
    bias_init_std = 0.5,
    # Connection parameters
    weight_max_value = 3.0,
    weight_min_value = -3.0,
    weight_init_mean = 0.0,
    weight_init_std = 0.5,
    enabled_default = True,
    # Mutation parameters
    add_connection_prob = 0.05,
    del_connection_prob = 0.01,
    add_node_prob = 0.02,
    del_node_prob = 0.01,
    toggle_connection_prob = 0.01,
    weight_mutation_prob = 0.5,
    reset_weight_prob = 0.1,
    weight_mutation_power = 0.5,
    # Activation and aggregation functions
    activation_options = {
        'sigmoid': lambda x: 1.0 / (1.0 + np.exp(-x)),
        'tanh': np.tanh,
        'relu': lambda x: max(0.0, x),
        'linear': lambda x: x
    },
    activation_default = 'sigmoid',
    aggregation_options = {
        'sum': sum,
        'mean': lambda x: sum(x) / len(x) if x else 0.0,
        'max': max,
        'min': min
    },
    aggregation_default = 'sum',
    # Speciation defaults
    compatibility_threshold = 3.0,
    c1 = 1.0,
    c2 = 1.0,
    c3 = 0.4,
    compatibility_modifier = 0.3,
    target_species = 10,
    max_stagnation = 15,
    min_species_size = 2,
    elitism_threshold = 5,
    neat_function = None,
)
