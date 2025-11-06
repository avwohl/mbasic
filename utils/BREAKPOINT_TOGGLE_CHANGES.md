# Breakpoint Toggle Feature

## Feature

Added `Ctrl+B` keyboard shortcut to toggle breakpoints on the current line in the curses UI editor.

## Usage

1. Position cursor on any line in the editor
2. Press `Ctrl+B` to toggle breakpoint
3. Status bar shows confirmation: "Breakpoint set on line X" or "Breakpoint removed from line X"
4. Status column updates to show `●` (or `?` if line also has error)

## Behavior

### Toggle Operation
- First press on a line: Sets breakpoint, shows `●` in status column
- Second press on same line: Removes breakpoint, shows ` ` (or `?` if error exists)
- Works on any line with a valid line number

### Priority System Integration
- When line has only breakpoint: Shows `●`
- When line has only error: Shows `?`
- When line has both breakpoint and error: Shows `?` (error priority)
- After fixing error: Automatically shows `●` (breakpoint revealed)

### Status Bar Feedback
- Setting breakpoint: "Breakpoint set on line 10"
- Removing breakpoint: "Breakpoint removed from line 10"
- Provides immediate visual feedback to user

## Implementation

### New Method: `_toggle_breakpoint_current_line()`

Located in `CursesBackend` class in `src/ui/curses_ui.py`:

```python
def _toggle_breakpoint_current_line(self):
    """Toggle breakpoint on the current line where the cursor is."""
    # Get current cursor position
    cursor_pos = self.editor.edit_widget.edit_pos
    current_text = self.editor.edit_widget.get_edit_text()

    # Find which line we're on (by counting newlines before cursor)
    text_before_cursor = current_text[:cursor_pos]
    line_index = text_before_cursor.count('\n')

    # Extract line number (variable width after status char)
    lines = current_text.split('\n')
    line = lines[line_index]
    # Use _parse_line_number to extract variable-width line number
    line_number, _ = self._parse_line_number(line)

    # Toggle breakpoint in set
    if line_number in self.editor.breakpoints:
        self.editor.breakpoints.remove(line_number)
        self.status_bar.set_text(f"Breakpoint removed from line {line_number}")
    else:
        self.editor.breakpoints.add(line_number)
        self.status_bar.set_text(f"Breakpoint set on line {line_number}")

    # Update display using priority system
    has_syntax_error = line_number in self.editor.syntax_errors
    new_status = self.editor._get_status_char(line_number, has_syntax_error)

    # Update line's status column
    lines[line_index] = new_status + line[1:]
    self.editor.edit_widget.set_edit_text('\n'.join(lines))
    self.editor.edit_widget.set_edit_pos(cursor_pos)
```

### Key Handler

Added to `_handle_input()` method:

```python
elif key == 'ctrl b':
    # Toggle breakpoint on current line
    self._toggle_breakpoint_current_line()
```

## Example Workflows

### Basic Toggle
```
1. Cursor on line 10:
       10 PRINT "hello"

2. Press Ctrl+B:
   ●   10 PRINT "hello"
   Status: "Breakpoint set on line 10"

3. Press Ctrl+B again:
       10 PRINT "hello"
   Status: "Breakpoint removed from line 10"
```

### With Syntax Error
```
1. Line with error and breakpoint set:
   ?   10 foo
   (error has priority, breakpoint hidden)

2. Fix the error:
   ●   10 PRINT "hello"
   (breakpoint automatically shown)

3. Press Ctrl+B to remove:
       10 PRINT "hello"
   Status: "Breakpoint removed from line 10"
```

### Multiple Breakpoints
```
Set breakpoints on multiple lines:
●   10 PRINT "start"
    20 FOR I = 1 TO 10
●   30 PRINT I
    40 NEXT I
●   50 END
```

## Testing

Created `utils/test_breakpoint_toggle.py` with comprehensive tests:

1. ✅ Toggle breakpoint on/off
   - Initially no breakpoint (` `)
   - After adding (` ●`)
   - After removing (` `)

2. ✅ Breakpoint with syntax error (priority)
   - No error: Shows `●`
   - With error: Shows `?` (error priority)
   - Error fixed: Shows `●` (breakpoint revealed)

3. ✅ Multiple breakpoints
   - Can set on multiple lines
   - Each line tracks independently
   - Removing one doesn't affect others

All tests pass successfully.

## Documentation Updates

### Files Updated

1. **README.md**
   - Added `Ctrl+B` to Features list

2. **docs/user/URWID_UI.md**
   - Added `Ctrl+B` to Keyboard Shortcuts table
   - Updated "Working with Breakpoints" section with usage instructions
   - Updated Roadmap: marked breakpoint support as completed

3. **src/ui/curses_ui.py**
   - Added `Ctrl+B` to help dialog text

## Integration with Priority System

The breakpoint toggle feature works seamlessly with the status priority system:

- `self.editor.breakpoints` set tracks which lines have breakpoints
- `self.editor.syntax_errors` dict tracks which lines have errors
- `_get_status_char()` computes status by priority: error > breakpoint > normal
- Status updates automatically when either state changes

## Future Enhancements

Breakpoint infrastructure is now in place for future debugger features:
- Step/Continue/End commands
- Pause execution at breakpoints
- Watch window showing variables at breakpoint
- Call stack viewer
- Conditional breakpoints

## Benefits

1. **Easy to use**: Single key (Ctrl+B) to toggle
2. **Visual feedback**: Immediate status column update
3. **Non-destructive**: Works with priority system (errors don't hide breakpoints)
4. **Persistent**: Breakpoints remain set across edits
5. **Foundation for debugging**: Infrastructure ready for step/continue features
