# Find and Replace (Curses UI)

## Current Status

The Curses UI currently **does not have** Find/Replace functionality for the editor. This feature is planned for future implementation.

**Note:** Search IS available in the Variables Window (press `/` while in the variables window to search for a variable by name). This document is specifically about Find/Replace in the program editor.

## Workarounds

### Finding Text

While there's no built-in find feature, you can:

1. **Use line numbers** to navigate directly:
   - In immediate mode, type a line number to view that line
   - Use arrow keys to move between lines

2. **Visual scanning**:
   - Use Page Up/Page Down to browse
   - Arrow keys for line-by-line movement

3. **Export and search**:
   - Save the program: {{kbd:save:curses}}
   - Use external editor with find feature
   - Reload with {{kbd:open:curses}}

### Replacing Text

For text replacement:

1. **Manual editing**:
   - Navigate to each occurrence
   - Edit line by line
   - Use Delete key to delete line and retype

2. **External editor**:
   - Save program to file
   - Edit in external editor (vim, nano, etc.)
   - Reload in Curses UI

3. **Use different UI**:
   - Tk UI has full Find/Replace
   - Edit there and return to Curses

## Planned Implementation

Find/Replace is planned with these features:

**Find:**
- Search forward/backward
- Case sensitive option
- Whole word matching
- Regular expression support

**Replace:**
- Replace single occurrence
- Replace all
- Confirmation prompts

**Navigation:**
- Next/Previous match navigation
- Highlight all matches
- Match counter

## Alternative UIs with Find/Replace

If you need Find/Replace now, use:

### Tk UI
- Full Find/Replace dialogs
- Use Edit menu for Find/Replace
- Case sensitive and whole word options

### Command to switch:
```bash
python3 mbasic --ui tk
```

## Status Updates

Check the project repository for updates on Find/Replace implementation for Curses UI:
- GitHub issues for feature requests
- Pull requests for implementation
- Release notes for availability

## See Also

- [Editing Commands](editing.md) - Current editing features
- [Keyboard Shortcuts](../../../user/keyboard-shortcuts.md) - Available shortcuts
- [Tk Features](../tk/features.md) - Tk UI with Find/Replace