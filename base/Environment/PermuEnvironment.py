from base.Crosser.PermuCrosser import PermuCrosser
from base.Environment.BaseEnvironment import BaseEnvironment
from base.Individual.PermuIndividual import PermuIndividual
from base.Evaluator.PermuEvaluator import PermuEvaluator
from base.Selector.EliteSelector import EliteSelector
from base.Mutator.PermuMutator import PermuMutator


class PermuEnvironment(BaseEnvironment):

    def __init__(self, options, **kwargs):
        options.individual = PermuIndividual
        options.evaluator = PermuEvaluator
        options.selector = EliteSelector
        options.mutator = PermuMutator
        options.crosser = PermuCrosser
        options.update(kwargs)
        super().__init__(options)
