# Curses UI Keyboard Commands

All keyboard shortcuts for the curses text interface.

## Program Commands

| Key | Action |
|-----|--------|
| **?** | Open help system |
| **Ctrl+R** | Run program |
| **Ctrl+L** | List program to output window |
| **Ctrl+S** | Save program (prompts for filename) |
| **Ctrl+O** | Load program (prompts for filename) |
| **Ctrl+N** | New program (clear all lines) |
| **ESC** | Clear error message, return to Ready |
| **Q** | Quit the IDE |

**Note:** No function keys required! All commands use Ctrl or regular keys.

## Editing Commands

| Key | Alternative | Action |
|-----|-------------|--------|
| **Up/Down** | | Navigate between program lines |
| **Left/Right** | | Move cursor within current line |
| **Home** | **Ctrl+A** | Move to start of line |
| **End** | **Ctrl+E** | Move to end of line |
| **Enter** | | Save current line and advance to next |
| **Backspace** | | Delete character before cursor |
| **Delete** | | Delete character at cursor |

## Help System Navigation

When viewing help (like you are now):

| Key | Action |
|-----|--------|
| **Up/Down** | Scroll through current help page |
| **Space** | Page down (scroll a full screen) |
| **Enter** | Follow a link (when on a link line) |
| **U** | Go up to parent topic |
| **N** | Next topic at same level |
| **P** | Previous topic at same level |
| **Q** or **ESC** | Exit help, return to editor |

## Screen Layout

```
┌─────────────────────────────────────────┐
│ Editor Window (green)                   │  ← Program lines
│ 10 PRINT "Hello"                        │     show here
│ 20 END                                  │
│                                         │
├─────────────────────────────────────────┤
│ Output Window (yellow)                  │  ← Program output
│ Hello                                   │     appears here
│                                         │
├─────────────────────────────────────────┤
│ Status Line (cyan)                      │  ← Commands and
│ ^R=Run ^L=List ^S=Save ^O=Load Q=Quit   │     messages
└─────────────────────────────────────────┘
```

## Tips

- The cursor shows where you're typing
- Press **ESC** anytime to clear error messages
- **?** opens help system
- Lines are saved when you press **Enter**
- Line numbers auto-increment by 10

## See Also

- [Editing Programs](editing.md)
- [Running Programs](running.md)
- [File Operations](files.md)
