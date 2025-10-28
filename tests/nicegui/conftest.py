"""
Shared fixtures for NiceGUI tests.

For MBASIC tests, we don't need a main.py file since we build UI directly in tests.
"""

import pytest

# Enable NiceGUI testing plugin
pytest_plugins = ['nicegui.testing.user_plugin']


def pytest_addoption(parser: pytest.Parser) -> None:
    """Override main_file default to empty string so tests don't need main.py."""
    parser.addini('main_file', 'main file', default='')
