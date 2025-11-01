# TODO: Move UI-Delegated Statements to Interpreter Implementation

## Problem

Many BASIC statements are currently implemented by delegating to UI `cmd_*` methods:
- FILES, LOAD, SAVE, MERGE, NEW, DELETE, RENUM, LIST, CHAIN

This causes problems:
1. **Web UI is missing all 12 cmd_* methods** - statements don't work
2. **Statements can't work in programs** - only immediate mode
3. **Violates MBASIC semantics** - these are regular statements, not "UI commands"

## Real MBASIC Behavior

In real MBASIC 5.21, these are **regular BASIC statements** that work:
- In immediate mode (typing at Ok prompt)
- Inside programs (with line numbers)

Example from real MBASIC:
```basic
Ok
100 files
run
[lists files - works fine inside program]

Ok
files
[also works in immediate mode]
```

**Nothing is "immediate mode only"** - they're all just statements.

## Current Wrong Implementation

**src/interpreter.py - execute_files (lines 2004-2006):**
```python
if hasattr(self, 'interactive_mode') and self.interactive_mode:
    self.interactive_mode.cmd_files(filespec)
else:
    # Fallback implementation...
```

This pattern is used for:
- FILES → `cmd_files(filespec)`
- LOAD → `cmd_load(filename)`
- SAVE → `cmd_save(filename)`
- RUN → `cmd_run()` and `cmd_load(filename)`
- CHAIN → `cmd_chain(filename, start_line)`
- SYSTEM → `cmd_system()`
- MERGE → `cmd_merge(filename)`
- NEW → `cmd_new()`
- DELETE → `cmd_delete(args)`
- RENUM → `cmd_renum(args)`
- LIST → `cmd_list(args)`
- CONT → `cmd_cont()`

## Progress Update (2025-11-01)

**✅ FILES - COMPLETE (v1.0.370)**
- Implemented FileIO module architecture (see FILEIO_MODULE_ARCHITECTURE_DONE.md)
- `Interpreter` now takes `file_io` parameter (defaults to `RealFileIO`)
- Web UI passes `SandboxedFileIO` (browser localStorage)
- Local UIs pass `None` (uses `RealFileIO` for direct filesystem)
- `execute_files()` now uses `self.file_io.list_files()` - no UI delegation
- Web UI is sandboxed - no server filesystem access
- Works in all UIs, both immediate mode and in programs

## Missing cmd_* Methods in Web UI

Remaining 11 cmd_* methods still missing from `src/ui/web/nicegui_backend.py`:
```
✅ cmd_files - COMPLETE (uses FileIO module)
✗ cmd_load - MISSING
✗ cmd_save - MISSING
✗ cmd_run - MISSING
✗ cmd_chain - MISSING
✗ cmd_system - MISSING
✗ cmd_merge - MISSING
✗ cmd_new - MISSING
✗ cmd_delete - MISSING
✗ cmd_renum - MISSING
✗ cmd_list - MISSING
✗ cmd_cont - MISSING
```

Web UI has equivalent functionality as `_menu_*` methods, but interpreter can't find them.

## Correct Implementation

**These statements should be 100% in the interpreter (no UI delegation):**

### 1. ✅ FILES - List Directory (COMPLETE)
**Status:** Implemented via FileIO module (v1.0.370)
- Uses `self.file_io.list_files(filespec)`
- Sandboxed for web UI (browser localStorage)
- Real filesystem for local UIs
- See: `src/file_io.py`, `FILEIO_MODULE_ARCHITECTURE_DONE.md`

### 2. LOAD - Load Program
Should load program into ProgramManager directly:
```python
# In interpreter
success, errors = self.program_manager.load_from_file(filename)
if errors:
    for line_num, error in errors:
        self.io.output(f"Parse error at line {line_num}: {error}")
if success:
    self.io.output(f"Loaded: {filename}")
```

**Note:** Interpreter needs reference to ProgramManager (currently only UIs have it).

### 3. SAVE - Save Program
```python
self.program_manager.save_to_file(filename)
self.io.output(f"Saved: {filename}")
```

### 4. MERGE - Merge Program
```python
success, errors = self.program_manager.merge_from_file(filename)
if errors:
    for line_num, error in errors:
        self.io.output(f"Parse error at line {line_num}: {error}")
if success:
    self.io.output(f"Merged: {filename}")
```

### 5. NEW - Clear Program
```python
self.program_manager.clear()
self.runtime.reset_for_run({}, {})  # Clear runtime too
self.io.output("New")
```

### 6. DELETE - Delete Lines
```python
# Parse args like "100-200"
start, end = parse_delete_args(args)
for line_num in range(start, end + 1):
    self.program_manager.delete_line(line_num)
```

### 7. RENUM - Renumber Lines
```python
# Parse args like "1000,100,10"
new_start, old_start, increment = parse_renum_args(args)
self.program_manager.renum(new_start, old_start, increment)
```

### 8. LIST - List Program Lines
```python
# Parse args like "100-200"
start, end = parse_list_args(args)
for line_num in sorted(self.program_manager.lines.keys()):
    if start <= line_num <= end:
        self.io.output(self.program_manager.lines[line_num])
```

### 9. CHAIN - Load and Run
```python
# CHAIN is just: LOAD + RUN (with optional line)
success, errors = self.program_manager.load_from_file(filename)
if success:
    self.runtime.reset_for_run(
        self.program_manager.line_asts,
        self.program_manager.lines
    )
    if start_line:
        self.runtime.pc = PC.from_line(start_line)
    else:
        # Start from first line
        first_line = min(self.program_manager.lines.keys())
        self.runtime.pc = PC.from_line(first_line)
```

## What About CONT and AUTO?

**CONT (Continue):**
- Needs runtime state check (can only continue if stopped/paused)
- Already implemented in interpreter (execute_cont)
- Keep as-is (not a UI delegation issue)

**AUTO (Auto line numbering):**
- This is an **editor feature**, not a BASIC statement
- Real MBASIC has AUTO for interactive line entry
- Should stay in UI (generates line numbers interactively)
- Not a statement that executes in programs

## Architecture Change Needed

**Problem:** Interpreter doesn't have reference to ProgramManager.

**Current:**
```
UI Backend → owns ProgramManager
           → creates Interpreter
Interpreter → no access to ProgramManager
```

**Needed:**
```
UI Backend → creates ProgramManager
           → creates Interpreter with ProgramManager reference
Interpreter → can modify ProgramManager for LOAD/SAVE/etc
```

**Fix:**
1. Add `self.program_manager` to Interpreter constructor
2. Pass ProgramManager when creating Interpreter
3. Statements can now modify program directly

## Implementation Plan

### Phase 1: Add ProgramManager to Interpreter
- Modify `Interpreter.__init__()` to accept `program_manager` parameter
- Update all UI backends to pass ProgramManager when creating Interpreter

### Phase 2: Move Statements to Interpreter (one at a time)
1. **FILES** - Remove delegation, always use direct implementation
2. **LIST** - Implement directly in interpreter using ProgramManager
3. **DELETE** - Implement directly
4. **RENUM** - Implement directly
5. **NEW** - Implement directly
6. **LOAD** - Implement directly
7. **SAVE** - Implement directly
8. **MERGE** - Implement directly
9. **CHAIN** - Implement as LOAD + RUN

### Phase 3: Remove cmd_* Methods from UIs
- Once all statements work via interpreter, remove cmd_* methods from UI backends
- Keep `_menu_*` methods for menu actions (they can call the statements via immediate executor)

## Benefits

1. **Statements work in all UIs** - no need for each UI to implement cmd_* methods
2. **Statements work in programs** - not just immediate mode
3. **Consistent behavior** - all UIs behave the same way
4. **Less code duplication** - implement once in interpreter, not in each UI
5. **Matches real MBASIC semantics** - these are statements, not UI commands

## Files to Modify

- `src/interpreter.py` - Add ProgramManager reference, implement statements directly
- `src/ui/web/nicegui_backend.py` - Pass ProgramManager to Interpreter
- `src/ui/tk_ui.py` - Pass ProgramManager to Interpreter
- `src/ui/curses_ui.py` - Pass ProgramManager to Interpreter
- `src/ui/cli.py` - Pass ProgramManager to Interpreter

## Priority

High - this fixes fundamental architecture issue and makes statements work in web UI

## Date Created

2025-11-01
