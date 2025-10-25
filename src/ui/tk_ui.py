"""Tkinter GUI backend for MBASIC interpreter.

This module provides a graphical UI using Python's tkinter library.
Tkinter provides a native GUI with buttons, menus, and text widgets,
making it suitable for a modern BASIC IDE experience.
"""

from .base import UIBackend
from runtime import Runtime
from interpreter import Interpreter


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

        # Runtime and interpreter for program execution
        self.runtime = None
        self.interpreter = None

        # Tick-based execution state
        self.running = False
        self.paused_at_breakpoint = False
        self.breakpoints = set()  # Set of line numbers with breakpoints
        self.tick_timer_id = None  # ID of pending after() call

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

        # Create main window
        self.root = tk.Tk()
        self.root.title("MBASIC 5.21 Interpreter")
        self.root.geometry("1000x600")

        # Create menu bar
        self._create_menu()

        # Create toolbar
        self._create_toolbar()

        # Create main content area (split pane)
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left pane: Editor
        editor_frame = ttk.Frame(paned)
        paned.add(editor_frame, weight=1)

        ttk.Label(editor_frame, text="Program Editor:").pack(anchor=tk.W, padx=5, pady=5)
        self.editor_text = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.NONE,
            width=60,
            height=30,
            font=("Courier", 10)
        )
        self.editor_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Right pane: Output
        output_frame = ttk.Frame(paned)
        paned.add(output_frame, weight=1)

        ttk.Label(output_frame, text="Output:").pack(anchor=tk.W, padx=5, pady=5)
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            width=60,
            height=30,
            font=("Courier", 10),
            state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Status bar
        self.status_label = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

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
        file_menu.add_command(label="New", command=self._menu_new, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self._menu_open, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self._menu_save, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self._menu_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._menu_exit)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=self._menu_cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self._menu_copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self._menu_paste, accelerator="Ctrl+V")

        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Program", command=self._menu_run, accelerator="Ctrl+R")
        run_menu.add_command(label="Step", command=self._menu_step, accelerator="Ctrl+T")
        run_menu.add_command(label="Continue", command=self._menu_continue, accelerator="Ctrl+G")
        run_menu.add_command(label="Stop", command=self._menu_stop, accelerator="Ctrl+X")
        run_menu.add_separator()
        run_menu.add_command(label="List Program", command=self._menu_list)
        run_menu.add_separator()
        run_menu.add_command(label="Clear Output", command=self._menu_clear_output)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._menu_about)

        # Bind keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self._menu_new())
        self.root.bind("<Control-o>", lambda e: self._menu_open())
        self.root.bind("<Control-s>", lambda e: self._menu_save())
        self.root.bind("<Control-r>", lambda e: self._menu_run())
        self.root.bind("<Control-t>", lambda e: self._menu_step())
        self.root.bind("<Control-g>", lambda e: self._menu_continue())
        # Note: Ctrl+X conflicts with Cut, so we'll check in the handler
        self.root.bind("<F5>", lambda e: self._menu_run())

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
        ttk.Button(toolbar, text="Run (F5)", command=self._menu_run).pack(side=tk.LEFT, padx=2, pady=2)
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

        except Exception as e:
            self._add_output(f"Stop error: {e}\n")
            self._set_status("Error")

    def _menu_clear_output(self):
        """Run > Clear Output"""
        import tkinter as tk
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

    def _menu_about(self):
        """Help > About"""
        import tkinter as tk
        from tkinter import messagebox

        messagebox.showinfo(
            "About MBASIC 5.21",
            "MBASIC 5.21 Interpreter\n\n"
            "A Python implementation of Microsoft BASIC 5.21\n\n"
            "Tkinter GUI Backend"
        )

    # Helper methods

    def _refresh_editor(self):
        """Load program into editor widget."""
        import tkinter as tk

        self.editor_text.delete(1.0, tk.END)
        for line_num, line_text in self.program.get_lines():
            self.editor_text.insert(tk.END, line_text + "\n")

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

            # Collect any output from io_handler
            # Note: For Tk, we should use a capturing IOHandler
            # For now, output goes to console

            # Handle different states
            if state.status == 'done':
                self.running = False
                self._add_output("\n--- Program finished ---\n")
                self._set_status("Ready")

            elif state.status == 'error':
                self.running = False
                error_msg = state.error_info.error_message if state.error_info else "Unknown error"
                line_num = state.error_info.error_line if state.error_info else "?"
                self._add_output(f"\n--- Runtime error at line {line_num}: {error_msg} ---\n")
                self._set_status("Error")

            elif state.status == 'at_breakpoint':
                self.running = False
                self.paused_at_breakpoint = True
                self._add_output(f"\n● Breakpoint hit at line {state.current_line}\n")
                self._set_status(f"Paused at line {state.current_line} - Ctrl+T=Step, Ctrl+G=Continue, Ctrl+X=Stop")

            elif state.status == 'paused':
                self.running = False
                self.paused_at_breakpoint = True
                self._add_output(f"\n→ Paused at line {state.current_line}\n")
                self._set_status(f"Paused at line {state.current_line} - Ctrl+T=Step, Ctrl+G=Continue, Ctrl+X=Stop")

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

            # Create runtime and interpreter
            self.runtime = Runtime(self.program.line_asts, self.program.lines)
            self.interpreter = Interpreter(self.runtime, self.io)

            # Start tick-based execution
            state = self.interpreter.start()
            if state.status == 'error':
                self._add_output(f"\n--- Setup error: {state.error_info.error_message if state.error_info else 'Unknown'} ---\n")
                self._set_status("Error")
                return

            # Set breakpoints if any
            if self.breakpoints:
                self.interpreter.state.breakpoints = self.breakpoints.copy()

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
