"""
The Reporter package.

This package provides the following classes for reporting and monitoring
the progress and statistics of evolutionary algorithms:

- `BaseReporter`: The base class for all reporter types.
- `StatisticsReporter`: A reporter specialized in collecting and displaying evolution statistics.
- `ReporterSet`: A container for managing multiple reporters simultaneously.
"""

from .base import BaseReporter, StatisticsReporter
from .reporter_set import ReporterSet

__all__ = [
    "BaseReporter",
    "StatisticsReporter",
    "ReporterSet",
]
