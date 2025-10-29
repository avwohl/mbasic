---
title: Tk UI Keyboard Shortcuts
type: guide
ui: tk
description: Complete keyboard shortcut reference for the Tk graphical interface
keywords: [shortcuts, keyboard, tk, tkinter, gui, hotkeys, commands]
---

# Tk UI Keyboard Shortcuts

Complete reference for all keyboard shortcuts in the Tk graphical interface.

## File Operations

| Shortcut | Action |
|----------|--------|
| **Ctrl+N** | New program (clear editor) |
| **Ctrl+O** | Open file (file browser dialog) |
| **Ctrl+S** | Save current file |
| **Ctrl+Shift+S** | Save As (choose new filename) |

## Program Execution

| Shortcut | Action |
|----------|--------|
| **Ctrl+R** | Run program from start |
| **Ctrl+Q** | Stop execution |
| **Ctrl+C** | Interrupt running program (also stops infinite loops) |

## Debugging

| Shortcut | Action |
|----------|--------|
| **Ctrl+B** | Toggle breakpoint on current line |
| **Ctrl+T** | Step (execute one statement, then pause) |
| **Ctrl+G** | Continue (run to next breakpoint or end) |
| **Ctrl+V** | Show/hide Variables window |
| **Ctrl+K** | Show/hide Execution Stack window |

### Step Statement vs Step Line

- **Step Statement**: Executes one statement at a time
  - Multi-statement lines (with `:`) are stepped through statement-by-statement
  - Example: `A=1 : B=2 : C=3` takes 3 steps
  - Current statement highlighted in yellow

- **Step Line**: Would execute the entire line
  - Currently same as Step Statement (may change in future)

## Editor Commands

| Shortcut | Action |
|----------|--------|
| **Ctrl+I** | Smart insert - insert blank line at midpoint between current and next line |
| **Ctrl+E** | Renumber program lines (opens dialog) |
| **Ctrl+F** | Find text in editor (opens Find dialog) |
| **F3** | Find next occurrence |
| **Ctrl+H** | Find and replace (opens Replace dialog) |

### Find and Replace (Ctrl+F, Ctrl+H)

The Tk UI includes full Find and Replace functionality:

**Find (Ctrl+F):**
- Opens Find dialog
- Enter search text
- Options: Case sensitive, Whole word
- Press Enter or "Find Next" to search
- **F3** to find next occurrence without reopening dialog
- Search wraps around to beginning when reaching end

**Replace (Ctrl+H):**
- Opens Replace dialog
- Enter find text and replacement text
- Same search options as Find
- Buttons:
  - **Find Next** - locate next match
  - **Replace** - replace current match and find next
  - **Replace All** - replace all occurrences at once
- Shows count of replacements made

**Visual Feedback:**
- Found text highlighted in yellow
- Editor auto-scrolls to show matches
- Status bar shows "not found" if no matches

### Smart Insert (Ctrl+I)

Intelligently inserts a blank line between the current line and the next line:

- **With gap**: Inserts at midpoint (e.g., line 15 between 10 and 20)
- **No gap**: Offers to renumber program to make room
- **At end**: Uses standard increment from current line

Example usage:
```basic
10 PRINT "START"
20 PRINT "END"

' Cursor on line 10, press Ctrl+I
' Inserts: 15 (cursor positioned after line number)

10 PRINT "START"
15
20 PRINT "END"
```

Perfect for adding code between existing lines without manual line number calculation!

### Standard Text Editing

| Shortcut | Action |
|----------|--------|
| **Ctrl+A** | Select all text |
| **Ctrl+X** | Cut selected text |
| **Ctrl+C** | Copy selected text |
| **Ctrl+V** | Paste text |
| **Home** | Move to start of line |
| **End** | Move to end of line |
| **Ctrl+Home** | Move to start of document |
| **Ctrl+End** | Move to end of document |

## Help System

| Shortcut | Action |
|----------|--------|
| **F1** or **Ctrl+H** | Open help topics |

## Visual Indicators

### Line Number Gutter

The line number gutter shows status for each line:

| Indicator | Color/Style | Meaning |
|-----------|-------------|---------|
| **?** | Red background | Parse error (syntax error) |
| **●** | Light red background | Breakpoint set |
| **(number only)** | Normal | No special status |

**Priority:** Error (?) always shows instead of breakpoint (●) if both apply.

### Statement Highlighting

When debugging, the current statement is highlighted:

- **Yellow background** on the exact statement being executed
- For multi-statement lines (using `:`), only the current statement is highlighted
- Highlight moves as you step through each statement with **Ctrl+T**
- Editor auto-scrolls to keep highlighted statement visible

Example:
```basic
100 A = 1 : B = 2 : PRINT A + B
```

Step 1: `A = 1` highlighted in yellow
Step 2: `B = 2` highlighted in yellow
Step 3: `PRINT A + B` highlighted in yellow
Step 4: Advances to next line

## Mouse Actions

### Line Numbers

- **Click line number** → Toggle breakpoint on that line

### Editor

- **Double-click word** → Select word
- **Triple-click line** → Select entire line
- **Click and drag** → Select text
- **Right-click** → Context menu (cut/copy/paste)

### Variables Window

- **Double-click variable** → Edit variable value
- **Click column header** → Sort by that column

## Tips

### Efficient Debugging

1. **Set breakpoints** with mouse clicks on line numbers
2. **Run to breakpoint** with **Ctrl+R** then **Ctrl+G**
3. **Step through code** with **Ctrl+T**
4. **Watch variables** with **Ctrl+V** (keep window open)
5. **Check execution stack** with **Ctrl+K** for loops/GOSUBs

### Multi-Statement Lines

- Use **Ctrl+T** (Step Statement) to step through each statement
- Watch the yellow highlight move across the line
- Perfect for debugging complex lines like:
  ```basic
  100 X=5 : IF X>3 THEN Y=1 : PRINT "Y="; Y
  ```

### Finding Errors

- Look for **?** markers in the line number gutter
- These indicate parse errors (syntax errors)
- Fix the syntax and the **?** will disappear
- Errors are checked automatically as you type (100ms delay)

### Breakpoint Management

- Click line numbers to quickly set/remove breakpoints
- **●** indicator shows where breakpoints are set
- Breakpoints persist when you edit code (as long as line number doesn't change)
- Use **Ctrl+B** if you prefer keyboard over mouse

## Quick Reference Card

### Most Important Shortcuts

| Task | Shortcut |
|------|----------|
| Run | **Ctrl+R** |
| Stop | **Ctrl+Q** |
| Step | **Ctrl+T** |
| Breakpoint | **Ctrl+B** (or click line number) |
| Variables | **Ctrl+V** |
| Smart Insert | **Ctrl+I** |
| Save | **Ctrl+S** |
| Help | **F1** |

Print this section for quick reference!

## See Also

- [Debugging Features](../../common/debugging.md) - Complete debugging guide
- [Tk UI Index](index.md) - Tk UI overview
- [Editor Commands](../../common/editor-commands.md) - Editing features
- [Getting Started](../../mbasic/getting-started.md) - Your first program

---

**Pro tip:** Keep the Variables window open (**Ctrl+V**) while debugging - it's your best debugging tool!
