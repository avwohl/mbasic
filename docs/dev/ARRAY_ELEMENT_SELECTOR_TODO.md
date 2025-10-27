# Array Element Selector Enhancement

## Date: 2025-10-27
## Status: ⏳ TODO

## Overview

Currently, variable editing supports arrays but only allows editing the **last accessed element**. Users want the ability to edit **any array element** by typing in arbitrary subscripts.

## Current Behavior

When editing an array in the Variables window:
- Shows array with last accessed element: `A%(10x10) [5,3]=42`
- Double-click/Enter opens dialog to edit that specific element only
- **Limitation**: Cannot choose which element to edit

## Requested Feature

### User Interface

Add an input field where users can type subscripts to select which array element to edit:

**Example Dialog:**
```
┌─────────────────────────────────────────┐
│ Edit Array Element: A%(10x10)           │
├─────────────────────────────────────────┤
│ Subscripts: [1,2,3_______________]      │ ← User types indices
│                                          │
│ Current value: 0                         │
│ New value: [42___________________]      │
│                                          │
│         [OK]  [Cancel]                   │
└─────────────────────────────────────────┘
```

### User Flow

1. User double-clicks array in Variables window
2. Dialog opens with two fields:
   - **Subscripts field**: For entering indices (e.g., "1,2,3")
   - **Value field**: For entering new value
3. User types subscripts: `1,2,3`
4. System validates subscripts (in bounds, correct count)
5. System shows current value at those subscripts
6. User enters new value
7. System updates array element

### Input Format

**Single dimension:**
- `5` → A%(5)

**Two dimensions:**
- `1,2` → A%(1,2)

**Three dimensions:**
- `1,2,3` → A%(1,2,3)

**Whitespace handling:**
- `1, 2, 3` (with spaces) → Same as `1,2,3`
- Trim whitespace before/after each number

## Implementation Details

### Tk UI

```python
def _edit_array_variable(self, array_name, array_dimensions, array_type):
    """Edit array element with subscript selector.

    Args:
        array_name: Array variable name (e.g., "A%")
        array_dimensions: List of dimension sizes [10, 10]
        array_type: Type suffix ('%', '$', '!', '#')
    """
    # Create dialog
    dialog = tk.Toplevel(self.root)
    dialog.title(f"Edit Array Element: {array_name}")
    dialog.geometry("400x200")

    # Subscripts label and entry
    tk.Label(dialog, text="Subscripts (e.g., 1,2,3):").grid(row=0, column=0, sticky='w', padx=10, pady=5)
    subscripts_entry = tk.Entry(dialog, width=40)
    subscripts_entry.grid(row=0, column=1, padx=10, pady=5)

    # Current value label (updates when subscripts change)
    current_value_label = tk.Label(dialog, text="Current value: <enter subscripts>")
    current_value_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

    # New value label and entry
    tk.Label(dialog, text="New value:").grid(row=2, column=0, sticky='w', padx=10, pady=5)
    value_entry = tk.Entry(dialog, width=40)
    value_entry.grid(row=2, column=1, padx=10, pady=5)

    # Error label (for validation messages)
    error_label = tk.Label(dialog, text="", fg="red")
    error_label.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

    def update_current_value(*args):
        """Update current value display when subscripts change."""
        subscripts_str = subscripts_entry.get().strip()
        if not subscripts_str:
            current_value_label.config(text="Current value: <enter subscripts>")
            error_label.config(text="")
            return

        try:
            # Parse subscripts
            subscripts = [int(s.strip()) for s in subscripts_str.split(',')]

            # Validate dimension count
            if len(subscripts) != len(array_dimensions):
                error_label.config(text=f"Expected {len(array_dimensions)} subscripts, got {len(subscripts)}")
                return

            # Validate bounds
            for i, (sub, dim) in enumerate(zip(subscripts, array_dimensions)):
                if sub < 0 or sub > dim:
                    error_label.config(text=f"Subscript {i} out of bounds: {sub} not in [0, {dim}]")
                    return

            # Get current value
            current_value = self._get_array_element_value(array_name, subscripts)
            current_value_label.config(text=f"Current value: {current_value}")
            error_label.config(text="")

        except ValueError:
            error_label.config(text="Invalid subscripts (must be integers)")
        except Exception as e:
            error_label.config(text=f"Error: {str(e)}")

    # Update current value when subscripts entry changes
    subscripts_entry.bind('<KeyRelease>', update_current_value)

    def on_ok():
        """Apply changes and close dialog."""
        subscripts_str = subscripts_entry.get().strip()
        new_value_str = value_entry.get().strip()

        if not subscripts_str or not new_value_str:
            error_label.config(text="Both fields are required")
            return

        try:
            # Parse subscripts
            subscripts = [int(s.strip()) for s in subscripts_str.split(',')]

            # Parse and validate new value based on type
            if array_type == '%':
                new_value = int(new_value_str)
            elif array_type == '$':
                new_value = new_value_str  # String
            else:
                new_value = float(new_value_str)

            # Update array element
            self._update_array_element(array_name, subscripts, new_value)

            # Refresh variables window
            self._update_variables_window()

            # Close dialog
            dialog.destroy()

        except ValueError as e:
            error_label.config(text=f"Invalid value: {str(e)}")
        except Exception as e:
            error_label.config(text=f"Error: {str(e)}")

    # OK and Cancel buttons
    button_frame = tk.Frame(dialog)
    button_frame.grid(row=4, column=0, columnspan=2, pady=10)

    tk.Button(button_frame, text="OK", command=on_ok, width=10).pack(side='left', padx=5)
    tk.Button(button_frame, text="Cancel", command=dialog.destroy, width=10).pack(side='left', padx=5)

    # Focus on subscripts entry
    subscripts_entry.focus()
```

### Helper Methods

```python
def _get_array_element_value(self, array_name, subscripts):
    """Get current value of array element.

    Args:
        array_name: Array variable name (e.g., "A%")
        subscripts: List of subscripts [1, 2, 3]

    Returns:
        Current value at those subscripts
    """
    if not self.interpreter or not self.interpreter.runtime:
        return None

    runtime = self.interpreter.runtime

    # Get array from variables
    if array_name not in runtime.variables:
        raise KeyError(f"Array {array_name} not found")

    array = runtime.variables[array_name]

    # Calculate linear index
    index = 0
    multiplier = 1
    for i in reversed(range(len(subscripts))):
        index += subscripts[i] * multiplier
        multiplier *= (array.dimensions[i] + 1)

    return array.elements[index]
```

### Curses UI

```python
def _edit_array_variable(self, array_name, array_dimensions, array_type):
    """Edit array element with subscript selector (Curses version).

    Uses status bar for inline input:
    1. Prompt for subscripts: "Enter subscripts (e.g., 1,2,3): "
    2. Show current value: "A%(1,2,3) = 42"
    3. Prompt for new value: "Enter new value: "
    """
    # Step 1: Get subscripts
    self.status_bar.set_text(f"Edit {array_name} - Enter subscripts (e.g., 1,2,3): ")
    # (Need to implement input mode for status bar)

    # Step 2: Show current value
    current_value = self._get_array_element_value(array_name, subscripts)
    self.status_bar.set_text(f"{array_name}({','.join(map(str, subscripts))}) = {current_value}")

    # Step 3: Get new value
    self.status_bar.set_text(f"Enter new value: ")
    # (Get input and update)
```

### Web UI

```javascript
// In web UI, use modal dialog with two input fields
function editArrayElement(arrayName, arrayDimensions, arrayType) {
    const dialog = document.createElement('div');
    dialog.className = 'modal';
    dialog.innerHTML = `
        <div class="modal-content">
            <h3>Edit Array Element: ${arrayName}</h3>

            <label>Subscripts (e.g., 1,2,3):</label>
            <input type="text" id="subscripts-input" placeholder="1,2,3" />

            <p id="current-value">Current value: <em>enter subscripts</em></p>
            <p id="error-message" style="color: red;"></p>

            <label>New value:</label>
            <input type="text" id="value-input" />

            <button onclick="applyArrayEdit()">OK</button>
            <button onclick="closeDialog()">Cancel</button>
        </div>
    `;

    document.body.appendChild(dialog);

    // Update current value when subscripts change
    document.getElementById('subscripts-input').addEventListener('input', updateCurrentValue);
}
```

## Validation Requirements

### Subscript Parsing
- **Split by comma**: `"1,2,3".split(',')` → `['1', '2', '3']`
- **Trim whitespace**: Each element trimmed
- **Convert to int**: `int(s)` for each subscript
- **Error handling**: Catch `ValueError` for non-numeric input

### Bounds Checking
- **Dimension count**: Must match array dimensions
- **Range**: Each subscript must be in `[0, dimension_size]`
- **Error messages**:
  - "Expected 2 subscripts, got 3"
  - "Subscript 1 out of bounds: 15 not in [0, 10]"

### Value Validation
- **Type matching**: Value must match array type
- **Integer arrays**: `int(value)`
- **String arrays**: Any string (max 255 chars)
- **Float arrays**: `float(value)`

## Error Messages

User-friendly error messages:

| Error | Message |
|-------|---------|
| Empty subscripts | "Please enter subscripts (e.g., 1,2,3)" |
| Non-numeric subscript | "Subscripts must be numbers separated by commas" |
| Wrong dimension count | "Expected N subscripts, got M" |
| Out of bounds | "Subscript N out of bounds: X not in [0, Y]" |
| Invalid value | "Invalid value for integer/string/float array" |
| Array not found | "Array not found (program not running?)" |

## User Experience

### Default Values
- **Subscripts field**: Empty (or pre-fill with last accessed subscripts?)
- **Value field**: Empty (fills after subscripts entered)

### Tab Order
1. Subscripts field (focused on open)
2. Value field
3. OK button
4. Cancel button

### Keyboard Shortcuts
- **Enter** in subscripts field: Move to value field
- **Enter** in value field: Apply changes (same as OK)
- **Escape**: Cancel dialog

## Testing

### Test Cases

1. **Single dimension array**
   - `DIM A%(10)`
   - Edit subscript `5` → Value `100`
   - Verify: `A%(5) = 100`

2. **Two dimension array**
   - `DIM B%(5, 5)`
   - Edit subscripts `2,3` → Value `200`
   - Verify: `B%(2,3) = 200`

3. **Three dimension array**
   - `DIM C%(3, 3, 3)`
   - Edit subscripts `1,2,3` → Value `300`
   - Verify: `C%(1,2,3) = 300`

4. **Input validation**
   - Enter `abc` → Error: "must be numbers"
   - Enter `1,2` for 3D array → Error: "Expected 3 subscripts"
   - Enter `15` for `DIM A%(10)` → Error: "out of bounds"

5. **String arrays**
   - `DIM S$(5, 5)`
   - Edit subscripts `1,1` → Value `"Hello"`
   - Verify: `S$(1,1) = "Hello"`

6. **Whitespace handling**
   - Enter ` 1 , 2 , 3 ` → Same as `1,2,3`

## Priority

**Priority:** MEDIUM

**Reason:**
- Current workaround: Use immediate mode to set values (e.g., `A%(1,2,3) = 100`)
- Enhancement improves UX but not critical for functionality
- Most useful for debugging arrays during program execution

## Dependencies

**Required:**
- Existing variable editing feature (already implemented)
- Runtime array access methods (already implemented)

**Optional:**
- Array inspector window (future enhancement for visual grid editing)

## References

- Variable editing feature: `docs/dev/VARIABLE_EDITING_FEATURE.md`
- Tk UI variables window: `src/ui/tk_ui.py:696-786`
- Curses UI variables window: `src/ui/curses_ui.py:2036-2088`
- Web UI variables window: `src/ui/web/web_ui.py:571-805`
- Runtime array access: `src/runtime.py`

## Future Enhancements

Once this is implemented, consider:

1. **Array Inspector Window** (Approach 2 from original design)
   - Full grid view of entire array
   - Click any cell to edit
   - Navigate with arrow keys

2. **Subscript History**
   - Remember last N subscripts used
   - Dropdown to quickly re-access

3. **Range Editing**
   - Edit multiple elements at once: `A%(1:5) = 0`

4. **Array Visualization**
   - Show array as table/grid in separate window
   - Color-code by value
   - Export to CSV
