import numpy as np


class Random:
    
    """
    Indicates that the value will be randomly generated during initialisation.
    """

    def __init__(self, seed=None):
        self.seed = seed

        np.random.seed(seed)

    
    def __str__(self):
        return "Random"
    
    def __repr__(self):
        return "Random"
    
Randomized = Random()
    
class Unknown:
    
    """
    Type for unknown values.
    """
    
    def __str__(self):
        return "Unknown"
    
    def __repr__(self):
        return "Unknown"