---
title: Getting Started with Tkinter GUI
type: guide
ui: tk
description: First steps with the MBASIC graphical interface
keywords: [tk, gui, getting started, quick start, first program]
---

# Getting Started with Tkinter GUI

Welcome to the MBASIC graphical IDE! This guide will help you get started quickly.

## Starting the GUI

```bash
mbasic --ui tk [filename.bas]
```

Or to use the default curses UI:
```bash
mbasic [filename.bas]
```

## Interface Layout

```
┌────────────────────────────────────────────────────┐
│ Menu Bar: File, Edit, Run, View, Help             │
├─────────┬──────────────────────────────────────────┤
│ Line #  │  Editor Window                           │
│  Gutter │  - Write your BASIC program here         │
│         │  - Line numbers in left gutter           │
│  10     │  - Breakpoints marked with ●             │
│  20  ●  │  - Syntax errors marked with ?           │
│  30  ?  │  - Current execution line highlighted    │
├─────────┴──────────────────────────────────────────┤
│ Output Window                                      │
│ - Program output appears here                      │
│ - Error messages and status                        │
└────────────────────────────────────────────────────┘
```

## Your First Program

1. **Type your program:**
   ```basic
   10 PRINT "Hello, World!"
   20 END
   ```

2. **Run it:** Press {{kbd:run_program}} or Run → Run Program

3. **See output:** Check the output window below the editor

Congratulations! You've run your first MBASIC program.

## Essential Shortcuts

| Shortcut | Action |
|----------|--------|
| {{kbd:run_program}} | Run program |
| {{kbd:save_file}} | Save file |
| {{kbd:smart_insert}} | Insert line between existing lines |
| {{kbd:toggle_breakpoint}} | Toggle breakpoint |
| {{kbd:toggle_variables}} | Show/hide variables window |

## Next Steps

- [Essential Features](features.md) - Learn about Smart Insert, Breakpoints, etc.
- [Common Workflows](workflows.md) - Step-by-step guides
- [Keyboard Shortcuts](keyboard-shortcuts.md) - Complete reference

[← Back to Tk GUI Help](index.md)
