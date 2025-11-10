# Web UI Debugging Guide

The Web UI provides debugging tools for BASIC program development with visual feedback and interactive controls.

## Overview

The Web UI debugger currently offers:
- Basic breakpoint management (via Run menu)
- Step-by-step execution
- Basic variable inspection (via Debug menu)
- Visual indicators in editor

## Setting Breakpoints

### Currently Implemented

1. Use **Run → Toggle Breakpoint** menu option
2. Enter the line number when prompted
3. A visual indicator appears in the editor
4. Use **Run → Clear All Breakpoints** to remove all

### Breakpoint Indicators

- Visual markers show where breakpoints are set
- Current execution line is highlighted during debugging

### Managing Breakpoints

**Current capabilities:**
- Toggle breakpoint via Run menu
- Clear all breakpoints via Run menu
- Breakpoints persist within the current session

**Note:** Advanced features like clicking line numbers to set breakpoints and a dedicated breakpoint panel are planned for future releases but not yet implemented.

## Starting Debug Session

### Debug Mode

1. **Set breakpoints** where needed (via Run menu)
2. Use **Run → Run Program** or press `{{kbd:run:web}}` to start
3. Program runs until first breakpoint
4. Use **Run → Continue** or `{{kbd:continue:web}}` to continue
5. Use **Run → Stop** or `{{kbd:stop:web}}` to stop

### Debug Controls

**Currently implemented:**

- **Run ({{kbd:run:web}})** - Start program from beginning
- **Continue ({{kbd:continue:web}})** - Run to next breakpoint
- **Step ({{kbd:step:web}})** - Step to next line
- **Stop ({{kbd:stop:web}})** - End execution

**Note:** The Web UI uses {{kbd:step:web}} for stepping. Statement-level stepping is not yet implemented.

## Variable Inspector

**Implementation Status:** Basic variable viewing via Debug menu is currently available. The detailed variable inspector panels, watch expressions, and interactive editing features described below are **planned for future releases** and not yet implemented.

### Variables Panel (Planned)

The following features are planned for future implementation and would be located in right sidebar during debugging:

```
Variables
├─ Scalars
│  ├─ A = 42 (Integer)
│  ├─ B$ = "Hello" (String)
│  └─ X! = 3.14 (Single)
├─ Arrays
│  ├─ ARR(10) = [1, 2, 3, ...] (Integer Array)
│  └─ NAMES$(5) = ["Alice", "Bob", ...] (String Array)
└─ System
   ├─ ERL = 100 (Error Line)
   └─ ERR = 0 (Error Code)
```

### Features (Planned)

**Variable Display (Planned):**
- Name, value, and type shown
- Arrays show dimensions and elements
- Strings shown with quotes
- Numbers formatted appropriately

**Interactive Editing (Planned):**
1. **Double-click** any variable value
2. Edit dialog appears
3. Enter new value
4. Press Enter to apply
5. Press Esc to cancel

**Filtering (Planned):**
- Search box to find variables
- Filter by type (scalar/array/string)
- Show only modified variables
- Hide system variables

### Watch Expressions (Planned)

Planned feature to add custom expressions to monitor:

1. Click **Add Watch** button
2. Enter expression (e.g., `A + B`, `LEN(S$)`)
3. Expression evaluates at each break
4. Remove with X button

## Call Stack

**Implementation Status:** Basic call stack viewing via Run → Show Stack menu is currently available. It shows the current execution stack in a popup dialog. The advanced stack panel features described below are planned for future releases.

### Stack Viewing (Current)

Use **Run → Show Stack** to view the current execution stack in a popup dialog showing:
- GOSUB call chain
- FOR loop contexts
- Line number information

### Advanced Stack Panel (Planned)

Planned enhanced features that would show execution path in a dedicated panel:

```
Call Stack
├─ Line 150 (current)
├─ GOSUB from Line 50
├─ GOSUB from Line 20
└─ Main Program
```

**Features (Planned):**
- Click to view source location
- Shows line numbers
- Indicates subroutine calls
- Displays FOR loop contexts

### FOR Loop Stack (Planned)

```
FOR Loops
├─ I = 3 of 10 (Line 100)
└─ J = 5 of 5 (Line 120)
```

Shows:
- Loop variable name
- Current value
- Limit value
- Source line

## Execution Flow

**Note:** The execution flow features described below are planned for future releases.

### Current Line Highlighting (Planned)

- **Yellow highlight** - Next line to execute
- **Green highlight** - Just executed
- **Gray highlight** - Skipped line (IF/THEN)

### Execution Trace (Planned)

Enable trace mode to see:
```
[10] PRINT "Start"
[20] A = 10
[30] B = 20
[40] IF A > B THEN 60
[50] PRINT "A <= B"
[60] END
```

### Flow Visualization (Planned)

- Arrows show jump targets
- GOSUB/RETURN paths highlighted
- Loop boundaries marked
- IF/THEN branches shown

## Advanced Debugging (Planned Features)

**Note:** The following features are planned for future releases but not yet implemented:

### Logpoints (Future)

Non-breaking points that will log values:
- Log variable values without stopping
- Custom log messages
- Trace execution flow

### Data Breakpoints (Future)

Will break when variable changes:
- Monitor specific variables
- Break on value changes
- Track variable access

### Debug Console (Future)

Will provide interactive debugging console:
- Direct BASIC statement execution
- Variable inspection and modification
- Debug command support

### Performance Profiling (Future)

Will provide timing and performance data:
- Line execution counts
- Performance hotspot identification
- Memory usage tracking

## Debug Settings

**Note:** The debug settings described below are planned for future releases. See [Settings](settings.md) for currently available settings.

### Options Menu (Planned)

**Display Options:**
- Show line numbers
- Show execution counts
- Highlight current line
- Show variable changes

**Behavior Options:**
- Break on error
- Break on warning
- Stop at END
- Auto-open debugger

**Performance:**
- Execution speed (slow/normal/fast)
- Update frequency
- Trace verbosity
- History size

## Debugging Workflows

### Finding Logic Errors

1. Set breakpoint at suspicious code
2. Run in debug mode
3. Inspect variables before/after
4. Step through logic
5. Identify incorrect values

### Debugging Loops

```basic
10 FOR I = 1 TO 10
20   PRINT I
30   A = A + I
40 NEXT I
```

1. Set breakpoint at line 30
2. Watch variables I and A
3. Continue through iterations
4. Verify accumulation

### Debugging Subroutines

```basic
100 GOSUB 200
110 PRINT "Result:"; R
120 END
200 REM Calculate
210 R = X * Y
220 RETURN
```

1. Set breakpoints at 200 and 210
2. Check input values (X, Y)
3. Step through calculation
4. Verify return value (R)

### Debugging Input/Output

```basic
10 INPUT "Enter value"; V
20 IF V < 0 THEN GOTO 100
30 PRINT "Positive"
40 END
100 PRINT "Negative"
```

1. Set breakpoints at lines 20 and 100
2. Test with various inputs
3. Verify branch logic
4. Check edge cases (0)

## Keyboard Shortcuts

**Currently Implemented:**
- `{{kbd:run:web}}` - Run program from beginning
- `{{kbd:continue:web}}` - Continue to next breakpoint
- `{{kbd:step:web}}` - Step to next line
- `{{kbd:stop:web}}` - Stop execution

**Planned for Future Releases:**
- Statement-level stepping (execute one statement at a time)
- Navigation shortcuts for debugger panels
- Variable inspector shortcuts

**Note:** {{kbd:toggle_breakpoint:web}} is implemented but currently available via menu only (not yet bound to keyboard).

## Tips and Best Practices

1. **Start Simple:** Set one breakpoint first
2. **Use Watch:** Monitor key variables
3. **Step Sparingly:** Use continue when possible
4. **Check Stack:** Understand execution path
5. **Edit Variables:** Test different values
6. **Save State:** Export variables for analysis

## Troubleshooting

### Debugger Not Stopping
- Verify breakpoints are active (red)
- Check line has code (not blank/comment)
- Ensure program reaches that line
- Clear and reset breakpoints

### Variables Not Updating
- Check update frequency setting
- Verify in debug mode
- Refresh browser if stuck
- Check for JavaScript errors

### Performance Issues
- Reduce trace verbosity
- Limit watch expressions
- Clear output panel
- Disable execution counting

## Integration with Browser Tools

**Note:** The browser integration features described below are planned for future releases.

### Browser DevTools (Standard Browser Features)

Press `F12` to open browser tools (standard browser shortcut):

**Console Tab:**
- View debug output
- JavaScript errors
- Performance warnings

**Network Tab:**
- Monitor server communication
- Check WebSocket messages

**Application Tab:**
- Inspect localStorage
- View session storage
- Check cookies

### Browser Console Commands (Planned)

```javascript
// These commands are planned for future releases:
// Get current program
mbasic.getProgram()

// Set variable value
mbasic.setVariable('A', 100)

// Get all variables
mbasic.getVariables()

// Export debug state
mbasic.exportDebugState()
```

## See Also

- [Getting Started](getting-started.md) - Web UI basics
- [Keyboard Shortcuts](../../../user/keyboard-shortcuts.md) - Complete reference
- [Features](features.md) - All Web UI capabilities
- [Variable Types](../../common/language/variables.md) - BASIC variables