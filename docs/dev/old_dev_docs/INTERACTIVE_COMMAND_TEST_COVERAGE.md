# Interactive Command Test Coverage

**Last Updated:** 2025-10-31

This document tracks test coverage for interactive/session management commands that are not suitable for automated BASIC program tests (in `basic/dev/tests_with_results/`).

## Summary

Interactive commands are tested via CLI automation tests using pexpect, shell scripts, and UI-specific test frameworks.

## Test Coverage Status

### ✅ Fully Tested Commands (12/12 = 100%)

These commands have comprehensive automated tests in the `tests/` directory:

| Command | Test File | Test Type | Description |
|---------|-----------|-----------|-------------|
| **RUN** | `tests/test_cli_comprehensive.py` | pexpect | Tests running programs from CLI |
| **LIST** | `tests/test_cli_comprehensive.py` | pexpect | Tests listing program lines |
| **SAVE** | `tests/test_cli_comprehensive.py` | pexpect | Tests saving programs to files |
| **LOAD** | `tests/test_cli_comprehensive.py` | pexpect | Tests loading programs from files |
| **NEW** | `tests/test_cli_comprehensive.py` | pexpect | Tests clearing program memory |
| **DELETE** | `tests/test_cli_comprehensive.py` | pexpect | Tests deleting program lines |
| **RENUM** | `tests/test_cli_comprehensive.py` | pexpect | Tests renumbering program lines |
| **EDIT** | `tests/test_cli_comprehensive.py` | pexpect | Tests editing program lines |
| **AUTO** | `tests/test_cli_comprehensive.py` | pexpect | Tests automatic line numbering |
| **CLEAR** | `tests/test_cli_comprehensive.py` | pexpect | Tests clearing variables/session state |
| **FILES** | `tests/test_cli_comprehensive.py` | pexpect | Tests directory listing |
| **CONT** | `tests/test_continue.sh`, `tests/test_simple_continue.py` | pexpect/curses | Tests continue from breakpoint |

## Test Files Overview

### Primary Test File: `tests/test_cli_comprehensive.py`

Comprehensive pexpect-based test suite for CLI backend covering:

**Tests Included:**
1. `test_new_command()` - NEW command clears program
2. `test_line_entry()` - Entering program lines (10, 20, 30)
3. `test_run_command()` - RUN command execution
4. `test_immediate_mode()` - Immediate mode (PRINT 2+2, etc.)
5. `test_delete_command()` - DELETE single line
6. `test_edit_command()` - EDIT command to modify line
7. `test_renum_command()` - RENUM with non-standard numbering (5, 17, 99 → 10, 20, 30)
8. `test_save_load()` - SAVE and LOAD roundtrip
9. `test_auto_command()` - AUTO mode for line entry
10. `test_clear_command()` - CLEAR command resets variables
11. `test_files_command()` - FILES command lists directory
12. `test_error_handling()` - Syntax errors and error messages
13. `test_help_system()` - HELP command and HELP SEARCH
14. `test_variables()` - Variable operations in immediate mode
15. `test_multistatement_lines()` - Multi-statement lines with colons
16. `test_for_loop()` - FOR/NEXT loop execution
17. `test_gosub_return()` - GOSUB/RETURN subroutine calls

**How to Run:**
```bash
cd tests
python3 test_cli_comprehensive.py
```

### CONT (Continue) Tests

**Test Files:**
- `tests/test_continue.sh` - Shell script with pexpect test for breakpoint continuation
- `tests/test_simple_continue.py` - Simple continue test for Curses UI
- `tests/test_continue_fix.sh` - Continue fix verification
- `tests/test_continue_manual.sh` - Manual testing instructions

**What's Tested:**
- Setting breakpoints on lines 20 and 40
- Running program and hitting first breakpoint
- Pressing 'c' to continue to next breakpoint
- Continuing to program completion
- Verifies breakpoint handler is called

**How to Run:**
```bash
cd tests
./test_continue.sh
# or
python3 test_simple_continue.py
```

### Other Related Tests

**Breakpoint Tests:**
- `tests/test_breakpoint_comprehensive.py` - Comprehensive breakpoint testing
- `tests/test_breakpoint_pexpect.py` - Pexpect-based breakpoint tests
- `tests/test_bp_simple.sh`, `test_bp_simple2.sh` - Simple breakpoint shell tests

**UI-Specific Tests:**
- `tests/test_all_ui_features.py` - Tests all UI features across backends
- `tests/test_recent_files.py` - Recent files list management
- `tests/regression/commands/test_renum_spacing.py` - RENUM edge cases

## All Tests Complete! ✅

All 12 interactive commands now have comprehensive automated tests.

## Integration with Language Tests

The tests in `basic/dev/tests_with_results/` focus on **language features** (FOR/NEXT, PRINT USING, etc.) that work in **program mode**.

The tests in `tests/` focus on **interactive commands** and **session management** that require user interaction or CLI automation.

**Clear Separation:**
- `basic/dev/tests_with_results/` - Language features (33 tests)
- `tests/` - Interactive commands and UI features (15+ test suites)

## Running All Interactive Tests

```bash
# Run CLI comprehensive test
cd tests
python3 test_cli_comprehensive.py

# Run continue tests
./test_continue.sh
python3 test_simple_continue.py

# Run breakpoint tests
python3 test_breakpoint_comprehensive.py

# Run regression tests
python3 run_regression.py
```

## See Also

- Language feature tests: `docs/dev/TEST_COVERAGE_MATRIX.md`
- Test runner for language tests: `utils/run_tests.py`
- Language test directory: `basic/dev/tests_with_results/`
- Interactive test directory: `tests/`
