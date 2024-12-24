from evopy.selector import BaseSelector
from evopy.population.base import BasePopulation


class EliteSelector(BaseSelector):

    _component_type: str = "Elite"
    _group_select: bool = True

    def group_select(self, population: BasePopulation, n_selected: int):
        return population.get_best_inds(n=n_selected), True
