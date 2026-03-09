"""
Explainability Benchmark Framework

A unified framework for evaluating explainability of knowledge graph-enhanced
recommendation models.

Usage:
    from evaluation import UnifiedEvaluator
    
    evaluator = UnifiedEvaluator("ml1m")
    metrics = evaluator.evaluate_model("vrkg4rec")
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .evaluation import UnifiedEvaluator
from .adapters import BaseAdapter

__all__ = [
    'UnifiedEvaluator',
    'BaseAdapter',
]
