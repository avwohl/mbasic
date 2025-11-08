---
title: Tips & Tricks
type: guide
ui: tk
description: Best practices and productivity tips
keywords: [tips, tricks, productivity, best practices]
---

# Tips & Tricks

Get the most out of the MBASIC Tkinter GUI.

**Note:** Some features described below (Smart Insert, Variables Window, Execution Stack) are documented here based on the Tk UI design specifications. Check [Settings](settings.md) for current implementation status or refer to the actual UI to verify which features are currently available.

## Smart Insert for Rapid Development

**Scenario:** You have a skeleton and need to flesh it out:
```basic
10 REM Initialize
100 REM Process
200 REM Output
300 END
```

Use **{{kbd:smart_insert:tk}}** (Smart Insert) to insert blank lines under each section without calculating line numbers!

## Variables Window for Arrays

When working with arrays, keep Variables window open (**{{kbd:toggle_variables:tk}}**):

```basic
10 DIM Scores(5)
20 FOR I = 1 TO 5
30   INPUT "Score"; Scores(I)
40 NEXT I
```

Watch each array element fill in real-time!

## Execution Stack for Nested Loops

Press **{{kbd:toggle_stack:tk}}** (Toggle Stack) while stepping through nested loops to see the current state of all active loops.

## Quick Testing Cycle

Fastest workflow:
```
Type → {{kbd:run_program:tk}} (Run) → Check → Edit → {{kbd:run_program:tk}} (Run) → Check → ...
```

No need to save between test runs! Save with **{{kbd:file_save:tk}}** only when satisfied.

## Use Comments Liberally

MBASIC supports two comment styles:
```basic
10 REM This is a remark statement
20 ' This is also a comment (shorter!)
```

Add comments with **{{kbd:smart_insert:tk}}** (Smart Insert).

## Common Mistakes to Avoid

❌ **Manually calculating line numbers** → Use **{{kbd:smart_insert:tk}}** (Smart Insert)
❌ **Running without saving** → Save often with **{{kbd:file_save:tk}}**
❌ **Ignoring ? markers** → Fix syntax errors before running
❌ **Not using Variables window** → You're debugging blind!
❌ **Stepping through entire program** → Use breakpoints + Continue (Run menu)

## Renumber Before Sharing

Keep development line numbers messy, but Renumber (**{{kbd:renumber:tk}}**) before sharing code. Makes it clean and professional.

[← Back to Tk GUI Help](index.md)
