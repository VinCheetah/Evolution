"""
Defines the BinaryChainIndividual class, which is a subclass of ChainIndividual.

This class represents an individual with a binary chain of values.
This class is the base class for all individuals with a binary chain of values.
"""

from evopy.individual.chain.base import ChainIndividual


class BinaryChainIndividual(ChainIndividual):
    """
    Base class for all individuals with a binary chain of values.

    Parameters:
        type_value (type): The type of the individual
            Fixed: int
        * min_value (float): The minimum value of the chain's elements
            Fixed: 0
        * max_value (float): The maximum value of the chain's elements
            Fixed: 1
    """

    component_type: str = "BinaryChain"

    @classmethod
    def fixed_options(cls):
        return {
            "type_value": int,
            "min_value": 0,
            "max_value": 1,
        } | super().fixed_options()

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        super().__init__(options)


    def flip(self, index: int):
        """
        Flip the value at the given index.
        """
        self._chain[index] = 1 - self._chain[index]

    def flip_all(self):
        """
        Flip all the values.
        """
        self._chain = 1 - self._chain
