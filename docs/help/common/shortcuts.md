# Keyboard Shortcuts

**Note:** This page shows shortcuts common across UIs using **^X** notation (meaning Ctrl+X). For UI-specific details, see:
- [Curses UI Shortcuts](ui/curses/editing.md) - Keyboard-focused shortcuts
- [Tk UI Shortcuts](ui/tk/index.md) - Keyboard + mouse shortcuts
- Web UI - Click-based interface (toolbar buttons and menus)

## Common Shortcuts (All UIs)

### Execution
- **^R** - Run program
- **^T** - Step statement (execute one statement)
- **^K** - Step line (Tk/Web only - execute one line)
- **^G** - Continue (run to next breakpoint)
- **^Q** - Stop execution

### Interface
- **^P** or **^H** - Show help
- **^C** or **ESC** - Cancel/Close dialogs
- **^V** - Open Variables window (Tk/Web)
- **^U** - Open Execution Stack window (Tk/Web)

## UI-Specific Shortcuts

### Breakpoint Toggle

| UI | Shortcut |
|----|----------|
| **Curses** | **b** - Toggle breakpoint on current line |
| **Tk** | **^B** - Toggle breakpoint on current line, or click line number gutter |
| **Web** | Click line number or use toolbar "Breakpoint" button |

### Curses-Specific (Terminal UI)

When paused at breakpoint:
- **c** - Continue to next breakpoint or end
- **s** - Step through line by line
- **e** - End execution and return to editor

## Menu Navigation

- **↑/↓** or **Tab** - Navigate menu items
- **Enter** - Select menu item
- **ESC** - Close menu

## Help Browser

- **↑/↓** - Scroll line by line
- **Space** - Page down
- **B** - Page up
- **Enter** - Follow link at cursor
- **U** - Go back/up to parent
- **N** - Next topic
- **P** - Previous topic
- **Q** or **ESC** - Exit help

[Back to main help](index.md)
