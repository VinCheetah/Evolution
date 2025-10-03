""" 
Defines the base class for permutation individuals
"""

import numpy as np
import numpy.typing as npt
from evopy.individual.base import BaseIndividual


class PermuIndividual(BaseIndividual):
    """
    Base class for permutation individuals

    Parameters:
        * individual_size (int): The size of the permutation of an individual
    """

    component_type = "Permutation"
    _size: int

    def __init__(self, options):
        super().__init__(options)
        self._permutation: npt.NDArray[np.int_] = np.random.permutation(self._size)
        
    @classmethod
    def initialize(cls, options):
        super().initialize(options)
        cls._size = options.individual_size

    def get_data(self) -> dict:
        return super().get_data() | {"permutation": self._permutation.copy()}
    
    def get_permutation(self) -> np.array:
        """ 
        Returns the permutation 
        """
        return self._permutation

    def _init(self, data):
        super()._init(data)
        permutation = data.get("permutation", None)
        if permutation is None:
            self.log(level="warning", msg="No permutation data")
        else:
            assert (
                len(permutation) == self._size
            ), f"Permutation should be of size {self._size} but {permutation} has size {len(permutation)}"
        self._permutation = permutation if permutation is not None else np.random.permutation(self._size)
        self._assert_is_perm()

    def swap(self, idx1, idx2) -> bool:
        """
        Swap the elements at index idx1 and idx2
        """

        self._permutation[idx1], self._permutation[idx2] = (
            self._permutation[idx2],
            self._permutation[idx1],
        )
        return True

    def move_element(self, idx: int, new_pos: int) -> bool:
        """
        Move the element at index idx to the new position new_pos

        Args:
            idx (int): the index of the element to move
                Should be between 0 and the size of the permutation - 1
            new_pos (int): the new position of the element
                Should be between 0 and the size of the permutation - 1

        Returns:
            bool: True if the element has been moved, False otherwise
        """
        if idx == new_pos:
            return False
        new_elt = self._permutation[idx]
        if idx < new_pos:
            if new_pos >= self._size:
                self._permutation[idx : self._size - 1] = self._permutation[idx + 1 :]
                self._permutation[-1] = self._permutation[0]
            else:
                self._permutation[idx:new_pos] = self._permutation[idx + 1 : new_pos + 1]
        else:
            if new_pos == 0:
                self._permutation[1 : idx + 1] = self._permutation[:idx]
                self._permutation[0] = self._permutation[-1]
            else:
                self._permutation[new_pos : idx + 1] = self._permutation[new_pos - 1 : idx]
        self._permutation[new_pos] = new_elt
        return True

    def move_elements(self, idx: int, dec: int, length: int, reverse=False) -> bool:
        """
        Move the elements from idx to idx+length-1 to the right by dec positions

        Args:
            idx (int): the index of the first element to move
                Should be between 0 and the size of the permutation - 1
            dec (int): the number of positions to move the elements to the right
                Should be between 1 and the size of the permutation - 1
            length (int): the number of elements to move
                Should be between 1 and the size of the permutation - 2
            reverse (bool): if True, the elements will be reversed

        Returns:
            bool: True if the move was successful, False otherwise
        """
        dec = dec % (self._size - length - 1) + 1

        if length == 0 or dec == 0:
            return False

        dec_idx_l = max(0, idx + length - self._size)
        permutation_less = np.concatenate(
            [self._permutation[idx + length - dec_idx_l :], self._permutation[dec_idx_l:idx]]
        )
        permutation_removed = np.concatenate(
            [self._permutation[idx : idx + length - dec_idx_l], self._permutation[:dec_idx_l]]
        )
        if reverse:
            permutation_removed = permutation_removed[::-1]
        self._permutation = np.concatenate([permutation_less[:dec], permutation_removed, permutation_less[dec:]])
        self._assert_is_perm()
        return True

    def reverse(self, idx1, idx2):
        """
        Reverse the elements from idx1 to idx2
        """
        self._permutation[idx1 : idx2 + 1] = self._permutation[idx1 : idx2 + 1][::-1].copy()
        return True

    def shuffle(self, idx1, idx2):
        """
        Shuffle the elements from idx1 to idx2
        """
        self._permutation[idx1 : idx2 + 1] = np.random.permutation(
            self._permutation[idx1 : idx2 + 1]
        )
        return True

    def _assert_is_perm(self):
        assert np.array_equal(
            np.sort(self._permutation), np.arange(self._size)
        ), f"Permutation {self._permutation} is not a permutation of {self._size}"

    def __eq__(self, other) -> bool:
        return isinstance(other, PermuIndividual) and np.array_equal(
            self._permutation, other._permutation
        )

    def __len__(self) -> int:
        return self._size

    def __setitem__(self, index, value) -> None:
        self._permutation[index] = value

    def __getitem__(self, index: int) -> int:
        return int(self._permutation[index])
