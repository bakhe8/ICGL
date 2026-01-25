"""
Module containing mathematical operations.
"""

from backend.agents.base import Problem
import asyncio
import os
import sys
from backend.agents.builder import BuilderAgent


def add_numbers(a: int, b: int) -> int:
    """
    Adds two numbers and returns the result.

    :param a: First number
    :param b: Second number
    :return: Sum of a and b
    """
    return a + b
