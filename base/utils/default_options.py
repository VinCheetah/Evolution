from base.utils.options import Options
from base.Individual.BaseIndividual import BaseIndividual
from base.Evaluator.BaseEvaluator import BaseEvaluator
from base.Selector.BaseSelector import BaseSelector
from base.Mutator.BaseMutator import BaseMutator
from base.Crosser.BaseCrosser import BaseCrosser
from base.Population.BasePopulation import BasePopulation
from base.Elite.BaseElite import BaseElite
from base.Graphic.BaseGraphic import BaseGraphic


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


    "random_seed": 123456789,
    "max_gen": 2000,
    "timeout": 1000,
    "eval_timeout": -1,
    "keep_sorted": True,
    "ascending_order": True,


    # Population
    "size_population": 1000,
    "complete_population": True,
    "immigration_rate": 0.1,
    "strict_size": True,

    # Selector
    "selection_ratio": 0.60,
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
    "tournament_size": 8,
    ## Wheel
    "wheel_selection_mode": "softmax",
    "wheel_power": 3,

    # Individual
    "individual_size": 150,
    "has_graph_repr": False,
    "has_graph_repr_init": False,

    # Mutator
    "mutation_prob": 0.3,

    # Crosser
    "cross_prob": 0.6,

    # Elite
    "create_elite": True,
    "elite_size": 1,

    # Evaluator
    # # PermuEval
    "weights": None,
    # # # TSP
    "cities": None,

    # Graphic_repr
    "max_gen_display": 50,
    "stop_graph": False,
    "end_graph": True,
    "metrics_graph": True,
    "best_elite": True,
    "best_pop": False,
    "time_gestion": True,
})
