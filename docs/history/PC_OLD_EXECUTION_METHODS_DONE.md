# Complete PC Migration - Remove Old Execution Methods

**Status:** ✅ COMPLETE
**Priority:** MEDIUM
**Created:** 2025-10-28 (v1.0.287)
**Completed:** 2025-10-29 (v1.0.300)

## Problem

While `tick_pc()` uses the new PC/NPC architecture, there are still old execution methods that use the 4-variable pattern:
- `run_from_current()` - used by CONT command
- `_run_loop()` - used by run_from_current
- `step_once()` - old stepping method
- `execute_line()` - old line-by-line execution

These methods still use:
- `runtime.current_line` (LineNode object)
- `runtime.current_stmt_index`
- `runtime.next_line`
- `runtime.next_stmt_index`

Additionally, ALL `execute_*` statement methods (GOTO, GOSUB, IF, etc.) are setting BOTH old and new fields:
```python
def execute_goto(self, stmt):
    self.runtime.next_line = stmt.line_number  # OLD
    self.runtime.npc = PC.from_line(stmt.line_number)  # NEW
```

This dual-mode approach was intentional for Phase 1, but now that `tick_pc()` is working, we should complete the migration.

## Files Affected

### src/interpreter.py
- `run_from_current()` - line ~527
- `_run_loop()` - line ~636
- `step_once()` - line ~553
- `execute_line()` - line ~570
- `advance_to_next_statement()` - line ~897
- ALL `execute_*` methods (50+ methods setting `runtime.next_line`)

### src/runtime.py
Fields that could be removed after migration:
- `current_line: Optional[LineNode]`
- `current_stmt_index: int`
- `next_line: Optional[int]`
- `next_stmt_index: Optional[int]`
- `stop_line` / `stop_stmt_index` (used by STOP command)

### src/interactive.py
- Uses `run_from_current()` for CONT command

## Migration Plan

### Phase 0: Update Breakpoint API

**Current API:**
```python
def set_breakpoint(self, line: int, stmt_offset: int = None):
    if stmt_offset is not None:
        pc = PC(line, stmt_offset)
        self.state.breakpoints.add(pc)
    else:
        self.state.breakpoints.add(line)

def clear_breakpoint(self, line: int, stmt_offset: int = None):
    if stmt_offset is not None:
        pc = PC(line, stmt_offset)
        self.state.breakpoints.discard(pc)
    else:
        self.state.breakpoints.discard(line)
```

**New API (with PC object support):**
```python
def set_breakpoint(self, line_or_pc: Union[int, PC], stmt_offset: int = None):
    """Add breakpoint. Accepts PC object or (line, offset) for backwards compatibility."""
    if isinstance(line_or_pc, PC):
        # PC object passed directly
        self.state.breakpoints.add(line_or_pc)
    elif stmt_offset is not None:
        # Statement-level: (line, offset)
        self.state.breakpoints.add(PC(line_or_pc, stmt_offset))
    else:
        # Line-level: just line number
        self.state.breakpoints.add(line_or_pc)

def clear_breakpoint(self, line_or_pc: Union[int, PC], stmt_offset: int = None):
    """Remove breakpoint. Accepts PC object or (line, offset) for backwards compatibility."""
    if isinstance(line_or_pc, PC):
        self.state.breakpoints.discard(line_or_pc)
    elif stmt_offset is not None:
        self.state.breakpoints.discard(PC(line_or_pc, stmt_offset))
    else:
        self.state.breakpoints.discard(line_or_pc)
```

**Usage examples:**
```python
# Line-level (backwards compatible)
interp.set_breakpoint(100)

# Statement-level (backwards compatible)
interp.set_breakpoint(100, 2)

# PC object (new, cleaner)
pc = PC(100, 2)
interp.set_breakpoint(pc)

# Or from statement table
pc = runtime.statement_table.first_pc()
interp.set_breakpoint(pc)
```

### Phase 1: Convert Old Execution Methods

**Option A: Convert to PC-based (recommended)**
1. Update `run_from_current()` to use `runtime.pc` instead of `runtime.current_line`
2. Update `_run_loop()` to iterate over PCs instead of line_order indices
3. Update `execute_line()` to use PC for statement execution
4. Update `advance_to_next_statement()` to use PC navigation

**Option B: Remove if unused (if not needed)**
1. Check if any code paths still call these methods
2. If only `interactive.py` uses them, update CONT to use tick-based execution
3. Remove methods entirely

### Phase 2: Remove Dual-Mode from Execute Methods

Update ALL `execute_*` statement methods to only set `runtime.npc`:

**Before:**
```python
def execute_goto(self, stmt):
    self.runtime.next_line = stmt.line_number
    self.runtime.npc = PC.from_line(stmt.line_number)
```

**After:**
```python
def execute_goto(self, stmt):
    self.runtime.npc = PC.from_line(stmt.line_number)
```

**Methods to update:** (~50 methods)
- `execute_goto()`
- `execute_gosub()`
- `execute_return()`
- `execute_if()` (THEN/ELSE jumps)
- `execute_ongoto()`
- `execute_ongosub()`
- `execute_for()` / `execute_next()`
- `execute_while()` / `execute_wend()`
- `execute_resume()`
- `execute_run()`
- `_invoke_error_handler()`
- Any other method setting `runtime.next_line` or `runtime.next_stmt_index`

### Phase 3: Remove Old Fields from Runtime

After all code uses PC exclusively:
1. Remove `current_line`, `current_stmt_index` from Runtime
2. Remove `next_line`, `next_stmt_index` from Runtime
3. Remove `stop_line`, `stop_stmt_index` (replace with `stop_pc`)
4. Update any serialization/debug code that references these fields

### Phase 4: Update STOP/CONT Commands

The STOP command stores position for CONT:
```python
# OLD
runtime.stop_line = runtime.current_line
runtime.stop_stmt_index = runtime.current_stmt_index

# NEW
runtime.stop_pc = runtime.pc
```

CONT command resumes from stopped position:
```python
# OLD
run_from_current()  # Uses runtime.current_line

# NEW
runtime.pc = runtime.stop_pc
tick('run')  # Use tick-based execution
```

## Benefits

1. **Single source of truth**: Only PC/NPC for position tracking
2. **Less code**: Remove ~300 lines of old execution methods
3. **Simpler execute_* methods**: Only set NPC, not 4 fields
4. **No duplication**: Remove dual-mode assignments
5. **Easier to understand**: One execution model, not two

## Risks

1. **CONT command**: Must verify CONT still works after migration
2. **STOP command**: Must update to store PC instead of line/stmt
3. **Interactive mode**: Must test immediate command execution
4. **Error handlers**: ON ERROR / RESUME must work with PC

## Testing Strategy

1. Test STOP/CONT in immediate mode
2. Test ON ERROR GOTO with RESUME
3. Test ON ERROR GOTO with RESUME NEXT
4. Test all control flow statements (GOTO, GOSUB, IF, FOR, WHILE)
5. Test step-by-step execution in debuggers
6. Test breakpoints with old and new code

## Estimated Effort

- **Phase 1**: 2-3 hours (convert or remove old execution methods)
- **Phase 2**: 1-2 hours (remove dual-mode from 50+ execute methods)
- **Phase 3**: 1 hour (remove runtime fields, update runtime.py)
- **Phase 4**: 1 hour (update STOP/CONT commands)
- **Testing**: 2 hours (comprehensive testing of all control flow)

**Total**: ~8 hours

## Current Workaround

The dual-mode approach works fine and all tests pass. This is a code cleanliness issue, not a functional bug. The current behavior is correct, just not as clean as it could be.

## Decision

**Defer** this work until:
1. All tick-based UIs are stable and tested
2. PC refactoring has been in production for a while
3. We're confident the old methods aren't needed

This is technical debt, not a blocking issue.
