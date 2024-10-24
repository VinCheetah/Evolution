from abc import ABC, abstractmethod


class AbstractElite(ABC):

    @abstractmethod
    def update(self, population) -> bool:
        pass
