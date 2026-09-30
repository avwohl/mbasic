# Testing

MBASIC has a comprehensive test suite with automated regression tests and BASIC program tests.

## Quick Start

Run all regression tests:
```bash
python3 tests/run_regression.py
```

Run tests in a specific category:
```bash
python3 tests/run_regression.py --category lexer
python3 tests/run_regression.py --category interpreter
```

## Test Organization

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
│   └── ui/            # UI-specific tests
├── manual/             # Manual verification tests
└── run_regression.py   # Test runner script
```

## Test Categories

- **regression/** - Automated tests (deterministic, repeatable)
- **manual/** - Tests requiring human verification
- **debug/** - Temporary debugging tests (not tracked in git)

## BASIC Test Programs

Test BASIC programs live in `basic/dev/bas_tests/`:

```bash
# Run any BASIC test program
python3 mbasic basic/dev/bas_tests/test_operator_precedence.bas
```

Self-checking tests verify correctness and report results:
```bash
python3 mbasic basic/dev/tests_with_results/test_operator_precedence.bas
# Result: All 20 tests PASS
```

## Writing Tests

Test files must:
- Start with `test_` prefix
- Use `src.` prefix for imports (`from src.lexer import Lexer`)
- Exit with code 0 on success, 1 on failure
- Include clear assertion messages

Example test structure:
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

**See [tests/README.md](https://github.com/avwohl/mbasic/blob/main/tests/README.md) for complete testing guide.**

## Test Coverage

✓ All statement types (FOR, WHILE, IF, GOSUB, etc.)
✓ All built-in functions (ABS, INT, LEFT$, etc.)
✓ All commands (RENUM, LIST, LOAD, SAVE, etc.)
✓ Edge cases and error handling
✓ Settings system
✓ Help system
✓ Editor features (case/spacing preservation)
