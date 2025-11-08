---
description: Quick reference card for all keyboard shortcuts in the Curses text UI
keywords:
- keyboard
- shortcuts
- commands
- ctrl
- hotkeys
- quick reference
- cheat sheet
ui: curses
title: MBASIC - Keyboard Shortcuts
type: guide
---

# MBASIC - Keyboard Shortcuts

Quick reference for the curses text UI.

## Global Commands

| Key | Action |
|-----|--------|
| **{{kbd:quit:curses}}** | Quit |
| **ESC** | Show menu |
| **{{kbd:help:curses}}** | Help |
| **Menu only** | Toggle variables window |
| **Menu only** | Settings |
| **Menu only** | Toggle execution stack window |

## Program Management

| Key | Action |
|-----|--------|
| **{{kbd:run:curses}}** | Run program |
| **Menu only** | List program |
| **{{kbd:new:curses}}** | New program |
| **{{kbd:save:curses}}** | Save program (Ctrl+S unavailable - terminal flow control) |
| **{{kbd:open:curses}}** | Open/Load program |

## Editing

| Key | Action |
|-----|--------|
| **{{kbd:toggle_breakpoint:curses}}** | Toggle breakpoint on current line |
| **Delete/Backspace** | Delete current line |
| **Menu only** | Renumber all lines (RENUM) |

**Note:** Cut/Copy/Paste are not available - use your terminal's native clipboard (typically Shift+Ctrl+C/V or mouse selection).

**Note:** Find/Replace is not yet available in Curses UI. See [Find/Replace](find-replace.md) for workarounds.

## Debugger (when program running)

| Key | Action |
|-----|--------|
| **{{kbd:continue:curses}}** | Continue execution |
| **{{kbd:step_line:curses}}** | Step Line - execute all statements on current line |
| **{{kbd:step:curses}}** | Step Statement - execute one statement at a time |
| **{{kbd:stop:curses}}** | Stop execution |
| **Menu only** | Show/hide variables window |
| **Menu only** | Show/hide execution stack window |

## Variables Window (when visible)

| Key | Action |
|-----|--------|
| **s** | Cycle sort mode (Accessed → Written → Read → Name) |
| **d** | Toggle sort direction (ascending ↑ / descending ↓) |
| **f** | Cycle filter mode (All → Scalars → Arrays → Modified) |
| **/** | Search for variable |
| **n** | Next search match |
| **N** | Previous search match |

**Sort Modes:**
- **Accessed**: Most recently accessed (read or written) - default, newest first
- **Written**: Most recently written to - newest first
- **Read**: Most recently read from - newest first
- **Name**: Alphabetically by variable name - A to Z

## Navigation

| Key | Action |
|-----|--------|
| **Tab** | Switch between editor and output |

## Screen Editor

### Display Format

```
S<linenum> CODE

Where:
[0]   Status: ? error (highest), ● breakpoint, space normal
[1+]  Line number (variable width)
      Separator space
      BASIC code
```

### Status Priority (when line has multiple states)

1. **Error (?)** - highest, shown when syntax error exists
2. **Breakpoint (●)** - shown when no error but breakpoint set
3. **Normal ( )** - default

### Line Number Editing

- Type digits to edit line number (variable width)
- Line numbers can be 1-65529

### Navigation Keys

| Key | Action |
|-----|--------|
| **Up/Down** | Move between lines (sorts if in number area) |
| **Left/Right** | Move within line (no auto-sort) |
| **Page Up/Down** | Scroll pages (triggers sort) |
| **Home/End** | Jump to start/end (triggers sort) |
| **Tab/Enter** | Move to code area / new line (triggers sort) |

### Auto-Numbering

- First line starts at 10 (configurable)
- Press Enter for next line (auto-increments by 10)
- Uses current line number + increment
- Avoids collisions with existing lines
- Configure in .mbasic.conf

## Examples

```basic
10 PRINT "Hello, World!"
20 END
```

## See Also

- [Keyboard Shortcuts](../../../user/keyboard-shortcuts.md) - Full command reference
- [Editing Programs](editing.md) - Detailed editing guide
- [Running Programs](running.md) - Execution and debugging
- [File Operations](files.md) - Save and load programs
- [BASIC Language](../../common/language.md) - Language reference