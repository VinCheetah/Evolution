"""
Define the SingleEvaluator class
This class is a subclass of the BaseEvaluator class.
This evaluator is used to evaluate a single individual at a time.
"""

from abc import abstractmethod
from time import time
from typing import Optional, Callable
from evopy.evaluator.base import BaseEvaluator
from evopy.population import BasePopulation
from evopy.utils.exceptions import IgnoreException


class SingleEvaluator(BaseEvaluator):
    """
    This is the SingleEvaluator class.
    This class is a subclass of the BaseEvaluator class.
    This evaluator is used to evaluate a single individual at a time.
    """

    BaseEvaluator.set_component_type("Single")

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseEvaluator.__init__(self, options)
        eval_func: Optional[Callable] = options.evaluation_func
        self._eval_func: Callable = eval_func if eval_func is not None else self._evaluate

    def _evaluate_pop(self, population: BasePopulation):
        """
        Evaluate individuals from the population
        """
        self._evaluated = 0
        for individual in population:
            if individual.get_is_evaluated():
                continue
            self._evaluated += 1
            start = time()
            try:
                fitness = self._eval_func(individual)
                err_eval = ""
            except IgnoreException as exception:
                self.log("warning", f"Error evaluating {individual.get_id()} - {exception}")
                fitness = 0.
                err_eval = str(exception)
            eval_time = time() - start
            individual.register_evaluation(fitness, eval_time, err_eval)
        population.update_order()

    @abstractmethod
    def _evaluate(self, individual) -> float:
        """
        Evaluate an individual and return its fitness
        """
