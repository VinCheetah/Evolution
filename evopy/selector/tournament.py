"""
Defines the TournamentSelector class.
This class is used to select individuals by tournament.
"""

from evopy.selector.base import BaseSelector
from evopy.population import BasePopulation


class TournamentSelector(BaseSelector):
    """
    This is the Tournament selector.
    Selects individuals by tournament.

    Parameters:
        * tournament_mode_ratio (bool): Whether the number of individuals in the tournament in selected by the size parameter, or the size_ratio parameter
        * tournament_size (int): The number of individuals to participate in a tournament
            Min: 1
        * tournament_size_ratio (float): The ratio of the number of participants in each tournament, with the number of individuals
            Min: 0
            Max: 1
        * size_population (int): The number of individuals in the population. Is important only if the mode is 'ratio'
            Min: 1
    """

    component_type: str = "Tournament"
    _single_select: bool = True

    def __init__(self, options):
        super().__init__(options)
        self._tournament_mode_ratio: bool = self._options.tournament_mode_ratio
        self._tournament_size: int = self._options.tournament_size
        self._tournament_size_ratio: float = self._options.tournament_size_ratio

        if self._tournament_mode_ratio:
            self._tournament_size = int(self._tournament_size_ratio * self._options.size_population)

    def single_select(self, idx: int, population: BasePopulation):
        """
        Select an individual by tournament.
        """
        competitors = population.get_random(n=self._tournament_size)
        if population.exist_valid(competitors):
            winner = population.get_best_ind(competitors)
            return winner, True
        return population.get_random(sample=competitors, n=1)[0], True
