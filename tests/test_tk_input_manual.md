# Manual Test: TK UI Inline INPUT

## Test Program

File: `tests/test_curses_input.bas`

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

## Test Steps

1. Launch TK UI:
   ```bash
   python3 mbasic --backend tk
   ```

2. Load the test program using File > Open, or type lines manually

3. Click Run > Run Program (or Ctrl+R)

4. **Expected Behavior:**
   - Program prints narrative text to output pane
   - When INPUT statement is reached, an input field appears below the output pane
   - Input field shows prompt: "Which direction do you go (N/S/E/W)"
   - User can see all previous output text while typing input
   - User types answer (e.g., "N") and presses Enter or clicks Submit
   - Input field disappears
   - Program continues and prints "You chose: N"

5. **Previous Behavior (with dialog):**
   - Modal dialog would pop up blocking view of narrative text
   - User couldn't read the game text while INPUT dialog was open
   - Poor UX for games with lots of text before INPUT

## Success Criteria

- ✅ No modal dialog appears
- ✅ Inline input field appears below output pane
- ✅ All previous output remains visible while typing
- ✅ Input field disappears after submission
- ✅ Program execution continues normally
- ✅ Same behavior for games with multiple INPUT statements

## Implementation Details

**Changes made:**
- Added INPUT row widgets to TkBackend: `input_row`, `input_label`, `input_entry`, `input_submit_btn`, `input_queue`
- INPUT row is hidden by default (not packed)
- Added `_show_input_row()` to display INPUT prompt and entry
- Added `_hide_input_row()` to hide INPUT row after submission
- Added `_submit_input()` to handle Enter key and Submit button
- Modified `TkIOHandler.input()` to use inline input instead of `simpledialog.askstring()`
- Uses `queue.Queue()` for thread-safe coordination between UI and interpreter
- Fallback to dialog if backend not available (backwards compatibility)

**Files modified:**
- `src/ui/tk_ui.py` (~100 lines changed)

## Notes

This matches the curses UI's inline input approach, which is the correct UX pattern for games and programs with narrative text before INPUT statements.
