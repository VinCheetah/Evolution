from base.Individual.BaseIndividual import BaseIndividual


class NNIndividual(BaseIndividual):

    _component_type: str = "NeuralNetwork"

    _sensors: list = []
    _interns: list = []
    _motors: list = []

    def __init__(self, options):
        super().__init__(options)
        self.max_links: int = options.get("max_links", 10)

        self._links: list

    def __attrs_post_init__(self):
        self.log("info", "NNIndividual initialized (not implemented)")
        self._links = []

    def _init(self, data):
        links = data.get("links", None)
        if links is None:
            self.log(level="warning", msg="No links data")
        self._links = links if links is not None else []

    @classmethod
    def set_sensors(cls, sensors):
        cls._sensors = sensors

    @classmethod
    def set_interns(cls, interns):
        cls._interns = interns

    @classmethod
    def set_motors(cls, motors):
        cls._motors = motors

    @classmethod
    def _create(cls, *args, **kwargs) -> "NNIndividual":
        return cls(*args, **kwargs)
