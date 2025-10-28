# Work in Progress

## Current Session: 2025-10-28 - Architecture and Safety

### Session Summary ✅ COMPLETED

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

- **Version**: 1.0.103
- **Status**: Architecture mature, safety features complete
- **Blocking Issues**: None
- **Ready for**: New features or refinements
- **Recent**: v1.0.100-102 stack validation, v1.0.103 docs deployment

## Next Steps (when resuming)

1. ✅ **RENUM with position adjustment** - COMPLETED (v1.0.92, v1.0.94)
2. ✅ **Single source of truth** - COMPLETED (v1.0.95) - Removed source_text, AST is only source
3. **Investigate 57 changed files** - Why aren't they perfectly preserved?
4. **Settings system** - Configuration for case conflict handling, etc.
5. **Fix MkDocs strict mode errors** - See FIX_MKDOCS_STRICT_MODE_TODO.md

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
