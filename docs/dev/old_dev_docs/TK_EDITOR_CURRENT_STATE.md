# Tk Editor Current State Analysis

## Current Implementation

### File: `src/ui/tk_widgets.py`

**Class**: `LineNumberedText` (lines 16-220)

### Layout

```
┌────────┬──────────────────────────────────┐
│ Canvas │ Text Widget                      │
│  (70px)│                                  │
│        │                                  │
│ [S][###│ User can type line numbers here │
│        │                                  │
└────────┴──────────────────────────────────┘
```

**Canvas shows**:
- Column 0: Status (●=breakpoint, ?=error, space=normal)
- Variable width line number

**Text widget**:
- User can type anything, including line numbers
- No coordination with Canvas line numbers

### Problems Identified

#### 1. Line Number Duplication ✗

User types in text: `10 PRINT "HELLO"`
Canvas shows: `[10]`
Result: Line number appears twice!

**Root cause**: Canvas line numbers extracted from text content, but user also types them.

#### 2. Non-Copyable Line Numbers ✗

When user selects text, only Text widget content is selected, not Canvas.
Cannot copy line numbers with code.

**Root cause**: Canvas is separate widget, not part of text selection.

#### 3. No Auto-Sort ✗

User types:
```
30 PRINT "C"
20 PRINT "B"
10 PRINT "A"
```

Lines stay in typed order, not sorted by line number.

**Root cause**: No event handler for line navigation that triggers sort.

#### 4. No Auto-Scroll ✗

Even if sort were implemented, no scroll to show line's new position.

**Root cause**: No tracking of edited line or scroll-to-position logic.

#### 5. Auto-Numbering Not Working ✗

Press Enter on line `10`, expect `20` to appear.
Result: Blank line.

**Root cause**: No Enter key handler for auto-numbering.

### Comparison with Curses UI (Reference Implementation)

**Curses UI**: `src/ui/curses_ui.py` (ProgramEditorWidget)

**Layout**:
```
S#####_CODE
```

All text (status, line number, code) is in one editable widget.

**Features that work**:
- ✅ Line numbers are part of editable text
- ✅ Copyable with code
- ✅ Auto-sort on navigation (when cursor leaves line)
- ✅ Auto-scroll to sorted position
- ✅ Auto-numbering on Enter

### Key Differences

| Feature | Curses UI | Tk UI (current) |
|---------|-----------|-----------------|
| Line number location | In text | In canvas |
| Copyable line numbers | Yes | No |
| Auto-sort | Yes | No |
| Auto-scroll | Yes | No |
| Auto-numbering | Yes | No |
| Status symbols | Part of text | In canvas |
| Breakpoint toggle | Click status column | Not in canvas |

## Proposed Solution (from VISUAL_UI_EDITOR_ENHANCEMENT.md)

### Option 1: Keep Canvas for Status Only (RECOMMENDED)

**Changes**:
1. Narrow Canvas to ~20px (just status symbol)
2. Remove line number drawing from Canvas
3. Add line numbers to text content programmatically
4. Implement auto-sort on cursor movement
5. Implement auto-scroll after sort
6. Implement auto-numbering on Enter

**Canvas**: `[●]` or `[?]` or `[ ]` (just 1 character)
**Text**: `10 PRINT "HELLO"` (line number + code)

**Benefits**:
- Status symbols remain clickable
- Line numbers are copyable
- Matches curses UI behavior
- Visual separation maintained

### Option 2: All-in-Text

Remove Canvas entirely, put `●10 PRINT` in text.

**Issues**:
- Status symbols become editable (users could delete ●)
- Harder to make clickable
- Mixed concerns in text widget

## Implementation Plan

### Phase 1: Narrow Canvas (Status Only)

**File**: `src/ui/tk_widgets.py`

```python
# Line 49: Change canvas width
self.canvas = tk.Canvas(
    self,
    width=20,  # Was: 70 (for status + line number)
    ...
)
```

**Update `_redraw()` method**:
- Remove line number drawing code
- Keep only status symbol drawing

### Phase 2: Line Numbers in Text

**Approach**: Maintain internal representation with line numbers, insert/update text widget content.

**Data structure**:
```python
# In TkBackend
self.program_lines = {  # line_num -> code (without line number prefix)
    10: 'PRINT "HELLO"',
    20: 'FOR I=1 TO 10',
    30: 'NEXT I'
}
```

**Text widget content** (computed from program_lines):
```
   10 PRINT "HELLO"
   20 FOR I=1 TO 10
   30 NEXT I
```

### Phase 3: Auto-Sort on Navigation

**Events to bind**:
- `<FocusOut>` - Focus leaves text widget
- `<KeyPress-Up>` - Arrow up
- `<KeyPress-Down>` - Arrow down
- `<Button-1>` - Mouse click (if on different line)

**Logic**:
```python
def _on_line_change(self, event):
    # Get current line index
    current_line_idx = get_current_line_index()

    # If we moved off previous line
    if self.last_edited_line_idx is not None:
        # Parse previous line for line number change
        old_line_num, old_code = parse_line(self.last_edited_line_idx)

        # Update program_lines
        if old_line_num:
            self.program_lines[old_line_num] = old_code

        # Rebuild text widget with sorted lines
        self._rebuild_text_sorted()

        # Scroll to edited line's new position
        self._scroll_to_line(old_line_num)

    self.last_edited_line_idx = current_line_idx
```

### Phase 4: Auto-Numbering on Enter

**Bind Enter key**:
```python
self.text.bind('<Return>', self._on_enter_key)

def _on_enter_key(self, event):
    # Get current line number
    current_line_num = parse_current_line_number()

    if current_line_num:
        # Calculate next number
        next_num = current_line_num + auto_number_increment

        # Find gap in existing line numbers
        existing_nums = sorted(self.program_lines.keys())
        next_available = find_next_available_number(
            current_line_num, existing_nums, auto_number_increment
        )

        # Insert new line with number (variable width)
        self.text.insert('insert', f'\\n{next_available} ')

        return 'break'  # Prevent default Enter behavior
```

## Testing Plan

### Manual Tests

1. **Line number duplication**
   - Type `10 PRINT "HELLO"`
   - Verify line number appears only once (not in canvas)

2. **Copyable line numbers**
   - Select line including line number
   - Copy and paste into another app
   - Verify line number is included

3. **Auto-sort**
   - Type: `30 PRINT "C"`
   - Type: `20 PRINT "B"`
   - Type: `10 PRINT "A"`
   - Move cursor up/down
   - Verify lines sort: 10, 20, 30

4. **Auto-scroll**
   - In program with 50 lines
   - Edit line 5 to be line 45
   - Move cursor off line
   - Verify scroll to show line 45

5. **Auto-numbering**
   - Type: `10 PRINT "HELLO"`
   - Press Enter
   - Verify: `   20 ` appears
   - Press Enter again
   - Verify: `   30 ` appears

### Automated Tests (Future)

Use tkinter test framework or screenshot comparison.

## Risks and Mitigations

### Risk 1: Performance

**Issue**: Rebuilding entire text widget on every line change could be slow for large programs.

**Mitigation**:
- Only rebuild if line number actually changed
- Use incremental update for simple edits
- Cache parsed line numbers

### Risk 2: Cursor Position

**Issue**: Rebuilding text widget loses cursor position.

**Mitigation**:
- Save cursor position before rebuild
- Restore after rebuild
- Adjust for line movement

### Risk 3: Undo/Redo

**Issue**: Programmatic text changes break undo stack.

**Mitigation**:
- Use text widget's undo/redo system carefully
- Mark programmatic changes as separate undo unit
- Test undo thoroughly

## References

- Current implementation: `src/ui/tk_widgets.py:16-220`
- Curses reference: `src/ui/curses_ui.py:104-1230` (ProgramEditorWidget)
- Design doc: `docs/dev/VISUAL_UI_EDITOR_ENHANCEMENT.md`

## Next Steps

1. Create feature branch: `feature/tk-editor-refactor`
2. Implement Phase 1 (narrow canvas)
3. Test with existing programs
4. Implement Phase 2 (line numbers in text)
5. Test copying
6. Implement Phase 3 (auto-sort)
7. Test sorting behavior
8. Implement Phase 4 (auto-numbering)
9. Full integration testing
10. Compare with curses UI behavior
