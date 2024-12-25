""" 
Defines the BaseCrosser class.

This class is the base class for all crossers. 
It defines the basic methods that a crosser should have.
"""

from random import random
from abc import abstractmethod
from evopy.component import BaseComponent
from evopy.population import BasePopulation
from evopy.individual import BaseIndividual


class BaseCrosser(BaseComponent):
    """
    Base class for all crossers.
    """

    BaseComponent.set_component_name("Crosser")
    BaseComponent.set_component_type("Base")
    BaseComponent.add_requirement("individual", BaseIndividual)

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseComponent.__init__(self, options)
        self._cross_prob: float = options.cross_prob
        self._crossed: int = 0

    def num_crossed_individuals(self):
        """ 
        Returns the number of crossovers performed during the last call to the cross method.
        """
        return self._crossed

    @BaseComponent.record_time
    def cross(self, population: BasePopulation) -> None:
        """
        Perform the crossover operation on the population.
        
        Parameters
        ----------
        population : BasePopulation (or subclass)
            The population on which the crossovers will be performed.
        """
        self._crossed = 0
        for ind1 in population:
            if random() < self._cross_prob:
                self._crossed += 1
                ind2 = population.get_random()[0]
                data = self._cross(ind1, ind2)
                origin = [f"crossover({ind1.get_id()}, {ind2.get_id()})"]
                population.add_individual_from_data(data, origin)

    @abstractmethod
    def _cross(self, ind1, ind2) -> dict:
        """
        Do the crossover between two individuals.
        
        Parameters
        ----------
        ind1 : BaseIndividual (or subclass)
            The first individual.
        ind2 : BaseIndividual (or subclass)
            The second individual.
            
        Returns
        -------
        dict
            A dictionary containing the data of the new individual
        """
