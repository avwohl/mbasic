# Curses UI Menu Navigation White Background Bug

## Issue
When navigating the interactive menu with right/left arrows (e.g., from File to Edit), the entire screen background turns white behind the menu dropdown.

## Current Behavior
1. Press Ctrl+U to open File menu - works correctly, black background
2. Press right arrow to navigate to Edit menu
3. Edit menu appears correctly, BUT the entire screen behind it turns white
4. The menu dropdown itself has correct colors, but the rest of the UI (editor, output, etc.) all have white background

## Expected Behavior
The background should remain black when navigating between menus. Only the dropdown menu should change, the rest of the UI should be unaffected.

## Technical Details
- Location: `src/ui/curses_ui.py` `_activate_menu()` method
- Location: `src/ui/interactive_menu.py` `_show_dropdown()` method
- When 'refresh' result is returned from `handle_key()`, we:
  1. Restore main_widget
  2. Call `draw_screen()` to clear
  3. Create new overlay with `_show_dropdown(base_widget=main_widget)`
  4. Set `self.loop.widget = new_overlay`

## Attempted Fixes
- ✗ Passing `base_widget=main_widget` to prevent overlay stacking
- ✗ Calling `draw_screen()` before showing new overlay
- ✗ Wrapping dropdown in AttrMap with 'body' style
- ✗ Adding min_width/min_height to Overlay

## Possible Causes
- urwid Overlay rendering issue with terminal color support
- AttrMap palette inheritance problem
- Terminal-specific rendering bug (only happens on user's terminal, not in pexpect tests)

## Workaround
Menu still functions correctly despite white background. Can close menu with ESC or by selecting an item.

## Status
Not fixed - low priority cosmetic issue
