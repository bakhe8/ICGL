"""
A simple calculator class that supports addition and subtraction operations.
"""

from backend.agents.builder import BuilderAgent
from backend.governance.icgl import ICGL
import os
from backend.agents.base import Problem
import traceback

class Calculator:
    """Calculator class for performing basic arithmetic operations."""

    def add(self, a, b):
        """
        Add two numbers.

        :param a: First number
        :param b: Second number
        :return: Sum of a and b
        """
        return a + b

    def subtract(self, a, b):
        """
        Subtract second number from first.

        :param a: First number
        :param b: Second number
        :return: Difference of a and b
        """
        return a - b
