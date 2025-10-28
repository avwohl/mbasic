# Work in Progress

## Current Session: 2025-10-28 - Settings System Implementation

### Session Summary ✅ COMPLETED

Implemented comprehensive settings system with CLI commands and variable case conflict handling.

### Completed Tasks

1. **Settings Infrastructure** (v1.0.104)
   - Created `src/settings.py` - SettingsManager with load/save/validate
   - Created `src/settings_definitions.py` - Setting definitions and types
   - Supports global settings (~/.mbasic/settings.json)
   - Scope precedence: file > project > global > default
   - JSON-based configuration format

2. **Setting Definitions** (v1.0.104)
   - Added 11 initial settings across 4 categories
   - Variables: `case_conflict`, `show_types_in_window`
   - Editor: `auto_number`, `auto_number_step`, `tab_size`, `show_line_numbers`
   - Interpreter: `strict_mode`, `max_execution_time`, `debug_mode`
   - UI: `theme`, `font_size`
   - Type validation with min/max/choices constraints

3. **CLI Commands** (v1.0.104)
   - Added `SET "setting.name" value` command
   - Added `SHOW SETTINGS ["pattern"]` command
   - Added `HELP SET "setting.name"` command
   - Token types: SET, SHOW, SETTINGS, HELP
   - AST nodes: SetSettingStatementNode, ShowSettingsStatementNode, HelpSettingStatementNode
   - Parser support for all three commands
   - Interpreter execution handlers with type conversion and validation

4. **Bug Fixes** (v1.0.105)
   - Fixed io.output() method calls (was using io.write())
   - Fixed type hints (removed ast_nodes. prefix)
   - All commands tested and working

### Files Modified/Created

**v1.0.104 - Settings Infrastructure:**
- `src/settings.py` - NEW: Settings manager with load/save/validate
- `src/settings_definitions.py` - NEW: Setting definitions and types
- `src/tokens.py` - Added SET, SHOW, SETTINGS, HELP tokens
- `src/ast_nodes.py` - Added SetSettingStatementNode, ShowSettingsStatementNode, HelpSettingStatementNode
- `src/parser.py` - Added parse_set_setting(), parse_show_settings(), parse_help_setting()
- `src/interpreter.py` - Added execute_setsetting(), execute_showsettings(), execute_helpsetting()

**v1.0.105 - Bug Fixes:**
- `src/interpreter.py` - Fixed io.write() → io.output()
- `src/parser.py` - Fixed type hints

**v1.0.106-108 - Variable Case Conflict Integration:**
- `src/runtime.py` - Added `_variable_case_variants` tracking dictionary
- `src/runtime.py` - Added `_check_case_conflict()` method with 5 policy implementations
- `src/runtime.py` - Updated `get_variable()` to track original_case and detect conflicts
- `src/runtime.py` - Updated `set_variable()` to track original_case and detect conflicts
- `src/runtime.py` - Store `original_case` in variable metadata for all variables
- `src/runtime.py` - Updated `get_all_variables()` to include `original_case` in returned dict
- `src/interpreter.py` - Added `settings_manager` parameter to Interpreter.__init__()
- `src/interpreter.py` - Updated all `get_variable()` calls to pass original_case and settings_manager
- `src/interpreter.py` - Updated all `set_variable()` calls to pass original_case and settings_manager
- `src/interpreter.py` - Fixed `execute_let()` to pass original_case and settings_manager (critical fix)
- `src/ui/tk_ui.py` - Updated `_update_variables()` to display canonical case from `original_case`
- `src/ui/tk_ui.py` - Updated variable filter to use `original_case` for matching
- `test_case_conflict_unit.py` - NEW: Unit tests for case conflict policies (3/3 passing)
- `test_case_conflict_integration.py` - NEW: Integration tests with full AST (2/2 passing)
- All 5 test cases passing: first_wins, prefer_upper, prefer_lower, error, variable window display

**Case Conflict Policies Implemented:**
1. `first_wins` (default) - First occurrence sets case, silent
2. `error` - Raises RuntimeError on conflict with line numbers
3. `prefer_upper` - Choose version with most uppercase letters
4. `prefer_lower` - Choose version with most lowercase letters
5. `prefer_mixed` - Prefer mixed case (camelCase/PascalCase)

### Next Steps

1. **Fix CHAIN/MERGE Case Handling** - Critical bug in `update_variables()`
   - See `docs/dev/CASE_CONFLICT_WITH_CHAIN_MERGE_COMMON.md` for analysis
   - Bug: `update_variables()` uses `set_variable_raw()` - bypasses case checking
   - Impact: CHAIN ALL loses original_case, variable window shows wrong case
   - Solution: Update `update_variables()` to preserve `original_case` metadata
   - Priority: HIGH (affects variable display after CHAIN)

2. **Keyword Case Handling** - Extend case conflict to keywords (separate `keywords.case_style` setting)
   - See `docs/dev/KEYWORD_CASE_HANDLING_TODO.md` for design
   - Default: `force_lower` (MBASIC 5.21 style)
   - Policies: force_lower, force_upper, first_wins, error, preserve

3. **Documentation** - Document case conflict system and TK UI improvements

4. **Additional UI Integration** - Add settings to curses/TK UIs

5. **Pretty Printer Settings** - Add configurable spacing options

6. **Settings Scope Testing** - Test project/file-level settings

7. **Simple Distribution via PyPI** - Pure Python = simple distribution!
   - ~~Build farms OVERKILL for interpreted Python~~ (see PACKAGING_BUILD_FARMS_TODO.md for why)
   - See `docs/dev/SIMPLE_DISTRIBUTION_APPROACH.md` for recommended approach
   - **Recommended**: Publish to PyPI (30 minutes work)
   - Users: `pip install mbasic` - works everywhere (Linux, Mac, Windows, all architectures)
   - Optional: GitHub Releases with zip files
   - Optional later: Desktop integration (.desktop files) if needed

## Previous Session: 2025-10-28 - Architecture and Safety ✅ COMPLETED

Major architectural improvements - single source of truth, stack validation, and documentation fixes.

## Previous Session: 2025-10-27 - Spacing, Case, and RENUM Preservation ✅ COMPLETED

Major work on preserving original source formatting - spacing, variable case, and RENUM with position preservation.

### Completed Tasks

1. **Position-Aware Serialization** (v1.0.89)
   - Created `position_serializer.py` with conflict detection
   - Fast path: uses original `source_text` from LineNode
   - Fallback: reconstructs from AST with position tracking
   - Debug mode reports position conflicts
   - Test results: 28.9% of files (107/370) preserved exactly
   - All unit tests passing for spacing preservation

2. **Case-Preserving Variables** (v1.0.90)
   - Added `original_case` field to Token and VariableNode
   - Lexer stores original case before lowercasing
   - Parser preserves case in VariableNode
   - Serializers output original case
   - Lookup remains case-insensitive
   - Test results: 9/10 tests passing
   - Historical note: approach by William Wulf (CMU, 1984)

3. **RENUM with Spacing Preservation** (v1.0.92, v1.0.94)
   - Implemented `renumber_with_spacing_preservation()` function
   - Updates all line number references: GOTO, GOSUB, ON GOTO, ON GOSUB, IF THEN, ON ERROR, RESTORE, RESUME, ERL comparisons
   - v1.0.92: Initially used source_text surgical editing
   - v1.0.94: Perfected with surgical text replacement (before single source refactor)
   - Test results: All tests passing (5/5 basic, 1/1 complex)

4. **Single Source of Truth** (v1.0.95)
   - Removed `source_text` field from LineNode
   - AST is now the ONLY source - text always regenerated from positions
   - Removed fast path in position_serializer
   - Simplified RENUM to adjust AST positions only
   - Updated parser to not store source_text
   - All tests still passing

5. **Documentation and Bug Fixes** (v1.0.96-99)
   - v1.0.96-97: Fixed docs deployment workflow (removed strict mode temporarily)
   - v1.0.98: Updated WORK_IN_PROGRESS.md
   - v1.0.99: Fixed REM statement serialization (text field not comment)

6. **Edit-at-Breakpoint Stack Validation** (v1.0.100-102)
   - Added `validate_stack()` method to Runtime
   - Validates FOR/GOSUB/WHILE return addresses after program edits
   - Integrated into tk_ui continue handler with warning messages
   - Prevents crashes when user edits code at breakpoints
   - Moved completed TODO to history

7. **MkDocs Strict Mode Fix** (v1.0.103)
   - Simplified nav structure to use auto-discovery (awesome-pages plugin)
   - Re-enabled strict mode in deployment workflow
   - Moved completed TODO to history

### Files Modified

**v1.0.89 - Spacing Preservation:**
- `src/position_serializer.py` - NEW: Position-aware serialization with conflict tracking
- `test_position_serializer.py` - NEW: Comprehensive test suite
- `tests/type_suffix_test.bas` - NEW: Test for type suffix behavior

**v1.0.90 - Case Preservation:**
- `src/tokens.py` - Added `original_case` field to Token
- `src/lexer.py` - Store original case before lowercasing
- `src/ast_nodes.py` - Added `original_case` field to VariableNode
- `src/parser.py` - Preserve case when creating VariableNodes
- `src/position_serializer.py` - Output variables with original case
- `src/ui/ui_helpers.py` - Output variables with original case
- `test_case_preservation.py` - NEW: Case preservation test suite

**v1.0.92 - RENUM with Spacing Preservation:**
- `src/position_serializer.py` - Added `renumber_with_spacing_preservation()` function
- `src/position_serializer.py` - Fixed serialize_if_statement() to handle then_line_number
- `src/position_serializer.py` - Fixed serialize_goto/gosub_statement() to use line_number field
- `src/position_serializer.py` - Added helper functions to update line references in AST
- `test_renum_spacing.py` - NEW: RENUM spacing preservation test suite

**v1.0.94 - Perfect RENUM Spacing:**
- `src/position_serializer.py` - Rewrote RENUM with surgical text editing approach
- `src/position_serializer.py` - Added position adjustment helpers
- All spacing perfectly preserved through RENUM

**v1.0.95 - Single Source of Truth:**
- `src/ast_nodes.py` - Removed source_text field from LineNode
- `src/parser.py` - Removed code that stored source_text
- `src/position_serializer.py` - Removed fast path, always serialize from AST
- `src/position_serializer.py` - Simplified RENUM to only adjust positions
- `test_renum_spacing.py` - Updated to regenerate text from AST

### Documentation Created

- `docs/dev/PRESERVE_ORIGINAL_SPACING_TODO.md` - Complete plan for spacing preservation
- `docs/dev/CASE_PRESERVING_VARIABLES_TODO.md` - Complete plan for case preservation
- `docs/dev/SETTINGS_SYSTEM_TODO.md` - Plan for configuration system
- `docs/dev/VARIABLE_TYPE_SUFFIX_BEHAVIOR.md` - Documentation of type suffix rules
- `docs/dev/EXPLICIT_TYPE_SUFFIX_WITH_DEFSNG_ISSUE.md` - Analysis of DEFSNG interaction

### Key Features

**Spacing Preservation:**
- Preserves exact spacing as typed: `X=Y+3` stays `X=Y+3`, not `X = Y + 3`
- Position conflict detection for debugging
- Fast path uses original source_text
- Fallback reconstructs from AST

**Case Preservation:**
- Variables display as typed: `TargetAngle`, `targetAngle`, `TARGETANGLE`
- Lookup remains case-insensitive (all refer to same variable)
- Backward compatible - no runtime changes

**RENUM with Spacing Preservation:**
- Renumbers program lines while updating all line number references
- Updates GOTO, GOSUB, ON GOTO, ON GOSUB, IF THEN, ON ERROR, RESTORE, RESUME
- Detects and updates ERL comparisons in expressions
- Regenerates source_text from AST to preserve formatting
- Handles position conflicts by adding spaces when needed

### Test Results

**Spacing Preservation:**
- ✅ 7/7 unit tests passing
- ✅ 107/370 files (28.9%) preserved exactly
- ❌ 57 files changed (need investigation)
- ❌ 206 parse errors (mostly in `bad_syntax/` - expected)

**Case Preservation:**
- ✅ 9/10 unit tests passing (snake_case with underscore not valid BASIC)
- ✅ No regressions in game preservation test

**RENUM with Spacing Preservation:**
- ✅ 5/5 basic tests passing (spacing, GOTO, GOSUB, IF THEN)
- ✅ 1/1 complex test passing (ON GOTO with multiple targets)
- ✅ All line number references correctly updated
- ⚠️ Position conflicts occur when line number length changes (expected behavior)

## Current State

- **Version**: 1.0.105
- **Status**: Settings system implemented, ready for integration
- **Blocking Issues**: None
- **Ready for**: Variable case conflict handling, additional settings integration
- **Recent**: v1.0.104-105 settings system with CLI commands

## Next Steps (when resuming)

1. ✅ **RENUM with position adjustment** - COMPLETED (v1.0.92, v1.0.94)
2. ✅ **Single source of truth** - COMPLETED (v1.0.95) - Removed source_text, AST is only source
3. ✅ **Settings system** - COMPLETED (v1.0.104-105) - Configuration for case conflict handling, etc.
4. **Integrate settings into variable storage** - Use variables.case_conflict setting
5. **Investigate 57 changed files** - Why aren't they perfectly preserved?
6. **Pretty printer spacing settings** - See PRETTY_PRINTER_SPACING_TODO.md

## Important Context

**Design Philosophy:**
All recent work follows the principle of **maintaining fidelity to source code**:
- Type suffix preservation (v1.0.85) - Don't output DEF-inferred suffixes
- Spacing preservation (v1.0.89) - Preserve user's exact spacing
- Case preservation (v1.0.90) - Display variables as user typed them
- RENUM preservation (v1.0.92) - Maintain formatting through renumbering

This respects the programmer's original intent and formatting choices.

**Technical Approach (v1.0.95+):**
- **Single source of truth**: AST is the only source, no source_text stored
- **Always regenerate**: Text generated from AST using token positions
- **Position preservation**: Every token stores line_num and column
- **Position conflicts**: Gracefully handled by adding spaces when needed
- **RENUM**: Adjust token positions, then regenerate from AST
- **Line number updates**: Traverse AST to update all references
