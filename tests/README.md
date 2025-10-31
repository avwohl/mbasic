# MBASIC Testing Guide

This directory contains all test files for the MBASIC interpreter project.

## Directory Structure

```
tests/
├── regression/          # Automated regression tests
│   ├── commands/       # Command tests (RENUM, LIST, etc.)
│   ├── debugger/       # Debugger functionality
│   ├── editor/         # Editor behavior
│   ├── help/           # Help system
│   ├── integration/    # End-to-end integration tests
│   ├── interpreter/    # Core interpreter features
│   ├── lexer/          # Lexer and tokenization
│   ├── parser/         # Parser and AST generation
│   ├── serializer/     # Position serialization and formatting
│   └── ui/            # UI-specific tests
├── manual/             # Manual/visual tests requiring human verification
├── debug/              # Temporary debugging tests (gitignored)
├── run_regression.py   # Test runner script
└── README.md          # This file
```

## Running Tests

### Quick Start

Run all regression tests:
```bash
python3 tests/run_regression.py
```

Run tests in a specific category:
```bash
python3 tests/run_regression.py --category lexer
python3 tests/run_regression.py --category integration
```

Run a specific test file:
```bash
python3 tests/regression/lexer/test_keyword_case_policies.py
```

### Test Runner Features

The test runner (`run_regression.py`) provides:
- **Automatic test discovery** - Finds all `test_*.py` files
- **Category filtering** - Run only tests in specific categories
- **Timeout protection** - Tests timeout after 30 seconds
- **Clear reporting** - Pass/fail summary with error details
- **Proper environment** - Sets PYTHONPATH and working directory

### Test Categories

**regression/** - Automated tests that verify behavior
- Should run quickly (< 5 seconds each)
- Should be deterministic and repeatable
- Should test specific functionality in isolation
- Exit code 0 = pass, non-zero = fail

**manual/** - Tests requiring human verification
- Visual/interactive tests
- Platform-specific tests
- Installation verification scripts

**debug/** - Temporary development tests
- NOT tracked in git (see `.gitignore`)
- Use for one-off debugging
- Move to regression/ when stabilized

## Writing Tests

### Test File Naming

- All test files must start with `test_`
- Example: `test_keyword_case_policies.py`
- Use descriptive names: `test_for_loop_execution.py` not `test_loops.py`

### Test File Structure

```python
#!/usr/bin/env python3
"""
Test description: What this test verifies

Tests:
- Specific behavior 1
- Specific behavior 2
- Edge case handling
"""

import sys
import os

# Add project root to path (adjust depth based on location)
# From tests/regression/category/ go up 3 levels
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter

def test_feature():
    """Test specific feature."""
    # Arrange
    code = "10 PRINT \"Hello\"\n"

    # Act
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    # Assert
    assert len(tokens) > 0, "Should tokenize code"
    print("✓ Feature works correctly")

if __name__ == "__main__":
    try:
        test_feature()
        print("\n✅ All tests passed")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

### Import Guidelines

**Always use `src.` prefix for project imports:**

```python
# ✓ CORRECT
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.tokens import Token

# ✗ WRONG - will fail when run via test runner
from lexer import Lexer
from parser import Parser
```

**Calculate path depth correctly:**

```python
# From tests/regression/category/test_file.py (3 levels deep)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

# From tests/regression/test_file.py (2 levels deep)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
```

### Assertion Patterns

Use clear assertion messages:
```python
# ✓ GOOD
assert result == expected, f"Expected {expected}, got {result}"
assert len(tokens) > 0, "Tokenization produced no tokens"

# ✗ BAD
assert result == expected  # Unclear what failed
```

### Exit Codes

Tests must exit with proper codes:
- **0** - All tests passed
- **1** - Test failed (assertion error)
- **1** - Test error (exception)

## Test Categories Explained

### regression/commands/
Tests for REPL commands (RENUM, LIST, RUN, etc.)
- Command parsing
- Command execution
- Output formatting

### regression/debugger/
Tests for debugger functionality
- Breakpoint handling
- Step execution
- Variable inspection

### regression/editor/
Tests for editor behavior
- Line editing
- Case preservation
- Spacing preservation

### regression/help/
Tests for help system
- Help content rendering
- Search functionality
- Navigation

### regression/integration/
End-to-end tests that exercise multiple components
- Full program execution
- CHAIN command behavior
- Settings system integration

### regression/interpreter/
Core interpreter features
- Statement execution
- Expression evaluation
- Control flow (FOR, WHILE, IF, GOSUB, etc.)
- Built-in functions
- Variable handling

### regression/lexer/
Tokenization and lexical analysis
- Keyword recognition
- Case handling policies
- Token generation

### regression/parser/
Parsing and AST generation
- Syntax validation
- Parse tree construction
- Error reporting

### regression/serializer/
Code formatting and serialization
- Position tracking
- Spacing preservation
- Case preservation
- Pretty printing

### regression/ui/
UI-specific functionality
- Help widget
- Settings display
- Editor integration

## Adding New Tests

### Workflow

1. **Create test file** in appropriate category
   ```bash
   # For interpreter feature test
   touch tests/regression/interpreter/test_new_feature.py
   chmod +x tests/regression/interpreter/test_new_feature.py
   ```

2. **Write test** using template above

3. **Run test directly** to verify
   ```bash
   python3 tests/regression/interpreter/test_new_feature.py
   ```

4. **Run via test runner** to verify discovery
   ```bash
   python3 tests/run_regression.py --category interpreter
   ```

5. **Commit test** with feature implementation
   ```bash
   ./checkpoint.sh "Add feature X with regression test"
   ```

### When to Add Tests

**Always add tests for:**
- Bug fixes (regression prevention)
- New features
- Edge cases discovered
- Refactoring (ensure behavior unchanged)

**Test granularity:**
- One test file per feature/component
- Multiple test functions per file OK
- Keep tests focused and independent

## Debugging Test Failures

### Running with Debug Output

Enable debug logging:
```bash
MBASIC_DEBUG=1 python3 tests/regression/interpreter/test_feature.py
```

### Common Issues

**ModuleNotFoundError**
- Check `sys.path.insert()` depth calculation
- Verify imports use `src.` prefix

**Test hangs/timeout**
- Check for infinite loops in test code
- Verify test cleanup (e.g., closing files)

**Inconsistent results**
- Check for shared state between tests
- Verify test independence

### Test Runner Verbose Mode

```bash
# Show all test output (including stdout/stderr)
python3 tests/run_regression.py --verbose
```

## Manual Testing

Some tests require human verification:

### tests/manual/test_clean_install.sh
Verifies installation from scratch on clean system
```bash
cd tests/manual/
./test_clean_install.sh
```

### UI Testing
Full curses UI testing requires pexpect:
```bash
python3 utils/test_curses_comprehensive.py
```

## BASIC Test Programs

BASIC program test files live in `basic/bas_tests/`:
```bash
# Run BASIC test program
python3 mbasic basic/bas_tests/test_program.bas

# With specific backend
python3 mbasic --backend=cli basic/bas_tests/test_program.bas
```

## CI/CD Integration

The test runner is designed for CI/CD integration:

```bash
# Run all tests, exit code indicates pass/fail
python3 tests/run_regression.py
EXIT_CODE=$?

# Run specific categories in parallel
python3 tests/run_regression.py --category lexer &
python3 tests/run_regression.py --category parser &
wait
```

## Coverage Goals

Aim to test:
- ✓ All statement types (FOR, WHILE, IF, GOSUB, etc.)
- ✓ All built-in functions (ABS, INT, LEFT$, etc.)
- ✓ All commands (RENUM, LIST, LOAD, SAVE, etc.)
- ✓ Edge cases (empty input, overflow, etc.)
- ✓ Error handling (syntax errors, runtime errors)
- ✓ Settings system (all settings, validation)
- ✓ Help system (navigation, search)
- ✓ Editor features (case/spacing preservation)

## Questions?

See also:
- `docs/dev/CURSES_UI_TESTING.md` - Curses UI testing details
- `tests/manual/README.md` - Manual testing guide
- `tests/debug/README.md` - Debug directory usage
- Main `README.md` - Project overview

For implementation questions, check:
- `docs/dev/` - Development documentation
- `docs/help/` - Help system content
