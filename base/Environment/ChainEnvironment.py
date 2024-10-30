from base.Environment.BaseEnvironment import BaseEnvironment
from base.Selector.TournamentSelector import TournamentSelector
from base.Individual.ChainIndividual import ChainIndividual
from base.Crosser.ChainCrosser import ChainCrosser
from base.Mutator.ChainMutator import ChainMutator


class ChainEnvironment(BaseEnvironment):

    _component_type = "Chain"

    def __init__(self, options, **kwargs):
        if not issubclass(options.individual, ChainIndividual):
            options.individual = ChainIndividual
        if not issubclass(options.mutator, ChainMutator):
            options.mutator = ChainMutator
        if not issubclass(options.crosser, ChainCrosser):
            options.crosser = ChainCrosser
        options.update(kwargs)
        super().__init__(options)
