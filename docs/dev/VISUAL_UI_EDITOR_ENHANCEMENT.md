# Visual UI Editor Enhancement Project

## Status: PARTIAL IMPLEMENTATION

**What's Been Done:**
- ✅ Auto-numbering on Enter (src/ui/tk_ui.py:1305)
- ✅ Smart Insert Line - Ctrl+I (src/ui/tk_ui.py:1469, bound at line 284)
- ✅ Auto-sort on line change (src/ui/tk_ui.py:1395 _check_line_change)
- ✅ LineNumberedText widget with status-only column (src/ui/tk_widgets.py:16, width=20)
- ✅ Renumber dialog (Web UI: src/ui/web/web_ui.py:476)

**What's NOT Done:**
- ❌ Complete removal of line number duplication (status column narrowed but numbers still may show)
- ❌ Auto-scroll to sorted position (needs verification)
- ❌ Full feature parity with curses UI (see TK_UI_ENHANCEMENT_PLAN.md)

---

## Problem Statement

The Tk and Web UI program editors have several usability issues compared to the curses UI:

### Current Issues

#### 1. Line Number Duplication (Tk/Web)
- **Problem**: Users type line numbers in the text area (e.g., `10 PRINT "HELLO"`)
- **Problem**: Line numbers are duplicated in a separate column on the left
- **Result**: Confusing visual duplication
- **Example**: `[10] 10 PRINT "HELLO"` (10 appears twice)

#### 2. Non-Copyable Line Numbers (Tk/Web)
- **Problem**: The separate line number column is not selectable/copyable
- **Curses behavior**: Both columns are selectable (you can copy with line numbers)
- **Tk/Web behavior**: Only the code text is copyable, not the line numbers

#### 3. No Auto-Sort on Edit (Tk/Web)
- **Curses behavior**: When you move off a line, it automatically sorts into line number order
- **Tk/Web behavior**: Line stays in place where you edited it, no auto-sort
- **Impact**: Lines get out of order, hard to navigate

#### 4. No Auto-Scroll to Sorted Position (Tk/Web)
- **Curses behavior**: After auto-sort, scrolls to show the line in its new sorted position
- **Tk/Web behavior**: N/A (no auto-sort)

#### 5. Auto-Numbering Not Working (Tk/Web)
- **Curses behavior**: Press Enter, next line gets auto-numbered (10, 20, 30...)
- **Tk/Web behavior**: Not implemented or broken

## Curses UI Reference Behavior

### Line Editing Flow
1. **Type line**: `10 PRINT "HELLO"`
2. **Move to next line** (arrow down, Enter, etc.)
3. **Auto-sort triggered**: Line moves to correct position based on line number
4. **Auto-scroll**: View scrolls to show the line in its new position
5. **Auto-number**: If Enter pressed, next line gets auto-numbered

### Format
```
S#####_CODE
│││││││└─── Code area (unlimited width)
││││││└──── Space separator
│││││└───── Line number digit 5
││││└────── Line number digit 4
│││└─────── Line number digit 3
││└──────── Line number digit 2
│└───────── Line number digit 1
└────────── Status (●=breakpoint, ?=error, space=normal)
```

### Key Features
- **Field 1**: Status symbol (read-only, visual only)
- **Field 2**: Line number (variable width, editable as part of text)
- **Separator**: Space
- **Field 3**: Code
- **All text is selectable and copyable** (including line numbers)
- **Auto-sort on navigation**: Sort only when moving away from line (not on every keystroke)
- **Auto-scroll**: Jump to line's new position after sort
- **Auto-numbering**: Smart increment based on surrounding lines

### Auto-Numbering Logic (Curses)
```python
# On Enter key:
current_line_number = 100  # Just edited line 100
increment = 10
next_num = current_line_number + increment  # 110

# Find next existing line number
existing_lines = [100, 150, 200]  # Sorted line numbers
# Next line after 100 is 150
# So next_num (110) must be < 150

# If 110 >= 150, keep incrementing until it fits
while next_num in existing_lines or next_num >= max_allowed:
    next_num += increment

# Insert new line: " 110  "
```

## Proposed Solution

### Remove Separate Line Number Column

**For Tk and Web UIs**:
- Remove the Canvas/column that shows line numbers
- Keep status symbols (●, ?) but integrate them differently
- Line numbers are part of the editable text (like curses)

### In-Place Line Number Editing

**Users type line numbers directly**:
```
10 PRINT "HELLO"
20 FOR I=1 TO 10
30 PRINT I
40 NEXT I
```

**No duplication** - what you see is what you type.

### Auto-Sort on Line Change

**Trigger**: When cursor moves away from a line (via keyboard or mouse):
- Detect line number change (compare before/after)
- Sort all lines by line number
- Update editor display with sorted lines
- Scroll to show the edited line in its new position

**Implementation**:
- Bind to cursor movement events
- Track "last edited line"
- On focus change, trigger sort+scroll

### Auto-Scroll to Position

**After sorting**:
- Find the line that was just edited
- Calculate its new position in sorted order
- Scroll the editor to make that line visible
- Position cursor at start of code area (column 7)

### Auto-Numbering

**On Enter key**:
1. Parse current line to get line number
2. Calculate next line number = current + increment
3. Check if next number conflicts with existing lines
4. Adjust if necessary (skip conflicts)
5. Insert new line with auto-generated line number
6. Position cursor at code area

**Configuration** (like curses):
- `auto_number_start`: Starting line number (default: 10)
- `auto_number_increment`: Increment between lines (default: 10)
- `auto_number_enabled`: Enable/disable auto-numbering (default: True)

### Status Symbol Integration

**Options**:

#### Option 1: Keep separate column for status only
- Remove line number from column
- Show only ● or ? symbols
- Width: ~15px (just for symbol)
- Line numbers are in text

#### Option 2: Inline status symbols
- Add status symbol at start of line text
- Format: `●10 PRINT "HELLO"` or `?10 PRINT "HELLO"`
- Fully copyable
- More like classic BASIC editors

#### Option 3: Gutter markers (modern)
- Show ● and ? in margin
- Like VS Code breakpoint gutter
- Clickable for toggle
- Not part of selectable text

**Recommendation**: Option 1 (status column only)
- Maintains clean separation
- Clickable for breakpoint toggle
- Doesn't interfere with copying code

## Implementation Plan

### Task Tracking

**Status Legend**: ⬜ Not Started | 🟨 In Progress | ✅ Completed

**Note**: Curses UI feature parity (variables window, debugger controls) is tracked in separate document: `CURSES_UI_FEATURE_PARITY.md`

#### Phase 1: Tk UI Refactoring (Editor)
- ⬜ 1.1 Remove line number display from column (keep status only)
- ⬜ 1.2 Implement auto-sort on line change
- ⬜ 1.3 Implement auto-numbering on Enter key
- ⬜ 1.4 Add auto-scroll to sorted position
- ⬜ 1.5 Update LineNumberedText widget
- ⬜ 1.6 Add event bindings for cursor movement tracking

#### Phase 2: Web UI Refactoring (Editor)
- ⬜ 2.1 Remove line number gutter (keep status only)
- ⬜ 2.2 Implement auto-sort on line change
- ⬜ 2.3 Implement auto-numbering on Enter key
- ⬜ 2.4 Add auto-scroll to sorted position
- ⬜ 2.5 Add JavaScript event handlers

#### Phase 3: Testing (All UIs)
- ⬜ 3.1 Test Tk UI line editing workflow
- ⬜ 3.2 Test Web UI line editing workflow
- ⬜ 3.3 Test auto-numbering in both UIs
- ⬜ 3.4 Test auto-sort in both UIs
- ⬜ 3.5 Test line number copying
- ⬜ 3.6 Performance test with 1000+ line programs
- ⬜ 3.7 Comparison test against curses UI (reference implementation)

#### Phase 4: Documentation
- ⬜ 4.1 Update Tk UI help documentation
- ⬜ 4.2 Update Web UI help documentation
- ⬜ 4.3 Add screenshots showing new behavior
- ⬜ 4.4 Update user guide

**See also**: `CURSES_UI_FEATURE_PARITY.md` for curses-specific enhancements (variables window sorting, array cell display, step commands)

### Phase 1: Tk UI Refactoring

#### 1.1 Remove Line Number Display from Column
**File**: `src/ui/tk_widgets.py`

```python
class LineNumberedText:
    def _redraw(self):
        # Remove line number drawing code
        # Keep only status symbol drawing

        # OLD:
        # self.canvas.create_text(20, y, text=f'{basic_line_num:>5}')

        # NEW:
        # (remove this code)
```

**Change Canvas width**: 70px → 20px (just for status symbol)

#### 1.2 Implement Auto-Sort on Line Change
**File**: `src/ui/tk_ui.py`

```python
class TkBackend:
    def __init__(self):
        # Track last cursor position
        self.last_cursor_line = None
        self.last_line_content = None

        # Bind cursor movement events
        self.editor_text.text.bind('<FocusOut>', self._on_line_change)
        self.editor_text.text.bind('<KeyPress-Up>', self._on_line_change)
        self.editor_text.text.bind('<KeyPress-Down>', self._on_line_change)
        self.editor_text.text.bind('<KeyPress-Return>', self._on_enter_key)

    def _on_line_change(self, event):
        """Called when cursor moves away from line."""
        current_line = self._get_current_line_index()

        if self.last_cursor_line is not None:
            # Check if line number changed
            old_content = self.last_line_content
            new_content = self._get_line_content(self.last_cursor_line)

            old_num = self._parse_line_number(old_content)
            new_num = self._parse_line_number(new_content)

            if old_num != new_num:
                # Line number changed, trigger sort
                self._sort_and_scroll(self.last_cursor_line, new_num)

        # Update tracking
        self.last_cursor_line = current_line
        self.last_line_content = self._get_line_content(current_line)

    def _sort_and_scroll(self, edited_line_index, edited_line_num):
        """Sort lines and scroll to edited line's new position."""
        # Get all lines
        lines = self.editor_text.text.get('1.0', 'end').split('\n')

        # Parse and sort
        parsed = []
        for i, line in enumerate(lines):
            line_num = self._parse_line_number(line)
            if line_num is not None:
                parsed.append((line_num, line))

        parsed.sort(key=lambda x: x[0])

        # Rebuild text
        sorted_lines = [line for _, line in parsed]
        new_text = '\n'.join(sorted_lines)

        # Update editor
        self.editor_text.text.delete('1.0', 'end')
        self.editor_text.text.insert('1.0', new_text)

        # Find new position of edited line
        new_index = next((i for i, (num, _) in enumerate(parsed) if num == edited_line_num), 0)

        # Scroll and position cursor
        self.editor_text.text.mark_set('insert', f'{new_index+1}.0')
        self.editor_text.text.see(f'{new_index+1}.0')
```

#### 1.3 Implement Auto-Numbering
**File**: `src/ui/tk_ui.py`

```python
class TkBackend:
    def __init__(self):
        self.auto_number_enabled = True
        self.auto_number_start = 10
        self.auto_number_increment = 10
        self.next_auto_line_num = self.auto_number_start

    def _on_enter_key(self, event):
        """Handle Enter key for auto-numbering."""
        if not self.auto_number_enabled:
            return None  # Let default handler run

        # Get current line number
        current_line = self._get_current_line()
        current_num = self._parse_line_number(current_line)

        if current_num is None:
            return None

        # Calculate next number
        next_num = current_num + self.auto_number_increment

        # Get all existing line numbers
        existing_nums = set()
        lines = self.editor_text.text.get('1.0', 'end').split('\n')
        for line in lines:
            num = self._parse_line_number(line)
            if num:
                existing_nums.add(num)

        # Find next line after current
        sorted_nums = sorted(existing_nums)
        current_idx = sorted_nums.index(current_num) if current_num in sorted_nums else -1
        max_allowed = sorted_nums[current_idx + 1] if current_idx + 1 < len(sorted_nums) else 99999

        # Adjust if conflict
        while next_num in existing_nums or next_num >= max_allowed:
            next_num += self.auto_number_increment
            if next_num >= 99999:
                next_num = current_num + 1
                break

        # Insert new line with number
        self.editor_text.text.insert('insert', f'\n{next_num} ')

        # Update next auto number
        self.next_auto_line_num = next_num + self.auto_number_increment

        return 'break'  # Prevent default Enter behavior
```

### Phase 2: Web UI Refactoring

Apply same changes to Web UI (CodeMirror/Monaco editor):
- Remove line number gutter (use built-in gutter for status only)
- Add keypress handlers for auto-sort
- Implement auto-numbering on Enter
- Add scroll-to-position after sort

**File**: `src/ui/web/web_ui.py`

Similar implementation using JavaScript event handlers in the web editor.

### Phase 3: Testing

#### 3.1 Manual Testing
1. **Line editing**: Type `10 PRINT`, move down, verify it sorts
2. **Out of order**: Type `30`, then `20`, then `10`, verify they sort on navigation
3. **Auto-number**: Type `10`, press Enter, verify `20` appears
4. **Auto-number gaps**: Lines `10, 30`, edit `10`, press Enter, verify `20` (not 30)
5. **Copying**: Select text including line numbers, copy, paste, verify format
6. **Scrolling**: Edit line `100` in program with many lines, verify scroll to position

#### 3.2 Comparison Test
- Edit same program in all three UIs (CLI, Curses, Tk, Web)
- Verify consistent behavior
- Document any differences

### Phase 4: Documentation

Update help files:
- `docs/help/ui/tk/editing.md` - Document new editing behavior
- `docs/help/ui/web/editing.md` - Document new editing behavior
- Add screenshots showing before/after

## Technical Details

### Event Binding Strategy (Tk)

**Problem**: Need to detect when cursor moves away from a line

**Solutions**:
1. `<KeyPress-Up>`, `<KeyPress-Down>` - Arrow keys
2. `<Button-1>` - Mouse click on different line
3. `<FocusOut>` - Focus leaves text widget
4. Timer-based - Check every N milliseconds (not ideal)

**Chosen**: Combination of #1, #2, #3

### Performance Considerations

**Concern**: Sorting on every line change could be slow for large programs

**Mitigation**:
- Only sort when line number actually changes
- Only sort on navigation away (not every keystroke)
- Cache parsed line numbers
- Use efficient sorting algorithm

**Benchmark target**: < 50ms for 1000-line program

### Curses UI - No Changes Needed

The curses UI already works correctly. This project is about bringing Tk and Web UIs to feature parity.

## Configuration

Add to user config (`.mbasic/config.toml`):

```toml
[editor]
auto_number_enabled = true
auto_number_start = 10
auto_number_increment = 10
auto_sort_on_edit = true  # NEW: Enable/disable auto-sort
```

## Future Enhancements

### Advanced Auto-Numbering
- **Smart increment**: Detect existing increment pattern (10, 20, 30 → increment=10)
- **Renumber**: Command to renumber all lines with new start/increment
- **Insert mode**: Auto-number between existing lines (10, 20 → insert 15)

### Visual Feedback
- **Flash line**: Briefly highlight line after sort to show new position
- **Animation**: Smooth scroll animation to new position
- **Status bar**: Show "Line sorted to position N"

### Undo Support
- Ensure auto-sort is undoable
- Single undo should revert both number change and sort

## Success Criteria

✅ Line numbers editable in-place (part of text)
✅ No duplication in separate column
✅ Line numbers copyable (select and copy text includes line numbers)
✅ Auto-sort when navigating away from edited line
✅ Auto-scroll to show line in new sorted position
✅ Auto-numbering works on Enter key
✅ Status symbols (●, ?) still visible and functional
✅ Breakpoint toggle still works
✅ Performance acceptable for large programs (1000+ lines)
✅ Behavior consistent across Tk and Web UIs
✅ Behavior matches curses UI reference implementation

## Open Questions

1. **Immediate sorting**: Should we sort immediately on line number edit, or wait for navigation?
   - **Answer**: Wait for navigation (like curses) - better performance

2. **Partial line numbers**: What if user types `1` (incomplete line number)?
   - **Answer**: Treat as line 1 (valid), sort accordingly

3. **Invalid line numbers**: What if user types `ABC PRINT` (no number)?
   - **Answer**: Leave at current position, don't sort (treat as comment/invalid)

4. **Multiple edits**: User edits 3 lines without navigating away, then navigates?
   - **Answer**: Only last edited line triggers sort

## References

- Curses UI implementation: `src/ui/curses_ui.py:109-223`
- Current Tk widget: `src/ui/tk_widgets.py:16-220`
- Auto-numbering logic: `src/ui/curses_ui.py:479-554`
- Sort logic: `src/ui/curses_ui.py:1183-1222`
