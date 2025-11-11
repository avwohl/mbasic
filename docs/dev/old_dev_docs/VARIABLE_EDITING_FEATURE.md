# Variable Editing Feature

## Overview

Add ability to edit variable values directly in the variables watch window, including simple variables and array elements.

## Current State

**All UIs** (Tk, Curses, Web):
- Variables window shows variables and their current values
- Values are **read-only** - cannot be edited
- To change a variable, must use immediate mode or edit program

## Proposed Feature

### Simple Variables

**Double-click or press Enter on variable** → Opens edit dialog

**Example**:
```
Variable: A%
Current value: 100
New value: [____] <- User edits here
```

**Apply**: Updates variable in runtime
**Cancel**: Closes dialog without changes

### String Variables

**Edit dialog for strings**:
```
Variable: NAME$
Current value: "Alice"
New value: [____________________] <- User edits here (no quotes needed)
```

**Handling**:
- User types without quotes: `Bob`
- System stores as: `"Bob"`

### Array Variables

**Two approaches**:

#### Approach 1: Edit Single Element (Simpler)

When user clicks array in variables list, show last accessed element for editing.

**Example**:
```
Variable: A%(10x10) [5,3]=42
Double-click → Edit dialog:
  A%(5,3) = [____] <- Edit value
```

#### Approach 2: Array Inspector Window (More Advanced)

Show full array in grid/table view:

```
┌─────────────────────────────────┐
│ Array: A%(10x10)                │
├─────────────────────────────────┤
│     0    1    2    3    4    5  │
│ 0 │ 0  │ 0  │ 0  │ 0  │ 0  │ 0 │
│ 1 │ 0  │10 │ 0  │ 0  │ 0  │ 0 │
│ 2 │ 0  │ 0  │ 0  │ 0  │ 0  │ 0 │
│ 3 │ 0  │ 0  │ 0  │42 │ 0  │ 0 │
│...│    │    │    │    │    │   │
└─────────────────────────────────┘
```

Double-click cell → Edit value

**Recommendation**: Start with Approach 1, add Approach 2 as future enhancement.

## Implementation

### Data Flow

```
User double-clicks variable
    ↓
UI shows edit dialog
    ↓
User enters new value
    ↓
Validate value (type checking)
    ↓
Update runtime variable
    ↓
Refresh variables window
```

### UI Integration

#### Tk UI

**Variables window**: Treeview widget
- Bind `<Double-Button-1>` to open edit dialog
- Use `simpledialog.askstring()` or `simpledialog.askinteger()` based on type

**Code**:
```python
def _on_variable_double_click(self, event):
    """Handle double-click on variable."""
    selection = self.variables_tree.selection()
    if not selection:
        return

    item_id = selection[0]
    item_data = self.variables_tree.item(item_id)

    # Extract variable info
    variable_name = item_data['values'][0]  # Variable column
    variable_type = item_data['values'][1]  # Type column
    current_value = item_data['values'][2]  # Value column

    # Open edit dialog based on type
    if variable_type == '%':  # Integer
        new_value = simpledialog.askinteger(
            "Edit Variable",
            f"Enter new value for {variable_name}:",
            initialvalue=int(current_value),
            parent=self.root
        )
    elif variable_type == '$':  # String
        new_value = simpledialog.askstring(
            "Edit Variable",
            f"Enter new value for {variable_name}:",
            initialvalue=current_value.strip('"'),
            parent=self.root
        )
    else:  # Single or Double
        new_value = simpledialog.askfloat(
            "Edit Variable",
            f"Enter new value for {variable_name}:",
            initialvalue=float(current_value),
            parent=self.root
        )

    if new_value is not None:
        # Update runtime variable
        self._update_runtime_variable(variable_name, new_value)

        # Refresh display
        self._update_variables_window()
```

**Update runtime**:
```python
def _update_runtime_variable(self, variable_name, new_value):
    """Update variable in runtime.

    Args:
        variable_name: Name with type suffix (e.g., "A%", "NAME$")
        new_value: New value to assign
    """
    if not self.interpreter or not self.interpreter.runtime:
        return

    runtime = self.interpreter.runtime

    # Parse variable name (remove type suffix)
    if variable_name[-1] in '%$!#':
        base_name = variable_name[:-1]
        type_suffix = variable_name[-1]
    else:
        base_name = variable_name
        type_suffix = ''

    # Update based on type
    if type_suffix == '$':
        # String variable
        runtime.set_variable(base_name, new_value, is_string=True)
    elif type_suffix == '%':
        # Integer variable
        runtime.set_variable(base_name, int(new_value), is_string=False)
    else:
        # Floating point
        runtime.set_variable(base_name, float(new_value), is_string=False)
```

#### Curses UI

**Variables window**: ListBox widget
- Bind Enter key or 'e' key to open edit prompt
- Use inline prompt in status bar or modal dialog

**Code**:
```python
def _handle_input(self, key):
    # ... existing key handlers ...

    if key == 'enter' or key == 'e':
        if self.watch_window_visible:
            self._edit_selected_variable()
            return

def _edit_selected_variable(self):
    """Edit currently selected variable in watch window."""
    # Get selected variable from variables_walker focus
    focus_idx = self.variables_walker.get_focus()[1]
    if focus_idx is None or focus_idx >= len(self.variables_walker):
        return

    # Get variable info (this requires tracking variable data)
    # For now, parse from display text
    widget = self.variables_walker[focus_idx]
    text = widget.get_text()[0]  # Get text content

    # Parse: "NAME$        = "Alice""
    # Extract variable name and current value
    parts = text.split('=')
    if len(parts) != 2:
        return

    variable_name = parts[0].strip()
    current_value = parts[1].strip()

    # Show inline edit prompt
    self.status_bar.set_text(f"Edit {variable_name} (current: {current_value}): ")

    # Get user input (this requires implementing input dialog for curses)
    # Simplified: use status bar for now
    # (Full implementation needs modal input dialog)
```

#### Web UI

Similar to Tk, but using HTML/JavaScript:
- Use `prompt()` or custom modal dialog
- Send update request to backend via WebSocket

### Array Element Editing

**Approach 1 Implementation** (edit last accessed cell):

```python
def _on_variable_double_click(self, event):
    # ... existing code ...

    # Check if array
    if 'Array' in current_value:
        # Parse: "Array(10x10) [5,3]=42"
        match = re.match(r'Array\([^)]+\)\s*\[([^\]]+)\]=(.+)', current_value)
        if match:
            subscripts_str = match.group(1)  # "5,3"
            value_str = match.group(2)       # "42"

            # Parse subscripts
            subscripts = [int(s.strip()) for s in subscripts_str.split(',')]

            # Edit value
            if variable_type == '%':
                new_value = simpledialog.askinteger(
                    "Edit Array Element",
                    f"Enter new value for {variable_name}({subscripts_str}):",
                    initialvalue=int(value_str),
                    parent=self.root
                )
            # ... similar for other types ...

            if new_value is not None:
                # Update array element
                self._update_array_element(variable_name, subscripts, new_value)
```

**Update array element**:
```python
def _update_array_element(self, array_name, subscripts, new_value):
    """Update array element in runtime.

    Args:
        array_name: Array variable name (e.g., "A%")
        subscripts: List of subscripts [5, 3]
        new_value: New value to assign
    """
    if not self.interpreter or not self.interpreter.runtime:
        return

    runtime = self.interpreter.runtime

    # Get array from runtime
    base_name = array_name[:-1] if array_name[-1] in '%$!#' else array_name

    # Access array storage
    # This depends on how arrays are stored in runtime
    # Assuming runtime has get_array() and set_array_element() methods
    try:
        runtime.set_array_element(base_name, subscripts, new_value)
    except KeyError:
        # Array doesn't exist
        self.status_bar.set_text(f"Array {array_name} not found")
    except IndexError:
        # Subscripts out of bounds
        self.status_bar.set_text(f"Subscripts {subscripts} out of bounds")
```

## Runtime Support

Need to add methods to Runtime class:

```python
# In src/runtime.py

def set_variable(self, name, value, is_string=False):
    """Set simple variable value.

    Args:
        name: Variable name (without type suffix)
        value: New value
        is_string: True if string variable
    """
    # Determine full variable name with type suffix
    if is_string:
        full_name = name + '$'
    elif isinstance(value, int):
        full_name = name + '%'
    else:
        full_name = name  # Default: single precision

    # Update variable storage
    self.variables[full_name] = value

    # Update timestamps for tracking
    import time
    timestamp = time.time()

    if full_name not in self.variable_accessed:
        self.variable_accessed[full_name] = {}

    self.variable_accessed[full_name]['last_write'] = {
        'timestamp': timestamp,
        'statement': None  # No statement (manual edit)
    }

def set_array_element(self, name, subscripts, value):
    """Set array element value.

    Args:
        name: Array name (without type suffix)
        subscripts: List of subscripts [5, 3]
        value: New value
    """
    # Find array in variables
    array_name = name + '%'  # Try integer array first
    if array_name not in self.variables:
        array_name = name + '$'  # Try string array
        if array_name not in self.variables:
            array_name = name  # Try default (single precision)
            if array_name not in self.variables:
                raise KeyError(f"Array {name} not found")

    array = self.variables[array_name]

    # Validate subscripts
    if len(subscripts) != len(array.dimensions):
        raise IndexError(f"Wrong number of subscripts: expected {len(array.dimensions)}, got {len(subscripts)}")

    # Calculate linear index
    index = 0
    multiplier = 1
    for i in reversed(range(len(subscripts))):
        if subscripts[i] < 0 or subscripts[i] > array.dimensions[i]:
            raise IndexError(f"Subscript {i} out of bounds: {subscripts[i]} not in [0, {array.dimensions[i]}]")
        index += subscripts[i] * multiplier
        multiplier *= (array.dimensions[i] + 1)

    # Update array element
    array.elements[index] = value

    # Update last accessed tracking
    import time
    timestamp = time.time()

    if array_name not in self.variable_accessed:
        self.variable_accessed[array_name] = {}

    self.variable_accessed[array_name]['last_accessed_subscripts'] = subscripts
    self.variable_accessed[array_name]['last_accessed_value'] = value
    self.variable_accessed[array_name]['last_write'] = {
        'timestamp': timestamp,
        'statement': None
    }
```

## UI Considerations

### Validation

- **Type checking**: Ensure value matches variable type
- **Range checking**: For integers, ensure within valid range
- **String length**: BASIC strings have max length (255)
- **Array bounds**: Ensure subscripts are valid

### Error Handling

Show user-friendly error messages:
- "Invalid value for integer variable"
- "String too long (max 255 characters)"
- "Array subscripts out of bounds"

### Feedback

After successful edit:
- Update variables window immediately
- Show brief status message: "A% updated to 150"
- Highlight changed variable briefly (optional)

## Testing

### Manual Tests

1. **Simple integer variable**
   - Create variable: `A% = 100`
   - Double-click in variables window
   - Change to: `200`
   - Verify: Variable shows `200` and program uses new value

2. **String variable**
   - Create variable: `NAME$ = "Alice"`
   - Edit to: `Bob` (without quotes)
   - Verify: Variable shows `"Bob"`

3. **Array element**
   - Create array: `DIM A%(10, 10)`
   - Access element: `A%(5, 3) = 42`
   - Edit: Change to `99`
   - Verify: `A%(5, 3)` now shows `99`

4. **Invalid input**
   - Try to set integer variable to `"abc"`
   - Verify: Error message shown, value unchanged

5. **Array bounds**
   - Array: `DIM B(5)`
   - Try to edit `B(10)` (out of bounds)
   - Verify: Error message shown

## Future Enhancements

### Array Inspector Window (Phase 2)

Full array viewer/editor:
- Show all array elements in grid
- Click any cell to edit
- Navigate with arrow keys
- Search for value
- Export array to CSV

### Bulk Edit

- Select multiple variables
- Apply formula to all: `+10`, `*2`, etc.

### Watch Expressions

- Add computed expressions to watch list
- Example: `A% + B%`, `LEN(NAME$)`

### Conditional Formatting

- Highlight variables that changed recently
- Color-code by value range (red for negative, green for positive)

## Implementation Status

- ✅ Design document created (commit b6a2fae)
- ✅ Runtime methods (set_variable, set_array_element) - Already existed!
- ✅ Tk UI: Double-click handler (commit 301c02f)
- ✅ Tk UI: Edit dialog for simple variables (commit 301c02f)
- ✅ Tk UI: Edit dialog for array elements (commit 301c02f)
- ✅ Curses UI: Key binding (Enter/'e') (commit fcedd97)
- ✅ Curses UI: Edit prompt (commit fcedd97)
- ✅ Web UI: Table selection and "Edit Selected" button
- ✅ Web UI: Double-click on row to edit
- ✅ Web UI: Edit dialog with type-based inputs
- ✅ Web UI: Simple variable editing
- ✅ Web UI: Array element editing
- ⬜ Testing: Manual testing with real programs
- ✅ Documentation: Quick reference updated

**Status**: All UIs complete! (Tk, Curses, and Web)

## References

- Variables window: `src/ui/tk_ui.py:696-786` (Tk)
- Variables window: `src/ui/curses_ui.py:2036-2088` (Curses)
- Variables window: `src/ui/web/web_ui.py:571-805` (Web)
- Runtime: `src/runtime.py`
