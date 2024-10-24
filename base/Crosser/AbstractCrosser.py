from abc import ABC, abstractmethod
from base.Individual.BaseIndividual import BaseIndividual


class AbstractCrosser(ABC):

    @abstractmethod
    def _cross(self, ind1, ind2) -> dict:
        """
        Cross two individuals
        """
        pass
