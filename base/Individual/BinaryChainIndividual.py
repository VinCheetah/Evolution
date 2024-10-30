from base.Individual.ChainIndividual import ChainIndividual


class BinaryChainIndividual(ChainIndividual):

    _component_type: str = "BinaryChain"

    def __init__(self, options, **kwargs):

        options.update(kwargs)
        options.type_value = int
        options.min_value = 0
        options.max_value = 1
        super().__init__(options)

    def flip(self, index: int):
        self._chain[index] = 1 - self._chain[index]
