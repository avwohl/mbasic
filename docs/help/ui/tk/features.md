---
title: Essential TK GUI Features
type: guide
ui: tk
description: Key features of the MBASIC Tkinter GUI
keywords: [tk, features, smart insert, breakpoints, variables, debugging]
---

# Essential TK GUI Features

The Tkinter GUI provides powerful features for BASIC development.

## Smart Insert ({{kbd:smart_insert:tk}})

**The fastest way to add code between existing lines!**

Example:
```basic
10 PRINT "START"
20 PRINT "END"
```

Press {{kbd:smart_insert:tk}} on line 10 → Automatically inserts line 15!

No mental math required.

## Syntax Checking

The editor checks syntax as you type (100ms delay).

- Red **?** appears in gutter for errors
- Error message shown in output pane
- Fix the error → **?** disappears automatically

## Breakpoints

**Set breakpoints:**
- Click line number in gutter
- Or press {{kbd:toggle_breakpoint:tk}}
- Blue ● appears

**Debug with:**
- {{kbd:step_statement:tk}} - Execute next statement
- {{kbd:step_line:tk}} - Execute next line
- {{kbd:continue_execution:tk}} - Continue to next breakpoint

## Variables Window ({{kbd:toggle_variables:tk}})

Shows all variables with:
- Name (case preserved - displays as you typed!)
- Value
- Type (integer, float, string, array)

Updates in real-time during debugging.

## Execution Stack ({{kbd:toggle_stack:tk}})

Shows active FOR loops and GOSUB calls. Perfect for understanding nested structures.

## Find and Replace

**Find text ({{kbd:find:tk}}):**
- Opens Find dialog with search options
- Case sensitive and whole word matching
- Press F3 to find next occurrence

**Replace text ({{kbd:replace:tk}}):**
- Opens combined Find/Replace dialog
- Find and replace single or all occurrences
- Visual highlighting of matches
- Shows replacement count

**Note:** {{kbd:find:tk}} opens the Find dialog. {{kbd:replace:tk}} opens the Find/Replace dialog which includes both Find and Replace functionality.

## Context Help (Shift+F1)

Get instant help for any BASIC keyword:
- Place cursor on a keyword (like PRINT, FOR, GOTO)
- Press Shift+F1
- Help page for that keyword opens automatically
- Quick way to look up syntax and examples

## More Features

For complete details, see:
- [Getting Started](getting-started.md)
- [Common Workflows](workflows.md)
- [Settings & Configuration](settings.md)

[← Back to Tk GUI Help](index.md)
