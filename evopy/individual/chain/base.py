""" 
Defines the ChainIndividual class, which is a subclass of BaseIndividual.

This class represents an individual with a chain of values.
This class is the base class for all individuals with a chain of values.
"""

import builtins
import numpy as np
from evopy.individual.base import BaseIndividual
from numpy.typing import NDArray


class ChainIndividual(BaseIndividual):
    """
    Base class for all individuals with a chain of values.

    Parameters:
        * individual_size (int): The size of the chain of an individual
            Min: 0
        * type_value (type): The type of the chain's elements
            Choices: int, float
        * min_value (float): The minimum value of the chain's elements
        * max_value (float): The maximum value of the chain's elements
    """

    component_type: str = "Chain"
    _type_value: type
    _min_val: float
    _max_val: float
    _size: int

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        super().__init__(options)

        match self._type_value:
            case builtins.int:
                self._chain = np.random.randint(self._min_value, self._max_value + 1, self._size)
            case builtins.float:
                self._chain = np.random.uniform(self._min_value, self._max_value, self._size)
            case _:
                raise NotImplementedError

    @classmethod
    def initialize(cls, options):
        super().initialize(options)
        cls._type_value = options.type_value
        cls._min_value = options.min_value
        cls._max_value = options.max_value
        cls._size = options.individual_size

    def _init(self, data):
        super()._init(data)
        chain = data.get("chain", None)
        if chain is None:
            self.log(level="warning", msg="No chain data")
        else:
            assert len(chain) == self._size, f"Chain should be of size {self._size} but {chain} has size {len(chain)}"
        self._chain = chain if chain is not None else np.random.permutation(self._size)
        self._assert_is_chain()

    def get_data(self) -> dict:
        return super().get_data() | {"chain": self._chain.copy()}

    def get_chain(self) -> NDArray:
        """
        Get the chain of values of the individual.
        """
        return self._chain
    
    def get_bounds(self) -> tuple:
        """
        Get the bounds of the individual.
        """
        return self._min_value, self._max_value
    
    def get_type(self) -> type:
        """
        Get the type of the individual.
        """
        return self._type_value

    def _assert_is_chain(self):
        assert np.issubdtype(
            self._chain.dtype, self._type_value
        ), f"Chain should have values of type {self._type_value}"
        assert np.all(
            self._chain >= self._min_value
        ), f"Chain should have values greater or equal to {self._min_value}"
        assert np.all(
            self._chain <= self._max_value
        ), f"Chain should have values lower or equal to {self._max_value}"
        assert (
            len(self._chain) == self._size
        ), f"Chain should be of size {self._size} but {self._chain} has size {len(self._chain)}"

    def __len__(self) -> int:
        return self._size

    def __setitem__(self, index: int, value) -> None:
        assert type(value) == self._type_value, f"Chain should be of type {self._type_value}, but {value} has type {type(value)}"
        self._chain[index] = value

    def __getitem__(self, index: int):
        return self._chain[index]

    def __eq__(self, other):
        if not isinstance(other, ChainIndividual):
            return False
        return np.array_equal(self._chain, other._chain)
