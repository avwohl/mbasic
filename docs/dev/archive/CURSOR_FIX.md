# Cursor Positioning and Display Reset Fix

## Problem

When typing program lines in the curses UI, the cursor would sometimes jump to incorrect positions and the display would reset unexpectedly, causing partial loss of typed text. For example:

1. User types `10 PRINT "a"` and presses Enter
2. Cursor moves to an incorrect position (one space left of where it should be)
3. User starts typing `20 PRINT "b"`
4. Partway through typing, screen resets and shows only line 10, rest is lost

## Root Cause

The issue was caused by the `keypress_timeout` setting being left at a very low value (1) after the execution system was set up. This caused npyscreen's event loop to poll very frequently, leading to excessive screen refreshes and cursor positioning glitches during normal editing.

The problem occurred because:
1. `_install_execution_handler()` set `keypress_timeout = 1` to enable frequent polling during program execution
2. The original `keypress_timeout` value wasn't being saved before modification
3. After execution completed, the timeout was restored to a hardcoded value (10) rather than the actual original value
4. Additionally, the form didn't explicitly set an initial `keypress_timeout`, relying on npyscreen's default

## Solution

The fix involved three changes in `src/ui/curses_ui.py`:

### 1. Explicit Initial Timeout (line 185)

```python
def create(self):
    """Create the form widgets."""
    # Set a reasonable keypress_timeout (in tenths of a second)
    self.keypress_timeout = 10  # 1 second timeout for normal editing
    ...
```

This ensures the form starts with a reasonable polling rate for normal editing.

### 2. Save Original Timeout Before Modification (line 684-687)

```python
def _install_execution_handler(self):
    ...
    # Store original keypress_timeout if not already stored
    if not hasattr(form, '_original_keypress_timeout'):
        form._original_keypress_timeout = getattr(form, 'keypress_timeout', 10)
        debug_log(f"Stored original keypress_timeout: {form._original_keypress_timeout}")
```

Now we save the actual current timeout value before changing it.

### 3. Restore Saved Timeout (line 795-798)

```python
def _restore_execution_handler(self):
    """Restore original execution handler."""
    ...
    # Restore keypress_timeout
    if hasattr(form, '_original_keypress_timeout'):
        form.keypress_timeout = form._original_keypress_timeout
        delattr(form, '_original_keypress_timeout')
```

After execution completes, we restore the exact original value.

## Testing

The fix was verified with:

1. **Breakpoint test suite**: All tests pass (Continue, Step, End commands work correctly)
   ```bash
   python3 tests/test_breakpoints_final.py
   ```

2. **Manual testing**: Users should test by:
   - Starting the curses UI: `python3 mbasic --ui curses`
   - Typing multiple program lines:
     ```
     10 PRINT "a"
     20 PRINT "b"
     30 PRINT "c"
     ```
   - Verifying cursor positioning remains correct
   - Running the program (Ctrl+R) to verify execution still works
   - Typing more lines after execution to verify timeout is restored

## Technical Details

### keypress_timeout Parameter

- Measured in **tenths of a second**
- Controls how often `getch()` returns when no input is available
- Lower values = more frequent polling = more CPU usage + potential display glitches
- Higher values = less frequent polling = better performance but slower background task response

### Value Guidelines

- **Normal editing**: 10 (1 second) - Good balance for interactive editing
- **During execution**: 1 (0.1 second) - Fast polling for responsive breakpoint handling
- **Never use**: 0 - Would cause excessive CPU usage and display problems

### Execution Flow

1. User presses Ctrl+R to run program
2. `on_run()` → `_schedule_execution()` → `_install_execution_handler()`
3. Handler saves original timeout and sets it to 1 for fast polling
4. Execution runs in background via `while_waiting` callback
5. When program completes/errors/stops, `_restore_execution_handler()` restores original timeout
6. Normal editing resumes with proper timeout value

## Related Files

- `src/ui/curses_ui.py`: Main implementation
- `tests/test_breakpoints_final.py`: Comprehensive test suite
- `docs/dev/BREAKPOINTS.md`: Breakpoint system documentation
- `docs/dev/CONTINUE_IMPLEMENTATION.md`: Continue/Step/End command implementation
