# Immediate Mode Execution Safety

**Date**: 2025-10-25
**Status**: Critical Implementation Note

## TL;DR

**NEVER execute immediate mode while `interpreter.state.status == 'running'`**

Always check `executor.can_execute_immediate()` before execution in tick-based UIs.

## The Problem

Visual UIs (Curses, Tk, Web) use **tick-based execution** where the interpreter processes one statement at a time via `tick()` calls. If immediate mode executes BASIC statements while the main program is mid-tick, it will:

❌ **Corrupt interpreter state** (line_index, current_line, statement_index)
❌ **Break control flow** (FOR loops, GOSUBs, WHILE loops)
❌ **Cause crashes** when program resumes
❌ **Produce incorrect results**

## The Solution

### 1. Safe States (Immediate Mode ENABLED)

Immediate mode is **safe** when interpreter is NOT actively executing:

| State | Description | Can Execute? |
|-------|-------------|--------------|
| `'idle'` | No program loaded | ✅ YES |
| `'paused'` | User stopped program (Ctrl+Q) | ✅ YES |
| `'at_breakpoint'` | Hit breakpoint | ✅ YES (BEST for debugging) |
| `'done'` | Program finished | ✅ YES |
| `'error'` | Runtime error occurred | ✅ YES |

### 2. Unsafe States (Immediate Mode DISABLED)

Immediate mode is **unsafe** when interpreter is actively executing:

| State | Description | Can Execute? |
|-------|-------------|--------------|
| `'running'` | Program is executing `tick()` | ❌ NO (will corrupt state) |
| `'waiting_for_input'` | Program waiting for INPUT | ❌ NO (use normal input) |

## Implementation Checklist

### For UI Developers

- [ ] Import `ImmediateExecutor` from `src/immediate_executor.py`
- [ ] Create executor with current runtime/interpreter
- [ ] Check `executor.can_execute_immediate()` before EVERY execution
- [ ] Disable immediate input field when `status == 'running'`
- [ ] Enable immediate input field when status changes to safe state
- [ ] Update panel state after every `tick()` call
- [ ] Show clear visual indicator when immediate mode is disabled

### Code Template

```python
from immediate_executor import ImmediateExecutor, OutputCapturingIOHandler

# Initialize
io_capture = OutputCapturingIOHandler()
executor = ImmediateExecutor(runtime, interpreter, io_capture)

# Update context when program starts/stops
def on_program_start():
    executor.set_context(self.runtime, self.interpreter)

# In main UI loop (after every tick)
def update_immediate_panel():
    if executor.can_execute_immediate():
        immediate_input.enable()
        immediate_status.text = "Ok"
    else:
        immediate_input.disable()
        immediate_status.text = f"[{interpreter.state.status}]"

# When user presses Enter in immediate panel
def on_immediate_execute(command):
    if executor.can_execute_immediate():
        success, output = executor.execute(command)
        immediate_history.append(f"> {command}")
        immediate_history.append(output)
    else:
        immediate_history.append("Error: Program is running")
```

## Visual Feedback

### Status Indicators

Show clear status in the immediate panel:

```
When ENABLED:
┌─────────────────────────┐
│ Immediate Mode          │
│ Ok                      │ ← Green indicator
│ > █                     │ ← Active cursor
└─────────────────────────┘

When DISABLED:
┌─────────────────────────┐
│ Immediate Mode          │
│ [running]               │ ← Red/gray indicator
│ > _                     │ ← Grayed out
└─────────────────────────┘
```

### Color Coding

- **Green "Ok"** - Safe to execute
- **Red "[running]"** - Cannot execute (program running)
- **Gray input** - Disabled during execution
- **White input** - Enabled when safe

## State Transition Examples

### Example 1: Normal Execution

```
1. User loads program
   Status: 'idle'
   Immediate: ✅ ENABLED

2. User presses Run (Ctrl+R)
   Status: 'idle' → 'running'
   Immediate: ✅ ENABLED → ❌ DISABLED

3. Program executes (tick, tick, tick...)
   Status: 'running'
   Immediate: ❌ DISABLED

4. Program finishes
   Status: 'running' → 'done'
   Immediate: ❌ DISABLED → ✅ ENABLED
```

### Example 2: Debugging with Breakpoint

```
1. User sets breakpoint at line 50
   Status: 'idle'
   Immediate: ✅ ENABLED

2. User runs program
   Status: 'idle' → 'running'
   Immediate: ✅ ENABLED → ❌ DISABLED

3. Program hits breakpoint at line 50
   Status: 'running' → 'at_breakpoint'
   Immediate: ❌ DISABLED → ✅ ENABLED

4. User inspects variables
   > PRINT X
    42
   > PRINT A$
   "Hello"

5. User modifies variable
   > X = 100
   Ok

6. User continues execution (Ctrl+G)
   Status: 'at_breakpoint' → 'running'
   Immediate: ✅ ENABLED → ❌ DISABLED

7. Program resumes with X=100
```

### Example 3: Stop and Inspect

```
1. Program is running
   Status: 'running'
   Immediate: ❌ DISABLED

2. User presses Ctrl+Q (stop)
   Status: 'running' → 'paused'
   Immediate: ❌ DISABLED → ✅ ENABLED

3. User can now inspect state
   > PRINT I, J, K
    1     2     3
   Ok
```

## Testing Checklist

### Manual Tests

- [ ] Start program, verify immediate mode disabled during execution
- [ ] Stop program (Ctrl+Q), verify immediate mode enabled
- [ ] Set breakpoint, verify immediate mode enabled when hit
- [ ] Try to execute immediate command while running (should be blocked)
- [ ] Verify variables accessible at breakpoint
- [ ] Verify variable modifications persist after continue
- [ ] Verify immediate mode enabled after program ends
- [ ] Verify immediate mode enabled after error

### Automated Tests

Create test that:
1. Starts program execution
2. Attempts immediate execution while running (should fail)
3. Hits breakpoint
4. Executes immediate mode (should succeed)
5. Modifies variable
6. Continues execution
7. Verifies modified value used

## Common Mistakes

### ❌ WRONG: No state check

```python
# DANGEROUS - can execute while running!
def on_enter_pressed(command):
    success, output = executor.execute(command)
    show_output(output)
```

### ✅ CORRECT: Always check state

```python
def on_enter_pressed(command):
    if executor.can_execute_immediate():
        success, output = executor.execute(command)
        show_output(output)
    else:
        show_error("Cannot execute while program is running")
```

### ❌ WRONG: Only check once at startup

```python
# WRONG - state changes during execution!
if executor.can_execute_immediate():
    immediate_panel.enable()  # Stays enabled forever!
```

### ✅ CORRECT: Check after every tick

```python
# Correct - update after every state change
while True:
    if interpreter.state.status == 'running':
        interpreter.tick()

    # Update immediate panel after tick
    if executor.can_execute_immediate():
        immediate_panel.enable()
    else:
        immediate_panel.disable()
```

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│              Visual UI                      │
│  ┌──────────────────────────────────────┐  │
│  │ Main Loop                            │  │
│  │  - Process input                     │  │
│  │  - Call tick() if running            │  │
│  │  - Update immediate panel state      │  │
│  │  - Render screen                     │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │ Immediate Panel                      │  │
│  │  - Check can_execute_immediate()     │  │
│  │  - Enable/disable input              │  │
│  │  - Execute when safe                 │  │
│  │  - Show status indicator             │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                    ↓
          ┌─────────────────────┐
          │ ImmediateExecutor   │
          │  - can_execute()    │
          │  - execute()        │
          └─────────────────────┘
                    ↓
          ┌─────────────────────┐
          │ Interpreter         │
          │  - state.status     │
          │  - tick()           │
          │  - execute_stmt()   │
          └─────────────────────┘
```

## Summary

✅ **Always check** `can_execute_immediate()` before execution
✅ **Disable** immediate mode when `status == 'running'`
✅ **Enable** immediate mode when status changes to safe state
✅ **Update** panel state after every `tick()` call
✅ **Show** clear visual indicator of enabled/disabled state

Immediate mode is a powerful debugging tool, but it MUST be used safely in tick-based execution environments. Following these guidelines ensures state integrity and prevents crashes.
