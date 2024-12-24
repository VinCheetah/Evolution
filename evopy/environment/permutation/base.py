from evopy.environment.graphic import GraphicEnvironment
from evopy.individual import PermuIndividual
from evopy.evaluator import PermuEvaluator
from evopy.mutator import PermuMutator
from evopy.crosser import PermuCrosser


class PermuEnvironment(GraphicEnvironment):

    _component_type = "Permu"

    def __init__(self, options, **kwargs):
        options.record_subfolder = "permutation"
        options.update(kwargs)
        options.assert_subtype("individual", PermuIndividual)
        options.assert_subtype("mutator", PermuMutator)
        options.assert_subtype("crosser", PermuCrosser)
        options.assert_subtype("evaluator", PermuEvaluator)
        GraphicEnvironment.__init__(self, options)
