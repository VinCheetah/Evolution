from evopy.component import BaseComponent


class BaseReporter(BaseComponent):

    component_name = "Reporter"
    component_type = "Base"

    def __init__(self, options):
        super().__init__(options)

    # Méthodes d'évolution générale
    def start_evolution_report(self, population):
        """Appelée au début de l'évolution"""
        pass

    def end_evolution_report(self, population, generation):
        """Appelée à la fin de l'évolution"""
        pass

    def new_generation_report(self, population, generation):
        """Appelée au début de chaque nouvelle génération"""
        pass

    def end_generation_report(self, population, generation):
        """Appelée à la fin de chaque génération"""
        pass

    # Méthodes de sélection et reproduction
    def pre_selection_report(self, population, generation):
        """Appelée avant la sélection"""
        pass

    def post_selection_report(self, selected_individuals, generation):
        """Appelée après la sélection"""
        pass

    def pre_crossover_report(self, parents, generation):
        """Appelée avant le croisement"""
        pass

    def post_crossover_report(self, offspring, generation):
        """Appelée après le croisement"""
        pass

    def pre_mutation_report(self, individuals, generation):
        """Appelée avant la mutation"""
        pass

    def post_mutation_report(self, individuals, generation):
        """Appelée après la mutation"""
        pass

    # Méthodes d'évaluation
    def pre_evaluation_report(self, individuals, generation):
        """Appelée avant l'évaluation de la population"""
        pass

    def post_evaluation_report(self, population, generation):
        """Appelée après l'évaluation de la population"""
        pass

    def individual_evaluation_report(self, individual, fitness, generation):
        """Appelée après l'évaluation d'un individu"""
        pass

    # Méthodes de population
    def population_stats_report(self, population, generation):
        """Appelée pour reporter les statistiques de population"""
        pass

    def best_individual_report(self, best_individual, generation):
        """Appelée quand un nouveau meilleur individu est trouvé"""
        pass

    def diversity_report(self, population, diversity_metric, generation):
        """Appelée pour reporter la diversité de la population"""
        pass

    # Méthodes d'événements spéciaux
    def stagnation_report(self, generation, stagnation_count):
        """Appelée quand la population stagne"""
        pass

    def convergence_report(self, population, generation, convergence_metric):
        """Appelée pour reporter la convergence"""
        pass

    def milestone_report(self, milestone_type, data, generation):
        """Appelée pour des jalons spéciaux"""
        pass

    # Méthodes de logging et debugging
    def debug_report(self, message, generation=None):
        """Appelée pour des messages de debug"""
        pass

    def error_report(self, error, generation=None):
        """Appelée pour reporter des erreurs"""
        pass

    def warning_report(self, warning, generation=None):
        """Appelée pour reporter des avertissements"""
        pass

    # Méthodes utilitaires
    def custom_report(self, report_type, data, generation=None):
        """Méthode générique pour des rapports personnalisés"""
        pass

    # Alias pour compatibilité
    def new_gen_report(self):
        """Ancienne méthode - utiliser new_generation_report à la place"""
        pass


class StatisticsReporter(BaseReporter):
    """
    Reporter pour collecter et afficher les statistiques principales
    lors d'une évolution classique
    """

    component_type = "Statistics"

    def __init__(self, options):
        super().__init__(options)
        self.generation_stats = []
        self.best_fitness_history = []
        self.average_fitness_history = []
        self.diversity_history = []
        self.start_time = None
        self.end_time = None

    def start_evolution_report(self, population):
        """Initialise le suivi des statistiques"""
        import time
        self.start_time = time.time()
        self.generation_stats = []
        self.best_fitness_history = []
        self.average_fitness_history = []
        self.diversity_history = []
        print(f"Début de l'évolution avec {len(population)} individus")

    def end_evolution_report(self, population, generation):
        """Affiche les statistiques finales"""
        import time
        self.end_time = time.time()
        duration = self.end_time - (self.start_time or 0)
        
        best = max(population, key=lambda ind: ind.fitness)
        print(f"\n=== Évolution terminée ===")
        print(f"Générations: {generation}")
        print(f"Durée: {duration:.2f} secondes")
        print(f"Meilleur fitness: {best.fitness}")
        if self.best_fitness_history:
            print(f"Amélioration totale: {self.best_fitness_history[-1] - self.best_fitness_history[0]:.4f}")

    def new_generation_report(self, population, generation):
        """Collecte les statistiques de la génération"""
        fitnesses = [ind.fitness for ind in population if hasattr(ind, 'fitness')]
        
        if fitnesses:
            best_fitness = max(fitnesses)
            avg_fitness = sum(fitnesses) / len(fitnesses)
            worst_fitness = min(fitnesses)
            
            self.best_fitness_history.append(best_fitness)
            self.average_fitness_history.append(avg_fitness)
            
            stats = {
                'generation': generation,
                'best_fitness': best_fitness,
                'average_fitness': avg_fitness,
                'worst_fitness': worst_fitness,
                'population_size': len(population)
            }
            self.generation_stats.append(stats)
            
            # Affichage périodique
            if generation % 10 == 0 or generation < 10:
                print(f"Gen {generation:3d}: Best={best_fitness:.4f}, "
                      f"Avg={avg_fitness:.4f}, Worst={worst_fitness:.4f}")

    def best_individual_report(self, best_individual, generation):
        """Signale quand un nouveau record est atteint"""
        if hasattr(best_individual, 'fitness'):
            print(f"Nouveau meilleur individu à la génération {generation}: "
                  f"fitness = {best_individual.fitness:.4f}")

    def population_stats_report(self, population, generation):
        """Calcule et affiche des statistiques détaillées de population"""
        fitnesses = [ind.fitness for ind in population if hasattr(ind, 'fitness')]
        
        if fitnesses:
            import statistics
            mean_fitness = statistics.mean(fitnesses)
            median_fitness = statistics.median(fitnesses)
            stdev_fitness = statistics.stdev(fitnesses) if len(fitnesses) > 1 else 0
            
            print(f"Stats Gen {generation}: Mean={mean_fitness:.4f}, "
                  f"Median={median_fitness:.4f}, StdDev={stdev_fitness:.4f}")

    def diversity_report(self, population, diversity_metric, generation):
        """Enregistre la diversité de la population"""
        self.diversity_history.append(diversity_metric)
        if generation % 20 == 0:
            print(f"Diversité génération {generation}: {diversity_metric:.4f}")

    def stagnation_report(self, generation, stagnation_count):
        """Alerte en cas de stagnation"""
        if stagnation_count > 10:
            print(f"⚠️  Stagnation détectée: {stagnation_count} générations sans amélioration "
                  f"(génération {generation})")

    def convergence_report(self, population, generation, convergence_metric):
        """Rapport sur la convergence de la population"""
        if convergence_metric > 0.9:
            print(f"🎯 Convergence élevée détectée (génération {generation}): "
                  f"{convergence_metric:.2%}")

    def get_statistics_summary(self):
        """Retourne un résumé des statistiques collectées"""
        return {
            'total_generations': len(self.generation_stats),
            'best_fitness_history': self.best_fitness_history,
            'average_fitness_history': self.average_fitness_history,
            'diversity_history': self.diversity_history,
            'generation_stats': self.generation_stats,
            'evolution_time': self.end_time - self.start_time if self.end_time and self.start_time else None
        }

    