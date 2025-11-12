# Curses Editor Scrolling Issues TODO

## Issue 1: ^U Menu Scrolls to Line 1 on Open

**Status**: TODO (partially fixed in v877 - scroll position restores on close)

**Current Behavior**:
- Press ^U to open menu
- **Bug**: Program scrolls to line 1
- Close menu with ESC
- **Good**: Scroll position restores correctly (fixed in v877)

**Root Cause**:
- Editor wrapped in `urwid.Filler(self.editor, valign='top')` at curses_ui.py:1661
- When overlay created in interactive_menu.py, urwid may re-render Filler
- Edit widget cursor position might be at 0, causing scroll to top
- v877 fix preserved base widget, but opening still triggers scroll

**Investigation Needed**:
1. Why does creating overlay trigger scroll in Filler?
2. Does Edit widget cursor position affect Filler scroll on render?
3. Can we save/restore Edit widget scroll position explicitly?

**Possible Solutions**:
1. Save edit_pos before opening menu, restore after
2. Use custom Filler subclass that preserves scroll offset
3. Investigate urwid.Edit `rows` method and viewport hints

## Issue 2: Editor Cursor Stuck at Bottom When Scrolling

**Status**: TODO

**Current Behavior**:
- Down arrow until cursor reaches bottom line of program area
- **Bug**: Cursor gets stuck at bottom, can't see next lines
- Up arrow to scroll up
- **Bug**: Lines move but cursor stays on bottom line of program area
- **Expected**: Cursor should stay in middle ~50% of viewport (like vim)

**Root Cause**:
- Editor uses raw `urwid.Edit` widget (multiline, no ListBox)
- Wrapped in `Filler` with `valign='top'` (curses_ui.py:1661)
- Filler doesn't automatically adjust viewport when cursor moves
- No mechanism to keep cursor centered in visible area

**Architecture**:
```
TopLeftBox (border)
  └─ Filler(valign='top')
       └─ ProgramEditorWidget (WidgetWrap)
            └─ Pile
                 └─ Edit(multiline=True)
```

**Expected Behavior** (like vim "soft centering"):
- **TRY** to keep cursor in middle 50% of viewport when scrolling
- When cursor moves up/down and there's content, scroll viewport to maintain centering
- When at **top of file**: cursor can move from top line to middle (don't force centering)
- When at **bottom of file**: cursor can move from middle to bottom line (don't force centering)
- User must be able to reach first and last lines with cursor

**Investigation Needed**:
1. Can Edit widget provide viewport management hints?
2. Should we use ListBox instead of Filler?
3. Can we override Edit.render() to adjust Filler scroll?
4. What does Edit.rows() return and how does Filler use it?

**Possible Solutions**:

### Option A: Custom Edit Subclass
Create `ScrollingEdit(urwid.Edit)` that:
- Overrides `keypress()` to detect up/down/pgup/pgdn
- Calculates visible area from `render()` size parameter
- Provides `get_pref_col()` to tell Filler where cursor should be
- Keeps cursor in middle 50% of viewport

### Option B: Replace Filler with Custom Widget
Create `CenteredFiller` widget that:
- Wraps Edit widget
- Tracks cursor line from edit_pos
- Adjusts vertical offset to keep cursor centered
- Handles edge cases (top/bottom of file)

### Option C: Use ListBox Architecture (Major Refactor)
Convert editor to ListBox-based design:
- Each line becomes a separate widget in SimpleFocusListWalker
- ListBox naturally centers focused item
- Better for very large files
- **Downside**: Major architecture change, may break existing features

### Option D: Manual Scroll Management in Filler
On each keypress that moves cursor:
1. Calculate cursor line number from edit_pos
2. Calculate visible lines from Filler size
3. Adjust Filler scroll offset to center cursor
4. May need custom Filler subclass

**Recommended Approach**: Option A (Custom Edit Subclass)
- Least invasive change
- Edit widget already multiline-aware
- Can implement proper vim-style scrolling
- Maintains existing architecture

## Files to Check

- `src/ui/curses_ui.py:1634-1700` - UI layout creation
- `src/ui/curses_ui.py:186-600` - ProgramEditorWidget class
- `src/ui/interactive_menu.py:156-180` - Menu overlay creation

## References

- urwid.Edit documentation: https://urwid.org/reference/widget.html#edit
- urwid.Filler documentation: https://urwid.org/reference/decoration.html#filler
- urwid.ListBox documentation: https://urwid.org/reference/widget.html#listbox

## Related Issues

- v877 fixed menu close restoring scroll position
- This is separate from the scrolling behavior during normal editing
