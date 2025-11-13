# FOR Loop Stack Implementation Options

## Current Problem

Our implementation uses a **unified execution stack** mixing GOSUB, FOR, and WHILE:

```python
# src/runtime.py lines 83-88
self.execution_stack = []  # Mixed: GOSUB, FOR, WHILE entries
self.for_loop_vars = {}    # Quick lookup: var_name -> stack index
```

**Error at line 996-1001**: When pushing a new FOR loop, we check if `var_name in self.for_loop_vars` and raise error if it exists. This prevents the Super Star Trek pattern from working.

**Problem**: The old FOR might be deep in the stack:
```
Stack: [FOR I (index 0), GOSUB (index 1), WHILE (index 2)]
         ↑ old FOR I is here
```

Can't just "pop the old one" because:
- It's not on top
- Popping from middle would break the unified stack structure
- `pop_for_loop()` verifies the FOR is on TOP before popping

## Real MBASIC Behavior (from tests)

1. **Test 3**: Jump out of FOR I, start new FOR I → ✅ Works
2. **Test 5**: Do this 9 times in a row → ✅ Works
3. **Test 6**: Super Star Trek pattern → ✅ Works

**No evidence of explicit cleanup on GOTO** - GOTO just sets PC, doesn't show any stack manipulation

**Hypothesis**: Real MBASIC's FOR loops might be in a **separate stack** from GOSUB/WHILE

## Option 1: Separate FOR Loop Stack

**Approach**: Split FOR loops into their own stack, separate from GOSUB/WHILE

```python
self.execution_stack = []     # Only GOSUB and WHILE
self.for_loop_stack = []      # Only FOR loops
self.for_loop_vars = {}       # var_name -> index in for_loop_stack
```

**Pros**:
- ✅ Easy to implement "replace on duplicate"
- ✅ Could implement 8-entry circular buffer if desired
- ✅ No need to sift through mixed stack
- ✅ Matches potential real MBASIC architecture

**Cons**:
- ❌ Can't detect improper nesting like `FOR I / GOSUB / NEXT I / RETURN`
- ❌ Loses unified ordering of control flow
- ❌ May break existing debugger stack inspection

**Implementation**:
```python
def push_for_loop(self, var_name, ...):
    # If variable already active, replace it (implicit cleanup)
    if var_name in self.for_loop_vars:
        old_index = self.for_loop_vars[var_name]
        self.for_loop_stack[old_index] = new_entry  # Replace in place
    else:
        self.for_loop_stack.append(new_entry)
        self.for_loop_vars[var_name] = len(self.for_loop_stack) - 1
```

## Option 2: Cleanup on GOTO (Unified Stack)

**Approach**: When GOTO/ON GOTO executes, remove FOR/WHILE loops that we're jumping out of

```python
def execute_goto(self, stmt):
    # Before jumping, clean up loops we're exiting
    current_line = self.runtime.pc.line_num
    target_line = stmt.line_number
    self.runtime.cleanup_loops_on_jump(current_line, target_line)
    self.runtime.npc = PC.from_line(target_line)
```

**Logic**: Remove any FOR/WHILE where:
- Current PC is inside the loop's range (between FOR and NEXT)
- Target PC is outside the loop's range

**Pros**:
- ✅ Keeps unified stack
- ✅ Matches the "GOTO cleans up" mental model
- ✅ Preserves nesting detection

**Cons**:
- ❌ Complex logic to determine loop ranges
- ❌ FOR...NEXT range not stored in stack entry
- ❌ May need to track NEXT statement locations
- ❌ More expensive (runs on every GOTO)

## Option 3: Allow Duplicate Variables (Sift Through Stack)

**Approach**: When pushing FOR with existing variable, find and remove old entry from anywhere in stack

```python
def push_for_loop(self, var_name, ...):
    if var_name in self.for_loop_vars:
        # Remove old entry from anywhere in stack
        old_index = self.for_loop_vars[var_name]
        self.execution_stack.pop(old_index)
        # Adjust indices for all FOR loops after the removed one
        for v in self.for_loop_vars:
            if self.for_loop_vars[v] > old_index:
                self.for_loop_vars[v] -= 1

    # Push new entry
    ...
```

**Pros**:
- ✅ Keeps unified stack
- ✅ Simple logic (just remove and reindex)
- ✅ Preserves nesting detection for GOSUB/WHILE

**Cons**:
- ❌ Leaves "holes" in control flow ordering
- ❌ May confuse debugger stack traces
- ❌ Doesn't clean up GOSUB entries between FOR loops

**Example problem**:
```
Before: [FOR I, GOSUB, FOR J, WHILE]
After removing FOR I: [GOSUB, FOR J, WHILE]
         ↑ GOSUB orphaned - its FOR context is gone
```

## Option 4: Mark as Inactive (Abandoned)

**Approach**: Keep old FOR in stack but mark as "abandoned" so NEXT skips it

```python
def push_for_loop(self, var_name, ...):
    if var_name in self.for_loop_vars:
        # Mark old entry as abandoned
        old_index = self.for_loop_vars[var_name]
        self.execution_stack[old_index]['abandoned'] = True

    # Push new entry
    new_entry = {'type': 'FOR', 'var': var_name, 'abandoned': False, ...}
    self.execution_stack.append(new_entry)
    self.for_loop_vars[var_name] = len(self.execution_stack) - 1
```

**NEXT logic**:
```python
def pop_for_loop(self, var_name):
    loop_index = self.for_loop_vars[var_name]
    entry = self.execution_stack[loop_index]

    if entry.get('abandoned'):
        # Skip abandoned loop, search for next one up the stack
        ...
```

**Pros**:
- ✅ Keeps unified stack intact
- ✅ Preserves all control flow history
- ✅ Good for debugger inspection

**Cons**:
- ❌ Stack grows with abandoned entries
- ❌ Need cleanup mechanism to remove abandoned entries
- ❌ Complex NEXT logic to skip abandoned loops

## Recommendation: Option 1 (Separate FOR Stack)

**Reasoning**:

1. **Real MBASIC evidence**: Tests show no indication that GOSUB and FOR interact in nesting detection
2. **Simplicity**: Separate stacks are much simpler to implement
3. **Matches behavior**: Real MBASIC allows immediate variable reuse, suggesting separate tracking
4. **Performance**: No need to sift through mixed stack

**Implementation plan**:

1. Add `self.for_loop_stack = []` separate from `self.execution_stack`
2. Move FOR entries from unified stack to separate stack
3. Keep GOSUB and WHILE in unified stack (they may still need nesting detection)
4. Update `push_for_loop` to replace existing entry with same variable
5. Update `get_execution_stack()` to merge both stacks for UI display
6. Update serialization (nicegui_backend.py) to save/restore both stacks

## UI/Debugger Considerations

### Current Stack Display

Three UIs display the execution stack:
- **Curses UI** (`src/ui/curses_ui.py:3371`)
- **TK UI** (`src/ui/tk_ui.py:1690`)
- **Web UI** (`src/ui/web/nicegui_backend.py:339`)

All call `runtime.get_execution_stack()` which returns a unified view.

### Display Format

Current display shows interleaved control flow:
```
GOSUB from line 100.0
  FOR I = 1 TO 10 (line 120.0)
    GOSUB from line 130.2
      WHILE (line 200.0)
```

Indentation shows nesting level, making control flow structure visible.

### Implementation for Separate Stacks

**Key insight**: UIs don't need to change if we maintain the unified view!

Modify `get_execution_stack()` to **merge** both stacks:

```python
def get_execution_stack(self):
    """Export unified execution stack for UI display.

    Merges GOSUB/WHILE stack with FOR loop stack, maintaining
    the appearance of unified nesting for debugging.
    """
    # Option A: Show FOR loops separately at bottom
    result = self.execution_stack.copy()  # GOSUB/WHILE
    result.extend(self.for_loop_stack)     # Add FOR loops
    return result

    # Option B: Show active FOR loops only
    result = self.execution_stack.copy()
    # Add only non-abandoned FOR loops
    for entry in self.for_loop_stack:
        if entry and 'var' in entry:
            result.append(entry)
    return result
```

**Trade-off**: We lose true interleaved ordering (can't tell if FOR came before or after a GOSUB), but:
1. Real MBASIC doesn't enforce FOR/GOSUB nesting anyway
2. Each section (GOSUB/WHILE vs FOR) still shows its own ordering
3. Debugger display remains useful

### Serialization Updates

**Web UI serialization** (`src/ui/web/nicegui_backend.py:3692-3693`):

```python
# Current (lines 3692-3693)
'execution_stack': self.runtime.execution_stack,
'for_loop_vars': self.runtime.for_loop_vars,

# After split (add for_loop_stack)
'execution_stack': self.runtime.execution_stack,      # GOSUB/WHILE only
'for_loop_stack': self.runtime.for_loop_stack,        # FOR only (new)
'for_loop_vars': self.runtime.for_loop_vars,
```

**Backwards compatibility**: Old saved sessions won't have `for_loop_stack`:
```python
# Restore (lines 3731-3732)
self.runtime.execution_stack = state['execution_stack']
self.runtime.for_loop_stack = state.get('for_loop_stack', [])  # Default to empty
self.runtime.for_loop_vars = state['for_loop_vars']
```

**Migration path**:
- Phase 1: Add separate FOR stack, test all existing programs
- Phase 2: (Optional) Implement circular 8-entry buffer if desired
- Phase 3: Update debugger UI to show both stacks clearly

## Test Cases to Verify

After implementation, verify:
- ✅ Test 3: Jump out and reuse variable
- ✅ Test 6: Super Star Trek pattern
- ✅ Nested FOR with same variable still errors (when both active)
- ✅ NEXT without matching FOR errors correctly
- ✅ Deep nesting (10+ levels) works

## Notes for Implementation

**Question**: Do WHILE/WEND need the same treatment?
- Need separate tests to determine if jumping out of WHILE allows reuse
- May need `self.while_loop_stack` if same pattern applies

**Question**: Does GOSUB/RETURN interact with FOR?
- Current unified stack catches `FOR / GOSUB / NEXT / RETURN` as error
- Need to determine if real MBASIC allows this or errors
- May be able to keep GOSUB in unified stack for this check

## References

- Test results: `docs/dev/FOR_LOOP_STACK_FINDINGS.md`
- Current implementation: `src/runtime.py` lines 83-1045
- GOTO implementation: `src/interpreter.py` line 1021
