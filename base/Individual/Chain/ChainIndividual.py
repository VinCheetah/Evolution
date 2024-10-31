from base.Individual.BaseIndividual import BaseIndividual
import numpy as np
import builtins
from numpy.typing import NDArray


class ChainIndividual(BaseIndividual):

    _component_type: str = "Chain"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        super().__init__(options)

        self._type_value: type = options.type_value
        self._min_value: int = options.min_value
        self._max_value: int = options.max_value

        self._size: int = options.individual_size
        match self._type_value:
            case builtins.int:
                self._chain = np.random.randint(self._min_value, self._max_value + 1, self._size)
            case builtins.float:
                self._chain = np.random.uniform(self._min_value, self._max_value, self._size)
            case _:
                raise NotImplementedError

    @classmethod
    def _create(cls, options) -> "ChainIndividual":
        return cls(options)

    def __len__(self) -> int:
        return self._size

    def __setitem__(self, index, value) -> None:
        self._chain[index] = value

    def __getitem__(self, index: int) -> int:
        return self._chain[index]

    def _get_data(self) -> dict:
        return super()._get_data() | {"chain": self._chain.copy()}

    def _init(self, data):
        super()._init(data)
        chain = data.get("chain", None)
        if chain is None:
            self.log(level="warning", msg="No chain data")
        else:
            assert len(chain) == self._size, f"Chain should be of size {self._size} but {chain} has size {len(chain)}"
        self._chain = chain if chain is not None else np.random.permutation(self._size)
        self._assert_is_chain()

    def _assert_is_chain(self):
        assert np.issubdtype(self._chain.dtype, self._type_value), f"Chain should have values of type {self._type_value}"
        assert np.all(self._chain >= self._min_value), f"Chain should have values greater or equal to {self._min_value}"
        assert np.all(self._chain <= self._max_value), f"Chain should have values lower or equal to {self._max_value}"
        assert len(self._chain) == self._size, f"Chain should be of size {self._size} but {self._chain} has size {len(self._chain)}"

    def __eq__(self, other):
        if not isinstance(other, ChainIndividual):
            return False
        return np.array_equal(self._chain, other._chain)
