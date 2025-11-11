# Breakpoint Display Fix

## Problem

When a breakpoint was hit, the screen showed blank with only the breakpoint status header visible. The user couldn't see the editor content or output window during the breakpoint pause.

## Root Cause

The original `_breakpoint_hit()` method was calling `curses.initscr()`, which creates a **new** curses screen, blanking out the existing npyscreen interface.

```python
# WRONG - creates new screen
stdscr = curses_module.initscr()
```

## Solution

Access the **existing** npyscreen curses window instead of creating a new one:

1. Use the form's widgets (editor, output) which are already displayed
2. Call `form.editor.display()` and `form.output.display()` to refresh content
3. Use `curses.doupdate()` to push changes to the physical screen
4. Access the parent window through `form.editor.parent` to draw status and get input
5. Restore the normal display by calling `form.display()` after breakpoint

```python
# CORRECT - use existing npyscreen windows
form.editor.display()
form.output.display()
curses.doupdate()

parent_window = form.editor.parent
parent_window.addstr(0, 0, status_msg, curses.A_REVERSE)
parent_window.noutrefresh()
curses.doupdate()
```

## Key Changes

### Before (src/ui/curses_ui.py:443-504)
- Called `curses.initscr()` - created new blank screen
- Used new `stdscr` for all operations
- Screen content was lost

### After (src/ui/curses_ui.py:443-529)
- Uses existing `form.editor.parent` window
- Calls `form.editor.display()` and `form.output.display()` first
- Uses `curses.doupdate()` to synchronize updates
- Calls `form.display()` to restore after breakpoint
- Screen content remains visible

## Testing

### Manual Test
```bash
./test_continue_fix.sh
```

### What You Should See

When breakpoint hits:
- ✅ Editor window with your BASIC code visible
- ✅ Output window with program output so far
- ✅ Status line at top: "BREAKPOINT at line XX - Press 'c' continue, 's' step, 'e' end"
- ❌ NOT a blank screen!

### Test Steps
1. Open test program: `python3 mbasic --ui curses test_continue.bas`
2. Set breakpoint on line 20 (press 'b')
3. Run with Ctrl+R
4. **Verify**: Can you see the program code?
5. **Verify**: Can you see the output?
6. **Verify**: Status line shows breakpoint info?
7. Press 'c' to continue
8. Program should complete and show output

## npyscreen Window Hierarchy

Understanding the window structure:

```
NPSAppManaged (app)
  └─> Form (main_form)
        ├─> parent = curses window for the form
        ├─> editor (MultiLineEdit widget)
        │     └─> parent = curses window (subwindow of form)
        └─> output (MultiLineEdit widget)
              └─> parent = curses window (subwindow of form)
```

Each npyscreen widget has a `.parent` attribute which is the curses window it draws to.

## Implementation Details

The fix uses npyscreen's built-in curses window management:

1. **Display Update**: Call widget `.display()` methods to update their content
2. **Screen Sync**: Use `curses.doupdate()` to push to physical screen
3. **Status Drawing**: Use `.parent.addstr()` to draw over the menu bar
4. **Input Handling**: Use `.parent.getch()` for keyboard input
5. **Restore**: Call `form.display()` to redraw everything cleanly

### Why This Works

npyscreen uses curses "pads" and "windows" internally:
- Forms create curses windows for their widgets
- Widgets draw to their parent windows
- `noutrefresh()` stages changes
- `doupdate()` applies all staged changes at once

By using the existing windows, we preserve all the content that's already there.

## Debugging

If the screen is still blank, check:

1. **Is `form.editor.display()` being called?**
   - This refreshes the editor content

2. **Is `curses.doupdate()` being called?**
   - This pushes changes to the screen

3. **Is `parent_window` valid?**
   - Check that `form.editor.parent` exists

4. **Are exceptions being silenced?**
   - Check stderr: `2> /tmp/mbasic_debug.log`

## Alternative Approaches Considered

### 1. Use curses.stdscr directly
- **Problem**: We don't have direct access to npyscreen's stdscr
- **Why not**: npyscreen wraps it internally

### 2. Temporarily exit npyscreen
- **Problem**: Would require saving/restoring state
- **Why not**: Too complex, loses context

### 3. Use npyscreen notify
- **Problem**: Creates a popup, hides code
- **Why not**: Defeats the purpose of seeing code during debug

### 4. Use current approach (CHOSEN)
- **Advantage**: Uses existing windows, keeps content visible
- **Advantage**: Minimal changes to npyscreen state
- **Advantage**: Clean restore with `form.display()`

## Status

- ✅ Fix implemented in src/ui/curses_ui.py:443-529
- 🔄 Awaiting manual testing to confirm screen is visible
- 📝 Documentation updated

## Next Steps

1. Test manually with `./test_continue_fix.sh`
2. Verify editor and output are visible during breakpoint
3. If still blank, add debug output to check window state
4. Consider highlighting the current line being debugged (future enhancement)
