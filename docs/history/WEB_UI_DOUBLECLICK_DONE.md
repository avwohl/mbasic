# Web UI File Browser Double-Click Support - RESOLVED

## Issue
Double-clicking files in the web UI file browser doesn't open them. Users must select file then click Open button.

## Root Cause
NiceGUI's `.on('dblclick')` event doesn't fire on `ui.row()` elements. Multiple attempts failed:

### Attempted Solutions (All Failed)
1. **v1.0.331**: Lambda with async function - `lambda p=file_path: self._handle_file_doubleclick(p)`
2. **v1.0.332**: Factory function returning async closure - `make_dblclick_handler(file_path)`
3. **v1.0.333**: `functools.partial` binding - `partial(self._handle_file_doubleclick, file_path)`
4. **v1.0.333**: Factory with explicit select+open and debug logging

None of these produce any output in stderr, meaning the event handler isn't being called at all.

## Why It Fails
- NiceGUI `.on('dblclick')` doesn't work on regular `ui.row()` elements
- Only specific components support it (e.g., `table.on('rowDblclick')` works - see line 299)
- The event simply never fires

## Solution Implemented

**Switched to AG Grid** (suggested by user via Google AI)

### v1.0.341-1.0.343: Replaced custom row-based file browser with `ui.aggrid`

Key changes:
1. **Created grid in `__init__()` instead of `show()`** - Fixed AG Grid zero width issue
2. **Used `cellDoubleClicked` event** - Works natively with AG Grid
3. **Proper grid configuration**:
   - `rowSelection: {'mode': 'singleRow'}` (new AG Grid API)
   - `domLayout: 'autoHeight'` for flexible content
   - `html_columns=[0]` for emoji/formatting in filename column
4. **Fixed layout** (v1.0.343):
   - Removed confusing "Upload" button
   - Wrapped grid in fixed-height scrollable container (400px)
   - Fixed action buttons at bottom (outside scroll area)

## Key Technical Insight

AG Grid must have dimensions when initialized. Creating it inside a hidden dialog causes zero width, preventing column sizing. Creating the grid in `__init__()` (when app starts) instead of `show()` (when dialog opens) gave it proper dimensions. This matches the NiceGUI example pattern.

## Related Code
- `src/ui/web/nicegui_backend.py:OpenFileDialog` - AG Grid file browser implementation
- Grid creation: Lines ~388-400
- Event handler: `_handle_double_click()` method
- Layout fix: Lines ~403-410 (scrollable container + fixed buttons)

## Status
✅ **RESOLVED** - v1.0.343
- Double-click opens files
- Navigation works (double-click directories)
- Clean UI with proper button placement
- No more confusing Upload button

## Date Created
2025-11-01

## Date Completed
2025-11-01 (v1.0.343)
