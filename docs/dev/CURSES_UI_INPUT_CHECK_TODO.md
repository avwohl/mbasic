# Curses UI: Verify INPUT Implementation

## Status: ⏳ TODO - Verification Needed

## Current Implementation

Curses UI uses **inline input** - the correct approach! No dialog boxes.

**Implementation:** `src/iohandler/curses_io.py:111-148`

```python
def input(self, prompt: str = '') -> str:
    """Input text from user via curses prompt."""
    if prompt:
        self.output(prompt, end='')

    # Use curses text input
    if self.output_win:
        try:
            # Enable echo and cursor
            curses.echo()
            curses.curs_set(1)

            # Get input
            input_bytes = self.output_win.getstr()
            result = input_bytes.decode('utf-8', errors='replace')

            # Disable echo and cursor
            curses.noecho()
            curses.curs_set(0)

            # Add newline to output
            self.output('\n', end='')

            return result
        except curses.error:
            curses.noecho()
            curses.curs_set(0)
            return ''
    else:
        return ''
```

## What It Does

1. Prints prompt to output window
2. Enables echo and cursor
3. Uses `output_win.getstr()` to get input **inline in the output window**
4. User can see all previous output while typing
5. Disables echo/cursor after input
6. Returns user input

## This is Good!

✅ No dialog boxes
✅ Inline input in output window
✅ Can see all previous text
✅ Perfect for games with narrative before INPUT

## Task

**Verify this actually works correctly:**

1. Test curses UI with a BASIC program that uses INPUT
2. Verify user can see previous output while typing
3. Verify cursor appears at correct position
4. Verify input echo works properly
5. Check for any edge cases or bugs

**Test Program:**
```basic
10 PRINT "Welcome to the Adventure Game!"
20 PRINT "You are standing at a crossroads."
21 PRINT "To the north is a dark forest."
22 PRINT "To the south is a sunny meadow."
23 PRINT "To the east is a mysterious cave."
24 PRINT "To the west is a babbling brook."
30 PRINT ""
40 INPUT "Which direction do you go (N/S/E/W)"; D$
50 PRINT "You chose: "; D$
60 END
```

## Priority

**LOW** - Curses likely already works correctly, just needs verification

## Notes

- Curses uses the RIGHT approach (inline)
- TK and Web should be updated to match curses pattern
- This is the model for how INPUT should work across all UIs

## Related

- `docs/dev/TK_UI_INPUT_DIALOG_TODO.md` - TK needs to be fixed to match curses
- `docs/dev/WEB_UI_INPUT_UX_TODO.md` - Web needs to be fixed to match curses
