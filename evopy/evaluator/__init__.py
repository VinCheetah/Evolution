""" 
This is the Evaluator package.

This package contains the following classes:
- BaseEvaluator
- SingleEvaluator
- GroupEvaluator
- GraphicReprEvaluator
- PermuEvaluator
    - SalesManEvaluator
- ChainEvaluator
    - FunctionEvaluator
    - SeparatorEvaluator
- NNEvaluator
    - NEATvaluator
    - RaceCarEvaluator

The BaseEvaluator class is the base class for all the evaluator classes.
"""

from evopy.evaluator.base import BaseEvaluator
from evopy.evaluator.single import SingleEvaluator
from evopy.evaluator.group import GroupEvaluator
from evopy.evaluator.graphic import GraphicReprEvaluator
from evopy.evaluator.permutation.base import PermuEvaluator
from evopy.evaluator.permutation.salesman import SalesManEvaluator
from evopy.evaluator.chain.base import ChainEvaluator
from evopy.evaluator.chain.function import FunctionEvaluator
from evopy.evaluator.chain.separator import SeparatorEvaluator
from evopy.evaluator.neural_network.base import NNEvaluator
from evopy.evaluator.neural_network.neat import NEATEvaluator
from evopy.evaluator.neural_network.race_car import RaceCarEvaluator


__all__ = [
    "BaseEvaluator",
    "SingleEvaluator",
    "GroupEvaluator",
    "GraphicReprEvaluator",
    "PermuEvaluator",
    "SalesManEvaluator",
    "ChainEvaluator",
    "FunctionEvaluator",
    "SeparatorEvaluator",
    "NNEvaluator",
    "NEATEvaluator",
    "RaceCarEvaluator",
]
