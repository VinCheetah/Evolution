"""
Define the GroupEvaluator class.
This class is a subclass of the BaseEvaluator class.
This evaluator is used to evaluate a group of individuals at the same time.
"""

from time import time
from abc import abstractmethod
from evopy.evaluator.base import BaseEvaluator
from evopy.population import BasePopulation
from evopy.individual import BaseIndividual


class GroupEvaluator(BaseEvaluator):
    """
    This is the GroupEvaluator class.
    This class is a subclass of the BaseEvaluator class.
    This evaluator is used to evaluate a group of individuals at the same time.

    Parameters:
    """

    component_type: str = "Group"

    def _evaluate_pop(self, population: BasePopulation):
        self._evaluated = population.size
        start = time()
        self._evaluate(population)
        eval_time = time() - start
        for individual in population:
            fitness, err_eval = self._get_evaluation(individual)
            individual.register_evaluation(fitness, eval_time, err_eval)
        population.update_order()

    @abstractmethod
    def _evaluate(self, population: BasePopulation) -> None:
        """
        Evaluate all the group of individuals in the population
        """

    @abstractmethod
    def _get_evaluation(self, individual: BaseIndividual) -> tuple[float, str]:
        """
        Get the evaluation of an individual
        """
