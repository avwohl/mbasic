---
title: Web UI Settings Dialog
type: guide
ui: web
description: How to configure settings in the web interface
keywords: [settings, configuration, web, browser, preferences]
---

# Web UI Settings Dialog

The web UI provides a simplified settings dialog for configuring essential MBASIC options. Unlike the Tk desktop interface which has extensive configuration options, the Web UI focuses on the most commonly used settings.

## Opening Settings

**Methods:**
1. Click the **⚙️ Settings** icon in the navigation bar
2. Click menu → Settings

## Settings Dialog Interface

The settings dialog appears as a modal overlay with tabs:

```
┌─────────────────────────────────────────┐
│  Settings                           ✕   │
├─────────────────────────────────────────┤
│  📝 Editor    📊 Limits                 │
├─────────────────────────────────────────┤
│                                         │
│  Auto-Numbering                         │
│  ═══════════════════════════════════    │
│                                         │
│  ☑ Enable auto-numbering                │
│                                         │
│  Line number increment:                 │
│  ┌──────┐                               │
│  │  10  │                               │
│  └──────┘                               │
│                                         │
│  Common values: 10 (classic), 100       │
│  (large programs), 1 (dense)            │
│                                         │
│                      [ Cancel ] [ Save ]│
└─────────────────────────────────────────┘
```

## Tabs

### Editor Tab

Controls editor behavior and auto-numbering.

**Settings available:**
- **Enable auto-numbering** (checkbox)
  - When checked, lines typed without numbers get auto-numbered
  - When unchecked, lines must be numbered manually

- **Line number increment** (number input)
  - Range: 1-1000
  - Default: 10
  - Common values:
    - 10 - Classic BASIC style
    - 100 - Large programs with room to insert
    - 1 - Dense numbering
    - 5 - Compromise between classic and dense

### Limits Tab

Shows resource limits (view-only in current version).

**Information displayed:**
- Maximum variables
- Maximum string length
- Maximum array dimensions

These limits are for information only and cannot be changed via the UI (they're set in the interpreter configuration).

## Changing Settings

### Enable/Disable Auto-Numbering

1. Open Settings dialog
2. Click **Editor** tab
3. Check or uncheck "Enable auto-numbering"
4. Click **Save**

### Change Line Number Increment

1. Open Settings dialog
2. Click **Editor** tab
3. Click on "Line number increment" field
4. Type new value (1-1000)
5. Click **Save**

**Example:** Change from 10 to 100
```
Before:
  PRINT "Hello"  → 10 PRINT "Hello"
  PRINT "World"  → 20 PRINT "World"

After changing to 100:
  PRINT "Hello"  → 100 PRINT "Hello"
  PRINT "World"  → 200 PRINT "World"
```

## Button Actions

### Save
- Apply all changes
- Save to browser localStorage
- Close dialog
- Show success notification

### Cancel
- Discard all changes
- Close dialog without saving

### Close (✕)
- Same as Cancel
- No changes are saved

## Settings Storage

Web UI settings can be stored in two ways depending on your deployment configuration:

### Local Storage (Default)

By default, settings are stored in your **browser's localStorage**. This means:

✅ **Advantages:**
- Settings persist across page reloads
- No server required
- Fast access
- Privacy - settings stay in your browser

⚠️ **Limitations:**
- Settings are per-browser, per-domain
- Clearing browser data clears settings
- Settings don't sync across devices/browsers
- Not shared with CLI/desktop versions

### Redis Session Storage (Multi-User Deployments)

If the web server is configured with `NICEGUI_REDIS_URL`, settings are stored in Redis with per-session isolation:

✅ **Advantages:**
- Settings persist across browser tabs
- Shared state in multi-instance deployments
- Better for production environments
- Automatic session cleanup
- Supports concurrent users

⚠️ **Limitations:**
- Requires Redis server
- Settings are session-based (cleared when session expires)
- Requires server-side configuration

**Server Configuration:**
```bash
# Set Redis URL environment variable
export NICEGUI_REDIS_URL="redis://localhost:6379/0"

# Start web server
python -m src.ui.web.main
```

Each user session gets isolated settings storage, preventing conflicts between concurrent users.

### Exporting Settings (Future)

To share settings across browsers or with CLI:
1. Open browser developer tools ({{kbd:help:web}}2)
2. Go to Application → Local Storage
3. Find MBASIC settings key
4. Copy JSON value
5. Import in other browser or save to `~/.mbasic/settings.json`

## Common Use Cases

### Quick Start with Classic BASIC Style

1. Open Settings
2. Set "Line number increment" to **10**
3. Save

Result: Lines number as 10, 20, 30, 40...

### Large Program with Room to Insert

1. Open Settings
2. Set "Line number increment" to **100**
3. Save

Result: Lines number as 100, 200, 300, 400...
You can easily insert lines like 150, 250 between them.

### Disable Auto-Numbering (Manual Control)

1. Open Settings
2. Uncheck "Enable auto-numbering"
3. Save

Result: You must type line numbers explicitly
```basic
10 PRINT "Hello"
20 PRINT "World"
```

### Dense Numbering

1. Open Settings
2. Set "Line number increment" to **1**
3. Save

Result: Lines number as 1, 2, 3, 4...
Use when you have very large programs and don't need gaps.

## Testing Settings

After changing settings, test immediately:

1. Change increment to 100
2. Click Save
3. In editor, type: `PRINT "TEST"`
4. Verify it auto-numbers as 100 (or next 100-increment)
5. Type another line: `PRINT "TEST2"`
6. Verify it auto-numbers as 200

If behavior is wrong, reopen settings and adjust.

## Validation

Settings are validated when you click Save:

- **Line number increment** must be 1-1000
- Invalid values show error notification
- Dialog remains open for correction

**Example error:**
```
⚠️ Error: Line number increment must be between 1 and 1000
```

## Tips

1. **Start conservative** - Use default 10 until you know your program size

2. **Large programs** - Use 100 or 1000 for flexibility

3. **Test immediately** - After changing settings, type a line to verify

4. **Reload to reset** - If confused, reload page to get last saved settings

5. **Check notifications** - Success/error messages appear top-right

6. **Mobile users** - Tap settings icon, use native number input

## Browser Compatibility

Settings dialog works in all modern browsers:
- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers

**Note:** localStorage must be enabled (check browser privacy settings)

## Troubleshooting

### Settings dialog won't open
- Check browser console for errors ({{kbd:help:web}}2)
- Refresh page
- Check that JavaScript is enabled

### Settings don't save
- Check localStorage isn't disabled
- Check browser isn't in private/incognito mode
- Check disk space (localStorage has ~5-10MB limit)

### Settings reset after reload
- Browser may be clearing localStorage
- Check browser privacy settings
- Try disabling auto-clear on exit

### Auto-numbering not working after change
- Make sure you clicked Save (not Cancel)
- Refresh page if needed
- Check "Enable auto-numbering" is checked
- Clear editor and try new lines

## Future Features

Planned enhancements for web settings:

- [ ] More settings (keywords, variables, interpreter)
- [ ] Import/export settings as JSON
- [ ] Share settings via URL
- [ ] Sync settings to cloud
- [ ] Per-project settings
- [ ] Settings presets (beginner, expert, classic)

## See Also

- [Settings System Overview](../../common/settings.md)
- [Web UI Features](features.md)
- [Web UI Getting Started](getting-started.md)
- [Keyboard Shortcuts](../../../user/keyboard-shortcuts.md)
- [Web UI Index](index.md)

[← Back to Web UI Help](index.md)
