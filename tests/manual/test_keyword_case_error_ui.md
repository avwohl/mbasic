# Manual Test: Keyword Case Error Display in UIs

**Purpose:** Verify that keyword case conflicts are properly displayed in all UIs when `keywords.case_style` is set to `error`.

## Setup

1. Set the keyword case policy to 'error':
   ```
   SET keywords.case_style error
   ```

2. Verify the setting:
   ```
   SHOW SETTINGS keywords
   ```

   Should show: `keywords.case_style = error`

## Test Program

Use this test program (save as `test_case_error.bas`):

```basic
10 PRINT "First line - uppercase"
20 print "Second line - lowercase"
30 PRINT "Third line - uppercase again"
```

## Expected Behavior

When loading or running this program with `keywords.case_style = error`:

**Error should be raised:**
- Error message: `Case conflict: 'print' at line 2:X vs 'PRINT' at line 1:X`
- Line numbers should be accurate
- Column positions may vary but should point to the keyword

## Test Cases

### Test 1: TK UI - Load Program

1. Launch TK UI: `python3 mbasic.py --tk`
2. Set policy: Menu → Commands → type `SET keywords.case_style error`
3. File → Open → select `test_case_error.bas`
4. **Expected:** Error displayed in output area:
   - "Parse error: Case conflict: 'print' at line 2:4 vs 'PRINT' at line 1:4"
   - Status bar shows "Parse error - fix and retry"

### Test 2: TK UI - Type Program

1. Launch TK UI: `python3 mbasic.py --tk`
2. Set policy: `SET keywords.case_style error`
3. Type the test program line by line
4. Try to run (Run → Run or F5)
5. **Expected:** Same error as Test 1

### Test 3: Curses UI - Load Program

1. Launch curses UI: `python3 mbasic.py --curses`
2. Set policy: `SET keywords.case_style error`
3. Load program
4. **Expected:** Error displayed appropriately in curses UI

### Test 4: CLI Mode - Direct Execution

1. Run from command line:
   ```bash
   python3 -c "
   from src.settings import set as settings_set
   settings_set('keywords.case_style', 'error')

   from src.lexer import tokenize
   code = '''10 PRINT \"test\"
   20 print \"test\"'''

   tokenize(code)
   "
   ```

2. **Expected:** Traceback with ValueError:
   ```
   ValueError: Case conflict: 'print' at line 2:4 vs 'PRINT' at line 1:4
   ```

### Test 5: No Error When Consistent

Use this program (all uppercase):

```basic
10 PRINT "First"
20 PRINT "Second"
30 PRINT "Third"
```

1. With `keywords.case_style = error`
2. Load and run this program
3. **Expected:** No errors, program runs normally

### Test 6: Other Policies Still Work

Test each policy with mixed-case program:

```basic
10 PRINT "test"
20 print "test"
30 Print "test"
```

**Policies to test:**
- `force_lower` - Should work, convert all to lowercase
- `force_upper` - Should work, convert all to UPPERCASE
- `force_capitalize` - Should work, convert all to Capitalize
- `first_wins` - Should work, use first occurrence's case
- `preserve` - Should work, keep each as typed

All should run without errors (only 'error' policy raises errors).

## Verification Checklist

- [ ] Error message includes both conflicting cases
- [ ] Error message includes line numbers
- [ ] Error message includes column positions
- [ ] Error occurs during parsing (before execution)
- [ ] Error is caught and displayed in UI (not crash)
- [ ] Error message is clear and actionable
- [ ] Other policies still work correctly
- [ ] Programs with consistent case work with 'error' policy

## Known Limitations

- Column positions in error message start from beginning of line (0-indexed)
- Error only detects first conflict, not all conflicts
- Error is raised during tokenization, before parsing

## Success Criteria

✅ All test cases pass
✅ Error messages are clear and helpful
✅ No crashes or unhandled exceptions
✅ Other policies unaffected
