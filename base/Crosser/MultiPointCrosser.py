from base.Individual.BaseIndividual import BaseIndividual

from abc import abstractmethod
import numpy as np

class MultiPointCrosser:

    def __init__(self, options, **kwargs):
        options.update(kwargs)

        self._num_points: int = options.num_points
        self._num_cross: int = options.num_cross


    def _cross(self, ind1: BaseIndividual, ind2: BaseIndividual) -> dict:
        """
        Cross two individuals
        """
        idxs = np.sort(np.random.randint(0, len(ind1) - 1, self._num_points * self._num_cross))
        data = ind1._get_data()
        for i in range(self._num_cross):
            idx = idxs[i*self._num_points: (i+1)*self._num_points]
            data = self._cross_points(data, ind2, *idx)
        return data

    @abstractmethod
    def _cross_points(self, data: dict, ind2: BaseIndividual, *idx) -> dict:
        pass
