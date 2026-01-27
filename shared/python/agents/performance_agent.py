"""Compatibility shim for tests that import `PerformanceAgent`.

Historically the agent was named `PerformanceAgent`; current code uses
`PerformanceAnalyzerAgent` in `performance_analyzer.py`. This module
re-exports the class under the older name so imports remain stable.
"""

from .performance_analyzer import PerformanceAnalyzerAgent as PerformanceAgent

__all__ = ["PerformanceAgent"]
