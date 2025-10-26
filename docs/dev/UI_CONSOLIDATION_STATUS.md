# UI Consolidation Status

## Goal
Move all common UI functionality to `ui_helpers.py` so all UIs (CLI, Tk, Web, Curses) can share the same code.

## Progress

### ✅ Completed
1. **AST Serialization** - Moved to ui_helpers.py
   - `serialize_line()` - LineNode → source text
   - `serialize_statement()` - Statement → text
   - `serialize_variable()` - Variable → text
   - `serialize_expression()` - Expression → text
   - `token_to_operator()` - TokenType → operator string
   - `serialize_program()` - Full program serialization

2. **Error Formatting** - Added to ui_helpers.py
   - `format_error_message()` - General errors
   - `format_syntax_error()` - Parse errors with indicators
   - `format_runtime_error()` - Runtime errors with codes
   - Position conversion utilities

### 🚧 In Progress
3. **Update InteractiveMode** - Replace methods with ui_helpers calls
   - `_serialize_line()` → delegate to `ui_helpers.serialize_line()`
   - `_serialize_statement()` → delegate to `ui_helpers.serialize_statement()`
   - `_serialize_expression()` → delegate to `ui_helpers.serialize_expression()`
   - `_serialize_variable()` → delegate to `ui_helpers.serialize_variable()`

### ⏳ TODO
4. **Update Tk UI** (src/ui/tk_ui.py)
   - Remove temp InteractiveMode creation (line 1999)
   - Use `ui_helpers.serialize_line()` directly (line 2015)
   - Check cmd_renum, cmd_delete, cmd_list for duplication

5. **Update Web UI** (src/ui/web/web_ui.py)
   - Check for command implementations
   - Use ui_helpers for serialization
   - Use ui_helpers for error formatting

6. **Update Curses UI** (src/ui/curses_ui.py)
   - Check cmd_list implementation (line 3009)
   - Use shared utilities where possible

7. **Consolidate Command Logic**
   - Consider moving RENUM/DELETE/LIST logic fully to ui_helpers
   - Or have all UIs delegate to InteractiveMode

## Duplicated Code Found

### RENUM Implementation
**Locations:**
- `interactive.py:724` - cmd_renum()
- `tk_ui.py:1947` - cmd_renum() [duplicates logic + creates temp InteractiveMode]

**Issue:** Tk UI reimplements RENUM and creates temp InteractiveMode just for serialization.

**Solution:** Tk UI should use `ui_helpers.serialize_line()` directly.

### DELETE Implementation
**Locations:**
- `interactive.py:682` - cmd_delete()
- `tk_ui.py:1898` - cmd_delete()

**Need to check:** Is Tk UI duplicating or delegating?

### LIST Implementation
**Locations:**
- `interactive.py:371` - cmd_list()
- `tk_ui.py:1777` - cmd_list()
- `curses_ui.py:3009` - cmd_list()

**Need to check:** Each UI likely needs its own display logic, but should share parsing/formatting.

## Decision Points

### Option 1: Full Delegation
All UIs delegate commands to InteractiveMode:
```python
# In Tk UI
def cmd_renum(self, args):
    self.interactive.cmd_renum(args)
    self._refresh_editor()
```

**Pros:** Single source of truth
**Cons:** Requires InteractiveMode instance in each UI

### Option 2: Shared Utilities (CURRENT)
Core logic in ui_helpers, UIs implement UI-specific parts:
```python
# In Tk UI
def cmd_renum(self, args):
    from ui.ui_helpers import build_line_mapping, serialize_program
    mapping = build_line_mapping(...)
    serialized = serialize_program(self.program.line_asts)
    self._refresh_editor()
```

**Pros:** UI independence, no coupling to InteractiveMode
**Cons:** Some duplication of command parsing

### Option 3: Hybrid
Commands in ui_helpers, UIs call them:
```python
# In ui_helpers
def renum_program(program, new_start, old_start, increment):
    # All RENUM logic here
    return updated_program

# In Tk UI
def cmd_renum(self, args):
    from ui.ui_helpers import renum_program
    result = renum_program(self.program, ...)
    self._refresh_editor()
```

**Pros:** Best of both worlds
**Cons:** Most work to implement

## Recommended Approach

Use **Option 3 (Hybrid)** with these principles:

1. **Core algorithms in ui_helpers**
   - Line renumbering logic
   - AST serialization
   - Error formatting
   - Position calculations

2. **Command parsing in ui_helpers**
   - `parse_renum_args()` ✓ (already exists)
   - `parse_delete_args()` ✓ (already exists)
   - `parse_list_args()` (TODO)

3. **High-level operations in ui_helpers**
   - `renum_program()` (TODO)
   - `delete_line_range()` ✓ (already exists)
   - `list_program()` (TODO)

4. **UI-specific parts stay in UIs**
   - Display/rendering
   - User input handling
   - Editor updates
   - Output formatting (terminal vs GUI vs web)

## Implementation Plan

### Phase 1: Update InteractiveMode ✓ (partially done)
```python
# In interactive.py
def _serialize_line(self, line_node):
    from ui.ui_helpers import serialize_line
    return serialize_line(line_node)
```

### Phase 2: Update Tk UI
```python
# In tk_ui.py - cmd_renum
def cmd_renum(self, args):
    from ui.ui_helpers import (
        parse_renum_args,
        build_line_mapping,
        serialize_line
    )

    new_start, old_start, increment = parse_renum_args(args)
    old_lines = sorted(self.program.line_asts.keys())
    line_mapping = build_line_mapping(old_lines, new_start, old_start, increment)

    # Update line number references
    for line_node in self.program.line_asts.values():
        for stmt in line_node.statements:
            self._renum_statement(stmt, line_mapping)  # Keep this method in interactive
        line_node.line_number = line_mapping[line_node.line_number]

    # Serialize
    new_line_asts = {}
    new_lines = {}
    for old_num in old_lines:
        new_num = line_mapping[old_num]
        line_node = self.program.line_asts[old_num]
        new_line_asts[new_num] = line_node
        new_lines[new_num] = serialize_line(line_node)  # Use ui_helpers!

    self.program.line_asts = new_line_asts
    self.program.lines = new_lines
    self._refresh_editor()
```

### Phase 3: Update Web UI
Check web_ui.py for command implementations and update similarly.

### Phase 4: Testing
- Test CLI (interactive.py)
- Test Tk UI
- Test Web UI
- Test Curses UI
- Verify RENUM preserves indentation across all UIs

## Files to Update

1. ✅ `src/ui/ui_helpers.py` - Add serialization functions
2. ⏳ `src/interactive.py` - Delegate to ui_helpers
3. ⏳ `src/ui/tk_ui.py` - Use ui_helpers, remove temp InteractiveMode
4. ⏳ `src/ui/web/web_ui.py` - Use ui_helpers
5. ⏳ `src/ui/curses_ui.py` - Use ui_helpers
6. ⏳ `docs/dev/UI_HELPERS_GUIDE.md` - Update documentation

## Testing Checklist

### AST Serialization
- [x] CLI: RENUM preserves indentation ✓ Tested - all loop levels preserved
- [x] Tk: RENUM preserves indentation ✓ Tested - ui_helpers logic works correctly
- [ ] Web: RENUM preserves indentation
- [x] All: Comments (' vs REM) preserved ✓ Tested - apostrophe and REM preserved
- [x] All: Variable case normalized ✓ Working - lowercase in serialization
- [x] All: Line structure correct ✓ Working - statements and colons handled

### Command Implementations
- [x] CLI: RENUM works ✓ Tested and committed
- [x] Tk: RENUM works ✓ Uses ui_helpers directly, no temp InteractiveMode
- [ ] Web: RENUM works (if implemented)
- [ ] CLI: DELETE works
- [ ] Tk: DELETE works
- [ ] Web: DELETE works (if implemented)
- [ ] CLI: LIST works
- [ ] Tk: LIST works
- [ ] Curses: LIST works

## Completed Steps

1. ✅ Update InteractiveMode._serialize_* methods to delegate
2. ✅ Update Tk UI cmd_renum to use ui_helpers directly
3. ✅ Check Web UI for command implementations (already using ui_helpers)
4. ✅ Test CLI (RENUM and comment preservation)
5. ✅ Test Tk UI (RENUM logic with ui_helpers)
6. ✅ Commit and push changes

## Status Summary

**Phase 1-3: COMPLETE**
- All serialization functions moved to ui_helpers.py
- InteractiveMode delegates to ui_helpers
- Tk UI uses ui_helpers directly
- Web UI already using ui_helpers

**Testing: IN PROGRESS**
- CLI RENUM: ✅ Tested - indentation preserved
- CLI Comments: ✅ Tested - apostrophe and REM preserved
- Tk UI RENUM: ✅ Tested - ui_helpers logic works correctly

**Remaining: Optional**
- Test DELETE and LIST commands (lower priority)
- Test Web UI (if RENUM is implemented there)
