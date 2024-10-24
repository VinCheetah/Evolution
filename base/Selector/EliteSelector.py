from base.Selector.BaseSelector import BaseSelector
from base.Population.BasePopulation import BasePopulation


class EliteSelector(BaseSelector):

    _component_type: str = "Elite"
    _group_select: bool = True

    def group_select(self, population: BasePopulation, n_selected: int):
        return population.get_best_inds(n=n_selected), True
