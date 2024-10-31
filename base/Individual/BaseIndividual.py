from base.Component.BaseComponent import BaseComponent
from base.Individual.AbstractIndividual import AbstractIndividual
import numpy as np
from copy import deepcopy


class BaseIndividual(BaseComponent, AbstractIndividual):

    _id_counter: int = 0
    _component_name: str = "Individual"
    _component_type: str = "Base"

    def __init__(self, options, **kwargs):
        BaseComponent.__init__(self, options)
        self._id: int
        self.get_new_id()


        self._unvalid_fit_value = options.get("unvalid_fit_value", np.NaN)
        self._unevaluated_time = options.get("unevaluated_time", np.NaN)
        self._type: str = options.get("type", "None")

        self._is_evaluated: bool = False
        self._is_valid: bool = False

        self._origin: list = ["void"]

        self._fitness: float = 0.
        self._eval_time: float
        self._err_eval: str = ""
        self._gen_birth: int = 0
        self._survived_gen: int = 0

    @classmethod
    def create(cls, options, **kwargs) -> "BaseIndividual":
        # cls._valid_create_args(*args, **kwargs)
        new_ind = cls._create(options, **kwargs)
        assert isinstance(new_ind, BaseIndividual)
        return new_ind

    def show(self):
        return f"{self._id} : {self.fitness:.3f}"

    def get_new_id(self):
        self._id = BaseIndividual._id_counter
        BaseIndividual._id_counter += 1

    def change_id(self, new_id):
        self._id = new_id
        self._id_counter -= 1

    def __len__(self):
        raise NotImplementedError

    @classmethod
    def from_data(cls, options, data, origin: list, set_id=None) -> "BaseIndividual":
        new_ind = cls(options)
        new_ind._init(data)

        new_ind.set_origin(origin)
        if set_id is not None:
            new_ind.change_id(set_id)
        return new_ind

    def has_mutate(self):
        self._origin_update_mutation()
        self.get_new_id()
        self._is_evaluated = False
        self._is_valid = False
        self._err_eval = ""

    def _origin_update_mutation(self):
        self._origin.append(f"mutation {self._id}")

    def _init(self, data):
        self._origin = data.get("origin", [])

    @property
    def fitness(self):
        return self._fitness if self._is_valid else self._unvalid_fit_value

    @property
    def eval_time(self):
        return self._eval_time if self._is_evaluated else self._unevaluated_time

    def new_generation(self):
        self._survived_gen += 1

    def register_evaluation(self, fitness: float, time: float, err_eval: str):
        self._eval_time = time
        self._is_evaluated = True
        if err_eval == "":
            self._fitness = fitness
            self._is_valid = True
        else:
            self._is_valid = False
            self._err_eval = err_eval
            self.log(level="debug", msg=f"Evaluation error: {err_eval}")

    def _get_data(self) -> dict:
        return {"origin": self._origin}

    def copy(self):
        copy = self.from_data(self._options, deepcopy(self._get_data()), self._origin, set_id=self._id)
        copy._fitness = self._fitness
        copy._eval_time = self._eval_time
        copy._survived_gen = self._survived_gen
        copy._gen_birth = self._gen_birth
        copy._is_evaluated = self._is_evaluated
        copy._err_eval = self._err_eval
        copy._is_valid = self._is_valid
        return copy

    def report(self) -> str:
        return f"Individual {self._id} : {self.fitness:.3f} - from {self._origin} - {self._survived_gen} generations survived - history : {' <- '.join(self._origin[::-1])}"

    def set_curr_origin(self, origin: str):
        assert self._origin[-1] == "void", "Origin already set"
        self._origin[-1] = origin

    def set_origin(self, origin: list):
        self._origin = origin

    def __eq__(self, other):
        return self._id == other._id

    def __lt__(self, other):
        return self.fitness < other.fitness

    def __le__(self, other):
        return self.fitness <= other.fitness

    def __gt__(self, other):
        return self.fitness > other.fitness

    def __ge__(self, other):
        return self.fitness >= other.fitness
