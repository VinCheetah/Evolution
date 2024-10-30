from base.Environment.ChainEnvironment import ChainEnvironment
from base.Individual.BinaryChainIndividual import BinaryChainIndividual
from base.Mutator.BinaryChainMutator import BinaryChainMutator


class BinaryChainEnvironment(ChainEnvironment):

    _component_type = "BinaryChain"


    def __init__(self, options, **kwargs):
        options.individual = BinaryChainIndividual
        options.mutator = BinaryChainMutator
        options.update(kwargs)
        super().__init__(options)
