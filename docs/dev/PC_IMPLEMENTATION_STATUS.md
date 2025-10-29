# PC (Program Counter) Implementation Status

**Goal:** Replace current_line/current_stmt_index/next_line/next_stmt_index with hardware-inspired PC/NPC design

**Design inspiration:** 1970s CPUs like KL10 with PC and NPC (next program counter) registers

## Architecture

### PC Class (`src/pc.py`)
- Immutable identifier: `PC(line_num, stmt_offset)`
- Examples: `PC(100, 0)` = line 100, first statement; `PC(100, 2)` = third statement
- Methods:
  - `halted()` - check if PC points past program end
  - `is_step_point(other_pc, mode)` - determine if debugger should stop
  - `from_line(line_num)` - create PC for GOTO target (offset 0)
  - `halted_pc()` - create PC representing halted state

### StatementTable Class (`src/pc.py`)
- Ordered dict: `{PC -> stmt_node}`
- Uses Python 3.7+ insertion-ordered dict
- Methods:
  - `first_pc()` - get first PC in program
  - `next_pc(pc)` - get sequential next PC (for normal execution)
  - `get(pc)` - retrieve statement at PC

## Implementation Status

### ✅ Phase 1: Dual Mode (COMPLETED - v1.0.276)

**What's done:**
1. ✅ Created `src/pc.py` with PC and StatementTable classes
2. ✅ Added `runtime.pc`, `runtime.npc`, `runtime.statement_table` to Runtime
3. ✅ Statement table built during `Runtime.setup()`
4. ✅ All control flow statements set BOTH old and new:
   - `execute_goto()` - sets `next_line` AND `npc`
   - `execute_gosub()` - sets `next_line` AND `npc`
   - `execute_return()` - sets `next_line/next_stmt_index` AND `npc`
   - `execute_if()` - sets `next_line` AND `npc` for THEN/ELSE jumps
   - `execute_ongoto()` - sets `next_line` AND `npc`
   - `execute_ongosub()` - sets `next_line` AND `npc`

**Tests passed:**
- ✅ Basic sequential execution
- ✅ GOTO jumps
- ✅ GOSUB/RETURN
- ✅ Multiple statements per line (colon separators)
- ✅ Statement table correctly maps all statements

**Current state:**
- Old execution loop still uses `current_line/next_line`
- New `pc/npc` fields are populated but not yet driving execution
- No breakage - everything backwards compatible

### ⏸️ Phase 2: PC-Based Execution Loop (PENDING)

**What needs to be done:**

1. **Refactor `interpreter.tick()` to use PC:**
   ```python
   # Current (line-based):
   while line_index < len(line_order):
       line = line_table[line_order[line_index]]
       for stmt_index in range(len(line.statements)):
           ...

   # Target (PC-based):
   pc = runtime.pc
   while not pc.halted():
       if npc is not None:
           pc = npc
           npc = None
       stmt = statement_table.get(pc)
       execute_statement(stmt)
       pc = statement_table.next_pc(pc)
   ```

2. **Update `runtime.pc` during execution:**
   - Set `runtime.pc` before executing each statement
   - This allows error messages, ERL%, breakpoints to use current PC

3. **Simplify control flow:**
   - Remove nested line/statement loops
   - Remove `advance_to_next_statement()` complexity
   - Single simple loop with PC navigation

### ⏸️ Phase 3: Statement-Level Breakpoints (PENDING)

**What needs to be done:**

1. **Update InterpreterState:**
   - Change `breakpoints` from `Set[int]` (line numbers) to `Set[PC]`
   - Store breakpoint as `PC(100, 2)` for "line 100, 3rd statement"

2. **Update breakpoint UI:**
   - Visual editor: click on specific statement to set breakpoint
   - CLI: `BREAK 100.2` syntax for statement-level breakpoints
   - Show breakpoint markers at statement level, not just line level

3. **Update breakpoint checking:**
   ```python
   if pc in breakpoints:  # Now checks exact PC, not just line
       pause()
   ```

### ⏸️ Phase 4: Enhanced TRACE (PENDING)

**What needs to be done:**

1. **Add `trace_detail` setting:**
   - `'line'` - show `[100]` on line boundary (current behavior)
   - `'statement'` - show `[100.0]`, `[100.1]`, `[100.2]` for each statement

2. **Update TRACE output:**
   ```python
   if trace_on:
       if trace_detail == 'statement':
           output(f"[{pc}]")  # [100.2]
       elif trace_detail == 'line' and pc.line_num != last_traced_line:
           output(f"[{pc.line_num}]")  # [100]
   ```

3. **Add TRON/TROFF variants:**
   - `TRON` - line-level trace (default)
   - `TRON STATEMENT` - statement-level trace

### ⏸️ Phase 5: Cleanup (PENDING)

**What needs to be done:**

1. **Remove old fields from Runtime:**
   - Remove `current_line`, `current_stmt_index`
   - Remove `next_line`, `next_stmt_index`
   - Remove `line_index` from InterpreterState

2. **Update all references:**
   - Error messages: Use `pc` instead of `current_line.line_number`
   - ERL%: Set from `pc.line_num` instead of `current_line.line_number`
   - Debugger: Use `pc` for position tracking

3. **Update serialization:**
   - Position save/restore uses PC instead of line+stmt pairs

## Benefits of New Design

1. **Reduced error surface:** Can't accidentally set line without offset, or vice versa
2. **Clearer semantics:** `npc = PC.from_line(100)` vs `next_line = 100; next_stmt_index = 0`
3. **Simpler execution loop:** Single loop over PCs, not nested line/statement loops
4. **Statement-level breakpoints:** `BREAK 100.2` to break at 3rd statement on line 100
5. **Better trace output:** Can show `[100.0]`, `[100.1]`, `[100.2]` for debugging
6. **Hardware analogy:** Matches CPU architecture (PC/NPC pattern from 1970s mainframes)

## Design Decisions

### Why immutable PC?
- Functional style: `pc = pc.next()` instead of `pc.advance()`
- Prevents accidental modification
- Clear data flow: new PC comes from statement table

### Why statement table navigation?
- PC doesn't need to know about statement table
- Keeps PC lightweight (just line + offset)
- Statement table manages ordered collection

### Why keep old fields during migration?
- Zero risk of breaking existing code
- Can test new PC system alongside old
- Gradual migration path
- Easy to rollback if issues found

## Next Steps

1. Start Phase 2: Refactor tick() loop to use PC
2. Test thoroughly with existing programs
3. Proceed to Phase 3 only after Phase 2 is stable
