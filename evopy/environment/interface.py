"""
Interactive CustomTkinter-based evolution interface with multi-page navigation.
"""

import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import statistics
from typing import Dict, List, Any, Optional

from evopy.environment.base import BaseEnvironment
from evopy.reporter.base import BaseReporter


class InterfaceReporter(BaseReporter):
    """Collects evolution statistics for visualization."""
    
    component_type = "Interface"
    
    def __init__(self, options):
        super().__init__(options)
        self.data = {
            'generations': [],
            'best_fitness': [],
            'mean_fitness': [],
            'worst_fitness': [],
            'pop_size': [],
            'mutations_count': [],
            'crossovers_count': [],
            'eval_time': []
        }
        self.environment = None  # Will be set by the environment
        
    def post_evaluation_report(self, population, generation):
        """Called after evaluation to collect statistics."""
        if not population or population.size == 0 or not self.environment:
            return
            
        # Calculate mean fitness
        fitnesses = [ind.fitness for ind in population if ind.is_valid]
        mean_fit = statistics.mean(fitnesses) if fitnesses else 0.0
        
        self.data['generations'].append(self.environment._n_gen)
        self.data['best_fitness'].append(population.get_best_ind().fitness)
        self.data['mean_fitness'].append(mean_fit)
        self.data['worst_fitness'].append(population.get_worst_ind().fitness)
        self.data['pop_size'].append(population.size)
        
        # Count mutations and crossovers
        mutations = sum(1 for ind in population if hasattr(ind, 'has_mutate') and ind.has_mutate())
        crossovers = sum(1 for ind in population if hasattr(ind, 'has_cross') and ind.has_cross())
        
        self.data['mutations_count'].append(mutations)
        self.data['crossovers_count'].append(crossovers)
        
    def post_mutation_report(self, individuals, generation):
        while len(self.data['mutations_count']) <= generation:
            self.data['mutations_count'].append(0)
        if len(self.data['mutations_count']) > generation:
            self.data['mutations_count'][generation] += len(individuals)
            
    def post_crossover_report(self, offspring, generation):
        while len(self.data['crossovers_count']) <= generation:
            self.data['crossovers_count'].append(0)
        if len(self.data['crossovers_count']) > generation:
            self.data['crossovers_count'][generation] += len(offspring)


class InterfaceEnvironment(BaseEnvironment):
    """
    Interactive evolution interface with multi-page navigation.
    
    Parameters:
        * ui_theme (str): Theme - "dark", "light", or "system"
        * ui_color (str): Color scheme - "blue", "green", "dark-blue"
        * update_interval (int): GUI update interval in ms (50-2000)
        * auto_start (bool): Auto-start evolution on launch
    """
    
    component_type: str = "Interface"
    
    _components = BaseEnvironment._components + ["reporter"]
    _activations = BaseEnvironment._activations | {"reporter": True}
    
    def __init__(self, options):
        # UI settings
        self.ui_theme = getattr(options, 'ui_theme', 'dark')
        self.ui_color = getattr(options, 'ui_color', 'blue')
        self.update_interval = getattr(options, 'update_interval', 100)
        self.auto_start = getattr(options, 'auto_start', False)
        
        # Initialize CTk
        ctk.set_appearance_mode(self.ui_theme)
        ctk.set_default_color_theme(self.ui_color)
        
        # Control state
        self.root = None
        self.is_running = False
        self.is_paused = False
        self.should_stop = False
        self.step_mode = False
        self.evolution_thread = None
        self.start_time = None
        
        # UI components
        self.current_page = "dashboard"
        self.graphs = {}
        self.param_widgets = {}
        self.stat_labels = {}
        
        # Reporter integration
        self.stats_reporter = InterfaceReporter(options)
        
        super().__init__(options)
        
        # Set reporter's environment reference
        self.stats_reporter.environment = self
        
        # Add reporter
        if hasattr(self, 'reporter'):
            if hasattr(self.reporter, 'add_reporter'):
                self.reporter.add_reporter(self.stats_reporter)
            else:
                from evopy.reporter.reporter_set import ReporterSet
                self.reporter = ReporterSet(options, [self.reporter, self.stats_reporter])
        else:
            self.reporter = self.stats_reporter
            
    def init_evolution(self):
        super().init_evolution()
        self.create_ui()
        
    def create_ui(self):
        """Create the main interface."""
        self.root = ctk.CTk()
        self.root.title("EvoPy - Interactive Evolution")
        self.root.geometry("1800x1000")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Main layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Sidebar
        self.create_sidebar()
        
        # Main content area
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Create pages
        self.pages = {}
        self.create_dashboard_page()
        self.create_control_page()
        self.create_graphs_page()
        self.create_parameters_page()
        
        # Show dashboard
        self.show_page("dashboard")
        
        # Start update loop
        self.root.after(self.update_interval, self.update_ui)
        
    def create_sidebar(self):
        """Create navigation sidebar."""
        sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        # Title
        title = ctk.CTkLabel(sidebar, text="EvoPy", font=("Arial", 28, "bold"))
        title.pack(pady=30)
        
        # Navigation buttons
        nav_buttons = [
            ("📊 Dashboard", "dashboard"),
            ("🎮 Control", "control"),
            ("📈 Graphs", "graphs"),
            ("⚙️ Parameters", "parameters")
        ]
        
        for text, page in nav_buttons:
            btn = ctk.CTkButton(
                sidebar, text=text, width=180, height=50,
                font=("Arial", 16),
                command=lambda p=page: self.show_page(p)
            )
            btn.pack(pady=10, padx=10)
            
        # Status indicator
        ctk.CTkLabel(sidebar, text="Status", font=("Arial", 14, "bold")).pack(pady=(50, 10))
        self.status_label = ctk.CTkLabel(sidebar, text="● Stopped", text_color="gray", font=("Arial", 14))
        self.status_label.pack()
        
    def create_dashboard_page(self):
        """Create overview dashboard."""
        page = ctk.CTkFrame(self.main_frame)
        self.pages["dashboard"] = page
        
        # Title
        ctk.CTkLabel(page, text="Evolution Dashboard", font=("Arial", 32, "bold")).pack(pady=20)
        
        # Stats grid
        stats_frame = ctk.CTkFrame(page)
        stats_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        stats_frame.grid_rowconfigure(0, weight=1)
        stats_frame.grid_rowconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        
        # Create stat cards
        self.create_stat_card(stats_frame, "Generation", "dash_gen", "0", 0, 0)
        self.create_stat_card(stats_frame, "Best Fitness", "dash_best", "N/A", 0, 1)
        self.create_stat_card(stats_frame, "Population", "dash_pop", "0", 0, 2)
        self.create_stat_card(stats_frame, "Time Elapsed", "dash_time", "0.0s", 1, 0)
        self.create_stat_card(stats_frame, "Mean Fitness", "dash_mean", "N/A", 1, 1)
        self.create_stat_card(stats_frame, "Eval/sec", "dash_evals", "0", 1, 2)
        
        # Quick fitness graph
        graph_frame = ctk.CTkFrame(page)
        graph_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        fig = Figure(figsize=(12, 4), dpi=80)
        ax = fig.add_subplot(111)
        self.setup_ax_colors(ax)
        
        canvas = FigureCanvasTkAgg(fig, graph_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.graphs['dash_fitness'] = {'fig': fig, 'ax': ax, 'canvas': canvas}
        
    def create_control_page(self):
        """Create evolution control page."""
        page = ctk.CTkFrame(self.main_frame)
        self.pages["control"] = page
        
        ctk.CTkLabel(page, text="Evolution Control", font=("Arial", 32, "bold")).pack(pady=20)
        
        # Control buttons
        btn_frame = ctk.CTkFrame(page)
        btn_frame.pack(pady=30)
        
        self.play_btn = ctk.CTkButton(
            btn_frame, text="▶ Start", width=150, height=60,
            font=("Arial", 20, "bold"),
            command=self.toggle_evolution
        )
        self.play_btn.pack(side="left", padx=10)
        
        self.step_btn = ctk.CTkButton(
            btn_frame, text="⏭ Step", width=150, height=60,
            font=("Arial", 20, "bold"),
            command=self.step_evolution
        )
        self.step_btn.pack(side="left", padx=10)
        
        self.reset_btn = ctk.CTkButton(
            btn_frame, text="↻ Reset", width=150, height=60,
            font=("Arial", 20, "bold"),
            command=self.reset_evolution
        )
        self.reset_btn.pack(side="left", padx=10)
        
        # Speed control
        speed_frame = ctk.CTkFrame(page)
        speed_frame.pack(pady=30, fill="x", padx=50)
        
        ctk.CTkLabel(speed_frame, text="Update Speed (ms)", font=("Arial", 18)).pack(pady=10)
        
        speed_inner = ctk.CTkFrame(speed_frame, fg_color="transparent")
        speed_inner.pack(fill="x", padx=50)
        
        self.speed_slider = ctk.CTkSlider(
            speed_inner, from_=50, to=2000, number_of_steps=39,
            command=self.update_speed
        )
        self.speed_slider.set(self.update_interval)
        self.speed_slider.pack(side="left", fill="x", expand=True, padx=10)
        
        self.speed_label = ctk.CTkLabel(speed_inner, text=f"{self.update_interval}ms", font=("Arial", 16), width=80)
        self.speed_label.pack(side="left", padx=10)
        
        # Info display
        info_frame = ctk.CTkFrame(page)
        info_frame.pack(fill="both", expand=True, padx=50, pady=20)
        
        ctk.CTkLabel(info_frame, text="Evolution Information", font=("Arial", 22, "bold")).pack(pady=20)
        
        info_text = ctk.CTkTextbox(info_frame, font=("Courier", 14), wrap="word")
        info_text.pack(fill="both", expand=True, padx=20, pady=20)
        
        info = f"""Max Generations: {self._max_gen}
Population Size: {getattr(self._options, 'n_individuals', 'N/A')}
Individual Type: {self.individual.component_type if hasattr(self, 'individual') else 'N/A'}
Evaluator: {self.evaluator.component_type if hasattr(self, 'evaluator') else 'N/A'}
Selector: {self.selector.component_type if hasattr(self, 'selector') else 'N/A'}
Mutator: {self.mutator.component_type if hasattr(self, 'mutator') else 'N/A'}
Crosser: {self.crosser.component_type if hasattr(self, 'crosser') else 'N/A'}"""
        
        info_text.insert("1.0", info)
        info_text.configure(state="disabled")
        
    def create_graphs_page(self):
        """Create graphs visualization page."""
        page = ctk.CTkFrame(self.main_frame)
        self.pages["graphs"] = page
        
        ctk.CTkLabel(page, text="Evolution Graphs", font=("Arial", 32, "bold")).pack(pady=20)
        
        # Graph selection
        select_frame = ctk.CTkFrame(page)
        select_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(select_frame, text="Select Graphs:", font=("Arial", 18, "bold")).pack(side="left", padx=20)
        
        self.graph_vars = {}
        graph_options = [
            ('fitness', 'Fitness Evolution', True),
            ('operations', 'Operations', True),
            ('eval_time', 'Evaluation Time', False)
        ]
        
        for key, label, default in graph_options:
            var = ctk.BooleanVar(value=default)
            self.graph_vars[key] = var
            ctk.CTkCheckBox(
                select_frame, text=label, variable=var,
                font=("Arial", 14),
                command=self.update_graph_layout
            ).pack(side="left", padx=10)
            
        # Graph container
        self.graph_container = ctk.CTkFrame(page)
        self.graph_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.update_graph_layout()
        
    def create_parameters_page(self):
        """Create parameters adjustment page."""
        page = ctk.CTkScrollableFrame(self.main_frame)
        self.pages["parameters"] = page
        
        ctk.CTkLabel(page, text="Runtime Parameters", font=("Arial", 32, "bold")).pack(pady=20)
        
        # Get available parameters from components
        params = []
        
        # Common mutation parameters
        if hasattr(self, 'mutator'):
            if hasattr(self.mutator, 'mutation_rate'):
                params.append(('mutation_rate', 'Mutation Rate', 0.0, 1.0, 0.01, self.mutator))
            if hasattr(self.mutator, 'weight_mutation_prob'):
                params.append(('weight_mutation_prob', 'Weight Mutation Prob', 0.0, 1.0, 0.01, self.mutator))
                
        # Crossover parameters
        if hasattr(self, 'crosser'):
            if hasattr(self.crosser, 'crossover_rate'):
                params.append(('crossover_rate', 'Crossover Rate', 0.0, 1.0, 0.01, self.crosser))
                
        # Selection parameters  
        if hasattr(self, 'selector'):
            if hasattr(self.selector, 'selection_ratio'):
                params.append(('selection_ratio', 'Selection Ratio', 0.1, 0.9, 0.05, self.selector))
            if hasattr(self.selector, 'tournament_size'):
                params.append(('tournament_size', 'Tournament Size', 2, 20, 1, self.selector))
                
        # Create parameter controls
        if params:
            for param_name, label, min_val, max_val, step, component in params:
                self.create_param_control(page, param_name, label, min_val, max_val, component)
        else:
            ctk.CTkLabel(
                page, text="No adjustable parameters found",
                font=("Arial", 18)
            ).pack(pady=50)
            
    def create_stat_card(self, parent, title, key, value, row, col):
        """Create a stat display card."""
        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(card, text=title, font=("Arial", 16)).pack(pady=10)
        
        value_label = ctk.CTkLabel(card, text=value, font=("Arial", 36, "bold"))
        value_label.pack(pady=20)
        
        self.stat_labels[key] = value_label
        
    def create_param_control(self, parent, param_name, label, min_val, max_val, component):
        """Create parameter control slider."""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=20, pady=15)
        
        current = getattr(component, param_name, (min_val + max_val) / 2)
        
        label_frame = ctk.CTkFrame(frame, fg_color="transparent")
        label_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(label_frame, text=label, font=("Arial", 18, "bold")).pack(side="left")
        
        value_label = ctk.CTkLabel(label_frame, text=f"{current:.3f}", font=("Arial", 18))
        value_label.pack(side="right")
        
        slider = ctk.CTkSlider(
            frame, from_=min_val, to=max_val,
            command=lambda v: self.update_param(param_name, v, component, value_label)
        )
        slider.set(current)
        slider.pack(fill="x", padx=20, pady=10)
        
        self.param_widgets[param_name] = {'slider': slider, 'label': value_label, 'component': component}
        
    def setup_ax_colors(self, ax):
        """Setup matplotlib axis colors based on theme."""
        color = 'white' if self.ui_theme == 'dark' else 'black'
        bg = '#2b2b2b' if self.ui_theme == 'dark' else '#f0f0f0'
        
        ax.set_facecolor(bg)
        ax.tick_params(colors=color)
        for spine in ax.spines.values():
            spine.set_color(color)
        ax.xaxis.label.set_color(color)
        ax.yaxis.label.set_color(color)
        ax.title.set_color(color)
        
    def update_graph_layout(self):
        """Update graph layout based on selection."""
        for widget in self.graph_container.winfo_children():
            widget.destroy()
            
        active = [k for k, v in self.graph_vars.items() if v.get()]
        
        if not active:
            ctk.CTkLabel(
                self.graph_container, text="No graphs selected",
                font=("Arial", 24)
            ).pack(expand=True)
            return
            
        # Layout
        n = len(active)
        rows = 1 if n <= 2 else 2
        cols = (n + rows - 1) // rows
        
        for i in range(rows):
            self.graph_container.grid_rowconfigure(i, weight=1)
        for j in range(cols):
            self.graph_container.grid_columnconfigure(j, weight=1)
            
        # Create graphs
        for idx, key in enumerate(active):
            row = idx // cols
            col = idx % cols
            
            frame = ctk.CTkFrame(self.graph_container)
            frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            
            fig = Figure(figsize=(6, 4), dpi=80)
            ax = fig.add_subplot(111)
            self.setup_ax_colors(ax)
            fig.patch.set_facecolor('#2b2b2b' if self.ui_theme == 'dark' else '#f0f0f0')
            
            canvas = FigureCanvasTkAgg(fig, frame)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            self.graphs[f'page_{key}'] = {'fig': fig, 'ax': ax, 'canvas': canvas}
            
    def update_graphs(self):
        """Update all graphs with latest data."""
        data = self.stats_reporter.data
        
        for graph_key, graph_info in self.graphs.items():
            ax = graph_info['ax']
            ax.clear()
            self.setup_ax_colors(ax)
            
            if graph_key == 'dash_fitness' and data['generations']:
                ax.plot(data['generations'], data['best_fitness'], 'g-', label='Best', linewidth=2)
                ax.plot(data['generations'], data['mean_fitness'], 'b-', label='Mean', linewidth=2)
                ax.plot(data['generations'], data['worst_fitness'], 'r-', label='Worst', alpha=0.7)
                ax.set_xlabel('Generation')
                ax.set_ylabel('Fitness')
                ax.set_title('Fitness Evolution')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
            elif graph_key == 'page_fitness' and data['generations']:
                ax.plot(data['generations'], data['best_fitness'], 'g-', label='Best', linewidth=3)
                ax.plot(data['generations'], data['mean_fitness'], 'b-', label='Mean', linewidth=2)
                ax.plot(data['generations'], data['worst_fitness'], 'r-', label='Worst', linewidth=1, alpha=0.7)
                ax.set_xlabel('Generation', fontsize=12)
                ax.set_ylabel('Fitness', fontsize=12)
                ax.set_title('Fitness Evolution', fontsize=14, fontweight='bold')
                ax.legend(fontsize=10)
                ax.grid(True, alpha=0.3)
                
            elif graph_key == 'page_operations' and data['generations']:
                if data['mutations_count']:
                    ax.bar(data['generations'][:len(data['mutations_count'])], data['mutations_count'], 
                          label='Mutations', alpha=0.7, color='orange')
                if data['crossovers_count']:
                    ax.bar(data['generations'][:len(data['crossovers_count'])], data['crossovers_count'],
                          label='Crossovers', alpha=0.7, color='purple', bottom=data['mutations_count'][:len(data['crossovers_count'])] if data['mutations_count'] else None)
                ax.set_xlabel('Generation', fontsize=12)
                ax.set_ylabel('Count', fontsize=12)
                ax.set_title('Genetic Operations', fontsize=14, fontweight='bold')
                ax.legend(fontsize=10)
                ax.grid(True, alpha=0.3, axis='y')
                
            elif graph_key == 'page_eval_time' and data['generations']:
                ax.plot(data['generations'], data['eval_time'], 'c-', linewidth=2)
                ax.set_xlabel('Generation', fontsize=12)
                ax.set_ylabel('Time (s)', fontsize=12)
                ax.set_title('Average Evaluation Time', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3)
                
            graph_info['canvas'].draw()
            
    def update_stats(self):
        """Update statistics display."""
        data = self.stats_reporter.data
        
        if data['generations']:
            self.stat_labels['dash_gen'].configure(text=str(data['generations'][-1]))
            
        if data['best_fitness']:
            self.stat_labels['dash_best'].configure(text=f"{data['best_fitness'][-1]:.6f}")
            self.stat_labels['dash_mean'].configure(text=f"{data['mean_fitness'][-1]:.6f}")
            
        if data['pop_size']:
            self.stat_labels['dash_pop'].configure(text=str(data['pop_size'][-1]))
            
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.stat_labels['dash_time'].configure(text=f"{elapsed:.1f}s")
            
            if hasattr(self, 'population') and self.population:
                valid = sum(1 for ind in self.population if ind.is_valid)
                rate = valid / elapsed if elapsed > 0 else 0
                self.stat_labels['dash_evals'].configure(text=f"{rate:.1f}")
                
    def update_ui(self):
        """Main UI update loop."""
        if self.root and self.root.winfo_exists():
            self.update_graphs()
            self.update_stats()
            self.root.after(self.update_interval, self.update_ui)
            
    def show_page(self, page_name):
        """Switch to a different page."""
        for name, page in self.pages.items():
            page.pack_forget()
            
        self.pages[page_name].pack(fill="both", expand=True)
        self.current_page = page_name
        
    def toggle_evolution(self):
        """Start/pause evolution."""
        if not self.is_running:
            self.start_evolution_thread()
            self.play_btn.configure(text="⏸ Pause")
            self.status_label.configure(text="● Running", text_color="green")
            self.is_running = True
            self.is_paused = False
        else:
            if self.is_paused:
                self.is_paused = False
                self.play_btn.configure(text="⏸ Pause")
                self.status_label.configure(text="● Running", text_color="green")
            else:
                self.is_paused = True
                self.play_btn.configure(text="▶ Resume")
                self.status_label.configure(text="● Paused", text_color="orange")
                
    def step_evolution(self):
        """Execute one generation."""
        if not self.is_running:
            self.start_evolution_thread()
            self.is_running = True
        self.is_paused = True
        self.step_mode = True
        
    def reset_evolution(self):
        """Reset evolution."""
        self.should_stop = True
        if self.evolution_thread:
            self.evolution_thread.join(timeout=2.0)
            
        # Reset stats
        self.stats_reporter.data = {
            'generations': [], 'best_fitness': [], 'mean_fitness': [],
            'worst_fitness': [], 'pop_size': [], 'mutations_count': [],
            'crossovers_count': [], 'eval_time': []
        }
        
        super().init_evolution()
        self.should_stop = False
        self.is_running = False
        self.is_paused = False
        self.play_btn.configure(text="▶ Start")
        self.status_label.configure(text="● Stopped", text_color="gray")
        
    def update_speed(self, value):
        """Update UI refresh speed."""
        self.update_interval = int(value)
        self.speed_label.configure(text=f"{self.update_interval}ms")
        
    def update_param(self, param_name, value, component, label):
        """Update parameter value."""
        value = float(value)
        setattr(component, param_name, value)
        label.configure(text=f"{value:.3f}")
        
    def start_evolution_thread(self):
        """Start evolution in background thread."""
        if not self.evolution_thread or not self.evolution_thread.is_alive():
            self.should_stop = False
            self.step_mode = False
            self.start_time = time.time()
            self.init_evolution()
            self.evaluate()
            self.evolution_thread = threading.Thread(target=self.run_evolution, daemon=True)
            self.evolution_thread.start()
            
    def run_evolution(self):
        """Evolution loop."""
        while not self.should_stop and self._n_gen < self._max_gen:
            if not self.is_paused:
                self._new_generation()
                
                if self.step_mode:
                    self.step_mode = False
                    self.is_paused = True
                    self.root.after(0, lambda: self.play_btn.configure(text="▶ Resume"))
                    self.root.after(0, lambda: self.status_label.configure(text="● Paused", text_color="orange"))
            else:
                time.sleep(0.1)
                
    def evolve(self):
        """Start the interface."""
        # Initialize evolution - must be called before any generations
        self.init_evolution()
        self.evaluate()  # Initial evaluation before evolution starts
            
        if self.auto_start:
            self.toggle_evolution()
            
        self.root.mainloop()
        
    def on_close(self):
        """Handle window close."""
        self.should_stop = True
        if self.evolution_thread:
            self.evolution_thread.join(timeout=2.0)
        if self.root:
            self.root.quit()
            self.root.destroy()

