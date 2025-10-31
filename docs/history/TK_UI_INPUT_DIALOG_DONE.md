# TK UI: Replace INPUT Dialog with Inline Input

## Status: ✅ IMPLEMENTED (v1.0.173) - Needs Manual Testing

## Problem

**User Feedback:**
> "add todo: tk dont use input dialog"

TK UI currently uses a modal dialog (`simpledialog.askstring()`) for INPUT statements. This has the same UX problem as web UI:

- Modal dialog blocks viewing previous output
- Games with narrative text before INPUT prompts are hard to play
- Breaks immersion and reading flow

**Current Implementation:** `src/ui/tk_ui.py:3421-3447`

```python
def input(self, prompt: str = '') -> str:
    from tkinter import simpledialog

    # Show prompt in output first
    if prompt:
        self.output(prompt, end='')

    # Show modal input dialog
    result = simpledialog.askstring(
        "INPUT",
        prompt if prompt else "Enter value:",
        parent=self.root
    )

    # If user clicked Cancel, raise exception (mimics Ctrl+C)
    if result is None:
        raise KeyboardInterrupt("Input cancelled")

    # Echo the input to output
    self.output(result)

    return result
```

## Recommended Solution

**Use inline input field below output pane** (similar to immediate mode entry that already exists)

### Implementation Approach:

1. **Add input row below output pane:**
   ```python
   # Hidden by default, shown when INPUT needed
   self.input_row = tk.Frame(output_frame)
   self.input_label = tk.Label(self.input_row, text="")  # Shows prompt
   self.input_entry = tk.Entry(self.input_row)
   self.input_submit = tk.Button(self.input_row, text="Submit", command=self._submit_input)
   ```

2. **Modify TkIOHandler.input():**
   ```python
   def input(self, prompt: str = '') -> str:
       # Show prompt in output
       if prompt:
           self.output(prompt, end='')

       # Show input row
       self.show_input_row(prompt)

       # Block until user submits input (use queue or event)
       result = self.input_queue.get()  # Blocking call

       # Hide input row
       self.hide_input_row()

       # Echo input to output
       self.output(result)

       return result
   ```

3. **Use Queue for coordination:**
   ```python
   import queue

   # In __init__:
   self.input_queue = queue.Queue()

   def _submit_input(self):
       value = self.input_entry.get()
       self.input_queue.put(value)
       self.input_entry.delete(0, tk.END)
   ```

4. **Handle Enter key:**
   ```python
   self.input_entry.bind('<Return>', lambda e: self._submit_input())
   ```

### Benefits:

- ✅ Can see all output while typing input
- ✅ Better for games with narrative text
- ✅ More terminal-like experience
- ✅ Similar to immediate mode entry (familiar UX)
- ✅ No modal dialogs blocking view

### Technical Notes:

- Interpreter already uses tick-based execution, so blocking in input() is safe
- Use `queue.Queue()` for thread-safe coordination
- Input row can be hidden/shown as needed
- Similar pattern to immediate mode entry that already exists

## Implementation Complete

**Version:** 1.0.173

**Changes Made:**

1. **Added INPUT row widgets to TkBackend `__init__()`:**
   - `self.input_row` - Frame containing INPUT UI elements
   - `self.input_label` - Label showing prompt text
   - `self.input_entry` - Entry field for user input
   - `self.input_submit_btn` - Submit button
   - `self.input_queue` - Queue for thread-safe coordination

2. **Created INPUT row UI in `start()`:**
   - Added after output_text widget
   - Hidden by default (not packed)
   - Styled similar to immediate mode entry
   - Bound Enter key to submit

3. **Added helper methods to TkBackend:**
   - `_show_input_row(prompt)` - Display INPUT row with prompt
   - `_hide_input_row()` - Hide INPUT row after submission
   - `_submit_input()` - Handle input submission

4. **Modified TkIOHandler:**
   - Added `backend` parameter to `__init__()`
   - Replaced `input()` method to use inline input row
   - Uses queue.Queue() for blocking coordination
   - Fallback to dialog if backend not available

5. **Updated TkIOHandler instantiation:**
   - Line 294: `TkIOHandler(self._add_output, self.root, backend=self)`
   - Line 2813: `TkIOHandler(self._add_output, self.root, backend=self)`

**Benefits Achieved:**
- ✅ Can see all output while typing input
- ✅ Better for games with narrative text
- ✅ More terminal-like experience
- ✅ Similar to immediate mode entry (familiar UX)
- ✅ No modal dialogs blocking view

**Testing:**

Manual test required (TK backend doesn't support CLI loading yet):

```bash
python3 mbasic --backend tk
# Load tests/test_curses_input.bas
# Run program
# Verify inline input appears below output
```

See `tests/test_tk_input_manual.md` for detailed test procedure.

## Files Modified

- `src/ui/tk_ui.py` - ~100 lines changed (INPUT row UI, helper methods, TkIOHandler.input())
- `tests/test_tk_input_manual.md` - Manual test instructions

## Related

- `docs/dev/WEB_UI_INPUT_UX_TODO.md` - Same issue for web UI (next task)
- `docs/dev/CURSES_UI_INPUT_CHECK_TODO.md` - Curses model we followed
