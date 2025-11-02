# Curses UI Mouse Support

## Overview
Add mouse support to the curses UI for better usability, especially in the help browser and editor.

## Current State
Mouse support is currently disabled in curses_ui.py:
```python
self.loop = urwid.MainLoop(
    main_widget,
    palette=self._get_palette(),
    unhandled_input=self._handle_input,
    handle_mouse=False  # Currently disabled
)
```

## Benefits
- **Help Browser**: Click links, scroll with mouse wheel
- **Editor**: Click to position cursor, select text
- **Menu Navigation**: Click menu items instead of keyboard-only
- **Window Management**: Resize panes, scroll output

## Implementation Tasks
1. Enable mouse in MainLoop: `handle_mouse=True`
2. Add mouse event handlers to widgets:
   - Help browser: click links, scroll
   - Editor: click to move cursor, mouse wheel to scroll
   - Menu bar: click to open menus
   - Output/Immediate windows: scroll with wheel
3. Test across different terminals (some may not support mouse)
4. Document mouse controls in help system

## Considerations
- Not all terminals support mouse (SSH, old terminals)
- Should still be fully keyboard-navigable
- May need terminal-specific handling
- Could affect copy/paste behavior in some terminals

## Status
Not started - future enhancement
