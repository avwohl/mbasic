# Work in Progress

## Task
Fix FOR loop stack corruption - 23 duplicate entries after ONE run

## Problem
User confirms:
- Fresh Tk window, paste program, click Run ONCE
- Program stops at line 70 with NEXT error (expected)
- Execution Stack shows **23 FOR loops** (WRONG!)
- First entry: "FOR x% = 20 TO 20" (x% finished its iterations)
- 22+ duplicate entries of "FOR y% = 0 TO 23"

## Expected
After stopping at line 70 on first iteration:
- Stack should have 2 entries: FOR x%, FOR y%

## Actual
- Stack has 23 entries!

## Theories
1. FOR statement is pushing multiple times per execution?
2. Loop is somehow iterating before the error?
3. Stack corruption during loop execution?

## Status
- ⏳ Adding debug logging to push_for_loop
- ⏳ Adding stack trace to see WHO is pushing duplicates
- ⏳ Need to understand execution flow

## Next Steps
1. Add logging to push_for_loop to see when it's called
2. Add click handler for stack entries to highlight line
3. Remove indent (unclear which indent user means)
