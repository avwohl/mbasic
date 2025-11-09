# Keybinding Systems Architecture

## Overview

MBASIC uses multiple keybinding systems that serve different purposes. This document clarifies the relationships between these systems.

## The Three Keybinding Systems

### 1. JSON-Based Runtime System (Primary)

**Files:**
- `src/ui/curses_keybindings.json` - Curses UI keybindings
- `src/ui/tk_keybindings.json` - Tk UI keybindings
- `src/ui/web_keybindings.json` - Web UI keybindings
- `src/ui/cli_keybindings.json` - CLI keybindings

**Loader:** `src/ui/keybinding_loader.py`

**Purpose:** Runtime event handling - binding keys to actions during program execution

**Used by:** Main UI event loops

**Example:**
```json
{
  "editor": {
    "help": {
      "keys": ["Ctrl+H"],
      "primary": "Ctrl+H",
      "description": "Open help browser"
    }
  }
}
```

### 2. Python Constants System (Curses UI)

**File:** `src/ui/keybindings.py`

**Purpose:** Provides Python constants for keybindings, loaded from `curses_keybindings.json`

**Used by:**
- Curses UI components (`curses_ui.py`, `interactive_menu.py`, `curses_settings_widget.py`)
- Status bar display
- Help system documentation

**Key features:**
- Loads from JSON at import time
- Provides constants like `HELP_KEY`, `RUN_KEY`, `SAVE_KEY`
- Includes conversion functions: `key_to_char()`, `key_to_display()`
- Validates keybindings on load

**Example:**
```python
from src.ui.keybindings import HELP_KEY, RUN_KEY, key_to_display
# HELP_KEY = 'ctrl f' (urwid format)
# key_to_display(HELP_KEY) = '^F'
```

**Note:** This system also includes **dialog-specific keys** that are NOT in the JSON:
- `SETTINGS_APPLY_KEY = 'ctrl a'` - Apply in settings dialog
- `SETTINGS_RESET_KEY = 'ctrl r'` - Reset in settings dialog
- `DIALOG_YES_KEY = 'y'` - Confirm in dialogs
- `DIALOG_NO_KEY = 'n'` - Cancel in dialogs
- `VARS_SORT_MODE_KEY = 's'` - Sort mode in variables window
- `VARS_SORT_DIR_KEY = 'd'` - Sort direction in variables window
- `VARS_EDIT_KEY = 'e'` - Edit variable in variables window
- `VARS_FILTER_KEY = 'f'` - Filter variables
- `VARS_CLEAR_KEY = 'c'` - Clear filter

These are intentionally hardcoded because they're context-specific and shown in dialog prompts/footers.

### 3. Help System Macro Expansion

**File:** `src/ui/help_macros.py`

**Purpose:** Expands `{{kbd:action:ui}}` macros in help documentation

**Uses:** Same JSON files as #1, but for documentation generation rather than runtime binding

**Example:**
```markdown
Press {{kbd:run:curses}} to run the program.
→ Expands to: Press ^R to run the program.
```

**Comment in code:**
> "This loads the same keybinding JSON files as keybinding_loader.py, but for a different purpose: macro expansion in help content"

## Special Cases

### Help Widget Navigation

**File:** `src/ui/help_widget.py`

**Keys:** Hardcoded in `keypress()` method

**Why:** Help navigation keys are intentionally hardcoded for these reasons:
1. Help system needs to work even if keybindings are misconfigured
2. Help navigation is meta-level (navigating help about keys)
3. Standard navigation conventions (arrow keys, Enter, ESC, Tab)

**Keys used:**
- Arrow keys (↑↓←→) - Scroll and navigate
- `Enter` - Follow link
- `ESC`, `Q` - Close help
- `Tab` - Next link
- `/` - Search
- `U` - Back

## Relationship Between Systems

```
JSON Files (*.json)
    ↓
    ├─→ keybinding_loader.py → Runtime event handling
    ├─→ keybindings.py → Python constants for Curses UI
    └─→ help_macros.py → Documentation macro expansion

Hardcoded Keys
    ├─→ keybindings.py (dialog-specific) → Context menus, dialogs
    └─→ help_widget.py → Help navigation
```

## Which System is Authoritative?

**For main editor/UI actions:** JSON files are authoritative
- All UIs should load from their respective JSON files
- JSON is the single source of truth for user-facing keybindings

**For dialog/widget-specific actions:** Python constants in `keybindings.py` are authoritative
- These are implementation details, not user-configurable
- Shown in dialog footers/prompts, not in main help

**For help navigation:** `help_widget.py` is authoritative
- Intentionally independent of JSON system
- Uses standard conventions

## Future Considerations

The current system has evolved organically and could be simplified:

1. **Potential unification:** Dialog-specific keys could potentially be added to JSON for completeness
2. **Deprecation candidate:** The Python constants system (`keybindings.py`) could potentially be replaced by direct JSON loading in all UIs (like Tk and Web already do)
3. **Documentation:** Help widget navigation could be documented in JSON even if implementation stays hardcoded

However, the current separation has benefits:
- Clear distinction between user-configurable (JSON) and implementation-specific (hardcoded)
- Help system independence from configuration
- Dialog keys are shown in context where they're used
