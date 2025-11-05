---
title: Tips & Tricks
type: guide
ui: tk
description: Best practices and productivity tips
keywords: [tips, tricks, productivity, best practices]
---

# Tips & Tricks

Get the most out of the MBASIC Tkinter GUI.

## Smart Insert for Rapid Development

**Scenario:** You have a skeleton and need to flesh it out:
```basic
10 REM Initialize
100 REM Process
200 REM Output
300 END
```

Use **Ctrl+I** (Smart Insert) to insert blank lines under each section without calculating line numbers!

## Variables Window for Arrays

When working with arrays, keep Variables window open (**Ctrl+W**):

```basic
10 DIM Scores(5)
20 FOR I = 1 TO 5
30   INPUT "Score"; Scores(I)
40 NEXT I
```

Watch each array element fill in real-time!

## Execution Stack for Nested Loops

Press **Ctrl+K** (Toggle Stack) while stepping through nested loops to see the current state of all active loops.

## Quick Testing Cycle

Fastest workflow:
```
Type → Ctrl+R (Run) → Check → Edit → Ctrl+R (Run) → Check → ...
```

No need to save between test runs! Save with **Ctrl+S** only when satisfied.

## Use Comments Liberally

MBASIC supports two comment styles:
```basic
10 REM This is a remark statement
20 ' This is also a comment (shorter!)
```

Add comments with **Ctrl+I** (Smart Insert).

## Common Mistakes to Avoid

❌ **Manually calculating line numbers** → Use **Ctrl+I** (Smart Insert)
❌ **Running without saving** → Save often with **Ctrl+S**
❌ **Ignoring ? markers** → Fix syntax errors before running
❌ **Not using Variables window** → You're debugging blind!
❌ **Stepping through entire program** → Use breakpoints + Continue (Run menu)

## Renumber Before Sharing

Keep development line numbers messy, but Renumber (**Ctrl+E**) before sharing code. Makes it clean and professional.

[← Back to Tk GUI Help](index.md)
