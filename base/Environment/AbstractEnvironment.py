from abc import ABC, abstractmethod


class AbstractEnvironment(ABC):

    @abstractmethod
    def evolve(self) -> None:
        """
        Evolution of the environment
        """
        pass
