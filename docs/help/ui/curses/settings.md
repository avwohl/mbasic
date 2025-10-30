---
title: Curses Settings Widget
type: guide
ui: curses
description: How to configure settings in the curses terminal UI
keywords: [settings, configuration, curses, terminal, preferences]
---

# Curses Settings Widget

The curses UI provides an interactive settings widget for viewing and modifying MBASIC settings.

## Opening the Settings Widget

**Keyboard shortcut:** `Ctrl+,`

Or navigate to the settings menu item if available in your version.

## Settings Widget Interface

The settings widget displays:

```
┌─ Settings ──────────────────────────────────────┐
│                                                  │
│  EDITOR                                          │
│  ────────────────────────────────────────────   │
│  Auto Number:                                    │
│    [✓]                                           │
│  Auto Number Step:                               │
│    [10    ]                                      │
│  Tab Size:                                       │
│    [4     ]                                      │
│  Show Line Numbers:                              │
│    [✓]                                           │
│                                                  │
│  KEYWORDS                                        │
│  ────────────────────────────────────────────   │
│  Case Style:                                     │
│    ( ) force_lower                               │
│    (•) force_upper                               │
│    ( ) force_capitalize                          │
│                                                  │
│  [  OK  ] [ Cancel ] [ Apply ] [  Reset  ]      │
└──────────────────────────────────────────────────┘
```

## Navigation

### Keyboard Controls

| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate between settings |
| `Tab` | Move to next widget |
| `Shift+Tab` | Move to previous widget |
| `Space` | Toggle checkbox / select radio button |
| `Enter` | Activate focused button |
| `ESC` | Close settings (cancel) |

### Mouse Controls

If mouse support is enabled:
- Click on checkboxes to toggle
- Click on radio buttons to select
- Click on input fields to edit
- Click buttons to activate

## Setting Types

### Boolean Settings (Checkboxes)

Example: `Auto Number`

- `[ ]` - Unchecked (false)
- `[✓]` - Checked (true)

**How to change:**
1. Navigate to checkbox with arrow keys
2. Press `Space` to toggle

### Integer Settings (Input Fields)

Example: `Auto Number Step`

**How to change:**
1. Navigate to input field
2. Press `Enter` or start typing
3. Enter new number
4. Press `Enter` to confirm

**Validation:**
- Only numeric values accepted
- Must be within valid range (displayed in help text)
- Invalid values show error and revert

### Enum Settings (Radio Buttons)

Example: `Case Style`

```
( ) force_lower
(•) force_upper
( ) force_capitalize
```

**How to change:**
1. Navigate to radio button group
2. Use arrow keys to move between options
3. Press `Space` to select

Only one option can be selected at a time.

## Button Actions

### OK
- Apply all changes
- Save to disk
- Close settings widget

### Cancel
- Discard all changes
- Restore previous values
- Close settings widget

### Apply
- Apply all changes
- Save to disk
- **Keep widget open** (for further editing)

### Reset
- Reset all settings to default values
- Does not save automatically
- Click OK or Apply to confirm reset

## Settings Categories

Settings are organized into categories:

### EDITOR
- Auto Number (checkbox)
- Auto Number Step (integer, 1-1000)
- Tab Size (integer, 1-16)
- Show Line Numbers (checkbox)

### KEYWORDS
- Case Style (radio buttons)
  - force_lower
  - force_upper
  - force_capitalize

### VARIABLES
- Case Conflict (radio buttons)
  - first_wins
  - error
  - prefer_upper
  - prefer_lower
  - prefer_mixed
- Show Types In Window (checkbox)

### INTERPRETER
- Strict Mode (checkbox)
- Max Execution Time (integer, 1-3600 seconds)
- Debug Mode (checkbox)

### UI
- Theme (radio buttons)
  - default
  - dark
  - light
  - classic
- Font Size (integer, 8-32 points)

## Common Tasks

### Change Auto-Numbering Increment

1. Press `Ctrl+,` to open settings
2. Navigate to EDITOR section
3. Find "Auto Number Step" field
4. Enter new value (e.g., 100)
5. Click Apply or OK

**Result:** New lines will increment by 100 instead of 10

### Force Uppercase Keywords

1. Open settings (`Ctrl+,`)
2. Navigate to KEYWORDS section
3. Select "force_upper" radio button
4. Click Apply

**Result:** When you LIST your program, keywords show in UPPERCASE

### Enable Error Checking for Variable Typos

1. Open settings
2. Navigate to VARIABLES section
3. Select "error" under Case Conflict
4. Click Apply

**Result:** Mistyped variable names trigger errors

### Switch to Dark Theme

1. Open settings
2. Navigate to UI section
3. Select "dark" theme
4. Click Apply

**Result:** UI switches to dark color scheme

## Tips

1. **Use Apply for experiments** - Click Apply to test settings without closing the widget. If you don't like the result, change it back and Apply again.

2. **Cancel to undo** - If you make unwanted changes, press ESC or click Cancel to revert.

3. **Reset when confused** - If settings get misconfigured, use Reset to return to safe defaults.

4. **Check help text** - Each setting shows brief help text below the input widget.

5. **Scroll for more** - If you have many settings, use arrow keys to scroll through the list.

## Settings Persistence

Settings changed via the widget are saved to:
- Linux/Mac: `~/.mbasic/settings.json`
- Windows: `%APPDATA%\mbasic\settings.json`

Changes persist across sessions automatically.

## Troubleshooting

### Settings widget won't open
- Check keyboard shortcut in your keybindings
- Try from command line: add `--settings` flag (if supported)

### Changes don't take effect
- Make sure you clicked Apply or OK (not Cancel)
- Check that value is within valid range
- Restart MBASIC if needed

### Invalid value error
- Check the valid range shown in help text
- For enums, only predefined choices are allowed
- Booleans must be toggled via checkbox

### Settings reset on restart
- Check file permissions on `~/.mbasic/settings.json`
- Make sure disk is not full
- Look for error messages when exiting

## See Also

- [Settings System Overview](../../common/settings.md)
- [Curses Keyboard Commands](keyboard-commands.md)
- [Curses Getting Started](getting-started.md)
- [Curses Index](index.md)

[← Back to Curses Help](index.md)
