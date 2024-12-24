from numpy.typing import NDArray
from evopy.component import BaseComponent
from evopy.individual import BaseIndividual
from evopy.population import BasePopulation

from math import ceil


class BaseSelector(BaseComponent):


    _component_name: str = "Selector"
    _component_type: str = "Base"

    _single_select: bool = False
    _group_select: bool = False

    def __init__(self, options):
        BaseComponent.__init__(self, options)
        self._selection_ratio: float = options.selection_ratio

        self._allow_invalid: bool = options.allow_invalid
        self._allow_copies: bool = options.allow_copies
        self._limit_size: bool = options.limit_size
        self._keep_best: bool = options.keep_best

        self._max_single_select_fail: int = options.max_single_select_fail
        self._max_group_select_fail: int = options.max_group_select_fail

        self._pre_selected_set: set = set()
        self._compute_selection_set: bool = not self._allow_invalid or self._keep_best

        self.prev_best: BaseIndividual | None = None

    @BaseComponent.record_time
    def select(self, population: BasePopulation):
        selection = self._get_selection(population)
        population.update(selection)

    def _get_selection(self, population):
        if self._limit_size:
            n_selected = ceil(self._selection_ratio * population._init_size)
        else:
            n_selected = ceil(self._selection_ratio * population.size)
        self._init_selection(population)

        if self._single_select:
            selected = self.single_selection(population, n_selected)
        elif self._group_select:
            selected = self.group_selection(population, n_selected)
        else:
            raise ValueError(f"{self} has no selection mode defined")

        if self._keep_best:
            self.best_preservation(selected, population, n_selected)

        return selected

    def best_preservation(self, selected, population, n_selected) -> None:
        best = population.get_best_ind()
        if not self._is_best_included(best, selected, population):
            if len(selected) == n_selected and self._limit_size:
                selected = selected[:-1]
            selected.append(best)



    def group_selection(self, population, n_selected) -> list[BaseIndividual]:
        selected = []
        n_test = 0
        while n_test < self._max_group_select_fail and self._max_group_select_fail != -1:
            n_test += 1
            selected, success = self.group_select(population, n_selected)
            if success and self._valid_group_selection(selected, population):
                break
            else:
                self.log("debug", f"Groupe select has failed")
        else:
            self.log("warning", f"Group select failed {n_test} times. Max authorized is {self._max_group_select_fail}.")
        return selected

    def single_selection(self, population, n_selected) -> list[BaseIndividual]:
        selected = []
        for idx in range(n_selected):
            n_test = 0
            while n_test < self._max_single_select_fail and self._max_single_select_fail != -1:
                n_test += 1
                ind, success = self.single_select(idx, population)
                if success and self._valid_single_selection(ind, population):
                    if self._allow_copies:
                        selected.append(ind.copy())
                    else:
                        selected.append(ind)
                    break
                else:
                    self.log("debug", f"Single select has failed")
            else:
                self.log("warning", f"Single select failed {n_test} times. Max authorized is {self._max_single_select_fail}.")
        return selected

    def group_select(self, population, n_selected) -> tuple[list[BaseIndividual], bool]:
        raise NotImplementedError(f"{self} is declared as a group selector but do not defines a group_select function")

    def single_select(self, idx, population) -> tuple[BaseIndividual, bool]:
        raise NotImplementedError(f"{self} is declared as a single selector but do not defines a single_select function")

    def _is_best_included(self, best, pre_selected: NDArray, population):
        if self._compute_selection_set:
            return best._id in self._pre_selected_set
        else:
            return best in pre_selected

    def _valid_group_selection(self, pre_selected, population):
        if not self._allow_invalid and population.exist_invalid(sample=pre_selected):
            return False
        if not self._allow_copies:
            self._pre_selected_set = set(pre_selected)
            if len(self._pre_selected_set) != len(pre_selected):
                return False
        return True

    def _valid_single_selection(self, ind, population):
        if not self._allow_invalid and not ind._is_valid:
            return False
        if not self._allow_copies:
            if ind._id in self._pre_selected_set:
                return False
            else:
                self._pre_selected_set.add(ind._id)
        return True

    def _init_selection(self, population: BasePopulation):
        self._valid_init()
        if not self._allow_copies:
            self._pre_selected_set.clear()

    def _valid_init(self):
            assert self._single_select ^ self._group_select, ValueError(f"{self} need exactly one selection mode. Got single_select: {self._single_select}, group_select: {self._group_select}.")
            if self._single_select and self._max_single_select_fail == -1:
                self.log("warning", f"{self} has mode Single Select with unlimited fails. Risk of infinite loop. Consider setting a limited number of fails'")
            if self._group_select and self._max_group_select_fail == -1:
                self.log("warning", f"{self} has mode Group Select with unlimited fails. Risk of infinite loop. Consider setting a limited number of fails'")

    def _reset(self):
        pass