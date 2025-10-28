# Work in Progress

## Current Status: Ready for Next Task

**Version**: 1.0.138 (as of 2025-10-28)

### Recently Completed (v1.0.104-138)

Major work completed on settings system, case handling, documentation system, and help build validation.

**Summary:**
- ✅ Settings infrastructure with CLI commands (SET, SHOW SETTINGS, HELP SET)
- ✅ Variable case conflict handling (5 policies: first_wins, error, prefer_upper, prefer_lower, prefer_mixed)
- ✅ Keyword case handling with table-based architecture (6 policies)
- ✅ Test organization planning (Phase 1 complete: 35 tests inventoried)
- ✅ Critical documentation improvements (real MBASIC testing, test inventory)
- ✅ TK UI help system restructured (582 lines → 95 line index with subsections)
- ✅ Checkpoint script auto-rebuilds help indexes when docs/help/ changes
- ✅ Help build validates macro expansion, fails on unexpanded {{kbd:...}} macros
- ✅ TK keybindings JSON file completed with all editor/view shortcuts

**See:**
- `docs/history/SESSION_2025_10_28_SETTINGS_AND_CASE_HANDLING.md` - Settings system work
- `docs/dev/GITHUB_DOCS_WORKFLOW_EXPLAINED.md` - GitHub Pages deployment explanation

---

## Active Work: Test Organization (Phase 2-3)

**Started:** 2025-10-28
**Task:** Organize 35 test files into proper test structure
**Current Version:** 1.0.141

### Status

- ✅ Phase 1: Inventory complete (35 tests categorized)
- ✅ Phase 2: Directory structure created
- ✅ Phase 3: Tests moved to appropriate locations
  - 6 regression tests from root → tests/regression/
  - 18 regression tests from utils/ → tests/regression/
  - 2 manual tests → tests/manual/
  - 8 debug tests → tests/debug/
  - 2 BASIC fixtures → basic/bas_tests/
- ✅ Test runner script created
- ⏳ Import fixes in progress (src module imports need updating)
- ⏸️ Phase 4: Documentation
- ⏸️ Phase 5: Update main README

### Files Modified (v1.0.140-141)

- Created: `tests/regression/{commands,debugger,editor,help,integration,interpreter,lexer,parser,serializer,ui}/`
- Created: `tests/manual/` with 3 files
- Created: `tests/debug/` with .gitignore and README.md
- Created: `tests/run_regression.py` - test runner framework
- Moved: 26 test files total from root/utils to new structure
- Moved: 2 BASIC test fixtures to basic/bas_tests/

### Remaining Work

1. **Fix src module imports** (HIGH priority)
   - src/lexer.py imports `tokens` instead of `src.tokens`
   - src/parser.py imports `ast_nodes` instead of `src.ast_nodes`
   - All src modules need relative imports or proper package structure
   - This blocks test runner from working correctly

2. **Create tests/README.md**
   - Document test organization
   - Explain categories (regression/manual/debug)
   - Testing guidelines

3. **Create tests/regression/README.md**
   - Document test categories
   - List what belongs in each subdirectory

4. **Create tests/manual/README.md**
   - Instructions for running manual tests
   - What each test does

5. **Update main README.md**
   - Add testing section
   - Document how to run tests

### Next Steps

Either:
A) Fix src module imports (requires package refactoring)
B) Continue with documentation (defer import fixes)

### Potential Next Tasks

1. **Test Organization (Phase 2+)**
   - Create tests/ directory structure
   - Move 25 regression tests to appropriate locations
   - Create test runner script
   - See: `docs/dev/TESTING_SYSTEM_ORGANIZATION_TODO.md`

2. **Keyword Case Error Policy**
   - Implement `error` policy checking at parse/edit time
   - Currently all policies except `error` are working

3. **PyPI Distribution**
   - Package and publish to PyPI
   - See: `docs/dev/SIMPLE_DISTRIBUTION_APPROACH.md`

4. **Additional UI Integration**
   - Add settings UI to curses/TK interfaces
   - Currently settings work via CLI commands only

5. **Pretty Printer Settings**
   - Add configurable spacing options

---

## Instructions

When starting new work:
1. Update this file with task description and status
2. List files being modified
3. Track progress with checkmarks
4. When complete, move to `docs/history/` and clear this file
