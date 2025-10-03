"""
Defines the BaseEnvironment class
This class is the base class for the environment
"""

import pickle
import random
from pathlib import Path
from typing import Any
from time import time
import numpy as np
from evopy.individual import BaseIndividual
from evopy.population import BasePopulation
from evopy.component import BaseComponent, Mixin
from evopy.evaluator import BaseEvaluator
from evopy.selector import BaseSelector
from evopy.mutator import BaseMutator
from evopy.crosser import BaseCrosser
from evopy.elite import BaseElite


class BaseEnvironment(BaseComponent):
    """
    Base class for environment

    Parameters:
        * individual (BaseIndividual): Class of the individuals
        * population (BasePopulation): Class of the population
        * evaluator (BaseEvaluator): Class of the evaluator
        * selector (BaseSelector): Class of the selector
        * crosser (BaseCrosser): Class of the crosser
        * mutator (BaseMutator): Class of the mutator
        * elite (BaseElite): Class of the elite

        * timeout (int): Maximal time to run an evolution in seconds. -1 means no timeout
            Min: -1
        * max_gen (int): Maximum number of generations
            Min: 0
        * random_seed (int): Random seed
            Min: 0
        * create_report (bool): Whether to create report for each generation
        * reproducing (bool): Reproduce an evolution using a previous record
        * from_beginning (bool): Whether to start from beginning if there is a reproducing record
        * evolution_record (Optional[dict]): Evolution record of an evolution. Should be given at the end of a tracking evolution
        * tracking (bool): Record the evolution
            Disable: record_folder, record_subfolder, record_file, record_file_spec
        * record_folder (str): Folder where to save the records
        * record_subfolder (str): Subfolder where to save the records
        * record_file (str): File where to save the records
        * record_file_spec (str): Spec of the file where to save the records

    """

    component_name: str = "Environment"
    component_type: str = "Base"

    _components: list[str] = ["individual", "evaluator", "selector", "population", "crosser", "mutator", "elite"]
    _activations: dict[str, bool] = {
        "individual": True,
        "crosser": True,
        "mutator": True,
        "evaluator": True,
        "selector": True,
        "population": True,
        "elite": True,
        "migration": True,
        "tracking": True,
    }

    @classmethod
    def make(cls, options):
        requirements = []
        while True:
            for comp in cls._components:
                comp: BaseComponent = options[comp]
                requirements.extend(comp.requirements)

    @classmethod
    def init_mixin(cls, options):
        pass

    @classmethod
    def get_components(cls) -> list:
        return cls._components

    def __init__(self, options):
        super().__init__(options)
        self._options.env = self
        self.random_seed: int = self._options.random_seed
        random.seed(self.random_seed)
        np.random.seed(self.random_seed)

        self._reproducing: bool = self._options.evolution_record is not None and self._options.reproducing
        if self._reproducing:
            self._evolution_record: dict = self._options.evolution_record
            self._evolution_process: list[tuple[int, str, Any]] = self._evolution_record["evolution_process"]
            self._evolution_process_idx: int = 0
            self._options.update(self._evolution_record["options"])
            if not self._options.from_beginning:
                self._options.population = self._evolution_record["last_population"]

        self.individual: BaseIndividual = self._options.individual
        self.crosser: BaseCrosser = self._options.crosser
        self.mutator: BaseMutator = self._options.mutator
        self.evaluator: BaseEvaluator = self._options.evaluator
        self.selector: BaseSelector = self._options.selector
        self.population: BasePopulation = self._options.population
        self.elite: BaseElite = self._options.elite

        self.check_requirements()
        self._init_components()

        self._tracking: bool = self.is_active("tracking") and self._options.tracking

        self._timeout: int = self._options.timeout
        self._max_gen: int = self._options.max_gen
        self._create_report: bool = self._options.create_report

        self._evolution_started: bool = False
        self._evolution_over: bool = False
        self._evo_time: float = 0.0
        self._extra_time: float = 0.0
        self._extra_time_start: float = 0.0
        self._n_gen: int = 0
        self._param_to_apply: set[tuple[str, Any]] = set()

        self._start_time: float
        self._stop_time: float
        self._data_report: dict

        if self._tracking:
            self._param_tracker: list[tuple[int, str, Any]] = []
            self._record_folder: str = self._options.record_folder
            self._record_subfolder: str = self._options.record_subfolder
            self._record_file: str = self._options.record_file
            self._record_file_spec: str = self._options.record_file_spec

        if self._reproducing and not self._options.from_beginning:
            self._n_gen = self._evolution_record["n_gen"]
            self._evo_time = self._evolution_record["evo_time"]

    def _init_mixin(self):
        if not isinstance(self, Mixin):
            return
        for comp_name, list_comp in self.get_requirements_mixin().items():
            for comp in list_comp:
                continue
                self.add_requirement(comp_name, comp)

    def check_requirements(self):
        for component_name, requirement_class in self.requirements:
            component_class = getattr(self, component_name)
            assert issubclass(component_class, requirement_class), (
                f"{component_name} requires {requirement_class.__name__}, but {component_class.__name__}"
                f"is not a subclass. Try to create an environment using the factory"
            )

    @classmethod
    def add_component(cls, component_name: str):
        """Add a component to the components list"""
        cls._components.append(component_name)

    def _init_components(self):
        """Initialize the components"""
        for component in self._components:
            self._init_component(component)

    def _init_component(self, component_name: str):
        """Initialize a component"""
        comp = getattr(self, component_name)
        if self._verif_init_comp(component_name):
            if False and comp.init_requires_environment:
                init_comp = comp(self, self._options)
            else:
                init_comp = comp(self._options)
            setattr(self, component_name, init_comp)
        else:
            comp.initialize(self._options)

    def _verif_init_comp(self, component_name) -> bool:
        """Verify if a component needs to be initialized"""
        used_comp = True if component_name in self._activations else self.is_active(component_name)
        need_init = component_name != "individual"
        not_init = isinstance(getattr(self, component_name), type)
        return need_init and not_init and used_comp

    def evolve(self):
        """Evolve the population"""
        self.init_evolution()
        self.evaluate()
        for _ in range(self._max_gen):
            if self._evolution_timeout():
                break
            self._new_generation()
        self.end_evolution()

    def _evolution_timeout(self) -> bool:
        """Check if the evolution has reached the timeout"""
        return self.time_since_start > self._timeout > 0

    def _start_extra_time(self):
        """Start the extra time"""
        self._extra_time_start = time()

    def _set_extra_time(self):
        """Set the extra time"""
        self._extra_time = time() - self._extra_time_start

    def init_evolution(self):
        """Initialize the evolution"""
        self._evolution_started = True
        self._evolution_over = False
        self._start_extra_time()
        self._start_time = time()

    def end_evolution(self):
        """End the evolution"""
        self._evolution_started = False
        self._evolution_over = True
        self._stop_time = time()
        self._evo_time += self._stop_time - self._start_time

        self.log("info", "Evolution is finished")
        self.log("info", f"Total time: {self._evo_time:.2f}s")

        if self._tracking:
            self._record_evolution()

    def is_active(self, component_name: str) -> bool:
        """Check if a component is active"""
        if component_name in self._activations:
            return self._activations[component_name]
        self.log("warning", f"Component {component_name} not found for activation")
        return False

    def _record_evolution(self):
        """Record the evolution"""
        rec_folder = Path(self._record_folder)
        rec_folder.mkdir(parents=True, exist_ok=True)
        rec_subfolder = Path(rec_folder / self._record_subfolder)
        rec_subfolder.mkdir(parents=True, exist_ok=True)
        record_file_name = self._record_file + "_" + self._record_file_spec + ".pkl"

        idx = 2
        while Path(rec_subfolder / self._record_file).exists():
            record_file_name = self._record_file + "_" + self._record_file_spec + f"_{idx}.pkl"
            idx += 1

        record_path = Path(rec_subfolder / record_file_name)
        with open(record_path, "wb") as f:
            pickle.dump(self._make_evolution_record(), f)

    def _make_evolution_record(self) -> dict[str, Any]:
        """Make the evolution record"""
        return {
            "options": self._options,
            "evo_time": self._evo_time,
            "n_gen": self._n_gen,
            "evolution_process": self._param_tracker,
            "last_population": self.population.get_population(),
        }

    def _record_param_update(self, parameter_name: str, value):
        """Record the parameter update"""
        self.log("info", f"Parameter {parameter_name} updated to {value}")
        self._param_tracker.append((self._n_gen, parameter_name, value))

    def update_parameter(self, parameter_name: str, value: Any) -> None:
        """Update a parameter"""
        self._param_to_apply.add((parameter_name, value))

    def _update_evolution_param(self):
        """Update the evolution parameters"""
        if self._param_to_apply:
            for param in self._param_to_apply:
                setattr(self, param[0], param[1])
                if self._tracking:
                    self._record_param_update(param[0], param[1])
            self._param_to_apply.clear()

    def _update_param_process(self):
        """Update the parameter process"""
        while (
            self._evolution_process_idx < len(self._evolution_process)
            and self._n_gen == self._evolution_process[self._evolution_process_idx][0]
        ):
            self.update_parameter(
                self._evolution_process[self._evolution_process_idx][1],
                self._evolution_process[self._evolution_process_idx][2],
            )
            self._evolution_process_idx += 1

    def init_new_generation(self):
        """Initialize a new generation"""
        self._n_gen += 1
        self.log("info", f"Generation {self._n_gen} started")
        if self._reproducing:
            self._update_param_process()
        self._update_evolution_param()

    @BaseComponent.record_time
    def new_generation(self):
        """
        New generation process : selection, migration, mutation, crossover, evaluation, elite update
        """
        self.select()
        self.migrate()
        self.cross()
        self.mutate()
        self.evaluate()
        self.update_elite()

    def _new_generation(self):
        """
        New generation process : selection, migration, mutation, crossover, evaluation, elite update
        The generation is encapsulated with the initialisation and a log report
        """
        self.init_new_generation()
        self._set_extra_time()
        self.new_generation()
        self._start_extra_time()
        self.log_report()

    def get_report(self):
        """Get the report"""
        return {
            "general": {
                "n_gen": self._n_gen,
                "time": int(self.time_since_start * 10) / 10,
            },
            "top": self.elite.best.fitness,
            "pop": int(self.population.best.fitness * 100) / 100,
            "mean": int(np.mean([ind.fitness for ind in self.population]) * 100) / 100,
            "population": {
                "size": self.population.size,
                "immi": self.population.num_immigrated_individuals(),
                "mut": self.mutator.num_mutated_individuals(),
                "cros": self.crosser.num_crossed_individuals(),
                "eval": self.evaluator.num_evaluated_individuals(),
            },
        }

    def log_report(self):
        """Log the report"""
        self.log("info", f"New report : {self.get_report()}")
        self.log("info", f"Generation n°{self._n_gen} is completed")
        self.log("info", f"Time since start: {self.time_since_start:.2f}s")
        print(self._get_str_report())

    def _get_str_report(self):
        """Get the report as a string"""
        report = ""
        space = 7
        for key, value in self.get_report().items():
            if isinstance(value, dict):
                report += "\t"
                for key2, valu2 in value.items():
                    report += (
                        key2
                        + ": "
                        + str(valu2)[:space]
                        + " " * max(0, space - len(str(valu2)))
                        + "  "
                    )
                report += "\t"
            else:
                report += (
                    key + ": " + str(value)[:space] + " " * max(0, space - len(str(value))) + "  "
                )
        return report

    def update_elite(self):
        """Update the elite"""
        if self.is_active("elite"):
            self.log("info", "Elite update begins")
            self.elite.update(self.population)

    def select(self):
        """Select the population"""
        if self.is_active("selector"):
            self.log("info", "Selection process begins")
            self.selector.select(self.population)

    def migrate(self):
        """Migrate the population"""
        if self.is_active("migration"):
            self.log("info", "Migration process begins")
            self.population.migrate()

    def mutate(self):
        """Mutate the population"""
        if self.is_active("mutator"):
            self.log("info", "Mutation process begins")
            self.mutator.mutate(self.population)

    def cross(self):
        """Cross the population"""
        if self.is_active("crosser"):
            self.log("info", "Crossover process begins")
            self.crosser.cross(self.population)

    def evaluate(self):
        """Evaluate the population"""
        self.log("info", "Evaluation process begins")
        self.evaluator.evaluate(self.population)

    @property
    def time_since_start(self):
        """Get the time since the start of the evolution"""
        if self._evolution_started:
            t = time() - self._start_time + self._evo_time
        else:
            t = self._evo_time / 1000
        return t

    def get_info(self):
        """Get the environment information"""
        return {
            "components": {comp_name: getattr(self, comp_name) for comp_name in self._components},
            "init": {
                "random_seed": self.random_seed,
                "size_population": self.population.get_init_size(),
                "timeout": self._timeout,
                "eval_timeout": self.evaluator.get_eval_timeout(),
            },
            "actual": {
                "size_population": self.population.size,
                "time_since_start": self.time_since_start,
                "n_gen": self._n_gen,
            },
        }

    def get_generation(self):
        """Get the number of the generation"""
        return self._n_gen

    def components_duration(self):
        """Get the components duration"""
        durations = {
            comp_name: getattr(self, comp_name).get_duration() for comp_name in self._components if comp_name != "individual"
        }
        durations["extra_time"] = self._extra_time
        durations["generation"] = self.get_duration()
        return durations
