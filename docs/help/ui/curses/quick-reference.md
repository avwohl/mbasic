---
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: MBASIC - Keyboard Shortcuts
type: guide
---

# MBASIC - Keyboard Shortcuts

Quick reference for the curses text UI.

## Global Commands

| Key | Action |
|-----|--------|
| **Ctrl+Q** / **Ctrl+C** | Quit |
| **Ctrl+U** | Show menu |
| **Ctrl+A** | This help |
| **Ctrl+W** | Toggle variables watch window |
| **Ctrl+K** | Toggle execution stack window |

## Program Management

| Key | Action |
|-----|--------|
| **Ctrl+R** | Run program |
| **Ctrl+L** | List program |
| **Ctrl+N** | New program |
| **Ctrl+S** | Save program |
| **Ctrl+O** | Open/Load program |

## Editing

| Key | Action |
|-----|--------|
| **Ctrl+B** | Toggle breakpoint on current line |
| **Ctrl+D** | Delete current line |
| **Ctrl+E** | Renumber all lines (RENUM) |

## Debugger (when program running)

| Key | Action |
|-----|--------|
| **Ctrl+G** | Continue execution (Go) |
| **Ctrl+T** | Step - execute one line (sTep) |
| **Ctrl+X** | Stop execution (eXit) |
| **Ctrl+W** | Show/hide variables window |
| **Ctrl+K** | Show/hide execution stack window |

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

- [Keyboard Commands](keyboard-commands.md) - Full command reference
- [Editing Programs](editing.md) - Detailed editing guide
- [Running Programs](running.md) - Execution and debugging
- [File Operations](files.md) - Save and load programs
- [BASIC Language](../../common/language.md) - Language reference