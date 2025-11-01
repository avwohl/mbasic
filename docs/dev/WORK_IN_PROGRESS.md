# Work in Progress: CodeMirror 6 Migration for Web UI

**Status:** IN PROGRESS - Implementing CodeMirror 6 editor

**Task:** Replace plain `ui.textarea()` with CodeMirror 6 to enable proper text highlighting for find results, breakpoints, and step debugging.

**Last Updated:** 2025-11-01

## Current Status

Starting CodeMirror 6 integration to solve fundamental text highlighting limitations.

## Files Being Modified

- `src/ui/web/nicegui_backend.py` - Replace textarea with CodeMirror
- Possibly new: `src/ui/web/codemirror_wrapper.py` - CodeMirror component wrapper (TBD)

## Implementation Plan (from WEB_UI_TEXT_HIGHLIGHTING_TODO.md)

### Part 1: CodeMirror Integration - IN PROGRESS
- [ ] Load CodeMirror 6 via CDN
- [ ] Create minimal editor instance
- [ ] Wire up basic text editing (get/set content)
- [ ] Event handlers for content changes
- [ ] Replace textarea in nicegui_backend.py

### Part 2: Find Highlighting - TODO
- [ ] Create yellow highlight decoration type
- [ ] Apply to found text ranges
- [ ] Persist across dialog open/close
- [ ] Remove flicker/scroll issues

### Part 3: Breakpoint Markers - TODO
- [ ] Add line gutter for breakpoints
- [ ] Show red circle/dot markers
- [ ] Click gutter to toggle breakpoint
- [ ] Update when breakpoints added/removed

### Part 4: Current Statement Highlighting - TODO
- [ ] Green/blue background for executing line
- [ ] Update during step/next/continue
- [ ] Clear when program finishes

### Part 5: Testing - TODO
- [ ] Test find + highlight
- [ ] Test breakpoint gutter markers
- [ ] Test step debugging highlight
- [ ] Test all features together

## Next Steps

1. Research CodeMirror 6 basic setup with NiceGUI
2. Create minimal working editor
3. Test basic editing operations

## Blockers

None currently

---

**Previous Work Completed**

**Recent Completions (October 31 - Language Testing):**
- ✅ Expanded test suite from 7 to 31 tests (343% increase)
- ✅ Fixed DEFINT/DEFSNG/DEFDBL/DEFSTR implementation
- ✅ Fixed duplicate line number bug in error messages
- ✅ Achieved 100% test coverage of all MBASIC 5.21 language features
- ✅ All tests passing: 31 passed, 0 failed, 0 skipped
- ✅ Documentation: TEST_COVERAGE_MATRIX.md, LANGUAGE_TESTING_DONE.md

**Recent Completions (October 31 - Variable Sorting Refactoring):**
- ✅ Created common variable sorting helper (src/ui/variable_sorting.py)
- ✅ Refactored Tk UI to use common helper (~30 lines removed)
- ✅ Refactored Curses UI to use common helper
- ✅ Refactored Web UI to use common helper
- ✅ Implemented Tk-style variable column header in web UI
- ✅ Removed silly type/value sorting from all UIs (4 useful modes remain)
- ✅ Fixed web UI layout confusion (dynamic column header)
- ✅ Documentation: VARIABLE_SORT_REFACTORING_DONE.md

**Recent Completions (October 29-30 - Web UI):**
- ✅ Fixed all NiceGUI dialog double-click bugs (proper pattern: create once, reuse)
- ✅ Refactored all 10 dialogs to use proper NiceGUI pattern
- ✅ Added web UI feature parity: variables window, stack window, sortable columns
- ✅ Fixed paste handling to remove blank lines
- ✅ Fixed default variable sort order
- ✅ Reverted broken Ctrl+C signal handling
- ✅ Documentation: NICEGUI_DIALOG_PATTERN.md

**Recent Completions (October 28 - Documentation & Web UI):**
- ✅ Fixed web UI output display (removed polling, push-based architecture)
- ✅ Fixed all broken documentation links
- ✅ Re-enabled mkdocs strict mode validation
- ✅ Auto-generated "See Also" sections for 75+ help files
- ✅ Improved help browser (3-tier welcome page)
- ✅ Added mkdocs validation to checkpoint.sh

**Project Status:**
- Version: 1.0.316
- All UIs working: CLI, Curses, Tk, Web
- Documentation: 75+ help files, fully cross-referenced
- Variable sorting: Common helper, consistent across all UIs
- Tests: All passing

For active TODO items, see `docs/dev/*_TODO.md` files.
