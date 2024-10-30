from base.Environment.AbstractEnvironment import AbstractEnvironment
from base.Component.BaseComponent import BaseComponent
from base.Individual.BaseIndividual import BaseIndividual
from base.Evaluator.BaseEvaluator import BaseEvaluator
from base.Selector.BaseSelector import BaseSelector
from base.Mutator.BaseMutator import BaseMutator
from base.Crosser.BaseCrosser import BaseCrosser
from base.Individual.BaseIndividual import BaseIndividual
from base.Population.BasePopulation import BasePopulation
from base.Elite.BaseElite import BaseElite

import matplotlib.pyplot as plt
from time import time
import numpy as np
import random
import sys
import os
from functools import wraps


class BaseEnvironment(BaseComponent, AbstractEnvironment):

    _components: list = ["crosser", "mutator", "evaluator", "selector", "population", "elite"]

    def __init__(self, options, **kwargs):

        self._active_selection: bool = True
        self._active_migration: bool = True
        self._active_mutation: bool = True
        self._active_cross: bool = True
        self._active_elite: bool = True
        self._active_graphic: bool = True
        self._active_interface: bool = False

        self.random_seed: int = options.random_seed
        random.seed(self.random_seed)
        np.random.seed(self.random_seed)

        options.update(kwargs)
        super().__init__(options)

        self.individual: type[BaseIndividual] = options.individual
        self.crosser: BaseCrosser = options.crosser
        self.mutator: BaseMutator = options.mutator
        self.evaluator: BaseEvaluator = options.evaluator
        self.selector: BaseSelector = options.selector
        self.population: BasePopulation = options.population
        self.elite: BaseElite = options.elite

        self._init_components(options)

        if self._active_graphic:
            self.graphic = options.graphic(self, options)
        if self._active_interface:
            self.interface = options.interface(self, options)

        self._timeout: int = options.timeout
        self._max_gen: int = options.max_gen

        self._create_elite: bool = options.create_elite
        self._create_report: bool = False

        self._evolution_started: bool = False
        self._evolution_over: bool = False
        self._evo_time: float = 0.
        self._extra_time: float = 0.

        self._n_gen: int = 0


    def __attrs_post_init__(self):
        self._verif_valid_init()

    def _init_components(self, options):
        for component in self._components:
            if self._verif_init_comp(component):
                comp = self.__getattribute__(component)
                setattr(self, component, comp(options))

    def _verif_init_comp(self, component_name) -> bool:
        used_comp = True if not hasattr(self, f"_create_{component_name}") else self.__getattribute__(f"_create_{component_name}")
        need_init = component_name != "individual"
        not_init = isinstance(self.__getattribute__(component_name), type)
        return need_init and not_init and used_comp

    def _verif_valid_init(self):
        assert True

    def evolve(self):
        self.init_evolution()
        self.evaluate()
        start_extra = time()
        for _ in range(self._max_gen):
            if self.time_since_start > self._timeout > 0:
                break
            end_extra = time()
            self.set_extra_time(end_extra - start_extra)
            self.new_generation()
            start_extra = time()
            self.update_graphic()
            self.log_report()
        self.end_evolution()

    def set_extra_time(self, extra_time):
        self._extra_time = extra_time


    def init_evolution(self):
        self._evolution_started = True
        self._evolution_over = False
        self._start_time = time()

        if self._active_graphic:
            self.graphic.init_evolution()

    def end_evolution(self):
        self._evolution_started = False
        self._evolution_over = True
        self._stop_time = time()
        self._evo_time += self._stop_time - self._start_time

        self.log("info", f"Evolution is finished")
        self.log("info", f"Total time: {self._evo_time:.2f}s")

        if self._active_graphic:
            self.graphic.end_evolution()

    @BaseComponent.record_time
    def new_generation(self):
        self._n_gen += 1
        self.select()
        self.migrate()
        self.mutate()
        self.cross()
        self.evaluate()
        self.update_elite()

    def log_report(self):
        self._data_report = {"general": {"n_gen": self._n_gen,
                                 "time": int(self.time_since_start*10)/10,},

                     "top": self.elite.best.fitness,
                     "pop": int(self.population.best.fitness*100)/100,
                     "mean": int(np.mean([ind.fitness for ind in self.population])*100)/100,

                     "population": {"size": self.population.size,
                                    "immi": self.population.num_immigrated_individuals(),
                                    "mut": self.mutator.num_mutated_individuals(),
                                    "cros": self.crosser.num_crossed_individuals(),
                                    "eval": self.evaluator.num_evaluated_individuals(),}
        }
        self.log("info", f"New report : {self._data_report}")
        self.log("info", f"Generation n°{self._n_gen} is completed")
        self.log("info", f"Time since start: {self.time_since_start:.2f}s")

        print(self._get_str_report())


    def _get_str_report(self):
        report = ""
        space = 7
        for key, value in self._data_report.items():
            if isinstance(value, dict):
                report += "\t"
                for key2, valu2 in value.items():
                    report += key2 + ": " + str(valu2)[:space]  + " " * max(0, space - len(str(valu2))) + "  "
                report += "\t"
            else:
                report += key + ": " + str(value)[:space] + " " * max(0, space - len(str(value))) + "  "
        return report

    def update_graphic(self):
        if self._active_graphic:
            self.log("info", f"Graphic is updating")
            self.graphic.update()

    def update_elite(self):
        if self._active_elite:
            self.log("info", "Elite update begins")
            self.elite.update(self.population)

    def select(self):
        if self._active_selection:
            self.log("info", f"Selection process begins")
            self.selector.select(self.population)

    def migrate(self):
        if self._active_migration:
            self.log("info", f"Migration process begins")
            self.population.migrate()

    def mutate(self):
        if self._active_mutation:
            self.log("info", f"Mutation process begins")
            self.mutator.mutate(self.population)

    def cross(self):
        if self._active_cross:
            self.log("info", f"Crossover process begins")
            self.crosser.cross(self.population)

    def evaluate(self):
        self.log("info", f"Evaluation process begins")
        self.evaluator.evaluate(self.population)

    @property
    def time_since_start(self):
        if self._evolution_started:
            t = time() - self._start_time + self._evo_time
        else:
            t = self._evo_time / 1000
        return t

    def get_info(self):
        return {
            "components" : {comp_name: getattr(self, comp_name) for comp_name in self._components},

            "init": {
                "random_seed": self.random_seed,
                "size_population": self.population._init_size,
                "timeout": self._timeout,
                "eval_timeout": self.evaluator._timeout,
            },

            "actual": {
                "size_population": self.population.size,
                "time_since_start": self.time_since_start,
                "n_gen": self._n_gen,

            }
        }
