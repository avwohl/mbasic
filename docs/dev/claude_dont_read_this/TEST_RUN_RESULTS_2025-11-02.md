# Test Run Results - 2025-11-02

## Summary

**Date:** 2025-11-02
**Test Runner:** `python3 tests/run_regression.py`
**Total Tests:** 27 regression tests
**Passed:** 14 (52%)
**Failed:** 13 (48%)
**Errors:** 0

## Results

### ✅ Passing Tests (14)

1. `regression/help/test_help_search_ranking.py` - Help search result ranking
2. `regression/integration/test_chain_case_preservation.py` - CHAIN command case preservation
3. `regression/interpreter/test_gosub_circular.py` - Circular GOSUB detection
4. `regression/interpreter/test_gosub_stack.py` - GOSUB/RETURN stack management
5. `regression/lexer/test_keyword_case_display_consistency.py` - Keyword case display consistency
6. `regression/lexer/test_keyword_case_policies.py` - Keyword case policy handling
7. `regression/lexer/test_keyword_case_settings_integration.py` - Keyword case settings integration
8. `regression/ui/test_curses_exit.py` - Curses UI exit handling
9. `regression/ui/test_curses_pexpect.py` - Curses UI with pexpect
10. `regression/ui/test_output_focus.py` - Output window focus management
11. `regression/ui/test_output_scroll.py` - Output scrolling behavior
12. `regression/ui/test_scrollable_output.py` - Scrollable output widget
13. `regression/ui/test_settings.py` - Settings system
14. `regression/ui/test_status_priority.py` - Status message priority

###  ❌ Failing Tests (13)

1. `regression/commands/test_renum_spacing.py` - RENUM command spacing preservation
2. `regression/debugger/test_breakpoint_toggle.py` - Breakpoint toggle functionality
3. `regression/editor/test_line_editing.py` - Line editing behavior
4. `regression/help/test_help_integration.py` - Help system integration
5. `regression/help/test_help_macros.py` - Help macro expansion
6. `regression/help/test_help_search.py` - Help search functionality
7. `regression/integration/test_integration_simple.py` - Simple end-to-end tests
8. `regression/lexer/test_keyword_case_scope_isolation.py` - Keyword case scope isolation
9. `regression/parser/test_syntax_checking.py` - Syntax validation
10. `regression/serializer/test_case_preservation.py` - Case preservation during serialization
11. `regression/serializer/test_position_serializer.py` - Position-aware serialization
12. `regression/ui/test_curses_output_display.py` - Curses output display
13. `regression/ui/test_keybinding_loader.py` - Keybinding configuration loading (partial failure)

## Fixes Applied

### 1. Import Path Fixes
Fixed import statements in multiple test files to use proper relative paths:
- Changed `sys.path.insert(0, 'src')` to `sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))`
- Fixed `from ui.` imports to `from src.ui.`
- Fixed late imports missing `src.` prefix

Files fixed:
- `test_renum_spacing.py`
- `test_chain_case_preservation.py`
- `test_integration_simple.py`
- `test_case_preservation.py`
- `test_position_serializer.py`
- `test_curses_pexpect.py`
- All UI tests with `from ui.` imports

### 2. File Path Fixes
Updated test generators to create files in correct locations:
- `test_gosub_circular.py` - Now creates files in `tests/` directory
- `test_gosub_stack.py` - Now creates files in `basic/dev/bas_tests/`
- `test_help_integration.py` - Now uses PROJECT_ROOT to find docs

### 3. Settings API Updates
Removed tests for deprecated keyword case policies that no longer exist:
- Removed tests for `error` policy (raised errors on conflicts)
- Removed tests for `first_wins` policy (used first occurrence's case)
- Removed tests for `preserve` policy (preserved original case)
- Updated tests to only use current policies: `force_lower`, `force_upper`, `force_capitalize`

Files updated:
- `test_keyword_case_settings_integration.py`
- `test_keyword_case_display_consistency.py`

## Remaining Issues

The 13 failing tests need further investigation. Common categories:

### Curses/UI Tests
These tests require urwid and may need running environment fixes:
- `test_breakpoint_toggle.py`
- `test_line_editing.py`
- `test_syntax_checking.py`
- `test_curses_output_display.py`

### Help System Tests
May need path or content updates:
- `test_help_integration.py`
- `test_help_macros.py`
- `test_help_search.py`

### Parser/Serializer Tests
May need API updates:
- `test_case_preservation.py`
- `test_position_serializer.py`
- `test_integration_simple.py`
- `test_keyword_case_scope_isolation.py`

### Command Tests
- `test_renum_spacing.py` - Fixed imports but may have other issues
- `test_keybinding_loader.py` - Partially passing (some keybinding expectations don't match)

## Progress

### Before Fixes
- ✓ Passed: 7
- ✗ Failed: 20

### After Fixes
- ✓ Passed: 14 (+7)
- ✗ Failed: 13 (-7)

**Improvement:** 100% increase in passing tests (7 → 14)

## Next Steps

1. **Investigate failing UI/curses tests** - May need mock objects or different test approach
2. **Check help system tests** - Verify help content paths and structure
3. **Review parser/serializer tests** - Check for API changes that need test updates
4. **Run BASIC tests** - Test the 38 self-checking BASIC programs
5. **Document working test examples** - Use passing tests as templates for writing new tests

## Notes

- All tests can now be run from any directory (proper path handling)
- Import statements are consistent across all tests
- Tests are properly categorized in regression/ subdirectories
- Test runner (`run_regression.py`) works correctly
- Full test output saved to `/tmp/test_results.txt`

## References

- Test inventory: `docs/dev/README_TESTS_INVENTORY.md`
- Test organization: `docs/dev/TEST_INVENTORY.md`
- README testing section: Lines 223-324
