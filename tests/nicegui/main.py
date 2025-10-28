"""Dummy main file for NiceGUI tests.

This file is required by NiceGUI's testing framework.
The actual UI is built in test functions using @ui.page('/') decorator.
"""

from nicegui import ui

# This needs to be called for NiceGUI tests to work
# The actual UI pages are defined in test functions
if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
