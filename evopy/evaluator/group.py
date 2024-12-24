from evopy.evaluator.base import BaseEvaluator
from evopy.population.base import BasePopulation
from evopy.individual import BaseIndividual
from abc import abstractmethod
from time import time


class GroupEvaluator(BaseEvaluator):

    _component_type: str = "Group"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseEvaluator.__init__(self, options)

    def _evaluate_pop(self, population: BasePopulation):
        """
        Evaluate individuals from the population
        """
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
        ...

    @abstractmethod
    def _get_evaluation(self, individual: BaseIndividual) -> tuple[float, str]:
        ...
