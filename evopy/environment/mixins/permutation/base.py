"""
Defines the PermuEnvironment class, which is a subclass of GraphicEnvironment.
It is used to add permutation capabilities to the environment.
"""

from evopy.component.mixin import Mixin
from evopy.individual import PermuIndividual
from evopy.evaluator import PermuEvaluator
from evopy.mutator import PermuMutator
from evopy.crosser import PermuCrosser


class PermuMixin(Mixin):
    """
    This is the PermuEnvironment class.
    It is used to add permutation capabilities to the environment.
    """

    Mixin.set_component_type("Permutation")
    Mixin.add_requirement("individual", PermuIndividual)
    Mixin.add_requirement("mutator", PermuMutator)
    Mixin.add_requirement("crosser", PermuCrosser)
    Mixin.add_requirement("evaluator", PermuEvaluator)
