from base.Environment.BaseEnvironment import BaseEnvironment
from base.Individual.Permutation.PermuIndividual import PermuIndividual
from base.Evaluator.PermuEvaluator import PermuEvaluator
from base.Selector.EliteSelector import EliteSelector
from base.Mutator.PermuMutator import PermuMutator
from base.Crosser.PermuCrosser import PermuCrosser


class PermuEnvironment(BaseEnvironment):

    _component_type = "Permu"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        options.assert_subtype("individual", PermuIndividual)
        options.assert_subtype("mutator", PermuMutator)
        options.assert_subtype("crosser", PermuCrosser)
        options.assert_subtype("evaluator", PermuEvaluator)
        BaseEnvironment.__init__(self, options)
