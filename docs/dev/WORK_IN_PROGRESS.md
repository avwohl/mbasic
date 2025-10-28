# Work in Progress

## Current Session: 2025-10-27 - Spacing and Case Preservation

### Session Summary ✅ COMPLETED

Major work on preserving original source formatting - both spacing and variable case.

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

### Test Results

**Spacing Preservation:**
- ✅ 7/7 unit tests passing
- ✅ 107/370 files (28.9%) preserved exactly
- ❌ 57 files changed (need investigation)
- ❌ 206 parse errors (mostly in `bad_syntax/` - expected)

**Case Preservation:**
- ✅ 9/10 unit tests passing (snake_case with underscore not valid BASIC)
- ✅ No regressions in game preservation test

## Current State

- **Version**: 1.0.90
- **Status**: Spacing and case preservation complete
- **Blocking Issues**: None
- **Ready for**: Further enhancements

## Next Steps (when resuming)

1. **RENUM with position adjustment** - Preserve spacing through renumbering
2. **Investigate 57 changed files** - Why aren't they perfectly preserved?
3. **Settings system** - Configuration for case conflict handling, etc.
4. **Single source of truth** - Architectural refactor

## Important Context

**Design Philosophy:**
All recent work follows the principle of **maintaining fidelity to source code**:
- Type suffix preservation (v1.0.85) - Don't output DEF-inferred suffixes
- Spacing preservation (v1.0.89) - Preserve user's exact spacing
- Case preservation (v1.0.90) - Display variables as user typed them

This respects the programmer's original intent and formatting choices.
