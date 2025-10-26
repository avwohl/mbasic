# Tests With Expected Results

This directory contains MBASIC 5.21 test programs with their expected output.

## Purpose

Unlike the programs in `bas_tests1/`, which are real-world programs we found but don't know the expected output for, these are **test cases** where we know exactly what the correct output should be.

## Format

For each test:
- **`test_name.bas`** - The MBASIC program
- **`test_name.txt`** - The expected output when the program is run

## Running Tests

To validate the interpreter/compiler:
1. Run the `.bas` file
2. Compare the output to the `.txt` file
3. Output should match exactly (or within acceptable floating-point tolerance)

## Current Tests

### test_operator_precedence.bas

Tests operator precedence to ensure operations are performed in the correct order.

**How it works:**
- The program itself checks each result and reports PASS/FAIL
- Each test assigns `RESULT = expression` and `EXPECTED = correct_value`
- A subroutine checks if RESULT equals EXPECTED
- Tracks pass/fail counts and prints summary at end

**Key test cases:**
- `3*3+1` should be 10, not 12 (multiplication before addition)
- `10-8/2` should be 6, not 1 (division before subtraction)
- `2*3^2` should be 18, not 36 (exponentiation before multiplication)
- `10\3+1` should be 4, not 3 (integer division before addition)
- `10 MOD 3+1` should be 2, not 0 (MOD before addition)
- `-2^2` should be -4, not 4 (exponentiation before negation)
- `0 OR 1 AND 0` should be 0, not 1 (AND before OR)
- And 13 more tests...

**MBASIC Operator Precedence (highest to lowest):**
1. Parentheses `()`
2. Exponentiation `^`
3. Negation (unary `-`)
4. Multiplication `*`, Division `/`, Integer Division `\`
5. Modulo `MOD`
6. Addition `+`, Subtraction `-`
7. Relational `=`, `<>`, `<`, `>`, `<=`, `>=`
8. Logical NOT
9. Logical AND
10. Logical OR
11. Logical XOR
12. Logical EQV
13. Logical IMP

**Note:** In MBASIC, TRUE is -1 and FALSE is 0.

### test_gosub.bas

Tests nested GOSUB/RETURN subroutine calls.

**What it tests:**
- Subroutine calls with GOSUB
- Proper RETURN to calling location
- Nested subroutines (up to 10 levels deep)
- GOSUB stack management

**How it works:**
- Calls subroutine at line 1000
- Each subroutine increments depth counter and calls next subroutine
- Tests that RETURN properly unwinds the call stack
- Verifies final depth value

### test_while_wend.bas

Tests WHILE/WEND loop constructs with nested FOR loops.

**What it tests:**
- WHILE condition evaluation
- WEND properly closes WHILE loop
- FOR loop nested inside WHILE loop
- Loop variable updates

**How it works:**
- Outer WHILE loop runs while J < 2
- Inner FOR loop runs from 1 to 3
- Tests proper nesting and loop completion

### test_data_read.bas

Tests DATA/READ/RESTORE statements.

**What it tests:**
- READ statement reads from DATA
- DATA statement stores values
- RESTORE resets data pointer to beginning
- String data handling

**How it works:**
- Uses READ in FOR loop to read 3 color names
- Uses RESTORE to reset data pointer
- Reads first value again to verify RESTORE works

### test_swap.bas

Tests SWAP statement for both numeric and string variables.

**What it tests:**
- SWAP exchanges values of two numeric variables
- SWAP exchanges values of two string variables
- Variable values properly updated after SWAP

**How it works:**
- Sets A=10, B=20, then swaps them
- Sets X$="HELLO", Y$="WORLD", then swaps them
- Prints before and after values to verify swap occurred

## Adding New Tests

When adding new tests:
1. Create a descriptive test name (e.g., `test_string_functions.bas`)
2. Add comments explaining what each test validates
3. Create the corresponding `.txt` file with exact expected output
4. Update this README with a description of the new test
