"""
Defines the ChainMixin class.
It is used to add chain requirements and suggestions to the environment.
"""

from evopy.component.mixin import Mixin
from evopy.individual import ChainIndividual
from evopy.crosser import ChainCrosser
from evopy.mutator import ChainMutator


class ChainMixin(Mixin):
    """
    This is the ChainMixin class.
    It is used to add chain requirements and suggestions to the environment.
    """

    Mixin.set_component_type("Chain")
    Mixin.add_requirement("individual", ChainIndividual)
    Mixin.add_requirement("mutator", ChainMutator)
    Mixin.add_requirement("crosser", ChainCrosser)
