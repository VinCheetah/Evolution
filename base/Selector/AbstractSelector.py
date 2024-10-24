from abc import ABC, abstractmethod


class AbstractSelector(ABC):

    @abstractmethod
    def select(self, population):
        """
        Select individuals from the population
        """
        pass
