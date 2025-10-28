# TK UI: Replace INPUT Dialog with Inline Input

## Status: ⏳ TODO

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

## Priority

**MEDIUM** - INPUT works but UX is poor for games

## Files to Modify

- `src/ui/tk_ui.py:3421-3447` - Replace dialog with inline input
- `src/ui/tk_ui.py:150-230` - Add input row UI elements (near immediate mode entry)

## Related

- `docs/dev/WEB_UI_INPUT_UX_TODO.md` - Same issue for web UI
- Both UIs should use consistent inline input approach
