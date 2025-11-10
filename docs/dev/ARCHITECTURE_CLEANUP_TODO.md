# Architecture Cleanup TODO

**Created:** 2025-11-10
**Status:** Not Started
**Priority:** High - Affects maintainability and bug potential

## Overview

The codebase has several architectural issues that make it difficult to maintain and prone to bugs:

1. **State Management Flags** - Multiple overlapping execution state flags
2. **Program Representation Duplication** - Text, AST, and serialized forms kept in sync manually
3. **Encapsulation Violations** - UIs directly access and modify interpreter/runtime internals

## Issue 1: State Management Flags

### Current State

**Runtime state flags found:**
- `runtime.stopped` - True if program stopped via STOP or Break
- `runtime.halted` - True if program not running / execution finished

**Historical context:**
- User asked to reduce from ~8 flags to fewer
- Some consolidation happened, but issues remain

### Problems

1. **Unclear semantics:** What's the difference between `stopped` and `halted`?
   - `stopped` = paused, can CONT
   - `halted` = finished/not running, cannot CONT
   - But both are checked/modified in overlapping ways

2. **UIs directly modify these flags:**
   ```python
   # curses_ui.py line 2068
   self.runtime.halted = False

   # curses_ui.py line 3694
   self.runtime.stopped = True
   ```

3. **No single source of truth** for execution state

### Proposed Solution

- [ ] Document the **exact semantics** of each flag
- [ ] Create a **state diagram** showing valid transitions
- [ ] Add **accessor methods** instead of direct flag access:
  ```python
  runtime.pause_execution()  # instead of runtime.stopped = True
  runtime.resume_execution() # instead of runtime.stopped = False
  runtime.halt()            # instead of runtime.halted = True
  runtime.is_stopped()      # instead of reading runtime.stopped
  ```
- [ ] Encapsulate flag logic in runtime, prevent external modification

### Files to Modify

- `src/runtime.py` - Add state management methods
- `src/ui/curses_ui.py` - 20+ direct flag modifications
- `src/ui/tk_ui.py` - Similar violations
- `src/ui/web/nicegui_backend.py` - Similar violations
- `src/interpreter.py` - Use new methods
- `src/interactive.py` - Use new methods

## Issue 2: Program Representation Duplication

### Current State

**Three representations exist:**

1. **Text (editor_lines)** - What the editor displays
   - Stored in: `curses_ui.editor_lines`, `tk_ui.editor_text`
   - Format: List of strings or Text widget content

2. **AST (line_asts)** - Parsed abstract syntax tree
   - Stored in: `interactive.line_asts`
   - Format: Dict mapping line number → AST node

3. **Serialized (statement_table)** - Runtime execution form
   - Stored in: `runtime.statement_table`
   - Format: List of executable statements

### Problems

1. **Manual synchronization:**
   ```python
   # Add line to AST
   self.line_asts[line_num] = parsed_ast

   # Add line to editor
   self.editor_lines.append(text)

   # Rebuild statement_table
   self.runtime.statement_table = ...
   ```

2. **Sync failures create bugs:**
   - Editor shows line 100 but AST doesn't have it
   - Runtime executes stale code from old statement_table
   - Line numbers in error messages don't match editor

3. **50+ places** in curses_ui.py alone juggle these representations

### Proposed Solution

- [ ] **Single source of truth:** AST should be canonical
- [ ] **Derived representations:**
  ```python
  editor_lines = program.to_text()  # Generated from AST
  statement_table = program.to_executable()  # Generated from AST
  ```
- [ ] **Lazy regeneration:** Only rebuild when needed
- [ ] **Hide internals:** Editor shouldn't access AST directly

### Files to Modify

- Create new: `src/program_model.py` - Unified program representation
- `src/interactive.py` - Replace line_asts with ProgramModel
- `src/ui/curses_ui.py` - Use ProgramModel API, remove direct AST access
- `src/ui/tk_ui.py` - Same
- `src/runtime.py` - Accept prebuilt statement_table from ProgramModel

## Issue 3: Encapsulation Violations

### Current State

**UIs directly access interpreter/runtime internals:**

```python
# curses_ui.py examples:
self.runtime.halted = False                    # Line 2068
self.runtime.stopped = True                    # Line 3694
self.runtime.pc = new_pc                       # (if exists)
self.program.line_asts[num] = ast             # Direct dict modification
```

### Problems

1. **No API contract** - UIs can modify anything
2. **Breaking changes hidden** - Renaming a field breaks all UIs
3. **State invariants violated** - PC set without updating NPC, etc.
4. **Testing nightmare** - Can't test interpreter without UI

### Proposed Solution

- [ ] **Define public API** for interpreter/runtime:
  ```python
  # Public methods (safe to call)
  interpreter.run()
  interpreter.step()
  interpreter.stop()
  interpreter.set_breakpoint(line)

  # Private internals (UIs should not touch)
  interpreter._runtime  # Not interpreter.runtime
  interpreter._pc       # Not interpreter.pc
  ```

- [ ] **Make fields private** (prefix with `_`)
- [ ] **Provide accessor methods** for legitimate UI needs
- [ ] **Document the contract** in docstrings

### Files to Modify

- `src/interpreter.py` - Make fields private, add public methods
- `src/runtime.py` - Same
- `src/interactive.py` - Same
- All UIs - Update to use public API only

## Implementation Plan

### Phase 1: Documentation (1-2 days)
- [ ] Document current state semantics
- [ ] Create state diagrams
- [ ] List all encapsulation violations

### Phase 2: State Management (3-5 days)
- [ ] Add state management methods to runtime
- [ ] Update all callers to use methods
- [ ] Remove direct flag access
- [ ] Add tests for state transitions

### Phase 3: Program Representation (5-7 days)
- [ ] Design ProgramModel class
- [ ] Migrate interactive.py to use ProgramModel
- [ ] Update UIs to use ProgramModel API
- [ ] Remove direct AST/line_asts access

### Phase 4: Encapsulation (3-5 days)
- [ ] Define public APIs
- [ ] Make internal fields private
- [ ] Update all UIs to use public API
- [ ] Add API documentation

### Phase 5: Testing & Validation (2-3 days)
- [ ] Write unit tests for new APIs
- [ ] Integration tests for UI interactions
- [ ] Manual testing of all UIs
- [ ] Performance regression testing

**Total Estimated Time:** 14-22 days

## Success Metrics

After completion:
- [ ] Zero direct assignments to `runtime.stopped/halted` outside runtime.py
- [ ] Single source of truth for program representation
- [ ] All interpreter/runtime fields are private (`_` prefix)
- [ ] UIs only call public methods, never access internal state
- [ ] State transitions documented and enforced
- [ ] Consistency checker finds fewer "unclear interaction" issues

## Notes

This refactoring will cause merge conflicts with any in-progress work. Recommend:
1. Complete all pending v20 fixes first
2. Create a feature branch for this refactoring
3. Merge incrementally (phase by phase) to catch regressions early

## Related Issues

- Consistency checker v1-v20 repeatedly flagged state management confusion
- CONT command bug (can't detect if program was edited) - architectural issue
- PC/NPC synchronization bugs - encapsulation issue
- Editor sync bugs - program representation issue
