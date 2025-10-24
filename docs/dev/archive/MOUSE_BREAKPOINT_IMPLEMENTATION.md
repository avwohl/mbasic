# Mouse Click Breakpoint Implementation

## Overview

Added mouse support to the MBASIC curses IDE, allowing users to toggle breakpoints by clicking on the breakpoint indicator (● or space) at the start of each line.

## Implementation Details

### Changes Made

#### 1. Enable Mouse Events (`src/ui/curses_ui.py`)

In `MBASICForm.create()`, added mouse event initialization:

```python
# Enable mouse events
try:
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
except:
    pass  # Mouse not supported in this terminal
```

#### 2. Mouse Event Handler

Added `h_mouse()` method to `MBASICForm`:

```python
def h_mouse(self, *args, **kwargs):
    """Handler for mouse events."""
    try:
        mouse_id, mouse_x, mouse_y, mouse_z, bstate = curses.getmouse()

        # Check for left click events
        if bstate & (curses.BUTTON1_CLICKED | curses.BUTTON1_PRESSED | curses.BUTTON1_RELEASED):
            # Get editor widget position
            editor_top = self.editor.rely
            editor_left = self.editor.relx
            editor_height = self.editor.height

            # Check if click is in editor area
            if editor_top <= mouse_y < editor_top + editor_height:
                line_in_editor = mouse_y - editor_top

                # Check if click is on breakpoint column (first character)
                if editor_left <= mouse_x <= editor_left + 1:
                    # Calculate actual line considering scrolling
                    scroll_offset = getattr(self.editor, 'start_display_at', 0)
                    actual_line = line_in_editor + scroll_offset

                    # Move cursor to that line and toggle breakpoint
                    editor_text = self.editor.value
                    lines = editor_text.split('\n')

                    if 0 <= actual_line < len(lines):
                        cursor_pos = sum(len(line) + 1 for line in lines[:actual_line])
                        self.editor.cursor_position = cursor_pos
                        self.on_toggle_breakpoint()
                        self.editor.display()
```

#### 3. Register Mouse Handler

Added mouse handler to both form-level and editor-level handlers:

**Form level:**
```python
def set_up_handlers(self):
    super().set_up_handlers()
    self.handlers.update({
        # ... other handlers ...
        curses.KEY_MOUSE: self.h_mouse,  # Mouse click (form level)
    })
```

**Editor level:**
```python
self.editor.handlers.update({
    # ... other handlers ...
    curses.KEY_MOUSE: lambda x: self.h_mouse(),  # Mouse click
})
```

### How It Works

1. **Mouse Events**: When mouse support is available, curses generates `KEY_MOUSE` events
2. **Event Detection**: The handler catches these events and calls `curses.getmouse()` to get coordinates
3. **Position Calculation**:
   - Calculates which line was clicked relative to editor widget position
   - Adjusts for scrolling using `start_display_at` offset
   - Checks if click is in the breakpoint column (x position 0-1)
4. **Breakpoint Toggle**:
   - Moves cursor to the clicked line
   - Calls existing `on_toggle_breakpoint()` method
   - Forces display refresh

### Visual Layout

Editor text format:
```
●10 PRINT "Line with breakpoint"
 20 PRINT "Line without breakpoint"
```

- Column 0: ● or space (breakpoint indicator)
- Column 1+: line number and code

Click target: Columns 0-1 (the ● or space character)

## Testing

### Manual Testing

Run the manual test script:
```bash
./test_mouse_click.sh
```

Then:
1. Click on the space before any line number
2. A ● should appear/disappear (breakpoint toggled)
3. Set breakpoints on multiple lines
4. Run the program (Ctrl+R) to verify breakpoints work
5. Quit (Ctrl+Q)

### Debug Tool

For testing mouse event handling:
```bash
./test_mouse_debug.py
```

This shows:
- Mouse coordinates for each click
- Button state information
- Whether click was on breakpoint column

## Documentation Updates

- Updated `docs/help/shortcuts.md` to document mouse click feature
- Updated `BREAKPOINTS.md` to list mouse clicking as a breakpoint toggle method

## Compatibility Notes

- Mouse support requires terminal with mouse capability (most modern terminals)
- Falls back gracefully if mouse not supported
- Works with xterm, gnome-terminal, iTerm2, Windows Terminal, etc.
- May not work in basic terminal emulators or over SSH without proper forwarding

## Future Enhancements

Possible improvements:
- Double-click to set breakpoint and run to that line
- Right-click context menu for breakpoint operations
- Visual hover effect when mouse is over breakpoint column
- Drag-and-drop to move breakpoints between lines
