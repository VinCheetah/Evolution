from evopy.selector import BaseSelector
from evopy.population.base import BasePopulation


class TournamentSelector(BaseSelector):

    _component_type: str = "Tournament"
    _single_select: bool = True

    def __init__(self, options):
        super().__init__(options)
        self._tournament_mode_ratio: bool = options.tournament_mode_ratio
        self._tournament_size: int = options.tournament_size
        self._tournament_size_ratio: float = options.tournament_size_ratio

        if self._tournament_mode_ratio:
            self._tournament_size = int(self._tournament_size_ratio * options.size_population)

    def single_select(self, idx: int, population: BasePopulation):
        competitors = population.get_random(n=self._tournament_size)
        if population.exist_valid(competitors):
            winner = population.get_best_ind(competitors)
            return winner, True
        else:
            return population.get_random(sample=competitors, n=1)[0], True
