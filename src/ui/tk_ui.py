"""Tkinter GUI backend for MBASIC interpreter.

This module provides a graphical UI using Python's tkinter library.
Tkinter provides a native GUI with buttons, menus, and text widgets,
making it suitable for a modern BASIC IDE experience.
"""

from .base import UIBackend
from runtime import Runtime
from interpreter import Interpreter
from .keybinding_loader import KeybindingLoader
from immediate_executor import ImmediateExecutor, OutputCapturingIOHandler
from iohandler.base import IOHandler


class TkBackend(UIBackend):
    """Tkinter-based graphical UI backend.

    Provides a graphical UI with:
    - Menu bar (File, Edit, Run, Help)
    - Toolbar with common actions
    - Split pane: editor on left, output on right
    - Line numbers in editor
    - Syntax highlighting (optional)
    - File dialogs for Open/Save

    Usage:
        from iohandler.console import ConsoleIOHandler
        from editing import ProgramManager
        from ui.tk_ui import TkBackend

        io = ConsoleIOHandler()
        program = ProgramManager(def_type_map)
        backend = TkBackend(io, program)
        backend.start()  # Runs Tk mainloop until window closed
    """

    def __init__(self, io_handler, program_manager):
        """Initialize Tkinter backend.

        Args:
            io_handler: IOHandler for I/O operations
            program_manager: ProgramManager instance
        """
        super().__init__(io_handler, program_manager)

        # Load keybindings from config
        self.keybindings = KeybindingLoader('tk')

        # Runtime and interpreter for program execution
        self.runtime = None
        self.interpreter = None

        # Tick-based execution state
        self.running = False
        self.paused_at_breakpoint = False
        self.breakpoints = set()  # Set of line numbers with breakpoints
        self.tick_timer_id = None  # ID of pending after() call

        # Variables watch window state
        self.variables_window = None
        self.variables_tree = None
        self.variables_visible = False

        # Execution stack window state
        self.stack_window = None
        self.stack_tree = None
        self.stack_visible = False

        # Immediate mode
        self.immediate_executor = None
        self.immediate_history = None
        self.immediate_entry = None
        self.immediate_status = None

        # Tkinter widgets (created in start())
        self.root = None
        self.editor_text = None
        self.output_text = None
        self.status_label = None

    def start(self) -> None:
        """Start the Tkinter GUI.

        Creates the main window and starts the Tk event loop.
        """
        import tkinter as tk
        from tkinter import ttk, scrolledtext
        from .tk_widgets import LineNumberedText

        # Create main window
        self.root = tk.Tk()
        self.root.title("MBASIC 5.21 Interpreter")
        self.root.geometry("1000x600")

        # Create menu bar
        self._create_menu()

        # Create toolbar
        self._create_toolbar()

        # Create main content area (split pane)
        paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Top pane: Editor with line numbers (60% of space)
        editor_frame = ttk.Frame(paned)
        paned.add(editor_frame, weight=3)

        ttk.Label(editor_frame, text="Program Editor:").pack(anchor=tk.W, padx=5, pady=5)
        self.editor_text = LineNumberedText(
            editor_frame,
            wrap=tk.NONE,
            width=100,
            height=20
        )
        self.editor_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Set up editor context menu
        self._setup_editor_context_menu()

        # Middle pane: Output (30% of space)
        output_frame = ttk.Frame(paned)
        paned.add(output_frame, weight=2)

        ttk.Label(output_frame, text="Output:").pack(anchor=tk.W, padx=5, pady=5)
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            width=100,
            height=10,
            font=("Courier", 10),
            state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Bottom pane: Immediate Mode (30% of space)
        immediate_frame = ttk.Frame(paned)
        paned.add(immediate_frame, weight=2)

        # Immediate mode header with status
        header_frame = ttk.Frame(immediate_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(header_frame, text="Immediate Mode:").pack(side=tk.LEFT)
        self.immediate_status = ttk.Label(header_frame, text="Ok", foreground="green", font=("Courier", 10, "bold"))
        self.immediate_status.pack(side=tk.LEFT, padx=10)

        # Immediate mode history (scrollable output)
        self.immediate_history = scrolledtext.ScrolledText(
            immediate_frame,
            wrap=tk.WORD,
            width=100,
            height=6,
            font=("Courier", 10),
            state=tk.DISABLED
        )
        self.immediate_history.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # Add right-click context menus for copy functionality
        self._setup_output_context_menu()
        self._setup_immediate_context_menu()

        # Immediate mode input
        input_frame = ttk.Frame(immediate_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        ttk.Label(input_frame, text="Ok >", font=("Courier", 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.immediate_entry = ttk.Entry(input_frame, font=("Courier", 10))
        self.immediate_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.immediate_entry.bind('<Return>', lambda e: self._execute_immediate())

        execute_btn = ttk.Button(input_frame, text="Execute", command=self._execute_immediate)
        execute_btn.pack(side=tk.LEFT)

        # Status bar
        self.status_label = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Create variables watch window (initially hidden)
        self._create_variables_window()

        # Create execution stack window (initially hidden)
        self._create_stack_window()

        # Load program into editor if already loaded
        self._refresh_editor()

        # Start event loop
        self.root.mainloop()

    def _create_menu(self):
        """Create menu bar."""
        import tkinter as tk

        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self._menu_new,
                             accelerator=self.keybindings.get_tk_accelerator('menu', 'file_new'))
        file_menu.add_command(label="Open...", command=self._menu_open,
                             accelerator=self.keybindings.get_tk_accelerator('menu', 'file_open'))
        file_menu.add_command(label="Save", command=self._menu_save,
                             accelerator=self.keybindings.get_tk_accelerator('menu', 'file_save'))
        file_menu.add_command(label="Save As...", command=self._menu_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._menu_exit,
                             accelerator=self.keybindings.get_tk_accelerator('menu', 'file_quit'))

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=self._menu_cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self._menu_copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self._menu_paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Toggle Breakpoint", command=self._toggle_breakpoint, accelerator="Ctrl+B")
        edit_menu.add_command(label="Clear All Breakpoints", command=self._clear_all_breakpoints)

        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Program", command=self._menu_run,
                            accelerator=self.keybindings.get_tk_accelerator('menu', 'run_program'))
        run_menu.add_command(label="Step", command=self._menu_step)
        run_menu.add_command(label="Continue", command=self._menu_continue)
        run_menu.add_command(label="Stop", command=self._menu_stop)
        run_menu.add_separator()
        run_menu.add_command(label="List Program", command=self._menu_list)
        run_menu.add_separator()
        run_menu.add_command(label="Clear Output", command=self._menu_clear_output)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Variables", command=self._toggle_variables, accelerator="Ctrl+W")
        view_menu.add_command(label="Execution Stack", command=self._toggle_stack, accelerator="Ctrl+K")

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Help Topics", command=self._menu_help,
                             accelerator=self.keybindings.get_tk_accelerator('menu', 'help_topics'))
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._menu_about)

        # Bind keyboard shortcuts from config
        self.keybindings.bind_all_to_tk(self.root, 'menu', 'file_new', lambda e: self._menu_new())
        self.keybindings.bind_all_to_tk(self.root, 'menu', 'file_open', lambda e: self._menu_open())
        self.keybindings.bind_all_to_tk(self.root, 'menu', 'file_save', lambda e: self._menu_save())
        self.keybindings.bind_all_to_tk(self.root, 'menu', 'file_quit', lambda e: self._menu_exit())
        self.keybindings.bind_all_to_tk(self.root, 'menu', 'run_program', lambda e: self._menu_run())
        self.keybindings.bind_all_to_tk(self.root, 'menu', 'help_topics', lambda e: self._menu_help())

        # Additional keyboard shortcuts not in config
        self.root.bind('<Control-b>', lambda e: self._toggle_breakpoint())

    def _create_toolbar(self):
        """Create toolbar with common actions."""
        import tkinter as tk
        from tkinter import ttk

        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(toolbar, text="New", command=self._menu_new).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(toolbar, text="Open", command=self._menu_open).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(toolbar, text="Save", command=self._menu_save).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Get run key from config for toolbar label
        run_key = self.keybindings.get_tk_accelerator('menu', 'run_program') or 'F5'
        ttk.Button(toolbar, text=f"Run ({run_key})", command=self._menu_run).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(toolbar, text="List", command=self._menu_list).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(toolbar, text="Clear Output", command=self._menu_clear_output).pack(side=tk.LEFT, padx=2, pady=2)

    # Menu handlers

    def _menu_new(self):
        """File > New"""
        self.cmd_new()

    def _menu_open(self):
        """File > Open"""
        import tkinter as tk
        from tkinter import filedialog

        filename = filedialog.askopenfilename(
            title="Open BASIC Program",
            filetypes=[("BASIC files", "*.bas"), ("All files", "*.*")]
        )
        if filename:
            self.cmd_load(filename)

    def _menu_save(self):
        """File > Save"""
        if self.program.current_file:
            self._save_editor_to_program()
            self.cmd_save(self.program.current_file)
        else:
            self._menu_save_as()

    def _menu_save_as(self):
        """File > Save As"""
        import tkinter as tk
        from tkinter import filedialog

        filename = filedialog.asksaveasfilename(
            title="Save BASIC Program",
            defaultextension=".bas",
            filetypes=[("BASIC files", "*.bas"), ("All files", "*.*")]
        )
        if filename:
            self._save_editor_to_program()
            self.cmd_save(filename)

    def _menu_exit(self):
        """File > Exit"""
        self.root.quit()

    def _menu_cut(self):
        """Edit > Cut"""
        self.editor_text.event_generate("<<Cut>>")

    def _menu_copy(self):
        """Edit > Copy"""
        self.editor_text.event_generate("<<Copy>>")

    def _menu_paste(self):
        """Edit > Paste"""
        self.editor_text.event_generate("<<Paste>>")

    def _menu_run(self):
        """Run > Run Program"""
        self._save_editor_to_program()
        self.cmd_run()

    def _menu_list(self):
        """Run > List Program"""
        self.cmd_list()

    def _menu_step(self):
        """Run > Step (execute one statement)"""
        if not self.interpreter:
            self._set_status("No program running")
            return

        try:
            state = self.interpreter.tick(mode='step', max_statements=1)

            # Handle state
            if state.status == 'paused' or state.status == 'at_breakpoint':
                stmt_info = f" statement {state.current_statement_index + 1}" if state.current_statement_index > 0 else ""
                self._add_output(f"→ Paused at line {state.current_line}{stmt_info}\n")
                self._set_status(f"Paused at line {state.current_line}{stmt_info}")
            elif state.status == 'done':
                self._add_output("\n--- Program finished ---\n")
                self._set_status("Ready")
            elif state.status == 'error':
                error_msg = state.error_info.error_message if state.error_info else "Unknown error"
                line_num = state.error_info.error_line if state.error_info else "?"
                self._add_output(f"\n--- Error at line {line_num}: {error_msg} ---\n")
                self._set_status("Error")

            # Update immediate mode status
            self._update_immediate_status()

            # Update variables and stack windows if visible
            self._update_variables()
            self._update_stack()

        except Exception as e:
            self._add_output(f"Step error: {e}\n")
            self._set_status("Error")

    def _menu_continue(self):
        """Run > Continue (from breakpoint)"""
        if not self.interpreter or not self.paused_at_breakpoint:
            self._set_status("Not paused")
            return

        try:
            # Resume execution
            self.running = True
            self.paused_at_breakpoint = False
            self._set_status("Continuing...")

            # Schedule next tick
            self.tick_timer_id = self.root.after(10, self._execute_tick)

        except Exception as e:
            self._add_output(f"Continue error: {e}\n")
            self._set_status("Error")

    def _menu_stop(self):
        """Run > Stop"""
        if not self.interpreter:
            self._set_status("No program running")
            return

        try:
            # Cancel pending tick
            if self.tick_timer_id:
                self.root.after_cancel(self.tick_timer_id)
                self.tick_timer_id = None

            # Stop execution
            self.running = False
            self.paused_at_breakpoint = False

            self._add_output("\n--- Program stopped by user ---\n")
            self._set_status("Stopped")
            self._update_immediate_status()

        except Exception as e:
            self._add_output(f"Stop error: {e}\n")
            self._set_status("Error")

    def _toggle_breakpoint(self):
        """Toggle breakpoint on current line (Ctrl+B)."""
        # Get current BASIC line number from cursor position
        line_number = self.editor_text.get_current_line_number()

        if not line_number:
            self._set_status("No line number at cursor")
            return

        # Toggle in breakpoints set
        if line_number in self.breakpoints:
            self.breakpoints.remove(line_number)
            self.editor_text.set_breakpoint(line_number, False)
            self._set_status(f"Breakpoint removed from line {line_number}")
        else:
            self.breakpoints.add(line_number)
            self.editor_text.set_breakpoint(line_number, True)
            self._set_status(f"Breakpoint set on line {line_number}")

        # Update interpreter state if running
        if self.interpreter:
            self.interpreter.state.breakpoints = self.breakpoints.copy()

    def _clear_all_breakpoints(self):
        """Clear all breakpoints."""
        # Clear all breakpoints from editor
        for line_number in list(self.breakpoints):
            self.editor_text.set_breakpoint(line_number, False)

        # Clear set
        self.breakpoints.clear()

        # Update interpreter state if running
        if self.interpreter:
            self.interpreter.state.breakpoints = self.breakpoints.copy()

        self._set_status("All breakpoints cleared")

    def _create_variables_window(self):
        """Create variables watch window (Toplevel)."""
        import tkinter as tk
        from tkinter import ttk

        # Create window
        self.variables_window = tk.Toplevel(self.root)
        self.variables_window.title("Variables & Resources")
        self.variables_window.geometry("400x400")
        self.variables_window.protocol("WM_DELETE_WINDOW", lambda: self._close_variables())
        self.variables_window.withdraw()  # Hidden initially

        # Create resource usage frame at top
        resource_frame = tk.Frame(self.variables_window, relief=tk.SUNKEN, borderwidth=1)
        resource_frame.pack(fill=tk.X, padx=5, pady=5)

        # Resource usage label
        self.resource_label = tk.Label(resource_frame, text="Resource Usage: --",
                                       font=("Courier", 9), justify=tk.LEFT, anchor=tk.W)
        self.resource_label.pack(fill=tk.X, padx=5, pady=5)

        # Create Treeview
        tree = ttk.Treeview(self.variables_window, columns=('Type', 'Value'), show='tree headings')
        tree.heading('#0', text='Variable')
        tree.heading('Type', text='Type')
        tree.heading('Value', text='Value')
        tree.column('#0', width=100)
        tree.column('Type', width=100)
        tree.column('Value', width=200)
        tree.pack(fill=tk.BOTH, expand=True)

        self.variables_tree = tree

    def _toggle_variables(self):
        """Toggle variables window visibility (Ctrl+W)."""
        if self.variables_visible:
            # Window is shown - check if it's topmost
            try:
                # Try to raise/focus the window
                self.variables_window.lift()
                self.variables_window.focus_force()
            except:
                # If that fails, toggle visibility
                self.variables_window.withdraw()
                self.variables_visible = False
        else:
            self.variables_window.deiconify()
            self.variables_window.lift()
            self.variables_window.focus_force()
            self.variables_visible = True
            self._update_variables()

    def _close_variables(self):
        """Close variables window (called from X button)."""
        self.variables_window.withdraw()
        self.variables_visible = False

    def _update_variables(self):
        """Update variables window from runtime."""
        if not self.variables_visible or not self.runtime:
            return

        # Update resource usage
        if self.interpreter and hasattr(self.interpreter, 'limits'):
            limits = self.interpreter.limits

            # Format memory usage
            mem_pct = (limits.current_memory_usage / limits.max_total_memory * 100) if limits.max_total_memory > 0 else 0
            mem_text = f"Mem: {limits.current_memory_usage:,} / {limits.max_total_memory:,} ({mem_pct:.1f}%)"

            # Format stack depths
            gosub_text = f"GOSUB: {limits.current_gosub_depth}/{limits.max_gosub_depth}"
            for_text = f"FOR: {limits.current_for_depth}/{limits.max_for_depth}"
            while_text = f"WHILE: {limits.current_while_depth}/{limits.max_while_depth}"

            resource_text = f"{mem_text}\n{gosub_text}  {for_text}  {while_text}"
            self.resource_label.config(text=resource_text)
        else:
            self.resource_label.config(text="Resource Usage: --")

        # Clear tree
        for item in self.variables_tree.get_children():
            self.variables_tree.delete(item)

        # Get variables from runtime
        variables = self.runtime.get_all_variables()

        # Map type suffix to type name
        type_map = {
            '$': 'String',
            '%': 'Integer',
            '!': 'Single',
            '#': 'Double'
        }

        # Add to tree
        for var in sorted(variables, key=lambda v: v['name']):
            name = var['name'] + var['type_suffix']
            type_name = type_map.get(var['type_suffix'], 'Unknown')

            if var['is_array']:
                dims = 'x'.join(str(d) for d in var['dimensions'])
                value = f"Array({dims})"
            else:
                value = var['value']
                if var['type_suffix'] == '$':
                    value = f'"{value}"'

            self.variables_tree.insert('', 'end', text=name,
                                      values=(type_name, value))

    def _create_stack_window(self):
        """Create execution stack window (Toplevel)."""
        import tkinter as tk
        from tkinter import ttk

        # Create window
        self.stack_window = tk.Toplevel(self.root)
        self.stack_window.title("Execution Stack")
        self.stack_window.geometry("400x300")
        self.stack_window.protocol("WM_DELETE_WINDOW", lambda: self._close_stack())
        self.stack_window.withdraw()  # Hidden initially

        # Create Treeview
        tree = ttk.Treeview(self.stack_window, columns=('Details',), show='tree headings')
        tree.heading('#0', text='Type')
        tree.heading('Details', text='Details')
        tree.column('#0', width=100)
        tree.column('Details', width=300)
        tree.pack(fill=tk.BOTH, expand=True)

        self.stack_tree = tree

    def _toggle_stack(self):
        """Toggle execution stack window visibility (Ctrl+K)."""
        if self.stack_visible:
            # Window is shown - check if it's topmost
            try:
                # Try to raise/focus the window
                self.stack_window.lift()
                self.stack_window.focus_force()
            except:
                # If that fails, toggle visibility
                self.stack_window.withdraw()
                self.stack_visible = False
        else:
            self.stack_window.deiconify()
            self.stack_window.lift()
            self.stack_window.focus_force()
            self.stack_visible = True
            self._update_stack()

    def _close_stack(self):
        """Close execution stack window (called from X button)."""
        self.stack_window.withdraw()
        self.stack_visible = False

    def _update_stack(self):
        """Update execution stack window from runtime."""
        if not self.stack_visible:
            return

        # Get runtime - prefer interpreter.runtime if available (for tick-based execution)
        runtime = self.interpreter.runtime if (self.interpreter and hasattr(self.interpreter, 'runtime')) else self.runtime
        if not runtime:
            return

        # Clear tree
        for item in self.stack_tree.get_children():
            self.stack_tree.delete(item)

        # Get stack from runtime
        stack = runtime.get_execution_stack()

        # Show helpful message if stack is empty
        if not stack:
            # Get current line if available
            current_line = None
            if self.interpreter and hasattr(self.interpreter, 'state'):
                current_line = self.interpreter.state.current_line

            if current_line:
                text = "(No active control structures)"
                details = f"Stopped before executing line {current_line}"
            else:
                text = "(No active control structures)"
                details = "No FOR/WHILE/GOSUB active yet"

            self.stack_tree.insert('', 'end', text=text, values=(details,))
            return

        # Add to tree with indentation for nesting
        for i, entry in enumerate(stack):
            indent = "  " * i

            if entry['type'] == 'GOSUB':
                text = f"{indent}GOSUB"
                details = f"from line {entry['from_line']}"
            elif entry['type'] == 'FOR':
                text = f"{indent}FOR"
                var = entry['var']
                current = entry['current']
                end = entry['end']
                step = entry.get('step', 1)
                details = f"{var} = {current} TO {end} STEP {step}"
            elif entry['type'] == 'WHILE':
                text = f"{indent}WHILE"
                details = f"at line {entry['line']}"
            else:
                text = f"{indent}{entry['type']}"
                details = ""

            self.stack_tree.insert('', 'end', text=text, values=(details,))

    def _menu_clear_output(self):
        """Run > Clear Output"""
        import tkinter as tk
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

    def _menu_help(self):
        """Help > Help Topics (F1)"""
        from pathlib import Path
        from .tk_help_browser import TkHelpBrowser

        # Get help root directory
        help_root = Path(__file__).parent.parent.parent / "docs" / "help"

        # Create and show help browser window
        TkHelpBrowser(self.root, str(help_root), "ui/tk/index.md")

    def _menu_about(self):
        """Help > About"""
        import tkinter as tk
        from tkinter import messagebox

        # Get help key from config
        help_keys = self.keybindings.get_all_keys('menu', 'help_topics')
        help_key_text = ' or '.join(help_keys) if help_keys else 'Ctrl+?'

        messagebox.showinfo(
            "About MBASIC 5.21",
            "MBASIC 5.21 Interpreter\n\n"
            "A Python implementation of Microsoft BASIC 5.21\n\n"
            "Tkinter GUI Backend\n\n"
            f"Press {help_key_text} for help"
        )

    # Helper methods

    def _refresh_editor(self):
        """Load program into editor widget."""
        import tkinter as tk

        self.editor_text.delete(1.0, tk.END)
        for line_num, line_text in self.program.get_lines():
            self.editor_text.insert(tk.END, line_text + "\n")

        # Clear error indicators
        self.editor_text.clear_all_errors()

    def _save_editor_to_program(self):
        """Save editor content back to program."""
        import tkinter as tk

        # Clear current program
        self.program.clear()

        # Parse each line from editor
        editor_content = self.editor_text.get(1.0, tk.END)
        for line in editor_content.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Try to parse line number
            import re
            match = re.match(r'^(\d+)\s', line)
            if match:
                line_num = int(match.group(1))
                success, error = self.program.add_line(line_num, line)
                if not success:
                    self._add_output(f"Parse error at line {line_num}: {error}\n")

    def _add_output(self, text):
        """Add text to output widget."""
        import tkinter as tk

        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

        # Force Tk to process the update immediately
        self.output_text.update_idletasks()

    def _set_status(self, text):
        """Set status bar text."""
        self.status_label.config(text=text)

    def _execute_tick(self):
        """Execute one tick of the interpreter and schedule next tick if needed."""
        if not self.running or not self.interpreter:
            return

        try:
            # Execute one quantum of work
            state = self.interpreter.tick(mode='run', max_statements=100)

            # Output is routed to output pane via TkIOHandler

            # Handle different states
            if state.status == 'done':
                self.running = False
                self._add_output("\n--- Program finished ---\n")
                self._set_status("Ready")
                self._update_immediate_status()

            elif state.status == 'error':
                self.running = False
                error_msg = state.error_info.error_message if state.error_info else "Unknown error"
                line_num = state.error_info.error_line if state.error_info else "?"
                self._add_output(f"\n--- Runtime error at line {line_num}: {error_msg} ---\n")
                self._set_status("Error")
                self._update_immediate_status()

            elif state.status == 'at_breakpoint':
                self.running = False
                self.paused_at_breakpoint = True
                self._add_output(f"\n● Breakpoint hit at line {state.current_line}\n")
                self._set_status(f"Paused at line {state.current_line} - Ctrl+T=Step, Ctrl+G=Continue, Ctrl+X=Stop")
                self._update_immediate_status()
                if self.stack_visible:
                    self._update_stack()
                if self.variables_visible:
                    self._update_variables_window()

            elif state.status == 'paused':
                self.running = False
                self.paused_at_breakpoint = True
                self._add_output(f"\n→ Paused at line {state.current_line}\n")
                self._set_status(f"Paused at line {state.current_line} - Ctrl+T=Step, Ctrl+G=Continue, Ctrl+X=Stop")
                self._update_immediate_status()
                if self.stack_visible:
                    self._update_stack()
                if self.variables_visible:
                    self._update_variables_window()

            elif state.status == 'running':
                # Schedule next tick
                self.tick_timer_id = self.root.after(10, self._execute_tick)

        except Exception as e:
            import traceback
            self.running = False
            self._add_output(f"\n--- Execution error: {e} ---\n")
            self._add_output(traceback.format_exc())
            self._set_status("Error")

    # UIBackend interface methods

    def cmd_run(self) -> None:
        """Execute RUN command - run the program."""
        try:
            # Clear output
            self._menu_clear_output()
            self._set_status("Running...")

            # Get program AST
            program_ast = self.program.get_program_ast()

            # Create runtime and interpreter with local limits
            from resource_limits import create_local_limits
            self.runtime = Runtime(self.program.line_asts, self.program.lines)

            # Create Tk-specific IOHandler that outputs to output pane
            tk_io = TkIOHandler(self._add_output)
            self.interpreter = Interpreter(self.runtime, tk_io, limits=create_local_limits())

            # Start tick-based execution
            state = self.interpreter.start()
            if state.status == 'error':
                self._add_output(f"\n--- Setup error: {state.error_info.error_message if state.error_info else 'Unknown'} ---\n")
                self._set_status("Error")
                return

            # Set breakpoints if any
            if self.breakpoints:
                self.interpreter.state.breakpoints = self.breakpoints.copy()

            # Initialize immediate mode executor
            immediate_io = OutputCapturingIOHandler()
            self.immediate_executor = ImmediateExecutor(self.runtime, self.interpreter, immediate_io)
            self._update_immediate_status()

            # Start running
            self.running = True
            self.paused_at_breakpoint = False

            # Schedule first tick
            self.tick_timer_id = self.root.after(10, self._execute_tick)

        except Exception as e:
            import traceback
            self._add_output(f"\n--- Runtime error: {e} ---\n")
            self._add_output(traceback.format_exc())
            self._set_status("Error")

    def cmd_list(self, args: str = "") -> None:
        """Execute LIST command - list program lines."""
        self._menu_clear_output()
        lines = self.program.get_lines()
        for line_num, line_text in lines:
            self._add_output(line_text + "\n")

    def cmd_new(self) -> None:
        """Execute NEW command - clear program."""
        import tkinter as tk

        self.program.clear()
        self.editor_text.delete(1.0, tk.END)
        self._menu_clear_output()
        self._set_status("New program")

    def cmd_save(self, filename: str) -> None:
        """Execute SAVE command - save to file."""
        try:
            self.program.save_to_file(filename)
            self._set_status(f"Saved to {filename}")
        except Exception as e:
            self._add_output(f"Save error: {e}\n")
            self._set_status("Save error")

    def cmd_load(self, filename: str) -> None:
        """Execute LOAD command - load from file."""
        try:
            success, errors = self.program.load_from_file(filename)
            if errors:
                for line_num, error in errors:
                    self._add_output(f"Parse error at line {line_num}: {error}\n")
            if success:
                self._refresh_editor()
                self._set_status(f"Loaded from {filename}")
        except Exception as e:
            self._add_output(f"Load error: {e}\n")
            self._set_status("Load error")

    def cmd_delete(self, args: str) -> None:
        """Execute DELETE command - delete line range."""
        # TODO: Implement
        pass

    def cmd_renum(self, args: str) -> None:
        """Execute RENUM command - renumber lines."""
        # TODO: Implement
        pass

    def cmd_cont(self) -> None:
        """Execute CONT command - continue after STOP."""
        # TODO: Implement
        pass

    # Immediate mode methods

    def _update_immediate_status(self):
        """Update immediate mode panel status based on interpreter state."""
        import tkinter as tk

        if not self.immediate_executor or not self.immediate_status or not self.immediate_entry:
            return

        if self.immediate_executor.can_execute_immediate():
            # Safe to execute - enable input
            self.immediate_status.config(text="Ok", foreground="green")
            self.immediate_entry.config(state=tk.NORMAL)
        else:
            # Not safe - disable input
            status = self.interpreter.state.status if hasattr(self.interpreter, 'state') else 'unknown'
            self.immediate_status.config(text=f"[{status}]", foreground="red")
            self.immediate_entry.config(state=tk.DISABLED)

    def _execute_immediate(self):
        """Execute immediate mode command."""
        import tkinter as tk
        from tkinter import messagebox

        if not self.immediate_executor or not self.immediate_entry or not self.immediate_history:
            messagebox.showwarning("Warning", "Immediate mode not initialized")
            return

        command = self.immediate_entry.get().strip()
        if not command:
            return

        # Check if safe to execute
        if not self.immediate_executor.can_execute_immediate():
            self._add_immediate_output("Cannot execute while program is running\n")
            messagebox.showwarning("Warning", "Cannot execute while program is running")
            return

        # Log the command
        self._add_immediate_output(f"> {command}\n")

        # Execute
        success, output = self.immediate_executor.execute(command)

        # Log the result
        if output:
            self._add_immediate_output(output)

        if success:
            self._add_immediate_output("Ok\n")
        else:
            messagebox.showerror("Error", "Immediate mode error")

        # Clear input
        self.immediate_entry.delete(0, tk.END)

        # Update variables/stack windows if they exist
        if hasattr(self, 'variables_window') and self.variables_window:
            self._update_variables_window()
        if hasattr(self, 'stack_window') and self.stack_window and self.stack_visible:
            self._update_stack()

    def _add_immediate_output(self, text):
        """Add text to immediate mode history widget."""
        import tkinter as tk

        self.immediate_history.config(state=tk.NORMAL)
        self.immediate_history.insert(tk.END, text)
        self.immediate_history.see(tk.END)
        self.immediate_history.config(state=tk.DISABLED)

    def _setup_editor_context_menu(self):
        """Setup right-click context menu for editor text widget."""
        import tkinter as tk

        def show_context_menu(event):
            menu = tk.Menu(self.editor_text, tearoff=0)

            # Check if there's a selection
            try:
                if self.editor_text.text.tag_ranges(tk.SEL):
                    menu.add_command(label="Cut", command=self._menu_cut)
                    menu.add_command(label="Copy", command=self._menu_copy)
                    menu.add_separator()
            except tk.TclError:
                pass

            # Always offer paste and select all
            menu.add_command(label="Paste", command=self._menu_paste)
            menu.add_separator()
            menu.add_command(label="Select All", command=self._select_all_editor)

            # Dismissal
            def dismiss_menu():
                try:
                    menu.unpost()
                except:
                    pass

            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

            menu.bind("<FocusOut>", lambda e: dismiss_menu())
            menu.bind("<Escape>", lambda e: dismiss_menu())

        # Bind to the inner text widget
        self.editor_text.text.bind("<Button-3>", show_context_menu)

    def _select_all_editor(self):
        """Select all text in editor."""
        import tkinter as tk
        self.editor_text.text.tag_add(tk.SEL, "1.0", tk.END)
        self.editor_text.text.mark_set(tk.INSERT, "1.0")
        self.editor_text.text.see(tk.INSERT)

    def _setup_output_context_menu(self):
        """Setup right-click context menu for output text widget."""
        import tkinter as tk

        def show_context_menu(event):
            menu = tk.Menu(self.output_text, tearoff=0)

            # Check if there's a selection
            try:
                if self.output_text.tag_ranges(tk.SEL):
                    menu.add_command(label="Copy", command=self._copy_output_selection)
                    menu.add_separator()
            except tk.TclError:
                pass

            # Always offer select all
            menu.add_command(label="Select All", command=self._select_all_output)

            # Dismissal
            def dismiss_menu():
                try:
                    menu.unpost()
                except:
                    pass

            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

            menu.bind("<FocusOut>", lambda e: dismiss_menu())
            menu.bind("<Escape>", lambda e: dismiss_menu())

        self.output_text.bind("<Button-3>", show_context_menu)

    def _setup_immediate_context_menu(self):
        """Setup right-click context menu for immediate history widget."""
        import tkinter as tk

        def show_context_menu(event):
            menu = tk.Menu(self.immediate_history, tearoff=0)

            # Check if there's a selection
            try:
                if self.immediate_history.tag_ranges(tk.SEL):
                    menu.add_command(label="Copy", command=self._copy_immediate_selection)
                    menu.add_separator()
            except tk.TclError:
                pass

            # Always offer select all
            menu.add_command(label="Select All", command=self._select_all_immediate)

            # Dismissal
            def dismiss_menu():
                try:
                    menu.unpost()
                except:
                    pass

            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

            menu.bind("<FocusOut>", lambda e: dismiss_menu())
            menu.bind("<Escape>", lambda e: dismiss_menu())

        self.immediate_history.bind("<Button-3>", show_context_menu)

    def _copy_output_selection(self):
        """Copy selected text from output widget to clipboard."""
        import tkinter as tk
        try:
            selected_text = self.output_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except tk.TclError:
            pass  # No selection

    def _select_all_output(self):
        """Select all text in output widget."""
        import tkinter as tk
        self.output_text.tag_add(tk.SEL, "1.0", tk.END)
        self.output_text.mark_set(tk.INSERT, "1.0")
        self.output_text.see(tk.INSERT)

    def _copy_immediate_selection(self):
        """Copy selected text from immediate history widget to clipboard."""
        import tkinter as tk
        try:
            selected_text = self.immediate_history.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except tk.TclError:
            pass  # No selection

    def _select_all_immediate(self):
        """Select all text in immediate history widget."""
        import tkinter as tk
        self.immediate_history.tag_add(tk.SEL, "1.0", tk.END)
        self.immediate_history.mark_set(tk.INSERT, "1.0")
        self.immediate_history.see(tk.INSERT)


class TkIOHandler(IOHandler):
    """IOHandler that routes output to Tk output pane.
    
    This handler captures program output and sends it to the Tk UI's
    output text widget via a callback function.
    """
    
    def __init__(self, output_callback):
        """Initialize Tk IOHandler.
        
        Args:
            output_callback: Function to call with output text (str) -> None
        """
        self.output_callback = output_callback
        self.input_callback = None  # Will be set when INPUT is needed
        
    def output(self, text: str, end: str = '\n') -> None:
        """Output text to Tk output pane."""
        full_text = text + end
        if self.output_callback:
            self.output_callback(full_text)
    
    def input(self, prompt: str = '') -> str:
        """Input from user via dialog."""
        # TODO: Implement input dialog
        raise RuntimeError("INPUT not yet implemented in Tk UI")
    
    def input_line(self, prompt: str = '') -> str:
        """Input complete line from user via dialog."""
        # TODO: Implement input dialog
        raise RuntimeError("LINE INPUT not yet implemented in Tk UI")
    
    def input_char(self, blocking: bool = True) -> str:
        """Input single character."""
        # TODO: Implement character input
        if not blocking:
            return ""  # Non-blocking: no key available
        raise RuntimeError("INPUT$ not yet implemented in Tk UI")
    
    def clear_screen(self) -> None:
        """Clear screen - no-op for Tk UI."""
        pass
    
    def error(self, message: str) -> None:
        """Output error message."""
        if self.output_callback:
            self.output_callback(f"ERROR: {message}\n")
    
    def debug(self, message: str) -> None:
        """Output debug message."""
        if self.output_callback:
            self.output_callback(f"DEBUG: {message}\n")
