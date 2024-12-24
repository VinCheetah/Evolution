from evopy.environment.graphic import GraphicEnvironment
from evopy.individual import ChainIndividual
from evopy.crosser import ChainCrosser
from evopy.mutator import ChainMutator


class ChainEnvironment(GraphicEnvironment):

    _component_type = "Chain"

    def __init__(self, options, **kwargs):
        options.assert_subtype("individual", ChainIndividual)
        options.assert_subtype("mutator", ChainMutator)
        options.assert_subtype("crosser", ChainCrosser)
        options.update(kwargs)
        GraphicEnvironment.__init__(self, options)
