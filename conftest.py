"""
PyTest configuration for test result reporting
"""

import os
import sys
import pytest

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import our reporting plugin
#pytest_plugins = ["pytest_results_plugin"]