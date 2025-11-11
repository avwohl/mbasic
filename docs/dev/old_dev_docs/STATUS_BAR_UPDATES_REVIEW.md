# Status Bar Updates Review

All 70 locations where `status_bar.set_text()` is called in `src/ui/curses_ui.py`.

## Issue
Some status bar updates happen during program execution and overwrite the "MBASIC - ^F help..." status line. Since output already goes to the output window, these messages should not overwrite the status bar.

## Program Execution/Control (REVIEW THESE)

These happen during program execution and may inappropriately overwrite the status bar:

1. **Line 2066**: `"No program running"` - Stop command when nothing running
2. **Line 2075**: `"Continuing execution..."` - Continue (Ctrl+G)
3. **Line 2080**: `"Not paused"` - Continue when not paused
4. **Line 2082**: `"Continue error: {e}"` - Continue error
5. **Line 2104**: `"Stepping..."` - Step statement (Ctrl+T)
6. **Line 2140**: `"Paused at {pc_display} - Ctrl+T=Step, Ctrl+G=Continue, Ctrl+X=Stop"` - Step paused
7. **Line 2149**: `"Error during step"` - Step error
8. **Line 2156**: `"Program completed"` - Step finished
9. **Line 2170**: `"Step error: {e}"` - Step exception
10. **Line 2192**: `"Stepping line..."` - Step line (Ctrl+K)
11. **Line 2223**: `"Paused at {pc_display} - Ctrl+T=Step, Ctrl+G=Continue, Ctrl+X=Stop"` - Step line paused
12. **Line 2231**: `"Error during step"` - Step line error
13. **Line 2237**: `"Program completed"` - Step line finished
14. **Line 2251**: `"Step line error: {e}"` - Step line exception
15. **Line 2256**: `"No program running"` - Stop when nothing running (duplicate)
16. **Line 2265**: `"Program stopped - Ready"` - Stop success (Ctrl+X)
17. **Line 2268**: `"Stop error: {e}"` - Stop exception
18. **Line 3068**: `"No program running"` - Variable inspection when not running
19. **Line 3436**: `"Parse error - Fix and try again"` - Runtime parse error
20. **Line 3456**: `'Ready'` - After execution completes
21. **Line 3470**: `"Error"` - Runtime error
22. **Line 3494**: `"Startup error - Check program"` - Execution start error
23. **Line 3511**: `"Running program..."` - Program starting (Ctrl+R)
24. **Line 3542**: `"Internal error - See output"` - ✅ Already says "See output"
25. **Line 3591**: `"Error - ^F help  ^U menu"` - Runtime error
26. **Line 3611**: `"Paused at line {state.current_line} - Ctrl+T=Step, Ctrl+G=Continue, Ctrl+X=Stop"` - Paused at breakpoint
27. **Line 3644**: `"Error - ^F help  ^U menu"` - Runtime error (duplicate)
28. **Line 3674**: `"Execution error - See output"` - ✅ Already says "See output"
29. **Line 4387**: `"Running program..."` - Program starting (duplicate?)

### Recommendation for Execution Messages
Most of these should either:
- Not update status bar at all (output goes to output window)
- Or send to output window instead of status bar
- Or restore the default status bar text after showing briefly

## Editor Operations (SAFE)

These are normal editor operations - OK to update status bar:

30. **Line 2302**: `"No line number to delete"` - Delete line (Ctrl+D)
31. **Line 2340**: `"Deleted line {line_number}"` - Delete line success
32. **Line 2365**: `"No current line"` - Insert line when no context
33. **Line 2372**: `"Current line has no line number"` - Insert line error
34. **Line 2377**: `"Current line has no line number"` - Insert line error (duplicate)
35. **Line 2390**: `"No program lines found"` - Insert line when empty
36. **Line 2411**: `"No room before first line. Use RENUM to make space."` - Insert line collision
37. **Line 2466**: `"Inserted line {insert_num}"` - Insert line success (Ctrl+J)

## Renumbering (SAFE)

38. **Line 2487**: `"No lines to renumber"` - Renumber (Ctrl+E) when empty
39. **Line 2500**: `"Renumber cancelled"` - User cancelled renumber
40. **Line 2508**: `"Invalid start number"` - Renumber validation error
41. **Line 2521**: `"Renumber cancelled"` - User cancelled increment prompt
42. **Line 2529**: `"Invalid increment"` - Renumber validation error
43. **Line 2578**: `"Renumbered {len(valid_lines)} lines from {start} by {increment}"` - Renumber success

## Breakpoints (SAFE)

44. **Line 2609**: `"Breakpoint removed from line {line_number}"` - Toggle breakpoint (Ctrl+B)
45. **Line 2612**: `"Breakpoint set on line {line_number}"` - Toggle breakpoint
46. **Line 2639**: `"No breakpoints to clear"` - Clear all breakpoints when none
47. **Line 2645**: `"Cleared {count} breakpoint(s)"` - Clear all breakpoints success

## Help/UI (SAFE)

48. **Line 2665**: `"Error: Help files not found - {e}"` - Help (Ctrl+F) error
49. **Line 3325**: `"Output maximized - ^O to restore"` - Maximize output toggle
50. **Line 3333**: `STATUS_BAR_SHORTCUTS` - Restore default after maximize

## Variables Window (SAFE)

51. **Line 3042**: `"Sorting variables by: {mode_label} {arrow}"` - Variable sort mode
52. **Line 3057**: `"Sort direction: {direction}"` - Variable sort direction
53. **Line 3075**: `"No variable selected"` - Edit variable when none selected
54. **Line 3078**: `"No variable selected"` - Edit variable when none selected (duplicate)
55. **Line 3090**: `"Cannot parse variable"` - Edit variable parse error
56. **Line 3133**: `"Error: Expected {len(dimensions)} subscripts, got {len(subscripts)}"` - Array subscript error
57. **Line 3140**: `"Error: Subscript {i} out of bounds: {sub} not in [0, {dimensions[i]}]"` - Array bounds error
58. **Line 3153**: `"Invalid subscripts (must be integers)"` - Array subscript type error
59. **Line 3156**: `"Error: {e}"` - Array edit error
60. **Line 3175**: `"Invalid value for type {type_suffix}"` - Array value type error
61. **Line 3189**: `"{variable_name}({subscripts_str}) = {new_value}"` - Array edit success
62. **Line 3192**: `"Error: {e}"` - Array edit exception
63. **Line 3214**: `"Invalid value for type {type_suffix}"` - Variable value type error
64. **Line 3228**: `"{variable_name} = {new_value}"` - Variable edit success
65. **Line 3231**: `"Error: {e}"` - Variable edit exception
66. **Line 3254**: `"Filter set: '{self.variables_filter_text}'"` - Variable filter set
67. **Line 3256**: `"Filter cleared"` - Variable filter cleared (empty)
68. **Line 3265**: `"Filter cancelled"` - Variable filter cancelled (ESC)
69. **Line 3307**: `"Filter cleared"` - Variable filter cleared (explicit)

## Output Operations (SAFE)

70. **Line 2052**: `"Output cleared"` - Clear output command

## Syntax Errors (SAFE)

71. **Line 2059**: `"{base_message} - {error_count} syntax error{plural} in program"` - Show syntax errors
72. **Line 2061**: `"{base_message} - ^F help  ^U menu"` - No syntax errors

## Summary

**Total**: 72 status bar updates

**Need Review**: 29 Program Execution/Control messages (items 1-29)
- These happen during program execution
- Output already goes to output window
- Should NOT overwrite the "MBASIC - ^F help..." status line
- Consider: Remove status bar updates, send to output window instead, or restore default after brief display

**Safe**: 43 Editor/Debug/UI operations (items 30-72)
- Normal user actions that should provide feedback in status bar
- OK to keep as-is
