"""
Moodle Analytics Package
A comprehensive analytics toolkit for Moodle learning management systems.
"""

__version__ = "1.0.0"
__author__ = "Moodle Analytics Team"

from .data_loader import MoodleDataLoader
from .preprocessing import MoodleDataPreprocessor
from .analysis import MoodleAnalytics
from .visualization import MoodleVisualizer

__all__ = [
    'MoodleDataLoader',
    'MoodleDataPreprocessor', 
    'MoodleAnalytics',
    'MoodleVisualizer'
]
