# Edit at Breakpoint Validation - TODO

**Status:** ⏳ TODO

**Priority:** HIGH

## Problem

We now allow full program editing when paused at breakpoint or error, then Continue re-parses and resumes. However, we don't validate that the execution state is still valid after edits.

## Potential Issues

### 1. NEXT pointing to wrong FOR or no FOR
```basic
40 FOR x%=0 TO 10
50   FOR y%=0 TO 5
60     PRINT x%, y%
70   NEXT y%
80 NEXT x%
```

User sets breakpoint at line 60, hits it. Stack has: [FOR x%, FOR y%]

**Edit scenario A:** User changes line 40:
```basic
40 FOR z%=0 TO 10  ' Changed x% to z%
```

Now NEXT x% at line 80 will fail because x% is not on the stack!

**Edit scenario B:** User deletes line 50:
```basic
40 FOR x%=0 TO 10
60   PRINT x%, y%    ' Line 50 deleted
70 NEXT y%           ' This NEXT has no matching FOR!
80 NEXT x%
```

Stack still has [FOR x%, FOR y%] but line 50 doesn't exist anymore.

### 2. Return addresses pointing to non-existing lines

**GOSUB scenario:**
```basic
10 GOSUB 100
20 PRINT "Back"
30 END
100 PRINT "Sub"
110 RETURN
```

Set breakpoint at line 100. Stack has: [GOSUB return to 20]

**Edit:** User deletes line 20

Now RETURN will try to jump to line 20 which doesn't exist!

**FOR loop scenario:**
```basic
40 FOR i%=0 TO 10
50   PRINT i%
60 NEXT i%
```

Breakpoint at line 50. Stack has: [FOR i% return to line 40]

**Edit:** User changes line 40 to line 45:
```basic
45 FOR i%=0 TO 10
50   PRINT i%
60 NEXT i%
```

NEXT i% will try to jump back to line 40 (in stack) but line 40 no longer exists!

### 3. Variable type changes

```basic
40 FOR i%=0 TO 10
50   PRINT i%
60 NEXT i%
```

Breakpoint at line 50. Variable i% exists in memory.

**Edit:** User changes to:
```basic
40 FOR i=0 TO 10   ' Changed i% to i (integer suffix removed)
50   PRINT i
60 NEXT i
```

Stack still has "FOR i%" but program now uses "i" - they're different variables!

### 4. Control structure nesting changes

```basic
40 FOR x%=0 TO 10
50   WHILE x% < 5
60     PRINT x%
70   WEND
80 NEXT x%
```

Breakpoint at line 60. Stack: [FOR x%, WHILE]

**Edit:** User deletes lines 50 and 70:
```basic
40 FOR x%=0 TO 10
60   PRINT x%
80 NEXT x%
```

Stack still has WHILE entry but WHILE/WEND no longer exist in code!

## Solution Approaches

### Option 1: Validate and Clear Stack (Safest)
When Continue is called after editing:
1. Re-parse program (already done)
2. Validate all stack entries:
   - FOR loops: Check return line exists and has FOR statement for that variable
   - GOSUB: Check return line exists
   - WHILE: Check while_line exists and has WHILE statement
3. If ANY validation fails:
   - Clear entire execution stack
   - Reset to beginning of current line
   - Show warning: "Program edited - execution stack cleared"

**Pros:**
- Safe - prevents crashes
- Clear behavior - user knows stack was cleared

**Cons:**
- Loses execution context
- Can't resume in middle of nested loops

### Option 2: Validate and Repair (Smart)
1. Re-parse program
2. For each stack entry, try to repair:
   - FOR loop: Search for matching FOR statement, update return address
   - GOSUB: Verify return line still exists, else fail
   - WHILE: Search for matching WHILE statement, update address
3. Remove invalid entries
4. Show summary: "2 stack entries removed due to edits"

**Pros:**
- Preserves valid stack entries
- More user-friendly

**Cons:**
- Complex to implement correctly
- May be confusing if behavior is unexpected

### Option 3: Warn but Don't Validate (Current)
Let the error happen naturally during execution:
- NEXT will fail: "NEXT x% without FOR"
- RETURN will fail: "Undefined line number"
- User gets immediate feedback

**Pros:**
- Simple - already works
- Errors are descriptive

**Cons:**
- May seem like a bug to user
- Execution state can be corrupted

## Recommended Approach

**Hybrid: Validate return addresses only**
1. Re-parse program (already done)
2. Validate all stack entries have valid return addresses:
   - FOR loops: Check return_line exists in line_table
   - GOSUB: Check return line exists in line_table
   - WHILE: Check while_line exists in line_table
3. If any return address is invalid:
   - Remove that stack entry
   - Show warning with details
4. Don't validate variable names/types - let natural errors occur

This catches the most dangerous issues (crashing on return to deleted line) while keeping implementation simple.

## Test Cases to Implement

### Test 1: Delete FOR line while in loop
```basic
10 FOR i%=1 TO 3
20   PRINT i%
30 NEXT i%
```
- Breakpoint at line 20
- Delete line 10
- Continue → Should detect and handle gracefully

### Test 2: Change FOR variable name
```basic
10 FOR i%=1 TO 3
20   PRINT i%
30 NEXT i%
```
- Breakpoint at line 20
- Change line 10 to `FOR j%=1 TO 3`
- Continue → NEXT i% should fail with clear error

### Test 3: Delete GOSUB return line
```basic
10 GOSUB 100
20 PRINT "Back"
30 END
100 PRINT "Sub"
110 RETURN
```
- Breakpoint at line 100
- Delete line 20
- Continue through line 110 → Should detect line 20 doesn't exist

### Test 4: Renumber lines
```basic
10 FOR i%=1 TO 3
20   PRINT i%
30 NEXT i%
```
- Breakpoint at line 20
- Renumber: change 10→15, 20→25, 30→35
- Continue → FOR loop return address is now wrong (points to 10, not 15)

### Test 5: Delete nested structure
```basic
10 FOR x%=1 TO 2
20   FOR y%=1 TO 2
30     PRINT x%, y%
40   NEXT y%
50 NEXT x%
```
- Breakpoint at line 30 (both loops on stack)
- Delete lines 20 and 40 (inner loop)
- Continue → Should handle gracefully

### Test 6: Change WHILE to FOR
```basic
10 WHILE x% < 5
20   PRINT x%
30   x% = x% + 1
40 WEND
```
- Breakpoint at line 20 (WHILE on stack)
- Change lines 10 and 40 to FOR/NEXT
- Continue → Stack expects WHILE but now has FOR

## Files to Modify

- `src/ui/tk_ui.py`: Add validation in `_menu_continue()` after re-parsing
- `src/ui/curses_ui.py`: Same validation for curses UI
- `src/ui/web/web_ui.py`: Same validation for web UI
- `src/runtime.py`: Maybe add `validate_stack()` helper method
- `utils/test_edit_at_breakpoint.py`: New test script for all scenarios

## Acceptance Criteria

- [ ] All test cases pass without crashes
- [ ] User gets clear error messages when edits invalidate execution state
- [ ] Valid edits (e.g., fixing a typo in PRINT statement) continue working
- [ ] Documentation explains what happens when you edit at breakpoints
- [ ] All 3 UIs (Tk, Curses, Web) handle this consistently
