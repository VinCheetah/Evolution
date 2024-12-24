from evopy.evaluator.base import BaseEvaluator
from evopy.population.base import BasePopulation
from abc import abstractmethod
from time import time


class SingleEvaluator(BaseEvaluator):

    _component_type: str = "Single"

    def __init__(self, options):
        self._eval_func = options.evaluation_func if options.evaluation_func is not None else self._evaluate
        super().__init__(options)

    def _evaluate_pop(self, population: BasePopulation):
        """
        Evaluate individuals from the population
        """
        self._evaluated = 0
        for individual in population:
            if individual._is_evaluated:
                continue
            self._evaluated += 1
            start = time()
            try:
                fitness = self._eval_func(individual)
                err_eval = ""
            except Exception as e:
                self.log("warning", f"Error evaluating individual {individual._id} - {e}")
                fitness = 0.
                err_eval = str(e)
            eval_time = time() - start
            individual.register_evaluation(fitness, eval_time, err_eval)
        population.update_order()

    @abstractmethod
    def _evaluate(self, individual) -> float:
        ...
