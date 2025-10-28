#!/usr/bin/env python3
"""
Test MBASIC NiceGUI web UI.

Tests the basic functionality of the NiceGUI-based web interface.
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
async def test_ui_loads(user: User):
    """Test that the UI loads without errors."""
    from src.ui.web.nicegui_backend import NiceGUIBackend

    # Create backend
    io_handler = ConsoleIOHandler()
    program_mgr = ProgramManager(create_def_type_map())
    backend = NiceGUIBackend(io_handler, program_mgr)

    # Build UI
    backend.build_ui()

    # Open page
    await user.open('/')

    # Should see title elements
    await user.should_see('Program Editor')
    await user.should_see('Output')
    await user.should_see('Ready')


@pytest.mark.asyncio
async def test_add_program_line(user: User):
    """Test adding a program line."""
    from src.ui.web.nicegui_backend import NiceGUIBackend

    io_handler = ConsoleIOHandler()
    program_mgr = ProgramManager(create_def_type_map())
    backend = NiceGUIBackend(io_handler, program_mgr)
    backend.build_ui()

    await user.open('/')

    # Type a program line
    user.find(marker='editor').type('10 PRINT "Hello"')

    # Click Add Line button
    user.find(marker='btn_add_line').click()

    # Should see line in program display
    await user.should_see('10 PRINT "Hello"', marker='program_display')

    # Editor should be cleared
    # (Can't easily test textarea value, but status should update)
    await user.should_see('Added:', marker='status')


@pytest.mark.asyncio
async def test_new_program(user: User):
    """Test File > New clears the program."""
    from src.ui.web.nicegui_backend import NiceGUIBackend

    io_handler = ConsoleIOHandler()
    program_mgr = ProgramManager(create_def_type_map())
    backend = NiceGUIBackend(io_handler, program_mgr)
    backend.build_ui()

    await user.open('/')

    # Add a line
    user.find(marker='editor').type('10 END')
    user.find(marker='btn_add_line').click()
    await user.should_see('10 END', marker='program_display')

    # Click New button
    user.find(marker='btn_new').click()

    # Program should be cleared
    await user.should_not_see('10 END')
    await user.should_see('New program', marker='status')


@pytest.mark.asyncio
async def test_clear_output(user: User):
    """Test clearing output pane."""
    from src.ui.web.nicegui_backend import NiceGUIBackend

    io_handler = ConsoleIOHandler()
    program_mgr = ProgramManager(create_def_type_map())
    backend = NiceGUIBackend(io_handler, program_mgr)
    backend.build_ui()

    await user.open('/')

    # Clear output
    user.find(marker='btn_clear_output').click()

    # Should see status update
    await user.should_see('Output cleared', marker='status')


@pytest.mark.asyncio
async def test_list_program(user: User):
    """Test Run > List Program."""
    from src.ui.web.nicegui_backend import NiceGUIBackend

    io_handler = ConsoleIOHandler()
    program_mgr = ProgramManager(create_def_type_map())
    backend = NiceGUIBackend(io_handler, program_mgr)
    backend.build_ui()

    await user.open('/')

    # Add some lines
    user.find(marker='editor').type('10 PRINT "A"')
    user.find(marker='btn_add_line').click()

    user.find(marker='editor').type('20 PRINT "B"')
    user.find(marker='btn_add_line').click()

    # List program (via menu would be better, but button works for now)
    backend._menu_list()

    # Should see program in output
    await user.should_see('10 PRINT "A"', marker='output')
    await user.should_see('20 PRINT "B"', marker='output')


@pytest.mark.asyncio
async def test_run_program(user: User):
    """Test running a simple BASIC program."""
    from src.ui.web.nicegui_backend import NiceGUIBackend

    io_handler = ConsoleIOHandler()
    program_mgr = ProgramManager(create_def_type_map())
    backend = NiceGUIBackend(io_handler, program_mgr)
    backend.build_ui()

    await user.open('/')

    # Add a simple program
    user.find(marker='editor').type('10 PRINT "Hello, World!"')
    user.find(marker='btn_add_line').click()

    user.find(marker='editor').type('20 PRINT "Testing 1 2 3"')
    user.find(marker='btn_add_line').click()

    user.find(marker='editor').type('30 END')
    user.find(marker='btn_add_line').click()

    # Run the program
    user.find(marker='btn_run').click()

    # Wait a bit for execution
    await asyncio.sleep(0.5)

    # Should see output
    await user.should_see('Hello, World!', marker='output')
    await user.should_see('Testing 1 2 3', marker='output')


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
