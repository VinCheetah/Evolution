import random
from evopy.population import BasePopulation
from evopy.individual import NEATIndividual
from evopy.crosser import NeuralNetworkCrosser


class NEATCrosser(NeuralNetworkCrosser):
    """
    Implements NEAT crossover between two NEATIndividuals.

    Parameters:
        * disable_inheritance_prob (float): Probability of transmitting disability of a link to offspring
    """

    component_type = "NEAT"

    def __init__(self, options):
        super(NEATCrosser, self).__init__(options)
        self._disable_inheritance_prob: float = options.disable_inheritance_prob

    def _cross(self, ind1: NEATIndividual, ind2: NEATIndividual) -> dict:
        """
        Perform NEAT crossover between two NEATIndividuals.
        Returns a dict of data for a new child individual.
        """
        if ind1.fitness > ind2.fitness:
            fitter, weaker = ind1, ind2
        elif ind2.fitness > ind1.fitness:
            fitter, weaker = ind2, ind1
        else:  # if equal fitness, pick randomly
            fitter, weaker = random.choice([(ind1, ind2), (ind2, ind1)])

        child_nodes = set(map(lambda n: n.copy(), fitter.nodes.union(weaker.nodes)))
        child_connections = set()
        for conn in fitter.connections.union(weaker.connections):
            cg1, cg2 = None, None
            if conn in fitter.connections:
                cg1 = conn
            if conn in weaker.connections:
                if conn in fitter.connections:
                    cg2 = next(c for c in weaker.connections if c.id == conn.id)
                else:
                    cg2 = conn

            if cg1 and cg2:  # matching gene
                chosen = random.choice([cg1, cg2])
                child_connections.add(chosen.copy())
                if not cg1.enabled or not cg2.enabled:
                    if random.random() < self._disable_inheritance_prob:
                        # Get the copy we just added and modify it
                        for child_conn in child_connections:
                            if child_conn.id == chosen.id:
                                if child_conn.enabled:
                                    child_conn.switch()
                                break
            elif cg1:  # disjoint/excess from fitter
                child_connections.add(cg1.copy())
            elif cg2 and fitter.fitness == weaker.fitness:
                # Only if fitter == weaker (same fitness) can weaker contribute excess genes
                child_connections.add(cg2.copy())

        data = {
            "nodes": child_nodes,
            "connections": child_connections,
        }
        return data
