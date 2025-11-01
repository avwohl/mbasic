# TODO: Eliminate Data Duplication Between ProgramManager and Runtime

## Problem

Currently, program data is duplicated in two places:

1. **ProgramManager** (`self.program`):
   - `self.lines` - Dict of line_number -> line_text
   - `self.line_asts` - Dict of line_number -> LineNode AST

2. **Runtime** (`self.runtime`):
   - Takes a copy of line_asts and lines in constructor
   - Builds `statement_table` from the ASTs
   - Stores `line_text_map` for error messages

## Why This Is Bad

Violates the "no copy" rule:
- Data gets out of sync
- Memory waste
- Must call `runtime.reset_for_run()` to sync data
- Breakpoints need statement table, but it's not populated until run

## Current Workaround

In `_save_editor_to_program()`, we call `runtime.reset_for_run()` after parsing
to keep the statement table in sync. This works but is a band-aid.

## Proper Solution

**Runtime should reference ProgramManager data directly, not copy it.**

### Proposed Design:

1. Runtime takes a reference to ProgramManager (or just its data dicts)
2. Runtime.statement_table is rebuilt on-demand or via explicit update
3. Remove `_ast_or_line_table` and `line_text_map` from Runtime
4. Use ProgramManager.lines and ProgramManager.line_asts directly

### Benefits:

- Single source of truth for program data
- No sync issues
- Statement table always available for breakpoints
- Less memory usage
- Cleaner architecture

## Files Affected

- `src/runtime.py` - Runtime constructor and reset methods
- `src/ui/web/nicegui_backend.py` - How Runtime is created
- `src/ui/tk_ui.py` - TK UI Runtime usage
- `src/ui/curses_ui.py` - Curses UI Runtime usage
- Other UI backends

## Priority

Medium - current workaround is functional but architectural debt
