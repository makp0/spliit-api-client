#!/usr/bin/env python3
"""
Python client for the Spliit expense sharing application API.
"""

from .client import Spliit, CATEGORIES, get_current_timestamp

__version__ = "0.1.5"
__all__ = ["Spliit", "CATEGORIES", "get_current_timestamp"]
