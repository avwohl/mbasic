# Testing System Organization - TODO

## Status: ⏳ TODO

## Problem

Over the course of development, many test files have been created:
- Some are **regression tests** that should run on every change
- Some are **debug tests** for specific features being developed
- Some are **one-off experiments** that may no longer be relevant
- There's no clear organization or documentation of what each test does
- No clear way to run "all important tests" vs "just this feature"

## Goal

Create a well-organized testing system with:
1. Clear separation between permanent regression tests and temporary debug tests
2. Documentation of what each test does and when to run it
3. A test runner that can run all regression tests
4. Guidelines for where to put new tests

## Current Test Inventory (Needs Review)

### Root Directory Tests (Potential Clutter)
```
test_keyword_case.bas
test_keyword_case_policies.py
test_renum_spacing.py
test_case_preservation.py
test_position_serializer.py
test_clean_install.sh
test_interactive_*.sh (multiple)
test_ctrl_*.sh (multiple)
test_clear_interactive.sh
test_renum_erl_interactive.sh
```

### Basic Test Directory
```
basic/
  bas_tests/          # BASIC test programs
  bas_tests1/         # More BASIC test programs (why separate?)
  tests_with_results/ # Tests with expected output
  bad_syntax/         # Programs with syntax errors
```

### Utils Directory
```
utils/
  test_curses_*.py (multiple curses UI tests)
```

## Proposed Organization

### 1. Regression Tests Directory
**Location:** `tests/regression/`

**Purpose:** Tests that should pass on every commit

**Structure:**
```
tests/
  regression/
    lexer/
      test_keyword_case.py
      test_tokenization.py
    parser/
      test_parsing.py
      test_ast_nodes.py
    serializer/
      test_position_serializer.py
      test_case_preservation.py
    interpreter/
      test_execution.py
      test_for_loops.py
    ui/
      test_curses_comprehensive.py
      test_tk_ui.py
    integration/
      test_end_to_end.py
```

### 2. Manual/Interactive Tests
**Location:** `tests/manual/`

**Purpose:** Tests that require human interaction

**Structure:**
```
tests/
  manual/
    test_interactive_def.sh
    test_interactive_all_def.sh
    test_ctrl_a3.sh
    test_ctrl_a4.sh
    test_clear_interactive.sh
    test_renum_erl_interactive.sh
    README.md (explains how to run each)
```

### 3. Debug/Development Tests
**Location:** `tests/debug/` (temporary, not committed)

**Purpose:** Quick tests for current feature development

**Structure:**
```
tests/
  debug/
    .gitignore (ignore all files in this directory)
    README.md (explains this is for temporary tests)
```

### 4. BASIC Program Tests
**Keep existing structure but document:**
```
basic/
  bas_tests/          # Valid BASIC programs for testing
  bas_tests1/         # (TODO: Merge with bas_tests or explain difference)
  tests_with_results/ # Programs with expected output files
  bad_syntax/         # Programs that should fail parsing
  README.md (document structure and conventions)
```

### 5. Test Runner Script
**Location:** `tests/run_regression.py`

**Purpose:** Run all regression tests

**Features:**
- Discover and run all tests in `tests/regression/`
- Report pass/fail with clear output
- Exit code 0 if all pass, 1 if any fail
- Optional: `--category lexer` to run just one category

**Usage:**
```bash
# Run all regression tests
python3 tests/run_regression.py

# Run just lexer tests
python3 tests/run_regression.py --category lexer

# Verbose output
python3 tests/run_regression.py --verbose
```

## Action Items

### Phase 1: Inventory (Review Current Tests)
- [ ] List all test files in root directory
- [ ] Identify purpose of each test
- [ ] Categorize: regression / manual / debug / obsolete
- [ ] Check if test still works and is relevant

### Phase 2: Create Structure
- [ ] Create `tests/regression/` directory structure
- [ ] Create `tests/manual/` directory
- [ ] Create `tests/debug/` with .gitignore
- [ ] Move tests to appropriate locations

### Phase 3: Documentation
- [ ] Write `tests/README.md` explaining organization
- [ ] Write `tests/regression/README.md` with test categories
- [ ] Write `tests/manual/README.md` with instructions
- [ ] Document each BASIC test directory

### Phase 4: Test Runner
- [ ] Create `tests/run_regression.py`
- [ ] Make it discover and run all regression tests
- [ ] Add to CI/CD if applicable
- [ ] Update main README with testing instructions

### Phase 5: Cleanup
- [ ] Delete obsolete tests
- [ ] Merge bas_tests1 into bas_tests if appropriate
- [ ] Remove test files from root directory
- [ ] Update .gitignore

## Testing Guidelines (To Document)

### When to Create a Test

**Regression Test (tests/regression/):**
- New feature that should keep working
- Bug fix that should stay fixed
- Core functionality (parsing, execution, etc.)

**Manual Test (tests/manual/):**
- Interactive UI feature
- Requires human verification
- Terminal control sequences

**Debug Test (tests/debug/):**
- Quick experiment
- Feature in development
- Will be deleted or promoted later

### Test Naming Convention

```
test_<feature>_<aspect>.py
```

Examples:
- `test_keyword_case_policies.py` - Test keyword case handling policies
- `test_position_serializer_spacing.py` - Test serializer spacing preservation
- `test_for_loop_execution.py` - Test FOR loop runtime behavior

### What Makes a Good Regression Test

1. **Automated** - Runs without human input
2. **Fast** - Completes in seconds
3. **Focused** - Tests one thing clearly
4. **Self-contained** - No external dependencies
5. **Reliable** - Same result every time
6. **Clear output** - Easy to see what failed

## Example Test Template

```python
#!/usr/bin/env python3
"""
Test: <Feature Name>

Purpose: <What this tests>
Category: <regression/manual/debug>
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.lexer import Lexer
from src.parser import Parser

def test_feature():
    """Test description"""
    # Test code here
    assert result == expected, f"Expected {expected}, got {result}"
    print("✓ Test passed")

if __name__ == "__main__":
    test_feature()
    sys.exit(0)  # 0 = success
```

## Notes

- Some test files in root may be important examples that should stay
- Consider keeping `test_keyword_case_policies.py` as example in docs
- Interactive tests are valuable - don't delete, just organize
- Consider using pytest or unittest framework for better test organization

## References

- Current test files scattered across root directory
- `utils/test_curses_comprehensive.py` - Good example of organized test
- `basic/bas_tests/` - Existing BASIC test programs
