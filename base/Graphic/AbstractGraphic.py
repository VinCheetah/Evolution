from abc import ABC, abstractmethod


class AbstractGraphic(ABC):

    @abstractmethod
    def update(self):
        pass
