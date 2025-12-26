"""
Moodle Analytics Data Package
Sample data generation and utilities for testing.
"""

__version__ = "1.0.0"
__author__ = "Moodle Analytics Team"

from .analysis import (
    get_sample_engagement_data,
    get_sample_quiz_data, 
    get_sample_forum_data,
    get_sample_completion_data
)
from .data_loader import SampleDataLoader
from .preprocessing import SampleDataPreprocessor
from .visualization import SampleVisualizer

__all__ = [
    'get_sample_engagement_data',
    'get_sample_quiz_data', 
    'get_sample_forum_data',
    'get_sample_completion_data',
    'SampleDataLoader',
    'SampleDataPreprocessor',
    'SampleVisualizer'
]
