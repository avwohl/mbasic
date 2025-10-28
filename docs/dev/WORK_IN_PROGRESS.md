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

## Completed: Test Organization (Phase 1-5)

**Completed:** 2025-10-28 (v1.0.140-144)
**Task:** Organize 35 test files into proper test structure

### Summary

✅ **All phases complete!**
- Phase 1: Inventory (35 tests categorized)
- Phase 2: Directory structure created
- Phase 3: Tests moved to appropriate locations (26 files)
- Phase 4: Import system refactored (13 src/ files fixed)
- Phase 5: Documentation complete

**Key achievements:**
- Created organized test structure: `tests/regression/`, `tests/manual/`, `tests/debug/`
- Built test runner with discovery, filtering, and timeout protection
- Fixed import system across entire codebase (bare imports → `src.` prefixed)
- Comprehensive documentation (`tests/README.md`, updated main `README.md`)
- ✅ **ALL REGRESSION TESTS PASSING**

### Files Modified (v1.0.140-144)

**Structure:**
- Created: `tests/regression/{commands,debugger,editor,help,integration,interpreter,lexer,parser,serializer,ui}/`
- Created: `tests/manual/` with 3 files
- Created: `tests/debug/` with .gitignore and README.md
- Created: `tests/run_regression.py` - test runner framework
- Moved: 26 test files from root/utils to organized structure

**Import fixes (v1.0.143):**
- Fixed: 10 src/ modules (lexer, parser, interpreter, runtime, etc.)
- Fixed: 3 src/ui/ modules (tk_ui, curses_ui, visual)
- Fixed: All iohandler, input_sanitizer, editing, filesystem imports
- Fixed: All test files to use proper import depth

**Documentation (v1.0.144):**
- Created: `tests/README.md` (comprehensive testing guide)
- Updated: Main `README.md` (testing section and project structure)

### Result

Test organization is **complete and functional**:
```bash
$ python3 tests/run_regression.py
✅ ALL REGRESSION TESTS PASSED
```

---

## Completed: PyPI Distribution Preparation

**Completed:** 2025-10-28 (v1.0.147-148)
**Task:** Prepare MBASIC for PyPI distribution

### Summary

✅ **Package fully prepared and ready for publication!**

**Key files created/updated:**
- ✅ `pyproject.toml` - Updated to v1.0.147 with correct metadata
- ✅ `mbasic.py` - Entry point already configured (main() function)
- ✅ `MANIFEST.in` - Already configured with all necessary files
- ✅ `docs/dev/DISTRIBUTION_TESTING.md` - Complete testing and publishing guide
- ✅ `utils/build_package.sh` - Automated build and test script
- ✅ `README.md` - Updated with PyPI status

### What's Ready

**Package configuration:**
- Version: 1.0.147
- Zero dependencies for core functionality
- Optional dependencies for curses/tk UIs
- Entry point: `mbasic` command
- Includes docs, help files, and example programs

**Build and test:**
- Build script: `./utils/build_package.sh`
- Test locally: `./utils/build_package.sh --test`
- Upload to TestPyPI: `./utils/build_package.sh --test-pypi`

**Documentation:**
- Complete guide: `docs/dev/DISTRIBUTION_TESTING.md`
- Pre-publication checklist included
- Emergency procedures documented

### Next Steps (When Ready to Publish)

1. **Install build tools** (requires venv):
   ```bash
   python3 -m venv venv-build
   source venv-build/bin/activate
   pip install build twine
   ```

2. **Build package**:
   ```bash
   ./utils/build_package.sh
   ```

3. **Test locally**:
   ```bash
   ./utils/build_package.sh --test
   ```

4. **(Optional) Test on TestPyPI**:
   ```bash
   ./utils/build_package.sh --test-pypi
   ```

5. **Publish to PyPI** (NEEDS EXPLICIT APPROVAL):
   ```bash
   python3 -m twine upload dist/*
   ```

See `docs/dev/DISTRIBUTION_TESTING.md` for complete instructions.

---

## Status: Ready for Next Task

### Potential Next Tasks

1. **Keyword Case Error Policy** (Core implemented, UI integration pending)
   - Core implementation: ✅ CaseKeeperTable raises ValueError on conflicts
   - Integration needed: Surface errors to editor/parser UI
   - Note: Mechanism works, needs better error reporting in UIs

2. **PyPI Distribution**
   - Package and publish to PyPI
   - See: `docs/dev/SIMPLE_DISTRIBUTION_APPROACH.md`

3. **Additional UI Integration**
   - Add settings UI to curses/TK interfaces
   - Currently settings work via CLI commands only

4. **Help System Enhancements**
   - Add history tracking
   - Add bookmarks
   - Improve search UX

**Deferred to future:** Pretty Printer Spacing Options (see `docs/future/`)

---

## Instructions

When starting new work:
1. Update this file with task description and status
2. List files being modified
3. Track progress with checkmarks
4. When complete, move to `docs/history/` and clear this file
