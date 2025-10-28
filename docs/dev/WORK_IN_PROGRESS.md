# Work in Progress

## Task: Synchronize Curses UI, Help Files, and Documentation with Current TK/Interpreter

**Started:** 2025-10-28
**Status:** In Progress

### Completed So Far

✅ **Phase 1: Audit** (v1.0.157)
- TK UI Feature Audit: 950 lines documenting 60+ features
- Curses vs TK Gap Analysis: 953 lines identifying gaps
- Critical issues identified: Edit-and-Continue, line number display, statement highlighting

✅ **De-Microsoft Project** (v1.0.158)
- Created MBASIC_HISTORY.md with proper disclaimers
- Updated README.md with clear attribution and disclaimers
- Fixed PyPI metadata (setup.py, pyproject.toml)
- Batch-updated 50+ source/doc files
- Preserved external historical docs
- Down to 70 references (mostly appropriate historical context)

### Problem

Over hundreds/thousands of changes focused on TK client and interpreter rewrites:
- Curses UI is outdated and doesn't match TK functionality
- Help files are outdated (written before recent changes)
- Documentation doesn't reflect current state
- Curses editor has line numbers in separate column (wrong - causes indent spacing issues)

### Source of Truth

**TK UI and Interpreter = Current Implementation**
- Use TK as reference for what features should exist
- Use TK editor design (line numbers embedded in text, not separate column)
- Use interpreter as reference for actual behavior

### Tasks

#### Phase 1: Audit Current State
1. ✅ Document all TK UI features (docs/dev/TK_UI_FEATURE_AUDIT.md - 950 lines)
2. ✅ Document all interpreter features (included in TK audit)
3. ✅ List curses UI features and identify gaps (docs/dev/CURSES_VS_TK_GAP_ANALYSIS.md - 953 lines)
4. ⏸️ Review help files for outdated content
5. ⏸️ Review docs for outdated content

**Findings:**
- 60+ features documented in TK UI
- Critical gap: Edit-and-Continue error recovery missing in curses
- Major issue: Line numbers in separate column (causes indent spacing problems)
- High priority: Statement highlighting, Recent Files menu
- Overall: 85% core parity, 40% advanced feature parity

#### Phase 2a: Web UI Rewrite (NiceGUI)
1. ✅ Rename current web UI to `oldweb` (quick prototype, outdated) - v1.0.161
2. ✅ Research NiceGUI testing framework (user fixture for fast tests) - v1.0.160
3. ✅ Create new web UI with NiceGUI from scratch - v1.0.161
4. ✅ Fix ProgramManager import issues (lazy imports failed in test context) - v1.0.162
5. ✅ Test new web UI - All 5 tests passing - v1.0.162
6. ⏸️ Add program execution functionality
7. ⏸️ Add file operations (Open/Save)
8. ⏸️ Complete NiceGUI web UI feature parity with TK

**Rationale:** Current web UI was a quick prototype. Rather than update it to match hundreds of TK changes, faster to rebuild with NiceGUI (impressed with its speed). Can salvage useful code from oldweb.

**Completed (v1.0.161-171):**
- Moved old web UI to `src/ui/oldweb`
- Created `src/ui/web/nicegui_backend.py` (440+ lines)
- Implemented basic UI: menu bar, toolbar, split pane (editor/output), status bar
- Created comprehensive test suite: `tests/nicegui/test_mbasic_web_ui.py` (6 tests)
- Fixed NiceGUI menu API (nested context managers, not bind_menu())
- Fixed ProgramManager imports (moved lazy imports to top of file for test compatibility)
- **Added program execution** (v1.0.164-165):
  - Created SimpleWebIOHandler for web output
  - Implemented tick-based execution with ui.timer()
  - Programs can run and produce output
  - Stop functionality works
- **INPUT UX Research** (v1.0.165-167):
  - Identified INPUT dialog UX issue (blocks game text)
  - Documented inline input as better approach
  - Created TODOs for TK, Web, and Curses INPUT improvements
  - Curses already uses inline input correctly!
- **Web UI Integration** (v1.0.169):
  - Added web backend to mbasic.py entry point
  - Updated requirements.txt with nicegui dependencies
  - Can launch with: python3 mbasic.py --backend web
- **Documentation** (v1.0.170):
  - Created comprehensive README for web UI
  - Documents features, installation, usage, architecture
- **Curses INPUT Verification** (v1.0.171):
  - ✅ Verified curses INPUT uses inline input (correct approach)
  - Created test program: tests/test_curses_input.bas
  - Confirmed this is the model TK and Web should follow
- All 6 tests passing:
  - ✅ test_ui_loads - UI loads without errors
  - ✅ test_add_program_line - Can add BASIC lines
  - ✅ test_new_program - File > New clears program
  - ✅ test_clear_output - Clear output works
  - ✅ test_list_program - List Program outputs to console
  - ✅ test_run_program - Program execution works!

**Next Steps:**
- ⏸️ Implement inline INPUT for web UI (see docs/dev/WEB_UI_INPUT_UX_TODO.md)
- ⏸️ Replace TK INPUT dialog with inline input (see docs/dev/TK_UI_INPUT_DIALOG_TODO.md)
- ⏸️ Add file operations to web UI (Open/Save)

#### Phase 2b: Update Curses UI
1. ⏸️ Fix editor line number display (embed in text like TK)
2. ⏸️ Add missing TK features to curses
3. ⏸️ Test curses UI matches TK behavior

#### Phase 3: Update Help Files
1. ⏸️ Update help files to reflect current features
2. ⏸️ Test help content is accurate

#### Phase 4: Update Documentation
1. ⏸️ Update docs to reflect current state
2. ⏸️ Remove outdated information

### Key Issues to Address

**Curses Editor Line Numbers:**
- Currently: Separate column for line numbers
- Problem: Causes indent spacing to be wrong vs real MBASIC/TK
- Solution: Embed line numbers in text like TK does

**Feature Parity:**
- TK has many features curses doesn't
- Need to identify and implement missing features

**Documentation Accuracy:**
- Help files describe features that may have changed
- Docs may reference old behavior
