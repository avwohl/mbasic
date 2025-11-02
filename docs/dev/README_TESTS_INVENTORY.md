# README.md Test Inventory

This document lists all tests mentioned in README.md and provides a comprehensive inventory of the actual test suite.

> **Last Updated:** 2025-11-02
> **Source:** README.md Testing section (lines 223-324)

## Test Organization (from README.md)

### Test Directory Structure

```
tests/
├── regression/          # Automated regression tests
│   ├── commands/       # REPL commands (RENUM, LIST, etc.)
│   ├── debugger/       # Debugger functionality
│   ├── editor/         # Editor behavior
│   ├── integration/    # End-to-end tests
│   ├── interpreter/    # Core interpreter features
│   ├── lexer/          # Tokenization and case handling
│   ├── parser/         # Parsing and AST generation
│   ├── serializer/     # Code formatting
│   └── ui/             # UI-specific tests
├── manual/             # Manual verification tests
└── run_regression.py   # Test runner script

basic/dev/
├── bas_tests/          # BASIC test programs (64 files)
└── tests_with_results/ # Self-checking BASIC tests (38 files)
```

### Test Categories

- **regression/** - Automated tests (deterministic, repeatable)
- **manual/** - Tests requiring human verification
- **debug/** - Temporary debugging tests (not tracked in git)

## Running Tests (from README.md)

### Run All Regression Tests
```bash
python3 tests/run_regression.py
```

### Run Tests by Category
```bash
python3 tests/run_regression.py --category lexer
python3 tests/run_regression.py --category interpreter
python3 tests/run_regression.py --category commands
python3 tests/run_regression.py --category debugger
python3 tests/run_regression.py --category editor
python3 tests/run_regression.py --category integration
python3 tests/run_regression.py --category parser
python3 tests/run_regression.py --category serializer
python3 tests/run_regression.py --category ui
python3 tests/run_regression.py --category help
```

### Run BASIC Test Programs
```bash
# Run any BASIC test program
python3 mbasic basic/dev/bas_tests/test_operator_precedence.bas

# Run self-checking tests (verify correctness automatically)
python3 mbasic basic/dev/tests_with_results/test_operator_precedence.bas
```

## Test Coverage (from README.md)

✓ All statement types (FOR, WHILE, IF, GOSUB, etc.)
✓ All built-in functions (ABS, INT, LEFT$, etc.)
✓ All commands (RENUM, LIST, LOAD, SAVE, etc.)
✓ Edge cases and error handling
✓ Settings system
✓ Help system
✓ Editor features (case/spacing preservation)

## Regression Tests (Python)

**Total: 27 automated regression tests**

### Commands (tests/regression/commands/)
1. `test_renum_spacing.py` - RENUM command spacing preservation

### Debugger (tests/regression/debugger/)
2. `test_breakpoint_toggle.py` - Breakpoint toggle functionality

### Editor (tests/regression/editor/)
3. `test_line_editing.py` - Line editing behavior

### Help System (tests/regression/help/)
4. `test_help_integration.py` - Help system integration
5. `test_help_macros.py` - Help macro expansion
6. `test_help_search.py` - Help search functionality
7. `test_help_search_ranking.py` - Help search result ranking

### Integration (tests/regression/integration/)
8. `test_chain_case_preservation.py` - CHAIN command case preservation
9. `test_integration_simple.py` - Simple end-to-end tests

### Interpreter (tests/regression/interpreter/)
10. `test_gosub_circular.py` - Circular GOSUB detection
11. `test_gosub_stack.py` - GOSUB/RETURN stack management

### Lexer (tests/regression/lexer/)
12. `test_keyword_case_display_consistency.py` - Keyword case display consistency
13. `test_keyword_case_policies.py` - Keyword case policy handling
14. `test_keyword_case_scope_isolation.py` - Keyword case scope isolation
15. `test_keyword_case_settings_integration.py` - Keyword case settings integration

### Parser (tests/regression/parser/)
16. `test_syntax_checking.py` - Syntax validation

### Serializer (tests/regression/serializer/)
17. `test_case_preservation.py` - Case preservation during serialization
18. `test_position_serializer.py` - Position-aware serialization

### UI (tests/regression/ui/)
19. `test_curses_exit.py` - Curses UI exit handling
20. `test_curses_output_display.py` - Curses output display
21. `test_curses_pexpect.py` - Curses UI with pexpect
22. `test_keybinding_loader.py` - Keybinding configuration loading
23. `test_output_focus.py` - Output window focus management
24. `test_output_scroll.py` - Output scrolling behavior
25. `test_scrollable_output.py` - Scrollable output widget
26. `test_settings.py` - Settings system
27. `test_status_priority.py` - Status message priority

## Self-Checking BASIC Tests (basic/dev/tests_with_results/)

**Total: 38 self-checking BASIC tests**

These tests verify correctness and report results automatically.

### Array and Memory Management
1. `test_dim_arrays.bas` - DIM array declarations
2. `test_erase.bas` - ERASE array statement
3. `test_option_base.bas` - OPTION BASE 0/1 for array indexing

### Control Flow
4. `test_for_next.bas` - FOR/NEXT loops
5. `test_gosub.bas` - GOSUB/RETURN statements
6. `test_goto.bas` - GOTO statement
7. `test_if_then_else.bas` - IF/THEN/ELSE conditionals
8. `test_on_goto_gosub.bas` - ON GOTO and ON GOSUB computed jumps
9. `test_while_wend.bas` - WHILE/WEND loops

### Data and I/O
10. `test_binary_conversion.bas` - Binary data conversion (MKI$/CVI, etc.)
11. `test_data_read.bas` - DATA/READ/RESTORE statements
12. `test_file_io.bas` - Sequential file I/O operations
13. `test_input.bas` - INPUT statement
14. `test_print_using.bas` - PRINT USING formatted output
15. `test_random_files.bas` - Random file I/O (FIELD, GET, PUT, etc.)
16. `test_tab_spc.bas` - TAB and SPC functions

### Error Handling
17. `test_error_handling.bas` - ON ERROR GOTO/GOSUB, RESUME, ERL, ERR

### Functions and Operators
18. `test_def_fn.bas` - DEF FN user-defined functions
19. `test_eqv_imp.bas` - EQV and IMP logical operators
20. `test_hex_oct.bas` - Hexadecimal and octal number literals
21. `test_logical_ops.bas` - AND, OR, NOT logical operators
22. `test_math_functions.bas` - Mathematical functions (SIN, COS, SQR, etc.)
23. `test_mid_assignment.bas` - MID$ assignment statement
24. `test_mod_intdiv.bas` - MOD and integer division (\)
25. `test_operator_precedence.bas` - Operator precedence rules
26. `test_string_functions.bas` - String functions (LEFT$, RIGHT$, MID$, etc.)

### Numeric Operations
27. `test_randomize.bas` - RANDOMIZE statement
28. `test_rnd.bas` - RND random number function
29. `test_rounding.bas` - Numeric rounding behavior
30. `test_type_conversion.bas` - Type conversion functions

### Program Management
31. `test_chain.bas` - CHAIN command
32. `test_merge.bas` - MERGE command

### System and I/O
33. `test_inkey.bas` - INKEY$ non-blocking input
34. `test_peek.bas` - PEEK function
35. `test_tron_troff.bas` - TRON/TROFF execution tracing

### Type Declarations
36. `test_deftypes.bas` - DEFINT/DEFSTR/DEFSNG/DEFDBL type declarations

### Utility Operations
37. `test_simple.bas` - Simple basic operations
38. `test_swap.bas` - SWAP statement

## BASIC Test Programs (basic/dev/bas_tests/)

**Total: 64 BASIC test programs**

General BASIC programs used for testing interpreter functionality.

### Games and Interactive Programs
1. `battle.bas` - Battle game
2. `doodle.bas` - Drawing program
3. `hanoi.bas` - Tower of Hanoi
4. `krak.bas` - Krak game
5. `nim.bas` - Nim game
6. `poker.bas` - Poker game

### GOSUB Stack Tests (20 files)
7. `gostk1.bas` - GOSUB stack test 1
8. `gosub10.bas` - GOSUB test (10 depth)
9. `gosub20.bas` - GOSUB test (20 depth)
10. `gosub30.bas` - GOSUB test (30 depth)
11. `gosub40.bas` - GOSUB test (40 depth)
12. `gosub50.bas` - GOSUB test (50 depth)
13. `gosub60.bas` - GOSUB test (60 depth)
14. `gosub70.bas` - GOSUB test (70 depth)
15. `gosub_stack_50.bas` - GOSUB stack test (50 depth)
16. `gosub_stack_100.bas` - GOSUB stack test (100 depth)
17. `gosub_stack_150.bas` - GOSUB stack test (150 depth)
18. `gosub_stack_200.bas` - GOSUB stack test (200 depth)
19. `gosub_stack_test_simple.bas` - Simple GOSUB stack test
20-26. _(Additional GOSUB stack tests)_

### Utility and Tool Programs
27. `asciiart.bas` - ASCII art generation
28. `asm2mac.bas` - Assembly to macro conversion
29. `genielst.bas` - Genie list utility
30. `maptest.bas` - Map test
31. `menu.bas` - Menu system test

### Calculation and Science Programs
32. `holtwint.bas` - Holt winter statistics
33. `mooncalc.bas` - Moon calculation

### Visual and Pattern Programs
34. `pattern.bas` - Pattern generation
35. `pattern1.bas` - Pattern generation variant

### Test and Debug Programs
36. `direct.bas` - Direct mode test
37. `hello_test.bas` - Hello world test

### Additional Programs (28 more)
38-64. _(Various other BASIC programs for comprehensive testing)_

## Test File Requirements (from README.md)

Test files must:
- Start with `test_` prefix
- Use `src.` prefix for imports (`from src.lexer import Lexer`)
- Exit with code 0 on success, 1 on failure
- Include clear assertion messages

### Example Test Structure
```python
#!/usr/bin/env python3
import sys
import os

# Add project root to path (3 levels up from tests/regression/category/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.lexer import Lexer

def test_feature():
    lexer = Lexer("10 PRINT \"Hello\"")
    tokens = lexer.tokenize()
    assert len(tokens) > 0, "Should tokenize code"
    print("✓ Feature works")

if __name__ == "__main__":
    try:
        test_feature()
        print("\n✅ All tests passed")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
```

## Summary Statistics

- **27** Python regression tests across 9 categories
- **38** self-checking BASIC tests with automatic verification
- **64** BASIC test programs for manual/interactive testing
- **129** total test files

### Test Coverage by Category

| Category | Python Tests | BASIC Tests | Total |
|----------|-------------|-------------|-------|
| Commands | 1 | - | 1 |
| Debugger | 1 | - | 1 |
| Editor | 1 | - | 1 |
| Help | 4 | - | 4 |
| Integration | 2 | - | 2 |
| Interpreter | 2 | 38 | 40 |
| Lexer | 4 | - | 4 |
| Parser | 1 | - | 1 |
| Serializer | 2 | - | 2 |
| UI | 9 | - | 9 |
| General | - | 64 | 64 |
| **Total** | **27** | **102** | **129** |

## Implementation Status Tests (from README.md)

The README.md lists comprehensive feature coverage including:

### Core Interpreter Features Tested
- Runtime state management
- Variable storage (all type suffixes)
- Array support with DIM
- Line number resolution
- GOSUB/RETURN stack
- FOR/NEXT loops
- WHILE/WEND loops
- ON GOTO/ON GOSUB (computed jumps)
- DATA/READ/RESTORE
- Expression evaluation
- All operators
- 50+ built-in functions
- User-defined functions (DEF FN)
- Sequential file I/O
- Random file I/O
- Binary file I/O
- Error handling
- File system operations
- Non-blocking input (INKEY$)
- Execution tracing (TRON/TROFF)
- PRINT USING
- SWAP statement
- MID$ assignment

### Interactive Mode Features Tested
- Line entry and editing
- RUN command
- LIST command (with ranges)
- SAVE/LOAD commands
- NEW command
- DELETE command
- RENUM command
- Immediate mode
- Error recovery
- CONT (continue after STOP or Ctrl+C)
- EDIT command

## References

- **Main Testing Guide:** `tests/README.md` (in repository root)
- **Test Organization Plan:** See TEST_INVENTORY.md for historical test organization
- **README Testing Section:** README.md lines 223-324
- **Project Status:** [PROJECT_STATUS.md](../PROJECT_STATUS.md)
