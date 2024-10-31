from base.Individual.Chain.ChainIndividual import ChainIndividual
from base.Selector.TournamentSelector import TournamentSelector
from base.Environment.BaseEnvironment import BaseEnvironment
from base.Crosser.ChainCrosser import ChainCrosser
from base.Mutator.ChainMutator import ChainMutator


class ChainEnvironment(BaseEnvironment):

    _component_type = "Chain"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        options.assert_subtype("individual", ChainIndividual)
        options.assert_subtype("mutator", ChainMutator)
        options.assert_subtype("crosser", ChainCrosser)
        BaseEnvironment.__init__(self, options)
