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

    component_type = "Chain"
    requirements = [
        ("individual", ChainIndividual),
        ("mutator", ChainMutator),
        ("crosser", ChainCrosser),
    ]
