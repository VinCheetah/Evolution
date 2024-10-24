from base.Evaluator.SingleEvaluator import SingleEvaluator
from base.Individual.PermuIndividual import PermuIndividual
import numpy as np
import numpy.typing as npt


class PermuEvaluator(SingleEvaluator):

    _component_type: str = "Permu"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        super().__init__(options)
        self._size: int = options.individual_size
        self.weights: npt.NDArray[np.float_] = options.weights if options.weights is not None else np.random.rand(self._size, self._size)

    def _evaluate(self, individual: PermuIndividual) -> float:
        tot = 0.
        for i in range(len(individual)-1):
            tot += self.weights[individual[i], individual[i+1]]
        tot += self.weights[individual[len(individual) - 1], individual[0]]
        return tot
