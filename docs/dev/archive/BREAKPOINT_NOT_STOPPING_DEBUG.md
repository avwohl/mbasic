# Breakpoint Not Stopping - Debug Guide

## Issue

Breakpoints are not stopping program execution. The program runs through without pausing at breakpoints.

## Debug Steps Added

I've added debug logging to the interpreter to help diagnose the issue.

### 1. Debug Logging Added

File: `src/interpreter.py` (lines 128-150)

The interpreter now logs:
- `[BP_CHECK]` - Every line checked, showing breakpoints set and step mode
- `[BP_HIT]` - When a breakpoint is actually triggered
- `[BP_RESULT]` - What the breakpoint callback returned

### 2. Run Debug Test

```bash
./test_bp_debug.sh
```

This will:
1. Open the IDE with test program
2. Prompt you to set a breakpoint on line 20
3. Prompt you to run with Ctrl+R
4. Save debug output to `/tmp/bp_debug.log`
5. Show analysis of what happened

### 3. What to Look For

The debug output will tell us:

#### Scenario A: Breakpoints working correctly
```
[BP_CHECK] Line 10: breakpoints={20}, step_mode=False, has_callback=True
[BP_CHECK] Line 20: breakpoints={20}, step_mode=False, has_callback=True
[BP_HIT] Calling breakpoint callback for line 20
[BP_RESULT] Callback returned: True
[BP_CHECK] Line 30: breakpoints={20}, step_mode=False, has_callback=True
```
✓ Breakpoint triggered, callback called, execution continued

#### Scenario B: Breakpoints set but not checked
```
(no [BP_CHECK] messages at all)
```
❌ Problem: Breakpoint checking code not running
- Possible cause: Program running without breakpoint callback
- Check: Is `_run_program_capture()` creating interpreter with callback?

#### Scenario C: Breakpoints checked but empty
```
[BP_CHECK] Line 10: breakpoints=set(), step_mode=False, has_callback=True
[BP_CHECK] Line 20: breakpoints=set(), step_mode=False, has_callback=True
```
❌ Problem: Breakpoints not being copied to interpreter
- Check line 592 in `src/ui/curses_ui.py`
- Verify `self.breakpoints` is not empty

#### Scenario D: Breakpoints checked, found, but callback not called
```
[BP_CHECK] Line 10: breakpoints={20}, step_mode=False, has_callback=True
[BP_CHECK] Line 20: breakpoints={20}, step_mode=False, has_callback=True
(no [BP_HIT] message)
```
❌ Problem: Condition on line 134 of interpreter.py failing
- Check: `has_callback=False` means callback is None
- Check: Logic error in condition

## Possible Root Causes

### 1. Breakpoints Not Being Set
**Check**: When you press 'b', does ● appear?
- If NO: Toggle breakpoint function not working
- If YES: Breakpoints are being set in `self.breakpoints`

### 2. Breakpoints Not Copied to Interpreter
**File**: `src/ui/curses_ui.py:592`
```python
self.interpreter.breakpoints = self.breakpoints.copy()
```
**Check**: Is `self.breakpoints` empty when this runs?
**Debug**: Add print statement:
```python
print(f"DEBUG: Copying breakpoints: {self.breakpoints}", file=sys.stderr)
self.interpreter.breakpoints = self.breakpoints.copy()
```

### 3. Breakpoint Callback Not Set
**File**: `src/ui/curses_ui.py:589`
```python
self.interpreter = Interpreter(self.runtime, capturing_io, breakpoint_callback=self._breakpoint_hit)
```
**Check**: Is `self._breakpoint_hit` actually passed?
**Debug**: Add to `_breakpoint_hit`:
```python
def _breakpoint_hit(self, line_number, stmt_index):
    import sys
    print(f"CALLBACK INVOKED for line {line_number}", file=sys.stderr)
    ...
```

### 4. Breakpoint Callback Returns Wrong Value
**Issue**: Callback must return `True` to continue or `False` to stop
**Current**: Returns `True` after 'c', `False` after 'e'
**Check**: Does callback complete and return?

## Quick Manual Check

Add this to `_run_program_capture()` before `self.interpreter.run()`:

```python
import sys
print(f"DEBUG: About to run with breakpoints={self.interpreter.breakpoints}", file=sys.stderr)
print(f"DEBUG: Callback is: {self.interpreter.breakpoint_callback}", file=sys.stderr)
```

Then run:
```bash
python3 mbasic --ui curses test_continue.bas 2>&1 | grep DEBUG
```

## Next Steps

1. **Run the debug test**: `./test_bp_debug.sh`
2. **Check the debug output**: Look for [BP_CHECK], [BP_HIT], [BP_RESULT]
3. **Identify which scenario** matches the output
4. **Report findings**: What did the debug output show?

## Expected Flow

When everything works correctly:

```
1. User sets breakpoint with 'b'
   → self.breakpoints.add(20)
   → Editor shows ●

2. User presses Ctrl+R
   → _run_program_capture() called
   → Creates interpreter with breakpoint_callback=self._breakpoint_hit
   → Copies: self.interpreter.breakpoints = self.breakpoints.copy()
   → Calls: self.interpreter.run()

3. Interpreter executes line 10
   → [BP_CHECK] Line 10: breakpoints={20}, ...
   → 10 not in {20}, continue

4. Interpreter executes line 20
   → [BP_CHECK] Line 20: breakpoints={20}, ...
   → 20 in {20}, condition TRUE
   → [BP_HIT] Calling breakpoint callback
   → self._breakpoint_hit(20, 0) called
   → Shows status, waits for input
   → User presses 'c'
   → Returns True
   → [BP_RESULT] Callback returned: True
   → Continue execution

5. Interpreter executes line 30
   → [BP_CHECK] Line 30: breakpoints={20}, ...
   → 30 not in {20}, continue
```

## If Debug Output Shows Nothing

If there's no debug output at all, it means:
- The program isn't running through the interpreter
- OR the DEBUG_BP environment variable isn't set
- OR stderr is being redirected somewhere else

Try:
```bash
DEBUG_BP=1 python3 -c "import os; print('DEBUG_BP =', os.environ.get('DEBUG_BP'))"
```

Should print: `DEBUG_BP = 1`

## Additional Debug Option

Add this at the START of `_breakpoint_hit`:
```python
def _breakpoint_hit(self, line_number, stmt_index):
    import sys
    print(f"\n\n*** BREAKPOINT HIT CALLED: line {line_number} ***\n\n", file=sys.stderr)
    sys.stderr.flush()
    ...
```

This will be VERY obvious if the callback is ever called.

---

**Run the debug test and report back what you see in the debug output!**
