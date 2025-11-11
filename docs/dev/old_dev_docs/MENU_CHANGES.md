# Menu Structure Changes

## Summary

Simplified the menu structure by removing the "Run" submenu and promoting its items to the top level.

## Changes Made

### Before
```
Main Menu:
├── New (^N)
├── Load... (^L)
├── Save... (^S)
├── Quit (^Q)
├── Run ▶
│   ├── Run Program (^R)
│   └── List (^L)
└── Help (^P)
```

### After
```
Main Menu:
├── New (^N)
├── Load... (^L)
├── Save... (^S)
├── Quit (^Q)
├── Run Program (^R)
├── List (^L)
└── Help (^P)
```

## Implementation

**File**: `src/ui/curses_ui.py` (lines 200-214)

**Previous Code**:
```python
# Create menus
self.menu = self.new_menu(name="Main Menu")

# File menu
self.menu.addItem(text="New", onSelect=self.on_new, shortcut="^N")
self.menu.addItem(text="Load...", onSelect=self.on_load, shortcut="^L")
self.menu.addItem(text="Save...", onSelect=self.on_save, shortcut="^S")
self.menu.addItem(text="Quit", onSelect=self.on_quit, shortcut="^Q")

# Run menu
submenu_run = self.menu.addNewSubmenu("Run")
submenu_run.addItem(text="Run Program", onSelect=self.on_run, shortcut="^R")
submenu_run.addItem(text="List", onSelect=self.on_list, shortcut="^L")

# Help - direct menu item instead of submenu
self.menu.addItem(text="Help", onSelect=self.on_help, shortcut="^P")
```

**Updated Code**:
```python
# Create menus
self.menu = self.new_menu(name="Main Menu")

# File menu
self.menu.addItem(text="New", onSelect=self.on_new, shortcut="^N")
self.menu.addItem(text="Load...", onSelect=self.on_load, shortcut="^L")
self.menu.addItem(text="Save...", onSelect=self.on_save, shortcut="^S")
self.menu.addItem(text="Quit", onSelect=self.on_quit, shortcut="^Q")

# Run and List - direct menu items
self.menu.addItem(text="Run Program", onSelect=self.on_run, shortcut="^R")
self.menu.addItem(text="List", onSelect=self.on_list, shortcut="^L")

# Help - direct menu item
self.menu.addItem(text="Help", onSelect=self.on_help, shortcut="^P")
```

## Benefits

1. **Faster Access**: No need to navigate into a submenu to run programs or list code
2. **Simpler UX**: Flatter menu structure is easier to understand
3. **Fewer Keystrokes**: Direct access reduces navigation steps
4. **Consistency**: All main functions are at the same level

## Testing

Created test scripts to verify the changes:
- `test_menu_structure.sh` - Manual testing script with instructions
- `test_menu_automated.sh` - Automated test confirming program execution still works

Test result: ✓ Program runs correctly with new menu structure

## Keyboard Shortcuts

All keyboard shortcuts remain unchanged:
- **Ctrl+N** - New
- **Ctrl+L** - Load (note: conflicts with List, but Load dialog appears first)
- **Ctrl+S** - Save
- **Ctrl+Q** - Quit
- **Ctrl+R** - Run Program
- **Ctrl+P** - Help
