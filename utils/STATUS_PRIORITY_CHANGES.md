# Status Column Priority System

## Feature

Implemented priority-based status display in the status column (column 0) of the curses editor. When a line has multiple states (error + breakpoint), the status character shows the highest priority state.

## Priority Order

1. **Error (`?`)** - Highest priority, always shown when syntax error exists
2. **Breakpoint (`●`)** - Shown when no error but breakpoint is set
3. **Normal (` `)** - Default when neither error nor breakpoint

## Behavior

### Before (without priority system)
- Setting status to '?' would overwrite breakpoint indicator
- Clearing error would always set status to ' ', losing breakpoint
- No way to see both error and breakpoint states

### After (with priority system)
- Error takes priority when both error and breakpoint exist
- When error is fixed, breakpoint indicator is automatically shown
- Both states are preserved independently

## Example Workflow

```
1. Set breakpoint on line 10:
   ●   10 PRINT "ok"

2. Introduce syntax error:
   ?   10 foo           (error has priority, shows '?')

3. Fix the error:
   ●   10 PRINT "ok"   (breakpoint shown again)
```

## Implementation

### New Method: `_get_status_char()`

```python
def _get_status_char(self, line_number, has_syntax_error):
    """Get the status character for a line based on priority.

    Priority order (highest to lowest):
    1. Syntax error (?) - highest priority
    2. Breakpoint (●) - medium priority
    3. Normal ( ) - default
    """
    if has_syntax_error:
        return '?'
    elif line_number in self.breakpoints:
        return '●'
    else:
        return ' '
```

### Modified Method: `_update_syntax_errors()`

Now uses `_get_status_char()` to determine the correct status instead of hardcoding '?' and ' ':

```python
# Determine correct status based on priority
new_status = self._get_status_char(line_number, has_syntax_error=not is_valid)

# Update status if it changed
if status != new_status:
    lines[i] = new_status + line[1:]
    changed = True
```

### Key Changes

1. **Empty lines preserve breakpoints:**
   - When code is cleared from a line with a breakpoint, the '●' remains
   - Previously would revert to ' '

2. **Error clearing reveals breakpoint:**
   - When syntax error is fixed on a line with breakpoint, status changes from '?' to '●'
   - Previously would change from '?' to ' ', losing breakpoint

3. **Independent state tracking:**
   - `self.breakpoints` set tracks breakpoints
   - `self.syntax_errors` dict tracks syntax errors
   - Status character computed from both using priority rules

## Testing

Created comprehensive tests in:
- `utils/test_status_priority.py` - 3 tests for priority system
- `utils/test_syntax_checking.py` - Updated with Test 6 for priority behavior

All tests verify:
- ✅ Priority order (error > breakpoint > normal)
- ✅ Breakpoint preserved when error is fixed
- ✅ Breakpoint preserved on empty lines
- ✅ Status changes correctly when states change

## Documentation Updates

Updated documentation to describe priority system:
- `/home/wohl/cl/mbasic/docs/user/URWID_UI.md` - Column Layout section
- `/home/wohl/cl/mbasic/src/ui/curses_ui.py` - Help dialog text

## Files Modified

- `/home/wohl/cl/mbasic/src/ui/curses_ui.py`
  - Added `_get_status_char()` method
  - Modified `_update_syntax_errors()` to use priority-based status
  - Updated help text to document priority system

## Benefits

1. **Better state visibility:** Users can set breakpoints without worrying about errors hiding them
2. **Non-destructive operations:** Fixing errors doesn't lose breakpoint information
3. **Clear priority:** Always know what state takes precedence
4. **Intuitive behavior:** Error is more urgent than breakpoint, so it shows first
