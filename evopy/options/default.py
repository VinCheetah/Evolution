from evopy.component import BaseComponent
from evopy.environment import BaseEnvironment
from evopy.individual import BaseIndividual
from evopy.evaluator import BaseEvaluator
from evopy.selector import BaseSelector
from evopy.mutator import BaseMutator
from evopy.crosser import BaseCrosser
from evopy.population import BasePopulation
from evopy.elite import BaseElite
from evopy.graphic import BaseGraphic
from evopy.interface.base import BaseInterface
from evopy.reporter import BaseReporter
from evopy.utils.evo_types import Random, Randomized
from evopy.utils.activations import relu_activation
from evopy.utils.aggregations import sum_aggregation

default = {
    "environment": BaseEnvironment,
    "component": BaseComponent,
    # Environment
    "individual": BaseIndividual,
    "evaluator": BaseEvaluator,
    "selector": BaseSelector,
    "mutator": BaseMutator,
    "population": BasePopulation,
    "elite": BaseElite,
    "crosser": BaseCrosser,
    "graphic": BaseGraphic,
    "interface": BaseInterface,
    "reporter": BaseReporter,
    "evolution_record": None,
    "reproducing": False,
    "from_beginning": False,

    "random_seed": 1234567865,
    "max_gen": 100,
    "timeout": 1000,
    "eval_timeout": -1,
    "keep_sorted": True,
    "ascending_order": True,

    # Population
    "size_population": 400,
    "complete_population": True,
    "immigration_rate": 0.2,
    "strict_size": True,

    # Selector
    "selection_ratio": 0.30,
    "allow_invalid": False,
    "allow_copies": True,
    "limit_size": True,
    "keep_best": True,
    "keep_previous_best": True,
    "max_single_select_fail": 10,
    "max_group_select_fail": 10,
    ## Tournament
    "tournament_mode_ratio": False,
    "tournament_size_ratio": 0.1,
    "tournament_size": 18,
    ## Wheel
    "wheel_selection_mode": "softmax",
    "wheel_power": 3,

    # Individual
    "individual_size": 100,
    "has_graph_repr": True,
    "has_graph_repr_init": False,
    "repr3d": False,
    # # Chain
    "min_value": -.5,
    "max_value": .5,
    "type_value": float,
    # # NN
    "input_size": 1,
    "output_size": 1,
    "hidden": [],
    # # # NEAT
    "bias_init_mean": 0,
    "bias_init_std": 0,
    "bias_max_value": 0,
    "bias_min_value": 0,
    "response_init_mean": 0,
    "response_init_std": 0,
    "response_max_value": 0,
    "response_min_value": 0,
    "activation_options": {"relu": relu_activation},
    "activation_default": "relu",
    "aggregation_options": {"sum": sum_aggregation},
    "aggregation_default": "sum",
    "weight_init_mean": 0,
    "weight_init_std": 0,
    "weight_max_value": 0,
    "weight_min_value": 0,
    "enabled_default": True,

    # Mutator
    "mutation_prob": 0.3,
    "multi_mutation": True,
    "multi_mode": False,
    "multi_mutation_mode": "power",
    # NEAT
    "add_connection_prob": 0.2,
    "del_connection_prob": 0.1,
    "add_node_prob":0.1,
    "del_node_prob": 0.05,
    "toggle_connection_prob": 0.05,
    "weight_mutation_prob": 0.3,
    "reset_weight_prob": 0.1,
    "weight_mutation_power": 0.3,

    # Crosser
    "cross_prob": 0.1,
    # # MultiPointCrosser
    "num_points": 2,
    "num_cross": 1,
    # # # NEAT
    "disable_inheritance_prob": 0.75,

    # Elite
    "create_elite": True,
    "elite_size": 1,

    # Evaluator
    "evaluation_func": None,
    "invalid_fit_value": 0,
    "unevaluated_time": 0,
    # # PermuEval
    "weights": Random,
    # # # TSP
    "cities": Random,
    # # # Separator
    "separator_weights": Randomized,
    # # NNEval


    # Graphic
    "active_graphic": True,
    "max_gen_display": -1,
    "stop_graph": False,
    "end_graph": True,
    "metrics_graph": True,
    "best_elite": True,
    "best_pop": True,
    "time_gestion": True,
    "metrics_log_scale": True,

    # Interface
    "active_interface": True,

    # Reporter
    "active_reporter": True,
    "reporter_periodic_display": 10,  # Affichage toutes les N générations
    "reporter_collect_statistics": True,
    "reporter_track_diversity": False,
    "reporter_verbose": False,  # Mode verbose pour plus de détails

    # Reproduction
    "tracking": False,
    "record_folder": "evo_records",
    "record_subfolder": "default",
    "record_file": "evo",
    "record_file_spec": "",

    #Logger
    "active_c_logg": True,
    "c_logg_level": "Warning",
    "c_logg_format": '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    "active_f_logg": False,
    "logg_file_name": "evo.log",
    "f_logg_level": "Info",
    "f_logg_format": '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    "filtered_components": [],

    # Report
    "create_report": True
}