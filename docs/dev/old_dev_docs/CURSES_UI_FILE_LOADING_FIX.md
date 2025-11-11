# Curses UI File Loading Fix

## Problem

After recent web UI changes to the interpreter and runtime, the curses UI had a critical bug where loading files didn't populate the editor display.

### Symptoms

1. When running `mbasic program.bas --ui curses`, the program would load but the editor would be empty
2. Internally `_load_program_file()` was failing to populate `editor_lines`
3. The program was loaded into `ProgramManager` but not synced to the editor

### Root Cause

The recent refactoring changed how `ProgramManager` stores program data:

**Before (broken code):**
- Code attempted to access `line_obj.original_text`
- Assumed `program.lines` was a dict of `LineNode` objects with `original_text` attribute

**After (current architecture):**
- `ProgramManager.lines` is `Dict[int, str]` mapping line_number → complete line text
- `ProgramManager.line_asts` is `Dict[int, LineNode]` mapping line_number → parsed AST
- `LineNode` no longer has `original_text` (per design: "Never store source_text")

## Solution

### Changes Made

1. **Fixed `_load_program_file()` in `src/ui/curses_ui.py`:**
   - Changed to iterate over `self.program.lines.items()` (which returns `(int, str)` tuples)
   - Extract code portion from full line text using regex
   - Refactored to use new `_sync_program_to_editor()` helper method

2. **Added `_sync_program_to_editor()` method:**
   - Centralizes the logic for syncing `ProgramManager.lines` to `editor_lines`
   - Extracts code part from full line text (strips line number prefix)
   - Updates editor display via `editor.set_edit_text()`

3. **Modified `start()` method:**
   - Added check: if program has lines but editor is empty, call `_sync_program_to_editor()`
   - Handles case where file is loaded via command line before UI starts

### Code Changes

```python
def _sync_program_to_editor(self):
    """Sync program from ProgramManager to editor display."""
    import re
    self.editor_lines = {}
    for line_num, line_text in sorted(self.program.lines.items()):
        # Extract code part (without line number)
        match = re.match(r'^\d+\s+(.*)', line_text)
        if match:
            self.editor_lines[line_num] = match.group(1)
        else:
            self.editor_lines[line_num] = line_text

    # Update editor display
    self.editor.set_edit_text(self._get_editor_text())
```

```python
def start(self):
    """Start the urwid-based curses UI main loop."""
    # Sync any pre-loaded program to the editor
    if self.program.has_lines() and not self.editor_lines:
        self._sync_program_to_editor()

    # ... rest of start() method
```

## Testing

All tests pass:

### Automated Tests
- ✅ `utils/test_curses_comprehensive.py` - 5/5 tests passed
- ✅ `utils/test_curses_file_loading.py` - Direct file loading test
- ✅ `utils/test_curses_cli_file_load.py` - Command-line file loading test
- ✅ `utils/test_curses_manual_check.py` - Editor state verification

### Test Coverage
1. **UI Creation** - Backend instantiation works
2. **Input Handlers** - Keyboard shortcuts functional
3. **Program Parsing** - Editor content parsing works
4. **Run Program** - Program execution works
5. **pexpect Integration** - Full process lifecycle works
6. **File Loading (internal)** - `_load_program_file()` populates editor
7. **File Loading (CLI)** - Command-line file argument works
8. **Editor State** - Editor correctly displays loaded programs

## Related Changes

This fix ensures compatibility with the web UI refactoring that:
- Changed `ProgramManager` to store `lines: Dict[int, str]` instead of objects with `original_text`
- Separated storage of source text (`lines`) from parsed AST (`line_asts`)
- Removed `original_text` from `LineNode` to avoid duplication

## Files Modified

- `src/ui/curses_ui.py` - Fixed file loading, added sync method

## Files Created

- `utils/test_curses_file_loading.py` - Test file loading functionality
- `utils/test_curses_cli_file_load.py` - Test command-line file loading
- `utils/test_curses_manual_check.py` - Manual editor state verification
- `utils/test_curses_visual_check.py` - Visual display verification
- `docs/dev/CURSES_UI_FILE_LOADING_FIX.md` - This document

## Status

**✅ FIXED** - All curses UI file loading functionality restored and tested.
