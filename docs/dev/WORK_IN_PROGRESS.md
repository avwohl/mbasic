# Work in Progress: Fix RUN/NEW/LIST in Immediate Mode

**Status:** PLANNING - Need architectural decisions before proceeding

**Task:** Fix `RUN 120` not working in immediate mode, eliminate `interactive_mode` backreference

**Last Updated:** 2025-11-01 v1.0.376

## Problem

User types `RUN 120` in web UI immediate mode → "RUN not available in this context"

Root cause: Multiple architectural issues with how immediate-mode commands are handled.

## Current Broken State (v1.0.376)

1. **RUN 120** executes via immediate executor, which:
   - Clears variables ✓
   - Sets PC to line 120 ✓
   - Returns
   - **But execution timer never starts** ✗

2. **NEW** and **LIST** delegate to `self.interpreter.interactive_mode.cmd_*()` methods
   - This creates a backreference from interpreter → UI
   - Violates separation of concerns
   - User complaint: "flags are bad, we got rid of run. what is interactive_mode?"

3. **`self.running` flag** should only be for UI decoration (spinner), not logic

## Design Questions to Answer

### Q1: Which commands are statements vs immediate-only?

User says: "many programs have run 120 in them" - so RUN IS a statement.

Need to verify for our implementation:
- **RUN** - ✓ Statement (confirmed by user)
- **NEW** - Statement or immediate-only? `100 NEW` would clear program including current line!
- **LIST** - Statement or immediate-only? `100 LIST`
- **AUTO** - Immediate-only?
- **CONT** - Immediate-only?
- **DELETE** - Statement or immediate-only?
- **RENUM** - Statement or immediate-only?

User says: "almost everything is a statement and can be in a program. auto maybe not. but if there is a list ill bet its less than 4"

### Q2: What needs UI access?

**Key insight:** Interpreter doesn't work with program text, it works with AST!

Operations that modify the AST:
- **NEW** - clear the AST (runtime has line_asts dict)
- **DELETE** - remove lines from AST
- **RENUM** - renumber lines in AST

Operations that only need I/O:
- **LIST** - output program lines (should use `self.io.output()`)
- **FILES** - list files (now uses FileIO module ✓)
- **LOAD/SAVE** - use FileIO module ✓

**But wait:** The UI has the program TEXT, interpreter has the AST. They're separate!
- When NEW clears the AST, the UI's text needs to be cleared too
- When DELETE removes lines from AST, the UI's text needs updating
- When user edits text, it gets re-parsed into AST

So: Program modification needs to happen in BOTH places, or text is just a view of AST?

### Q3: How should statements that modify program text work?

Current: `interpreter.interactive_mode.cmd_new()` - BAD

Options:

**Option A: ProgramManager Interface**
- Interpreter has `self.program_manager` reference (not `interactive_mode`)
- ProgramManager is an interface/protocol
- UI provides ProgramManager implementation
- Keeps separation: interpreter doesn't know about UI specifics

**Option B: Event Notifications**
- Interpreter emits events: "program_cleared", "line_deleted", etc.
- UI listens and updates accordingly
- User mentioned: "when an interpreter is created the ui passes in a notify object"

**Option C: Return Values**
- execute_new() returns "clear_program" signal
- Caller (UI) acts on it
- Statement execution becomes multi-step

**Option D: These aren't really statements**
- NEW, DELETE, RENUM are immediate-mode commands only
- Never get into execute_statement() at all
- Contradicts user's guidance that "almost everything is a statement"

### Q4: How should RUN in immediate mode start execution?

When user types `RUN 120`:
1. Immediate executor executes it as statement ✓
2. Statement clears variables, sets PC ✓
3. **How does execution loop start?**

Options:
- A: Check after immediate execution: "is PC valid and not halted? Start timer"
- B: RUN sets a flag/state that UI checks
- C: RUN is special-cased before immediate executor

User says: "get rid of the whole running concept. it is only to turn on a light for the user to say running. why does the UI care?"

So probably: Option A - just check if interpreter should be running after any immediate command.

## Answers from User

1. **Almost all commands are statements** (except maybe AUTO and a few others)

2. **AST is source of truth, text is just a view/cache**
   - "there is an array of pointers into the AST indexed by PCs"
   - Text preserved so syntax errors don't disappear before editing

3. **NEW/DELETE/RENUM operate on AST, then serialize to text**
   - Interpreter modifies AST
   - UI serializes AST → text when needed

4. **No state checking, just ask interpreter if it has work**
   - Add `interpreter.has_work()` method
   - Returns `not runtime.halted()`
   - After immediate execution: if has_work(), start timer

## Solution

### Part 1: Add has_work() method to interpreter

```python
def has_work(self):
    """Does the interpreter have work to do?"""
    return not self.runtime.halted()
```

### Part 2: NEW/DELETE/RENUM modify AST directly

- Remove `interactive_mode` backreference
- execute_new() clears runtime.line_asts, statement_table, etc.
- execute_delete() removes lines from AST
- execute_renum() renumbers lines in AST

### Part 3: UI serializes AST to text after modifications

After immediate execution:
```python
# Sync text with AST (in case NEW/DELETE/RENUM modified it)
lines = self.program.get_lines()  # Serialize AST
editor_text = '\n'.join(line_text for _, line_text in lines)
self.editor.value = editor_text

# Start execution if interpreter has work
if self.interpreter and self.interpreter.has_work():
    if not self.exec_timer:
        self.exec_timer = ui.timer(0.01, self._execute_tick, once=False)
```

### Part 4: Fix LIST to use self.io.output()

No more delegation to UI, just output directly.

## Implementation Plan

### Step 1: Add has_work() to Interpreter
- Add method to interpreter
- Returns `not self.runtime.halted()`
- No state flags needed

### Step 2: Fix execute_new() to modify AST directly
- Remove `interactive_mode.cmd_new()` call
- Clear runtime.line_asts
- Clear runtime.statement_table
- Clear variables/arrays
- Set halted = True

### Step 3: Fix execute_list() to use self.io.output()
- Remove `interactive_mode.cmd_list()` call
- Get lines from runtime.line_asts
- Output directly via self.io.output()

### Step 4: Fix execute_delete() and execute_renum() (if needed)
- Operate on AST directly
- Remove any interactive_mode calls

### Step 5: Update web UI immediate execution
- After immediate execution, serialize AST → text
- Check interpreter.has_work()
- Start timer if has work

### Step 6: Remove interactive_mode references
- Search for all uses of interactive_mode
- Replace with proper AST operations
- Remove the attribute entirely

## Files That Will Need Changes

- src/interpreter.py - replace interactive_mode
- src/program_manager.py - define interface (maybe?)
- src/ui/base.py - ProgramManager interface
- All UIs - provide ProgramManager to interpreter
- src/immediate_executor.py - remove special casing (already done)
- src/ui/web/nicegui_backend.py - check state after immediate execution

## Current Commits

- v1.0.375 - Fixed execute_run() to use stmt.target, added cmd_new() to web UI
- v1.0.376 - Added RUN/NEW/LIST special handling to immediate executor (WRONG - removed)
- v1.0.376 - Reverted to remove special handling from immediate executor

## Progress (v1.0.377)

**Implemented:**
- ✅ Added `interpreter.has_work()` method - returns `not runtime.halted()`
- ✅ Fixed `execute_new()` - modifies AST directly (clears line_asts, statement_table, lines)
- ✅ Fixed `execute_list()` - outputs via `self.io.output()`, no UI delegation
- ✅ Fixed `execute_delete()` - modifies AST directly (removes lines from dictionaries)
- ✅ RENUM marked as TODO (complex - needs GOTO/GOSUB target updates)
- ✅ Web UI immediate execution - serializes AST→text after commands, checks `has_work()`

**Remaining:**
- Some interactive_mode references still exist (LOAD, SAVE, RUN, CHAIN, SYSTEM, MERGE, CONT)
- Need to test if RUN 120 now works

## Next Step

Test `RUN 120` in web UI.

---

**Previous WORK_IN_PROGRESS (CodeMirror 6):**
Completed - switched to CodeMirror 5 instead (v1.0.360-1.0.365)
