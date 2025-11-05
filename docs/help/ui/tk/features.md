---
title: Essential TK GUI Features
type: guide
ui: tk
description: Key features of the MBASIC Tkinter GUI
keywords: [tk, features, smart insert, breakpoints, variables, debugging]
---

# Essential TK GUI Features

The Tkinter GUI provides powerful features for BASIC development.

## Smart Insert ({{kbd:smart_insert}})

**The fastest way to add code between existing lines!**

Example:
```basic
10 PRINT "START"
20 PRINT "END"
```

Press {{kbd:smart_insert}} on line 10 → Automatically inserts line 15!

No mental math required.

## Syntax Checking

The editor checks syntax as you type (100ms delay).

- Red **?** appears in gutter for errors
- Error message shown in output pane
- Fix the error → **?** disappears automatically

## Breakpoints

**Set breakpoints:**
- Click line number in gutter
- Or press {{kbd:toggle_breakpoint}}
- Blue ● appears

**Debug with:**
- {{kbd:step_statement}} - Execute next statement
- {{kbd:step_line}} - Execute next line
- {{kbd:continue_execution}} - Continue to next breakpoint

## Variables Window ({{kbd:toggle_variables}})

Shows all variables with:
- Name (case preserved - displays as you typed!)
- Value
- Type (integer, float, string, array)

Updates in real-time during debugging.

## Execution Stack ({{kbd:toggle_stack}})

Shows active FOR loops and GOSUB calls. Perfect for understanding nested structures.

## Find and Replace

**Find text (Ctrl+F):**
- Opens Find dialog with search options
- Case sensitive and whole word matching
- Press F3 to find next occurrence

**Replace text (Ctrl+H):**
- Find and replace single or all occurrences
- Visual highlighting of matches
- Shows replacement count

## More Features

For complete details, see:
- [Getting Started](getting-started.md)
- [Common Workflows](workflows.md)
- [Settings & Configuration](settings.md)

[← Back to Tk GUI Help](index.md)
