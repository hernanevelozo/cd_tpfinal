"""Distributed Ant Colony Optimization (ACO) for TSP.

This package is a refactored version of the original monolithic script
into a clean, testable, and modular structure.
"""
__all__ = ["core", "network"]
from .network.worker import Worker as ACONode