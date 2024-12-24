from evopy.component import BaseComponent
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class BaseInterface(BaseComponent):

    _component_name: str = "Interface"
    _component_type: str = "Base"

    def __init__(self, env, options, **kwargs):
        options.update(kwargs)
        BaseComponent.__init__(self, options)
        self._env = env
        self._root: tk.Tk = tk.Tk()
        self._root.title("Genetic Algorithm")
        self._root.geometry("800x600")

        self._main_frame = ttk.Frame(self._root)
        self._main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Frame pour les graphiques sur la gauche
        self.graph_frame = ttk.LabelFrame(self._main_frame, text="Graphics")
        self.graph_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Frame pour les stats et boutons sur la droite
        self.stats_frame = ttk.LabelFrame(self._main_frame, text="Statistiques et Contrôles")
        self.stats_frame.grid(row=0, column=1, sticky="ns")

        # Rendre le cadre de gauche extensible
        self._main_frame.columnconfigure(0, weight=3)
        self._main_frame.columnconfigure(1, weight=1)

        # Options de sélection de graphique
        self.options_frame = ttk.LabelFrame(self.graph_frame, text="Choix des graphiques")
        self.options_frame.pack(padx=10, pady=10, fill="x")

        # Liste des graphiques à sélectionner
        self.graph_options = ["Graphique 1", "Graphique 2", "Graphique 3"]
        self.selected_graphs = tk.StringVar(value=[])

        # Liste déroulante multisélection
        self.graph_listbox = tk.Listbox(
            self.options_frame,
            listvariable=self.selected_graphs,
            selectmode="multiple",
            height=len(self.graph_options)
        )
        for option in self.graph_options:
            self.graph_listbox.insert(tk.END, option)
        self.graph_listbox.pack(padx=5, pady=5)

        # Bouton pour afficher les graphiques
        self.show_button = ttk.Button(self.options_frame, text="Afficher", command=self.show_graphs)
        self.show_button.pack(pady=5)

        # Ajouter des statistiques et boutons dans stats_frame
        self.stats_label = ttk.Label(self.stats_frame, text="Statistiques", font=("Arial", 12, "bold"))
        self.stats_label.pack(pady=(10, 5))

        # Exemples de statistiques
        self.stat1_label = ttk.Label(self.stats_frame, text="Statistique 1 : Valeur")
        self.stat1_label.pack(anchor="w", padx=5)

        self.stat2_label = ttk.Label(self.stats_frame, text="Statistique 2 : Valeur")
        self.stat2_label.pack(anchor="w", padx=5)

        # Boutons supplémentaires
        self.update_button = ttk.Button(self.stats_frame, text="Mettre à jour les stats", command=self.update_stats)
        self.update_button.pack(pady=(10, 5))

        self.clear_button = ttk.Button(self.graph_frame, text="Effacer les graphiques", command=self.clear_graphs)
        self.clear_button.pack(pady=(5, 10))

    def show_graphs(self):
        # Efface les graphiques précédents
        for widget in self.graph_frame.winfo_children():
            if isinstance(widget, FigureCanvasTkAgg):
                widget.get_tk_widget().destroy()

        # Obtenir les graphiques sélectionnés
        selected_indices = self.graph_listbox.curselection()
        selected_graphs = [self.graph_options[i] for i in selected_indices]

        # Affichage des graphiques sélectionnés
        for graph_name in selected_graphs:
            fig = self.create_figure(graph_name)
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side="left", fill="both", expand=True)

    def create_figure(self, graph_name):
        # Création d'un graphique (à personnaliser selon vos besoins)
        fig = Figure(figsize=(4, 3))
        ax = fig.add_subplot(111)
        if graph_name == "Graphique 1":
            ax.plot([0, 1, 2], [0, 1, 0], label="Graphique 1")
        elif graph_name == "Graphique 2":
            ax.plot([0, 1, 2], [0, 2, 1], label="Graphique 2")
        elif graph_name == "Graphique 3":
            ax.plot([0, 1, 2], [0, 3, 2], label="Graphique 3")
        ax.legend()
        return fig

    def update_stats(self):
        # Méthode pour mettre à jour les statistiques (à personnaliser)
        self.stat1_label.config(text="Statistique 1 : Mise à jour")
        self.stat2_label.config(text="Statistique 2 : Mise à jour")

    def clear_graphs(self):
        # Méthode pour effacer tous les graphiques
        for widget in self.graph_frame.winfo_children():
            if isinstance(widget, FigureCanvasTkAgg):
                widget.get_tk_widget().destroy()
