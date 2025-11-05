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
| **Ctrl+Q** | Quit |
| **Ctrl+U** | Show menu |
| **^F** (Ctrl+F) | Help (with search) |
| **Ctrl+W** | Toggle variables watch window |
| **Menu only** | Toggle execution stack window |

## Program Management

| Key | Action |
|-----|--------|
| **Ctrl+R** | Run program |
| **Menu only** | List program |
| **Ctrl+N** | New program |
| **^V** (Ctrl+V) | Save program (Ctrl+S unavailable - terminal flow control) |
| **Ctrl+O** | Open/Load program |

## Editing

| Key | Action |
|-----|--------|
| **Ctrl+B** | Toggle breakpoint on current line |
| **Ctrl+D** | Delete current line |
| **Ctrl+E** | Renumber all lines (RENUM) |

**Note:** Find/Replace is not yet available in Curses UI. See [Find/Replace](find-replace.md) for workarounds.

## Debugger (when program running)

| Key | Action |
|-----|--------|
| **Ctrl+G** | Continue execution |
| **Ctrl+K** | Step Line - execute all statements on current line |
| **Ctrl+T** | Step Statement - execute one statement at a time |
| **Ctrl+X** | Stop execution |
| **Ctrl+W** | Show/hide variables window |
| **Menu only** | Show/hide execution stack window |

## Variables Window (when visible)

| Key | Action |
|-----|--------|
| **s** | Cycle sort mode (Accessed → Written → Read → Name) |
| **d** | Toggle sort direction (ascending ↑ / descending ↓) |
| **f** | Filter variables (All/Scalars/Arrays/Modified) |
| **/** | Search for variable |

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

### Column Layout

```
[0]   Status: ? error (highest), ● breakpoint, space normal
[1-5] Line number (5 digits, right-aligned)
[6]   Separator space
[7+]  BASIC code
```

### Status Priority (when line has multiple states)

1. **Error (?)** - highest, shown when syntax error exists
2. **Breakpoint (●)** - shown when no error but breakpoint set
3. **Normal ( )** - default

### Line Number Editing

- Type digits in columns 1-5 (calculator-style)
- Numbers auto right-justify when leaving column
- Leftmost digit drops when typing at rightmost position
- Backspace deletes rightmost digit and right-justifies

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