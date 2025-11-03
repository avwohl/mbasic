---
title: Tk Settings Dialog
type: guide
ui: tk
description: How to configure settings in the Tk desktop GUI
keywords: [settings, configuration, tkinter, desktop, preferences, dialog]
---

# Tk Settings Dialog

The Tk (Tkinter) desktop GUI provides the most comprehensive settings dialog with tabbed interface for all MBASIC settings. It offers more configuration options than the Web UI, including keyword display, variable case handling, interpreter settings, and UI themes.

## Opening the Settings Dialog

**Methods:**
1. Menu: **File → Settings**
2. Keyboard shortcut: (check your system's menu)

## Settings Dialog Interface

The settings dialog is a multi-tabbed window:

```
┌─ MBASIC Settings ──────────────────────┐
│  ┌──────────────────────────────────┐  │
│  │ Editor │ Interpreter │ Keywords  │  │
│  │  ...   │             │           │  │
│  ├──────────────────────────────────┤  │
│  │                                   │  │
│  │  Auto Number:              [✓]   │  │
│  │                                   │  │
│  │  Auto Number Step:  [10      ]   │  │
│  │                                   │  │
│  │  Tab Size:          [4       ]   │  │
│  │                                   │  │
│  │  Show Line Numbers:        [✓]   │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
│                                          │
│  [ Reset to Defaults ]  [ Apply ]       │
│                         [ Cancel ] [OK] │
└──────────────────────────────────────────┘
```

## Tabs

### Editor Tab

Controls editor behavior:

| Setting | Type | Range | Description |
|---------|------|-------|-------------|
| Auto Number | Checkbox | - | Enable/disable auto-numbering |
| Auto Number Step | Spinbox | 1-1000 | Line number increment |
| Tab Size | Spinbox | 1-16 | Tab width in spaces |
| Show Line Numbers | Checkbox | - | Show line numbers in gutter |

### Keywords Tab

Controls keyword display:

| Setting | Type | Choices | Description |
|---------|------|---------|-------------|
| Case Style | Dropdown | force_lower, force_upper, force_capitalize | How keywords are displayed |

**Examples:**
- `force_lower`: `print "hello"`
- `force_upper`: `PRINT "hello"`
- `force_capitalize`: `Print "hello"`

### Variables Tab

Controls variable behavior:

| Setting | Type | Choices | Description |
|---------|------|---------|-------------|
| Case Conflict | Dropdown | first_wins, error, prefer_upper, prefer_lower, prefer_mixed | How to handle variable name case mismatches |
| Show Types In Window | Checkbox | - | Show type suffixes ($, %, !) in variable window |

**Case Conflict Policies:**
- `first_wins` - First use sets the case (silent)
- `error` - Flag mismatches as errors (catches typos!)
- `prefer_upper` - Choose most uppercase version
- `prefer_lower` - Choose most lowercase version
- `prefer_mixed` - Prefer camelCase/PascalCase

### Interpreter Tab

Controls interpreter behavior:

| Setting | Type | Range | Description |
|---------|------|-------|-------------|
| Strict Mode | Checkbox | - | Enable strict error checking |
| Max Execution Time | Spinbox | 1-3600 | Program timeout in seconds |
| Debug Mode | Checkbox | - | Enable debug output |

### UI Tab

Controls UI appearance:

| Setting | Type | Choices/Range | Description |
|---------|------|---------------|-------------|
| Theme | Dropdown | default, dark, light, classic | Color scheme |
| Font Size | Spinbox | 8-32 | Font size in points |

## Using the Dialog

### Viewing Settings

1. Open dialog (**File → Settings**)
2. Click on tabs to view different categories
3. Scroll within tabs if needed

### Changing Settings

1. Navigate to the setting you want to change
2. For checkboxes: click to toggle
3. For spinboxes: click arrows or type value
4. For dropdowns: click and select option

### Setting Help

For settings with detailed help text:
- Look for **?** button next to setting
- Click **?** to see full help dialog

For short settings:
- Help text shown inline (gray text)

## Button Actions

### OK
- Apply all changes
- Save to disk
- Close dialog immediately

### Cancel
- Discard all changes
- Restore previous values
- Close dialog

### Apply
- Apply all changes
- Save to disk
- **Keep dialog open** for more changes

### Reset to Defaults
- Reset all settings to default values
- Does not save automatically
- Must click OK or Apply to confirm

**Use case:** Settings misconfigured? Click Reset to return to known-good defaults.

## Common Tasks

### Change Auto-Numbering

**Quick Setup for Classic BASIC:**
1. Open Settings → Editor tab
2. Check "Auto Number"
3. Set "Auto Number Step" to 10
4. Click OK

**Quick Setup for Large Programs:**
1. Set "Auto Number Step" to 100
2. This leaves room (110, 120, etc.) to insert lines

### Force Uppercase Keywords

For classic BASIC appearance:
1. Open Settings → Keywords tab
2. Select "force_upper" from Case Style dropdown
3. Click Apply
4. LIST your program to see UPPERCASE keywords

### Enable Variable Typo Detection

Catch mistyped variables:
1. Open Settings → Variables tab
2. Select "error" from Case Conflict dropdown
3. Click Apply

Now `TotalCount` vs `TotalCont` triggers error!

### Enable Strict Mode

More error checking:
1. Open Settings → Interpreter tab
2. Check "Strict Mode"
3. Click Apply

### Change Theme

1. Open Settings → UI tab
2. Select theme from dropdown
3. Click Apply
4. UI updates immediately

## Settings Persistence

Settings are saved to disk automatically when you click OK or Apply.

**Location:**
- Linux/Mac: `~/.mbasic/settings.json`
- Windows: `%APPDATA%\mbasic\settings.json`

Changes persist across sessions.

## Validation

All settings are validated:

- **Range checking**: Spinboxes enforce min/max
- **Type checking**: Only valid types accepted
- **Enum validation**: Dropdowns restrict to valid choices

Invalid values show error dialog and revert to previous value.

## Keyboard Navigation

You can navigate the dialog with keyboard:

| Key | Action |
|-----|--------|
| `Tab` | Next control |
| `Shift+Tab` | Previous control |
| `Space` | Toggle checkbox / open dropdown |
| `Enter` | Activate focused button |
| `Escape` | Close dialog (same as Cancel) |
| `Alt+O` | Click OK (if mnemonic enabled) |
| `Alt+C` | Click Cancel |
| `Alt+A` | Click Apply |

## Tips

1. **Use Apply to experiment** - Apply settings, test them, then tweak and Apply again without closing

2. **Check help buttons** - Settings with **?** have detailed explanations

3. **Reset when lost** - Misconfigured? Reset to Defaults is your friend

4. **Test immediately** - After changing editor settings, type a line to verify

5. **Document your setup** - Screenshot or note your preferred settings

## Workflows

### First-Time Setup

1. Open Settings
2. Set auto-numbering preference (Editor tab)
3. Choose keyword case style (Keywords tab)
4. Optionally enable strict mode (Interpreter tab)
5. Adjust theme/font (UI tab)
6. Click OK

### Switching Between Projects

Different projects may need different settings:

**Classic BASIC project:**
- Auto Number Step: 10
- Keywords: force_upper

**Modern project:**
- Auto Number Step: 100
- Keywords: force_capitalize
- Variables Case Conflict: error

Use Apply to switch quickly without closing dialog.

### Teaching Environment

For teaching BASIC to students:
- Enable "error" mode for variables (catches typos)
- Enable strict mode (more helpful errors)
- Use large font size (easier to read)
- Use classic theme (nostalgic BASIC feel)

## Troubleshooting

### Dialog won't open
- Check File menu for Settings option
- Try keyboard shortcut if available
- Check console for errors

### Changes don't save
- Make sure you clicked OK or Apply (not Cancel or X)
- Check file permissions on `~/.mbasic/settings.json`
- Check disk space

### Setting reverts immediately
- Value is invalid (out of range)
- Check validation error message
- Try value within valid range

### Can't find a setting
- Check all tabs - settings are categorized
- Some settings may not be in Tk (check CLI with SHOWSETTINGS)

## Additional Settings via CLI

Some advanced settings may only be available via CLI commands:

```basic
' In MBASIC CLI mode:
SHOWSETTINGS
SETSETTING setting.name value
```

See: [CLI Settings Commands](../cli/settings.md)

## See Also

- [Settings System Overview](../../common/settings.md)
- [Tk GUI Features](features.md)
- [Tk GUI Getting Started](getting-started.md)
- [Keyboard Shortcuts](../../../user/keyboard-shortcuts.md)
- [CLI Settings Commands](../cli/settings.md)
- [Tk GUI Index](index.md)

[← Back to Tk GUI Help](index.md)
