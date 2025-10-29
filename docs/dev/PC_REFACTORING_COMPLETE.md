# PC (Program Counter) Refactoring - COMPLETE ✅

**Status:** Fully complete including cleanup (v1.0.276 - v1.0.286)
**Inspired by:** 1970s hardware CPUs (KL10 with FPD bit)

## Executive Summary

Successfully replaced the scattered 4-variable position tracking system with a clean hardware-inspired PC/NPC (Program Counter / Next Program Counter) design. This eliminates ~56 manual assignments to `current_line`, `current_stmt_index`, `next_line`, `next_stmt_index` scattered throughout the codebase.

## What Changed

### Before: Scattered State (The Problem)
```python
# 56 places in code doing variations of:
runtime.current_line = line_node
runtime.current_stmt_index = 2
runtime.next_line = 100
runtime.next_stmt_index = 0

# Nested loops, manual offset arithmetic
for line_index in line_order:
    line = line_table[line_index]
    for stmt_index in range(len(line.statements)):
        # Complex statement advancement logic
        # Easy to get wrong (partial updates)
```

### After: Hardware-Like PC (The Solution)
```python
# Clean PC objects
pc = PC(100, 2)  # Line 100, statement 2
npc = PC.from_line(200)  # Jump target

# Single simple loop
while not pc.halted():
    if npc is not None:
        pc = npc
        npc = None
    stmt = statement_table.get(pc)
    execute_statement(stmt)
    pc = statement_table.next_pc(pc)
```

## Implementation Phases

### Phase 1: Dual Mode (v1.0.276)
**Goal:** Add PC infrastructure without breaking anything

**Delivered:**
- ✅ `PC` class: Immutable `(line_num, stmt_offset)` identifier
- ✅ `StatementTable`: Ordered dict `{PC → statement_node}`
- ✅ Built during `Runtime.setup()` - every statement gets a PC
- ✅ All control flow sets BOTH old and new formats
- ✅ Zero breakage - fully backwards compatible

**Example:**
```python
# Statement table for: 10 PRINT "A":PRINT "B":PRINT "C"
PC(10, 0) → PrintStatementNode("A")
PC(10, 1) → PrintStatementNode("B")
PC(10, 2) → PrintStatementNode("C")
```

### Phase 2: PC-Based Execution (v1.0.277)
**Goal:** Replace execution loop with PC navigation

**Delivered:**
- ✅ New `tick_pc()` method - single while loop over PCs
- ✅ No more nested line/statement loops
- ✅ All statement executors use `runtime.pc` instead of `current_line`
- ✅ Control flow uses `statement_table.next_pc()` for navigation
- ✅ Handles cross-line jumps correctly (FOR/NEXT, WHILE/WEND)
- ✅ Old `tick()` redirects to `tick_pc()`, saved as `tick_old()` for reference

**Key Achievement:**
- Execution loop reduced from ~320 lines to ~160 lines
- Single simple loop replaces complex nested structure
- Impossible to partially update position (atomic PC)

### Phase 3: Statement-Level Features (v1.0.278)
**Goal:** Enable breakpoints and trace at statement level

**Delivered:**
- ✅ Breakpoints support both `int` (line) and `PC` (statement) objects
- ✅ `set_breakpoint(100, 2)` - break at 3rd statement on line 100
- ✅ Backwards compatible: `set_breakpoint(100)` still works for lines
- ✅ `runtime.trace_detail`: `'line'` or `'statement'` mode
- ✅ Line trace: `[100]` once per line (default)
- ✅ Statement trace: `[PC(100.0)]`, `[PC(100.1)]`, `[PC(100.2)]` per statement

**Enables:**
- Precise debugging of multi-statement lines (colon-separated)
- IDE-style statement highlighting
- Step-through at statement granularity

## API Changes

### PC Class
```python
from src.pc import PC

# Create PC
pc = PC(100, 2)              # Line 100, statement 2
pc = PC.from_line(100)       # Line 100, statement 0 (for GOTO)
pc = PC.halted_pc()          # Halted state (past end)

# Query
pc.halted()                  # → False
pc.line_num                  # → 100
pc.stmt_offset               # → 2
str(pc)                      # → "PC(100.2)"

# Step mode check
pc.is_step_point(next_pc, 'step_statement')  # → True (always)
pc.is_step_point(next_pc, 'step_line')       # → True if line changed
```

### StatementTable
```python
# Automatically built during Runtime.setup()
runtime.statement_table      # Ordered dict {PC → stmt_node}

# Navigation
first_pc = runtime.statement_table.first_pc()
next_pc = runtime.statement_table.next_pc(pc)
stmt = runtime.statement_table.get(pc)
```

### Breakpoints
```python
interp = Interpreter(runtime, io)

# Line-level (backwards compatible)
interp.set_breakpoint(100)
interp.clear_breakpoint(100)

# Statement-level (new)
interp.set_breakpoint(100, 2)  # Break at 3rd statement on line 100
interp.clear_breakpoint(100, 2)
```

### Trace
```python
runtime.trace_on = True
runtime.trace_detail = 'line'       # [100] once per line (default)
runtime.trace_detail = 'statement'  # [PC(100.0)], [PC(100.1)], etc.
```

## Benefits Realized

### 1. Reduced Error Surface
**Before:** 56 separate assignments, easy to forget one
```python
runtime.next_line = 100
# Oops, forgot next_stmt_index!
```

**After:** Atomic PC update
```python
runtime.npc = PC.from_line(100)  # Both line and offset set together
```

### 2. Simpler Control Flow
**Before:** Manual offset arithmetic
```python
runtime.push_gosub(
    runtime.current_line.line_number,
    runtime.current_stmt_index + 1  # Hope this is valid!
)
```

**After:** Automatic navigation
```python
return_pc = runtime.statement_table.next_pc(runtime.pc)
runtime.push_gosub(return_pc.line_num, return_pc.stmt_offset)
```

### 3. Cross-Line Jumps
**Before:** Complex validation, edge case handling
```python
return_stmt = loop_info['return_stmt']
if return_stmt >= len(line_node.statements):
    # Special case: advance to next line
    line_index += 1
    runtime.current_stmt_index = 0
    # ... 20 more lines of edge case handling
```

**After:** Just works
```python
for_pc = PC(return_line, return_stmt)
next_pc = runtime.statement_table.next_pc(for_pc)  # Automatically handles line boundary
runtime.npc = next_pc
```

### 4. Statement-Level Debugging
**Before:** Can only break on entire line
```python
10 PRINT "A":PRINT "B":PRINT "C"
# Can only break at line 10 start, executes all 3 statements
```

**After:** Can break at any statement
```python
10 PRINT "A":PRINT "B":PRINT "C"
set_breakpoint(10, 1)  # Break before PRINT "B"
# Trace shows: [PC(10.0)], [PC(10.1)] ← stops here
```

## Testing

### Test Suite
All tests pass:
- ✅ Sequential execution
- ✅ GOTO jumps
- ✅ GOSUB/RETURN
- ✅ FOR/NEXT loops (including cross-line)
- ✅ WHILE/WEND loops
- ✅ Multi-statement lines (colons)
- ✅ Variable assignments and expressions
- ✅ PC equality and hashing
- ✅ Set membership (for breakpoints)

### Compatibility
- ✅ All existing programs run unchanged
- ✅ Line-level breakpoints still work
- ✅ Line-level trace still works (default)
- ✅ Old tick() method preserved as tick_old() for reference

## Code Metrics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| tick() method lines | ~320 | ~160 | -50% |
| Nested loops | 2 (line, statement) | 1 (PC) | -50% |
| Position assignments | 56 scattered | PC objects | Centralized |
| Cross-line jump handling | ~40 lines | 3 lines | -92% |

## Phase 5: State Field Cleanup (v1.0.286) ✅

**Goal:** Remove cached state fields that duplicated data from runtime.pc

**Delivered:**
- ✅ Converted `current_line`, `current_statement_char_start`, `current_statement_char_end` to `@property` methods
- ✅ Properties compute values on-demand from `interpreter.runtime.pc` and `statement_table`
- ✅ Added `_interpreter` reference to InterpreterState for property access
- ✅ Removed all assignments to these cached fields from `tick_pc()`
- ✅ Updated `immediate_executor.py` to stop writing to read-only properties
- ✅ No UI changes needed - all existing UI code works unchanged

**Key Achievement:**
- Eliminated data duplication and sync issues
- UIs automatically get current values from runtime.pc
- Properties are computed, not cached - always accurate

**Before:**
```python
@dataclass
class InterpreterState:
    current_line: Optional[int] = None  # Cached, could get stale
    current_statement_char_start: int = 0  # Duplicated data
    current_statement_char_end: int = 0  # Could desync
```

**After:**
```python
@dataclass
class InterpreterState:
    _interpreter: Optional['Interpreter'] = field(default=None, repr=False)

    @property
    def current_line(self) -> Optional[int]:
        """Computed from runtime.pc.line_num"""
        if self._interpreter:
            return self._interpreter.runtime.pc.line_num
        return None

    @property
    def current_statement_char_start(self) -> int:
        """Computed from statement_table.get(pc).char_start"""
        # ... computes from runtime.pc and statement table
```

## Remaining Work (Optional)

### UI Integration
- [ ] CLI command: `BREAK 100.2` syntax parsing (see `CALLSTACK_UI_PC_ENHANCEMENT_TODO.md`)
- [ ] CLI command: `TRON STATEMENT` to enable statement trace
- [ ] Visual editor: Click statement to set breakpoint (not just line)
- [ ] Debugger: Show current statement highlighted (not just line)
- [ ] Call stack display: Show "Return to 10.2" instead of "Return to 10"

These are enhancements, not requirements. The core refactoring is **fully complete**.

## Design Principles

### 1. Immutability
PC objects are immutable - no `.advance()` method. Always create new PC:
```python
pc = statement_table.next_pc(pc)  # Functional style
```

### 2. Separation of Concerns
- `PC`: Lightweight position identifier (just line + offset)
- `StatementTable`: Manages navigation and lookup
- `Runtime`: Holds current pc/npc state

### 3. Hardware Analogy
Matches CPU architecture:
- **PC**: Current instruction pointer
- **NPC**: Next instruction pointer (for jumps)
- **Statement table**: Instruction memory
- **next_pc()**: Program counter increment logic

### 4. Backwards Compatibility
- Old fields maintained during migration (Phase 1)
- Both old and new set during Phase 1
- Switch to PC-only in Phase 2
- No breaking changes to external APIs

## Conclusion

**Mission accomplished!** The PC refactoring successfully:

1. ✅ Eliminated scattered position state (4 variables → 2 PC objects)
2. ✅ Simplified execution loop (320 lines → 160 lines, nested → single)
3. ✅ Enabled statement-level debugging (breakpoints, trace)
4. ✅ Reduced error surface (atomic updates, automatic navigation)
5. ✅ Maintained backwards compatibility (zero breaking changes)
6. ✅ Eliminated data duplication (computed properties from single source of truth)

The codebase is now cleaner, more maintainable, and more powerful. The hardware-inspired design proved to be exactly the right abstraction for this problem.

**Status:** Fully complete and production-ready (v1.0.276 - v1.0.286)
