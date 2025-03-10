"""
Define the BaseEvaluator class.
Evaluator component is responsible for evaluating the individuals in the population.
"""

from abc import abstractmethod
from evopy.component import BaseComponent
from evopy.population import BasePopulation


class BaseEvaluator(BaseComponent):
    """
    This is the BaseEvaluator class.
    The evaluator component is responsible for evaluating the individuals in the population.

    Parameters:
        * individual_size (int): The size of the individual
            Min: 0
        * eval_timeout (int): The maximum time to wait for a single evaluation. -1 is no limit.
            Min: -1

    """

    component_name: str = "Evaluator"
    component_type: str = "Base"
    requirements = [("population", BasePopulation)]

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseComponent.__init__(self, options)

        self._size: int = self._options.individual_size
        self._timeout: int = self._options.eval_timeout
        self._evaluated: int = 0

    @BaseComponent.record_time
    def evaluate(self, population: BasePopulation) -> None:
        """
        Evaluate a population
        """
        population.init_evaluation()
        self._evaluate_pop(population)

    def num_evaluated_individuals(self) -> int:
        """ 
        Return the number of individuals evaluated in the last call of the evaluator
        """
        return self._evaluated

    @abstractmethod
    def _evaluate_pop(self, population: BasePopulation) -> None:
        """ 
        Evaluate a whole population
        """

    def get_eval_timeout(self) -> float | None:
        """ 
        Return the evalution timeout.
        """
        return self._timeout if self._timeout > 0 else None
