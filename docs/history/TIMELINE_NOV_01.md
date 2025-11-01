# MBASIC Development Timeline - November 1, 2025

## Session Overview
Major improvements to breakpoint and statement-level debugging in the web UI.

---

## Version 1.0.362 - Fix Breakpoints: Preserve Across RUN, Add reset_for_run()

**Problem:** Breakpoints were not working in web UI
- Visual marker (red line) wasn't showing - CSS not loaded properly
- Breakpoints lost when clicking RUN - new Runtime created each time
- First step after breakpoint jumped to wrong line (line 20 instead of continuing)

**Root Causes:**
1. CSS file not being served by NiceGUI component system
2. Runtime object recreated on RUN, discarding old one with breakpoints (violates "no copy" principle)
3. When breakpoint hit during RUN, `self.running` set to False, so next STEP thought program wasn't running

**Solutions:**
1. **CSS Loading:** Inject CSS as `<style>` tag in JavaScript instead of external file
2. **Runtime Reuse:** Added `Runtime.reset_for_run()` method that:
   - Resets execution state (variables, PC, arrays, files, etc.) like CLEAR
   - Rebuilds statement table from new program
   - **Preserves breakpoints** - not cleared
   - Now follows BASIC semantics: RUN = CLEAR + GOTO first line, but keeps breakpoints
3. **Step After Breakpoint:** Changed condition from `if not self.running` to `if not self.running and not self.paused`

**Key Design Improvement:**
Following "no copy" rule - Runtime object now **reused** instead of recreated:
- Before: Create new Runtime → try to copy breakpoints → fail
- After: Keep same Runtime → call `reset_for_run()` → breakpoints preserved automatically

**Files Modified:**
- `src/runtime.py` - Added `reset_for_run()` method
- `src/ui/web/codemirror5_editor.js` - Inline CSS injection
- `src/ui/web/nicegui_backend.py` - Reuse Runtime, fix step conditions
- `src/interpreter.py` - Already had correct breakpoint logic

---

## Version 1.0.363 - Implement Statement-Level Highlighting

**Problem:** Step statement works but doesn't highlight each statement as it steps
- Highlighted whole line instead of individual statements
- Strings like `X0$=" IS "` had incorrect highlight end (stopped after 'S')
- Breakpoint hit during RUN didn't show statement highlight

**Solutions:**
1. **Statement-Level Highlighting:** Changed from line classes to text markers
   - Uses `markText()` with char_start/char_end positions
   - Green background with green underline for current statement
   - Works for multi-statement lines like `100 A=1 : B=2 : C=3`

2. **String Token char_end Fix:** Smart calculation using next statement's position
   ```python
   # If there's a next statement: use max(char_end, next_start - 1)
   # If at end of line: use line length
   ```
   - Handles string tokens where char_end doesn't include closing quote
   - Works for both middle and end-of-line statements

3. **Breakpoint Highlighting:** Added statement highlighting when hitting breakpoint
   - Pass char_start/char_end to `set_current_statement()` 
   - Works in both RUN mode (_execute_tick) and STEP mode (_handle_step_result)

4. **Continue After Step:** Fixed `running` flag being incorrectly set to False
   - In _execute_tick, when paused/at_breakpoint, keep `running = True`
   - Allows Continue to work after stepping

**Files Modified:**
- `src/interpreter.py` - Added `current_statement_char_end` property with smart logic
- `src/ui/web/codemirror5_editor.js` - Text markers instead of line classes
- `src/ui/web/codemirror5_editor.py` - Accept char_start/char_end parameters
- `src/ui/web/nicegui_backend.py` - Pass char positions, fix running flag

---

## Version 1.0.364 - Statement-Level Breakpoint Highlighting

**Problem:** Breakpoint highlighting showed whole line, not specific statement
- Can't tell which statement in multi-statement line has breakpoint
- Empty statements (`::`) are legal but invisible
- Breakpoint positions not available until program runs

**Solutions:**
1. **Statement-Level Breakpoint Markers:**
   - Changed from line background to text markers
   - Red background with red underline
   - Includes preceding space or colon for visibility (so you can see `:: B=2` breakpoint)
   - Uses same char_end calculation as current statement

2. **Statement Table Population on Load:**
   - Call `runtime.reset_for_run()` in `_save_editor_to_program()`
   - Statement table now populated when program edited, not just when run
   - Allows breakpoint character positions to be calculated before running

3. **Data Duplication Issue:**
   - Discovered: ProgramManager stores lines/ASTs, Runtime copies them
   - Violates "no copy" principle but functional for now
   - **Benefit:** Preserves lines with syntax errors for editing
     - If stored only ASTs, error lines would disappear!
     - Current design keeps raw text even when parsing fails
   - Created `RUNTIME_PROGRAM_DATA_DUPLICATION_TODO.md` documenting:
     - Problem and current workaround
     - Proper solution (Runtime references ProgramManager directly)
     - Must preserve syntax error line editing behavior

**Files Modified:**
- `src/ui/web/codemirror5_editor.js` - Text markers with char adjustment for preceding space/colon
- `src/ui/web/codemirror5_editor.py` - Accept char_start/char_end for breakpoints
- `src/ui/web/nicegui_backend.py` - Get char positions from statement table, populate on load
- `docs/dev/RUNTIME_PROGRAM_DATA_DUPLICATION_TODO.md` - Architecture TODO

---

## Overall Impact

### Debugging Features Now Working:
✅ Visual breakpoint markers (red highlight on specific statement)
✅ Breakpoints persist across RUN commands
✅ Step statement shows exactly which statement is executing (green highlight)
✅ Step line works correctly
✅ Continue after breakpoint/step works
✅ Breakpoints work on multi-statement lines
✅ String token highlighting works correctly

### Architecture Improvements:
✅ Runtime reused instead of recreated (follows "no copy" principle)
✅ Statement table available before running (for breakpoint display)
✅ Documented data duplication issue with TODO for proper fix

### User Experience:
- Can set breakpoints and see exactly which statement will break
- Step through multi-statement lines and see each statement highlighted
- Lines with syntax errors preserved for editing
- Visual feedback matches TK UI behavior

---

## Technical Notes

### PC-Based Breakpoints
Breakpoints stored as PC objects (line_num, stmt_offset) not just line numbers:
- Allows statement-level breakpoints like `PC(100, 2)` for 3rd statement on line 100
- Currently UI only sets line-level (stmt_offset=0) but infrastructure supports statement-level

### Empty Statements
Parser handles `::` (empty statements) by skipping them - legal in BASIC.
Including preceding colon in breakpoint highlight makes it visible.

### Character Position Calculation
Key insight: Use next statement's char_start - 1 for char_end calculation.
Works because:
- Colon separator is at next_start - 1
- Handles incorrect token char_end (especially strings)
- Falls back to line length at end of line

---

## Version 1.0.366 - Convert All Files to Unix LF Line Endings

**Problem:** Files in repository had mixed line endings (CRLF, CR, LF)

**Solution:**
- Converted 180 BASIC files in `basic/` to LF (178 CRLF→LF, 2 CR→LF)
- Converted 35 docs files to LF
- Skipped .mac files (need CRLF for CP/M M80 assembler)
- Created `convert_to_cpm.py` utility for CP/M format conversion

**Documentation:**
- `docs/user/FILE_FORMAT_COMPATIBILITY.md` - User guide on line endings and CP/M compatibility
- Updated utility scripts index

**Files Modified:**
- 215 files converted to LF
- New utilities: `convert_eol_to_lf.py`, `convert_docs_eol_to_lf.py`, `convert_to_cpm.py`

---

## Version 1.0.367-1.0.369 - Fix RUN Command Semantics

**Problem:** RUN command had incorrect checks preventing it from working properly
- Web UI checked `if self.running: return` - prevented RUN at breakpoints
- Web UI rejected empty programs - real MBASIC allows RUN on empty (just CLEAR)
- Misunderstanding: RUN is NOT special, it's just `RUN = CLEAR + GOTO first line`

**Solution:**
- Removed `if self.running` check - RUN always works
- Removed empty program error - RUN on empty is allowed
- Added timer cancellation before RUN
- Clarified: `self.running` is for DISPLAY only (spinner), NOT control logic

**Documentation Created:**
- `RUN_COMMAND_SEMANTICS_TODO.md` - Documents RUN semantics and `self.running` flag issues
- `MOVE_STATEMENTS_TO_INTERPRETER_TODO.md` - Plan to move FILES/LOAD/SAVE to interpreter

**Files Modified:**
- `src/ui/web/nicegui_backend.py` - _menu_run() fixed

---

## Version 1.0.370 - FileIO Module Architecture for Sandboxed Web UI

**Problem:** FILES statement had security issue in web UI
- `cmd_files()` used `glob.glob()` - direct server filesystem access
- Web users could list server directories: `FILES "../../etc/passwd"`
- No sandboxing - web UI needs browser-only file access

**Solution:** FileIO module architecture
1. **Created `src/file_io.py`:**
   - `FileIO` abstract interface
   - `RealFileIO` - Direct filesystem (TK/Curses/CLI)
   - `SandboxedFileIO` - Browser localStorage (Web UI)

2. **Updated Interpreter:**
   - Added `file_io` parameter to `__init__()`
   - Defaults to `RealFileIO()` if `None` passed
   - `execute_files()` uses `self.file_io.list_files()` - no UI delegation

3. **Updated Web UI:**
   - Creates `SandboxedFileIO(self)` and passes to Interpreter
   - Removed insecure `cmd_files()` method
   - Applied to both RUN mode and immediate mode

**Key Design:**
- Interpreter takes optional `file_io` parameter
- `None` → creates `RealFileIO` (local filesystem)
- Web UI passes `SandboxedFileIO` (browser localStorage)
- It's a **sandbox issue** - web UI is responsible for sandboxing, not interpreter

**Security Benefits:**
- ✅ Web UI sandboxed - no server filesystem access
- ✅ No path traversal attacks possible
- ✅ Files scoped per-user session (localStorage)
- ✅ Local UIs unchanged - real filesystem on user's machine

**FILES Statement Now:**
- Works in web UI (shows localStorage files)
- Works in local UIs (shows real files)
- 100% in interpreter - no UI delegation
- Sandboxed automatically based on FileIO passed

**Files Modified:**
- `src/file_io.py` - NEW (318 lines)
- `src/interpreter.py` - Added file_io parameter, updated execute_files()
- `src/ui/web/nicegui_backend.py` - Pass SandboxedFileIO, removed cmd_files()

**Documentation:**
- Moved `FILEIO_MODULE_ARCHITECTURE_TODO.md` → `FILEIO_MODULE_ARCHITECTURE_DONE.md`
- Updated `MOVE_STATEMENTS_TO_INTERPRETER_TODO.md` with FILES completion
