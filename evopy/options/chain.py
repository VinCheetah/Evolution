# Auto-generated preset
from evopy.crosser.chain.base import ChainCrosser
from evopy.evaluator.chain.base import ChainEvaluator
from evopy.individual.chain.base import ChainIndividual
from evopy.mutator.chain.base import ChainMutator
from evopy.utils.options import Options

chain = Options('unknown',
    individual=ChainIndividual,
    evaluator=ChainEvaluator,
    crosser=ChainCrosser,
    mutator=ChainMutator
)
