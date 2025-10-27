# Work in Progress

## Task
Fix immediate mode entry widget not accepting input in TK UI

## Status
- ✅ Identified root cause: immediate_executor not initialized at startup
- ✅ Identified root cause: entry widget not explicitly enabled/focused
- ✅ Fixed: Initialize entry to NORMAL state and set focus after 100ms
- ✅ Fixed: Create immediate executor at startup with None context
- ✅ Fixed: Update immediate executor context when program runs (instead of recreating)
- ✅ Identified second issue: ttk.Entry may have focus issues
- ✅ Fixed: Changed from ttk.Entry to tk.Entry for better input reliability
- ✅ Fixed: Use focus_force() instead of focus_set() for more reliable focus
- ⏳ Testing: Need to manually test in TK UI (second attempt)

## Files Modified
- src/ui/tk_ui.py (lines 229-238, 2417-2420)

## Root Causes
1. **Entry widget not initialized**: The immediate_entry widget was created but never explicitly set to NORMAL state or given focus
2. **Immediate executor not created**: The immediate_executor was only created when a program ran (_menu_run), not at UI startup
3. **Early return in _update_immediate_status**: When immediate_executor was None, the method returned early without enabling the entry
4. **ttk.Entry focus issues**: ttk.Entry widget may not reliably accept focus/input in all scenarios
5. **Weak focus methods**: focus_set() may not work reliably; focus_force() is more aggressive

## Changes Made

### 1. Change from ttk.Entry to tk.Entry (line 219)
```python
# Use tk.Entry instead of ttk.Entry for better input reliability
self.immediate_entry = tk.Entry(input_frame, font=("Courier", 10), state='normal')
```

### 2. Initialize entry widget with focus_force (lines 230-235)
```python
# Initialize immediate mode entry to be enabled and focused
self.immediate_entry.config(state=tk.NORMAL)
# Give initial focus to immediate entry for convenience
# Use focus_force to ensure focus is actually set
self.root.after(100, lambda: self.immediate_entry.focus_force())
```

### 3. Create immediate executor at startup (lines 237-240)
```python
# Initialize immediate executor for standalone use (no program running)
immediate_io = OutputCapturingIOHandler()
self.immediate_executor = ImmediateExecutor(runtime=None, interpreter=None, io_handler=immediate_io)
```

### 4. Update context instead of recreating (lines 2417-2420)
```python
# Update immediate mode executor context to use program's runtime and interpreter
if self.immediate_executor:
    self.immediate_executor.set_context(self.runtime, self.interpreter)
```

### 5. Use focus_force in click handler (line 2701)
```python
self.immediate_entry.focus_force()  # Changed from focus_set()
```

## Next Steps
1. ~~Test immediate mode entry accepts input on startup~~
2. Test immediate mode works before running a program
3. Test immediate mode works during program execution (at breakpoint/error/paused)
4. Commit changes if tests pass

## Test Plan
1. Launch `python3 mbasic.py --ui tk`
2. Verify cursor appears in immediate mode entry
3. Type "PRINT 123" and press Enter
4. Verify output appears in immediate history
5. Load test program: basic/test_immediate_input.bas
6. Run program and pause at breakpoint
7. Verify immediate mode works during pause

## Context/Notes
- ImmediateExecutor supports None context and creates temporary runtime when needed
- Entry widget needs explicit state=NORMAL after creation
- Focus must be set after window is realized (using after(100, ...))
