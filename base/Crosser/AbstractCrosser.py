from abc import ABC, abstractmethod


class AbstractCrosser(ABC):

    @abstractmethod
    def cross(self, population) -> None:
        """
        Cross two individuals
        """
        pass
