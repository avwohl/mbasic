# Testing Checklist - Breakpoint Display Fix

## Quick Test (2 minutes)

```bash
./test_continue_fix.sh
```

## Manual Test Steps

### 1. Start IDE
```bash
python3 mbasic --ui curses test_continue.bas
```

### 2. Set Breakpoint
- Move cursor to line 20
- Press **'b'**
- Verify: **●** appears next to line 20

### 3. Run Program
- Press **Ctrl+R**
- Program starts executing

### 4. Check Display at Breakpoint ⭐ KEY TEST

When the breakpoint hits, verify you can see:

- [ ] **Editor window content** - Can you see the BASIC program lines?
- [ ] **Line numbers** - Can you see "10", "20", "30", etc.?
- [ ] **Breakpoint marker** - Can you see the **●** symbol?
- [ ] **Output window** - Can you see "Line 10" output?
- [ ] **Status line** - Does it say "BREAKPOINT at line 20..."?

**FAIL CONDITION**: If you see a mostly blank screen with only the status line, the fix didn't work.

**PASS CONDITION**: If you can see your program code AND the status line, the fix worked!

### 5. Test Continue Command
- Press **'c'**
- Verify: Program continues running
- Verify: More output appears in output window

### 6. Exit
- Press **Ctrl+Q**

## Expected vs. Actual

### Before Fix (BLANK SCREEN)
```
╔══════════════════════════════════════════════╗
║ BREAKPOINT at line 20 - Press 'c' continue  ║
╠══════════════════════════════════════════════╣
║                                              ║
║                                              ║
║              (blank)                         ║
║                                              ║
║                                              ║
╚══════════════════════════════════════════════╝
```

### After Fix (SCREEN VISIBLE) ✅
```
╔══════════════════════════════════════════════╗
║ BREAKPOINT at line 20 - Press 'c' continue  ║
╠══════════════════════════════════════════════╣
║  10 PRINT "Line 10"                          ║
║ ●20 PRINT "Line 20 - set breakpoint here"   ║
║  30 PRINT "Line 30"                          ║
║  40 PRINT "Line 40"                          ║
║────────────────────────────────────────────  ║
║ Output:                                      ║
║ Line 10                                      ║
╚══════════════════════════════════════════════╝
```

## Troubleshooting

### Still seeing blank screen?

1. **Check debug log**:
   ```bash
   python3 mbasic --ui curses test_continue.bas 2> /tmp/debug.log
   # Hit breakpoint
   # Exit
   cat /tmp/debug.log
   ```

2. **Check if exception occurred**:
   - Look for "Breakpoint display error" in debug.log
   - Look for Python tracebacks

3. **Try simple breakpoint first**:
   - Create a 3-line program
   - Set one breakpoint
   - See if screen is visible

### Screen flickers?

This is normal - npyscreen refreshing. Should stabilize quickly.

### Can't type 'c'?

- Check if cursor is blinking
- Try pressing 'c' multiple times
- Try 'C' (capital C)

### Program doesn't stop?

- Verify **●** marker is visible before running
- Breakpoint must be set BEFORE pressing Ctrl+R

## Success Criteria

✅ **PASS**: All five items in section 4 are checked
❌ **FAIL**: Cannot see editor content during breakpoint

## Report Results

Please report:
1. ✅ PASS or ❌ FAIL
2. What you saw (screenshot or description)
3. Any errors in debug log
4. Terminal type/size

## Additional Tests

### Test with Multiple Breakpoints
```bash
# Set breakpoints on lines 20, 40, 60
# Run with Ctrl+R
# At each breakpoint, verify screen is visible
# Press 'c' at each to continue
```

### Test Step Mode
```bash
# Set breakpoint on line 20
# Run with Ctrl+R
# At breakpoint, press 's' instead of 'c'
# Verify: Stops at line 30
# Verify: Screen still visible
# Press 's' again
# Verify: Stops at line 40
```

### Test End Command
```bash
# Set breakpoint on line 20
# Run with Ctrl+R
# At breakpoint, press 'e'
# Verify: Program stops immediately
# Verify: Partial output visible
```

## Automated Test (Future)

Would need expect/pexpect to automate:
```python
# Pseudo-code
launch_ide("test_continue.bas")
send_keys("b")  # Set breakpoint
send_keys("^R")  # Run
wait_for("BREAKPOINT")
screen_content = capture_screen()
assert "10 PRINT" in screen_content  # Verify code visible
send_keys("c")  # Continue
```

## Performance Check

- Breakpoint should pause within 0.1 seconds
- Display should refresh within 0.1 seconds
- Input should be responsive (no lag)

If slow, check:
- Terminal rendering speed
- System load
- npyscreen version

---

**Bottom Line**: When breakpoint hits, you should see your code. That's the whole point of the fix!
