""" 
Defines the BaseIndividual class.
This class is the base class for all individuals.
"""

from abc import abstractmethod
from copy import deepcopy
from evopy.component import BaseComponent


class BaseIndividual(BaseComponent):
    """
    Base class for all individuals.


    Attributes
    ----------
    _id_counter : int
        The counter for the id of the individuals.
    """

    _id_counter: int = 0
    _component_name: str = "Individual"
    _component_type: str = "Base"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseComponent.__init__(self, options)
        self._id: int
        self.get_new_id()

        self._unvalid_fit_value = options.unvalid_fit_value
        self._unevaluated_time = options.unevaluated_time

        self._is_evaluated: bool = False
        self._is_valid: bool = False

        self._origin: list = ["void"]

        self._fitness: float = 0.0
        self._eval_time: float
        self._err_eval: str = ""
        self._gen_birth: int = 0
        self._survived_gen: int = 0

    @classmethod
    def from_data(cls, options, data: dict, origin: list[str], set_id:int=-1) -> "BaseIndividual":
        """
        Create an individual from data.

        Parameters
        ----------
        options : dict
            The options of the individual.
        data : dict
            The data of the individual.
        origin : list[str]
            The origin of the individual.
        set_id : int, optional (default=-1)
            The id of the individual. If None, a new id is generated.

        Returns
        -------
        BaseIndividual
            The individual created from data.
        """
        new_ind = cls(options)
        new_ind._init(data)

        new_ind.set_origin(origin)
        if set_id := -1:
            new_ind.change_id(set_id)
        return new_ind

    @classmethod
    def create(cls, options, **kwargs) -> "BaseIndividual":
        """
        Create a new individual
        """
        # cls._valid_create_args(*args, **kwargs)
        new_ind = cls._create(options, **kwargs)
        assert isinstance(new_ind, BaseIndividual)
        return new_ind

    @classmethod
    @abstractmethod
    def _create(cls, options, **kwargs) -> "BaseIndividual":
        """
        Create a random individual
        """

    @abstractmethod
    def _init(self, data) -> None:
        """
        Initialize individual from data
        """

    def show(self):
        """
        Show the individual, as a string containing its id and fitness.
        """
        return f"{self._id} : {self.fitness:.3f}"

    def get_new_id(self):
        """
        Get a new id for the individual.
        """
        self._id = BaseIndividual._id_counter
        BaseIndividual._id_counter += 1

    def get_id(self):
        """
        Get the id of the individual.
        """
        return self._id

    def change_id(self, new_id):
        """
        Change the id of the individual.
        """
        self._id = new_id
        self._id_counter -= 1

    def has_mutate(self):
        """
        Update the individual after a mutation.
        It gets a new id, and is not evaluated nor valid.
        Its origin is updated too.
        """
        self._origin_update_mutation()
        self.get_new_id()
        self._is_evaluated = False
        self._is_valid = False
        self._err_eval = ""

    def _origin_update_mutation(self):
        """
        Update the origin of the individual after a mutation.
        """
        self._origin.append(f"mutation {self._id}")

    def _init(self, data):
        self._origin = data.get("origin", [])

    @property
    def fitness(self):
        """
        Returns the fitness of the individual if it is valid, else the unvalid_fit_value.
        """
        return self._fitness if self._is_valid else self._unvalid_fit_value

    @property
    def eval_time(self):
        """
        Returns the evaluation time of the individual if it is evaluated, else the unevaluated_time.
        """
        return self._eval_time if self._is_evaluated else self._unevaluated_time

    def new_generation(self):
        """
        Update the individual after a new generation.
        """
        self._survived_gen += 1

    def register_evaluation(self, fitness: float, time: float, err_eval: str):
        """
        Register the evaluation of the individual.
        """
        self._eval_time = time
        self._is_evaluated = True
        if err_eval == "":
            self._fitness = fitness
            self._is_valid = True
        else:
            self._is_valid = False
            self._err_eval = err_eval
            self.log(level="debug", msg=f"Evaluation error: {err_eval}")

    def get_data(self) -> dict:
        """
        Get the data of the individual.
        """
        return {"origin": self._origin}

    def get_eval_data(self):
        """
        Get the evaluation data of the individual.
        """
        return {
            "fitness": self._fitness,
            "eval_time": self._eval_time,
            "is_evaluated": self._is_evaluated,
            "err_eval": self._err_eval,
            "is_valid": self._is_valid,
            "survived_gen": self._survived_gen,
            "gen_birth": self._gen_birth,
        }

    def transfer_eval_data(self, ind: "BaseIndividual"):
        """
        Transfer the evaluation data from another individual.
        """
        side_data = ind.get_eval_data()
        self._fitness = side_data["fitness"]
        self._eval_time = side_data["eval_time"]
        self._is_evaluated = side_data["is_evaluated"]
        self._err_eval = side_data["err_eval"]
        self._is_valid = side_data["is_valid"]
        self._survived_gen = side_data["survived_gen"]
        self._gen_birth = side_data["gen_birth"]

    def copy(self) -> "BaseIndividual":
        """
        Copy the individual.
        """
        copy = self.from_data(
            self._options, deepcopy(self.get_data()), self._origin, set_id=self._id
        )
        copy.transfer_eval_data(self)
        return copy

    def report(self) -> str:
        """
        Returns a description of the individual.
        """
        return f"Individual {self._id} : {self.fitness:.3f} - from {self._origin} - " \
               f"{self._survived_gen} generations survived - " \
               f"history : {' <- '.join(self._origin[::-1])}"

    def set_curr_origin(self, origin: str):
        """
        Set the current origin of the individual.
        Asserts that the origin is not already set.
        """
        assert self._origin[-1] == "void", "Origin already set"
        self._origin[-1] = origin

    def set_origin(self, origin: list):
        """
        Set the complete origin of the individual.
        """
        self._origin = origin

    def __len__(self):
        raise NotImplementedError

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
