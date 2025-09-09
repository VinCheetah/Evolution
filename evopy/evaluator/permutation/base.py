"""
Deine the PermuEvaluator class.
The PermuEvaluator class is an abstract class that inherits from the SingleEvaluator class.
It is used to evaluate permutation individuals.
"""

from abc import abstractmethod
from evopy.evaluator.single import SingleEvaluator
from evopy.individual import PermuIndividual

class PermuEvaluator(SingleEvaluator):
    """
    This is the PermuEvaluator class.
    This class is a subclass of the SingleEvaluator class.
    It is used to evaluate permutation individuals.
    """

    component_type = "Permutation"
    _requirements = [("individual", PermuIndividual)]

    def _evaluate(self, individual: PermuIndividual) -> float:
        return self._evaluate_permu(individual.get_permutation())

    @abstractmethod
    def _evaluate_permu(self, permutation: list) -> float:
        """
        Evaluate the permutation
        """
