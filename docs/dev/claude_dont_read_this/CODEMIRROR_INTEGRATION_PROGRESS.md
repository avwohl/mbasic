# CodeMirror 6 Integration Progress

**Status:** IN PROGRESS - Basic integration complete, event handlers and features pending
**Last Updated:** 2025-11-01
**Version:** 1.0.354

## Completed Work

### 1. Statement-Level Breakpoints ✅
**Version:** 1.0.349 (Web UI), 1.0.350 (TK UI)

- ✅ Web UI now supports statement-level breakpoints using AST
- ✅ TK UI now supports statement-level breakpoints using AST
- ✅ Both UIs query `runtime.statement_table` to find statement at cursor position
- ✅ Breakpoints stored as `PC(line_num, stmt_offset)` objects
- ✅ Supports multi-statement lines (e.g., `100 PRINT "A" : PRINT "B"`)

**Files Modified:**
- `src/ui/web/nicegui_backend.py:1368-1460` - Statement-level breakpoint toggle
- `src/ui/tk_ui.py:877-950` - Statement-level breakpoint toggle and clear

### 2. Custom CodeMirror Component ✅
**Version:** 1.0.351

Created complete CodeMirror 6 component with:
- ✅ Python wrapper class (`codemirror_editor.py`)
- ✅ JavaScript implementation (`codemirror_editor.js`)
- ✅ CSS styling (`codemirror_editor.css`)

**Features Implemented:**
- Text get/set operations
- Find highlighting (yellow background)
- Breakpoint markers (red line background)
- Current statement highlighting (green background)
- Line numbers
- Scroll control
- Cursor position tracking
- Read-only mode

**Files Created:**
- `src/ui/web/codemirror_editor.py` - Python wrapper with API methods
- `src/ui/web/codemirror_editor.js` - CodeMirror 6 component implementation
- `src/ui/web/codemirror_editor.css` - Styling for decorations

### 3. Import Map and Dependencies ✅
**Version:** 1.0.352

- ✅ Added ES6 import map for CodeMirror modules
- ✅ Added CodeMirror CSS from CDN
- ✅ Modules loaded: `@codemirror/view`, `@codemirror/state`, `@codemirror/commands`

**File Modified:**
- `src/ui/web/nicegui_backend.py:1114-1128` - Import map in `build_ui()`

### 4. Replace Textarea with CodeMirror ✅
**Version:** 1.0.354
**Status:** COMPLETED

**What was done:**
1. ✅ Added `from src.ui.web.codemirror_editor import CodeMirrorEditor` import
2. ✅ Replaced `ui.textarea()` with `CodeMirrorEditor()` component
3. ✅ Set proper styling (width: 100%, height: 300px, border)
4. ⏳ Event handlers temporarily kept with TODO comment (to be migrated next)

**Files Modified:**
- `src/ui/web/nicegui_backend.py:19` - Added CodeMirrorEditor import
- `src/ui/web/nicegui_backend.py:1161-1185` - Replaced textarea with CodeMirrorEditor

**Note:** Event handlers (keyup, click, blur, paste) are still attached using old pattern - need to migrate to CodeMirror's event system in next step.

## Remaining Work

### 5. Implement Find Highlighting ⏳
**Status:** NOT STARTED

**What needs to be done:**
1. Update find dialog to call `editor.add_find_highlight()`
2. Clear highlights when new search starts
3. Scroll to highlighted text
4. Preserve highlights when dialog closes

**Files to Modify:**
- `src/ui/web/nicegui_backend.py` - Find dialog methods

### 6. Implement Breakpoint Gutter Markers ⏳
**Status:** NOT STARTED

**What needs to be done:**
1. Update `_toggle_breakpoint()` to call `editor.add_breakpoint()`
2. Clear markers when breakpoints removed
3. Update visual markers when breakpoints change
4. Test with statement-level breakpoints

**Files to Modify:**
- `src/ui/web/nicegui_backend.py:1368-1460` - Breakpoint toggle method

### 7. Implement Current Statement Highlighting ⏳
**Status:** NOT STARTED

**What needs to be done:**
1. Add callback during step/next/continue
2. Call `editor.set_current_statement(line_num)` during execution
3. Clear highlight when program finishes
4. Test with step debugging

**Files to Modify:**
- `src/ui/web/nicegui_backend.py` - Debugger step/next/continue methods

### 8. Testing ⏳
**Status:** NOT STARTED

**Test Cases:**
1. Basic editing (type, delete, copy/paste)
2. Auto-numbering still works
3. Find text → yellow highlight appears
4. Close find dialog → highlight stays
5. Toggle breakpoint → red marker appears
6. Step through code → green highlight moves
7. Multiple features at once (find + breakpoint + current line)

## Architecture

### Component Structure
```
CodeMirrorEditor (Python)
  ├── codemirror_editor.py - NiceGUI component wrapper
  ├── codemirror_editor.js - Vue.js component with CodeMirror 6
  └── codemirror_editor.css - Decoration styles
```

### State Management (JavaScript)
- **findHighlightField** - Stores find result decorations
- **breakpointField** - Stores breakpoint line decorations
- **currentStatementField** - Stores current executing line decoration

### API Methods (Python)
```python
editor.set_value(text)           # Set content
editor.get_value()                # Get content
editor.add_find_highlight(...)    # Add yellow highlight
editor.clear_find_highlights()    # Remove all find highlights
editor.add_breakpoint(line_num)   # Add red breakpoint marker
editor.remove_breakpoint(...)     # Remove breakpoint marker
editor.set_current_statement(...) # Set green current line
editor.scroll_to_line(line)       # Scroll to line
```

## Blockers

**None currently** - Foundation is complete and ready for integration

## Timeline Estimate

- **Textarea replacement:** 2-3 hours
- **Find highlighting:** 1 hour
- **Breakpoint markers:** 1 hour
- **Current statement:** 1 hour
- **Testing:** 2-3 hours

**Total:** ~8-10 hours for complete integration

## Related Files

### Modified Files
- `src/ui/web/nicegui_backend.py` - Main web UI backend
- `src/ui/tk_ui.py` - TK UI with statement-level breakpoints

### New Files
- `src/ui/web/codemirror_editor.py` - Component wrapper
- `src/ui/web/codemirror_editor.js` - Component implementation
- `src/ui/web/codemirror_editor.css` - Component styles

### Documentation
- `docs/dev/WEB_UI_TEXT_HIGHLIGHTING_TODO.md` - Original requirements
- `docs/dev/WORK_IN_PROGRESS.md` - Current work tracking

## Next Steps

1. **Test basic CodeMirror functionality** - Create simple test page to verify component works
2. **Replace textarea** - Swap out ui.textarea() for CodeMirrorEditor
3. **Migrate event handlers** - Port all keyup/click/blur/paste logic
4. **Implement highlights** - Add find/breakpoint/current statement decorations
5. **Full testing** - Verify all features work together

## Notes

- CodeMirror component follows NiceGUI custom component pattern
- Uses ES6 modules from CDN (jsDelivr)
- Statement-level breakpoints already working with existing textarea
- Foundation complete - just needs integration and testing
