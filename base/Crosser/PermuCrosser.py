from base.Crosser.BaseCrosser import BaseCrosser
from base.Individual.PermuIndividual import PermuIndividual
import random as rd
import numpy as np

import time
class PermuCrosser(BaseCrosser):

    _component_name: str = "Crosser"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseCrosser.__init__(self, options)

    def _cross(self, ind1: PermuIndividual, ind2: PermuIndividual) -> dict:
        debug = False
        if debug:
            print(ind1._permutation, ind2._permutation)
        size: int = len(ind1)
        start: int = rd.randint(0, size-1)

        path: list[None | int] = [None] * (size * 2)
        seen: list[bool] = [False] * size
        beg: int = size - 1
        end: int = size + 1
        path[size] = start
        seen[start] = True
        idx_1: int = np.flatnonzero(ind1._permutation == start)[0]
        idx_2: int = np.flatnonzero(ind2._permutation == start)[0]


        while end - beg <= size:
            if rd.random() < .5:
                while seen[ind1[idx_1 % size]]:
                    if debug:
                        print(f"Already seen : {ind1[idx_1 % size]}")
                        time.sleep(0.01)
                    idx_1 += 1
                seen[ind1[idx_1 % size]] = True
                path[end] = ind1[idx_1 % size]
                end += 1
            else:
                while seen[ind2[idx_2 % size]]:
                    if debug:
                        print(f"Already seen : {ind2[idx_2 % size]}")
                    idx_2 -= 1
                seen[ind2[idx_2 % size]] = True
                path[beg] = ind2[idx_2 % size]
                beg -= 1
            if debug:
                print(path[beg+1:end])

        return {"permutation": np.array(path[beg+1: end])}
