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

## More Detail

The [Testing Guide](../docs/dev/TESTING_GUIDE.md) covers writing tests, import rules,
each regression category, adding tests, debugging failures, manual tests,
BASIC test programs, CI use, and coverage goals.

## Questions?

See also:
- `docs/dev/CURSES_UI_TESTING.md` - Curses UI testing details
- `tests/manual/README.md` - Manual testing guide
- `tests/debug/README.md` - Debug directory usage
- Main `README.md` - Project overview

For implementation questions, check:
- `docs/dev/` - Development documentation
- `docs/help/` - Help system content
