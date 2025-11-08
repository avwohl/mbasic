---
description: How to navigate and use the built-in help system in Curses UI
keywords:
- help
- navigation
- browse
- search
- links
- ctrl+p
ui: curses
title: Using the Help System
type: guide
---

# Using the Help System

How to navigate MBASIC help.

## Opening Help

Press **{{kbd:help:curses}}** anytime to open help.

## Navigation Keys

### Scrolling

| Key | Action |
|-----|--------|
| **Up/Down** | Scroll one line |
| **Page Up/Down** | Scroll one page |

### Following Links

Links appear with text in square brackets followed by URL in parentheses.

**Format:** Square brackets around text, then parentheses around destination

1. Use **Tab** to move to next link
2. Press **Enter** to follow the link

### Searching

| Key | Action |
|-----|--------|
| **/** | Open search prompt |
| Type query | Enter search terms |
| **Enter** | Execute search |
| **ESC** | Cancel search |

**Search tips:**
- Search across all three documentation tiers
- Try keywords like "loop", "array", "file"
- Try statement names like "print", "for", "if"
- Try function names like "left$", "abs", "int"
- Results show tier markers: 📕 Language, 📗 MBASIC, 📘 UI

### Going Back

| Key | Action |
|-----|--------|
| **U** | Go back to previous topic |

### Browsing Topics

| Key | Action |
|-----|--------|
| **Tab** | Next link in current page |
| **Shift+Tab** | Previous link in current page |

### Exiting Help

| Key | Action |
|-----|--------|
| **ESC** or **Q** | Exit help, return to editor |

## Help Organization

Help is organized into sections:

### UI-Specific Help

Commands specific to this interface:
- [Curses UI](index.md) - This interface
- Other UIs (Tkinter, CLI) - Different interfaces

### Language Reference

BASIC language (same for all UIs):
- [Getting Started](../../common/getting-started.md) - BASIC basics
- [Statements](../../common/language/statements/index.md) - Language reference
- [Functions](../../common/language/functions/index.md) - Built-in functions

### Examples

Sample programs to learn from.

## Tips

- Press **{{kbd:help:curses}}** anytime for help
- Links are highlighted
- **U** goes back
- **ESC** or **Q** exits help
- Status bar shows navigation keys

## See Also

- [Keyboard Shortcuts](../../../user/keyboard-shortcuts.md) - All editor shortcuts