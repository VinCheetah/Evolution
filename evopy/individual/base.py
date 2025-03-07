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

    Parameters:
        * invalid_fit_value (float) : Fitness value for an individual that could not be fit
        * unevaluated_time (float) : Time for an individual that could not be evaluated
    """

    component_name: str = "Individual"
    component_type: str = "Base"
    _id_counter: int = 0

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        BaseComponent.__init__(self, options)
        self._id: int
        self.set_new_id()

        self._is_evaluated: bool = False
        self._origin: list = ["void"]
        self._gen_birth: int = 0
        self._survived_gen: int = 0
        self._evaluation: tuple[float, float, str] = (0., 0., "")


    @classmethod
    def from_data(
        cls, options, data: dict, origin: list[str], set_id: int = -1
    ) -> "BaseIndividual":
        """
        Create an individual from data.

        Parameters
        ----------
        options : Options
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
            new_ind.set_new_id(set_id)
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

    def set_new_id(self, new_id: int | None = None):
        """
        Get a new id for the individual.
        """
        if new_id is None:
            new_id = BaseIndividual._id_counter
            BaseIndividual._id_counter += 1
        self._id = new_id

    def get_id(self) -> int:
        """
        Get the id of the individual.
        """
        return self._id

    def get_is_evaluated(self):
        """
        Returns whether the individual is evaluated.
        """
        return self._is_evaluated

    def has_mutate(self):
        """
        Update the individual after a mutation.
        It gets a new id, and is not evaluated nor valid.
        Its origin is updated too.
        """
        self._origin_update_mutation()
        self.set_new_id()
        self._is_evaluated = False

    def _origin_update_mutation(self):
        """
        Update the origin of the individual after a mutation.
        """
        self._origin.append(f"mutation {self._id}")

    def _init(self, data):
        self._origin = data.get("origin", [])

    @property
    def is_valid(self):
        """ 
        Returns if the individual has been evaluated successfully
        """
        return self._is_evaluated and self.err_eval == ""

    @property
    def fitness(self) -> float:
        """
        Returns the fitness of the individual if it is valid, else the invalid_fit_value.
        """
        return self._evaluation[0] if self.is_valid else self._options.invalid_fit_value

    @property
    def eval_time(self) -> float:
        """
        Returns the evaluation time of the individual if it is evaluated, else the unevaluated_time.
        """
        return self._evaluation[1] if self._is_evaluated else self._options.unevaluated_time

    @property
    def err_eval(self) -> str:
        """ 
        Returns the error message of the evaluation.
        If the evaluation did not raise any errors, then it returns ''.
        If the indvidual is not evaluated, then it returns 'None'.
        """
        return self._evaluation[2] if self._is_evaluated else "None"

    def new_generation(self):
        """
        Update the individual after a new generation.
        """
        self._survived_gen += 1

    def register_evaluation(self, fitness: float, time: float, err_eval: str):
        """
        Register the evaluation of the individual.
        """
        self._is_evaluated = True
        self._evaluation = (fitness, time, err_eval)

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
            "is_evaluated": self._is_evaluated,
            "evaluation": self._evaluation,
            "survived_gen": self._survived_gen,
            "gen_birth": self._gen_birth,
        }

    def transfer_eval_data(self, ind: "BaseIndividual"):
        """
        Transfer the evaluation data from another individual.
        """
        side_data = ind.get_eval_data()
        self._is_evaluated = side_data["is_evaluated"]
        self._evaluation = side_data["evaluation"]
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
        return (
            f"Individual {self._id} : {self.fitness:.3f} - from {self._origin} - "
            f"{self._survived_gen} generations survived - "
            f"history : {' <- '.join(self._origin[::-1])}"
        )

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
        return self._id == other.get_id()

    def __lt__(self, other):
        return self.fitness < other.fitness

    def __le__(self, other):
        return self.fitness <= other.fitness

    def __gt__(self, other):
        return self.fitness > other.fitness

    def __ge__(self, other):
        return self.fitness >= other.fitness
