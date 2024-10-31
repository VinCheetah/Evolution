from base.Individual.Chain.BinaryChainIndividual import BinaryChainIndividual
from base.Environment.ChainEnvironment import ChainEnvironment
from base.Mutator.BinaryChainMutator import BinaryChainMutator


class BinaryChainEnvironment(ChainEnvironment):

    _component_type = "BinaryChain"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        options.assert_subtype("individual", BinaryChainIndividual)
        options.assert_subtype("mutator", BinaryChainMutator)
        ChainEnvironment.__init__(self, options)
