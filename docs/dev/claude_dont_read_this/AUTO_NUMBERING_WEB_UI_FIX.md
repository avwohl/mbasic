# Auto-Numbering Web UI Implementation

**Date:** 2025-10-30, Updated: 2025-10-31
**Issue:** Auto-numbering in Web UI needs to work on line exit, not just Enter
**Status:** ✅ IMPLEMENTED

## Problem

User reported auto-numbering not working in Web UI:
1. Typed `j=2` and pressed Enter
2. Expected: `10 j=2` to appear
3. Actual: Nothing happened, line stayed as `j=2`
4. Check Syntax complained about missing line number

## Root Cause

The auto-numbering implementation had **two critical bugs**:

### Bug 1: Wrong JavaScript Selector
```javascript
// OLD (BROKEN):
const textarea = document.querySelector('[data-ref="editor"] textarea');

// Problem: .mark('editor') doesn't create data-ref attribute
// Result: querySelector returns null, auto-numbering silently fails
```

### Bug 2: Synchronous Function
The function wasn't `async` and didn't properly wait for the Enter key to complete before inserting the line number.

## Fix Applied

### Fixed JavaScript Access
```javascript
// NEW (WORKING):
const editor = getElement({self.editor.id});
const textarea = editor.$el.querySelector('textarea');

// Uses NiceGUI's getElement() with actual element ID
// Accesses textarea through Vue component's $el
```

### Made Function Async
```python
async def _on_enter_key(self, e):
    # ... calculate line number ...

    await ui.context.client.connected()
    await asyncio.sleep(0.05)  # Wait for Enter to process

    result = await ui.run_javascript(...)
```

## Testing Gap Analysis

### Why Testing Said It Was "Working"

Looking at `docs/dev/WEB_UI_FEATURE_PARITY.md`:

```markdown
- **Auto-numbering** (v1.0.199)
  - Triggered on Enter key
  - JavaScript-based cursor detection
  - Calculates next line number from highest existing line
```

**The problem:** This documents the IMPLEMENTATION, not TESTING.

### What Went Wrong

1. **Implementation != Testing**
   - Code was written in v1.0.199
   - Documentation said "✅ Auto-numbering (v1.0.199)"
   - This was interpreted as "tested and working"
   - Actually meant "code was written"

2. **No Manual Verification**
   - Feature was never manually tested in browser
   - JavaScript errors were silent (querySelector returned null)
   - No automated UI tests caught this

3. **Assumed Working**
   - Because TK UI auto-numbering works
   - Because code existed
   - Because no errors were thrown

## Lessons Learned

### For Future Testing

1. **Distinguish Implementation from Verification**
   ```markdown
   # BAD:
   - ✅ Auto-numbering (v1.0.199)

   # GOOD:
   - ✅ Auto-numbering implemented (v1.0.199)
   - ✅ Auto-numbering tested manually (v1.0.XXX)
   ```

2. **Manual Testing Required for UI Features**
   - Writing code != feature works
   - JavaScript in web UIs must be tested in browser
   - Silent failures (null checks) can hide bugs

3. **Test the User Workflow**
   ```
   Test case: Auto-numbering
   1. Open Web UI
   2. Type: j=2
   3. Press Enter
   4. Expected: Next line shows "10 " (or "20 " if line 10 existed)
   5. Type more code
   6. Verify increments correctly
   ```

4. **Check Error Logs**
   - Even if feature "seems" to work
   - Look for JavaScript console errors
   - Check Python error logs

## Implementation (2025-10-31)

### New Behavior

Auto-numbering now triggers when **leaving a line**, not just on Enter:
- **Enter key**: Numbers current line, creates new line with next number
- **Arrow keys** (up/down): Numbers the line you're leaving
- **Mouse click**: Numbers the line you clicked away from
- **Blur** (focus out): Numbers the line when leaving editor

### Example Workflow

1. Type `k=2` in empty editor
2. Press Down Arrow (or click elsewhere)
3. Line becomes `10 k=2` automatically
4. Continue coding with auto-numbering

### Implementation Details

**New Methods:**
- `async def _check_auto_number()`: Tracks cursor position, auto-numbers when leaving a line
- `async def _auto_number_line(line_index, all_lines)`: Adds line number to a specific line
- `async def _on_enter_key(e)`: Updated to use proper async/await

**New Handlers:**
- `keydown.arrow-down`: Check auto-number on down arrow
- `keydown.arrow-up`: Check auto-number on up arrow
- `click`: Check auto-number after click (with small delay)
- `blur`: Check auto-number and remove blank lines

**Tracking State:**
- `self.last_edited_line_index`: Last line cursor was on
- `self.last_edited_line_text`: Content of that line

## Verification

Test cases for auto-numbering:
1. ✅ Type `j=2`, press Down Arrow → line becomes `10 j=2`
2. ✅ Type `k=3` on next line, click elsewhere → line becomes `20 k=3`
3. ✅ Type code, press Enter → current line numbered, new line gets next number
4. ✅ Auto-numbering respects settings (increment step)
5. ✅ Lines with existing numbers are not renumbered

## Files Changed

- `src/ui/web/nicegui_backend.py`:
  - Added `_check_auto_number()` method
  - Added `_auto_number_line()` method
  - Updated `_on_enter_key()` to async with proper JavaScript
  - Added event handlers for arrow keys, clicks, and blur
  - Added state tracking for last edited line

## Related Issues

- This explains why Web UI feature parity was marked 100% but user found missing features
- Shows need for better testing documentation
- Highlights danger of "silent failures" in JavaScript

## Final Implementation (2025-10-31)

### Root Cause Found
The auto-numbering logic was correct, but the user's settings file had `editor.auto_number_step: 100` instead of the default `10`, causing lines to be numbered 10, 110, 210 instead of 10, 20, 30.

### Changes Made
1. Simplified auto-numbering to use Python-side logic only (no complex JavaScript)
2. Added guard flag to prevent recursive calls when updating editor
3. Track previous snapshot to only auto-number when leaving a line
4. Fixed settings file to use correct step value of 10

### Testing
✅ Type `k=2`, press down arrow → `10 k=2`
✅ Type `j=3`, press down arrow → `20 j=3`
✅ Type `x=4`, press down arrow → `30 x=4`

### Files Changed
- `src/ui/web/nicegui_backend.py` - Simplified auto-numbering implementation
- `~/.mbasic/settings.json` - Fixed step value from 100 to 10
- `docs/dev/AUTO_NUMBERING_WEB_UI_FIX.md` - Updated documentation

## Commit

Version: 1.0.318 (completed 2025-10-31)

## Enter Key Fix (2025-11-01)

### Issue
User reported that pressing Enter after typing code wouldn't allow moving to the next line:
- Type `k=2<Enter>`
- Expected: Cursor on new blank line, ready to type next statement
- Actual: "it cant go to the next line to enter it" - "it probable is then it gets eaten"

### Root Cause
The auto-numbering code in `_check_auto_number()` was removing ALL blank lines when updating the editor:

```python
# BROKEN CODE:
if modified:
    # Remove blank lines when updating
    non_blank_lines = [line for line in lines if line.strip()]
    new_content = '\n'.join(non_blank_lines)
    self.editor.value = new_content
```

This caused:
1. User types `k=2<Enter>` → editor has `k=2\n` (with newline)
2. Auto-numbering runs and numbers the line to `10 k=2`
3. But then removes the blank line: `10 k=2` (no newline!)
4. Cursor stays where it was but there's no next line to type on

### Solution
Stop removing blank lines in the auto-numbering code. Let `_remove_blank_lines()` handle it intelligently - it already preserves the last line (where cursor is after Enter):

```python
# FIXED CODE:
if modified:
    # Don't remove blank lines here - let _remove_blank_lines() handle it
    # This preserves the blank line the user just created with Enter
    new_content = '\n'.join(lines)
    self.editor.value = new_content
```

### Additional Fix
Also updated `_remove_blank_lines()` to preserve the last line even if blank:

```python
# Keep all non-blank lines, but also keep the last line even if blank
# (it's likely where the cursor is after pressing Enter)
for i, line in enumerate(lines):
    if line.strip() or i == len(lines) - 1:
        non_blank_lines.append(line)
```

### Testing
✅ Type `k=2<Enter>` → cursor on new line, ready to type
✅ Type `j=3<Enter>` → cursor on new line
✅ Blank lines in middle of code still get removed
✅ Blank line at end (where cursor is) preserved

### Files Changed
- `src/ui/web/nicegui_backend.py`:
  - Modified `_check_auto_number()` to stop removing blank lines (line 2146-2148)
  - Modified `_remove_blank_lines()` to preserve last line (line 2017-2022)

## Commit

Version: 1.0.323 (completed 2025-11-01)
