from evopy.environment import BaseEnvironment
from evopy.graphic import BaseGraphic

class GraphicEnvironment(BaseEnvironment):

    _active_graphic: bool = True

    def __init__(self, options, **kwargs):
        self._components.append("graphic")

        self._active_graphic = self._active_graphic and options.active_graphic
        if self._active_graphic:
            self.graphic: BaseGraphic = options.graphic

        super().__init__(options, **kwargs)

    def init_evolution(self):
        super().init_evolution()
        if self._active_graphic:
            self.graphic.init_evolution()

    def end_evolution(self):
        super().end_evolution()
        if self._active_graphic:
            self.graphic.end_evolution()

    def update_graphic(self):
        if self._active_graphic:
            self.log("info", f"Graphic is updating")
            self.graphic.update()

    def _new_generation(self):
        super()._new_generation()
        self.update_graphic()
