---
description: NEEDS_DESCRIPTION
keywords:
- command
- commands
- curses
- error
- file
- for
- function
- keyboard
- line
- next
title: Curses UI Keyboard Commands
type: guide
---

# Curses UI Keyboard Commands

All keyboard shortcuts for the curses text interface.

## Program Commands

| Key | Action |
|-----|--------|
| **Ctrl+P** | Open help system |
| **Ctrl+R** | Run program |
| **Ctrl+L** | List program to output window |
| **Ctrl+S** | Save program (prompts for filename) |
| **Ctrl+O** | Load program (prompts for filename) |
| **Ctrl+N** | New program (clear all lines) |
| **Ctrl+E** | Renumber program lines (RENUM command) |
| **ESC** | Clear error message, return to Ready |
| **Q** | Quit the IDE |

**Note:** No function keys required! All commands use Ctrl or regular keys.

## Debugging Commands

| Key | Action |
|-----|--------|
| **b** | Toggle breakpoint on current line (shows ● indicator) |
| **Ctrl+T** | Step (execute one statement, then pause) |
| **Ctrl+G** | Continue (run to next breakpoint or end) |
| **Ctrl+Q** | Stop execution |
| **Ctrl+V** | Open variables window (during execution) |
| **Ctrl+K** | Open execution stack window (during execution) |

### Line Indicators

Lines in the editor show status with indicators:

| Indicator | Meaning |
|-----------|---------|
| **?** | Parse error (syntax error in line) |
| **●** | Breakpoint set on this line |
| **(space)** | Normal line |

**Priority:** Error (?) > Breakpoint (●) > Normal

### Statement Highlighting

When stepping through code, the status bar shows which statement is executing:
- Single-statement line: `Line 100`
- Multi-statement line: `Line 100 statement 2`

Multi-statement lines use `:` to separate statements:
```basic
100 A = 1 : B = 2 : C = 3
```
Use **Ctrl+T** to step through each statement individually.

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
- Press **ESC** to clear error messages
- Press **Ctrl+P** to open help system
- Lines are saved when you press **Enter**
- Line numbers auto-increment by 10

## See Also

- [Editing Programs](editing.md)
- [Running Programs](running.md)
- [File Operations](files.md)