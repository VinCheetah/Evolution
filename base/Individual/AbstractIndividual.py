from abc import ABC, abstractmethod


class AbstractIndividual(ABC):

    @classmethod
    @abstractmethod
    def _create(cls, *args, **kwargs) -> "AbstractIndividual":
        """
        Create a random individual
        """
        ...

    @abstractmethod
    def _init(self, data) -> None:
        """
        Initialize individual from data
        """
        ...
