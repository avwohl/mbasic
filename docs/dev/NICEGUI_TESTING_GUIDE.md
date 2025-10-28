# NiceGUI Testing Guide for MBASIC Web UI

## Overview

This guide documents how to test NiceGUI applications without manual browser testing. NiceGUI provides a `user` fixture that simulates browser interactions in pure Python, making tests as fast as unit tests.

## Why This Matters

**Problem with TK Testing:**
- Required manual testing with pasted stderr output
- User became bottleneck in debug loop
- Slow iteration cycle

**Solution with NiceGUI Testing:**
- Automated testing with `user` fixture
- No browser needed - pure Python simulation
- Fast test execution
- Logical assertions (click button, verify result)
- Visual errors are rare - most issues are logical

## Setup

**Requirements:**
- NiceGUI 3.2.0+ (has built-in testing support)
- pytest
- pytest-asyncio

**Installation:**
```bash
pip install nicegui pytest-asyncio
```

## Testing Approach

### User Fixture (Recommended)

The `user` fixture cuts away the browser and replaces it with lightweight simulation. Tests run as fast as unit tests.

**Key capabilities:**
- ✓ Click buttons, links
- ✓ Input text
- ✓ Select from dropdowns
- ✓ Assert text visibility
- ✓ Find elements by type, marker, text
- ✓ Async/await support
- ✓ Multi-user scenarios

### Screen Fixture (Slower, If Needed)

Uses headless browser (Selenium). Only needed for:
- Visual rendering issues
- Complex JavaScript interactions
- Browser-specific behavior

**We should rarely need this** - the user fixture handles 99% of testing needs.

## Test Structure

### Basic Test File

```python
import pytest
from nicegui import ui
from nicegui.testing import User

# Enable the NiceGUI testing plugin
pytest_plugins = ['nicegui.testing.user_plugin']

@pytest.mark.asyncio
async def test_button_click(user: User):
    # Build UI
    counter = {'value': 0}

    def increment():
        counter['value'] += 1

    ui.button('Click me', on_click=increment)
    ui.label().mark('counter').bind_text_from(counter, 'value')

    # Open the page
    await user.open('/')

    # Test interaction
    user.find(ui.button).click()
    await user.should_see('1', marker='counter')

    user.find(ui.button).click()
    await user.should_see('2', marker='counter')
```

### Key Testing Patterns

**1. Finding Elements:**
```python
# By UI type
user.find(ui.button)
user.find(ui.input)

# By marker (recommended for complex UIs)
ui.label().mark('status')
user.find(marker='status')

# By text content
user.find('Click me')
```

**2. Interactions:**
```python
# Click
user.find(ui.button).click()

# Input text
user.find(ui.input).type('Hello')

# Select from dropdown
user.find(ui.select).choose('Option 1')
```

**3. Assertions:**
```python
# Should see text
await user.should_see('Expected text')

# Should NOT see text
await user.should_not_see('Error message')

# With marker
await user.should_see('Success', marker='status')
```

**4. Markers for Complex UIs:**
```python
# Mark important elements
ui.label('Status:').mark('status')
ui.input('Name:').mark('name_input')
ui.button('Submit').mark('submit_btn')

# Test with markers
user.find(marker='name_input').type('Alice')
user.find(marker='submit_btn').click()
await user.should_see('Hello Alice', marker='status')
```

## Testing MBASIC Web UI

### Example: Testing Editor

```python
import pytest
from nicegui import ui
from nicegui.testing import User

pytest_plugins = ['nicegui.testing.user_plugin']

@pytest.mark.asyncio
async def test_editor_basic_entry(user: User):
    """Test entering a BASIC program line."""
    # Assume we have build_mbasic_ui() function
    build_mbasic_ui()

    await user.open('/')

    # Type a program line
    user.find(marker='editor').type('10 PRINT "Hello"')

    # Press Enter or click Add Line button
    user.find(marker='add_line_btn').click()

    # Verify line appears in program listing
    await user.should_see('10 PRINT "Hello"', marker='program_listing')

@pytest.mark.asyncio
async def test_run_program(user: User):
    """Test running a simple program."""
    build_mbasic_ui()
    await user.open('/')

    # Enter program
    user.find(marker='editor').type('10 PRINT "TEST"')
    user.find(marker='add_line_btn').click()

    # Run program
    user.find(marker='run_btn').click()

    # Check output
    await user.should_see('TEST', marker='output')

@pytest.mark.asyncio
async def test_syntax_error_display(user: User):
    """Test that syntax errors are shown."""
    build_mbasic_ui()
    await user.open('/')

    # Enter invalid line
    user.find(marker='editor').type('10 PRINT')
    user.find(marker='add_line_btn').click()

    # Should see error indicator
    await user.should_see('Syntax error', marker='error_display')
```

### Example: Testing Menu Commands

```python
@pytest.mark.asyncio
async def test_file_menu_new(user: User):
    """Test File > New clears the program."""
    build_mbasic_ui()
    await user.open('/')

    # Enter a line
    user.find(marker='editor').type('10 END')
    user.find(marker='add_line_btn').click()
    await user.should_see('10 END')

    # Click File menu
    user.find(marker='file_menu').click()

    # Click New
    user.find(marker='menu_new').click()

    # Confirm dialog (if exists)
    user.find(marker='confirm_yes').click()

    # Program should be cleared
    await user.should_not_see('10 END')

@pytest.mark.asyncio
async def test_run_menu_stop(user: User):
    """Test Run > Stop interrupts execution."""
    build_mbasic_ui()
    await user.open('/')

    # Enter infinite loop
    user.find(marker='editor').type('10 GOTO 10')
    user.find(marker='add_line_btn').click()

    # Run
    user.find(marker='run_btn').click()

    # Stop
    user.find(marker='stop_btn').click()

    # Should show stopped message
    await user.should_see('Stopped', marker='status')
```

### Example: Testing Breakpoints

```python
@pytest.mark.asyncio
async def test_breakpoint_stops_execution(user: User):
    """Test that breakpoints halt execution."""
    build_mbasic_ui()
    await user.open('/')

    # Enter program
    user.find(marker='editor').type('10 PRINT "A"')
    user.find(marker='add_line_btn').click()
    user.find(marker='editor').type('20 PRINT "B"')
    user.find(marker='add_line_btn').click()

    # Set breakpoint on line 20
    user.find(marker='line_20').click()  # Select line
    user.find(marker='toggle_breakpoint_btn').click()

    # Should see breakpoint indicator
    await user.should_see('●', marker='line_20_status')

    # Run program
    user.find(marker='run_btn').click()

    # Should stop at breakpoint
    await user.should_see('A', marker='output')
    await user.should_not_see('B', marker='output')
    await user.should_see('Paused at line 20', marker='status')
```

## Test Organization

```
tests/
├── nicegui/                    # NiceGUI web UI tests
│   ├── conftest.py            # Shared fixtures
│   ├── test_editor.py         # Editor functionality
│   ├── test_execution.py      # Program execution
│   ├── test_menus.py          # Menu commands
│   ├── test_breakpoints.py    # Debugger features
│   ├── test_variables.py      # Variables window
│   └── test_immediate.py      # Immediate mode
└── run_nicegui_tests.py       # Test runner
```

## Running Tests

```bash
# Run all NiceGUI tests
cd venv-nicegui
source bin/activate
pytest tests/nicegui/

# Run specific test file
pytest tests/nicegui/test_editor.py

# Run specific test
pytest tests/nicegui/test_editor.py::test_editor_basic_entry

# Verbose output
pytest tests/nicegui/ -v

# Show print statements
pytest tests/nicegui/ -s
```

## Best Practices

### 1. Use Markers Extensively

```python
# Good - testable
ui.button('Run', on_click=run_program).mark('run_btn')
ui.label('Ready').mark('status')
ui.textarea('').mark('output')

# Bad - hard to find
ui.button('Run', on_click=run_program)
ui.label('Ready')
ui.textarea('')
```

### 2. Test Logical Flow, Not Visuals

```python
# Good - tests functionality
user.find(marker='run_btn').click()
await user.should_see('Program output', marker='output')

# Bad - testing visual appearance (usually unnecessary)
# These are rare edge cases
```

### 3. Use Async/Await Properly

```python
# Good
await user.open('/')
user.find(ui.button).click()
await user.should_see('Result')

# Bad - missing await on assertions
user.find(ui.button).click()
user.should_see('Result')  # Missing await!
```

### 4. Create Reusable Fixtures

```python
# conftest.py
import pytest
from nicegui.testing import User

@pytest.fixture
async def mbasic_user(user: User):
    """User with MBASIC UI already loaded."""
    build_mbasic_ui()
    await user.open('/')
    return user

# test_editor.py
async def test_something(mbasic_user: User):
    mbasic_user.find(marker='editor').type('10 END')
    # ...
```

### 5. Test One Thing Per Test

```python
# Good
async def test_add_line(mbasic_user: User):
    mbasic_user.find(marker='editor').type('10 END')
    mbasic_user.find(marker='add_btn').click()
    await mbasic_user.should_see('10 END')

async def test_delete_line(mbasic_user: User):
    # Setup...
    mbasic_user.find(marker='delete_btn').click()
    await mbasic_user.should_not_see('10 END')

# Bad - testing multiple things
async def test_editor_everything(mbasic_user: User):
    # Add, delete, edit, run, stop, etc. all in one test
```

## Comparison: CLI vs TK vs NiceGUI Testing

| Aspect | CLI | TK | NiceGUI |
|--------|-----|-----|---------|
| Testability | ✅ Excellent | ❌ Poor | ✅ Excellent |
| Speed | ✅ Fast | ❌ Manual | ✅ Fast |
| Automation | ✅ Full | ⚠️ Partial | ✅ Full |
| User involvement | None | Heavy | None |
| Debug loop | Fast | Slow | Fast |

## Debugging Tests

### Print Debugging

```python
async def test_something(user: User):
    user.find(marker='btn').click()

    # Print current page content (debugging)
    print(await user.get_text())

    await user.should_see('Expected')
```

### Check Element Exists

```python
# Verify element exists before clicking
assert user.find(marker='my_btn') is not None
user.find(marker='my_btn').click()
```

### Run Single Test with Output

```bash
pytest tests/nicegui/test_editor.py::test_something -v -s
```

## Summary

**Key Points:**
1. NiceGUI's `user` fixture enables fast automated testing
2. No browser needed - pure Python simulation
3. Test logical interactions, not visual appearance
4. Use markers to identify UI elements
5. Write one test per feature
6. Fast iteration without user involvement

**This solves the TK testing problem** - we can now test the web UI as thoroughly as we tested the CLI, with fast automated tests and no manual bottleneck.
