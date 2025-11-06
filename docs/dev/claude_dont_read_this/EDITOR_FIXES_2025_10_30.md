# Editor Fixes - 2025-10-30

## Auto-Numbering Fix

### Problem
Auto-numbering wasn't working when typing `k=2<Enter>` in the editor.

### Root Cause
1. The function was `async` which caused timing issues with NiceGUI event handlers
2. The JavaScript wasn't properly preventing default Enter behavior
3. The event binding might not have been working correctly

### Fix Applied
1. Changed `_on_enter_key` from `async def` to regular `def`
2. Added `event.preventDefault()` in the JavaScript
3. Added debug logging to track execution
4. Used synchronous `ui.run_javascript()` instead of `await ui.run_javascript()`

### Testing
When you press Enter in the editor, check `/tmp/debug.log` for:
```
DEBUG: _on_enter_key called
DEBUG: Auto-numbering to line 20
```

If you see these messages but auto-numbering still doesn't work, it's a JavaScript/browser issue.

### Location
- `src/ui/web/nicegui_backend.py:220` - Event binding
- `src/ui/web/nicegui_backend.py:1806-1861` - Auto-numbering handler

## Blank Lines Fix

### Problem
Editor allowed blank lines to be entered/pasted.

### Fix Applied
1. Added `blur` event handler that removes blank lines when editor loses focus
2. Filters out any lines that are empty or contain only whitespace
3. Only updates editor if blank lines were found (avoids unnecessary DOM updates)

### How It Works
- When you click outside the editor (blur event)
- Or when you paste content and then click elsewhere
- The handler automatically removes all blank lines

### Location
- `src/ui/web/nicegui_backend.py:223` - Event binding  
- `src/ui/web/nicegui_backend.py:1785-1804` - Blank line removal handler

## Settings
Auto-numbering is **enabled by default** in `src/settings_definitions.py`:
- `editor.auto_number`: `True` (default)
- `editor.auto_number_step`: `10` (default)

Users can disable it via Settings menu if desired.
