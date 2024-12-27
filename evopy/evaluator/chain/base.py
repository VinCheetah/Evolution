"""
Define the ChainEvaluator class.
This class is a subclass of the SingleEvaluator class.
"""

from abc import abstractmethod
from evopy.evaluator.single import SingleEvaluator
from evopy.individual import ChainIndividual


class ChainEvaluator(SingleEvaluator):
    """
    This is the ChainEvaluator class.
    This class is a subclass of the SingleEvaluator class.
    """

    SingleEvaluator.set_component_type("Chain")
    SingleEvaluator.add_requirement("individual", ChainIndividual)

    def iter_ind(self, individual):
        """
        Iterate over the individual's chain
        """
        return iter(individual.get_chain())

    def ind_size(self, individual):
        """
        Get the size of the individual's chain
        """
        return individual.size

    def _evaluate(self, individual: ChainIndividual) -> float:
        return self._evaluate_chain(individual.get_chain())

    @abstractmethod
    def _evaluate_chain(self, chain: list) -> float:
        """
        Evaluate the chain
        """
