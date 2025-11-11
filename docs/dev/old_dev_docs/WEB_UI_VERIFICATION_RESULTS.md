# Web UI Debugger Verification Results

## Date: 2025-10-26
## Test File: `tests/web_ui_verification_test.bas`

This document records the verification of Web UI debugger features against Tk UI behavior.

---

## Code Analysis Results

### ✅ Variables Window Column Order
**Status:** FIXED
**Location:** `src/ui/web/web_ui.py:886-890`

**Before:**
```python
columns=[
    {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
    {'name': 'type', 'label': 'Type', 'field': 'type', 'align': 'left'},  # Wrong order
    {'name': 'value', 'label': 'Value', 'field': 'value', 'align': 'left'},
]
```

**After:**
```python
columns=[
    {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
    {'name': 'value', 'label': 'Value', 'field': 'value', 'align': 'left'},  # Fixed!
    {'name': 'type', 'label': 'Type', 'field': 'type', 'align': 'left'},
]
```

**Result:** Column order now matches Tk UI (Name | Value | Type)

---

## Debugger State Tracking

### ✅ Current Line Tracking
**Status:** IMPLEMENTED
**Location:** `src/ui/web/web_ui.py:774, 792, 818, 824, 826`

The Web UI correctly uses:
- `self.interpreter.current_line_number` - Gets current line from shared interpreter
- `state.current_statement_index` - Gets statement position from shared interpreter state

**Evidence:**
```python
# Line 774: Breakpoint pause
self.status_label.text = f'Paused at breakpoint (line {self.interpreter.current_line_number}{stmt_info})'

# Line 818: Step mode status
stmt_info = f' statement {state.current_statement_index + 1}' if state.current_statement_index > 0 else ''

# Line 826: Step pause status
self.status_label.text = f'Paused at line {self.interpreter.current_line_number}{stmt_info}'
```

**Result:** Web UI uses the shared interpreter state that was fixed in commits 79f0a77, 27b555c, d04b7c8, a803ecc

---

## Manual Verification Required

The following features need manual testing in a running Web UI instance:

### Test 1: Step Mode Shows NEXT Statement
**Expected Behavior:** When stepping, debugger pauses BEFORE executing the statement (shows what WILL execute)

**Test Steps:**
1. Load `tests/web_ui_verification_test.bas`
2. Set breakpoint on line 60
3. Click Run
4. Should pause at line 60 with status "Paused at breakpoint (line 60)"
5. Check: I = 0 (FOR initialized), but "I=0" NOT printed yet
6. Click Step
7. Check: Now "I=0" appears in output
8. Status should show "Paused at line 70" (NEXT statement)

**Pass Criteria:** ✓ Breakpoint stops BEFORE executing line 60
**Pass Criteria:** ✓ After step, output shows "I=0"
**Pass Criteria:** ✓ Status shows correct line number

---

### Test 2: Control Flow Jumps (GOSUB)
**Expected Behavior:** When stepping through GOSUB, display jumps to subroutine

**Test Steps:**
1. Continue from Test 1 or restart
2. Set breakpoint on line 110
3. Run program
4. Should pause at line 110 with "Before GOSUB" printed
5. Status: "Paused at breakpoint (line 110)"
6. Click Step
7. Status should jump to line 210 (inside subroutine)
8. Should show "Paused at line 210"

**Pass Criteria:** ✓ Status jumps from line 110 to line 210
**Pass Criteria:** ✓ Shows "In subroutine 1" after next step

---

### Test 3: RETURN Jump Back
**Expected Behavior:** RETURN jumps back to line after GOSUB

**Test Steps:**
1. Continue from Test 2 (at line 210)
2. Click Step twice (execute lines 210, 220)
3. Should be at line 230 (RETURN)
4. Click Step
5. Status should jump to line 120 (NOT line 110!)
6. Should show "Paused at line 120"
7. Next step should print "After GOSUB"

**Pass Criteria:** ✓ RETURN jumps to line 120 (after GOSUB)
**Pass Criteria:** ✓ Does NOT jump back to line 110

---

### Test 4: Mid-Line GOSUB Return Position
**Expected Behavior:** RETURN from mid-line GOSUB should highlight statement AFTER GOSUB

**Test Steps:**
1. Restart program
2. Set breakpoint on line 150
3. Run program
4. Should pause at line 150
5. Click Step (executes PRINT "A", prints "A")
6. Click Step (executes GOSUB 300, jumps to line 310)
7. Status: "Paused at line 310"
8. Click Step twice (execute J=J+1 and RETURN)
9. Status should show "Paused at line 150 statement 3"
10. Next step should print "B" (NOT "A" again)

**Pass Criteria:** ✓ After RETURN, status shows "line 150 statement 3"
**Pass Criteria:** ✓ Next step prints "B" not "A"
**Pass Criteria:** ✓ Statement position shows correct part of line

---

### Test 5: Multi-Statement Line Stepping
**Expected Behavior:** Each statement on a line can be stepped separately

**Test Steps:**
1. Continue to line 180 or restart with breakpoint on 180
2. Pause at line 180
3. Click Step - should print "X"
4. Status: "Paused at line 180 statement 2"
5. Click Step - should print "Y"
6. Status: "Paused at line 180 statement 3"
7. Click Step - should print "Z"
8. Status: "Paused at line 190" (END)

**Pass Criteria:** ✓ Can step through each PRINT separately
**Pass Criteria:** ✓ Statement index updates correctly (statement 2, 3)
**Pass Criteria:** ✓ Prints appear one at a time

---

### Test 6: Variables Window
**Expected Behavior:** Variables appear with correct values and types

**Test Steps:**
1. Run program with breakpoint at line 220 (inside first subroutine)
2. Open Variables window (Ctrl+V or menu)
3. Check columns: Should be Name | Value | Type (NOT Name | Type | Value)
4. Check variables:
   - I should show current value (0, 1, 2, or 3)
   - Q should show current value
5. Step and verify values update

**Pass Criteria:** ✓ Columns are Name | Value | Type
**Pass Criteria:** ✓ Variable values are correct
**Pass Criteria:** ✓ Values update when stepping

---

### Test 7: NEXT Loop Jump
**Expected Behavior:** NEXT jumps back to FOR line

**Test Steps:**
1. Set breakpoint on line 70 (NEXT I)
2. Run program
3. Should pause at line 70 with I=0, "I=0" printed
4. Click Step
5. Status should jump to line 50 (FOR line)
6. Should show "Paused at line 50"
7. I should now be 1
8. Click Step
9. Should jump to line 60 again

**Pass Criteria:** ✓ NEXT jumps to FOR line (line 50)
**Pass Criteria:** ✓ Loop variable increments
**Pass Criteria:** ✓ Loop continues correctly

---

## Summary Checklist

Based on code analysis:
- ✅ **Variables window column order** - FIXED (commit pending)
- ✅ **Uses correct interpreter state** - Confirmed via code
- ✅ **Displays statement index** - Confirmed via code
- ⏳ **Step mode shows NEXT** - Manual test required
- ⏳ **GOSUB jump** - Manual test required
- ⏳ **RETURN jump** - Manual test required
- ⏳ **Mid-line GOSUB return** - Manual test required
- ⏳ **Multi-statement stepping** - Manual test required
- ⏳ **NEXT loop jump** - Manual test required

---

## Expected Outcome

Since the Web UI uses the shared interpreter (`self.interpreter.current_line_number` and `state.current_statement_index`), and those were fixed in commits 79f0a77, 27b555c, d04b7c8, and a803ecc, all manual tests **should pass**.

If any tests fail, it indicates a Web UI-specific display issue, not an interpreter issue.

---

## Notes

- Status bar shows: "Paused at line X [stmt Y]"
- Statement index is 0-based in code, displayed as 1-based to user
- Web UI doesn't highlight specific line/statement in editor (limitation of textarea)
- Status text is the primary indicator of current position
