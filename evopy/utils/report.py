import numpy as np



def log_report(self):
    self._data_report = {"general": {"n_gen": self._n_gen,
                                "computation_time": self.time_since_start,},

                    "best elite": self.elite.best.fitness,
                    "best population": self.population.best.fitness,
                    "mean fitness": np.mean([ind.fitness for ind in self.population]),

                    "population": {"size": self.population.size,
                                "immigrants": self.population.num_immigrated_individuals(),
                                "mutated": self.mutator.num_mutated_individuals(),
                                "crossed": self.crosser.num_crossed_individuals(),
                                "evaluated": self.evaluator.num_evaluated_individuals(),}
    }
    self.log("info", f"New report : {self._data_report}")
    self.log("info", f"Generation n°{self._n_gen} is completed")
    self.log("info", f"Time since start: {self.time_since_start:.2f}s")

    print(self._get_str_report())

def _get_str_report(self):
    report = ""
    space = 10
    for value in self._data_report.values():
        if isinstance(value, dict):
            report += "\t"
            for valu2 in value.values():
                report += str(valu2)[:space]  + " " * max(0, space - len(str(value))) + "  "
            report += "\t"
        else:
            report += str(value)[:space] + " " * max(0, space - len(str(value))) + "  "
    return report
