from abc import ABC, abstractmethod


class AbstractEnvironment(ABC):

    @abstractmethod
    def evolve(self):
        """
        Evolution of the environment
        """
        ...
