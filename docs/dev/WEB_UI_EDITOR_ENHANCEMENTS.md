# Web UI Editor Enhancements

## Overview

Implemented editor enhancements for the Web UI to provide similar functionality to Tk and Curses UIs, adapted for web-based interaction patterns.

## Implementation Approach

### Differences from Tk UI

The Tk UI uses Tkinter's Text widget which provides:
- Direct cursor position access
- Event binding for all key presses
- Character-level text manipulation
- Automatic scrolling control

The Web UI uses NiceGUI's textarea (Quasar q-textarea) which:
- Has limited event binding capabilities
- Operates at the whole-text level
- Doesn't expose cursor position easily
- Better suited to manual actions (buttons)

### Design Decision

Instead of automatic behaviors (like Tk's auto-sort on navigation), the Web UI provides **explicit toolbar buttons** for:

1. **Sort** - Sort lines by line number
2. **Renumber** - Renumber lines with GOTO/GOSUB reference updates

This approach:
- ✅ Better fits web interaction patterns
- ✅ Gives user explicit control
- ✅ Works within NiceGUI/Quasar limitations
- ✅ Provides same end result as Tk auto-features

## Features Implemented

### 1. Sort Program Lines

**Button**: "Sort" with sort icon
**Location**: Editor toolbar
**Functionality**:
- Parses all lines in the editor
- Identifies lines with line numbers (regex: `^\s*(\d+)\s`)
- Sorts numbered lines by line number
- Preserves unnumbered lines (comments, blank lines) at end
- Updates editor with sorted content

**Usage**:
1. Edit your program (add/change line numbers)
2. Click "Sort" button
3. Lines automatically reorder by line number

**Example**:
```basic
Before:
30 PRINT "C"
10 PRINT "A"
20 PRINT "B"

After Sort:
10 PRINT "A"
20 PRINT "B"
30 PRINT "C"
```

### 2. Renumber Program

**Button**: "Renumber" with numbered list icon
**Location**: Editor toolbar
**Functionality**:
- Opens dialog to configure:
  - Start line number (default: 10)
  - Increment (default: 10)
- Parses and sorts lines
- Creates mapping of old → new line numbers
- Updates GOTO/GOSUB/THEN/ELSE references
- Renumbers all lines
- Preserves code content

**Smart Reference Updates**:
The renumber feature automatically updates:
- `GOTO linenum`
- `GOSUB linenum`
- `THEN linenum`
- `ELSE linenum`
- `ON variable GOTO linenum`
- `ON variable GOSUB linenum`

**Usage**:
1. Click "Renumber" button
2. Configure start and increment (or use defaults)
3. Click "Renumber" in dialog
4. Program renumbered with references updated

**Example**:
```basic
Before:
5 GOTO 35
15 PRINT "A"
25 IF X > 10 THEN 35
35 PRINT "End"

After Renumber (10, 10):
10 GOTO 40
20 PRINT "A"
30 IF X > 10 THEN 40
40 PRINT "End"
```

## UI Layout

```
Editor Toolbar:
[Run] [Step] [Continue] [Stop] | [Sort] [Renumber] | [Breakpoint] [Variables] [Stack]
```

## Comparison with Other UIs

| Feature | Tk UI | Curses UI | Web UI |
|---------|-------|-----------|--------|
| **Line numbering** | Auto-insert on Enter | Manual | Manual |
| **Line sorting** | Auto on navigation | Manual (RENUM) | Button (Sort) |
| **Renumbering** | Manual (Ctrl+E) | Manual (Ctrl+E) | Button (Renumber) |
| **GOTO/GOSUB update** | Yes | Yes | Yes |
| **User control** | Automatic | Keyboard | Button clicks |

## Technical Implementation

### File: `src/ui/web/web_ui.py`

#### sort_program_lines() (lines 274-308)
```python
def sort_program_lines(self):
    """Sort program lines by line number."""
    # Parse lines with regex
    # Separate numbered from unnumbered
    # Sort numbered lines
    # Rebuild and update editor
```

#### renumber_program() (lines 310-332)
Opens dialog with configuration options.

#### _apply_renumber() (lines 334-392)
```python
def _apply_renumber(self, start: int, increment: int, dialog):
    """Apply renumbering to program."""
    # Parse and sort lines
    # Create old → new line number mapping
    # Update GOTO/GOSUB/THEN/ELSE references
    # Renumber all lines
    # Update editor
```

## User Experience Benefits

1. **Explicit Control**: Users click when they want action
2. **Visual Feedback**: Notifications confirm actions
3. **Configurable**: Renumber dialog allows customization
4. **Safe**: No automatic changes while typing
5. **Consistent**: Same toolbar pattern as other actions

## Future Enhancements

### Phase 2: Advanced Features

1. **Auto-sort on blur**: Automatically sort when leaving editor
2. **Format on paste**: Auto-format pasted code
3. **Undo/Redo**: Add undo support for sort/renumber
4. **Keyboard shortcuts**:
   - Ctrl+Shift+S for Sort
   - Ctrl+Shift+R for Renumber

### Phase 3: Code Editor Upgrade

Consider replacing textarea with a full code editor:
- **CodeMirror 6**: Lightweight, extensible
- **Monaco Editor**: VS Code editor (heavier)

Benefits:
- Syntax highlighting
- Line numbers in gutter
- Auto-completion
- Bracket matching
- Better cursor control

## Testing

### Manual Test Scenarios

1. **Sort mixed lines**:
   - Enter: 30, 10, 20, 50, 40
   - Click Sort
   - Verify: 10, 20, 30, 40, 50

2. **Renumber with GOTO**:
   - Program: `5 GOTO 25` / `25 END`
   - Renumber (10, 10)
   - Verify: `10 GOTO 20` / `20 END`

3. **Preserve comments**:
   - Mix of numbered lines and REM lines
   - Sort
   - Verify: REM lines at end

4. **Empty program**:
   - Clear editor
   - Click Sort/Renumber
   - Verify: Warning message

## Implementation Status

- ✅ Sort button added to toolbar
- ✅ Sort functionality implemented
- ✅ Renumber button added to toolbar
- ✅ Renumber dialog created
- ✅ Renumber with reference updates implemented
- ✅ Tooltips added to buttons
- ✅ Notification feedback
- ⬜ Auto-sort on blur (future)
- ⬜ Keyboard shortcuts (future)

## Commits

- Initial implementation: (pending)

## References

- Tk Editor: `docs/dev/TK_EDITOR_COMPLETION_SUMMARY.md`
- Tk Implementation: `src/ui/tk_ui.py`
- Curses RENUM: `src/ui/curses_ui.py`
- Web UI: `src/ui/web/web_ui.py:274-392`
