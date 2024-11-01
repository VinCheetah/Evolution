from base.Crosser.BaseCrosser import BaseCrosser
import builtins


class MeanChainCrosser(BaseCrosser):

    _component_type = "MeanChain"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseCrosser.__init__(self, options)
        self._type_value = options.type_value

    def _cross(self, ind1, ind2):
        match self._type_value:
            case builtins.int:
                return {"chain": (ind1._chain + ind2._chain) // 2}
            case builtins.float:
                return {"chain": (ind1._chain + ind2._chain) / 2}
            case _:
                raise ValueError(f"Invalid type value {self._type_value}")
