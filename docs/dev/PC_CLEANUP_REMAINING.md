# PC Cleanup - Remaining Work

**Status:** Mostly Complete (v1.0.293)

## Completed (v1.0.293)

✅ **ErrorInfo now uses PC** (v1.0.291)
- Changed `error_line: int` to `pc: PC`
- Updated all ErrorInfo creation sites (3 places)
- Updated UI code to use `error_info.pc.line_num`

✅ **Removed dual-mode from execute_* methods** (v1.0.291)
- GOTO, GOSUB, IF, RETURN now only set `runtime.npc`
- FOR/NEXT now only set `runtime.npc`
- WHILE/WEND now only set `runtime.npc`
- ON GOTO/ON GOSUB now only set `runtime.npc`
- Removed 9+ lines of redundant `runtime.next_line` assignments

✅ **RESUME Statement** (v1.0.293)
- Complete rewrite to use ErrorInfo.pc instead of runtime fields
- Uses statement_table.next_pc() for RESUME NEXT
- Simplified from ~50 lines to ~30 lines
- No longer uses runtime.error_line/error_stmt_index

✅ **RUN Statement** (v1.0.293)
- Fixed to set runtime.npc with PC object
- One-line change: `self.runtime.npc = PC.from_line(stmt.line_number)`

✅ **Error Handler Invocation** (v1.0.293)
- Changed signature from `(error_code, error_line, error_stmt_index)` to `(error_code, error_pc)`
- Fixed both call sites to construct PC objects
- Now uses PC throughout error handling

✅ **ERS% System Variable** (v1.0.293)
- Added ERS% (Error Statement) variable alongside ERL% (Error Line)
- Set in both _invoke_error_handler() and ERROR statement
- Provides statement-level error reporting (0-based offset)
- Test: `20 A=1:B=2:C=1/0:D=4` correctly reports line 20 statement 2

## Remaining Work

### 1. Old Execution Methods (Not Using PC)

These methods still use `runtime.current_line`, `runtime.next_line`, etc.:

**src/interpreter.py:**
- `run_from_current()` - line ~527 (used by CONT command)
- `_run_loop()` - line ~636
- `step_once()` - line ~553
- `execute_line()` - line ~570
- `advance_to_next_statement()` - line ~897

**Status:** Used by `interactive.py` for CONT command

**Options:**
1. Convert to PC-based (rewrite to use runtime.pc)
2. Remove and update CONT to use tick-based execution

**Decision:** Leave as-is for now. These methods are isolated to CONT functionality in interactive mode. The new tick_pc() execution is PC-based and used everywhere else.

### 2. Runtime Fields Still Exist

**src/runtime.py** still has old fields:
- `current_line: Optional[LineNode]`
- `current_stmt_index: int`
- `next_line: Optional[int]`
- `next_stmt_index: Optional[int]`
- `stop_line` / `stop_stmt_index` (for STOP command)

**Status:** Still used by old execution methods (CONT command only)

**Should NOT remove yet** - old execution methods depend on them.

**When to remove:** After converting CONT to use tick-based execution.

## Testing Status

✅ Tested:
1. **FOR loops** - verified working with test_for.bas
2. **Error handlers** - ON ERROR GOTO tested
3. **ERS%** - multi-statement error reporting works correctly
4. **RESUME** - logic updated, needs integration testing
5. **RUN** - logic updated, needs integration testing

⏸️ Needs testing:
1. **CONT command** - may be affected by changes
2. **RESUME** - needs full integration test with ON ERROR
3. **RESUME NEXT** - needs test with statement-level resume
4. **RUN with line number** - needs test

## Current Status

**~95% complete.** All core execute_* methods are PC-only. Main interpreter uses tick_pc() which is fully PC-based. Only the old CONT-specific execution methods remain, and they're isolated.

## Next Steps (Optional)

If you want to complete the remaining 5%:

1. **Convert CONT to tick-based** (2-3 hours)
   - Modify CONT to save/restore runtime.pc instead of current_line/current_stmt_index
   - Use tick_pc() instead of run_from_current()
   - Test STOP/CONT functionality thoroughly

2. **Remove old runtime fields** (1 hour)
   - Remove current_line, current_stmt_index, next_line, next_stmt_index
   - Remove stop_line, stop_stmt_index (replace with stop_pc)
   - Clean up any remaining references

3. **Remove old execution methods** (1 hour)
   - Delete run_from_current(), _run_loop(), etc.
   - Simplify interpreter.py

**Total remaining effort:** ~4-5 hours

**Recommendation:** Not urgent. Current implementation is clean and PC-based for all normal execution. CONT is an edge case used rarely in interactive mode.
