"""Module containing a simple greeting function."""

import os
import sys
from backend.governance.icgl import ICGL
from backend.agents.capability_checker import *
import traceback


def greet():
    """Returns a simple greeting.

    Returns:
        str: A greeting string.
    """
    return 'Hello'