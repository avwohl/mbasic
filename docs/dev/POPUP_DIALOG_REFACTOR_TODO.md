# Popup Dialog Refactor TODO

## Problem
Current dialog implementation uses nested event loops (`self.loop.run()` called recursively), which breaks urwid's event loop and causes ESC key to close the entire application instead of just the dialog.

## Root Cause
Calling `self.loop.run()` while already inside the event loop creates nested loops. Exceptions like `DialogExit` or `ExitMainLoop` exit all loops, not just the innermost one.

## Proper Solution
Use urwid's `PopUpLauncher` pattern which is callback-driven and doesn't require nested event loops.

## Implementation Plan

### 1. Dialog Widget Classes (DONE)
- ✅ Created `InputDialog` class with 'close' signal
- ✅ Created `YesNoDialog` class with 'close' signal
- Both widgets emit signals with results instead of using return values

### 2. Wrap Main UI in PopUpLauncher (DONE)
- ✅ Created `MainUIWithPopups` class that extends `PopUpLauncher`
- ✅ Added `show_input_popup()` and `show_yesno_popup()` methods
- ✅ Updated `_create_ui()` to wrap main widget in PopUpLauncher
- ✅ Integrated into MainLoop

### 3. Convert Dialog Methods
Replace synchronous dialog methods with async/callback versions:

**Before:**
```python
def _load_program(self):
    filename = self._get_input_dialog("Load file: ")
    if not filename:
        return
    # ... use filename
```

**After:**
```python
def _load_program(self):
    self._show_input_popup("Load file: ", self._on_load_filename)

def _on_load_filename(self, filename):
    if not filename:
        return
    # ... use filename
```

### 4. Refactor These Methods
- `_get_input_dialog()` → `_show_input_popup(prompt, callback)`
- `_show_yesno_dialog()` → `_show_yesno_popup(title, message, callback)`
- All callers of these methods need callback versions

### 5. Update Callers
Methods that call dialogs:

**DONE:**
- ✅ `_load_program()` - file open dialog (curses_ui.py:4067)
  - ✅ Tested: ESC closes dialog without crashing UI
  - ✅ Tested: UI remains responsive after dialog

**TODO (9 remaining _get_input_dialog calls):**
- ⏳ Line 2390: Auto-numbering response handler
- ⏳ Line 2447: `_renumber_lines()` - start line number input
- ⏳ Line 2461: `_renumber_lines()` - increment input
- ⏳ Line 3054: Variable editing - array subscripts
- ⏳ Line 3093: Variable editing - new value for scalar
- ⏳ Line 3132: Variable editing - new value (alternate path)
- ⏳ Line 3611: Settings filter input
- ⏳ Line 3974: `_save_program()` - save as dialog
- ⏳ Line 4022: `_save_as_program()` - save as dialog

### 6. Testing
**DONE:**
- ✅ Test file open with ESC (closes dialog only, UI stays open)
- ✅ Test file open then 'list' command (UI responsive)

**TODO:**
- ⏳ Test file open with Enter and valid filename
- ⏳ Test autosave recovery yes/no dialog
- ⏳ Test save-as dialog
- ⏳ Test renumber dialogs
- ⏳ Test variable editing dialogs
- ⏳ Test nested popups if needed
- ⏳ Test popup positioning on different screen sizes

## Benefits
- ESC will properly close only the dialog
- No more nested event loops
- Follows urwid best practices
- More maintainable code
- Better separation of concerns

## Workaround (Current)
Users can press Enter with empty input to cancel dialogs. Dialog titles updated to reflect this.

## Estimated Effort
4-6 hours including testing

## Priority
Medium - current workaround is functional but not ideal UX
