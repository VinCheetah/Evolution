from evopy.utils.options import Options
from evopy.individual import BaseIndividual
from evopy.evaluator import BaseEvaluator
from evopy.selector import BaseSelector
from evopy.mutator import BaseMutator
from evopy.crosser import BaseCrosser
from evopy.population import BasePopulation
from evopy.elite import BaseElite
from evopy.graphic import BaseGraphic
from evopy.interface.base import BaseInterface



default_opts = Options({
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
    "evolution_record": None,

    "random_seed": 1234567865,
    "max_gen": 10000,
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
    "selection_ratio": 0.50,
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
    "tournament_size": 20,
    ## Wheel
    "wheel_selection_mode": "softmax",
    "wheel_power": 3,

    # Individual
    "individual_size": 100,
    "has_graph_repr": False,
    "has_graph_repr_init": False,
    "repr3D": False,
    # # Chain
    "min_value": -.5,
    "max_value": .5,
    "type_value": float,

    # Mutator
    "mutation_prob": 0.3,
    "multi_mutation": True,
    "multi_mutation_mode": "power",

    # Crosser
    "cross_prob": 0.5,
    # # MultiPointCrosser
    "num_points": 2,
    "num_cross": 1,

    # Elite
    "create_elite": True,
    "elite_size": 1,

    # Evaluator
    "evaluation_func": None,
    "unvalid_fit_value": 0,
    "unevaluated_time": 0,
    # # PermuEval
    "weights": None,
    # # # TSP
    "cities": None,
    # # # Separator
    "separator_weights": None,

    # Graphic
    "active_graphic": True,
    "max_gen_display": -1,
    "stop_graph": False,
    "end_graph": True,
    "metrics_graph": True,
    "best_elite": True,
    "best_pop": False,
    "time_gestion": False,
    "metrics_log_scale": True,

    # Interface
    "active_interface": True,

    # Reproduction
    "tracking": True,
    "record_folder": "evo_records",
    "record_subfolder": "default",
    "record_file": "evo",
    "record_file_spec": "",

    # Report
    "create_report": True
})
