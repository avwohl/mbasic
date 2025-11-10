---
description: Guide to writing and editing BASIC programs in the Curses UI
keywords:
- command
- curses
- editing
- execute
- file
- for
- if
- line
- next
- number
title: Editing Programs in Curses UI
type: guide
---

# Editing Programs in Curses UI

How to write and edit BASIC programs.

## Line-Based Editing

BASIC programs are made of numbered lines:

```basic
10 PRINT "Hello"
20 END
```

Each line starts with a line number (1-65535).

## Adding Lines

1. Type a line number
2. Type your BASIC code
3. Press **Enter** to save the line

### Example

```
Type: 10 PRINT "Hello"
Press Enter
→ Line 10 saved
```

## Editing Existing Lines

1. Use **Up/Down** arrows to navigate to the line
2. Edit the text
3. Press **Enter** to save changes

## Deleting Lines

To delete a line, use one of these methods:

### Quick Delete (^D)
1. Navigate to the line
2. Press **^D**
3. Line is deleted immediately

### Manual Delete
1. Navigate to the line
2. Delete all text after the line number
3. Press **Enter**

Or type just the line number:

```
Type: 10
Press Enter
→ Line 10 deleted
```

## Line Numbering

### Auto-increment

After entering a line, the cursor moves to the next line number (incremented by 10).

### Manual Line Numbers

You can use any line numbers:

```basic
10 PRINT "First"
15 PRINT "Middle"
20 PRINT "Last"
```

This leaves room to insert lines later.

## Cursor Movement

| Key | Action |
|-----|--------|
| **Left/Right** | Move within line |
| **Up/Down** | Move between lines |
| **Home** or **^A** | Start of line |
| **End** or **^E** | End of line |

## Editing Keys

| Key | Action |
|-----|--------|
| **Backspace** | Delete before cursor |
| **Delete** | Delete at cursor |
| **Enter** | Save line |

**Note:** Cut/Copy/Paste operations are not available in the Curses UI due to keyboard shortcut conflicts:
- **{{kbd:stop:curses}}** (Ctrl+C) - Used for Stop/Interrupt, cannot be used for Copy
- **{{kbd:save:curses}}** (Ctrl+S) - Used for Save File, cannot be used for Paste (also reserved by terminal for flow control)
- Cut would require Ctrl+X which isn't used but omitted for consistency

**Workaround:** Use your terminal's native clipboard functions (typically Shift+Ctrl+C/V or mouse selection).

## Tips

- Line numbers can be any value 1-65535
- Common practice: increment by 10
- This leaves room for insertions
- Use **^A/^E** if no Home/End keys

## See Also

- [Keyboard Shortcuts](../../../user/keyboard-shortcuts.md) - All shortcuts
- [Running Programs](running.md) - Execute your code
- [File Operations](files.md) - Save and load