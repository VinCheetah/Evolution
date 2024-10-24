from abc import ABC, abstractmethod


class AbstractMutator(ABC):


    @abstractmethod
    def _mutate(self, individual) -> bool:
        """
        Mutate an individual
        """
        pass
