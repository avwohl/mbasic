#!/usr/bin/env python3
"""
Test MBASIC Web UI features that are currently broken.

These tests SHOULD FAIL until the bugs are fixed.
Tests for:
- Show Variables window (currently shows empty)
- Show Stack window (currently shows empty)
- Auto-numbering in editor (currently doesn't work)
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
import pytest
from nicegui.testing import User
from src.iohandler.console import ConsoleIOHandler
from src.editing import ProgramManager
from src.parser import TypeInfo


def create_def_type_map():
    """Create default DEF type map (all SINGLE precision)"""
    def_type_map = {}
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        def_type_map[letter] = TypeInfo.SINGLE
    return def_type_map


@pytest.mark.asyncio
async def test_show_variables_window():
    """Test that Show Variables displays actual variables.

    BUG: Currently shows 'No variables defined yet' even after running
    a program with variables because it checks runtime.variables instead
    of runtime.get_all_variables().
    """
    from src.ui.web.nicegui_backend import NiceGUIBackend

    io_handler = ConsoleIOHandler()
    program_mgr = ProgramManager(create_def_type_map())
    backend = NiceGUIBackend(io_handler, program_mgr)
    backend.build_ui()

    # Create a simple program with variables
    program_mgr.add_or_replace_line('10 K=2')
    program_mgr.add_or_replace_line('20 X$="HELLO"')
    program_mgr.add_or_replace_line('30 END')

    # Parse and run the program
    backend._menu_run()

    # Wait for program to complete
    await asyncio.sleep(0.5)

    # Check that runtime has variables
    assert backend.runtime is not None, "Runtime should exist after running program"
    variables = backend.runtime.get_all_variables()
    assert 'K' in variables or 'k' in variables, "Variable K should exist"
    assert 'X$' in variables or 'x$' in variables, "Variable X$ should exist"

    # Now test Show Variables window
    # This should NOT show "No variables defined yet"
    # But currently DOES because of the bug
    backend._show_variables_window()

    # The method should create a dialog with variables
    # We can't easily test the dialog content in unit tests,
    # but we can verify it doesn't show the error notification
    # TODO: Add proper assertion when we can inspect dialogs


@pytest.mark.asyncio
async def test_show_stack_window():
    """Test that Show Stack displays actual GOSUB stack.

    BUG: Currently shows 'Stack is empty' because it checks
    runtime.gosub_stack instead of runtime.execution_stack.
    """
    from src.ui.web.nicegui_backend import NiceGUIBackend

    io_handler = ConsoleIOHandler()
    program_mgr = ProgramManager(create_def_type_map())
    backend = NiceGUIBackend(io_handler, program_mgr)
    backend.build_ui()

    # Create a program with GOSUB
    program_mgr.add_or_replace_line('10 GOSUB 100')
    program_mgr.add_or_replace_line('20 END')
    program_mgr.add_or_replace_line('100 RETURN')

    # Parse program
    backend._parse_program()

    # TODO: Need to pause execution mid-GOSUB to test stack
    # This is hard to test without debugger/breakpoint support
    # For now, this documents the expected behavior


@pytest.mark.asyncio
async def test_auto_numbering_on_enter(user: User):
    """Test that pressing Enter in editor auto-numbers the next line.

    BUG: Auto-numbering doesn't work because JavaScript uses undefined
    'event' variable instead of preventing default properly.

    Expected behavior:
    1. Type 'PRINT "HELLO"' in editor
    2. Press Enter
    3. Editor should show:
       10 PRINT "HELLO"
       20
    4. Cursor should be after the line number
    """
    from src.ui.web.nicegui_backend import NiceGUIBackend

    io_handler = ConsoleIOHandler()
    program_mgr = ProgramManager(create_def_type_map())
    backend = NiceGUIBackend(io_handler, program_mgr)
    backend.build_ui()

    await user.open('/')

    # Enable auto-numbering
    backend.settings_manager.set('editor.auto_number', True)
    backend.settings_manager.set('editor.auto_number_step', 10)

    # Type in editor
    editor = user.find(marker='editor')
    editor.type('PRINT "HELLO"')

    # Press Enter - should auto-number
    # This currently DOESN'T WORK due to JavaScript bug
    await user.press_key('Enter')

    # Wait for JavaScript to execute
    await asyncio.sleep(0.2)

    # Editor should now contain auto-numbered line
    # Expected: "10 PRINT "HELLO"\n20 "
    # Actual: Just a newline, no line number

    # TODO: Add assertion to check editor value contains "10 PRINT"
    # Can't easily test textarea value with current NiceGUI testing API


@pytest.mark.asyncio
async def test_auto_numbering_increments(user: User):
    """Test that auto-numbering increments based on existing lines.

    If editor has:
    10 PRINT "A"
    20 PRINT "B"

    And user types 'PRINT "C"' and presses Enter,
    it should become:
    10 PRINT "A"
    20 PRINT "B"
    30 PRINT "C"
    40
    """
    from src.ui.web.nicegui_backend import NiceGUIBackend

    io_handler = ConsoleIOHandler()
    program_mgr = ProgramManager(create_def_type_map())
    backend = NiceGUIBackend(io_handler, program_mgr)
    backend.build_ui()

    await user.open('/')

    # Enable auto-numbering
    backend.settings_manager.set('editor.auto_number', True)
    backend.settings_manager.set('editor.auto_number_step', 10)

    # Put existing lines in editor
    backend.editor.value = '10 PRINT "A"\n20 PRINT "B"\n'

    # Type new line and press Enter
    editor = user.find(marker='editor')
    # Position at end
    editor.click()
    editor.type('PRINT "C"')
    await user.press_key('Enter')

    await asyncio.sleep(0.2)

    # Should auto-number to 30
    # TODO: Add assertion


def test_variables_bug_analysis():
    """Verify that _show_variables_window uses get_all_variables().

    This is a pure code analysis test - no UI needed.
    """
    from src.ui.web.nicegui_backend import NiceGUIBackend
    import inspect

    # Get the source code
    source = inspect.getsource(NiceGUIBackend._show_variables_window)

    # The CORRECT code should be:
    #     variables = self.runtime.get_all_variables()

    # The WRONG code was:
    # if hasattr(self.runtime, 'variables'):
    #     variables = self.runtime.variables

    # Check that the fix is in place
    assert 'get_all_variables()' in source, \
        "BUG: _show_variables_window should use runtime.get_all_variables()"

    # Make sure the OLD buggy code is NOT there
    if "hasattr(self.runtime, 'variables')" in source:
        pytest.fail(
            "BUG STILL EXISTS: _show_variables_window still checks hasattr for 'variables'. "
            "Should use get_all_variables() directly!"
        )


def test_stack_bug_analysis():
    """Document the exact bug in _show_stack_window.

    This is a pure code analysis test - no UI needed.
    """
    from src.ui.web.nicegui_backend import NiceGUIBackend
    import inspect

    source = inspect.getsource(NiceGUIBackend._show_stack_window)

    # The bug is:
    # if hasattr(self.runtime, 'gosub_stack'):
    #     stack = self.runtime.gosub_stack

    # It should be:
    #     stack = self.runtime.execution_stack

    if "'gosub_stack')" in source:
        pytest.fail(
            "BUG STILL EXISTS: _show_stack_window uses runtime.gosub_stack "
            "instead of runtime.execution_stack. "
            "Stack will always show as empty!"
        )


def test_auto_numbering_bug_analysis():
    """Document the exact bug in _on_enter_key.

    This is a pure code analysis test - no UI needed.
    """
    from src.ui.web.nicegui_backend import NiceGUIBackend
    import inspect

    source = inspect.getsource(NiceGUIBackend._on_enter_key)

    # The bug is in the JavaScript:
    # event.preventDefault();
    #
    # But 'event' is not defined in that scope!
    # The event comes from Python side as parameter 'e'

    if 'event.preventDefault' in source:
        pytest.fail(
            "BUG STILL EXISTS: _on_enter_key JavaScript uses 'event.preventDefault()' "
            "but 'event' is not defined in the JavaScript scope. "
            "Auto-numbering will not work!"
        )


if __name__ == '__main__':
    # Run tests - these SHOULD FAIL until bugs are fixed
    print("=" * 70)
    print("Running tests for KNOWN BUGS in web UI")
    print("These tests SHOULD FAIL until the bugs are fixed")
    print("=" * 70)
    pytest.main([__file__, '-v', '-s'])
