# Variable Management (Curses UI)

The Curses UI provides a visual variable inspector window for viewing and managing variables during program execution and debugging.

## Opening the Variables Window

### Keyboard Shortcut
Press `{{kbd:toggle_variables:curses}}` to open the variables window.

### Window Layout
```
┌─── Variables ───────────────────────────┐
│ Name    Type      Value                 │
│ ─────────────────────────────────────── │
│ A       Integer   42                    │
│ B$      String    "Hello World"         │
│ ARR()   Array     Integer[10]           │
│ X!      Single    3.14159               │
│ Total#  Double    1234.56789            │
│                                         │
│ [Tab] Switch  [↑↓] Navigate  [Esc] Close│
└─────────────────────────────────────────┘
```

## Viewing Variables

### Navigation
- **Arrow Keys**: Move between variables
- **Page Up/Down**: Scroll through long lists
- **Home/End**: Jump to first/last variable

### Display Information
Each variable shows:
- **Name**: Variable identifier
- **Type**: Integer, String, Single, Double, Array
- **Value**: Current value or array info

### Array Inspection
Arrays show:
- Type and dimensions: `Integer[10]` or `String[5,5]`
- Element count
- Cannot expand to show individual elements (limitation)

## Limitations

### Variable Editing Not Available
⚠️ **Not Implemented**: You cannot edit variable values directly in the variables window.

The variables window is read-only. To modify variables, use immediate mode:

1. Close variables window (Esc)
2. Stop program if running ({{kbd:continue:curses}})
3. Use immediate mode to modify:
   ```
   A = 100
   B$ = "New Value"
   ```
4. Continue program or re-run

The variables window provides:
- View all variables
- See current values
- Monitor during execution
- Update display in real-time

## Filtering and Searching

### Search Function
1. In variables window, press `/` to search
2. Type variable name or partial match
3. Press Enter to find
4. Press `n` for next match
5. Press `N` for previous match

### Filter Options
Press `f` to cycle through filters:
- **All**: Show all variables
- **Scalars**: Hide arrays
- **Arrays**: Show only arrays
- **Modified**: Show recently changed

## Sorting Options

Press `s` to cycle through sort orders:
- **Accessed**: Most recently accessed (read or written) - shown first (default)
- **Written**: Most recently written to - shown first
- **Read**: Most recently read from - shown first
- **Name**: Alphabetical by variable name

Press `d` to toggle sort direction (ascending/descending).

**Note**: The default sort order is "Accessed" with newest first.

## During Debugging

### Breakpoint Mode
When stopped at a breakpoint:
1. Variables window auto-updates
2. Changed variables highlight briefly
3. Current scope variables shown

### Step Mode
During single-stepping:
- Window updates after each step
- Modified variables flash yellow
- Previous values shown in tooltip

### Real-time Updates
- Variables refresh automatically
- Update frequency: ~100ms during execution
- Immediate update when paused

## Variable Types Display

### Type Indicators
```
Integer    : 42, -100, 32767
String     : "Hello", "Line 1", ""
Single (!) : 3.14159, -0.001, 1.5E10
Double (#) : 3.14159265359, 1.23E-100
Array      : Type[dimensions]
```

### Special Values
```
Empty String  : ""
Zero         : 0
Uninitialized: (not shown until used)
Error        : [ERROR] or [UNDEFINED]
```

## Window Controls

### Resize and Position
- **Ctrl+Arrow**: Move window
- **Alt+Arrow**: Resize window
- **Ctrl+M**: Maximize/restore
- **{{kbd:stop:curses}}**: Close window

### Display Options
- **v**: Toggle value truncation
- **t**: Toggle type display
- **d**: Show decimal/hex toggle
- **w**: Word wrap long strings

## Integration with Editor

### Synchronized Display
- Variables window tracks cursor position
- Shows variables referenced on current line
- Highlights undefined variables

### Quick Navigation
- Double-click variable name (if mouse enabled)
- Jumps to first usage in code
- Shows all references

## Performance Considerations

### Large Programs
With many variables:
- Window may lag slightly
- Use filtering to reduce display
- Disable auto-update if needed (press `u`)

### Arrays
Large arrays:
- Only show dimensions, not contents
- Prevents memory/display issues
- Use PRINT in immediate mode for elements

## Tips and Tricks

1. **Keep window small**: Resize to show only needed variables
2. **Use filters**: Reduce clutter with type filters
3. **Pin window**: Press `p` to keep always on top
4. **Export list**: Press `e` to save variable list to file
5. **Quick close**: Press `Esc` or `q` to close

## Keyboard Reference

| Key | Action |
|-----|--------|
| `{{kbd:toggle_variables:curses}}` | Open/focus variables window |
| `Esc` | Close window |
| `Tab` | Switch between windows |
| `↑↓` | Navigate variables |
| `/` | Search |
| `f` | Filter |
| `s` | Sort |
| `r` | Refresh |
| `u` | Toggle auto-update |
| `e` | Export to file |
| `h` | Help |

## Examples

### Example 1: Monitoring Loop Variables
```basic
10 FOR I = 1 TO 100
20   A = A + I
30   IF I MOD 10 = 0 THEN PRINT I, A
40 NEXT I
```
- Open variables window
- Watch I and A increment
- See accumulator pattern

### Example 2: String Processing
```basic
10 INPUT "Enter text"; T$
20 L = LEN(T$)
30 FOR I = 1 TO L
40   C$ = MID$(T$, I, 1)
50   PRINT C$;
60 NEXT I
```
- Monitor T$, L, I, C$
- Watch character extraction

### Example 3: Array Operations
```basic
10 DIM NUMS(10)
20 FOR I = 1 TO 10
30   NUMS(I) = INT(RND * 100)
40 NEXT I
```
- See NUMS() array declared
- Note dimension: Integer[10]
- Cannot see individual elements in window

## Limitations

### Current Limitations
1. **No inline editing**: Cannot modify values in window
2. **No array expansion**: Cannot view array elements
3. **Limited mouse support**: Depends on terminal

### Planned Enhancements
- Full variable editing
- Array element viewing
- Better mouse integration
- Value history tracking

## Comparison with Other UIs

| Feature | Curses | CLI | Tk | Web |
|---------|--------|-----|-----|-----|
| Visual window | ✅ | ❌ | ✅ | ✅ |
| Edit values | ❌ | ❌ | ✅ | ✅ |
| Filtering | ✅ | ❌ | ✅ | ✅ |
| Sorting | ✅ | ❌ | ✅ | ✅ |
| Real-time | ✅ | ❌ | ✅ | ✅ |

## See Also

- [Keyboard Shortcuts](../../../user/keyboard-shortcuts.md) - All shortcuts
- [Running Programs](running.md) - Running and debugging programs
- [Getting Started](getting-started.md) - Curses UI basics
- [CLI Variables](../cli/variables.md) - CLI comparison