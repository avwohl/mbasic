# Find and Replace (Curses UI)

## Current Status

The Curses UI currently **does not have** Find/Replace functionality. This feature is planned for future implementation.

## Workarounds

### Finding Text

While there's no built-in find feature, you can:

1. **Use line numbers** to navigate directly:
   - Press `Ctrl+G` to go to a specific line
   - Type the line number and press Enter

2. **Visual scanning**:
   - Use Page Up/Page Down to browse
   - Arrow keys for line-by-line movement

3. **Export and search**:
   - Save the program: `Ctrl+S`
   - Use external editor with find feature
   - Reload with `Ctrl+O`

### Replacing Text

For text replacement:

1. **Manual editing**:
   - Navigate to each occurrence
   - Edit line by line
   - Use `Ctrl+K` to clear line and retype

2. **External editor**:
   - Save program to file
   - Edit in external editor (vim, nano, etc.)
   - Reload in Curses UI

3. **Use different UI**:
   - Tk UI has full Find/Replace (Ctrl+F/Ctrl+H)
   - Edit there and return to Curses

## Planned Implementation

Find/Replace is planned with these features:

**Find (Ctrl+F):**
- Search forward/backward
- Case sensitive option
- Whole word matching
- Regular expression support

**Replace (Ctrl+H):**
- Replace single occurrence
- Replace all
- Confirmation prompts
- Undo support

**Navigation:**
- F3 for Find Next
- Shift+F3 for Find Previous
- Highlight all matches
- Match counter

## Alternative UIs with Find/Replace

If you need Find/Replace now, use:

### Tk UI
- Full Find/Replace dialogs
- Ctrl+F for Find
- Ctrl+H for Replace
- F3 for Find Next
- Case sensitive and whole word options

### Command to switch:
```bash
python3 mbasic.py --backend tk
```

## Status Updates

Check the project repository for updates on Find/Replace implementation for Curses UI:
- GitHub issues for feature requests
- Pull requests for implementation
- Release notes for availability

## See Also

- [Editing Commands](editing.md) - Current editing features
- [Keyboard Commands](keyboard-commands.md) - Available shortcuts
- [Tk Features](../tk/features.md) - Tk UI with Find/Replace