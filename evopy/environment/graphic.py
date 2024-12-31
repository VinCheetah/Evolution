"""
Defines the GraphicEnvironment class, which is a subclass of BaseEnvironment.
It is used to add graphic capabilities to the environment.
"""

from evopy.environment.base import BaseEnvironment
from evopy.graphic import BaseGraphic


class GraphicEnvironment(BaseEnvironment):
    """
    GraphicEnvironment class, subclass of BaseEnvironment.
    It is used to add graphic capabilities to the environment.
    """

    def __init__(self, options, **kwargs):
        self._components.append("graphic")
        self._activations["graphic"] = True and options.active_graphic

        if self.is_active("graphic"):
            self.graphic: BaseGraphic = options.graphic

        BaseEnvironment.__init__(self, options, **kwargs)

    def init_evolution(self):
        super().init_evolution()
        if self.is_active("graphic"):
            self.graphic.init_evolution()

    def end_evolution(self):
        super().end_evolution()
        if self.is_active("graphic"):
            self.graphic.end_evolution()

    def update_graphic(self):
        """
        Updates the graphic component.
        """
        if self.is_active("graphic"):
            self.log("info", "Graphic is updating")
            self.graphic.update()

    def _new_generation(self):
        super()._new_generation()
        self.update_graphic()
