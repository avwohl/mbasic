# Immediate Mode Execution for Visual UIs

**Date**: 2025-10-25
**Status**: Design Phase

## Problem Statement

The CLI/traditional BASIC interface has the "Ok" prompt where users can:
- Execute immediate commands: `PRINT X`, `LIST`, `RUN`
- Modify variables while debugging: `X=5`
- Inspect state: `PRINT A$, B, C(5)`
- Test expressions: `? SIN(0.5) * 2`

**Visual UIs (Curses, Tk, Web) currently lack this capability**, which is critical for:
- Interactive debugging
- Variable inspection/modification during breakpoints
- Testing code snippets
- Traditional BASIC workflow

## Design Goals

1. **Feature Parity**: Match CLI immediate mode functionality
2. **Non-Intrusive**: Don't clutter the UI or interfere with editor
3. **Context Aware**: Work with current program state (runtime context)
4. **Discoverable**: Clear how to access and use
5. **Efficient**: Quick access via keyboard shortcut

## Proposed Solution

### Option 1: Dedicated Immediate Mode Window (RECOMMENDED)

Add a third panel to all visual UIs:

```
┌─────────────────────────────────────────┐
│ Editor (Program Code)                   │
│ 10 PRINT "HELLO"                        │
│ 20 FOR I = 1 TO 10                      │
│ 30   PRINT I                            │
├─────────────────────────────────────────┤
│ Output (Program Output)                 │
│ HELLO                                   │
│ 1                                       │
│ 2                                       │
├─────────────────────────────────────────┤
│ Immediate (Ctrl+I to focus)             │
│ Ok                                      │
│ > PRINT I                               │ ← User types here
│ 2                                       │ ← Immediate result
│ Ok                                      │
│ > I = 5                                 │
│ Ok                                      │
│ >█                                      │ ← Cursor
└─────────────────────────────────────────┘
```

**Advantages**:
- Always visible (no mode switching)
- Clear separation of concerns
- History visible in panel
- Matches traditional "Ok" prompt experience

**Layout Details**:

**Curses UI**:
```
┌──────────────────────────────────┐
│ [E]ditor | [O]utput | [I]mmediate│ ← Tab bar
├──────────────────────────────────┤
│                                  │
│        Active Panel              │
│                                  │
└──────────────────────────────────┘
```
- Vertical split (40% editor, 30% output, 30% immediate)
- OR: Tabbed panels with Ctrl+E/O/I to switch
- Immediate panel shows scrollable history

**Tk UI**:
```
┌─────────────────────────────────────┐
│ Editor (top 40%)                    │
├─────────────────────────────────────┤
│ Output (middle 30%)                 │
├─────────────────────────────────────┤
│ Immediate (bottom 30%)              │
│ Ok                                  │
│ > PRINT X                           │
│ 42                                  │
│ Ok                                  │
│ > █                                 │
└─────────────────────────────────────┘
```
- Three `tk.Text` widgets in vertical stack
- Bottom panel has input field + history

**Web UI**:
```
┌─────────────────────────────────────┐
│ Editor (NiceGUI textarea)           │
├─────────────────────────────────────┤
│ Output (log area)                   │
├─────────────────────────────────────┤
│ Immediate (chat-like interface)     │
│ Ok                                  │
│ > PRINT A$                          │
│ "Hello"                             │
│ Ok                                  │
│ [________________] [Execute]         │
└─────────────────────────────────────┘
```
- Chat-like interface (like a REPL)
- Input field at bottom
- History scrolls up

### Option 2: Modal Dialog (Not Recommended)

Press Ctrl+I to open immediate mode dialog:

```
┌───────────────────────────────┐
│ Immediate Mode                │
├───────────────────────────────┤
│ History:                      │
│ > PRINT I                     │
│ 2                             │
│ > I = 5                       │
│ Ok                            │
├───────────────────────────────┤
│ Command: [____________]       │
│         [Execute] [Close]     │
└───────────────────────────────┘
```

**Disadvantages**:
- Hides program output
- Modal interruption
- Less discoverable
- Doesn't feel like traditional BASIC

### Option 3: Output Panel Dual-Purpose (Not Recommended)

Make output panel accept input when program stopped:

```
┌─────────────────────────────────┐
│ Output                          │
│ HELLO                           │
│ 1                               │
│ 2                               │
│ Program stopped at line 30      │
│ Ok                              │
│ > █                             │ ← Can type here
└─────────────────────────────────┘
```

**Disadvantages**:
- Confusing (mixing output and input)
- Scrolling issues
- Hard to distinguish what's what

## Recommended Implementation: Option 1

### Architecture

#### 1. Immediate Mode Interpreter Integration

**New Method in Interpreter**:
```python
def execute_immediate(self, command: str) -> tuple[bool, str]:
    """
    Execute an immediate mode command.

    Args:
        command: BASIC statement or expression (no line number)

    Returns:
        (success: bool, output: str)

    Examples:
        "PRINT X"      → (True, "42\n")
        "X = 100"      → (True, "Ok\n")
        "? 2 + 2"      → (True, "4\n")
        "LIST"         → (True, "10 PRINT...\n")
        "SYNTAX ERR"   → (False, "Syntax error\n")
    """
    # Use current runtime context (variables, arrays, etc.)
    # Parse command as immediate statement (no line number)
    # Execute and capture output
    # Return result
```

**Key Points**:
- Uses **current runtime state** (same variables as running program)
- No line number required
- Can execute any statement: `PRINT`, assignment, `LIST`, etc.
- `?` shorthand for `PRINT` works
- Errors don't crash program state

#### 2. Curses UI Implementation

**Layout**:
```python
class ImmediatePanel:
    """Immediate mode execution panel."""

    def __init__(self):
        self.history = []  # List of (command, result) tuples
        self.current_command = ""
        self.cursor_pos = 0

    def handle_input(self, key):
        """Handle keyboard input in immediate panel."""
        if key == '\n':  # Enter
            self.execute_command()
        elif key == curses.KEY_UP:
            self.history_prev()
        elif key == curses.KEY_DOWN:
            self.history_next()
        else:
            self.current_command += key

    def execute_command(self):
        """Execute current command and add to history."""
        if not self.current_command.strip():
            return

        success, output = self.interpreter.execute_immediate(self.current_command)
        self.history.append((self.current_command, output))
        self.current_command = ""
        self.scroll_to_bottom()

    def render(self, window):
        """Render immediate panel."""
        # Show history (scrollable)
        # Show current "Ok" prompt
        # Show current command with cursor
```

**Keybindings**:
- `Ctrl+I` - Focus immediate panel
- `Enter` - Execute command
- `Up/Down` - History navigation
- `Ctrl+L` - Clear immediate panel history

#### 3. Tk UI Implementation

**Layout**:
```python
class ImmediateFrame(tk.Frame):
    """Immediate mode execution frame."""

    def __init__(self, parent, interpreter):
        super().__init__(parent)

        # History display (read-only)
        self.history_text = tk.Text(self, height=10, state='disabled')
        self.history_text.pack(fill='both', expand=True)

        # Input frame
        input_frame = tk.Frame(self)
        input_frame.pack(fill='x')

        tk.Label(input_frame, text="Ok >").pack(side='left')

        self.command_entry = tk.Entry(input_frame)
        self.command_entry.pack(side='left', fill='x', expand=True)
        self.command_entry.bind('<Return>', self.execute_command)
        self.command_entry.bind('<Up>', self.history_prev)
        self.command_entry.bind('<Down>', self.history_next)

        self.history = []
        self.history_index = 0

    def execute_command(self, event=None):
        """Execute command from entry."""
        command = self.command_entry.get().strip()
        if not command:
            return

        # Execute
        success, output = self.interpreter.execute_immediate(command)

        # Add to history display
        self.append_history(f"Ok\n> {command}\n{output}")

        # Save to history
        self.history.append(command)
        self.history_index = len(self.history)

        # Clear input
        self.command_entry.delete(0, tk.END)

    def append_history(self, text):
        """Append text to history display."""
        self.history_text.config(state='normal')
        self.history_text.insert('end', text)
        self.history_text.see('end')
        self.history_text.config(state='disabled')
```

#### 4. Web UI Implementation

**Layout** (NiceGUI):
```python
async def create_immediate_panel(self):
    """Create immediate mode panel for web UI."""

    with ui.card().classes('w-full').style('height: 300px'):
        ui.label('Immediate Mode').classes('text-h6')

        # History area (scrollable log)
        self.immediate_log = ui.log().classes('w-full h-64')

        # Input area
        with ui.row().classes('w-full items-center gap-2'):
            ui.label('Ok >')

            self.immediate_input = ui.input(
                placeholder='Enter BASIC command...',
                on_change=None
            ).classes('flex-grow').on('keydown.enter', self.execute_immediate)

            ui.button('Execute', on_click=self.execute_immediate).props('flat')

async def execute_immediate(self):
    """Execute immediate mode command."""
    command = self.immediate_input.value.strip()
    if not command:
        return

    # Log command
    self.immediate_log.push(f'> {command}')

    # Execute
    success, output = self.interpreter.execute_immediate(command)

    # Log result
    self.immediate_log.push(output.rstrip())
    self.immediate_log.push('Ok')

    # Clear input
    self.immediate_input.value = ''
```

## Execution Context

### When Can Immediate Mode Execute?

**CRITICAL FOR TICK-BASED EXECUTION**: Visual UIs use tick-based execution where the interpreter processes one statement at a time. Immediate mode must ONLY execute when the interpreter is in a safe state.

| Interpreter State | Safe? | Immediate Mode Behavior |
|-------------------|-------|------------------------|
| **'idle'** | ✅ YES | No program loaded - can execute, but no program variables exist |
| **'paused'** | ✅ YES | User hit Ctrl+Q (stop) - can execute, accesses current runtime state |
| **'at_breakpoint'** | ✅ YES | Hit breakpoint - can execute, accesses current runtime state (IDEAL) |
| **'done'** | ✅ YES | Program finished - can execute, runtime state preserved |
| **'error'** | ✅ YES | Program encountered error - can execute, runtime state preserved |
| **'running'** | ❌ NO | Program is executing tick() - **MUST NOT EXECUTE** (will corrupt state) |
| **'waiting_for_input'** | ❌ NO | Program waiting for INPUT - use normal input mechanism instead |

### Implementation Requirements

**All visual UIs MUST**:

1. **Check state before execution**:
   ```python
   if executor.can_execute_immediate():
       success, output = executor.execute(command)
   ```

2. **Disable input when unsafe**:
   - Gray out immediate mode input field
   - Show status: "Immediate mode disabled (program running)"
   - Prevent Enter key from executing

3. **Enable input when safe**:
   - Enable immediate mode input field
   - Show status: "Ok" or "Ready"
   - Allow command execution

4. **Update on state changes**:
   - After every tick() call, check interpreter.state.status
   - Enable/disable immediate panel accordingly

### Tick-Based Execution Workflow

**Example: Curses UI with tick() loop**:

```python
# Main UI loop
while True:
    # Check keyboard input
    key = self.screen.getch()

    if key == ord('r'):  # Run program
        interpreter.start()

    # Execute one tick if program running
    if interpreter.state.status == 'running':
        interpreter.tick()

        # After tick, update immediate panel state
        if executor.can_execute_immediate():
            immediate_panel.enable()
        else:
            immediate_panel.disable()

    # Handle immediate mode input
    if immediate_panel.has_input():
        if executor.can_execute_immediate():
            command = immediate_panel.get_command()
            success, output = executor.execute(command)
            immediate_panel.show_result(output)
        else:
            immediate_panel.show_error("Program is running")
```

**State Transitions**:

```
User presses Run (Ctrl+R):
  interpreter.state.status: 'idle' → 'running'
  immediate_panel: ENABLED → DISABLED

Program hits breakpoint:
  interpreter.state.status: 'running' → 'at_breakpoint'
  immediate_panel: DISABLED → ENABLED
  User can now execute immediate commands

User presses Continue (Ctrl+G):
  interpreter.state.status: 'at_breakpoint' → 'running'
  immediate_panel: ENABLED → DISABLED

Program finishes:
  interpreter.state.status: 'running' → 'done'
  immediate_panel: DISABLED → ENABLED
```

### Use Cases

#### 1. Debugging at Breakpoint

```
Program hits breakpoint at line 30
User presses Ctrl+I (focus immediate panel)

> PRINT I
2
Ok
> PRINT A$
"Hello"
Ok
> I = 10
Ok
>

User presses Ctrl+G (continue) - program continues with I=10
```

#### 2. Inspecting After Stop

```
User stops program with Ctrl+Q

> PRINT X, Y, Z
42    3.14    "test"
Ok
> LIST 100-200
100 FOR I = 1 TO 10
110   PRINT I
120 NEXT I
Ok
>
```

#### 3. Testing Without Running

```
No program running

> ? SIN(0) * 2 + 3
3
Ok
> A$ = "TEST"
Ok
> PRINT LEN(A$)
4
Ok
```

## Implementation Phases

### Phase 1: Interpreter Support
- Add `execute_immediate()` method to Interpreter
- Handle immediate statements (no line number)
- Preserve runtime context
- Capture output
- Handle errors gracefully

### Phase 2: Curses UI
- Add immediate panel (bottom 30% of screen)
- Implement input handling
- History navigation (up/down arrows)
- Scrolling support
- Ctrl+I to focus

### Phase 3: Tk UI
- Add immediate frame (bottom panel)
- tk.Entry for input
- tk.Text for history
- Execute button + Enter key
- History navigation

### Phase 4: Web UI
- Add immediate section below output
- ui.log() for history
- ui.input() for command entry
- Execute button
- History with up/down (if possible in browser)

### Phase 5: Testing & Documentation
- Test all use cases
- Document keybindings
- Add help content
- Create user guide

## User Experience

### Discovery

**Curses UI**:
- Status bar shows: `[E]ditor [O]utput [I]mmediate`
- Ctrl+I focuses immediate panel
- Visible "Ok >" prompt

**Tk UI**:
- Immediate panel always visible at bottom
- Clear label: "Immediate Mode"
- Entry field with placeholder: "Enter command..."

**Web UI**:
- Section labeled "Immediate Mode"
- Input field with placeholder
- Clear "Execute" button

### Workflow

1. **Set breakpoint** on line 50
2. **Run program** (Ctrl+R)
3. **Hit breakpoint** - program pauses
4. **Press Ctrl+I** - focus immediate panel
5. **Type**: `PRINT X`
6. **Press Enter** - see result
7. **Type**: `X = 100`
8. **Press Enter** - modify variable
9. **Press Ctrl+G** - continue execution with modified state

## Edge Cases

### 1. Immediate Command Modifies Program

```
> 10 PRINT "NEW LINE"
Ok
```

**Behavior**: Allowed - modifies the loaded program just like CLI

### 2. Immediate Command Calls GOSUB

```
> GOSUB 1000
Ok
```

**Behavior**: Executes subroutine, returns to immediate mode

### 3. Immediate Command Causes Error

```
> PRINT UNDEFINED_VAR
Type mismatch
Ok
```

**Behavior**: Shows error, doesn't crash, state preserved

### 4. Immediate RUN Command

```
> RUN
```

**Behavior**: Starts program execution from beginning

### 5. Immediate LIST Command

```
> LIST
10 PRINT "HELLO"
20 END
Ok
```

**Behavior**: Lists program in immediate panel history

## Configuration

### Settings (keybindings.json)

```json
{
  "immediate": {
    "focus": "Ctrl+I",
    "clear": "Ctrl+L",
    "execute": "Enter"
  }
}
```

## Future Enhancements

1. **Syntax highlighting** in immediate input
2. **Auto-complete** for variable names
3. **Multi-line immediate** (like Python's `>>>` and `...`)
4. **Save/load immediate history** between sessions
5. **Immediate panel resize** (drag divider)

## Benefits

✅ **Feature parity** with CLI BASIC
✅ **Enhanced debugging** - inspect/modify state at breakpoints
✅ **Interactive exploration** - test code without running programs
✅ **Traditional workflow** - feels like classic BASIC
✅ **Discoverable** - clear UI element, documented keybinding
✅ **Non-intrusive** - doesn't interfere with editor or output

## Summary

Adding an **Immediate Mode panel** to all visual UIs provides essential interactive debugging capabilities missing from the current implementation. The recommended approach is a dedicated third panel with:

- Clear "Ok >" prompt
- Command history
- Execute on Enter
- Ctrl+I to focus
- Full access to runtime state

This matches the traditional BASIC experience while integrating cleanly into modern visual UIs.
