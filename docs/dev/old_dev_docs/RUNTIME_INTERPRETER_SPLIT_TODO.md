# Runtime/Interpreter Architecture Split - TODO

## Issue
The split between Runtime and Interpreter classes seems somewhat arbitrary and they have pointers into each other's data, creating tight coupling.

**Current structure:**
- **Runtime** (`src/runtime.py`): Holds persistent data across program runs
  - Variables, arrays, program lines
  - DEF FNs, DATA statements, READ pointer
  - RANDOMIZE seed, trace settings
  - Breakpoints (newly added)

- **Interpreter** (`src/interpreter.py`): Handles execution
  - Creates new InterpreterState each run
  - Has pointer to Runtime (`self.runtime`)
  - Delegates to Runtime for variable access

- **InterpreterState** (`src/interpreter.py`): Temporary execution state
  - PC (program counter), call stack, FOR loops
  - Status (running/paused/error/at_breakpoint)
  - Input handling state
  - Error info
  - Previously had breakpoints (now removed)

**Cross-references:**
- Interpreter has `self.runtime`
- Runtime operations often need access to interpreter state
- Some data could arguably live in either place

## Questions to Answer

1. **Is this split beneficial or just complexity?**
   - Does it make the code clearer or more confusing?
   - Are there clear ownership boundaries?

2. **Should these be merged?**
   - Would a single Interpreter class with persistent/transient sections be simpler?
   - Or is the separation of concerns actually valuable?

3. **If keeping separate, what's the principle?**
   - Runtime = "BASIC machine state" (variables, program, settings)
   - Interpreter = "execution engine" (control flow, statement execution)
   - State = "current execution context" (PC, stack, status)

4. **What about breakpoints?**
   - We just moved breakpoints from InterpreterState → Runtime
   - This makes sense because they persist across runs
   - Should this pattern guide other decisions?

## Next Steps

1. **Document the current split** with clear principles if it makes sense
   - Add doc comments to runtime.py and interpreter.py explaining the split
   - Create architecture doc in docs/design/

2. **OR refactor to simplify** if the split is unnecessarily complex
   - Consider merging Runtime into Interpreter
   - Or clarify the interface between them

## Context
- This came up during breakpoint refactoring
- User observation: "im rather vague as to the runtime/interpreter split. it seems arbitrary"
- The bidirectional dependencies suggest the abstraction boundary may be unclear
