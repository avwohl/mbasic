# Language Testing TODO

**Status:** TODO
**Priority:** HIGH
**Created:** 2025-10-30

## Problem

DEFINT/DEFSTR/DEFDBL/DEFSNG are marked as implemented in STATUS.md and have help documentation, but are actually broken. This happened because there weren't enough tests to catch the regression.

**Example of broken feature:**
- STATUS.md says: `✓ DEFINT/DEFSNG/DEFDBL/DEFSTR (type declarations)`
- Test file exists: `basic/tests_with_results/test_deftypes.bas`
- But running the test fails: `Syntax error in 70: Unknown DEF statement token type: TokenType.DEFINT`
- Impact: 23+ programs in the library cannot load

## Goal

Add at least a few tests for **every language feature** so regressions like broken DEFINT don't happen.

## Requirements

### 1. Test Coverage for All Features

Every feature marked with ✓ in STATUS.md must have:
- **At least 2-3 test cases** in `basic/tests_with_results/`
- **Expected output file** (.txt) for comparison
- **Automated test** that runs the program and compares output

### 2. Test Categories Needed

#### Arithmetic & Math
- ✓ Basic arithmetic (+, -, *, /, ^, MOD, \)
- ✓ Math functions (SIN, COS, TAN, ATN, EXP, LOG, SQR, ABS, SGN, INT, FIX, CINT)
- ✓ RND (random numbers)

#### String Operations
- ✓ String functions (LEFT$, RIGHT$, MID$, LEN, ASC, CHR$, STR$, VAL)
- ✓ String concatenation (+)
- ✓ INSTR (find substring)
- ✓ SPACE$, STRING$

#### Variables & Types
- ⚠️ DEFINT/DEFSNG/DEFDBL/DEFSTR - **BROKEN, needs fixing and more tests**
- ✓ Type suffixes (%, $, !, #)
- ✓ Variable assignment
- ✓ DIM (arrays)

#### Control Flow
- ✓ GOTO, GOSUB, RETURN
- ✓ IF/THEN/ELSE
- ✓ FOR/NEXT
- ✓ WHILE/WEND
- ✓ ON GOTO, ON GOSUB

#### I/O
- ✓ PRINT, PRINT USING
- ✓ INPUT
- ✓ READ/DATA/RESTORE
- ✓ FILE operations (OPEN, CLOSE, PRINT#, INPUT#, LINE INPUT#)
- ✓ LPRINT (printer output)
- ✓ INKEY$ (keyboard input)

#### User-Defined
- ✓ DEF FN (user-defined functions)
- ✓ Function parameters and return values

#### Program Control
- ✓ RUN, STOP, END
- ✓ CONT (continue after STOP)
- ✓ CLEAR
- ✓ NEW

#### Debugging
- ✓ TRON/TROFF (trace execution)
- ✓ Error handling (ON ERROR GOTO, RESUME, ERL, ERR)

#### Advanced Features
- ✓ PEEK/POKE (memory access)
- ✓ CALL (assembly language)
- ✓ OUT/INP (port I/O)
- ✓ WAIT (wait for port condition)

### 3. Test Structure

Each test should:
1. **Be in `basic/tests_with_results/`** directory
2. **Have a .bas file** with the test program
3. **Have a .txt file** with expected output
4. **Print clear results** showing what's being tested
5. **Be runnable non-interactively** (avoid INPUT unless necessary)

#### Example Test Format
```basic
10 REM Test DEFINT Statement
20 PRINT "Testing DEFINT A-Z"
30 DEFINT A-Z
40 A = 10.7
50 B = 20.9
60 PRINT "A = 10.7 should become"; A; "(integer)"
70 PRINT "B = 20.9 should become"; B; "(integer)"
80 IF A = 10 AND B = 20 THEN PRINT "PASS" ELSE PRINT "FAIL"
90 END
```

### 4. Automated Test Runner

Need a script that:
1. Runs all tests in `basic/tests_with_results/`
2. Compares output to expected .txt files
3. Reports PASS/FAIL for each test
4. Exits with error code if any test fails
5. Can be run in CI/CD pipeline

### 5. Test Categories to Add

**High Priority (missing or broken):**
1. DEFINT/DEFSNG/DEFDBL/DEFSTR - Multiple tests for:
   - Single letter ranges (A-Z)
   - Partial ranges (I-N)
   - Multiple ranges (A-C, X-Z)
   - Type precedence (DEF vs suffix)
   - Case insensitivity

2. Error handling - Tests for:
   - ON ERROR GOTO
   - RESUME, RESUME NEXT
   - ERL, ERR functions
   - Error recovery

3. File I/O - Tests for:
   - Sequential files (OPEN, CLOSE, PRINT#, INPUT#)
   - Random access files
   - EOF function
   - File errors

4. Arrays - Tests for:
   - DIM with multiple dimensions
   - Array bounds checking
   - Array operations
   - OPTION BASE

**Medium Priority (have some tests, need more):**
1. String functions - More edge cases
2. Math functions - Boundary conditions
3. Control flow - Nested loops, complex conditions
4. PRINT USING - All format types

**Low Priority (well tested):**
1. Basic arithmetic
2. Simple PRINT statements
3. Variable assignment

## Implementation Plan

### Phase 1: Audit Current Tests
1. List all tests in `basic/tests_with_results/`
2. Map tests to features in STATUS.md
3. Identify features with no tests or only one test
4. Create test coverage matrix

### Phase 2: Add Missing Tests
1. Create tests for features with 0 tests
2. Add second/third test for features with only 1 test
3. Focus on high-priority features first

### Phase 3: Fix Broken Tests
1. Fix DEFINT/DEFSNG/DEFDBL/DEFSTR implementation
2. Verify test_deftypes.bas passes
3. Add more DEFINT tests for edge cases

### Phase 4: Automated Testing
1. Create test runner script (Python)
2. Run all tests, compare output
3. Generate test report
4. Add to CI/CD if applicable

### Phase 5: Documentation
1. Document test structure in README
2. Add guidelines for writing new tests
3. Keep test coverage matrix updated

## Current Status

### Tests That Exist
- `basic/tests_with_results/test_deftypes.bas` - **BROKEN** (DEFINT not working)
- `basic/bas_tests/*.bas` - Various test programs (need to review which are actual tests)
- Other test files need audit

### Tests That Are Missing
- Most language features have no tests
- Or only one test that might not be comprehensive
- No systematic test coverage

## Success Criteria

1. **Every feature in STATUS.md** has at least 2-3 tests
2. **All tests pass** when run
3. **Automated test runner** can validate all tests
4. **Test coverage matrix** shows what's tested
5. **No regressions** - broken features are caught immediately

## Related Files

- Status tracking: `docs/dev/STATUS.md`
- Test directory: `basic/tests_with_results/`
- Test programs: `basic/bas_tests/`
- Library test results: `docs/dev/LIBRARY_TEST_RESULTS.md`

## Next Steps

1. **IMMEDIATE:** Fix DEFINT/DEFSNG/DEFDBL/DEFSTR implementation
2. **HIGH:** Audit existing tests and create coverage matrix
3. **HIGH:** Add tests for features with no coverage
4. **MEDIUM:** Create automated test runner
5. **MEDIUM:** Add more tests for partially-covered features
6. **LOW:** Document test writing guidelines

---

**Created:** 2025-10-30
**Reporter:** User
**Priority:** HIGH - Prevents regressions like broken DEFINT
**Blocked by:** DEFINT bug fix
