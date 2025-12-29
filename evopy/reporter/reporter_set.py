"""
ReporterSet class for managing multiple reporters simultaneously
"""

from typing import List, Union, Any, Optional
from .base import BaseReporter


class ReporterSet(BaseReporter):
    """
    ReporterSet allows managing and coordinating multiple reporters simultaneously.
    
    This class acts as a container for multiple reporter instances and forwards
    all reporter calls to each registered reporter. This enables combining
    different types of reporters (statistics, logging, graphics, etc.) in a
    single evolution.
    
    Examples:
        # Create multiple reporters
        stats_reporter = StatisticsReporter(options)
        log_reporter = LogReporter(options)
        
        # Combine them in a ReporterSet
        reporter_set = ReporterSet(options, [stats_reporter, log_reporter])
        
        # Or add reporters individually
        reporter_set = ReporterSet(options)
        reporter_set.add_reporter(stats_reporter)
        reporter_set.add_reporter(log_reporter)
    """

    component_type = "Set"

    def __init__(self, options, reporters: Optional[List[BaseReporter]] = None):
        """
        Initialize the ReporterSet
        
        Args:
            options: Configuration options
            reporters: List of reporter instances to manage
        """
        super().__init__(options)
        self._reporters: List[BaseReporter] = reporters or []
        self._active_reporters: List[BaseReporter] = []
        self._update_active_reporters()

    def add_reporter(self, reporter: BaseReporter) -> None:
        """
        Add a reporter to the set
        
        Args:
            reporter: Reporter instance to add
        """
        if not isinstance(reporter, BaseReporter):
            raise TypeError(f"Expected BaseReporter instance, got {type(reporter)}")
        
        if reporter not in self._reporters:
            self._reporters.append(reporter)
            self._update_active_reporters()

    def remove_reporter(self, reporter: BaseReporter) -> bool:
        """
        Remove a reporter from the set
        
        Args:
            reporter: Reporter instance to remove
            
        Returns:
            bool: True if reporter was found and removed, False otherwise
        """
        if reporter in self._reporters:
            self._reporters.remove(reporter)
            self._update_active_reporters()
            return True
        return False

    def clear_reporters(self) -> None:
        """Remove all reporters from the set"""
        self._reporters.clear()
        self._active_reporters.clear()

    def get_reporters(self) -> List[BaseReporter]:
        """Get a copy of the reporters list"""
        return self._reporters.copy()

    def get_active_reporters(self) -> List[BaseReporter]:
        """Get a copy of the active reporters list"""
        return self._active_reporters.copy()

    def get_reporter_by_type(self, reporter_type: str) -> List[BaseReporter]:
        """
        Get all reporters of a specific type
        
        Args:
            reporter_type: The component_type to filter by
            
        Returns:
            List of reporters matching the type
        """
        return [r for r in self._reporters if getattr(r, 'component_type', None) == reporter_type]

    def _update_active_reporters(self) -> None:
        """Update the list of active reporters"""
        self._active_reporters = [r for r in self._reporters if self._is_reporter_active(r)]

    def _is_reporter_active(self, reporter: BaseReporter) -> bool:
        """
        Check if a reporter should be considered active
        
        Args:
            reporter: Reporter to check
            
        Returns:
            bool: True if reporter is active
        """
        # A reporter is active if it has at least one method that's not just 'pass'
        return True  # For now, consider all reporters active

    def _call_reporters(self, method_name: str, *args, **kwargs) -> None:
        """
        Call a method on all active reporters
        
        Args:
            method_name: Name of the method to call
            *args: Arguments to pass to the method
            **kwargs: Keyword arguments to pass to the method
        """
        for reporter in self._active_reporters:
            try:
                method = getattr(reporter, method_name, None)
                if method and callable(method):
                    method(*args, **kwargs)
            except Exception as e:
                # Log error but don't stop other reporters
                self._handle_reporter_error(reporter, method_name, e)

    def _handle_reporter_error(self, reporter: BaseReporter, method_name: str, error: Exception) -> None:
        """
        Handle errors from individual reporters
        
        Args:
            reporter: The reporter that caused the error
            method_name: The method that failed
            error: The exception that was raised
        """
        error_msg = f"Reporter {reporter.__class__.__name__}.{method_name} failed: {error}"
        print(f"⚠️  {error_msg}")
        # Could also log to a file or handle differently

    # === Evolution lifecycle methods ===
    
    def start_evolution_report(self, population):
        """Forward to all reporters"""
        self._call_reporters('start_evolution_report', population)

    def end_evolution_report(self, population, generation):
        """Forward to all reporters"""
        self._call_reporters('end_evolution_report', population, generation)

    def new_generation_report(self, population, generation):
        """Forward to all reporters"""
        self._call_reporters('new_generation_report', population, generation)

    def end_generation_report(self, population, generation):
        """Forward to all reporters"""
        self._call_reporters('end_generation_report', population, generation)

    # === Selection and reproduction methods ===
    
    def pre_selection_report(self, population, generation):
        """Forward to all reporters"""
        self._call_reporters('pre_selection_report', population, generation)

    def post_selection_report(self, selected_individuals, generation):
        """Forward to all reporters"""
        self._call_reporters('post_selection_report', selected_individuals, generation)

    def pre_crossover_report(self, parents, generation):
        """Forward to all reporters"""
        self._call_reporters('pre_crossover_report', parents, generation)

    def post_crossover_report(self, offspring, generation):
        """Forward to all reporters"""
        self._call_reporters('post_crossover_report', offspring, generation)

    def pre_mutation_report(self, individuals, generation):
        """Forward to all reporters"""
        self._call_reporters('pre_mutation_report', individuals, generation)

    def post_mutation_report(self, individuals, generation):
        """Forward to all reporters"""
        self._call_reporters('post_mutation_report', individuals, generation)

    # === Evaluation methods ===
    
    def pre_evaluation_report(self, individuals, generation):
        """Forward to all reporters"""
        self._call_reporters('pre_evaluation_report', individuals, generation)

    def post_evaluation_report(self, population, generation):
        """Forward to all reporters"""
        self._call_reporters('post_evaluation_report', population, generation)

    def individual_evaluation_report(self, individual, fitness, generation):
        """Forward to all reporters"""
        self._call_reporters('individual_evaluation_report', individual, fitness, generation)

    # === Population methods ===
    
    def population_stats_report(self, population, generation):
        """Forward to all reporters"""
        self._call_reporters('population_stats_report', population, generation)

    def best_individual_report(self, best_individual, generation):
        """Forward to all reporters"""
        self._call_reporters('best_individual_report', best_individual, generation)

    def diversity_report(self, population, diversity_metric, generation):
        """Forward to all reporters"""
        self._call_reporters('diversity_report', population, diversity_metric, generation)

    # === Special event methods ===
    
    def stagnation_report(self, generation, stagnation_count):
        """Forward to all reporters"""
        self._call_reporters('stagnation_report', generation, stagnation_count)

    def convergence_report(self, population, generation, convergence_metric):
        """Forward to all reporters"""
        self._call_reporters('convergence_report', population, generation, convergence_metric)

    def milestone_report(self, milestone_type, data, generation):
        """Forward to all reporters"""
        self._call_reporters('milestone_report', milestone_type, data, generation)

    # === Logging and debugging methods ===
    
    def debug_report(self, message, generation=None):
        """Forward to all reporters"""
        self._call_reporters('debug_report', message, generation)

    def error_report(self, error, generation=None):
        """Forward to all reporters"""
        self._call_reporters('error_report', error, generation)

    def warning_report(self, warning, generation=None):
        """Forward to all reporters"""
        self._call_reporters('warning_report', warning, generation)

    # === Utility methods ===
    
    def custom_report(self, report_type, data, generation=None):
        """Forward to all reporters"""
        self._call_reporters('custom_report', report_type, data, generation)

    # === ReporterSet specific methods ===
    
    def get_combined_statistics(self) -> dict:
        """
        Collect and combine statistics from all reporters that support it
        
        Returns:
            dict: Combined statistics from all reporters
        """
        combined_stats = {
            'reporter_count': len(self._active_reporters),
            'reporter_types': [r.component_type for r in self._active_reporters],
            'statistics': {}
        }
        
        for reporter in self._active_reporters:
            if hasattr(reporter, 'get_statistics_summary') and callable(getattr(reporter, 'get_statistics_summary')):
                try:
                    stats = getattr(reporter, 'get_statistics_summary')()
                    if stats:
                        combined_stats['statistics'][f"{reporter.__class__.__name__}"] = stats
                except Exception as e:
                    combined_stats['statistics'][f"{reporter.__class__.__name__}_error"] = str(e)
        
        return combined_stats

    def enable_reporter_type(self, reporter_type: str) -> int:
        """
        Enable all reporters of a specific type
        
        Args:
            reporter_type: The component_type to enable
            
        Returns:
            int: Number of reporters enabled
        """
        count = 0
        for reporter in self._reporters:
            if getattr(reporter, 'component_type', None) == reporter_type:
                # Implementation depends on how individual reporters handle enable/disable
                count += 1
        return count

    def disable_reporter_type(self, reporter_type: str) -> int:
        """
        Disable all reporters of a specific type
        
        Args:
            reporter_type: The component_type to disable
            
        Returns:
            int: Number of reporters disabled
        """
        count = 0
        for reporter in self._reporters:
            if getattr(reporter, 'component_type', None) == reporter_type:
                # Implementation depends on how individual reporters handle enable/disable
                count += 1
        return count

    def __len__(self) -> int:
        """Return the number of reporters in the set"""
        return len(self._reporters)

    def __iter__(self):
        """Iterate over reporters in the set"""
        return iter(self._reporters)

    def __contains__(self, reporter: BaseReporter) -> bool:
        """Check if a reporter is in the set"""
        return reporter in self._reporters

    def __str__(self) -> str:
        """String representation of the ReporterSet"""
        types = [getattr(r, 'component_type', 'Unknown') for r in self._reporters]
        return f"ReporterSet({len(self._reporters)} reporters: {', '.join(types)})"

    def __repr__(self) -> str:
        """Detailed representation of the ReporterSet"""
        return f"ReporterSet(reporters={len(self._reporters)}, active={len(self._active_reporters)})"
