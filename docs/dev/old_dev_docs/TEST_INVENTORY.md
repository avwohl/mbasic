# Test Files Inventory

**Created:** 2025-10-28
**Purpose:** Comprehensive inventory of all test files to support test organization project

## Summary Statistics

- **Root directory Python tests:** 10 files
- **Root directory shell tests:** 1 file
- **Root directory BASIC tests:** 2 files
- **Utils directory tests:** 22 files
- **Total:** 35 test files identified

---

## Root Directory Tests (Python)

### Regression Tests (Should Move to tests/regression/)

#### 1. `test_position_serializer.py`
- **Purpose:** Test spacing preservation in serialization
- **Category:** REGRESSION - Serializer
- **Status:** Important, should run on every commit
- **Test cases:** Compact/spacious/mixed spacing styles
- **Move to:** `tests/regression/serializer/test_position_serializer.py`

#### 2. `test_case_preservation.py`
- **Purpose:** Test variable name case preservation
- **Category:** REGRESSION - Serializer
- **Status:** Important, should run on every commit
- **Test cases:** PascalCase, camelCase, UPPERCASE, snake_case variables
- **Move to:** `tests/regression/serializer/test_case_preservation.py`

#### 3. `test_renum_spacing.py`
- **Purpose:** Test RENUM command preserves spacing
- **Category:** REGRESSION - Commands
- **Status:** Important
- **Move to:** `tests/regression/commands/test_renum_spacing.py`

#### 4. `test_chain_case_preservation.py`
- **Purpose:** Test case preservation through parse→serialize→parse chain
- **Category:** REGRESSION - Integration
- **Status:** Important end-to-end test
- **Move to:** `tests/regression/integration/test_chain_case_preservation.py`

#### 5. `test_keyword_case_policies.py`
- **Purpose:** Test keyword case handling policies (v1.0.122-128 feature)
- **Category:** REGRESSION - Lexer/Serializer
- **Status:** Important, tests force_lower/upper/capitalize/first_wins/preserve
- **Move to:** `tests/regression/lexer/test_keyword_case_policies.py`

#### 6. `test_integration_simple.py`
- **Purpose:** Simple integration test of parser→runtime→interpreter
- **Category:** REGRESSION - Integration
- **Status:** Basic smoke test
- **Move to:** `tests/regression/integration/test_integration_simple.py`

### Debug/Development Tests (Should Move to tests/debug/ or Delete)

#### 7. `test_case_conflict_unit.py`
- **Purpose:** Unit test for case conflict detection
- **Category:** DEBUG - May be temporary
- **Action:** Review if still needed, move to tests/debug/ or promote to regression

#### 8. `test_case_conflict_integration.py`
- **Purpose:** Integration test for case conflict detection
- **Category:** DEBUG - May be temporary
- **Action:** Review if still needed, move to tests/debug/ or promote to regression

#### 9. `test_case_debug.py`
- **Purpose:** Debug test for case handling
- **Category:** DEBUG - Temporary
- **Action:** Review if still needed, likely delete or move to tests/debug/

#### 10. `test_ast_case.py`
- **Purpose:** Test AST representation of case
- **Category:** DEBUG - May be temporary
- **Action:** Review if still needed, move to tests/debug/ or promote to regression

---

## Root Directory Tests (Shell)

### Installation/System Tests

#### 11. `test_clean_install.sh`
- **Purpose:** Test MBASIC installation in clean environment
- **Category:** MANUAL/CI - Installation validation
- **Status:** Important for release testing
- **Tests:** Virtual env, CLI backend, curses support, package metadata
- **Move to:** `tests/manual/test_clean_install.sh` or keep in root for CI

---

## Root Directory Tests (BASIC)

### Test Programs

#### 12. `test_case_conflict.bas`
- **Purpose:** BASIC program to test case conflict behavior
- **Category:** Test fixture
- **Move to:** `basic/bas_tests/test_case_conflict.bas`

#### 13. `test_keyword_case.bas`
- **Purpose:** BASIC program to test keyword case handling
- **Category:** Test fixture
- **Move to:** `basic/bas_tests/test_keyword_case.bas`

---

## Utils Directory Tests

### Curses UI Tests

#### 14. `utils/test_curses_comprehensive.py`
- **Purpose:** Comprehensive curses UI test suite
- **Category:** REGRESSION - UI
- **Status:** IMPORTANT - Main curses test runner
- **Tests:** UI creation, input handlers, parsing, execution, lifecycle
- **Keep in:** utils/ (documented in CLAUDE.md)

#### 15. `utils/test_curses_pexpect.py`
- **Purpose:** Curses integration testing with pexpect
- **Category:** REGRESSION - UI
- **Status:** Integration test approach
- **Keep in:** utils/

#### 16. `utils/test_curses_pyte.py`
- **Purpose:** Terminal emulator testing (experimental)
- **Category:** DEBUG/EXPERIMENTAL
- **Status:** May be obsolete
- **Action:** Review if still used

#### 17. `utils/test_curses_urwid_sim.py`
- **Purpose:** Direct simulation testing
- **Category:** DEBUG/EXPERIMENTAL
- **Status:** May be obsolete if comprehensive test covers this
- **Action:** Review if still used

#### 18. `utils/test_curses_output_display.py`
- **Purpose:** Test curses output display functionality
- **Category:** REGRESSION - UI
- **Status:** Specific feature test

#### 19. `utils/test_curses_border_visual.py`
- **Purpose:** Visual test of curses border rendering
- **Category:** MANUAL - Visual verification
- **Status:** Requires human inspection

#### 20. `utils/test_curses_topleft_visual.py`
- **Purpose:** Visual test of top-left corner rendering
- **Category:** MANUAL - Visual verification

#### 21. `utils/test_curses_3column_editor.py`
- **Purpose:** Test 3-column editor layout
- **Category:** DEBUG/DEVELOPMENT
- **Status:** May be from specific feature development

#### 22. `utils/test_curses_column_behavior.py`
- **Purpose:** Test column behavior in curses UI
- **Category:** DEBUG/DEVELOPMENT

#### 23. `utils/test_curses_exit.py`
- **Purpose:** Test curses exit handling
- **Category:** REGRESSION - UI

### Interpreter/Runtime Tests

#### 24. `utils/test_gosub_circular.py`
- **Purpose:** Test GOSUB stack circular buffer behavior
- **Category:** REGRESSION - Interpreter
- **Status:** Important for GOSUB stack correctness
- **Move to:** `tests/regression/interpreter/test_gosub_circular.py`

#### 25. `utils/test_gosub_stack.py`
- **Purpose:** Test GOSUB stack functionality
- **Category:** REGRESSION - Interpreter
- **Move to:** `tests/regression/interpreter/test_gosub_stack.py`

#### 26. `utils/test_syntax_checking.py`
- **Purpose:** Test syntax checking functionality
- **Category:** REGRESSION - Parser
- **Move to:** `tests/regression/parser/test_syntax_checking.py`

#### 27. `utils/test_line_editing.py`
- **Purpose:** Test line editing functionality
- **Category:** REGRESSION - Editor
- **Move to:** `tests/regression/editor/test_line_editing.py`

### Help System Tests

#### 28. `utils/test_help_search.py`
- **Purpose:** Test help search functionality
- **Category:** REGRESSION - Help
- **Move to:** `tests/regression/help/test_help_search.py`

#### 29. `utils/test_help_integration.py`
- **Purpose:** Integration test for help system
- **Category:** REGRESSION - Help
- **Move to:** `tests/regression/help/test_help_integration.py`

#### 30. `utils/test_help_macros.py`
- **Purpose:** Test help macro expansion
- **Category:** REGRESSION - Help
- **Move to:** `tests/regression/help/test_help_macros.py`

#### 31. `utils/test_keybinding_loader.py`
- **Purpose:** Test keybinding loading/configuration
- **Category:** REGRESSION - UI
- **Move to:** `tests/regression/ui/test_keybinding_loader.py`

### UI Feature Tests

#### 32. `utils/test_output_focus.py`
- **Purpose:** Test output window focus behavior
- **Category:** REGRESSION - UI
- **Move to:** `tests/regression/ui/test_output_focus.py`

#### 33. `utils/test_status_priority.py`
- **Purpose:** Test status message priority
- **Category:** REGRESSION - UI
- **Move to:** `tests/regression/ui/test_status_priority.py`

#### 34. `utils/test_output_scroll.py`
- **Purpose:** Test output scrolling
- **Category:** REGRESSION - UI
- **Move to:** `tests/regression/ui/test_output_scroll.py`

#### 35. `utils/test_scrollable_output.py`
- **Purpose:** Test scrollable output widget
- **Category:** REGRESSION - UI
- **Move to:** `tests/regression/ui/test_scrollable_output.py`

#### 36. `utils/test_breakpoint_toggle.py`
- **Purpose:** Test breakpoint toggle functionality
- **Category:** REGRESSION - Debugger
- **Move to:** `tests/regression/debugger/test_breakpoint_toggle.py`

---

## Categorization Summary

### Definitely Keep as Regression Tests (25)
- Position serializer tests
- Case preservation tests
- Keyword case policy tests
- Integration tests
- GOSUB stack tests
- Help system tests
- UI feature tests
- Syntax checking
- Line editing
- Breakpoint toggle
- Curses comprehensive test

### Review for Relevance (6)
- test_case_conflict_unit.py
- test_case_conflict_integration.py
- test_case_debug.py
- test_ast_case.py
- test_curses_pyte.py (experimental)
- test_curses_urwid_sim.py (may be obsolete)

### Manual/Visual Tests (4)
- test_clean_install.sh
- test_curses_border_visual.py
- test_curses_topleft_visual.py
- (Any interactive .sh tests in /tmp - not found in current inventory)

### Test Fixtures (2)
- test_case_conflict.bas
- test_keyword_case.bas

---

## Proposed Organization Actions

### Phase 1: Create Structure
```bash
mkdir -p tests/{regression,manual,debug}
mkdir -p tests/regression/{serializer,parser,lexer,interpreter,editor,help,ui,debugger,integration,commands}
```

### Phase 2: Move Regression Tests
- Move 25 identified regression tests to appropriate subdirectories
- Keep utils/test_curses_comprehensive.py in utils/ (documented in CLAUDE.md)

### Phase 3: Move Manual Tests
- Move test_clean_install.sh to tests/manual/
- Move visual test scripts to tests/manual/

### Phase 4: Move Test Fixtures
- Move .bas test files to basic/bas_tests/

### Phase 5: Review Questionable Tests
- Review 6 tests marked for review
- Either promote to regression or move to tests/debug/ (with .gitignore)

### Phase 6: Create Test Runner
- Create tests/run_regression.py
- Discover and run all tests in tests/regression/
- Add --category flag for selective testing

### Phase 7: Documentation
- Create tests/README.md
- Document test organization and conventions
- Update main README with testing instructions

---

## Notes

- **utils/test_curses_comprehensive.py** is special - keep in utils/ as documented in CLAUDE.md
- Some tests in root directory are important regression tests
- Many utils/ tests should be promoted to tests/regression/
- Need .gitignore in tests/debug/ to prevent committing temporary tests
- test_clean_install.sh is important for CI/release validation

## References

- See: `docs/dev/TESTING_SYSTEM_ORGANIZATION_TODO.md` for implementation plan
- See: `.claude/CLAUDE.md` for testing documentation requirements
