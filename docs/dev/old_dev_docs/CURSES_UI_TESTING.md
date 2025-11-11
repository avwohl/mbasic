# Curses UI Testing Framework

## Overview

This document describes the testing approaches for the curses (urwid) UI backend, allowing automated testing without manual interaction.

## Problem

The curses UI runs in a full-screen terminal interface, making it difficult to:
1. Test automatically
2. Catch errors during development
3. Run in CI/CD environments
4. Debug issues

## Testing Approaches Evaluated

### 1. Direct Method Testing (Recommended)

**File:** `utils/test_curses_comprehensive.py`

**How it works:**
- Imports UI classes directly
- Creates UI components without running the main loop
- Tests individual methods (create UI, parse program, handle input)
- Catches exceptions immediately

**Pros:**
- ✓ Fast execution
- ✓ Catches most errors
- ✓ No subprocess overhead
- ✓ Easy to debug
- ✓ Can test individual methods

**Cons:**
- ✗ Doesn't test full integration
- ✗ Can't test event loop behavior
- ✗ Can't catch rendering issues

**Example:**
```python
from ui.curses_ui import CursesBackend
from iohandler.console import ConsoleIOHandler
from editing import ProgramManager

# Create components
backend = CursesBackend(io_handler, program_manager)
backend._create_ui()

# Test method directly
backend._handle_input('ctrl h')
```

**Result:** ✓ Best for unit testing and catching logic errors

---

### 2. pexpect - Process Control

**File:** `utils/test_curses_pexpect.py`

**How it works:**
- Spawns actual curses UI process
- Sends keyboard input via PTY
- Captures output
- Tests integration

**Pros:**
- ✓ Tests real process
- ✓ Can send actual keystrokes
- ✓ Integration testing
- ✓ Can detect hangs/crashes

**Cons:**
- ✗ Slower than direct testing
- ✗ Limited screen capture
- ✗ Harder to debug
- ✗ Can't easily inspect internal state

**Example:**
```python
import pexpect

child = pexpect.spawn('python3 mbasic --ui curses',
                      encoding='utf-8',
                      dimensions=(24, 80))
child.send('\x12')  # Ctrl+R
```

**Result:** ✓ Good for integration testing, detecting hangs

---

### 3. pyte - Terminal Emulator

**File:** `utils/test_curses_pyte.py`

**How it works:**
- Creates virtual terminal emulator
- Spawns process with PTY
- Captures full screen state
- Can inspect exact screen content

**Pros:**
- ✓ Full screen capture
- ✓ Can verify exact output
- ✓ Good for visual regression testing

**Cons:**
- ✗ Doesn't capture urwid output well (blank screens)
- ✗ Complex setup
- ✗ Slower than direct testing
- ✗ May not handle all terminal escape sequences

**Example:**
```python
import pyte

screen = pyte.Screen(80, 24)
stream = pyte.Stream(screen)
# Feed terminal output
stream.feed(data)
# Get screen text
screen_text = '\n'.join(screen.display)
```

**Result:** ✗ Doesn't work well with urwid (produces blank screens)

---

### 4. urwid Simulation (Partial)

**File:** `utils/test_curses_urwid_sim.py`

**How it works:**
- Uses urwid's built-in rendering without running loop
- Can render to canvas
- Direct input handler testing

**Pros:**
- ✓ Fast
- ✓ Can test input handlers directly
- ✓ Can render UI without loop

**Cons:**
- ✗ Can't test event loop
- ✗ Canvas rendering is complex
- ✗ Not full integration test

**Result:** ✓ Good for unit testing, but comprehensive test is better

---

## Recommended Approach

**Use `utils/test_curses_comprehensive.py`** for automated testing.

This combines:
1. **Direct method testing** - Fast, catches most errors
2. **pexpect integration testing** - Ensures process works end-to-end

### Test Suite Coverage

The comprehensive test checks:

1. **UI Creation** - Can UI be instantiated?
2. **Input Handlers** - Do keyboard shortcuts work?
3. **Program Parsing** - Can editor content be parsed?
4. **Run Program Method** - Does _run_program() execute without errors?
5. **pexpect Integration** - Does the full process start/stop cleanly?

### Example Error Caught

```
✗ FAIL: Run Program Method
  Error: Error in output: Runtime error:
Traceback (most recent call last):
  File "/home/wohl/cl/mbasic/src/ui/curses_ui.py", line 209, in _run_program
    self.loop.draw_screen()
```

This caught a real error where `draw_screen()` was called before the loop was running.

---

## Usage

### Run all tests:
```bash
python3 utils/test_curses_comprehensive.py
```

### Run individual test files:
```bash
# Direct method testing
python3 utils/test_curses_urwid_sim.py

# pexpect testing
python3 utils/test_curses_pexpect.py

# pyte testing (experimental)
python3 utils/test_curses_pyte.py
```

### Exit codes:
- `0` - All tests passed
- `1` - One or more tests failed

---

## Adding New Tests

To add tests to the comprehensive suite:

```python
def test_my_feature(self):
    """Test description."""
    result = TestResult("My Feature")

    try:
        # Create UI
        backend = create_backend()

        # Test something
        backend.my_method()

        # Verify
        if some_condition:
            result.success("Feature works!")
        else:
            result.fail("Feature broken")

    except Exception as e:
        result.fail(f"{type(e).__name__}: {e}")

    self.results.append(result)
    return result.passed
```

Then add to `run_all_tests()`:
```python
("My Feature", self.test_my_feature),
```

---

## Dependencies

- **pexpect** - `apt install python3-pexpect` or `pip3 install pexpect`
- **pyte** - `apt install python3-pyte` or `pip3 install pyte`
- **urwid** - `apt install python3-urwid` or `pip3 install urwid`

All are available via system packages on Ubuntu/Debian.

---

## Future Improvements

1. **Screenshot comparison** - Save "known good" screenshots, compare against them
2. **Performance testing** - Measure response times
3. **Memory leak detection** - Run for extended periods
4. **CI Integration** - Run tests in GitHub Actions
5. **Coverage reporting** - Track test coverage of UI code

---

## Conclusion

**For development testing:**
- Use `test_curses_comprehensive.py` - catches most errors quickly

**For specific needs:**
- UI method testing → Direct method tests
- Integration testing → pexpect
- Screen capture → pyte (experimental, doesn't work well with urwid currently)

The comprehensive test suite provides the best balance of speed, coverage, and error detection.
