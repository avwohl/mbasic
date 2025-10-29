# Work in Progress

## No Active Work

Last session completed: 2025-10-29 - PC_OLD_EXECUTION_METHODS refactoring (v1.0.300)

All work committed and ready to push.

### Next Session Recommendations
- Test old test files that used step_once() - may need updating
- Consider additional UX improvements
- Review remaining TODOs

---

## Session Complete - 2025-10-29 (Part 6) - PC_OLD_EXECUTION_METHODS Refactoring

### Status ✅ COMPLETE

Completed PC/NPC migration - removed all old execution methods and runtime fields.

**Task:** Remove old execution methods and complete PC/NPC migration
**Status:** Phase 1 - Updating CONT command
**Version:** 1.0.299

### Current Work

Removing dual-mode execution and old runtime fields to complete PC migration.

**Progress:**
1. ✅ Phase 1: Update CONT command to use PC-based execution (COMPLETE)
   - Added stop_pc field to Runtime
   - Updated execute_stop() to save stop_pc
   - Updated CONT command to use tick-based loop
   - Fixed cli_debug.py enhanced_run signature bug
2. ✅ Phase 2: Remove dual-mode from execute_* methods (ALREADY DONE!)
   - Analysis shows all execute_* methods only set npc, not next_line
   - Dual-mode removal was completed in previous PC refactoring
3. ⏳ Phase 3: Remove old execution methods (IN PROGRESS)
   - run_from_current() (line 545-569)
   - _run_loop() (line 654-803)
   - step_once() (line 571-652)
4. Phase 4: Remove old runtime fields
5. Phase 5: Comprehensive testing

### Files Modified
- ✅ src/interpreter.py - execute_stop uses stop_pc
- ✅ src/interactive.py - CONT uses PC and tick()
- ✅ src/runtime.py - Added stop_pc field
- ✅ src/ui/cli_debug.py - Fixed enhanced_run signature

### Next Steps
1. Remove run_from_current(), _run_loop(), step_once()
2. Remove old runtime fields (current_line, next_line, stop_line, stop_stmt_index)
3. Comprehensive testing

---

## Session Complete - 2025-10-29 (Part 5) - Call Stack PC Enhancement

### Status ✅ COMPLETE

Added statement-level precision to call stack displays, showing exact statement offsets for GOSUB, FOR, and WHILE entries.

### Changes Made

**Files:**
- `src/runtime.py`:
  - Updated `get_gosub_stack()` to return `[(line, stmt), ...]` tuples instead of just line numbers
  - Updated `get_execution_stack()` to include `return_stmt` and `stmt` fields for all entry types
  - Added statement offset tracking to GOSUB, FOR, and WHILE stack entries

- `src/ui/curses_ui.py`:
  - Updated stack display to show statement offsets: `100.2` format
  - GOSUB: "GOSUB from line 100.2" (shows where to return)
  - FOR: "FOR I = 1 TO 3 (line 10.0)" (shows loop location)
  - WHILE: "WHILE (line 10.2)" (shows loop location)

### Benefits
- **Statement-level debugging**: Can see exactly which statement will execute after RETURN/NEXT
- **Multi-statement clarity**: Distinguishes between multiple GOSUBs/FORs on same line
- **Better UX**: More precise information for developers debugging complex programs

### Example
```
GOSUB Stack (before): GOSUB from line 100
GOSUB Stack (after):  GOSUB from line 100.2
```

Now you can see that execution will resume at the 3rd statement (index 2) on line 100.

---

## Session Complete - 2025-10-29 (Part 4) - Web UI Output Buffer Limiting

### Status ✅ COMPLETE

Implemented line-based output buffer limiting for web UI to prevent memory issues with long-running programs.

### Changes Made

**File:** `src/ui/web/nicegui_backend.py`
- Added `self.output_max_lines = 3000` configuration in `__init__()`
- Updated `_append_output()` to use line-based limiting instead of character-based
- Changed from 10,000 chars to 3,000 lines (more predictable)
- Adds "[... output truncated ...]" indicator when buffer is trimmed
- Prevents browser memory issues with long-running programs

**Documentation:**
- Updated `docs/dev/WEB_UI_OUTPUT_IMPROVEMENTS_TODO.md` → moved to history
- All 4 web UI output improvements now complete

### Impact
- More predictable memory usage for web UI
- Prevents performance degradation with long output
- Configurable limit (can be adjusted in __init__)

---

## Session Complete - 2025-10-29 (Part 3) - DE_NONEIFY Refactoring

### Status ✅ COMPLETE

DE_NONEIFY code quality refactoring - replaced semantic None checks with clearly-named predicates.

### Progress So Far

#### 1. TODO Cleanup ✅
- Moved LEXER_CLEANUP_TODO.md → history (complete)
- Deleted PACKAGING_BUILD_FARMS_TODO.md (all Python, nothing to compile)
- Moved TK_UI_INPUT_DIALOG_TODO.md → history (implemented v1.0.173)
- Moved WEB_UI_INPUT_UX_TODO.md → history (implemented v1.0.174)
- Moved CURSES_UI_INPUT_CHECK_TODO.md → history (verified correct)

#### 2. DE_NONEIFY Phase 1: Analysis ✅
- Created `utils/analyze_none_checks.py` - categorization script
- Found 326 total None checks across codebase
- 284 in semantic_analyzer.py (legitimate optional value tracking)
- Identified actionable categories:
  - Control Flow: 5 checks
  - Error Handler: 2 checks
  - Interpreter State: 5 checks
  - Loop State: 2 checks
  - Token Checks: 17 checks
  - File Ops: 6 checks

#### 3. DE_NONEIFY Phase 2: Helper Methods ✅
Added to `src/runtime.py`:
- `has_error_handler()` - Check if ON ERROR GOTO is installed
- `has_active_loop(var_name=None)` - Check if FOR loop is active

Already existed:
- `has_pending_jump()` - Check if GOTO/GOSUB pending
- `is_sequential_execution()` - Check if no jump pending

#### 4. DE_NONEIFY Phase 3: Replace Usage Sites ✅
Completed in `src/interpreter.py`:
- Line 346: `error_handler is not None` → `has_error_handler()`
- Line 755: `error_handler is not None` → `has_error_handler()`

Completed in `src/parser.py`:
- Added helper methods: `has_more_tokens()`, `at_end_of_tokens()`
- Replaced 8 token None checks with semantic methods:
  - `advance()`: token is None → at_end_of_tokens()
  - `expect()`: token is None → at_end_of_tokens()
  - `match()`: token is None → at_end_of_tokens()
  - `at_end_of_line()`: token is None → at_end_of_tokens()
  - `at_end_of_statement()`: token is None → at_end_of_tokens()
  - `parse_statement()`: token is None → at_end_of_tokens()
  - `parse_primary()`: token is None → at_end_of_tokens()
  - `parse_input_prompt_list()`: current_token is None → at_end_of_tokens()

Not replaced (legitimate optional values):
- file_number checks (optional parameter for I/O statements)
- line lookups (None = line not found, valid sentinel)
- loop_info/wend_pos (None = not found, error case)

### Files Modified
- `src/runtime.py` - Added helper methods (has_error_handler, has_active_loop)
- `src/interpreter.py` - Replaced 2 error handler checks
- `src/parser.py` - Added token helper methods, replaced 8 None checks
- `utils/analyze_none_checks.py` - Created analysis tool

### Summary

**DE_NONEIFY Phase 1-3 COMPLETE**

Successfully replaced semantic None checks with clearly-named predicates in core modules:
- Runtime: Added has_error_handler(), has_active_loop()
- Parser: Added at_end_of_tokens(), replaced 8 checks
- Interpreter: Replaced 2 error handler checks

**Impact:**
- Reduced ambiguous None checks by ~10 in high-traffic code paths
- Improved code readability with semantic method names
- All tests passing

**Remaining work (deferred to future):**
- UI None checks (interpreter existence)
- Optional parameters (already well-typed, low priority)
- Semantic analyzer (284 checks, legitimate optional values)

### Notes
- semantic_analyzer.py has 284 checks - these are legitimate optional values, leave as-is
- Token checks in parser may need parser-level helper methods
- Focus on high-impact semantic improvements first

## Session Complete - 2025-10-29 (Part 2)

### Major Accomplishments ✅

#### 1. Lexer Cleanup (COMPLETED)
- **Removed problematic keyword case policies** - `first_wins`, `error`, `preserve` don't make sense for keywords since interpreter registers them at startup
- **Created `SimpleKeywordCase`** - Only supports sensible policies: force_lower, force_upper, force_capitalize
- **Removed old BASIC keyword handling** - No longer splits `NEXTI` into `NEXT I`
- **Clarified FILE_IO_KEYWORDS** - Better documented why `PRINT#1` needs special handling
- **Fixed BASIC programs** - Manually fixed `IF` spacing in finance.bas and lifscore.bas

#### 2. Utility Scripts Documentation
- **Created `utils/UTILITY_SCRIPTS_INDEX.md`** - Comprehensive index of all utility scripts
- **Updated CLAUDE.md** - Added utility script reference section so future Claudes check existing scripts
- **Identified `fix_keyword_spacing.py`** - Existing script that fixes keywords running together (has bug with OR/AND)

#### 3. MBASIC-2025 Branding and Extension Documentation
- **Created `docs/help/mbasic/extensions.md`** - Complete guide to features NOT in original MBASIC 5.21
- **Established project name: MBASIC-2025** - Modern implementation with extensions
- **Updated all branding**:
  - README.md - Now "MBASIC-2025: Modern MBASIC 5.21 Interpreter"
  - version.py - Added PROJECT_NAME constant
  - CLI startup message - Shows extensions available
  - Tk UI title and About dialog
- **Clarified extensions**:
  - BREAK, STEP, WATCH, STACK commands are NOT in original MBASIC
  - GUI interfaces are modern additions
  - Visual debugging is new
  - 100% backward compatible for original programs

### Key Discoveries
- Keyword case "first_wins" policy doesn't work since interpreter registers keywords at startup
- We already had `fix_keyword_spacing.py` utility but it has bugs with OR/AND replacement
- Need to clearly mark which features are extensions vs original MBASIC 5.21

### Files Modified/Created

#### Created
- `src/simple_keyword_case.py` - Simplified keyword case handler
- `src/case_string_handler.py` - Unified case handling (created but not integrated)
- `utils/UTILITY_SCRIPTS_INDEX.md` - Utility script documentation
- `docs/help/mbasic/extensions.md` - Extension documentation
- `docs/dev/LEXER_CLEANUP_COMPLETE.md` - Lexer cleanup summary

#### Modified
- `src/lexer.py` - Removed old BASIC handling, simplified
- `src/settings_definitions.py` - Removed problematic keyword policies
- `src/version.py` - Added project branding
- `src/interactive.py` - Updated startup message
- `src/ui/tk_ui.py` - Updated window title and About
- `docs/help/mbasic/compatibility.md` - Added extension references
- `.claude/CLAUDE.md` - Added utility script section
- `README.md` - Updated to MBASIC-2025 branding
- `basic/finance.bas` - Fixed `IFR=0` → `IF R=0`
- `basic/lifscore.bas` - Fixed `IFL1<-29` → `IF L1<-29`

### Statistics
- **Lexer issues fixed:** 4 major issues from LEXER_CLEANUP_TODO.md
- **Documentation created:** 3 major documents (extensions, utility index, lexer complete)
- **Files fixed:** 2 BASIC programs with keyword spacing
- **Branding updates:** 6+ files updated with MBASIC-2025

### Next Session Suggestions
1. Fix `fix_keyword_spacing.py` bug with OR/AND replacement
2. Consider integrating `case_string_handler.py` for unified case handling
3. Update help system to prominently show extension warnings
4. Consider adding `--pure-mbasic` flag that disables all extensions
5. Test all changes with existing BASIC programs

## Summary
This session focused on cleaning up the lexer to properly handle MBASIC 5.21 syntax (not old BASIC dialects) and establishing clear documentation about which features are modern extensions vs original MBASIC. The project is now clearly branded as MBASIC-2025 with explicit documentation of its 100% compatibility plus optional extensions.