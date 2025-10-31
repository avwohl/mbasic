# Variable Window Sorting Refactoring

## Current Status

The web UI variables window has been improved with:
- ✅ Sortable columns
- ✅ Correct default sort (most recently accessed first)
- ✅ Filter search box

## Remaining Work

### 1. Implement Tk-Style Variable Column Header (Web UI)

The Tk UI has a sophisticated variable column header with TWO separate click zones:

**Current Tk behavior:**
- **Arrow click**: Toggle sort direction (↑/↓) for current sort mode
- **Label click**: Cycle through sort modes:
  1. `accessed` - Last accessed (read OR write) - **DEFAULT**
  2. `written` - Last write time
  3. `read` - Last read time
  4. `name` - Variable name alphabetically

The header displays as: `↓ Variable (Last Accessed)`

**Web UI needs:**
- Similar two-zone header for Name column
- Click arrow to toggle direction
- Click label to cycle through modes
- Display current mode in header text

### 2. Create Common Variable Sorting Helper

Currently each UI (Tk, Curses, Web) has its own variable sorting code with identical logic. This should be refactored into a common helper.

**Create**: `src/ui/variable_sorting.py`

**Functions needed:**

```python
def get_variable_sort_modes():
    """Return list of available sort modes.

    Returns:
        list: Sort mode definitions with keys:
            - 'key': internal name ('accessed', 'written', 'read', 'name', 'type', 'value')
            - 'label': display name for UI
            - 'key_func': function that takes variable dict and returns sortable key
    """

def get_sort_key(variables, sort_mode, reverse=False):
    """Get sorted variables list.

    Args:
        variables: List of variable dicts from runtime.get_all_variables()
        sort_mode: One of 'accessed', 'written', 'read', 'name', 'type', 'value'
        reverse: If True, sort descending (newest first for timestamps)

    Returns:
        list: Sorted variable list
    """

def cycle_sort_mode(current_mode):
    """Get next sort mode in cycle.

    Args:
        current_mode: Current sort mode key

    Returns:
        str: Next mode key in cycle
    """
```

**Sort key implementations:**
- `accessed`: `max(last_read.timestamp, last_write.timestamp)`
- `written`: `last_write.timestamp`
- `read`: `last_read.timestamp`
- `name`: `name.lower()` (alphabetical)
- `type`: `type_suffix` (group by $, %, !, #)
- `value`: complex (arrays last, then numeric/string sorting)

**Refactor UIs:**
1. Update `src/ui/tk_ui.py` to use helper
2. Update `src/ui/curses_ui.py` to use helper
3. Update `src/ui/web/nicegui_backend.py` to use helper

This ensures all UIs have identical, well-tested sorting behavior.

## Benefits

1. **Consistency**: All UIs sort variables exactly the same way
2. **Maintainability**: Fix sorting bugs in one place
3. **Testing**: Can unit test sorting logic independently
4. **Features**: Easy to add new sort modes (e.g., "by line number where defined")

## Implementation Priority

Given the complexity, this is marked as future work. The web UI currently has:
- ✅ Working sortable columns
- ✅ Correct default sort
- ✅ Search/filter

The advanced Tk-style header and common refactoring can be done in a future session.
