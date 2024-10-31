from base.Component.BaseComponent import BaseComponent
from base.Evaluator.AbstractEvaluator import AbstractEvaluator
from base.Population.BasePopulation import BasePopulation


class BaseEvaluator(BaseComponent, AbstractEvaluator):

    _component_name: str = "Evaluator"
    _component_type: str = "Base"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseComponent.__init__(self, options)
        self._timeout: int = self._options.eval_timeout
        self._evaluated: int = 0

    @BaseComponent.record_time
    def evaluate(self, population: BasePopulation) -> None:
        population._init_evaluation()
        self._evaluate_pop(population)

    def num_evaluated_individuals(self) -> int:
        return self._evaluated

    def _evaluate_pop(self, population: BasePopulation) -> None:
        self.log("warning", "Method _evaluate_pop not implemented, no selection done")
