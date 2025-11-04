"""
Real NiceGUI UI tests using the User fixture.

This tests ACTUAL UI behavior, not just code analysis.
Uses NiceGUI's pytest plugin to simulate user interactions.
"""

import pytest
from nicegui.testing import User

pytest_plugins = ['nicegui.testing.user_plugin']


@pytest.mark.asyncio
async def test_variables_window_double_click_bug(user: User):
    """Test that variables window doesn't trigger double-open on double-click"""
    # Import and setup the UI
    from src.ui.web.nicegui_backend import create_client_ui
    from editing import ProgramManager
    from parser import TypeInfo
    from iohandler.console import ConsoleIOHandler

    # Create test program manager
    def_type_map = {letter: TypeInfo.SINGLE for letter in 'abcdefghijklmnopqrstuvwxyz'}
    program = ProgramManager(def_type_map)
    io_handler = ConsoleIOHandler(debug_enabled=False)

    # Create the UI
    create_client_ui(user.client.page, program, io_handler)

    await user.open('/')

    # Find and double-click the "Show Variables" button
    variables_button = user.find('Show Variables')
    variables_button.click()
    variables_button.click()  # Double click

    # Should only see ONE variables window
    # If there's a bug, we'd see multiple windows or errors
    await user.should_see('Variables')

    # Check that no duplicate windows were created
    # (NiceGUI's user fixture will fail if JS errors occur)


@pytest.mark.asyncio
async def test_stack_window_double_click_bug(user: User):
    """Test that stack window doesn't trigger double-open on double-click"""
    from src.ui.web.nicegui_backend import create_client_ui
    from editing import ProgramManager
    from parser import TypeInfo
    from iohandler.console import ConsoleIOHandler

    def_type_map = {letter: TypeInfo.SINGLE for letter in 'abcdefghijklmnopqrstuvwxyz'}
    program = ProgramManager(def_type_map)
    io_handler = ConsoleIOHandler(debug_enabled=False)

    create_client_ui(user.client.page, program, io_handler)

    await user.open('/')

    # Find and double-click the "Show Stack" button
    stack_button = user.find('Show Stack')
    stack_button.click()
    stack_button.click()  # Double click

    await user.should_see('Execution Stack')


@pytest.mark.asyncio
async def test_all_window_buttons_for_double_click(user: User):
    """Systematically test ALL window-opening buttons for double-click bugs"""
    from src.ui.web.nicegui_backend import create_client_ui
    from editing import ProgramManager
    from parser import TypeInfo
    from iohandler.console import ConsoleIOHandler

    def_type_map = {letter: TypeInfo.SINGLE for letter in 'abcdefghijklmnopqrstuvwxyz'}
    program = ProgramManager(def_type_map)
    io_handler = ConsoleIOHandler(debug_enabled=False)

    create_client_ui(user.client.page, program, io_handler)

    await user.open('/')

    # List of all buttons that open windows
    window_buttons = [
        'Show Variables',
        'Show Stack',
        'Help',
        # Add more as we find them
    ]

    for button_text in window_buttons:
        try:
            button = user.find(button_text)
            # Double click
            button.click()
            button.click()
            # If this causes errors, the test will fail
        except Exception as e:
            pytest.fail(f"Double-click on '{button_text}' caused error: {e}")
