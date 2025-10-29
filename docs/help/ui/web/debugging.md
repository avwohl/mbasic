# Web UI Debugging Guide

The Web UI provides comprehensive debugging tools for BASIC program development with visual feedback and interactive controls.

## Overview

The Web UI debugger offers:
- Visual breakpoint management
- Step-by-step execution
- Real-time variable inspection
- Call stack visualization
- Execution flow tracking
- Interactive variable editing

## Setting Breakpoints

### Click to Set

1. **Click any line number** in the editor
2. A **red dot** appears indicating breakpoint
3. Click again to remove

### Breakpoint Indicators

- 🔴 **Red dot** - Active breakpoint
- 🟡 **Yellow dot** - Disabled breakpoint
- 🟢 **Green arrow** - Current execution line

### Managing Breakpoints

**Right-click line number for menu:**
- Toggle Breakpoint
- Disable/Enable Breakpoint
- Clear All Breakpoints
- Run to This Line

**Breakpoint Panel:**
- View all breakpoints
- Jump to breakpoint location
- Enable/disable individually
- Clear selected or all

## Starting Debug Session

### Debug Mode

1. **Set breakpoints** where needed
2. Click **Debug** button or press `F5`
3. Program runs until first breakpoint
4. Debugger panel activates

### Debug Controls

When paused at breakpoint:

- **Continue (F5)** - Run to next breakpoint
- **Step Over (F10)** - Execute current line
- **Step Into (F11)** - Enter subroutine
- **Step Out (Shift+F11)** - Exit current subroutine
- **Stop (Shift+F5)** - End debug session

## Variable Inspector

### Variables Panel

Located in right sidebar during debugging:

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

### Features

**Variable Display:**
- Name, value, and type shown
- Arrays show dimensions and elements
- Strings shown with quotes
- Numbers formatted appropriately

**Interactive Editing:**
1. **Double-click** any variable value
2. Edit dialog appears
3. Enter new value
4. Press Enter to apply
5. Press Esc to cancel

**Filtering:**
- Search box to find variables
- Filter by type (scalar/array/string)
- Show only modified variables
- Hide system variables

### Watch Expressions

Add custom expressions to monitor:

1. Click **Add Watch** button
2. Enter expression (e.g., `A + B`, `LEN(S$)`)
3. Expression evaluates at each break
4. Remove with X button

## Call Stack

### Stack Panel

Shows execution path:

```
Call Stack
├─ Line 150 (current)
├─ GOSUB from Line 50
├─ GOSUB from Line 20
└─ Main Program
```

**Features:**
- Click to view source location
- Shows line numbers
- Indicates subroutine calls
- Displays FOR loop contexts

### FOR Loop Stack

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

### Current Line Highlighting

- **Yellow highlight** - Next line to execute
- **Green highlight** - Just executed
- **Gray highlight** - Skipped line (IF/THEN)

### Execution Trace

Enable trace mode to see:
```
[10] PRINT "Start"
[20] A = 10
[30] B = 20
[40] IF A > B THEN 60
[50] PRINT "A <= B"
[60] END
```

### Flow Visualization

- Arrows show jump targets
- GOSUB/RETURN paths highlighted
- Loop boundaries marked
- IF/THEN branches shown

## Advanced Debugging

### Conditional Breakpoints

Right-click breakpoint to set condition:

```basic
Break when: A > 100
Break when: B$ = "ERROR"
Break when: I MOD 10 = 0
```

### Logpoints

Non-breaking points that log values:

1. Right-click line number
2. Select "Add Logpoint"
3. Enter message: `"A={A}, B={B}"`
4. Values logged to console

### Data Breakpoints

Break when variable changes:

1. Right-click variable in inspector
2. Select "Break on Change"
3. Program pauses when value modified

## Debug Console

### Using the Console

Bottom panel during debugging:

```
Debug> PRINT A
42
Debug> A = 100
Debug> WATCH B$
B$ = "Hello"
Debug> CONT
```

**Commands:**
- Direct BASIC statements
- Variable assignments
- PRINT expressions
- Debug commands

### Debug Commands

- `WATCH var` - Show variable value
- `WATCH` - Show all variables
- `STACK` - Show call stack
- `BREAK` - List breakpoints
- `CONT` - Continue execution
- `STEP` - Single step

## Performance Profiling

### Timing Information

Enable profiling to see:
- Line execution counts
- Time spent per line
- Hotspot identification
- Call frequency

### Memory Usage

Monitor during debug:
- Variable count
- Array allocations
- String usage
- Stack depth

## Debug Settings

### Options Menu

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

**Debug Control:**
- `F5` - Start/Continue debugging
- `Shift+F5` - Stop debugging
- `F9` - Toggle breakpoint
- `Ctrl+F9` - Clear all breakpoints
- `F10` - Step over
- `F11` - Step into
- `Shift+F11` - Step out

**Navigation:**
- `Ctrl+G` - Go to line
- `Alt+Left` - Go back
- `Alt+Right` - Go forward
- `Ctrl+Shift+F` - Find in files

**Inspector:**
- `Ctrl+Alt+V` - Toggle variables panel
- `Ctrl+Alt+C` - Toggle call stack
- `Ctrl+Alt+W` - Add watch
- `Ctrl+Alt+D` - Toggle debug console

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

### Browser DevTools

Press `F12` to open browser tools:

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

### Browser Console Commands

```javascript
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
- [Keyboard Shortcuts](keyboard-shortcuts.md) - Complete reference
- [Features](features.md) - All Web UI capabilities
- [Variable Types](../../common/language/variables.md) - BASIC variables