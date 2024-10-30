from tkinter.ttk import Separator
from base.Evaluator.SingleEvaluator import SingleEvaluator
from base.Individual.SeparatorIndividual import SeparatorIndividual
import numpy as np
from numpy.typing import NDArray


class SeparatorEvaluator(SingleEvaluator):

    _component_type = "Separator"

    def __init__(self, options):
        if options.separator_weights is None:
            options.separator_weights = self.create_weights(options.individual_size)
        elif not type(self.weights) is NDArray:
            options.separator_weights = np.array(options.separator_weights)
        SingleEvaluator.__init__(self, options)
        #assert type(options.separator_weights) is NDArray
        self.weights: NDArray = options.separator_weights
        SeparatorIndividual.set_weights(self.weights)

    def _evaluate(self, individual) -> float:
        assert isinstance(individual, SeparatorIndividual)
        set_1 = 0
        set_2 = 0
        for i in range(len(individual)):
            if individual[i] == 1:
                set_1 += self.weights[i]
            else:
                set_2 += self.weights[i]
        individual.set1_value = set_1
        individual.set2_value = set_2
        return abs(set_1 - set_2)

    def create_weights(self, size) -> NDArray:
        w = np.random.random(size)
        return w / w.sum()
