from typing_extensions import Tuple
from base.Component.BaseComponent import BaseComponent
from base.Graphic.AbstractGraphic import AbstractGraphic
import numpy as np
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt

class BaseGraphic(BaseComponent, AbstractGraphic):

    _component_type: str = "Base"
    _component_name: str = "Graphic"

    def __init__(self, env, options, **kwargs):
        self.env = env
        options.update(kwargs)
        BaseComponent.__init__(self, options)
        self._repr3D_ind: bool = options.repr3D
        self._stop_graph: bool = options.stop_graph
        self._end_graph: bool = options.end_graph
        self._metrics_graph: bool = options.metrics_graph
        self._best_elite: bool = options.best_elite & (options.elite_size > 0) & options.has_graph_repr
        self._best_pop: bool = options.best_pop & options.has_graph_repr
        self._time_gestion: bool = options.time_gestion
        self._num_graphs: int = self._metrics_graph + self._best_elite + self._best_pop + self._time_gestion
        self._dic_axs: dict[str, tuple[int] | tuple[int, int]] = {}
        self._max_gen_display: int = options.max_gen_display
        if self._num_graphs > 0 and not self._stop_graph:
            self._init_graph()

        self._generations: list[int] = []

        if self._metrics_graph:
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

    def _init_graph(self):
        plt.ion()
        self.col = min(self._num_graphs, 4)
        self.lign =  1 + (self._num_graphs - 1) // 4
        self.fig, self.axs = plt.subplots(self.lign, self.col, figsize=(4 * self.col, 4 * self.lign))

        i = 0
        if self._metrics_graph:
            self._set_dic_asx('metrics', i)
            i += 1
            ax = self.get_ax('metrics')

            #ax.set_yscale('log')
            ax.set_title('Metrics')
            self._elite_evo, = ax.plot([], label='Top Elite')
            self._pop_evo, = ax.plot([], label="Top Population")
            self._mean_evo, = ax.plot([], label="Mean Population")
            self._selected_evo, = ax.plot([], label="Mean Selected Population")

        if self._best_elite:
            self._set_dic_asx('elite', i)
            if self._repr3D_ind:
                self.replace_ax3D('elite')
            i += 1
            ax = self.get_ax('elite')
            self.env.evaluator.init_plot(ax)
            ax.set_title('Best elite')
            self._prev_elite_id = - 1

        if self._best_pop:
            self._set_dic_asx('pop', i)
            if self._repr3D_ind:
                self.replace_ax3D('pop')
            i += 1
            ax = self.get_ax('pop')
            self.env.evaluator.init_plot(ax)
            ax.set_title('Best population')
            self._prev_pop_id = -1

        if self._time_gestion:
            self._set_dic_asx('time', i)
            i += 1
            ax = self.get_ax('time')
            ax.set_title('Time gestion')
            self._extra_time, = ax.plot([], label='Extra')
            self._generation_time, = ax.plot([], label='Generation')
            self._evaluation_time, = ax.plot([], label='Evaluation')
            self._cross_time, = ax.plot([], label='Cross-over')
            self._mutation_time, = ax.plot([], label='Mutation')
            self._selection_time, = ax.plot([], label='Selection')
            ax.legend()

        plt.ioff()

    def _set_dic_asx(self, type: str, i: int):
        if self.lign == 1:
            self._dic_axs[type] = (i, )
        else:
            self._dic_axs[type] = (i // self.col, i % self.col)

    def get_ax(self, type):
        if self._num_graphs == 1:
            return self.axs
        return self.axs[*self._dic_axs[type]]

    def replace_ax3D(self, type):
        idx = self._dic_axs[type]
        if len(idx) == 1:
            idx = (idx[0], 0)
        l, c, n = idx[0]+1, idx[1]+1, idx[1]*4+idx[0]+1
        self.axs[*self._dic_axs[type]] = self.fig.add_subplot(l, c, n, projection='3d')

    def update(self):
        if self._stop_graph:
            return

        self._generations.append(self.env._n_gen)

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
        plt.ion()

    def end_evolution(self):
        plt.ioff()
        if self._end_graph:
            plt.show()

    def store_metrics(self):
        self._elite_evo_data.append(self.env.elite.best.fitness)
        self._pop_evo_data.append(self.env.population.best.fitness)
        self._mean_evo_data.append(float(np.mean([ind.fitness for ind in self.env.population])))
        self._selected_evo_data.append(float(self.env.population._selected_mean))
        self._metrics_ymax = max(self._metrics_ymax, self._mean_evo_data[-1], self._selected_evo_data[-1])

    def store_durations(self):
        self._selection_time_data.append(self.env.selector._duration)
        self._mutation_time_data.append(self.env.mutator._duration + self._selection_time_data[-1])
        self._cross_time_data.append(self.env.crosser._duration + self._mutation_time_data[-1])
        self._evaluation_time_data.append(self.env.evaluator._duration + self._cross_time_data[-1])
        self._generation_time_data.append(self.env._duration)
        self._extra_time_data.append(self._generation_time_data[-1] + self.env._extra_time)
        self._time_ymax = max(self._time_ymax, self._extra_time_data[-1])

    def update_graph_metrics(self):
        ax = self.get_ax('metrics')
        for metric in ["elite", "pop", "mean", "selected"]:
            getattr(self, f"_{metric}_evo").set_xdata(self._generations[-self._max_gen_display:])
            getattr(self, f"_{metric}_evo").set_ydata(getattr(self, f"_{metric}_evo_data")[-self._max_gen_display:])
        ax.relim()
        #ax.set_ylim(0, self._metrics_ymax)
        ax.autoscale_view()

    def update_graph_elite(self):
        if self._prev_elite_id == -1 or self._prev_elite_id != self.env.elite.best._id:
            self._prev_elite_id = self.env.elite.best._id
            ax = self.get_ax('elite')
            best = self.env.elite.best
            self.env.evaluator.plot(ax, best)

    def update_graph_pop(self):
        if self._prev_pop_id == -1 or self._prev_pop_id != self.env.population.best._id:
            self._prev_pop_id = self.env.population.best._id
            ax = self.get_ax('pop')
            best = self.env.population.best
            self.env.evaluator.plot(ax, best)

    def update_time_gestion(self):
        ax = self.get_ax('time')
        for metric in ["extra", "generation", "cross", "mutation", "selection", "evaluation"]:
            getattr(self, f"_{metric}_time").set_xdata(self._generations[-self._max_gen_display:])
            getattr(self, f"_{metric}_time").set_ydata(getattr(self, f"_{metric}_time_data")[-self._max_gen_display:])
        ax.relim()
        ax.set_ylim(0, self._time_ymax)
        ax.autoscale_view()
