"""
Defines the BinaryChainMixin class.
It is used to add binary chain requirements and suggestions to the environment.
"""

from evopy.environment.mixins.chain.base import ChainMixin
from evopy.individual import BinaryChainIndividual
from evopy.mutator import BinaryChainMutator


class BinaryChainMixin(ChainMixin):
    """
    This is the BinaryChainMixin class.
    It is used to add binary chain requirements and suggestions to the environment.
    """

    component_type = "BinaryChain"
    requirements = [
        ("individual", BinaryChainIndividual),
        ("mutator", BinaryChainMutator),
    ]