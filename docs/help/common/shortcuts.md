# Keyboard Shortcuts

Keyboard shortcuts vary significantly by UI. This page shows a comparison across all interfaces. For detailed UI-specific help, see:
- [CLI Commands](../ui/cli/index.md) - Command-based interface
- [Curses UI Shortcuts](../ui/curses/quick-reference.md) - Full-screen terminal interface
- [Tk UI Shortcuts](../ui/tk/feature-reference.md) - GUI with keyboard shortcuts
- [Web Interface](../ui/web/index.md) - Click-based browser interface

## Execution Shortcuts

| Action | CLI | Curses | Tk | Web |
|--------|-----|--------|-----|-----|
| **Run program** | {{kbd:run:cli}} | {{kbd:run:curses}} | {{kbd:run_program:tk}} | {{kbd:run:web}} |
| **Step statement** | {{kbd:step:cli}} | {{kbd:step:curses}} | Toolbar only | {{kbd:step:web}} |
| **Step line** | Not available | {{kbd:step_line:curses}} | Toolbar only | Not available |
| **Continue** | {{kbd:continue:cli}} | {{kbd:continue:curses}} | Toolbar only | {{kbd:continue:web}} |
| **Stop** | {{kbd:stop:cli}} | {{kbd:stop:curses}} | Toolbar only | {{kbd:stop:web}} |

## Interface Shortcuts

| Action | CLI | Curses | Tk | Web |
|--------|-----|--------|-----|-----|
| **Help** | {{kbd:help:cli}} | {{kbd:help:curses}} | {{kbd:help_topics:tk}} | {{kbd:help:web}} |
| **Save** | {{kbd:save:cli}} | {{kbd:save:curses}} | {{kbd:file_save:tk}} | {{kbd:save:web}} |
| **Open/Load** | {{kbd:open:cli}} | {{kbd:open:curses}} | {{kbd:file_open:tk}} | {{kbd:open:web}} |
| **New program** | {{kbd:new:cli}} | {{kbd:new:curses}} | {{kbd:file_new:tk}} | {{kbd:new:web}} |
| **Quit** | {{kbd:quit:cli}} | {{kbd:quit:curses}} | {{kbd:file_quit:tk}} | Menu only |

## UI-Specific Shortcuts

### Breakpoint Toggle

| UI | Shortcut |
|----|----------|
| **CLI** | Not available in CLI mode |
| **Curses** | **b** - Toggle breakpoint on current line |
| **Tk** | **{{kbd:toggle_breakpoint:tk}}** - Toggle breakpoint on current line, or click line number gutter |
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
