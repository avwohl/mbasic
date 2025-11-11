# Tk UI Enhancement Plan - Feature Parity with Curses UI

## Status Assessment

### What Exists (src/ui/tk_ui.py - 386 lines)

**Basic Features:**
- ✅ Menu bar (File, Edit, Run, Help)
- ✅ Toolbar with common actions
- ✅ Editor and output windows
- ✅ File operations (New, Open, Save, Save As)
- ✅ Basic program execution
- ✅ Status bar
- ✅ Monospace font
- ✅ Scrollable editor and output

**Architecture:**
- Uses old program_manager architecture (not tick-based interpreter)
- Basic Text widgets without line numbers
- Horizontal split layout (needs to be changed to vertical like curses UI)
- No debugging features
- No watch windows

### What's Missing (Feature Parity with Curses UI)

**Critical Missing Features:**
- ❌ Line number column with status indicators (●, ?, space)
- ❌ Tick-based interpreter integration
- ❌ Breakpoint support (visual + functionality)
- ❌ Debugger (Step/Continue/Stop)
- ❌ Variables watch window (Ctrl+W)
- ❌ Execution stack window (Ctrl+K)
- ❌ Statement highlighting (cyan background for active statement)
- ❌ Automatic line sorting
- ❌ Auto-numbering with calculator-style digit entry
- ❌ Syntax error detection with ? markers
- ❌ Current line highlighting during execution
- ❌ Help dialog (Ctrl+A)
- ❌ Delete line command (Ctrl+D)
- ❌ Renumber command (Ctrl+E)

**Keyboard Shortcut Gaps:**
- Current: Ctrl+N, Ctrl+O, Ctrl+S, F5
- Missing: Ctrl+R, Ctrl+T, Ctrl+G, Ctrl+X, Ctrl+B, Ctrl+W, Ctrl+K, Ctrl+D, Ctrl+E, Ctrl+A, Ctrl+U

## Enhancement Plan

### Target Layout (Vertical, Matching Curses UI)

**IMPORTANT:** The layout must match the curses UI vertical arrangement, NOT horizontal split.

```
┌─────────────────────────────────────────────┐
│ File  Edit  Run  Help                       │ Menu Bar
├─────────────────────────────────────────────┤
│ ●  10  PRINT "Hello"                        │
│    20  FOR I = 1 TO 10                      │ Editor
│    30    PRINT I                            │ (60% height)
│    40  NEXT I                               │
│    50  END                                  │
├─────────────────────────────────────────────┤ ← Draggable splitter
│ Variable    Type      Value                 │
│ I%          Integer   3                     │ Variables Window
│ MSG$        String    "Hello"               │ (optional, Ctrl+W)
├─────────────────────────────────────────────┤ ← Draggable splitter
│ Type              Details                   │
│ GOSUB from 20     → line 100                │ Stack Window
│   FOR I = 2/10    (line 30)                 │ (optional, Ctrl+K)
├─────────────────────────────────────────────┤ ← Draggable splitter
│ Hello                                       │
│ 1                                           │ Output
│ 2                                           │ (30% height)
│ 3                                           │
├─────────────────────────────────────────────┤
│ Ready - Press Ctrl+A for help               │ Status Bar
└─────────────────────────────────────────────┘
```

**Implementation:**
- Use `tk.PanedWindow` with `orient=tk.VERTICAL`
- Default: Menu → Editor → Output → Status
- When variables shown (Ctrl+W): Menu → Editor → Variables → Output → Status
- When stack shown (Ctrl+K): Menu → Editor → [Variables] → Stack → Output → Status
- All splitters are draggable
- Remember sizes between runs

**Current tk_ui.py uses horizontal split:**
```python
# WRONG - current implementation (to be changed):
paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
paned.add(editor_frame, weight=1)  # Left
paned.add(output_frame, weight=1)  # Right
```

**Correct implementation:**
```python
# RIGHT - new implementation:
paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
paned.add(editor_frame, weight=6)  # Top (60%)
# Variables and stack added dynamically with .insert()
paned.add(output_frame, weight=3)  # Bottom (30%)
```

### Phase 1: Modernize Architecture (Priority: CRITICAL)

**Goal:** Update to use tick-based interpreter like curses UI

**Changes to tk_ui.py:**

```python
# Update imports
from tick_interpreter import create_tick_interpreter

class TkBackend(UIBackend):
    def __init__(self):
        # Add tick-based interpreter state
        self.tick_interpreter = None
        self.running = False
        self.paused_at_breakpoint = False
        self.breakpoints = set()  # Set of line numbers

    def cmd_run(self):
        """Run program using tick-based interpreter"""
        # Create tick interpreter
        self.tick_interpreter = create_tick_interpreter(program_text)
        self.running = True

        # Start tick loop
        self.root.after(10, self._tick)

    def _tick(self):
        """Execute one interpreter tick"""
        if not self.running or not self.tick_interpreter:
            return

        state = self.tick_interpreter.tick()

        # Handle different states
        if state.status == 'completed':
            self.running = False
            self._add_output("\n--- Program finished ---\n")
        elif state.status == 'error':
            self.running = False
            self._add_output(f"\n--- Error: {state.error} ---\n")
        elif state.status == 'at_breakpoint':
            self.running = False
            self.paused_at_breakpoint = True
            self._highlight_current_line(state.current_line)
            self._update_watches()
        elif state.status == 'running':
            # Schedule next tick
            self.root.after(10, self._tick)

        # Update display
        self._update_output_from_state(state)
        self._highlight_current_line(state.current_line)
```

**Testing:** Can run programs and see output

### Phase 2: Line Numbers and Status Column (Priority: HIGH)

**Goal:** Add 3-column editor like curses UI: [Status][Line Number][Code]

**Create new widget: LineNumberedText (new file src/ui/tk_widgets.py)**

```python
import tkinter as tk
from tkinter import font as tkfont

class LineNumberedText(tk.Frame):
    """Text widget with line numbers and status column.

    Layout: [Status (1 char)][Line Number (variable width)][Separator][Code]
    Status symbols: ● breakpoint, ? error, space normal
    """

    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent)

        # Status and line number canvas
        self.canvas = tk.Canvas(self, width=70, bg='lightgray')
        self.canvas.pack(side=tk.LEFT, fill=tk.Y)

        # Text widget
        self.text = tk.Text(self, **kwargs)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        self.scrollbar = tk.Scrollbar(self, command=self._on_scroll)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure scrolling
        self.text.config(yscrollcommand=self._on_text_scroll)

        # Track line data
        self.line_data = {}  # line_num -> {'status': '●'|'?'|' ', 'number': int}

        # Bind events
        self.text.bind('<Configure>', self._redraw)
        self.text.bind('<KeyRelease>', self._on_key)
        self.canvas.bind('<Button-1>', self._on_margin_click)

    def _redraw(self, event=None):
        """Redraw line numbers for visible lines"""
        self.canvas.delete('all')

        # Get visible range
        first = self.text.index('@0,0')
        last = self.text.index(f'@0,{self.text.winfo_height()}')

        # Font metrics
        font_obj = tkfont.Font(font=self.text['font'])
        line_height = font_obj.metrics('linespace')

        # Draw each visible line
        first_line = int(first.split('.')[0])
        last_line = int(last.split('.')[0])

        for i in range(first_line, last_line + 1):
            y = (i - first_line) * line_height + line_height // 2

            # Get BASIC line number for this text line
            basic_line = self._get_basic_line_number(i)

            if basic_line:
                # Get status
                status = self.line_data.get(basic_line, {}).get('status', ' ')

                # Draw status (column 0)
                self.canvas.create_text(10, y, text=status, font=font_obj)

                # Draw line number (variable width)
                self.canvas.create_text(55, y, text=str(basic_line),
                                      font=font_obj, anchor='e')

    def _get_basic_line_number(self, text_line):
        """Extract BASIC line number from text line"""
        line_content = self.text.get(f'{text_line}.0', f'{text_line}.end')
        import re
        match = re.match(r'^(\d+)', line_content.strip())
        return int(match.group(1)) if match else None

    def _on_margin_click(self, event):
        """Handle click in margin - toggle breakpoint"""
        # Calculate which line was clicked
        font_obj = tkfont.Font(font=self.text['font'])
        line_height = font_obj.metrics('linespace')
        line = int(event.y / line_height) + 1

        # Get BASIC line number
        basic_line = self._get_basic_line_number(line)
        if basic_line:
            self._toggle_breakpoint(basic_line)

    def set_breakpoint(self, line_num, enabled=True):
        """Set/clear breakpoint on line"""
        if line_num not in self.line_data:
            self.line_data[line_num] = {'status': ' ', 'number': line_num}
        self.line_data[line_num]['status'] = '●' if enabled else ' '
        self._redraw()

    def set_error(self, line_num, has_error=True):
        """Mark line with error"""
        if line_num not in self.line_data:
            self.line_data[line_num] = {'status': ' ', 'number': line_num}
        self.line_data[line_num]['status'] = '?' if has_error else ' '
        self._redraw()
```

**Integration into tk_ui.py:**

```python
def _create_ui(self):
    # Replace self.editor_text with LineNumberedText
    from .tk_widgets import LineNumberedText

    self.editor = LineNumberedText(
        editor_frame,
        wrap=tk.NONE,
        font=("Courier", 10)
    )
    self.editor.pack(fill=tk.BOTH, expand=True)

    # Access text widget as self.editor.text
```

**Testing:** Can see line numbers, click margin to toggle breakpoints

### Phase 3: Debugging Features (Priority: HIGH)

**Goal:** Add Step/Continue/Stop commands

**Add to tk_ui.py:**

```python
def _create_menu(self):
    # Add to Run menu
    run_menu.add_separator()
    run_menu.add_command(label="Step", command=self._debug_step, accelerator="Ctrl+T")
    run_menu.add_command(label="Continue", command=self._debug_continue, accelerator="Ctrl+G")
    run_menu.add_command(label="Stop", command=self._debug_stop, accelerator="Ctrl+X")
    run_menu.add_command(label="Toggle Breakpoint", command=self._toggle_breakpoint_current,
                        accelerator="Ctrl+B")

    # Bind keys
    self.root.bind("<Control-t>", lambda e: self._debug_step())
    self.root.bind("<Control-g>", lambda e: self._debug_continue())
    self.root.bind("<Control-x>", lambda e: self._debug_stop())
    self.root.bind("<Control-b>", lambda e: self._toggle_breakpoint_current())

def _debug_step(self):
    """Execute one line"""
    if not self.tick_interpreter:
        # Start program in step mode
        self.cmd_run()
        self.running = False  # Pause immediately
        return

    # Execute one tick
    state = self.tick_interpreter.tick()
    self._handle_tick_state(state)
    self._update_displays()

def _debug_continue(self):
    """Continue execution from breakpoint"""
    if self.paused_at_breakpoint:
        self.running = True
        self.paused_at_breakpoint = False
        self.root.after(10, self._tick)

def _debug_stop(self):
    """Stop execution"""
    self.running = False
    self.paused_at_breakpoint = False
    self.tick_interpreter = None
    self._clear_current_line_highlight()

def _toggle_breakpoint_current(self):
    """Toggle breakpoint on current line"""
    # Get cursor position
    cursor_pos = self.editor.text.index(tk.INSERT)
    line = int(cursor_pos.split('.')[0])

    # Get BASIC line number
    basic_line = self.editor._get_basic_line_number(line)
    if basic_line:
        if basic_line in self.breakpoints:
            self.breakpoints.remove(basic_line)
            self.editor.set_breakpoint(basic_line, False)
        else:
            self.breakpoints.add(basic_line)
            self.editor.set_breakpoint(basic_line, True)
```

**Testing:** Can step through program, set breakpoints, continue, stop

### Phase 4: Variables Watch Window (Priority: MEDIUM)

**Goal:** Add Ctrl+W toggleable variables window

**Add to tk_ui.py:**

```python
def __init__(self):
    # Add variables window state
    self.variables_window = None
    self.variables_visible = False

def _create_ui(self):
    # Create variables window (initially hidden)
    self.variables_window = self._create_variables_window()

def _create_variables_window(self):
    """Create variables Treeview window"""
    from tkinter import ttk

    window = tk.Toplevel(self.root)
    window.title("Variables")
    window.geometry("400x300")
    window.protocol("WM_DELETE_WINDOW", lambda: self._toggle_variables())
    window.withdraw()  # Hidden initially

    # Create Treeview
    tree = ttk.Treeview(window, columns=('Type', 'Value'), show='tree headings')
    tree.heading('#0', text='Variable')
    tree.heading('Type', text='Type')
    tree.heading('Value', text='Value')
    tree.column('#0', width=100)
    tree.column('Type', width=100)
    tree.column('Value', width=200)
    tree.pack(fill=tk.BOTH, expand=True)

    self.variables_tree = tree
    return window

def _toggle_variables(self):
    """Toggle variables window visibility (Ctrl+W)"""
    if self.variables_visible:
        self.variables_window.withdraw()
        self.variables_visible = False
    else:
        self.variables_window.deiconify()
        self.variables_visible = True
        self._update_variables()

def _update_variables(self):
    """Update variables window from runtime"""
    if not self.variables_visible or not self.tick_interpreter:
        return

    # Clear tree
    for item in self.variables_tree.get_children():
        self.variables_tree.delete(item)

    # Get variables from runtime
    variables = self.tick_interpreter.runtime.get_all_variables()

    # Add to tree
    for var in sorted(variables, key=lambda v: v['name']):
        name = var['name'] + var['type_suffix']
        type_name = var['type_name']

        if var['is_array']:
            dims = 'x'.join(str(d) for d in var['dimensions'])
            value = f"Array({dims})"
        else:
            value = var['value']
            if var['type_suffix'] == '$':
                value = f'"{value}"'

        self.variables_tree.insert('', 'end', text=name,
                                  values=(type_name, value))

# Add keyboard binding
self.root.bind("<Control-w>", lambda e: self._toggle_variables())
```

**Testing:** Can view variables, updates during stepping

### Phase 5: Execution Stack Window (Priority: MEDIUM)

**Goal:** Add Ctrl+K toggleable stack window

**Similar to variables window but showing execution stack:**

```python
def _create_stack_window(self):
    """Create execution stack Treeview window"""
    # Similar to variables window
    # Columns: Type, Details
    # Shows: GOSUB from X, FOR I=1 TO 10, WHILE (line X)
    # Use indentation for nesting
    pass

def _update_stack(self):
    """Update stack window from runtime"""
    if not self.stack_visible or not self.tick_interpreter:
        return

    stack = self.tick_interpreter.runtime.get_execution_stack()

    # Clear and rebuild tree with indentation
    for i, entry in enumerate(stack):
        indent = "  " * i
        if entry['type'] == 'GOSUB':
            text = f"{indent}GOSUB from {entry['from_line']}"
        elif entry['type'] == 'FOR':
            text = f"{indent}FOR {entry['var']} = {entry['current']} TO {entry['end']}"
        # etc.
```

### Phase 6: Additional Features (Priority: LOW)

**Statement Highlighting:**
- Use Text tags to highlight active statement with cyan background
- Parse line on ':' to find statement boundaries

**Delete Line (Ctrl+D):**
```python
def _delete_current_line(self):
    cursor = self.editor.text.index(tk.INSERT)
    line = cursor.split('.')[0]
    self.editor.text.delete(f'{line}.0', f'{line}.end+1c')
```

**Renumber (Ctrl+E):**
- Dialog asking for start and increment
- Renumber all lines in editor

**Help Dialog (Ctrl+A):**
- Show help text in dialog box

**Automatic Line Sorting:**
- Sort lines when navigating (harder in Tk)

**Auto-Numbering:**
- Intercept Return key
- Insert next line number

## Implementation Priority

1. **Phase 1** (CRITICAL): Modernize to tick-based interpreter
2. **Phase 2** (HIGH): Line numbers with status column
3. **Phase 3** (HIGH): Debugging (Step/Continue/Stop/Breakpoints)
4. **Phase 4** (MEDIUM): Variables window
5. **Phase 5** (MEDIUM): Stack window
6. **Phase 6** (LOW): Polish features

## Testing Requirements

**Environment:**
- Requires desktop environment with X11/Wayland or Windows/Mac
- Install tkinter: `sudo apt-get install python3-tk` (Ubuntu)
- Test on: Linux with X11, Windows 10+, macOS 10.14+

**Test Cases:**
1. Load and save files
2. Run simple program
3. Set breakpoints and hit them
4. Step through program line by line
5. View variables during execution
6. View execution stack with nested loops/GOSUB
7. Stop execution mid-run
8. Error handling

## Advantages Over Curses UI

1. **Mouse support**: Click to set breakpoints, select text, drag splitters
2. **Native file dialogs**: Better UX for file operations
3. **Resizable everything**: Drag window edges and vertical splitters
4. **Better fonts**: Anti-aliased, variable size
5. **Copy/paste**: Native clipboard integration
6. **Multiple windows**: Variables and stack in embedded panes with splitters
7. **Color**: Full RGB color support for syntax highlighting
8. **Portability**: Same UI on Windows/Mac/Linux
9. **Accessibility**: Screen reader support, system themes

## Development Notes

**Cannot develop in current environment:**
- Requires display server (X11/Wayland/Windows/macOS)
- Current environment is headless (no tkinter module)
- Code can be written but not tested here

**Recommended development setup:**
- Local machine with GUI
- Or: VM with X11 forwarding
- Or: VNC/RDP to remote desktop

**Code organization:**
- Keep tk_ui.py for main backend
- Create tk_widgets.py for custom widgets (LineNumberedText, etc.)
- Create tk_dialogs.py for help/about/renumber dialogs
- Follow curses_ui.py as reference for feature parity

## Completion Criteria

- [ ] All curses UI keyboard shortcuts work
- [ ] All curses UI features present
- [ ] Passes same test suite as curses UI
- [ ] Works on Windows, Mac, Linux
- [ ] Documented in URWID_UI.md (or new TK_UI.md)

---

## Future Enhancement: Interactive Execution Stack

**Feature Request (2025-10-26):**

Add interactivity to the execution stack window to allow navigation to source lines.

**Options:**
1. **Single-click navigation**: Left-click on a stack item scrolls the editor and highlights the corresponding line
2. **Context menu**: Right-click on stack item shows menu with "Go to Line" option
3. **Double-click**: Double-click to jump to line in editor

**Implementation Details:**
- Execution stack displays FOR loops, WHILE loops, and GOSUB calls
- Each stack entry has an associated line number:
  - FOR: line where FOR statement is located
  - WHILE: line where WHILE statement is located
  - GOSUB: line where GOSUB was called from
- Clicking an entry should:
  - Scroll editor to show that line
  - Highlight the line (similar to breakpoint highlighting)
  - Optionally show line in different color to indicate "stack view"

**Benefits:**
- Easier debugging of nested loops and subroutines
- Quick navigation to understand call stack
- Matches behavior of modern debuggers (VS Code, Visual Studio, etc.)

**UI Widget:**
- Currently using `ttk.Treeview` with columns for type and details
- Can bind `<ButtonRelease-1>` for single-click
- Can bind `<Button-3>` (right-click) for context menu
- Can bind `<Double-Button-1>` for double-click

**Example Code:**
```python
def _on_stack_click(self, event):
    """Handle click on execution stack item."""
    item = self.stack_tree.selection()
    if not item:
        return

    # Get line number from the stack entry
    line_num = self._get_line_from_stack_item(item[0])
    if line_num:
        self._scroll_to_line_and_highlight(line_num)
```

**Status:** TODO - Not yet implemented

---

## Variable Editing and Array Cell Inspection

**Feature Request (2025-10-26):**

Add capability to edit variable values and inspect/edit array cells from the variables window.

### Variable Value Editing

**Goal:** Allow editing scalar variable values during debugging

**Interaction:**
- Double-click on a variable in the variables window
- Opens edit dialog showing current value
- User enters new value
- Value is validated and applied to runtime
- Variables window refreshes to show new value

**Implementation:**
```python
def _on_variable_double_click(self, event):
    """Handle double-click on variable to edit value."""
    item = self.variables_tree.selection()
    if not item:
        return

    # Get variable info
    var_name = self.variables_tree.item(item[0])['text']
    current_value = self.variables_tree.item(item[0])['values'][1]

    # Show edit dialog
    new_value = self._show_variable_edit_dialog(var_name, current_value)
    if new_value is not None:
        # Update runtime (using set_variable_raw to avoid tracking)
        self.runtime.set_variable_raw(var_name, new_value)
        # Refresh display
        self._update_variables()
```

**Dialog Requirements:**
- Show variable name and type
- Input field with current value pre-filled
- Type validation (numeric for %/!/# , string for $)
- OK/Cancel buttons
- Error handling for invalid input

### Array Cell Selector

**Goal:** Browse and edit any cell in an array, not just the last accessed one

**Interaction:**
- Right-click on array variable → "Inspect Array..."
- Opens array inspector dialog
- Shows array dimensions and current cell selector
- User enters subscripts (e.g., "3,2" for 2D array)
- Shows value of that cell
- User can edit the value
- Changes are applied to runtime

**Implementation:**
```python
def _on_array_right_click(self, event):
    """Handle right-click on array to inspect cells."""
    item = self.variables_tree.identify_row(event.y)
    if not item:
        return

    # Get array info
    var_name = self.variables_tree.item(item)['text']
    # Check if it's an array
    if not self._is_array_variable(var_name):
        return

    # Show array inspector dialog
    self._show_array_inspector(var_name)
```

**Array Inspector Dialog:**

```
┌─────────────────────────────────────┐
│ Array Inspector: A%(10,5)           │
├─────────────────────────────────────┤
│ Dimensions: 10 x 5 (base 0)         │
│                                      │
│ Subscripts: [3] [2]                 │
│             ▼   ▼                    │
│                                      │
│ Current Value: 42                    │
│                                      │
│ [ Edit Value... ]                   │
│                                      │
│ Last Accessed: [5,4] = 99           │
│                                      │
│      [Close]                         │
└─────────────────────────────────────┘
```

**Features:**
- Spinboxes or entry fields for each dimension
- Range validation (0 to dim for base 0, 1 to dim for base 1)
- Live value display as subscripts change
- Edit button to modify cell value
- Shows last accessed cell for reference
- Limit to 4 dimensions for usability

**Benefits:**
- Debug array contents without adding PRINT statements
- Fix wrong values during debugging session
- Inspect arrays systematically
- Understand array state at breakpoints

**Status:** TODO - Not yet implemented

**Priority:** Medium - useful for debugging but arrays can be inspected via immediate mode

---

**Status:** Plan complete, implementation blocked by environment constraints

**Next Steps:** Implement on machine with GUI environment, test thoroughly
