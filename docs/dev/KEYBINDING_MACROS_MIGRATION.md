# Keybinding Macros Migration Status

## Overview
Migrated hardcoded Ctrl+ references in documentation to use {{kbd:action:ui}} macro system for maintainability and accuracy.

## Progress
- **Total Ctrl+ references found:** 230
- **Automated replacements:** 171 (74%)
- **Remaining for manual review:** 70 (26%) - split into 3 categories below (59 + 6 + 5)

## Completed

### Automated Replacements (171 total)
1. **UI-specific files** (142 replacements):
   - `docs/help/ui/tk/` - TK GUI keybindings
   - `docs/help/ui/curses/` - Curses terminal keybindings
   - `docs/help/ui/web/` - Web interface keybindings
   - `docs/help/ui/cli/` - CLI keybindings

2. **Common UI-specific files** (29 replacements):
   - `docs/help/common/ui/tk/` - TK documentation in common area
   - `docs/help/common/ui/curses/` - Curses documentation in common area
   - `docs/help/common/ui/cli/` - CLI documentation in common area

### Documentation Fixes
- Fixed `docs/help/ui/tk/feature-reference.md`: Removed incorrect shortcuts for Continue (Ctrl+G), Step Statement (Ctrl+T), Delete Lines (Ctrl+D) - these don't actually exist in TK
- Fixed {{kbd:cut:tk}} typo (should have been "Stop")

## Remaining Work (70 references)

### Category 1: Cross-UI Documentation (59 refs)
Files that describe features across multiple UIs - need UI-aware text or conditional macros:
- `docs/help/mbasic/getting-started.md` (7) - Getting started guide mentions shortcuts generically
- `docs/help/common/debugging.md` (8) - Debugging guide covers all UIs
- `docs/help/mbasic/features.md` (4) - Feature overview across UIs
- `docs/help/common/shortcuts.md` (1) - Shortcut reference page
- And 39 others in various common/ and mbasic/ files

**Recommendation:** These may need:
1. UI-specific versions with appropriate macros
2. Conditional text based on current UI
3. Generic descriptions without specific shortcuts

### Category 2: Non-Existent Shortcuts in UI Docs (6 refs)
Documentation claims shortcuts exist that aren't in keybindings:
- `docs/help/ui/curses/feature-reference.md` (8):
  - Ctrl+E (Renumber) - not in curses_keybindings.json
  - Ctrl+W (Variables) - not in curses_keybindings.json
  - Ctrl+U (Menu) - actually ESC
  - Ctrl+D (Delete) - not in curses_keybindings.json
  - Ctrl+I (Smart Insert) - not in curses_keybindings.json
  - Ctrl+, (Settings) - not in curses_keybindings.json

**Recommendation:** Either remove these references or add missing keybindings to JSON files if they should exist.

### Category 3: Browser/Terminal Native Shortcuts (5 refs)
References to native browser or terminal shortcuts, not MBASIC features:
- `docs/help/ui/web/web-interface.md` (5):
  - Ctrl+V, Ctrl+A, Ctrl+C - browser clipboard operations
- `docs/help/common/ui/cli/index.md` (2):
  - Ctrl+D, Ctrl+Z - Unix/Windows terminal exit shortcuts

**Recommendation:** Leave as-is (these are describing platform behavior, not MBASIC keybindings)

## Tools Created
- `utils/fix_help_keybindings.py` - Automated replacement script
  - Maps Ctrl+ combinations to action names for each UI
  - Processes UI-specific directories
  - Handles common/ui/{ui}/ directories

## Keybinding Files
- `src/ui/tk_keybindings.json` - TK GUI keybindings
- `src/ui/curses_keybindings.json` - Curses terminal keybindings
- `src/ui/web_keybindings.json` - Web interface keybindings (created)
- `src/ui/cli_keybindings.json` - CLI keybindings (created)

## Macro System
Extended `src/ui/help_macros.py` to support:
- `{{kbd:action}}` - Current UI's keybinding
- `{{kbd:action:ui}}` - Specific UI's keybinding (for cross-UI comparisons)

## Next Steps
1. Review Category 1 files - decide on approach for cross-UI documentation
2. Fix Category 2 files - remove incorrect shortcuts or add missing keybindings
3. Category 3 can stay as-is (platform-specific, not MBASIC)

## Testing
All macro tests passing: `python3 tests/regression/help/test_help_macros.py`
