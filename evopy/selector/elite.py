"""
Defines the EliteSelector class.
This class is used to select the best individuals of the population.
"""

from evopy.selector.base import BaseSelector
from evopy.population import BasePopulation


class EliteSelector(BaseSelector):
    """
    This is the Elite selector.
    Selects the best individuals of the population.

    Parameters:
    """

    component_name: str = "Elite"
    _group_select: bool = True

    def group_select(self, population: BasePopulation, n_selected: int):
        """
        Select the best individuals of the population.
        """
        return population.get_best_inds(n=n_selected), True
