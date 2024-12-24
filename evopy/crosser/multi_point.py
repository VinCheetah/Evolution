""" 
Defines the MultiPointCrosser class.
This class is an optional class for a crosser.
It permits to perform the crossover operation on multiple points.
"""

from abc import abstractmethod
import numpy as np
from evopy.crosser.base import BaseCrosser
from evopy.individual import BaseIndividual


class MultiPointCrosser(BaseCrosser):
    """
    MultiPointCrosser class.
    This class is an optional class for a crosser.
    It permits to perform the crossover operation on multiple points.
    
    Attributes
    ----------
    _num_points : int
        The number of points for the crossover operation.
    _num_cross : int
        The number of crossovers to perform.
    """

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseCrosser.__init__(self, options)

        self._num_points: int = options.num_points
        self._num_cross: int = options.num_cross

    def _cross(self, ind1: BaseIndividual, ind2: BaseIndividual) -> dict:
        """ 
        Do the crossover between two individuals.
        The crossover is performed on multiple points, as defined by the num_points attribute.
        
        Parameters
        ----------
        ind1 : BaseIndividual (or subclass)
            The first individual.
        ind2 : BaseIndividual (or subclass)
            The second individual.
        
        Returns
        -------
        dict
            The data of the new individual.
        """
        idxs = np.sort(np.random.randint(0, len(ind1) - 1, self._num_points * self._num_cross))
        data = ind1.get_data()
        for i in range(self._num_cross):
            idx = idxs[i * self._num_points: (i+1) * self._num_points]
            data = self._cross_points(data, ind2, *idx)
        return data

    @abstractmethod
    def _cross_points(self, data: dict, ind2: BaseIndividual, *idx) -> dict:
        """
        Cross two individuals at given points.
        First individual is given as a dictionnary of data.
        
        Parameters
        ----------
        data : dict
            The data of the first individual.
        ind2 : BaseIndividual (or subclass)
            The second individual.
        idx : int (variable length, set by num_points value)
            The indices of the crossover points.
            
        Returns
        -------
        dict
            The data of the new individual.
        """
