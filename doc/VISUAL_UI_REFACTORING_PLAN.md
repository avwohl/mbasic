# Visual UI Refactoring Plan

**Status**: Phases 1-4 COMPLETE ✅✅✅✅ | Phase 5 DEFERRED
**Last Updated**: 2025-10-24

## Implementation Status

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1** | ✅ COMPLETE | I/O Abstraction and Debugging Support |
| **Phase 2** | ✅ COMPLETE | Program Management |
| **Phase 3** | ✅ COMPLETE | UI Abstraction |
| **Phase 4** | ✅ COMPLETE | Dynamic Backend Loading |
| **Phase 5** | ⏸️ DEFERRED | Mobile/Visual UI Framework Evaluation |

**Progress**: Core refactoring complete! The interpreter is now fully embeddable and extensible.

See detailed progress documents:
- [Phase 1 Progress](PHASE1_IO_ABSTRACTION_PROGRESS.md) - I/O abstraction, IOHandler interface
- [Phase 2 Progress](PHASE2_PROGRAM_MANAGEMENT_PROGRESS.md) - ProgramManager class
- [Phase 3 Progress](PHASE3_UI_ABSTRACTION_PROGRESS.md) - UIBackend interface, CLI/Visual backends
- [Phase 4 Progress](PHASE4_DYNAMIC_LOADING_PROGRESS.md) - Dynamic loading with importlib

## Goal

Refactor mbasic.py to enable embedding the interpreter in a visual UI while keeping the command-line tool functional. The architecture should use dynamic imports (importlib) and allow customizable I/O handlers.

## Current Architecture Analysis

### Current Structure

```
mbasic.py (85 lines)
├── Imports: lexer, parser, runtime, interpreter, interactive
├── run_file() - Loads and executes a BASIC file
├── main() - Entry point, starts InteractiveMode
└── Uses InteractiveMode.start() for REPL

src/interactive.py (1462 lines)
├── InteractiveMode class
├── I/O: Uses input() and print() directly
├── Commands: RUN, LIST, SAVE, LOAD, NEW, DELETE, RENUM, EDIT, AUTO, etc.
└── Immediate mode execution

src/interpreter.py
├── Interpreter class
├── I/O: Uses print() directly for PRINT statements
└── Uses input() for INPUT statements (via basic_builtins.py)

src/basic_builtins.py
└── I/O: input() for INPUT$, INKEY$, LINE INPUT
```

### Current I/O Points

**Output:**
- `print()` used in ~50+ places across interpreter.py, interactive.py
- PRINT statement execution
- Error messages
- DEBUG output
- Command feedback (LIST, SAVE, etc.)

**Input:**
- `input()` used for:
  - Interactive REPL prompt
  - BASIC INPUT statement
  - INPUT$ function
  - LINE INPUT statement
  - INKEY$ (non-blocking keyboard)

### Current Editing Functions (in InteractiveMode)

- `cmd_list()` - List program lines
- `cmd_save()` - Save to file
- `cmd_load()` - Load from file
- `cmd_new()` - Clear program
- `cmd_delete()` - Delete line range
- `cmd_renum()` - Renumber lines
- `cmd_edit()` - Line editor
- `cmd_auto()` - Auto line numbering
- `cmd_merge()` - Merge files
- `cmd_chain()` - Chain to another program

## Proposed Architecture

### Design Principles

1. **Separation of Concerns**
   - Core interpreter logic (execution) - stays in src/
   - I/O abstraction layer - new
   - UI-specific code - separate modules
   - Command/editing layer - refactored

2. **Dynamic Loading**
   - Use importlib to load UI backends dynamically
   - CLI and GUI both implement same interface
   - Selectable via command line or config

3. **I/O Abstraction**
   - All I/O goes through an IOHandler interface
   - Default: ConsoleIOHandler (current behavior)
   - Visual: GUIIOHandler (for visual UI)

4. **Editing Abstraction**
   - Core editing operations (add/delete/renumber lines)
   - UI-specific editors (CLI line editor vs GUI visual editor)

### New Directory Structure

```
mbasic/
├── mbasic.py                   # Main entry point (refactored)
├── src/
│   ├── core/                   # NEW: Core interpreter (no I/O)
│   │   ├── __init__.py
│   │   ├── engine.py           # Refactored interpreter (I/O abstracted)
│   │   ├── lexer.py            # Move from src/
│   │   ├── parser.py           # Move from src/
│   │   ├── runtime.py          # Move from src/
│   │   ├── ast_nodes.py        # Move from src/
│   │   ├── tokens.py           # Move from src/
│   │   └── basic_builtins.py   # Move and refactor
│   │
│   ├── io/                     # NEW: I/O abstraction
│   │   ├── __init__.py
│   │   ├── base.py             # IOHandler interface
│   │   ├── console.py          # ConsoleIOHandler (default)
│   │   └── gui.py              # GUIIOHandler (visual UI)
│   │
│   ├── editing/                # NEW: Editing abstraction
│   │   ├── __init__.py
│   │   ├── base.py             # ProgramEditor interface
│   │   ├── manager.py          # ProgramManager (line storage/AST)
│   │   └── commands.py         # Core editing commands
│   │
│   └── ui/                     # NEW: UI implementations
│       ├── __init__.py
│       ├── base.py             # UIBackend interface
│       ├── cli.py              # CLIBackend (current interactive.py)
│       └── visual.py           # VisualBackend (for GUI)
│
├── backends/                   # NEW: Pluggable UI backends
│   ├── __init__.py
│   ├── cli.py                  # CLI backend module
│   └── visual.py               # Visual UI backend module
│
└── examples/                   # NEW: Usage examples
    ├── embed_cli.py            # Example: CLI embedding
    ├── embed_gui.py            # Example: GUI embedding
    └── custom_io.py            # Example: Custom I/O handler
```

### Core Components

#### 1. IOHandler Interface (src/io/base.py)

```python
class IOHandler:
    """Abstract interface for I/O operations"""

    def output(self, text: str, end: str = '\n') -> None:
        """Output text (like print())"""
        raise NotImplementedError

    def input(self, prompt: str = '') -> str:
        """Input text (like input())"""
        raise NotImplementedError

    def input_line(self, prompt: str = '') -> str:
        """Input a full line (LINE INPUT)"""
        raise NotImplementedError

    def input_char(self, blocking: bool = True) -> str:
        """Input single character (INKEY$, INPUT$)"""
        raise NotImplementedError

    def clear_screen(self) -> None:
        """Clear screen (CLS)"""
        raise NotImplementedError

    def error(self, message: str) -> None:
        """Output error message"""
        raise NotImplementedError

    def debug(self, message: str) -> None:
        """Output debug message (if DEBUG enabled)"""
        raise NotImplementedError
```

#### 2. ProgramManager (src/editing/manager.py)

```python
class ProgramManager:
    """Manages program lines and ASTs (extracted from InteractiveMode)"""

    def __init__(self, def_type_map: dict):
        self.lines: Dict[int, str] = {}        # line_number -> text
        self.line_asts: Dict[int, LineNode] = {}  # line_number -> AST
        self.def_type_map = def_type_map
        self.current_file: Optional[str] = None

    def add_line(self, line_number: int, line_text: str) -> bool:
        """Add or replace a line, returns True if parse succeeded"""
        ...

    def delete_line(self, line_number: int) -> bool:
        """Delete a line"""
        ...

    def delete_range(self, start: int, end: int) -> None:
        """Delete a range of lines"""
        ...

    def get_line(self, line_number: int) -> Optional[str]:
        """Get line text"""
        ...

    def get_lines(self, start: int = None, end: int = None) -> List[Tuple[int, str]]:
        """Get lines in range, sorted"""
        ...

    def renumber(self, new_start: int, old_start: int, increment: int) -> None:
        """Renumber lines"""
        ...

    def clear(self) -> None:
        """Clear all lines"""
        ...

    def save_to_file(self, filename: str) -> None:
        """Save program to file"""
        ...

    def load_from_file(self, filename: str) -> bool:
        """Load program from file, returns True on success"""
        ...

    def get_ast(self) -> ProgramNode:
        """Build ProgramNode from current lines"""
        ...
```

#### 3. InterpreterEngine (src/core/engine.py)

```python
class ExecutionState:
    """Snapshot of current execution state for debugging"""
    current_line: int
    current_statement_index: int
    stopped: bool
    breakpoints: Set[int]

class InterpreterEngine:
    """Core interpreter engine with abstracted I/O and debugging support"""

    def __init__(self, io_handler: IOHandler):
        self.io = io_handler
        self.runtime = None
        self.execution_state = ExecutionState()
        self.step_mode: Optional[str] = None  # None, 'line', 'statement', 'expression'
        self.step_callback: Optional[Callable] = None

    def run_program(self, program: ProgramNode) -> None:
        """Execute a BASIC program"""
        ...

    def execute_line(self, line: LineNode) -> Any:
        """Execute a single line (immediate mode)"""
        ...

    def break_execution(self) -> None:
        """Handle Ctrl+C / BREAK"""
        ...

    def continue_execution(self) -> None:
        """Continue after STOP or Ctrl+C"""
        ...

    # Debugging and Inspection Interface
    def get_variable_table(self) -> Dict[str, Any]:
        """Export all variables with their current values and types

        Returns:
            Dict mapping variable names to their values:
            {
                'A': 42,
                'B$': 'HELLO',
                'C#': 3.14159,
                'D(': [1, 2, 3, 4, 5],  # Array
                'FN_X': <DEF FN object>,  # User-defined function
            }
        """
        if not self.runtime:
            return {}
        return self.runtime.get_all_variables()

    def get_gosub_stack(self) -> List[int]:
        """Export GOSUB call stack

        Returns:
            List of line numbers representing GOSUB return points:
            [100, 500, 1000]  # Called GOSUB at lines 100, 500, 1000
        """
        if not self.runtime:
            return []
        return self.runtime.get_gosub_stack()

    def get_for_loop_stack(self) -> List[Dict[str, Any]]:
        """Export FOR loop stack for debugging

        Returns:
            List of FOR loop contexts:
            [
                {'var': 'I', 'current': 5, 'end': 10, 'step': 1, 'line': 100},
                {'var': 'J', 'current': 2, 'end': 5, 'step': 1, 'line': 150}
            ]
        """
        if not self.runtime:
            return []
        return self.runtime.get_for_loop_stack()

    def get_execution_state(self) -> ExecutionState:
        """Get current execution state for debugging UI"""
        return self.execution_state

    # Stepping and Breakpoint Support
    def set_step_mode(self, mode: str, callback: Callable = None) -> None:
        """Enable stepping mode

        Args:
            mode: 'line', 'statement', or 'expression'
            callback: Optional callback(state) called at each step
        """
        self.step_mode = mode
        self.step_callback = callback

    def clear_step_mode(self) -> None:
        """Disable stepping, run normally"""
        self.step_mode = None
        self.step_callback = None

    def step_line(self) -> None:
        """Execute one line then pause"""
        self.set_step_mode('line')
        self.continue_execution()

    def step_statement(self) -> None:
        """Execute one statement then pause"""
        self.set_step_mode('statement')
        self.continue_execution()

    def step_expression(self) -> None:
        """Step through expression evaluation (enter sub-expressions)"""
        self.set_step_mode('expression')
        self.continue_execution()

    def set_breakpoint(self, line: int) -> None:
        """Set a breakpoint at a line number"""
        self.execution_state.breakpoints.add(line)

    def clear_breakpoint(self, line: int) -> None:
        """Clear a breakpoint"""
        self.execution_state.breakpoints.discard(line)

    def clear_all_breakpoints(self) -> None:
        """Clear all breakpoints"""
        self.execution_state.breakpoints.clear()
```

#### 4. UIBackend Interface (src/ui/base.py)

```python
class UIBackend:
    """Abstract interface for UI backends"""

    def __init__(self, io_handler: IOHandler, program_manager: ProgramManager):
        self.io = io_handler
        self.program = program_manager
        self.engine = InterpreterEngine(io_handler)

    def start(self) -> None:
        """Start the UI"""
        raise NotImplementedError

    def cmd_run(self) -> None:
        """Execute RUN command"""
        ...

    def cmd_list(self, args: str) -> None:
        """Execute LIST command"""
        ...

    # Other commands...

    def execute_immediate(self, statement: str) -> None:
        """Execute immediate mode statement"""
        ...
```

### Debugging and Inspection Features

Visual UIs need access to runtime state for debugging displays. The architecture provides comprehensive inspection capabilities:

#### Variable Table Display

The visual UI can display all variables in real-time:

```python
# In visual UI update loop
variables = engine.get_variable_table()

# Display in variable watch window:
# A = 42 (INTEGER)
# B$ = "HELLO" (STRING)
# C# = 3.14159 (DOUBLE)
# D( = [1, 2, 3, 4, 5] (ARRAY)
# FN_X = <function> (DEF FN)
```

**Implementation details:**
- Variable table includes suffix (%, $, #, !, (, FN_) for type identification
- Arrays show as list of values (or summary if large)
- DEF FN functions marked specially
- Updated at each step or breakpoint

#### Call Stack Display

Display GOSUB/RETURN call stack for debugging:

```python
gosub_stack = engine.get_gosub_stack()
for_stack = engine.get_for_loop_stack()

# GOSUB Stack:
# → Line 1000  (current)
# → Line 500
# → Line 100

# FOR Loop Stack:
# FOR I = 5 TO 10 STEP 1  (line 100)
# FOR J = 2 TO 5 STEP 1   (line 150)
```

**Use cases:**
- Visualize nested GOSUB calls
- Detect infinite recursion
- Show FOR loop nesting
- Display loop variable values

#### Execution Stepping

Three levels of stepping granularity:

**Line Stepping**: Execute one entire line
```python
engine.step_line()  # Executes: 100 PRINT A: GOSUB 500: B = B + 1
# Pauses after completing all statements on line 100
```

**Statement Stepping**: Execute one statement at a time
```python
engine.step_statement()  # Executes: PRINT A
engine.step_statement()  # Executes: GOSUB 500
engine.step_statement()  # Executes: B = B + 1
# Pauses after each statement
```

**Expression Stepping**: Step into expression evaluation
```python
# Line: 100 X = (A + B) * (C + D)
engine.step_expression()  # Evaluates: A
engine.step_expression()  # Evaluates: B
engine.step_expression()  # Evaluates: A + B
engine.step_expression()  # Evaluates: C
engine.step_expression()  # Evaluates: D
engine.step_expression()  # Evaluates: C + D
engine.step_expression()  # Evaluates: (A + B) * (C + D)
# Shows expression evaluation tree
```

#### Breakpoints

Set breakpoints at line numbers:

```python
engine.set_breakpoint(100)
engine.set_breakpoint(500)
engine.run_program(program)  # Pauses at line 100
# User inspects variables, call stack
engine.continue_execution()  # Continues to line 500
```

**Visual UI features:**
- Click line numbers to toggle breakpoints
- Red dot indicates breakpoint
- Highlight current line during execution
- Step buttons: Step Line, Step Statement, Step Expression
- Continue button: Run until next breakpoint

#### Step Callbacks

Register callbacks for UI updates during stepping:

```python
def on_step(state: ExecutionState):
    # Update UI highlighting
    highlight_line(state.current_line)

    # Update variable display
    refresh_variable_table()

    # Update call stack display
    refresh_call_stack()

    # Scroll to current line
    scroll_to_line(state.current_line)

engine.set_step_mode('line', callback=on_step)
```

#### Runtime State Inspection

Access full execution state:

```python
state = engine.get_execution_state()
print(f"Current line: {state.current_line}")
print(f"Statement index: {state.current_statement_index}")
print(f"Stopped: {state.stopped}")
print(f"Breakpoints: {state.breakpoints}")
```

### Refactoring Steps

#### Phase 1: I/O Abstraction and Debugging Support

**Goal**: Extract all I/O into IOHandler interface AND add debugging/inspection capabilities

1. **Create src/io/ directory structure**
   - base.py: IOHandler interface
   - console.py: ConsoleIOHandler (wraps print/input)
   - gui.py: GUIIOHandler stub

2. **Refactor interpreter.py → src/core/engine.py**
   - Pass IOHandler to constructor
   - Replace `print()` with `self.io.output()`
   - Replace error messages with `self.io.error()`
   - Replace DEBUG print with `self.io.debug()`

3. **Add debugging support to InterpreterEngine**
   - Add ExecutionState class
   - Implement `get_variable_table()` method
   - Implement `get_gosub_stack()` method
   - Implement `get_for_loop_stack()` method
   - Implement `get_execution_state()` method
   - Add stepping support: `step_line()`, `step_statement()`, `step_expression()`
   - Add breakpoint support: `set_breakpoint()`, `clear_breakpoint()`
   - Add step_callback mechanism for UI updates

4. **Extend runtime.py to support inspection**
   - Add `get_all_variables()` method to export variable table
   - Add `get_gosub_stack()` method to export return stack
   - Add `get_for_loop_stack()` method to export FOR loop contexts
   - Track current_line and current_statement during execution

5. **Refactor basic_builtins.py**
   - Pass IOHandler to built-in functions
   - Replace `input()` with `io_handler.input()`
   - Replace `print()` with `io_handler.output()`

6. **Test**: Ensure CLI still works with ConsoleIOHandler
7. **Test**: Verify debugging methods return correct data

**Time Estimate**: 3-4 hours (increased for debugging features)

#### Phase 2: Program Management

**Goal**: Extract line/AST management from InteractiveMode

1. **Create src/editing/ directory**
   - manager.py: ProgramManager class
   - commands.py: Core editing commands

2. **Extract from interactive.py**:
   - Line storage (self.lines, self.line_asts)
   - Parsing logic (parse_single_line)
   - SAVE/LOAD/NEW/DELETE/RENUM logic
   - Move to ProgramManager

3. **Test**: Ensure editing commands work

**Time Estimate**: 2-3 hours

#### Phase 3: UI Abstraction

**Goal**: Make InteractiveMode a UI backend

1. **Create src/ui/ directory**
   - base.py: UIBackend interface
   - cli.py: Refactored InteractiveMode

2. **Refactor InteractiveMode → CLIBackend**
   - Use ProgramManager instead of direct line storage
   - Use InterpreterEngine instead of direct Interpreter
   - Keep CLI-specific: REPL loop, line editor

3. **Create visual.py stub**
   - Minimal VisualBackend implementation
   - Document interface for GUI integration

**Time Estimate**: 3-4 hours

#### Phase 4: Dynamic Loading

**Goal**: Use importlib to load backends dynamically

1. **Refactor mbasic.py**
   - Add --backend argument (cli/visual)
   - Use importlib.import_module() to load backend
   - Pass IOHandler and ProgramManager to backend

2. **Create backend loader**:
   ```python
   def load_backend(backend_name: str, io_handler: IOHandler,
                    program_manager: ProgramManager) -> UIBackend:
       module = importlib.import_module(f'backends.{backend_name}')
       return module.create_backend(io_handler, program_manager)
   ```

3. **Test**: Ensure both CLI and stub visual backend work

**Time Estimate**: 1-2 hours

#### Phase 5: Visual UI Preparation (DEFERRED)

**Goal**: Stop before implementing visual UI, evaluate mobile-friendly options

**Status**: This phase is intentionally deferred until after Phases 1-4 are complete.

**Rationale**: The architecture created in Phases 1-4 (IOHandler, UIBackend) is framework-agnostic. Before committing to a specific visual framework, we'll evaluate cross-platform options for **iOS, Android, and desktop**.

**Potential Mobile Frameworks to Evaluate**:
1. **Kivy** - Python native, runs on iOS/Android/Desktop, touch-friendly
2. **BeeWare (Toga)** - Native widgets on each platform, Python-based
3. **PyQt/PySide** - QML for mobile, mature framework
4. **React Native + Python bridge** - Web tech, native performance
5. **Flutter + Python bridge** - High-performance, beautiful UIs
6. **Web-based (PWA)** - HTML5/JavaScript calling Python backend via REST/WebSocket

**Evaluation Criteria**:
- iOS and Android support (primary requirement)
- Touch input and gesture support
- Native feel vs web view performance
- Deployment complexity (app store requirements)
- Screen size adaptation (phone/tablet)
- Text editor widget quality
- Development velocity
- Python integration quality

**Phase 5 Implementation**:
After Phase 4, we'll create a separate document (MOBILE_UI_EVALUATION.md) analyzing each framework with:
- Proof-of-concept implementations
- Pros/cons for MBASIC use case
- Recommended approach
- Implementation plan for chosen framework

**Time Estimate**: TBD (depends on framework choice and evaluation time)

### Migration Strategy

**Backward Compatibility:**
- Keep `mbasic.py` working exactly as before (default CLI)
- `python3 mbasic.py` → CLI mode (no changes for users)
- `python3 mbasic.py --backend visual` → Visual mode

**Gradual Migration:**
1. Phase 1-3: Refactor internal structure (no API changes)
2. Phase 4: Add dynamic loading (optional --backend flag)
3. **STOP**: Evaluate mobile UI frameworks before Phase 5
4. Phase 5: Implement chosen mobile/visual backend (deferred)

**Testing:**
- After each phase, run existing test suite
- Ensure `python3 mbasic.py` still works
- Ensure `python3 mbasic.py program.bas` still works

## API for Visual UI Developers

### Example: Custom Visual UI

```python
from src.io.base import IOHandler
from src.editing.manager import ProgramManager
from src.ui.base import UIBackend
from src.core.engine import InterpreterEngine
from parser import TypeInfo

class MyGUIIOHandler(IOHandler):
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def output(self, text: str, end: str = '\n') -> None:
        self.text_widget.insert('end', text + end)

    def input(self, prompt: str = '') -> str:
        # Show dialog or input field
        return self.show_input_dialog(prompt)

    # ... implement other methods

class MyVisualUI(UIBackend):
    def __init__(self, io_handler, program_manager):
        super().__init__(io_handler, program_manager)
        # Your GUI setup here

    def start(self):
        # Start your GUI main loop
        pass

# Usage:
io = MyGUIIOHandler(my_text_widget)
manager = ProgramManager(default_def_type_map())
ui = MyVisualUI(io, manager)
ui.start()
```

### Example: Embed in Existing App

```python
import importlib

def create_mbasic_interpreter(output_callback, input_callback):
    """Create embedded MBASIC interpreter"""

    # Custom I/O handler
    class CallbackIOHandler(IOHandler):
        def output(self, text: str, end: str = '\n'):
            output_callback(text + end)

        def input(self, prompt: str = ''):
            return input_callback(prompt)

        # ... other methods

    # Load backend dynamically
    backend_module = importlib.import_module('src.ui.cli')

    io = CallbackIOHandler()
    manager = ProgramManager(default_def_type_map())
    backend = backend_module.CLIBackend(io, manager)

    return backend
```

### Example: Visual Debugger UI

```python
class VisualDebuggerUI:
    """Example visual UI with full debugging support"""

    def __init__(self):
        self.io = GUIIOHandler(self.output_widget)
        self.program = ProgramManager(default_def_type_map())
        self.engine = InterpreterEngine(self.io)

        # UI components
        self.code_editor = CodeEditorWidget()
        self.output_widget = OutputWidget()
        self.variable_table = VariableTableWidget()
        self.call_stack_widget = CallStackWidget()

        # Register step callback
        self.engine.set_step_mode('line', callback=self.on_step)

    def on_step(self, state: ExecutionState):
        """Called at each step during execution"""
        # Highlight current line in editor
        self.code_editor.highlight_line(state.current_line)
        self.code_editor.scroll_to_line(state.current_line)

        # Update variable table
        variables = self.engine.get_variable_table()
        self.variable_table.update(variables)

        # Update call stack display
        gosub_stack = self.engine.get_gosub_stack()
        for_stack = self.engine.get_for_loop_stack()
        self.call_stack_widget.update(gosub_stack, for_stack)

        # Update UI state
        self.update_button_states(state)

    def on_run_clicked(self):
        """Run button clicked"""
        program_ast = self.program.get_ast()
        self.engine.clear_step_mode()  # Run normally
        self.engine.run_program(program_ast)

    def on_step_line_clicked(self):
        """Step Line button clicked"""
        self.engine.step_line()

    def on_step_statement_clicked(self):
        """Step Statement button clicked"""
        self.engine.step_statement()

    def on_step_expression_clicked(self):
        """Step Expression button clicked"""
        self.engine.step_expression()

    def on_continue_clicked(self):
        """Continue button clicked (run to next breakpoint)"""
        self.engine.continue_execution()

    def on_breakpoint_toggle(self, line_number: int):
        """User clicked on line number to toggle breakpoint"""
        state = self.engine.get_execution_state()
        if line_number in state.breakpoints:
            self.engine.clear_breakpoint(line_number)
            self.code_editor.remove_breakpoint_marker(line_number)
        else:
            self.engine.set_breakpoint(line_number)
            self.code_editor.add_breakpoint_marker(line_number)

    def on_variable_clicked(self, var_name: str):
        """User clicked on variable to inspect"""
        variables = self.engine.get_variable_table()
        value = variables.get(var_name)
        self.show_variable_inspector(var_name, value)

    def update_button_states(self, state: ExecutionState):
        """Update button enabled/disabled states"""
        self.run_button.enabled = not state.stopped
        self.step_buttons.enabled = state.stopped
        self.continue_button.enabled = state.stopped
```

This example shows how a visual UI can:
- Display all variables in real-time during execution
- Show GOSUB and FOR loop call stacks
- Support line/statement/expression stepping
- Toggle breakpoints by clicking line numbers
- Highlight the current execution line
- Inspect variable values on click


## Benefits of This Architecture

### For CLI Users
- **No Changes**: Existing workflow unchanged
- **Performance**: No overhead from abstraction (Python duck typing)
- **Backward Compatible**: All existing scripts work

### For Visual UI Developers
- **Clean API**: IOHandler and UIBackend interfaces
- **Flexible I/O**: Custom handlers for any UI framework
- **Embeddable**: Drop interpreter into existing apps
- **Dynamic Loading**: No need to modify mbasic.py
- **Full Debugging Support**: Variable inspection, call stacks, stepping, breakpoints
- **Real-time State Access**: Query runtime state at any time during execution
- **Step Callbacks**: UI updates automatically during stepping

### For Maintainers
- **Separation of Concerns**: Core logic vs UI vs I/O
- **Testable**: Mock IOHandler for testing
- **Extensible**: New backends without touching core
- **Clear Boundaries**: Well-defined interfaces

## Implementation Checklist

### Phase 1: I/O Abstraction and Debugging Support ✅ COMPLETE
- [x] Create src/iohandler/ directory structure (renamed from io/)
- [x] Implement IOHandler interface (base.py)
- [x] Implement ConsoleIOHandler (console.py)
- [x] Refactor interpreter.py to use IOHandler
- [x] Extend runtime.py with get_all_variables() method
- [x] Extend runtime.py with get_gosub_stack() method
- [x] Extend runtime.py with get_for_loop_stack() method
- [x] Test: CLI functionality unchanged
- [x] Test: Variable/stack inspection methods work
- [x] Document: Phase 1 progress

**Notes:**
- ExecutionState, stepping, and breakpoints deferred (not needed for initial visual UI)
- Can be added in future when visual debugger is implemented

### Phase 2: Program Management ✅ COMPLETE
- [x] Create src/editing/ directory
- [x] Implement ProgramManager class (355 lines)
- [x] Extract line storage from InteractiveMode
- [x] Extract parsing from InteractiveMode
- [x] Extract SAVE/LOAD from InteractiveMode
- [x] Test: All editing commands work
- [x] Document: Phase 2 progress

### Phase 3: UI Abstraction ✅ COMPLETE
- [x] Create src/ui/ directory
- [x] Implement UIBackend interface (base.py)
- [x] Create CLIBackend wrapping InteractiveMode (cli.py)
- [x] Create VisualBackend template (visual.py)
- [x] Update InteractiveMode to use ProgramManager
- [x] Test: Interactive mode works
- [x] Document: Phase 3 progress

**Notes:**
- CLIBackend wraps InteractiveMode for backward compatibility (not full refactor)
- VisualBackend provides complete template for GUI developers

### Phase 4: Dynamic Loading ✅ COMPLETE
- [x] Add importlib loading to mbasic.py
- [x] Add --backend command line argument (cli/visual)
- [x] Add --debug command line argument
- [x] Create load_backend() function using importlib
- [x] Refactor main() to use UIBackend architecture
- [x] Test: CLI backend loads dynamically
- [x] Test: Visual backend (stub) loads correctly
- [x] Test: Backward compatibility maintained
- [x] Document: Phase 4 progress

**Notes:**
- No backends/ directory created - backends live in src/ui/
- 100% backward compatible - default behavior unchanged

### Phase 5: Mobile/Visual UI (DEFERRED)
**STOP HERE - Complete Phases 1-4 first, then evaluate mobile frameworks**
- [ ] Create MOBILE_UI_EVALUATION.md
- [ ] Evaluate Kivy, BeeWare, PyQt, React Native, Flutter, PWA
- [ ] Build proof-of-concept for top 2-3 options
- [ ] Choose framework based on iOS/Android support
- [ ] Design mobile-specific UI (touch, gestures, screen sizes)
- [ ] Implement chosen framework
- [ ] Document: Mobile UI integration guide

## Timeline Estimate

**Phases 1-4 (Core Refactoring)**: 10-14 hours
- Phase 1: 3-4 hours (I/O abstraction + debugging features)
- Phase 2: 2-3 hours (Program management)
- Phase 3: 3-4 hours (UI abstraction)
- Phase 4: 2-3 hours (Dynamic loading + debugging UI examples)

**Phase 5 (Mobile UI)**: TBD - Deferred pending framework evaluation
- Framework evaluation: 2-4 hours
- Proof-of-concepts: 4-8 hours
- Implementation: 8-20 hours (varies by framework)
- Documentation: 2-4 hours

## Risks and Mitigations

### Risk: Breaking existing functionality
**Mitigation**: Test after each phase, maintain backward compatibility

### Risk: Performance overhead
**Mitigation**: Python duck typing is fast, minimal overhead

### Risk: Complex refactoring
**Mitigation**: Incremental approach, keep old code until new works

### Risk: Different UI paradigms (CLI vs GUI)
**Mitigation**: Clean abstractions, document differences

## Future Extensions

Once the refactoring is complete, these become possible:

1. **Web UI**: Create a web-based backend using Flask/Django
2. **Jupyter**: Jupyter notebook integration
3. **IDE Plugin**: VS Code or other IDE plugins
4. **Headless**: Run BASIC programs as services
5. **Testing**: Mock I/O for comprehensive testing
6. **Network**: Remote BASIC execution (telnet-like)

## Mobile Platform Considerations

### iOS and Android Requirements

The architecture must support:
- **Touch Input**: No mouse, touch gestures (tap, swipe, pinch)
- **Screen Sizes**: Phone (3-7") to tablet (8-13")
- **Virtual Keyboard**: Screen space management when keyboard is visible
- **App Store Requirements**: Code signing, sandboxing, review process
- **Native vs Web Feel**: Balance between performance and development speed

### Framework Requirements for MBASIC

1. **Text Editing Widget**
   - Line numbers display
   - Syntax highlighting (nice to have)
   - Touch-friendly scrolling
   - Selection and cursor control

2. **Output Display**
   - Monospace font support
   - Scrollable text output
   - Clear screen capability
   - ANSI/cursor positioning (for CLS, LOCATE)

3. **Input Handling**
   - Dialog for INPUT statement
   - Keyboard management
   - INKEY$ simulation (button or gesture)

4. **Program Management**
   - File picker for LOAD/SAVE
   - Visual line editor
   - RUN/STOP buttons
   - Program listing view

### Recommended Evaluation Order

After Phase 4 completion:

1. **Kivy** (Try first)
   - Pro: Pure Python, iOS/Android/Desktop proven
   - Pro: Good documentation, active community
   - Con: Custom widget look (not native)

2. **BeeWare** (Try second)
   - Pro: Native widgets on each platform
   - Pro: Python-native philosophy
   - Con: Younger project, less mature

3. **Web-based (PWA)** (Fallback)
   - Pro: Easiest cross-platform
   - Pro: Familiar web technologies
   - Con: Need Python backend (API approach)

## Conclusion

This refactoring plan provides a clear path to making MBASIC embeddable in visual UIs while maintaining CLI functionality. The architecture uses standard Python patterns (importlib, abstract interfaces) and follows best practices for separation of concerns.

**Key Decision**: The plan deliberately stops after Phase 4 to evaluate mobile frameworks properly. The IOHandler and UIBackend architecture is framework-agnostic and will work with any UI technology chosen for iOS/Android support.

The incremental approach ensures each phase is testable and doesn't break existing functionality. Phases 1-4 create a flexible, embeddable BASIC interpreter core that can be wrapped in any UI framework - command-line, desktop GUI, mobile app, or web interface.
