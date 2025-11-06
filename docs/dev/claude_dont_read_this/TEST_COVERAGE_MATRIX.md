# Test Coverage Matrix

**Last Updated:** 2025-10-31

## Summary

This document tracks which language features have automated tests in `basic/dev/tests_with_results/` and `tests/`.

**Current Status:**
- ✓ **36 language feature tests** passing (automated BASIC programs)
- ✓ **17 interactive command tests** in CLI test suite (pexpect automation)
- ✓ **0 tests failing**
- ✓ **Complete coverage** of all implemented MBASIC 5.21 features

**What's Tested:**
- ✅ All control flow (IF/THEN, FOR/NEXT, WHILE/WEND, GOTO, GOSUB, etc.)
- ✅ All math and string functions
- ✅ All operators (arithmetic, logical, relational)
- ✅ All I/O (PRINT, INPUT, file operations)
- ✅ All type features (DEFINT/DEFSNG/DEFDBL/DEFSTR, arrays, conversions)
- ✅ Error handling (ON ERROR, RESUME, ERR, ERL)
- ✅ Program management (CHAIN, MERGE)
- ✅ All interactive commands (RUN, LIST, SAVE, LOAD, NEW, DELETE, RENUM, EDIT, AUTO, CLEAR, FILES, CONT)
- ✅ Memory compatibility (PEEK returns random 0-255 for RND seeding)

**What's Not Implemented (cannot test):**
- ❌ EQV, IMP logical operators
- ❌ RANDOMIZE statement
- ❌ Hardware features (POKE, CALL, OUT/INP, WAIT, LPRINT)

## Test Results

Run tests with: `python3 utils/run_tests.py`

```
Results: 36 passed, 0 failed, 0 skipped
```

## Existing Tests

| Test File | Features Tested | Status |
|-----------|----------------|--------|
| test_binary_conversion.bas | CVI, CVS, CVD, MKI$, MKS$, MKD$ binary conversion | ✓ PASS |
| test_chain.bas | CHAIN statement, ALL flag, variable preservation | ✓ PASS |
| test_data_read.bas | DATA, READ, RESTORE | ✓ PASS |
| test_def_fn.bas | DEF FN, user-defined functions, string functions, nested calls | ✓ PASS |
| test_deftypes.bas | DEFINT, DEFSNG, DEFDBL, DEFSTR, type suffixes, case insensitivity | ✓ PASS |
| test_dim_arrays.bas | DIM, single & multi-dimensional arrays, array access | ✓ PASS |
| test_erase.bas | ERASE statement, array clearing, re-dimensioning | ✓ PASS |
| test_error_handling.bas | ON ERROR GOTO, ON ERROR GOSUB, RESUME, RESUME NEXT, ERR, ERL | ✓ PASS |
| test_file_io.bas | OPEN, CLOSE, PRINT#, INPUT#, LINE INPUT#, WRITE#, EOF, KILL | ✓ PASS |
| test_for_next.bas | FOR/NEXT, STEP, negative STEP, nested loops, decimal STEP | ✓ PASS |
| test_gosub.bas | GOSUB, RETURN, recursion depth | ✓ PASS |
| test_goto.bas | GOTO, computed GOTO, line branching | ✓ PASS |
| test_hex_oct.bas | HEX$ and OCT$ conversion functions | ✓ PASS |
| test_if_then_else.bas | IF/THEN/ELSE, nested conditions, relational operators | ✓ PASS |
| test_inkey.bas | INKEY$ keyboard input (returns empty in non-TTY) | ✓ PASS |
| test_input.bas | INPUT functionality (simulated with DATA/READ) | ✓ PASS |
| test_logical_ops.bas | AND, OR, XOR, NOT logical operators, bitwise operations | ✓ PASS |
| test_math_functions.bas | ABS, SQR, SIN, COS, TAN, ATN, EXP, LOG, SGN | ✓ PASS |
| test_merge.bas | MERGE statement, program overlays, adding subroutines | ✓ PASS |
| test_mid_assignment.bas | MID$ in-place string modification | ✓ PASS |
| test_mod_intdiv.bas | MOD operator and integer division (\) | ✓ PASS |
| test_on_goto_gosub.bas | ON GOTO, ON GOSUB, computed branching with expressions | ✓ PASS |
| test_operator_precedence.bas | Operator precedence, parentheses, arithmetic | ✓ PASS |
| test_option_base.bas | OPTION BASE 1 for arrays | ✓ PASS |
| test_peek.bas | PEEK function returns random 0-255 for RND seeding | ✓ PASS |
| test_print_using.bas | PRINT USING, format strings, currency, decimals, strings | ✓ PASS |
| test_random_files.bas | FIELD, LSET, RSET, PUT, GET random access files | ✓ PASS |
| test_rnd.bas | RND function, random number generation, range validation | ✓ PASS |
| test_rounding.bas | INT, FIX, CINT, banker's rounding, integer type suffix | ✓ PASS |
| test_simple.bas | PRINT, LET, basic variables | ✓ PASS |
| test_string_functions.bas | LEFT$, RIGHT$, MID$, LEN, ASC, CHR$, STR$, VAL, INSTR, SPACE$, STRING$ | ✓ PASS |
| test_swap.bas | SWAP statement | ✓ PASS |
| test_tab_spc.bas | TAB and SPC formatting functions | ✓ PASS |
| test_tron_troff.bas | TRON/TROFF trace mode (line & statement level) | ✓ PASS |
| test_type_conversion.bas | CINT, CSNG, CDBL, STR$, VAL type conversion | ✓ PASS |
| test_while_wend.bas | WHILE/WEND, FOR/NEXT nesting | ✓ PASS |

## Feature Coverage

### ✅ Comprehensively Tested Features

All major MBASIC 5.21 language features now have complete test coverage:

#### Control Flow (100% Covered)
- ✅ IF/THEN/ELSE - test_if_then_else.bas
- ✅ GOTO - test_goto.bas
- ✅ GOSUB/RETURN - test_gosub.bas
- ✅ ON GOTO - test_on_goto_gosub.bas
- ✅ ON GOSUB - test_on_goto_gosub.bas
- ✅ FOR/NEXT with STEP - test_for_next.bas
- ✅ WHILE/WEND - test_while_wend.bas
- ✅ END - Multiple tests

#### Arithmetic & Math (100% Covered)
- ✅ Operator precedence - test_operator_precedence.bas
- ✅ Basic arithmetic (+, -, *, /, ^) - test_operator_precedence.bas
- ✅ MOD operator - test_mod_intdiv.bas
- ✅ Integer division (\) - test_mod_intdiv.bas
- ✅ Math functions (SIN, COS, TAN, ATN, EXP, LOG, SQR, ABS, SGN) - test_math_functions.bas
- ✅ Rounding functions (INT, FIX, CINT) - test_rounding.bas
- ✅ RND random numbers - test_rnd.bas

#### String Operations (100% Covered)
- ✅ String functions (LEFT$, RIGHT$, MID$, LEN) - test_string_functions.bas
- ✅ String conversion (ASC, CHR$, STR$, VAL) - test_string_functions.bas, test_type_conversion.bas
- ✅ String concatenation (+) - test_string_functions.bas
- ✅ INSTR (find substring) - test_string_functions.bas
- ✅ SPACE$, STRING$ - test_string_functions.bas
- ✅ MID$ assignment - test_mid_assignment.bas

#### Variables & Types (100% Covered)
- ✅ Variable assignment - test_simple.bas
- ✅ Type suffixes (%, $, !, #) - test_deftypes.bas
- ✅ DEFINT/DEFSNG/DEFDBL/DEFSTR - test_deftypes.bas
- ✅ Type conversion (CINT, CSNG, CDBL) - test_type_conversion.bas
- ✅ DIM (arrays) - test_dim_arrays.bas
- ✅ Multi-dimensional arrays - test_dim_arrays.bas
- ✅ OPTION BASE - test_option_base.bas
- ✅ ERASE - test_erase.bas
- ✅ SWAP - test_swap.bas

#### Data Management (100% Covered)
- ✅ DATA/READ/RESTORE - test_data_read.bas
- ✅ INPUT - test_input.bas (simulated with DATA/READ)
- ✅ INKEY$ - test_inkey.bas (keyboard polling, returns empty in non-TTY)

#### I/O Operations (100% Covered)
- ✅ PRINT - Multiple tests
- ✅ PRINT USING - test_print_using.bas
- ✅ TAB/SPC - test_tab_spc.bas
- ✅ Sequential file I/O (OPEN, CLOSE, PRINT#, INPUT#, LINE INPUT#, WRITE#, EOF, KILL) - test_file_io.bas
- ✅ Random access files (OPEN "R", FIELD, LSET, RSET, PUT, GET) - test_random_files.bas

#### User-Defined Features (100% Covered)
- ✅ DEF FN - test_def_fn.bas
- ✅ Function parameters - test_def_fn.bas
- ✅ Multiple functions - test_def_fn.bas

#### Error Handling (100% Covered)
- ✅ ON ERROR GOTO - test_error_handling.bas
- ✅ ON ERROR GOSUB - test_error_handling.bas
- ✅ RESUME, RESUME NEXT - test_error_handling.bas
- ✅ ERR, ERL - test_error_handling.bas

#### Debugging (100% Covered)
- ✅ TRON/TROFF - test_tron_troff.bas (line & statement level)

#### Logical Operators (100% Covered)
- ✅ AND, OR, XOR, NOT - test_logical_ops.bas
- ✅ Bitwise operations - test_logical_ops.bas

#### Conversion Functions (100% Covered)
- ✅ HEX$, OCT$ - test_hex_oct.bas
- ✅ Binary conversion (CVI, CVS, CVD, MKI$, MKS$, MKD$) - test_binary_conversion.bas

#### Program Management (100% Covered)
- ✅ CHAIN - test_chain.bas (with ALL flag, variable preservation)
- ✅ MERGE - test_merge.bas (program overlays, subroutine loading)

#### Interactive Commands (100% Covered via CLI automation - see INTERACTIVE_COMMAND_TEST_COVERAGE.md)
- ✅ RUN, LIST, SAVE, LOAD, NEW, DELETE, RENUM, EDIT, AUTO - tests/test_cli_comprehensive.py
- ✅ CONT (continue from breakpoint) - tests/test_continue.sh
- ✅ CLEAR (session state) - tests/test_cli_comprehensive.py
- ✅ FILES (directory listing) - tests/test_cli_comprehensive.py

#### Memory/Hardware Functions (Tested/No-Op/Not Applicable)
- ✅ PEEK - test_peek.bas (returns random 0-255 for RND seeding)
- ❌ POKE - No-op (memory write not supported)
- ❌ CALL - No-op (assembly language not supported)
- ❌ OUT/INP - No-op (port I/O not supported)
- ❌ WAIT - No-op (port waiting not supported)
- ❌ LPRINT - No-op (printer output not supported)

### 🔴 Features Not Yet Implemented

These features are parsed but not yet implemented in the interpreter (will throw NotImplementedError):

⚠️ **IMPORTANT:** Need to verify these are actually in MBASIC 5.21 (see `docs/dev/MISSING_OPERATORS_TODO.md`)

- **EQV** - Logical equivalence operator (parsed, not executed - may not be in MBASIC 5.21)
- **IMP** - Logical implication operator (parsed, not executed - may not be in MBASIC 5.21)
- **RANDOMIZE** - RNG seeding statement (parsed, not executed - may not be in MBASIC 5.21, use PEEK(0) instead)


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
   - Generate with: `python3 mbasic --ui cli test.bas > test.txt`
   - Strip out prompt lines (MBASIC-, Ready, etc.) - run_tests.py does this
   - Verify output is correct before committing

## Future Enhancements

All testing is complete for implemented features. Potential future work:

1. **Verify & implement missing operators** - Verify EQV/IMP are in MBASIC 5.21, then implement and add tests
2. **Verify & implement RANDOMIZE** - Verify RANDOMIZE is in MBASIC 5.21, then implement and add tests
3. **CI/CD Integration** - Add test suite to continuous integration pipeline

## See Also

- **Language test files:** `basic/dev/tests_with_results/` (36 automated BASIC tests)
- **Language test runner:** `utils/run_tests.py`
- **Interactive command tests:** `tests/` directory (CLI automation with pexpect)
- **Interactive test coverage:** `docs/dev/INTERACTIVE_COMMAND_TEST_COVERAGE.md`
- **Language features status:** `docs/dev/STATUS.md`
- **Testing completion:** `docs/history/LANGUAGE_TESTING_DONE.md`
- **Missing operators TODO:** `docs/dev/MISSING_OPERATORS_TODO.md` (EQV, IMP, RANDOMIZE - need verification)
