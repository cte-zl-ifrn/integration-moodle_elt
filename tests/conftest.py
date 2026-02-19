"""
Pytest configuration and fixtures.
"""

import sys
from pathlib import Path

# Add dags directory to Python path for imports
dags_path = Path(__file__).parent.parent / 'dags'
sys.path.insert(0, str(dags_path))

# Import all fixtures
pytest_plugins = ['tests.fixtures.common_fixtures']
