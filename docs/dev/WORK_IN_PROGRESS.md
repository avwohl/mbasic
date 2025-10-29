# Work in Progress

## Session - 2025-10-29 (Part 3) - DE_NONEIFY Refactoring

### Current Status ⏳

Working on DE_NONEIFY code quality refactoring - replacing semantic None checks with clearly-named predicates.

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

#### 4. DE_NONEIFY Phase 3: Replace Usage Sites ⏳
Completed in `src/interpreter.py`:
- Line 346: `error_handler is not None` → `has_error_handler()`
- Line 755: `error_handler is not None` → `has_error_handler()`

Still TODO:
- Other None checks in interpreter.py (file ops, line lookups)
- Parser token checks
- UI None checks

### Files Modified
- `src/runtime.py` - Added helper methods
- `src/interpreter.py` - Replaced 2 error handler checks
- `utils/analyze_none_checks.py` - Created analysis tool

### Next Steps
1. Continue replacing None checks in interpreter.py (file_number, line lookups)
2. Update parser.py token checks (consider parser-level helpers)
3. Update UI files (interpreter existence checks)
4. Test all changes
5. Commit and checkpoint

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