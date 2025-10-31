# Test Coverage Matrix

**Last Updated:** 2025-10-30

## Summary

This document tracks which language features have automated tests in `basic/dev/tests_with_results/`.

**Current Status:**
- ✓ 7 tests passing
- 0 tests failing
- Many features have NO tests yet

## Test Results

Run tests with: `python3 utils/run_tests.py`

```
Results: 7 passed, 0 failed, 0 skipped
```

## Existing Tests

| Test File | Features Tested | Status |
|-----------|----------------|--------|
| test_data_read.bas | DATA, READ, RESTORE | ✓ PASS |
| test_deftypes.bas | DEFINT, DEFSNG, DEFDBL, DEFSTR, type suffixes, case insensitivity | ✓ PASS |
| test_gosub.bas | GOSUB, RETURN, recursion depth | ✓ PASS |
| test_operator_precedence.bas | Operator precedence, parentheses, arithmetic | ✓ PASS |
| test_simple.bas | PRINT, LET, basic variables | ✓ PASS |
| test_swap.bas | SWAP statement | ✓ PASS |
| test_while_wend.bas | WHILE/WEND, FOR/NEXT nesting | ✓ PASS |

## Feature Coverage

### ✓ Tested Features (have at least 1 test)

- **Variables & Types:**
  - ✓ DEFINT/DEFSNG/DEFDBL/DEFSTR (1 test)
  - ✓ Type suffixes (%, $, !, #) (1 test)
  - ✓ Variable assignment (1 test)
  - ✓ Case insensitivity (1 test)

- **Arithmetic & Math:**
  - ✓ Operator precedence (1 test)
  - ✓ Basic arithmetic (+, -, *, /, ^) (1 test)

- **Control Flow:**
  - ✓ GOSUB/RETURN (1 test)
  - ✓ FOR/NEXT (1 test)
  - ✓ WHILE/WEND (1 test)
  - ✓ Nested loops (1 test)

- **I/O:**
  - ✓ PRINT (1 test)
  - ✓ DATA/READ/RESTORE (1 test)

- **Statements:**
  - ✓ SWAP (1 test)

### ⚠️ Partially Tested (need more tests - only 1 test per feature)

ALL of the above features need at least 1-2 more tests for edge cases.

### ❌ NOT Tested (need tests urgently)

#### Control Flow
- ❌ GOTO
- ❌ IF/THEN/ELSE
- ❌ ON GOTO
- ❌ ON GOSUB

#### Arithmetic & Math
- ❌ MOD operator
- ❌ Integer division (\)
- ❌ Math functions (SIN, COS, TAN, ATN, EXP, LOG, SQR, ABS, SGN, INT, FIX, CINT)
- ❌ RND (random numbers)

#### String Operations
- ❌ String functions (LEFT$, RIGHT$, MID$, LEN, ASC, CHR$, STR$, VAL)
- ❌ String concatenation (+)
- ❌ INSTR (find substring)
- ❌ SPACE$, STRING$

#### Variables & Types
- ❌ DIM (arrays)
- ❌ Multi-dimensional arrays
- ❌ Array bounds
- ❌ OPTION BASE

#### I/O
- ❌ INPUT
- ❌ LINE INPUT
- ❌ PRINT USING (format codes)
- ❌ FILE operations (OPEN, CLOSE, PRINT#, INPUT#, LINE INPUT#)
- ❌ LPRINT (printer output)
- ❌ INKEY$ (keyboard input)

#### User-Defined
- ❌ DEF FN (user-defined functions)
- ❌ Function parameters
- ❌ Multiple functions

#### Program Control
- ❌ RUN
- ❌ STOP
- ❌ END
- ❌ CONT
- ❌ CLEAR
- ❌ NEW

#### Debugging
- ❌ TRON/TROFF (trace execution)
- ❌ Error handling (ON ERROR GOTO, RESUME, ERL, ERR)

#### Advanced Features
- ❌ PEEK/POKE (memory access)
- ❌ CALL (assembly language)
- ❌ OUT/INP (port I/O)
- ❌ WAIT (wait for port condition)

## Priority for New Tests

### HIGH PRIORITY (critical language features)

1. **IF/THEN/ELSE** - Most basic control flow, needs multiple tests
2. **INPUT** - Essential for interactive programs
3. **DIM** - Arrays are fundamental
4. **String functions** - LEFT$, RIGHT$, MID$, LEN at minimum
5. **Math functions** - SIN, COS, SQR, ABS, INT at minimum
6. **Error handling** - ON ERROR GOTO, RESUME
7. **GOTO** - Basic control flow

### MEDIUM PRIORITY (common features)

1. **DEF FN** - User-defined functions
2. **PRINT USING** - Formatted output
3. **File I/O** - OPEN, CLOSE, PRINT#, INPUT#
4. **ON GOTO/ON GOSUB** - Computed jumps
5. **More DEFINT tests** - Edge cases, ranges
6. **String concatenation** - Common operation
7. **RND** - Random numbers for games

### LOW PRIORITY (advanced or less common)

1. **PEEK/POKE** - Memory access
2. **CALL** - Assembly calls
3. **OUT/INP** - Port I/O
4. **WAIT** - Port waiting
5. **TRON/TROFF** - Trace mode
6. **LPRINT** - Printer output

## Test Writing Guidelines

1. **File location:** `basic/dev/tests_with_results/`
2. **Naming:** `test_<feature>.bas`
3. **Expected output:** `test_<feature>.txt`
4. **Structure:**
   - Start with REM explaining what's tested
   - PRINT clear test descriptions
   - Test multiple cases/edge conditions
   - PRINT "PASS" or "FAIL" for each test
   - END at the end

5. **Make tests non-interactive:**
   - Avoid INPUT unless testing INPUT itself
   - Use DATA/READ instead of INPUT where possible
   - Tests should run to completion automatically

6. **Expected output:**
   - Generate with: `python3 mbasic --backend cli test.bas > test.txt`
   - Strip out prompt lines (MBASIC-, Ready, etc.) - run_tests.py does this
   - Verify output is correct before committing

## Next Steps

1. ✓ Create automated test runner (utils/run_tests.py)
2. ✓ Update expected outputs for current behavior
3. ⏳ Add high-priority missing tests (IF/THEN, INPUT, DIM, strings, math)
4. ⏳ Add second test for each partially-tested feature
5. ⏳ Add medium-priority tests
6. ⏳ Document test results in CI/CD

## See Also

- Test files: `basic/dev/tests_with_results/`
- Test runner: `utils/run_tests.py`
- Language features: `docs/dev/STATUS.md`
- TODO: `docs/dev/LANGUAGE_TESTING_TODO.md`
