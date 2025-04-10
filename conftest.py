"""
PyTest configuration for test result reporting
"""

import os
import sys
import pytest

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import our custom reporter
from custom_json_reporter import *

# If you need any other pytest configurations, add them below
# For example, you might want to define additional fixtures or hooks

# Note that we're not using the original pytest_results_plugin anymore
# pytest_plugins = ["pytest_results_plugin"]  # This line should be commented out or removed