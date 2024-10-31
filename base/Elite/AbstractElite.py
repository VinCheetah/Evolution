from abc import ABC, abstractmethod


class AbstractElite(ABC):

    @abstractmethod
    def update(self, population) -> None:
        """
        Update the elite with the best individuals from the population.
        """
        pass
