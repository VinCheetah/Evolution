from abc import ABC, abstractmethod


class AbstractEvaluator(ABC):

    @abstractmethod
    def evaluate(self, population) -> None:
        """
        Evaluate individuals from the population
        """
        pass
