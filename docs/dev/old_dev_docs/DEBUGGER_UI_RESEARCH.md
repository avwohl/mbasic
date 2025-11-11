# Debugger UI Research - Common Controls

## Standard Debugger Controls

### Primary Actions
1. **Continue/Run** (F5) - Resume execution until next breakpoint
2. **Pause/Break** (Ctrl+Break) - Interrupt running program
3. **Stop** (Shift+F5) - Terminate execution
4. **Restart** (Ctrl+Shift+F5) - Stop and restart from beginning

### Stepping Commands
1. **Step Into** (F11) - Execute next statement, enter functions/subroutines
2. **Step Over** (F10) - Execute next statement, skip over function calls
3. **Step Out** (Shift+F11) - Execute until return from current function
4. **Step** (F8) - Generic step (line or statement level)

### Breakpoints
1. **Toggle Breakpoint** (F9) - Set/clear breakpoint at current line
2. **Conditional Breakpoint** - Break when condition is true
3. **Clear All Breakpoints** - Remove all breakpoints
4. **Disable/Enable Breakpoint** - Temporarily disable without removing

### View Controls
1. **Variables/Watch** - View variable values
2. **Call Stack** - View execution stack
3. **Breakpoints List** - Manage all breakpoints
4. **Output/Console** - View program output

## MBASIC Context - Our Implementation

### What We Have
- Breakpoints (line-level)
- Continue (run)
- Stop
- Step (currently ambiguous - line or statement?)
- Variables window
- Call stack window
- Output pane

### BASIC-Specific Considerations

#### No Functions/Subroutines in MBASIC
- BASIC uses GOSUB/RETURN, not function calls
- "Step Into" vs "Step Over" less relevant
- Could mean: Step Into GOSUB vs Step Over GOSUB

#### Multi-Statement Lines
- BASIC allows multiple statements per line: `100 A=1: B=2: C=3`
- Need to decide: step by line or by statement?

#### FOR Loops
- `FOR I=1 TO 10: PRINT I: NEXT I` is one line, multiple statements
- Step Over: Execute entire loop
- Step Into: Step through each iteration/statement

### Proposed Control Scheme

#### Stepping Modes
1. **Step Line** (F10) - Execute all statements on current line, pause at next line
2. **Step Statement** (F11) - Execute one statement, pause (even if same line)
3. **Step Over** (Shift+F10) - Execute current structure (FOR loop, GOSUB) completely
4. **Continue** (F5) - Run until breakpoint or end

#### Button Layout (Toolbar)
```
[New] [Open] [Save] | [Run] [Pause] [Stop] | [Step Line] [Step Stmt] | [Continue] | [Breakpoint] | [Variables] [Stack] | [List] [New Prog] [Clear Out]
```

#### Shortened Names for Buttons
- "Step Line" or "Line" (Step by line)
- "Step Stmt" or "Stmt" (Step by statement)
- "Continue" or "Cont" (Resume)
- "Stop" (Terminate)
- "Run" (Start/restart)

### Implementation Mapping

#### Current MBASIC Interpreter
```python
tick(mode='run', max_statements=100)          # Continue
tick(mode='step_line', max_statements=1)      # Step Line (NEW - not yet implemented)
tick(mode='step_statement', max_statements=1) # Step Statement (EXISTS)
```

#### Missing: Step Line Mode
Need to add to interpreter:
```python
if mode == 'step_line':
    # Execute all statements on current line, then pause
    # Currently, step_statement pauses after each statement
    # step_line should execute until line changes
```

#### Step Over (Advanced)
For step over, need to track:
- If on FOR, execute until corresponding NEXT
- If on WHILE, execute until corresponding WEND
- If on GOSUB, execute until RETURN
- Otherwise, same as step_line

### UI Elements Needed

#### Toolbar Buttons (Left to Right)
1. **File Group**: New, Open, Save
2. **Execution Group**: Run, Pause, Stop
3. **Stepping Group**: Step Line, Step Stmt
4. **Control Group**: Continue
5. **Debug Group**: Breakpoint (toggle current line)
6. **View Group**: Variables, Stack
7. **Utility Group**: List, New Prog, Clear Out

#### Keyboard Shortcuts
- F5: Run/Continue
- F8: Pause
- Shift+F5: Stop
- F10: Step Line
- F11: Step Statement
- F9: Toggle Breakpoint
- Ctrl+W: Variables window
- Ctrl+K: Stack window

### Immediate Changes for Tk UI

1. **Add Buttons**:
   - "New Prog" - Clear program (NEW command)
   - "Step Line" - Step by line
   - "Step Stmt" - Step by statement
   - Keep "Clear Output"

2. **Reorganize Toolbar**:
   ```
   [New][Open][Save] | [Run][Stop] | [Step][Stmt] | [Cont] | [List][New Prog][Clear Out]
   ```

3. **Rename for Space**:
   - "Step" instead of "Step Line"
   - "Stmt" instead of "Step Statement"
   - "Cont" instead of "Continue"
   - "New Prog" or "Clear" instead of "Remove List"

4. **Menu Structure** (already exists, verify):
   - Run > Run Program
   - Run > Pause
   - Run > Stop
   - Run > Step Line
   - Run > Step Statement
   - Run > Continue

## Visual Studio Code Debugger Reference

```
[Continue F5] [Step Over F10] [Step Into F11] [Step Out Shift+F11] [Restart Ctrl+Shift+F5] [Stop Shift+F5]
```

## GDB/LLDB Reference

Commands:
- `run` (r) - Start execution
- `continue` (c) - Resume execution
- `step` (s) - Step into (line level)
- `next` (n) - Step over (line level)
- `finish` - Step out (until function returns)
- `break` (b) - Set breakpoint
- `print` (p) - Print variable value
- `backtrace` (bt) - Show call stack

## Python Debugger (pdb) Reference

Commands:
- `continue` (c) - Continue until breakpoint
- `step` (s) - Step into
- `next` (n) - Step over
- `return` (r) - Step out
- `list` (l) - List source code
- `break` (b) - Set breakpoint
- `print` (p) - Evaluate expression

## Recommendations

### Phase 1: Immediate (Simple Enhancements)
1. Add "New Prog" button (clears program)
2. Keep "Clear Output" button
3. Add "Step" button (step_statement mode)
4. Rename existing step to be clearer

### Phase 2: Enhanced Stepping
1. Implement step_line mode in interpreter
2. Add "Step Line" and "Step Stmt" buttons
3. Update menu with both options
4. Document difference in help

### Phase 3: Advanced (Future)
1. Step Over (loop-aware, GOSUB-aware)
2. Run to Cursor
3. Conditional breakpoints
4. Watch expressions
