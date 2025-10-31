# Debug Mode

## Overview

MBASIC includes a debug mode controlled by the `MBASIC_DEBUG` environment variable. When enabled, detailed error information is output to stderr, making it easier to diagnose issues when working with Claude Code or other development tools.

## Enabling Debug Mode

Set the `MBASIC_DEBUG` environment variable to enable debug output:

```bash
# Enable debug mode
export MBASIC_DEBUG=1

# Run MBASIC
python3 mbasic program.bas

# Or inline:
MBASIC_DEBUG=1 python3 mbasic program.bas
```

Accepted values for `MBASIC_DEBUG`:
- `1` - enabled
- `true` - enabled
- `yes` - enabled
- `on` - enabled
- Any other value or unset - disabled

## What Debug Mode Does

### Normal Mode (Debug Off)

```
--- Execution error: division by zero ---
Traceback (most recent call last):
  File "...", line 123
    ...
ZeroDivisionError: division by zero
```

### Debug Mode (Debug On)

**User sees in UI:**
```
--- Execution error: division by zero ---
(Full traceback sent to stderr - check console)
```

**Developer/Claude sees on stderr:**
```
======================================================================
MBASIC DEBUG ERROR
======================================================================
Message: Execution error
Exception: ZeroDivisionError: division by zero

Traceback:
Traceback (most recent call last):
  File "/home/user/mbasic/src/ui/tk_ui.py", line 2037, in _execute_tick
    state = self.interpreter.tick(mode='run', max_statements=100)
  ...
ZeroDivisionError: division by zero

Context:
  current_line: 20
  status: running
======================================================================
```

## Benefits for Claude Code Debugging

When working with Claude Code:

1. **Cleaner UI for users** - Brief error messages in the interface
2. **Full details for Claude** - Complete tracebacks and context in stderr
3. **Context information** - Additional details like current line number, interpreter state
4. **No UI clutter** - Detailed traces don't fill up the output window

## Usage in Code

The debug logger is in `src/debug_logger.py`:

```python
from debug_logger import debug_log_error, is_debug_mode

# Log an error
try:
    risky_operation()
except Exception as e:
    error_msg = debug_log_error(
        "Operation failed",
        exception=e,
        context={'user_input': input_val, 'state': current_state}
    )
    ui.show_error(error_msg)

# Check if debug mode is enabled
if is_debug_mode():
    print("Extra debugging info", file=sys.stderr)
```

## Implementation Details

- **Module**: `src/debug_logger.py`
- **Functions**:
  - `is_debug_mode()` - Check if debug mode is enabled
  - `debug_log_error(message, exception, context)` - Log error with details
  - `debug_log(message, context)` - Log debug messages (not errors)

- **Integrated in**:
  - TK UI: Exception handlers in `_execute_tick()` and `cmd_run()`
  - Future: Can be added to other UIs and error points

## Tips

### For Users

Only enable debug mode when reporting bugs or working with developers. Normal use doesn't need it.

### For Developers

When debugging with Claude Code:
1. Enable debug mode: `MBASIC_DEBUG=1`
2. Run the failing program
3. Share the stderr output with Claude
4. Claude gets full context to diagnose the issue

### Adding Debug Logging to New Code

When adding error handling:
```python
except Exception as e:
    # Instead of:
    # print(f"Error: {e}")

    # Use:
    error_msg = debug_log_error("Operation failed", e, {'key': 'value'})
    ui.display_error(error_msg)
```

## See Also

- Source: `src/debug_logger.py`
- Example usage: TK UI error handlers in `src/ui/tk_ui.py`
