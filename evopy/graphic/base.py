"""
Defines the BaseGraphic class.

This class is a base class for all graphic components.
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from evopy.component import BaseComponent


mpl.use("TkAgg")


class BaseGraphic(BaseComponent):
    """
    Base class for all graphic components.

    Parameters:
        * repr3d (bool): Whether to use 3D representation for the graphic
        * stop_graph (bool): Whether to stop the graph
        * end_graph (bool): Whether to plot the final graph at the end of the evolution
        * metrics_graph (bool): Whether to plot the metrics graph of the evolution
        * best_elite (bool): Whether to plot the best individual from the elite
        * best_pop (bool): Whether to plot the best individual from the population
        * elite_size (int): The size of the elite
            Secondary
        * time_gestion (bool): Whether to plot the time gestion of the evolution
        * max_gen_display (int): The maximum number of generations to display
            Min: 1
        * metrics_log_scale (bool): Whether to log the metrics


    """

    component_type: str = "Base"
    component_name = "Graphic"

    def __init__(self, options):
        self.env = options.env
        BaseComponent.__init__(self, options)
        self._repr3d_ind: bool = self._options.repr3d
        self._end_graph: bool = self._options.end_graph
        self._metrics_graph: bool = self._options.metrics_graph
        self._best_elite: bool = (
            self._options.best_elite & (self._options.elite_size > 0) & self._options.has_graph_repr
        )
        print(self._options.best_elite, self._options.elite_size > 0, self._options.has_graph_repr)
        self._best_pop: bool = self._options.best_pop & self._options.has_graph_repr
        self._time_gestion: bool = self._options.time_gestion
        self._num_graphs: int = (
            self._metrics_graph + self._best_elite + self._best_pop + self._time_gestion
        )
        self._dic_axs: dict[str, tuple[int] | tuple[int, int]] = {}
        self._max_gen_display: int = self._options.max_gen_display

        self._generations: list[int] = []

        if self._best_elite:
            self._prev_elite_id: int = -1

        if self._best_pop:
            self._prev_pop_id: int = -1

        if self._metrics_graph:
            self._log_scale: bool = self._options.metrics_log_scale
            self._elite_evo_data: list[float] = []
            self._pop_evo_data: list[float] = []
            self._mean_evo_data: list[float] = []
            self._selected_evo_data: list[float] = []
            self._metrics_ymax: float = 0

        if self._time_gestion:
            self._evaluation_time_data: list[float] = []
            self._mutation_time_data: list[float] = []
            self._cross_time_data: list[float] = []
            self._selection_time_data: list[float] = []
            self._generation_time_data: list[float] = []
            self._extra_time_data: list[float] = []
            self._time_ymax: float = 0


        if self._num_graphs > 0:
            self._init_graph()

    def _init_graph(self):
        """
        Initialize the graphic representation.
        """
        plt.ion()
        self.col = min(self._num_graphs, 4)
        self.lign = 1 + (self._num_graphs - 1) // 4
        self.fig, self.axs = plt.subplots(self.lign, self.col, figsize=(4*self.col, 4*self.lign))

        i = 0
        if self._metrics_graph:
            self._set_dic_asx("metrics", i)
            i += 1
            ax = self.get_ax("metrics")
            if self._log_scale:
                ax.set_yscale('log')
            ax.set_title("Metrics")
            (self._elite_evo,) = ax.plot([], label="Top Elite")
            (self._pop_evo,) = ax.plot([], label="Top Population")
            (self._mean_evo,) = ax.plot([], label="Mean Population")
            (self._selected_evo,) = ax.plot([], label="Mean Selected Population")

        if self._best_elite:
            self._set_dic_asx("elite", i)
            if self._repr3d_ind:
                self.replace_ax3d("elite")
            i += 1
            ax = self.get_ax("elite")
            self.env.evaluator.init_plot(ax)
            ax.set_title("Best elite")

        if self._best_pop:
            self._set_dic_asx("pop", i)
            if self._repr3d_ind:
                self.replace_ax3d("pop")
            i += 1
            ax = self.get_ax("pop")
            self.env.evaluator.init_plot(ax)
            ax.set_title("Best population")

        if self._time_gestion:
            self._set_dic_asx("time", i)
            i += 1
            ax = self.get_ax("time")
            ax.set_title("Time gestion")
            (self._extra_time,) = ax.plot([], label="Extra")
            (self._generation_time,) = ax.plot([], label="Generation")
            (self._evaluation_time,) = ax.plot([], label="Evaluation")
            (self._cross_time,) = ax.plot([], label="Cross-over")
            (self._mutation_time,) = ax.plot([], label="Mutation")
            (self._selection_time,) = ax.plot([], label="Selection")
            ax.legend()

        plt.ioff()

    def _set_dic_asx(self, ax_name: str, i: int):
        """
        Set the position in the grid of axes, of a new ax in the dictionary.
        """
        if self.lign == 1:
            self._dic_axs[ax_name] = (i,)
        else:
            self._dic_axs[ax_name] = (i // self.col, i % self.col)

    def get_ax(self, ax_name: str) -> mpl.axes.Axes:
        """
        Get the ax corresponding to the name.
        """
        if self._num_graphs == 1:
            return self.axs
        return self.axs[self._dic_axs[ax_name]]

    def replace_ax3d(self, ax_name: str):
        """
        Replace the ax by a 3D ax.
        """
        idx = self._dic_axs[ax_name]
        if len(idx) == 1:
            idx = (idx[0], 0)
        l, c, n = idx[0] + 1, idx[1] + 1, idx[1] * 4 + idx[0] + 1
        self.axs[self._dic_axs[type]] = self.fig.add_subplot(l, c, n, projection="3d")

    def update(self):
        """
        Update the graphic representation.
        """

        self._generations.append(self.env.get_generation())

        if self._metrics_graph:
            self.store_metrics()
            self.update_graph_metrics()
        if self._best_elite:
            self.update_graph_elite()
        if self._best_pop:
            self.update_graph_pop()
        if self._time_gestion:
            self.store_durations()
            self.update_time_gestion()

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def init_evolution(self):
        """
        Initialize the graphic representation.
        """
        plt.ion()

    def end_evolution(self):
        """
        End the graphic representation.
        """
        plt.ioff()
        if self._end_graph:
            plt.show()

    def store_metrics(self):
        """
        Store the metrics of the current generation.
        """
        self._elite_evo_data.append(self.env.elite.best.fitness)
        self._pop_evo_data.append(self.env.population.best.fitness)
        self._mean_evo_data.append(float(np.mean([ind.fitness for ind in self.env.population])))
        self._selected_evo_data.append(float(self.env.population.get_selected_mean()))
        self._metrics_ymax = max(
            self._metrics_ymax, self._mean_evo_data[-1], self._selected_evo_data[-1]
        )

    def store_durations(self):
        """
        Store the durations of the current generation.
        """
        durations = self.env.components_duration()
        gap = 0
        self._selection_time_data.append(durations["selector"] + gap)
        gap += durations["selector"]
        self._mutation_time_data.append(durations["mutator"] + gap)
        gap += durations["mutator"]
        self._cross_time_data.append(durations["crosser"] + gap)
        gap += durations["crosser"]
        self._evaluation_time_data.append(durations["evaluator"] + gap)
        self._generation_time_data.append(durations["generation"])
        self._extra_time_data.append(durations["extra_time"] + durations["generation"])
        self._time_ymax = max(self._time_ymax, self._extra_time_data[-1])

    def update_graph_metrics(self):
        """
        Update the metrics graph.
        """
        ax = self.get_ax("metrics")
        for metric in ["elite", "pop", "mean", "selected"]:
            x_data = self._generations[-self._max_gen_display :]
            y_data = getattr(self, f"_{metric}_evo_data")[-self._max_gen_display :]
            getattr(self, f"_{metric}_evo").set_xdata(x_data)
            getattr(self, f"_{metric}_evo").set_ydata(y_data)
        ax.relim()
        # ax.set_ylim(0, self._metrics_ymax)
        ax.autoscale_view()

    def update_graph_elite(self):
        """
        Update the elite graph.
        """
        if self._prev_elite_id == -1 or self._prev_elite_id != self.env.elite.best.get_id():
            self._prev_elite_id = self.env.elite.best.get_id()
            ax = self.get_ax("elite")
            best = self.env.elite.best
            self.env.evaluator.plot(ax, best)

    def update_graph_pop(self):
        """
        Update the population graph.
        """
        if self._prev_pop_id == -1 or self._prev_pop_id != self.env.population.best.get_id():
            self._prev_pop_id = self.env.population.best.get_id()
            ax = self.get_ax("pop")
            best = self.env.population.best
            self.env.evaluator.plot(ax, best)

    def update_time_gestion(self):
        """
        Update the time gestion graph.
        """
        ax = self.get_ax("time")
        for metric in ["extra", "generation", "cross", "mutation", "selection", "evaluation"]:
            x_data = self._generations[-self._max_gen_display :]
            y_data = getattr(self, f"_{metric}_time_data")[-self._max_gen_display :]
            getattr(self, f"_{metric}_time").set_xdata(x_data)
            getattr(self, f"_{metric}_time").set_ydata(y_data)
        ax.relim()
        ax.set_ylim(0, self._time_ymax)
        ax.autoscale_view()
