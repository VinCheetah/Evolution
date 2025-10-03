from evopy.individual import NNIndividual
from evopy.mutator import BaseMutator


class NeuralNetworkMutator(BaseMutator):

    def __init__(self, options):
        super().__init__(options)

    def _mutate(self, individual: NNIndividual) -> bool:
        pass