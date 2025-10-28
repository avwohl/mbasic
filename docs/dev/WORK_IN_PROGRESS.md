# Work in Progress

## Task: Settings UI Integration

**Started:** 2025-10-28
**Completed:** 2025-10-28
**Status:** Complete

### Goal

Add GUI for managing settings in TK and curses interfaces. Currently settings can only be changed via CLI commands (`SET`, `SHOW SETTINGS`).

### Requirements

**TK UI:**
- Settings menu item in menu bar
- Settings dialog with all available settings
- Organized by category (keywords, variables, editor, etc.)
- Input widgets appropriate for setting type (dropdown for enum, checkbox for bool, etc.)
- Apply/OK/Cancel buttons
- Live validation

**Curses UI:**
- Settings screen accessible via keyboard shortcut
- Navigate settings with arrow keys
- Edit settings with appropriate input method
- Save changes or cancel

### Available Settings

From `src/settings_definitions.py`:
- `keywords.case_style` - Enum: force_lower, force_upper, force_capitalize, first_wins, error, preserve
- `variables.case_policy` - Enum: first_wins, error, prefer_upper, prefer_lower, prefer_mixed
- More settings may exist - need to enumerate all

### Implementation Plan

#### Phase 1: TK UI (Simpler, start here)
1. ✅ Enumerate all available settings from settings system
2. ✅ Design settings dialog layout
3. ✅ Create settings dialog class
4. ✅ Add "Settings..." menu item
5. ✅ Test TK settings UI

#### Phase 2: Curses UI
1. ✅ Design curses settings screen
2. ✅ Implement settings navigation
3. ✅ Test curses settings UI

#### Phase 3: Documentation
1. ✅ Update user documentation
2. ✅ Commit changes

### Summary

Successfully implemented settings UI for both TK and curses interfaces:

**TK UI:**
- Created `src/ui/tk_settings_dialog.py` with full settings dialog
- Tabbed interface organized by category (editor, interpreter, keywords, variables, ui)
- Appropriate widgets for each type (checkbox, spinbox, combobox, entry)
- OK/Cancel/Apply/Reset buttons
- Help text for each setting
- Added "Settings..." menu item to Edit menu

**Curses UI:**
- Created `src/ui/curses_settings_widget.py` with settings widget
- Category-based layout with scrolling
- Checkbox, IntEdit, RadioButton, and Edit widgets for different types
- OK/Cancel/Apply/Reset buttons
- Ctrl+P keyboard shortcut to open settings
- ESC to close

**Testing:**
- Created `tests/manual/test_tk_settings_ui.py` - all tests pass
- Created `tests/manual/test_curses_settings_ui.py` - all tests pass

All 12 available settings are accessible in both UIs.

### Files to Create/Modify

**TK UI:**
- `src/ui/tk_ui.py` - Add menu item and settings dialog
- Possibly `src/ui/tk_settings_dialog.py` - New settings dialog class

**Curses UI:**
- `src/ui/curses_ui.py` - Add settings screen/dialog

### Next Steps

Starting with enumerating available settings...
