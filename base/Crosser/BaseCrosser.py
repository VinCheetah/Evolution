from base.Component.BaseComponent import BaseComponent
from base.Crosser.AbstractCrosser import AbstractCrosser
import random as rd

from base.Population.BasePopulation import BasePopulation

class BaseCrosser(BaseComponent, AbstractCrosser):

    _component_name: str = "Crosser"
    _component_type: str = "Base"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseComponent.__init__(self, options)
        self._cross_prob: float = options.cross_prob

    def num_crossed_individuals(self):
        return self._crossed

    @BaseComponent.record_time
    def cross(self, population:BasePopulation):
        self._crossed = 0
        for ind1 in population:
            if rd.random() < self._cross_prob:
                self._crossed += 1
                ind2 = population.get_random()[0]
                data = self._cross(ind1, ind2)
                population.add_individual_from_data(data, [f"crossover({ind1._id}, {ind2._id})"])
