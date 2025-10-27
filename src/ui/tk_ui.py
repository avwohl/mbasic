"""Tkinter GUI backend for MBASIC interpreter.

This module provides a graphical UI using Python's tkinter library.
Tkinter provides a native GUI with buttons, menus, and text widgets,
making it suitable for a modern BASIC IDE experience.
"""

from .base import UIBackend
from runtime import Runtime
from interpreter import Interpreter
from .keybinding_loader import KeybindingLoader
from .recent_files import RecentFilesManager
from .auto_save import AutoSaveManager
from immediate_executor import ImmediateExecutor, OutputCapturingIOHandler
from iohandler.base import IOHandler
from input_sanitizer import sanitize_and_clear_parity, is_valid_input_char
from debug_logger import debug_log_error, is_debug_mode, debug_log


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

        # Recent files manager
        self.recent_files = RecentFilesManager()

        # Auto-save manager
        self.auto_save = AutoSaveManager()

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
        self.variables_sort_column = 'accessed'  # Current sort column: 'accessed', 'written', 'read', 'name', 'type', or 'value'
        self.variables_sort_reverse = True  # Sort direction: False=ascending, True=descending (default descending for timestamps)

        # Execution stack window state
        self.stack_window = None
        self.stack_tree = None
        self.stack_visible = False

        # Immediate mode
        self.immediate_executor = None
        self.immediate_history = None
        self.immediate_entry = None
        self.immediate_status = None

        # Editor auto-sort state
        self.last_edited_line_index = None  # Last editor line index (1-based)
        self.last_edited_line_text = None   # Content of last edited line

        # Editor auto-numbering configuration
        self.auto_number_enabled = True      # Enable auto-numbering
        self.auto_number_start = 10          # Starting line number
        self.auto_number_increment = 10      # Increment between lines

        # Tkinter widgets (created in start())
        self.root = None
        self.editor_text = None
        self.output_text = None
        self.status_label = None
        self.recent_files_menu = None  # Recent Files submenu
        self.variables_search_entry = None  # Variables window search entry
        self.variables_filter_text = ""  # Current filter text

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

        # Bind events for auto-sort on navigation
        self.editor_text.text.bind('<KeyRelease-Up>', self._on_cursor_move)
        self.editor_text.text.bind('<KeyRelease-Down>', self._on_cursor_move)
        self.editor_text.text.bind('<KeyRelease-Prior>', self._on_cursor_move)  # Page Up
        self.editor_text.text.bind('<KeyRelease-Next>', self._on_cursor_move)   # Page Down
        self.editor_text.text.bind('<Button-1>', self._on_mouse_click, add='+')
        self.editor_text.text.bind('<FocusOut>', self._on_focus_out)

        # Bind Enter key for auto-numbering
        self.editor_text.text.bind('<Return>', self._on_enter_key)

        # Bind Ctrl+I for smart insert line (must be on text widget to prevent tab)
        self.editor_text.text.bind('<Control-i>', self._on_ctrl_i)

        # Bind paste event for input sanitization
        self.editor_text.text.bind('<<Paste>>', self._on_paste)

        # Bind key press for input sanitization
        self.editor_text.text.bind('<Key>', self._on_key_press, add='+')

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

        # Bottom pane: Immediate Mode - just the input line
        immediate_frame = ttk.Frame(paned)
        paned.add(immediate_frame, weight=1)  # Reduced weight since no history

        # Immediate mode input (just the prompt and entry, no header or history)
        input_frame = ttk.Frame(immediate_frame, height=40)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        input_frame.pack_propagate(False)  # Force frame to maintain its height

        # Create the "Ok >" prompt label (saved to update color based on program state)
        self.immediate_prompt_label = tk.Label(input_frame, text="Ok >", font=("Courier", 10), fg="green")
        self.immediate_prompt_label.pack(side=tk.LEFT, padx=(0, 5))
        # Use tk.Entry instead of ttk.Entry for better input reliability
        # Explicitly set state, takefocus, and exportselection to ensure entry accepts input
        self.immediate_entry = tk.Entry(input_frame, font=("Courier", 10),
                                        state='normal', takefocus=True,
                                        exportselection=False)
        self.immediate_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.immediate_entry.bind('<Return>', lambda e: self._execute_immediate())

        # Add click handler to force focus when clicking in entry
        def on_entry_click(e):
            # Force focus to this widget when clicked
            self.immediate_entry.focus_force()
            # Also set the insert cursor at the click position
            self.immediate_entry.icursor(f"@{e.x}")
            return "break"  # Prevent event from propagating

        # Bind click handler
        self.immediate_entry.bind('<Button-1>', on_entry_click)

        # Add right-click context menu for immediate entry
        def show_immediate_context_menu(event):
            menu = tk.Menu(self.immediate_entry, tearoff=0)
            menu.add_command(label="Cut", command=lambda: self.immediate_entry.event_generate("<<Cut>>"))
            menu.add_command(label="Copy", command=lambda: self.immediate_entry.event_generate("<<Copy>>"))
            menu.add_command(label="Paste", command=lambda: self.immediate_entry.event_generate("<<Paste>>"))
            menu.add_separator()
            menu.add_command(label="Select All", command=lambda: self.immediate_entry.select_range(0, 'end'))
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        self.immediate_entry.bind('<Button-3>', show_immediate_context_menu)

        execute_btn = ttk.Button(input_frame, text="Execute", command=self._execute_immediate)
        execute_btn.pack(side=tk.LEFT)

        # Create dummy immediate_history and immediate_status for compatibility
        # (some code still references these)
        self.immediate_history = None
        self.immediate_status = None

        # Add right-click context menu for output only
        self._setup_output_context_menu()

        # Initialize immediate mode entry to be enabled and focused
        # (it will be enabled/disabled later based on program state via _update_immediate_status)
        self.immediate_entry.config(state=tk.NORMAL)

        # Ensure entry is above other widgets
        self.immediate_entry.lift()

        # Give initial focus to immediate entry for convenience
        def set_initial_focus():
            # Ensure all widgets are fully laid out
            self.root.update_idletasks()
            # Set focus to immediate entry
            self.immediate_entry.focus_force()

        # Try setting focus after a delay to ensure window is fully realized
        self.root.after(500, set_initial_focus)

        # Initialize runtime/interpreter for immediate mode and program execution
        # Create empty runtime that both immediate mode and programs will use
        from resource_limits import create_unlimited_limits
        self.runtime = Runtime({}, {})

        # Create IOHandler that outputs to output pane
        tk_io = TkIOHandler(self._add_output, self.root)
        self.interpreter = Interpreter(self.runtime, tk_io, limits=create_unlimited_limits())

        # Wire up interpreter to use Tk UI's command methods
        self.interpreter.interactive_mode = self

        # Initialize immediate executor to use the same runtime/interpreter
        immediate_io = OutputCapturingIOHandler()
        self.immediate_executor = ImmediateExecutor(runtime=self.runtime, interpreter=self.interpreter, io_handler=immediate_io)

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

        # Recent Files submenu
        self.recent_files_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_files_menu)
        self._update_recent_files_menu()

        file_menu.add_separator()
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
        edit_menu.add_command(label="Insert Line", command=self._smart_insert_line, accelerator="Ctrl+I")
        edit_menu.add_separator()
        edit_menu.add_command(label="Toggle Breakpoint", command=self._toggle_breakpoint, accelerator="Ctrl+B")
        edit_menu.add_command(label="Clear All Breakpoints", command=self._clear_all_breakpoints)

        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Program", command=self._menu_run,
                            accelerator=self.keybindings.get_tk_accelerator('menu', 'run_program'))
        run_menu.add_separator()
        run_menu.add_command(label="Step Line", command=self._menu_step_line)
        run_menu.add_command(label="Step Statement", command=self._menu_step)
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
        # Note: Ctrl+I is bound in start() after editor is created

    def _create_toolbar(self):
        """Create toolbar with common actions."""
        import tkinter as tk
        from tkinter import ttk

        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # File group
        ttk.Button(toolbar, text="New", command=self._menu_new).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(toolbar, text="Open", command=self._menu_open).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(toolbar, text="Save", command=self._menu_save).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Execution group
        ttk.Button(toolbar, text="Run", command=self._menu_run).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(toolbar, text="Stop", command=self._menu_stop).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Stepping group
        ttk.Button(toolbar, text="Step", command=self._menu_step_line).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(toolbar, text="Stmt", command=self._menu_step).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(toolbar, text="Cont", command=self._menu_continue).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Utility buttons removed - use menus instead:
        # - List → Run > List Program
        # - Clear Prog → File > New
        # - Clear Out → Run > Clear Output

    # Menu handlers

    def _menu_new(self):
        """File > New"""
        self.cmd_new()

    def _menu_open(self):
        """File > Open"""
        import tkinter as tk
        from tkinter import filedialog, messagebox

        filename = filedialog.askopenfilename(
            title="Open BASIC Program",
            filetypes=[("BASIC files", "*.bas"), ("All files", "*.*")]
        )
        if filename:
            # Check for autosave recovery
            if self.auto_save.is_autosave_newer(filename):
                prompt = self.auto_save.format_recovery_prompt(filename)
                if prompt:
                    response = messagebox.askyesno(
                        "Recover Auto-Save?",
                        prompt,
                        icon='question'
                    )
                    if response:
                        # Load from autosave
                        autosave_content = self.auto_save.load_autosave(filename)
                        if autosave_content:
                            # Load content into editor
                            self.editor_text.text.delete(1.0, tk.END)
                            self.editor_text.text.insert(1.0, autosave_content)
                            # Parse into program
                            self._save_editor_to_program()
                            # Set current file
                            self.program.current_file = filename
                            self._set_status(f"Recovered from autosave: {filename}")
                            # Add to recent files
                            self.recent_files.add_file(filename)
                            self._update_recent_files_menu()
                            # Start autosave
                            self.auto_save.start_autosave(
                                filename,
                                self._get_editor_content,
                                interval=30
                            )
                            return

            # Normal load (no recovery or user declined)
            self.cmd_load(filename)
            # Add to recent files
            self.recent_files.add_file(filename)
            self._update_recent_files_menu()

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
            # Add to recent files
            self.recent_files.add_file(filename)
            self._update_recent_files_menu()

    def _menu_exit(self):
        """File > Exit"""
        # Stop autosave
        self.auto_save.stop_autosave()
        # Clean up old autosaves (7+ days)
        self.auto_save.cleanup_old_autosaves()
        self.root.quit()

    def _update_recent_files_menu(self):
        """Update the Recent Files submenu with current list."""
        import tkinter as tk
        from pathlib import Path

        if not self.recent_files_menu:
            return

        # Clear existing menu items
        self.recent_files_menu.delete(0, tk.END)

        # Get recent files
        recent = self.recent_files.get_recent_files(max_count=10)

        if not recent:
            # No recent files
            self.recent_files_menu.add_command(label="(No recent files)", state=tk.DISABLED)
        else:
            # Add recent files
            for i, filepath in enumerate(recent, 1):
                # Show just the filename with accelerator number
                filename = Path(filepath).name
                # Add accelerator if within first 9 files (1-9 keys)
                if i <= 9:
                    label = f"{i}. {filename}"
                else:
                    label = f"   {filename}"

                self.recent_files_menu.add_command(
                    label=label,
                    command=lambda f=filepath: self._open_recent_file(f)
                )

            # Add separator and clear option
            self.recent_files_menu.add_separator()
            self.recent_files_menu.add_command(
                label="Clear Recent Files",
                command=self._clear_recent_files
            )

    def _open_recent_file(self, filepath):
        """Open a file from the recent files list.

        Args:
            filepath: Full path to file to open
        """
        from pathlib import Path
        import tkinter as tk
        from tkinter import messagebox

        # Check if file exists
        if not Path(filepath).exists():
            messagebox.showerror(
                "File Not Found",
                f"The file '{filepath}' no longer exists.\n\n"
                "It will be removed from the recent files list."
            )
            # Remove from recent files
            self.recent_files.remove_file(filepath)
            self._update_recent_files_menu()
            return

        # Check for autosave recovery
        if self.auto_save.is_autosave_newer(filepath):
            prompt = self.auto_save.format_recovery_prompt(filepath)
            if prompt:
                response = messagebox.askyesno(
                    "Recover Auto-Save?",
                    prompt,
                    icon='question'
                )
                if response:
                    # Load from autosave
                    autosave_content = self.auto_save.load_autosave(filepath)
                    if autosave_content:
                        # Load content into editor
                        self.editor_text.text.delete(1.0, tk.END)
                        self.editor_text.text.insert(1.0, autosave_content)
                        # Parse into program
                        self._save_editor_to_program()
                        # Set current file
                        self.program.current_file = filepath
                        self._set_status(f"Recovered from autosave: {filepath}")
                        # Update recent files
                        self.recent_files.add_file(filepath)
                        self._update_recent_files_menu()
                        # Start autosave
                        self.auto_save.start_autosave(
                            filepath,
                            self._get_editor_content,
                            interval=30
                        )
                        return

        # Load the file normally
        self.cmd_load(filepath)
        # Update recent files (moves to top)
        self.recent_files.add_file(filepath)
        self._update_recent_files_menu()

    def _clear_recent_files(self):
        """Clear the recent files list."""
        import tkinter as tk
        from tkinter import messagebox

        result = messagebox.askyesno(
            "Clear Recent Files",
            "Are you sure you want to clear the recent files list?"
        )
        if result:
            self.recent_files.clear()
            self._update_recent_files_menu()

    def _menu_cut(self):
        """Edit > Cut"""
        self.editor_text.event_generate("<<Cut>>")

    def _menu_copy(self):
        """Edit > Copy"""
        self.editor_text.event_generate("<<Copy>>")

    def _menu_paste(self):
        """Edit > Paste"""
        self.editor_text.text.event_generate("<<Paste>>")

    def _menu_run(self):
        """Run > Run Program"""
        success = self._save_editor_to_program()
        if not success:
            self._set_status("Cannot run - program has syntax errors")
            return
        self.cmd_run()

    def _menu_list(self):
        """Run > List Program"""
        self.cmd_list()

    def _menu_step_line(self):
        """Run > Step Line (execute all statements on current line)"""
        if not self.interpreter:
            self._set_status("No program running")
            return

        # Clear paused state to allow stepping through breakpoints
        self.paused_at_breakpoint = False

        try:
            state = self.interpreter.tick(mode='step_line', max_statements=100)

            # Handle state
            if state.status == 'paused' or state.status == 'at_breakpoint':
                self._add_output(f"→ Paused at line {state.current_line}\n")
                self._set_status(f"Paused at line {state.current_line}")
                # Set breakpoint flag if we hit one
                if state.status == 'at_breakpoint':
                    self.paused_at_breakpoint = True
                # Highlight current statement
                if state.current_statement_char_start > 0 or state.current_statement_char_end > 0:
                    self._highlight_current_statement(state.current_line, state.current_statement_char_start, state.current_statement_char_end)
            elif state.status == 'done':
                self._add_output("\n--- Program finished ---\n")
                self._set_status("Ready")
                self._clear_statement_highlight()
            elif state.status == 'error':
                error_msg = state.error_info.error_message if state.error_info else "Unknown error"
                line_num = state.error_info.error_line if state.error_info else "?"
                self._add_output(f"\n--- Error at line {line_num}: {error_msg} ---\n")
                self._set_status("Error")
                self._clear_statement_highlight()

            # Update immediate mode status
            self._update_immediate_status()

            # Update variables and stack windows if visible
            self._update_variables()
            self._update_stack()

        except Exception as e:
            self._add_output(f"Step error: {e}\n")
            self._set_status("Error")

    def _menu_step(self):
        """Run > Step Statement (execute one statement)"""
        if not self.interpreter:
            self._set_status("No program running")
            return

        # Clear paused state to allow stepping through breakpoints
        self.paused_at_breakpoint = False

        try:
            state = self.interpreter.tick(mode='step_statement', max_statements=1)

            # Handle state
            if state.status == 'paused' or state.status == 'at_breakpoint':
                stmt_info = f" statement {state.current_statement_index + 1}" if state.current_statement_index > 0 else ""
                self._add_output(f"→ Paused at line {state.current_line}{stmt_info}\n")
                self._set_status(f"Paused at line {state.current_line}{stmt_info}")
                # Set breakpoint flag if we hit one
                if state.status == 'at_breakpoint':
                    self.paused_at_breakpoint = True
                # Highlight current statement
                if state.current_statement_char_start > 0 or state.current_statement_char_end > 0:
                    self._highlight_current_statement(state.current_line, state.current_statement_char_start, state.current_statement_char_end)
            elif state.status == 'done':
                self._add_output("\n--- Program finished ---\n")
                self._set_status("Ready")
                self._clear_statement_highlight()
            elif state.status == 'error':
                error_msg = state.error_info.error_message if state.error_info else "Unknown error"
                line_num = state.error_info.error_line if state.error_info else "?"
                self._add_output(f"\n--- Error at line {line_num}: {error_msg} ---\n")
                self._set_status("Error")
                self._clear_statement_highlight()

            # Update immediate mode status
            self._update_immediate_status()

            # Update variables and stack windows if visible
            self._update_variables()
            self._update_stack()

        except Exception as e:
            self._add_output(f"Step error: {e}\n")
            self._set_status("Error")

    def _menu_continue(self):
        """Run > Continue (from breakpoint or error)"""
        import tkinter as tk
        from src.debug_logger import debug_log

        debug_log(f"_menu_continue called: interpreter={self.interpreter is not None}, paused={self.paused_at_breakpoint}", level=1)

        if not self.interpreter or not self.paused_at_breakpoint:
            self._set_status("Not paused")
            debug_log(f"Continue rejected: not paused", level=1)
            return

        try:
            # If we're continuing from an error, re-parse the program to incorporate edits
            if self.interpreter.state.status == 'error':
                debug_log(f"Continuing from error state", level=1)
                self._add_output("\n--- Re-parsing program after edit ---\n")

                # Clear all error markers first
                debug_log(f"Clearing all error markers", level=1)
                self.editor_text.clear_all_errors()

                # Get current editor text
                debug_log(f"Getting editor text", level=1)
                program_text = self.editor_text.get("1.0", tk.END)
                debug_log(f"Got {len(program_text)} chars of program text", level=1)

                # Parse the updated program
                from src.parser import Parser
                from src.lexer import Lexer
                try:
                    debug_log(f"Starting parse", level=1)
                    lexer = Lexer(program_text)
                    tokens = lexer.tokenize()
                    parser = Parser(tokens)
                    program = parser.parse()
                    debug_log(f"Parse successful, got {len(program.lines)} lines", level=1)
                except Exception as parse_error:
                    debug_log(f"Parse FAILED: {parse_error}", level=1)
                    self._add_output(f"Parse error: {parse_error}\n")
                    self._add_output("Fix the syntax error and try again.\n")
                    self._set_status("Parse error - fix and retry")
                    return

                # Update the interpreter's runtime with new program
                # Build line_table from ProgramNode.lines
                new_line_table = {}
                for line in program.lines:
                    new_line_table[line.line_number] = line
                new_line_order = sorted(new_line_table.keys())

                self.runtime.line_table = new_line_table
                self.runtime.line_order = new_line_order
                debug_log(f"Updated line_table with {len(new_line_table)} lines", level=1)

                # Clear error state and set to paused
                self.interpreter.state.status = 'paused'
                self.interpreter.state.error_info = None
                debug_log(f"Cleared error state, status now: {self.interpreter.state.status}", level=1)

                self._add_output("--- Program updated, resuming execution ---\n")

            # Resume execution
            self.running = True
            self.paused_at_breakpoint = False
            self._set_status("Continuing...")
            debug_log(f"Scheduling next tick, running={self.running}", level=1)

            # Schedule next tick
            self.tick_timer_id = self.root.after(10, self._execute_tick)
            debug_log(f"Next tick scheduled with timer_id={self.tick_timer_id}", level=1)

        except Exception as e:
            import traceback
            from src.debug_logger import debug_log
            debug_log(f"Continue EXCEPTION: {e}", level=1)
            debug_log(f"Traceback: {traceback.format_exc()}", level=1)
            self._add_output(f"Continue error: {e}\n")
            self._add_output(f"Traceback: {traceback.format_exc()}\n")
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

        # Create search/filter frame
        search_frame = tk.Frame(self.variables_window)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(search_frame, text="Filter:").pack(side=tk.LEFT, padx=(0, 5))
        self.variables_search_entry = tk.Entry(search_frame, font=("Courier", 10))
        self.variables_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.variables_search_entry.bind('<KeyRelease>', lambda e: self._on_variable_filter_change())

        ttk.Button(search_frame, text="Edit", command=self._edit_selected_variable, width=6).pack(side=tk.LEFT)

        # Create Treeview
        tree = ttk.Treeview(self.variables_window, columns=('Value', 'Type'), show='tree headings')
        # Set initial heading text with arrows
        tree.heading('#0', text='↓ Variable (Last Accessed)')
        tree.heading('Value', text='  Value')
        tree.heading('Type', text='  Type')
        tree.column('#0', width=180)
        tree.column('Value', width=140)
        tree.column('Type', width=80)
        tree.pack(fill=tk.BOTH, expand=True)

        # Bind click handler for heading clicks
        tree.bind('<Button-1>', self._on_variable_heading_click)

        # Bind double-click handler for editing variable values
        tree.bind('<Double-Button-1>', self._on_variable_double_click)

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

    def _on_variable_heading_click(self, event):
        """Handle clicks on variable list column headings.

        Arrow area (left ~20 pixels): Toggle sort direction
        Rest of heading: Cycle sort column (for Variable) or set column (for Type/Value)
        """
        # Identify which part of the tree was clicked
        region = self.variables_tree.identify_region(event.x, event.y)

        if region != 'heading':
            return  # Not a heading click, let normal handling continue

        # Identify which column heading was clicked
        column = self.variables_tree.identify_column(event.x)

        # Calculate x-coordinate relative to the start of the clicked column
        # to determine if we're clicking the arrow or the text
        if column == '#0':  # Tree column (Variable)
            col_x = event.x
        elif column == '#1':  # Value column (swapped to be first)
            col_x = event.x - self.variables_tree.column('#0', 'width')
        elif column == '#2':  # Type column (swapped to be second)
            col_x = event.x - self.variables_tree.column('#0', 'width') - self.variables_tree.column('Value', 'width')
        else:
            return

        # Click on arrow area (left 20 pixels) = toggle sort direction
        # Click on rest = cycle/set sort column
        ARROW_CLICK_WIDTH = 20
        if col_x < ARROW_CLICK_WIDTH:
            self._toggle_variable_sort_direction()
        else:
            if column == '#0':  # Variable column
                self._cycle_variable_sort()
            elif column == '#1':  # Value column (swapped)
                self._sort_variables_by('value')
            elif column == '#2':  # Type column (swapped)
                self._sort_variables_by('type')

    def _on_variable_double_click(self, event):
        """Handle double-click on variable to edit its value."""
        import tkinter as tk
        from tkinter import simpledialog
        import re

        # Check if we clicked on a row (accept 'tree' for first column or 'cell' for other columns)
        region = self.variables_tree.identify_region(event.x, event.y)
        if region not in ('cell', 'tree'):
            return

        # Get selected item
        selection = self.variables_tree.selection()
        if not selection:
            return

        item_id = selection[0]
        item_data = self.variables_tree.item(item_id)

        # Extract variable info from display
        variable_display = item_data['text']  # From #0 column (Variable)
        value_display = str(item_data['values'][0])  # Value column (swapped to first) - convert to string
        type_suffix_display = item_data['values'][1]  # Type column (swapped to second)

        # Parse variable name and type
        # Format examples: "A%", "NAME$", "X", "A%(10x10) [5,3]=42"
        if 'Array' in value_display:
            # Array variable - edit last accessed element
            self._edit_array_element(variable_display, type_suffix_display, value_display)
        else:
            # Simple variable
            self._edit_simple_variable(variable_display, type_suffix_display, value_display)

    def _edit_simple_variable(self, variable_name, type_suffix, current_value):
        """Edit a simple (non-array) variable.

        Args:
            variable_name: Variable name with type suffix (e.g., "A%", "NAME$")
            type_suffix: Type character ($, %, !, #, or empty)
            current_value: Current value as string
        """
        import tkinter as tk
        from tkinter import simpledialog, messagebox

        if not self.runtime:
            messagebox.showerror("Error", "Runtime not available")
            return

        # Determine dialog type based on type suffix
        if type_suffix == '$':
            # String variable
            # Remove quotes from display
            initial_value = current_value.strip('"')
            new_value = simpledialog.askstring(
                "Edit Variable",
                f"Enter new value for {variable_name}:",
                initialvalue=initial_value,
                parent=self.variables_window
            )
        elif type_suffix == '%':
            # Integer variable
            try:
                initial_value = int(float(current_value))  # Handle both "23" and "23.0"
            except ValueError:
                initial_value = 0
            new_value = simpledialog.askinteger(
                "Edit Variable",
                f"Enter new value for {variable_name}:",
                initialvalue=initial_value,
                parent=self.variables_window
            )
        else:
            # Float variable (single or double precision)
            # Show the current value as-is (already formatted nicely from display)
            new_value_str = simpledialog.askstring(
                "Edit Variable",
                f"Enter new value for {variable_name}:",
                initialvalue=current_value,
                parent=self.variables_window
            )
            if new_value_str is None:
                return  # User cancelled
            try:
                new_value = float(new_value_str)
            except ValueError:
                messagebox.showerror("Error", f"Invalid number: {new_value_str}")
                return

        if new_value is None:
            return  # User cancelled

        # Update runtime variable
        try:
            # Parse variable name (remove type suffix for runtime call)
            if variable_name[-1] in '$%!#':
                base_name = variable_name[:-1]
                suffix = variable_name[-1]
            else:
                base_name = variable_name
                suffix = None

            # Create a token with line=-1 to indicate immediate mode / variable editor
            class ImmediateModeToken:
                def __init__(self):
                    self.line = -1
                    self.position = None

            self.runtime.set_variable(
                base_name,
                suffix,
                new_value,
                token=ImmediateModeToken()
            )

            # Refresh variables window
            self._update_variables()

            # Show confirmation in status
            self.status_label.config(text=f"Variable {variable_name} updated to {new_value}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update variable: {e}")

    def _edit_array_element(self, variable_name, type_suffix, value_display):
        """Edit any array element by typing subscripts.

        Args:
            variable_name: Array name with type suffix (e.g., "A%")
            type_suffix: Type character ($, %, !, #, or empty)
            value_display: Display string like "Array(10x10) [5,3]=42"
        """
        import tkinter as tk
        from tkinter import messagebox
        import re

        if not self.runtime:
            messagebox.showerror("Error", "Runtime not available")
            return

        # Get array dimensions from display "Array(10x10)"
        dims_match = re.search(r'Array\(([^)]+)\)', value_display)
        dimensions_str = dims_match.group(1) if dims_match else "?"

        # Parse last accessed subscripts if available (for default value)
        default_subscripts = ""
        match = re.search(r'\[([^\]]+)\]=(.+)$', value_display)
        if match:
            default_subscripts = match.group(1)

        # Get array info from runtime
        base_name = variable_name[:-1] if variable_name[-1] in '$%!#' else variable_name
        suffix = variable_name[-1] if variable_name[-1] in '$%!#' else None

        # Get dimensions from runtime's _arrays dictionary
        full_name, _ = self.runtime._resolve_variable_name(base_name, suffix, None)
        dimensions = []
        if full_name in self.runtime._arrays:
            dimensions = self.runtime._arrays[full_name]['dims']

        # If no default subscripts, use first element based on array_base
        if not default_subscripts and dimensions:
            array_base = self.runtime.array_base
            if array_base == 0:
                # OPTION BASE 0: use all zeros
                default_subscripts = ','.join(['0'] * len(dimensions))
            else:
                # OPTION BASE 1: use all ones
                default_subscripts = ','.join(['1'] * len(dimensions))

        # Create custom dialog
        dialog = tk.Toplevel(self.variables_window)
        dialog.title(f"Edit Array Element: {variable_name}")
        dialog.geometry("450x280")
        dialog.transient(self.variables_window)

        # Wait for window to be visible before grabbing
        dialog.update_idletasks()
        dialog.grab_set()

        # Array info label
        tk.Label(dialog, text=f"Array: {variable_name}({dimensions_str})", font=('TkDefaultFont', 10, 'bold')).pack(pady=(10, 5))

        # Subscripts frame
        sub_frame = tk.Frame(dialog)
        sub_frame.pack(fill='x', padx=20, pady=5)
        tk.Label(sub_frame, text="Subscripts (e.g., 1,2,3):").pack(anchor='w')
        subscripts_entry = tk.Entry(sub_frame, width=40)
        subscripts_entry.pack(fill='x')
        subscripts_entry.insert(0, default_subscripts)

        # Current value label
        current_value_label = tk.Label(dialog, text="", fg='blue')
        current_value_label.pack(pady=5)

        # Error label
        error_label = tk.Label(dialog, text="", fg='red')
        error_label.pack(pady=2)

        # Value frame
        value_frame = tk.Frame(dialog)
        value_frame.pack(fill='x', padx=20, pady=5)
        tk.Label(value_frame, text="New value:").pack(anchor='w')
        value_entry = tk.Entry(value_frame, width=40)
        value_entry.pack(fill='x')

        result = {'cancelled': True}

        def update_current_value(*args):
            """Show current value when subscripts change and pre-fill the value entry."""
            subscripts_str = subscripts_entry.get().strip()
            if not subscripts_str:
                current_value_label.config(text="Enter subscripts above")
                error_label.config(text="")
                value_entry.delete(0, 'end')
                return

            try:
                # Parse subscripts
                subscripts = [int(s.strip()) for s in subscripts_str.split(',')]

                # Validate dimension count
                if dimensions and len(subscripts) != len(dimensions):
                    error_label.config(text=f"Expected {len(dimensions)} subscripts, got {len(subscripts)}")
                    current_value_label.config(text="")
                    value_entry.delete(0, 'end')
                    return

                # Validate bounds
                ordinals = ['1st', '2nd', '3rd', '4th']
                for i, sub in enumerate(subscripts):
                    if dimensions and i < len(dimensions):
                        if sub < 0 or sub > dimensions[i]:
                            ordinal = ordinals[i] if i < len(ordinals) else f"{i+1}th"
                            error_label.config(text=f"{ordinal} subscript out of bounds: {sub} not in [0, {dimensions[i]}]")
                            current_value_label.config(text="")
                            value_entry.delete(0, 'end')
                            return

                # Get current value using runtime's method
                current_val = self.runtime.get_array_element_for_debugger(base_name, suffix, subscripts, None)
                current_value_label.config(text=f"Current value: {current_val}")
                error_label.config(text="")

                # Pre-fill the value entry with current value
                value_entry.delete(0, 'end')
                if type_suffix == '$':
                    # String - insert as-is
                    value_entry.insert(0, str(current_val))
                elif type_suffix == '%' or (isinstance(current_val, (int, float)) and current_val == int(current_val)):
                    # Integer - show without decimal
                    value_entry.insert(0, str(int(current_val)))
                else:
                    # Float - show as-is
                    value_entry.insert(0, str(current_val))

            except ValueError:
                error_label.config(text="Invalid subscripts (must be integers)")
                current_value_label.config(text="")
                value_entry.delete(0, 'end')
            except Exception as e:
                error_label.config(text=f"Error: {str(e)}")
                current_value_label.config(text="")
                value_entry.delete(0, 'end')

        # Update current value when subscripts change
        subscripts_entry.bind('<KeyRelease>', update_current_value)

        # Initial update if we have default subscripts
        if default_subscripts:
            update_current_value()

        def on_ok():
            subscripts_str = subscripts_entry.get().strip()
            new_value_str = value_entry.get().strip()

            if not subscripts_str:
                error_label.config(text="Please enter subscripts")
                return

            if not new_value_str:
                error_label.config(text="Please enter a new value")
                return

            try:
                # Parse subscripts
                subscripts = [int(s.strip()) for s in subscripts_str.split(',')]

                # Convert value to appropriate type
                if type_suffix == '$':
                    new_value = new_value_str
                elif type_suffix == '%':
                    new_value = int(new_value_str)
                else:
                    new_value = float(new_value_str)

                # Create a token with line=-1 to indicate immediate mode / variable editor
                class ImmediateModeToken:
                    def __init__(self):
                        self.line = -1
                        self.position = None

                # Update array element
                self.runtime.set_array_element(
                    base_name,
                    suffix,
                    subscripts,
                    new_value,
                    token=ImmediateModeToken()
                )

                result['cancelled'] = False
                result['subscripts'] = subscripts_str
                result['value'] = new_value
                dialog.destroy()

            except ValueError as e:
                error_label.config(text=f"Invalid value: {str(e)}")
            except Exception as e:
                error_label.config(text=f"Error: {str(e)}")

        def on_cancel():
            dialog.destroy()

        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="OK", command=on_ok, width=10).pack(side='left', padx=5)
        tk.Button(button_frame, text="Cancel", command=on_cancel, width=10).pack(side='left', padx=5)

        # Focus on subscripts entry
        subscripts_entry.focus()
        subscripts_entry.select_range(0, 'end')

        # Wait for dialog
        dialog.wait_window()

        # Update display and show confirmation
        if not result['cancelled']:
            self._update_variables()
            self.status_label.config(text=f"Array {variable_name}({result['subscripts']}) updated to {result['value']}")

    def _toggle_variable_sort_direction(self):
        """Toggle sort direction (ascending/descending) without changing column."""
        self.variables_sort_reverse = not self.variables_sort_reverse
        self._update_variable_headings()
        self._update_variables()

    def _cycle_variable_sort(self):
        """Cycle through variable sort modes: accessed → written → read → name.

        Does not change sort direction - use arrow click for that.
        """
        cycle_order = ['accessed', 'written', 'read', 'name']
        try:
            current_idx = cycle_order.index(self.variables_sort_column)
            next_idx = (current_idx + 1) % len(cycle_order)
        except ValueError:
            next_idx = 0  # Default to accessed if current column not in cycle

        self.variables_sort_column = cycle_order[next_idx]

        # Update headers and display
        self._update_variable_headings()
        self._update_variables()

    def _sort_variables_by(self, column):
        """Set the sort column to the specified column.

        Does not change sort direction - use arrow click for that.

        Args:
            column: 'type' or 'value'
        """
        # Just set the column, don't change direction
        self.variables_sort_column = column

        # Update headers and display
        self._update_variable_headings()
        self._update_variables()

    def _update_variable_headings(self):
        """Update all variable window column headings to show current sort state."""
        # Determine arrow character based on sort direction
        arrow = '↓' if self.variables_sort_reverse else '↑'

        # Update Variable column heading (shows which sub-field we're sorting by)
        if self.variables_sort_column in ['accessed', 'written', 'read', 'name']:
            sort_labels = {
                'accessed': 'Last Accessed',
                'written': 'Last Written',
                'read': 'Last Read',
                'name': 'Name'
            }
            var_text = f'{arrow} Variable ({sort_labels[self.variables_sort_column]})'
            self.variables_tree.heading('#0', text=var_text)
            self.variables_tree.heading('Value', text='  Value')
            self.variables_tree.heading('Type', text='  Type')
        elif self.variables_sort_column == 'type':
            self.variables_tree.heading('#0', text='  Variable')
            self.variables_tree.heading('Value', text='  Value')
            self.variables_tree.heading('Type', text=f'{arrow} Type')
        elif self.variables_sort_column == 'value':
            self.variables_tree.heading('#0', text='  Variable')
            self.variables_tree.heading('Value', text=f'{arrow} Value')
            self.variables_tree.heading('Type', text='  Type')

    def _update_variables(self):
        """Update variables window from runtime."""
        if not self.variables_visible or not self.runtime:
            return

        runtime = self.runtime
        interpreter = self.interpreter

        # Update resource usage
        if interpreter and hasattr(interpreter, 'limits'):
            limits = interpreter.limits

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
        variables = runtime.get_all_variables()

        # Map type suffix to type name
        type_map = {
            '$': 'String',
            '%': 'Integer',
            '!': 'Single',
            '#': 'Double'
        }

        # Sort variables based on current sort settings
        if self.variables_sort_column == 'name':
            sort_key = lambda v: v['name'].lower()
        elif self.variables_sort_column == 'type':
            sort_key = lambda v: v['type_suffix']
        elif self.variables_sort_column == 'accessed':
            # Sort by most recent access (read or write)
            def accessed_sort_key(v):
                read_ts = v['last_read']['timestamp'] if v.get('last_read') else 0
                write_ts = v['last_write']['timestamp'] if v.get('last_write') else 0
                return max(read_ts, write_ts)
            sort_key = accessed_sort_key
        elif self.variables_sort_column == 'written':
            # Sort by most recent write
            sort_key = lambda v: v['last_write']['timestamp'] if v.get('last_write') else 0
        elif self.variables_sort_column == 'read':
            # Sort by most recent read
            sort_key = lambda v: v['last_read']['timestamp'] if v.get('last_read') else 0
        elif self.variables_sort_column == 'value':
            # For value sorting, handle arrays specially (sort them last)
            # For scalars, sort by numeric value or string value
            def value_sort_key(v):
                if v['is_array']:
                    return (2, 0, '')  # Arrays sort last
                elif v['type_suffix'] == '$':
                    return (1, 0, str(v['value']).lower())  # Strings sort alphabetically
                else:
                    try:
                        return (0, float(v['value']), '')  # Numbers sort numerically
                    except (ValueError, TypeError):
                        return (0, 0, '')
            sort_key = value_sort_key
        else:
            sort_key = lambda v: v['name'].lower()

        sorted_variables = sorted(variables, key=sort_key, reverse=self.variables_sort_reverse)

        # Apply filter if present
        if self.variables_filter_text:
            filter_lower = self.variables_filter_text.lower()
            filtered_variables = []
            for var in sorted_variables:
                name = var['name'] + var['type_suffix']
                # Check if filter matches name, value (as string), or type
                if (filter_lower in name.lower() or
                    filter_lower in str(var['value']).lower() or
                    filter_lower in type_map.get(var['type_suffix'], '').lower()):
                    filtered_variables.append(var)
            sorted_variables = filtered_variables

        # Update window title with count
        if self.variables_filter_text:
            self.variables_window.title(f"Variables & Resources ({len(sorted_variables)}/{len(variables)} filtered)")
        else:
            self.variables_window.title(f"Variables & Resources ({len(sorted_variables)} total)")

        # Add to tree
        for var in sorted_variables:
            name = var['name'] + var['type_suffix']
            type_name = type_map.get(var['type_suffix'], 'Unknown')

            if var['is_array']:
                # Enforce 4 dimension display limit
                dims = var['dimensions'][:4] if len(var['dimensions']) <= 4 else var['dimensions'][:4] + ['...']
                dims_str = 'x'.join(str(d) for d in dims)

                # Show last accessed cell and value if available
                if var.get('last_accessed_subscripts') and var.get('last_accessed_value') is not None:
                    subs = var['last_accessed_subscripts']
                    last_val = var['last_accessed_value']

                    # Format the value naturally
                    if var['type_suffix'] != '$' and isinstance(last_val, (int, float)) and last_val == int(last_val):
                        last_val_str = str(int(last_val))
                    elif var['type_suffix'] == '$':
                        last_val_str = f'"{last_val}"'
                    else:
                        last_val_str = str(last_val)

                    # Format subscripts
                    subs_str = ','.join(str(s) for s in subs)
                    value = f"Array({dims_str}) [{subs_str}]={last_val_str}"
                else:
                    value = f"Array({dims_str})"
            else:
                value = var['value']
                # Format numbers naturally - show integers without decimals
                if var['type_suffix'] != '$' and isinstance(value, (int, float)) and value == int(value):
                    value = str(int(value))
                elif var['type_suffix'] == '$':
                    value = f'"{value}"'

            self.variables_tree.insert('', 'end', text=name,
                                      values=(value, type_name))

    def _on_variable_filter_change(self):
        """Handle variable filter text change."""
        if self.variables_search_entry:
            self.variables_filter_text = self.variables_search_entry.get()
            self._update_variables()

    def _clear_variable_filter(self):
        """Clear the variable filter."""
        if self.variables_search_entry:
            self.variables_search_entry.delete(0, 'end')
            self.variables_filter_text = ""
            self._update_variables()

    def _edit_selected_variable(self):
        """Edit the currently selected variable (called by Edit button)."""
        from tkinter import messagebox

        # Get selected item
        selection = self.variables_tree.selection()
        if not selection:
            messagebox.showinfo("Edit Variable", "Please select a variable to edit")
            return

        item_id = selection[0]
        item_data = self.variables_tree.item(item_id)

        # Extract variable info from display
        variable_display = item_data['text']  # From #0 column (Variable)
        value_display = str(item_data['values'][0])  # Value column - convert to string
        type_suffix_display = item_data['values'][1]  # Type column

        # Call the appropriate edit function
        if 'Array' in value_display:
            # Array variable - edit last accessed element
            self._edit_array_element(variable_display, type_suffix_display, value_display)
        else:
            # Simple variable
            self._edit_simple_variable(variable_display, type_suffix_display, value_display)

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

        # Get runtime
        runtime = self.runtime
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

        # Add to tree (no indentation for easier debugging)
        for i, entry in enumerate(stack):
            if entry['type'] == 'GOSUB':
                text = "GOSUB"
                details = f"from line {entry['from_line']}"
            elif entry['type'] == 'FOR':
                text = "FOR"
                var = entry['var']
                current = entry['current']
                end = entry['end']
                step = entry.get('step', 1)
                # Format numbers naturally - show integers without decimals
                current_str = str(int(current)) if isinstance(current, (int, float)) and current == int(current) else str(current)
                end_str = str(int(end)) if isinstance(end, (int, float)) and end == int(end) else str(end)
                step_str = str(int(step)) if isinstance(step, (int, float)) and step == int(step) else str(step)
                # Only show STEP if it's not the default value of 1
                if step == 1:
                    details = f"{var} = {current_str} TO {end_str}"
                else:
                    details = f"{var} = {current_str} TO {end_str} STEP {step_str}"
            elif entry['type'] == 'WHILE':
                text = "WHILE"
                details = f"at line {entry['line']}"
            else:
                text = entry['type']
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
        """Load program into editor widget.

        Line numbers are part of the text content as entered by user.
        No formatting is applied to preserve compatibility with real MBASIC.
        """
        import tkinter as tk

        self.editor_text.text.delete(1.0, tk.END)
        for line_num, line_text in self.program.get_lines():
            # Insert line exactly as stored - no formatting
            # This preserves compatibility with real MBASIC
            self.editor_text.text.insert(tk.END, line_text + "\n")

        # Clear error indicators
        self.editor_text.clear_all_errors()

    def _save_editor_to_program(self):
        """Save editor content back to program.

        Returns:
            bool: True if all lines parsed successfully, False if any errors occurred
        """
        import tkinter as tk

        # Clear current program
        self.program.clear()

        # Parse each line from editor and track errors
        had_errors = False
        editor_content = self.editor_text.text.get(1.0, tk.END)
        for line in editor_content.split('\n'):
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Try to parse line number from stripped version
            import re
            match = re.match(r'^(\d+)(?:\s|$)', line_stripped)  # Whitespace or end of string
            if match:
                line_num = int(match.group(1))

                # Check if there's any content after the line number
                # Skip lines that are just a number (e.g., "20 " or "20")
                content_match = re.match(r'^\d+\s+(.+)', line_stripped)
                if not content_match or not content_match.group(1).strip():
                    # No content after line number - skip this line
                    continue

                # Save the original line (with formatting), not stripped
                success, error = self.program.add_line(line_num, line.rstrip('\r\n'))
                if not success:
                    self._add_output(f"Parse error at line {line_num}: {error}\n")
                    # Mark line as having error with message
                    self.editor_text.set_error(line_num, True, error)
                    had_errors = True
                else:
                    # Clear error marker if line is now valid
                    self.editor_text.set_error(line_num, False, None)

        return not had_errors

    def _validate_editor_syntax(self):
        """Validate syntax of all lines in editor and update error markers.

        Validates each line independently as entered - immediate feedback.
        """
        import tkinter as tk
        import re

        # Get editor content
        editor_content = self.editor_text.text.get(1.0, tk.END)

        # Clear existing error markers
        self.editor_text.clear_all_errors()

        # Collect errors to show in output
        errors_found = []

        # Check each line independently (immediate per-line validation)
        for line in editor_content.split('\n'):
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Try to parse line number
            match = re.match(r'^(\d+)\s+(.+)$', line_stripped)
            if match:
                line_num = int(match.group(1))
                code = match.group(2)

                # Check syntax - each line independently
                is_valid, error_msg = self._check_line_syntax(code)
                if not is_valid:
                    self.editor_text.set_error(line_num, True, error_msg)
                    errors_found.append((line_num, error_msg))

        # Show errors in output window if any found
        if errors_found:
            # Only show error list in output if there are multiple errors or this is the first time
            # Don't spam output on every keystroke
            should_show_list = len(errors_found) > 1
            if should_show_list:
                self._add_output("\n=== Syntax Errors ===\n")
                for line_num, error_msg in errors_found:
                    self._add_output(f"Line {line_num}: {error_msg}\n")
                self._add_output("===================\n")

            # Update status bar to show there are syntax errors
            error_count = len(errors_found)
            plural = "s" if error_count > 1 else ""
            self._set_status(f"Syntax error{plural} in program - cannot run")

            from debug_logger import debug_log
            debug_log(f"Validation found {error_count} error(s), status set", level=2)
        else:
            # No errors - clear any previous error status
            if hasattr(self, 'status_label') and self.status_label:
                current_status = self.status_label.cget('text')
                if 'Syntax error' in current_status:
                    self._set_status("Ready")

    def _check_line_syntax(self, code_text):
        """Check if a line of BASIC code has valid syntax.

        Args:
            code_text: The BASIC code (without line number)

        Returns:
            Tuple of (is_valid: bool, error_message: str or None)
        """
        if not code_text or not code_text.strip():
            return (True, None)

        try:
            from lexer import tokenize
            from parser import Parser

            # Add a dummy line number for parsing
            line_with_number = f"1 {code_text}"
            tokens = list(tokenize(line_with_number))
            parser = Parser(tokens, self.program.def_type_map, source=line_with_number)
            parser.parse_line()

            return (True, None)

        except Exception as e:
            # Strip "Parse error at line X, " prefix
            error_msg = str(e)
            import re
            error_msg = re.sub(r'^Parse error at line \d+, ', '', error_msg)
            return (False, error_msg)

    def _on_cursor_move(self, event):
        """Handle cursor movement (arrows, page up/down) - check for line change."""
        self._check_line_change()
        # Also validate syntax after movement
        self.root.after(100, self._validate_editor_syntax)

    def _on_mouse_click(self, event):
        """Handle mouse click - check for line change after click settles."""
        # Clear yellow statement highlight when clicking (allows text selection to be visible)
        if self.paused_at_breakpoint:
            self._clear_statement_highlight()
        # Use after() to check after click is processed
        self.root.after(10, self._check_line_change)
        # Also validate syntax after clicking (clears red ? when line is fixed)
        self.root.after(100, self._validate_editor_syntax)

    def _on_focus_out(self, event):
        """Handle focus leaving editor - check for line change."""
        self._check_line_change()
        # Validate syntax when leaving editor
        self._validate_editor_syntax()

    def _remove_blank_lines(self):
        """Remove all blank lines from the editor.

        This ensures the editor can NEVER contain blank lines.
        Called after any modification (typing, pasting, etc.)
        """
        import tkinter as tk

        # Get current cursor position
        cursor_pos = self.editor_text.text.index(tk.INSERT)

        # Get all content
        content = self.editor_text.text.get(1.0, tk.END)
        lines = content.split('\n')

        # Filter out blank lines (completely empty or only whitespace)
        # But keep the last line (which is always empty in Tk Text widget)
        filtered_lines = []
        removed_count = 0
        for i, line in enumerate(lines):
            # Keep non-blank lines
            if line.strip() or i == len(lines) - 1:
                filtered_lines.append(line)
            else:
                removed_count += 1

        # Check if we need to update
        if removed_count > 0:
            # Blank lines were found - remove them
            new_content = '\n'.join(filtered_lines)

            # Replace content
            self.editor_text.text.delete(1.0, tk.END)
            self.editor_text.text.insert(1.0, new_content)

            # Try to restore cursor position
            try:
                self.editor_text.text.mark_set(tk.INSERT, cursor_pos)
            except:
                # If position no longer exists, move to end
                self.editor_text.text.mark_set(tk.INSERT, tk.END)

    def _on_enter_key(self, event):
        """Handle Enter key - auto-number current line and move to next.

        Returns:
            'break' to prevent default Enter behavior
        """
        import tkinter as tk
        import re
        from lexer import tokenize
        from parser import Parser

        if not self.auto_number_enabled:
            return None  # Allow default behavior

        # Get current line
        current_pos = self.editor_text.text.index(tk.INSERT)
        current_line_index = int(current_pos.split('.')[0])
        current_line_text = self.editor_text.text.get(
            f'{current_line_index}.0',
            f'{current_line_index}.end'
        ).strip()

        # If line is completely blank, don't do anything (prevent blank lines)
        if not current_line_text:
            return 'break'

        # Check if line is just a line number with no content (e.g., "20 ")
        # This happens when Enter is pressed on the auto-generated prompt
        match_number_only = re.match(r'^\s*(\d+)\s*$', current_line_text)
        if match_number_only:
            # Line has only a number, no code - remove it and don't create another blank line
            self.editor_text.text.delete(f'{current_line_index}.0', f'{current_line_index}.end')
            # Also remove the newline if this isn't the last line
            try:
                self.editor_text.text.delete(f'{current_line_index}.0', f'{current_line_index+1}.0')
            except:
                pass
            return 'break'

        # Check if line already has a line number with content
        match = re.match(r'^\s*(\d+)\s+(.+)', current_line_text)
        if match:
            # Already has line number - just save and move to next line
            current_line_num = int(match.group(1))
        else:
            # No line number - try to add one
            try:
                # Validate it's valid BASIC
                test_line = f"1 {current_line_text}"
                tokens = list(tokenize(test_line))
                parser = Parser(tokens, self.program.def_type_map, source=test_line)
                parser.parse_line()

                # Valid BASIC - find next line number
                if self.program and self.program.has_lines():
                    existing_lines = self.program.get_all_line_numbers()
                    current_line_num = max(existing_lines) + self.auto_number_increment
                else:
                    current_line_num = self.auto_number_start

                # Replace current line with numbered version
                numbered_line = f"{current_line_num} {current_line_text}"
                self.editor_text.text.delete(f'{current_line_index}.0', f'{current_line_index}.end')
                self.editor_text.text.insert(f'{current_line_index}.0', numbered_line)

            except Exception:
                # Not valid BASIC - don't auto-number, just move to next line
                self.editor_text.text.insert(tk.INSERT, '\n')
                return 'break'

        # Save current program state
        success = self._save_editor_to_program()

        # If there were parse errors, don't refresh (keeps error lines visible)
        if not success:
            # Don't refresh - let user fix the error
            # Just move cursor to end of current line
            self.editor_text.text.mark_set(tk.INSERT, f'{current_line_index}.end')
            return 'break'

        # Refresh to sort lines (only if no errors)
        self._refresh_editor()

        # At this point, the editor contains only the numbered lines (no blank lines)
        # because _refresh_editor loads from the program, which filters out blank lines

        # Calculate the next line number for the prompt
        next_line_num = current_line_num + self.auto_number_increment

        # Check if we're already at the end of a line with content
        # If the last character is NOT a newline, add one
        last_char = self.editor_text.text.get("end-2c", "end-1c")
        if last_char != '\n':
            self.editor_text.text.insert(tk.END, '\n')

        # Insert the next line number prompt (like classic BASIC)
        self.editor_text.text.insert(tk.END, f'{next_line_num} ')

        # Move cursor to end (after the line number)
        self.editor_text.text.mark_set(tk.INSERT, tk.END)
        self.editor_text.text.see(tk.END)

        return 'break'  # Prevent default Enter behavior

    def _on_paste(self, event):
        """Handle paste event - sanitize clipboard content.

        Returns:
            'break' to prevent default paste, None to allow it
        """
        import tkinter as tk

        try:
            # Get clipboard content
            clipboard_text = self.root.clipboard_get()

            # Sanitize: clear parity bits and filter control characters
            sanitized_text, was_modified = sanitize_and_clear_parity(clipboard_text)

            # Remove blank lines and auto-number lines without line numbers
            import re
            from lexer import tokenize
            from parser import Parser

            lines = sanitized_text.split('\n')
            filtered_lines = []
            removed_blank = False
            removed_invalid = False
            added_line_numbers = False

            # Start with default auto-number or find highest existing line number
            next_line_num = self.auto_number_start

            # Check highest line number in existing program
            if self.program and self.program.has_lines():
                existing_lines = self.program.get_all_line_numbers()
                if existing_lines:
                    highest_existing = max(existing_lines)
                    next_line_num = max(next_line_num, highest_existing + self.auto_number_increment)

            # First pass - find highest line number in pasted content
            for line in lines:
                stripped = line.strip()
                if stripped:
                    match = re.match(r'^\s*(\d+)', stripped)
                    if match:
                        line_num = int(match.group(1))
                        next_line_num = max(next_line_num, line_num + self.auto_number_increment)

            # Second pass - process lines
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    # Blank line
                    if line != lines[-1]:
                        removed_blank = True
                    continue

                # Check if line starts with a line number
                if not re.match(r'^\s*\d+', stripped):
                    # Line without line number - try to auto-number it
                    # First check if it would be valid BASIC code
                    try:
                        test_line = f"1 {stripped}"
                        tokens = list(tokenize(test_line))
                        parser = Parser(tokens, self.program.def_type_map, source=test_line)
                        parser.parse_line()

                        # Valid BASIC code - add line number
                        numbered_line = f"{next_line_num} {stripped}"
                        filtered_lines.append(numbered_line)
                        next_line_num += self.auto_number_increment
                        added_line_numbers = True
                    except Exception:
                        # Invalid BASIC code - reject it
                        removed_invalid = True
                    continue

                # Valid line with line number - keep it
                filtered_lines.append(line)

            sanitized_text = '\n'.join(filtered_lines)

            # Add back trailing newline if original had one
            if clipboard_text.endswith('\n'):
                sanitized_text += '\n'

            if was_modified or removed_blank or removed_invalid or added_line_numbers:
                # Show warning that content was modified
                msg = []
                if was_modified:
                    msg.append("control characters removed")
                if removed_blank:
                    msg.append("blank lines removed")
                if added_line_numbers:
                    msg.append("line numbers added")
                if removed_invalid:
                    msg.append("invalid lines removed")
                self._set_status(f"Pasted content was sanitized ({', '.join(msg)})")

            # Insert sanitized text at cursor position
            try:
                # Delete selected text if any
                self.editor_text.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                # No selection, just insert
                pass

            self.editor_text.text.insert(tk.INSERT, sanitized_text)

            # Prevent default paste behavior
            return 'break'

        except tk.TclError:
            # Clipboard empty or error - allow default behavior
            return None

    def _on_key_press(self, event):
        """Handle key press - filter invalid characters.

        Returns:
            'break' to prevent character insertion, None to allow it
        """
        # Clear yellow statement highlight when user starts editing
        # This prevents the "half yellow line" issue when editing error/breakpoint lines
        if self.paused_at_breakpoint:
            self._clear_statement_highlight()

        # Schedule blank line removal after key is processed
        self.root.after(10, self._remove_blank_lines)

        # Ignore special keys (arrows, function keys, modifiers, etc.)
        if len(event.char) != 1:
            return None

        # Allow editing keys (backspace, delete) - these modify text but aren't input
        char_code = ord(event.char)
        if char_code in (8, 127):  # Backspace (0x08) or Delete (0x7F)
            return None

        # Allow keyboard shortcuts with modifier keys (Control, Alt, etc.) to propagate
        # This ensures shortcuts like Ctrl+B, Ctrl+S, etc. reach their handlers
        # event.state contains modifier flags:
        # 0x0004 = Control, 0x0008 = Alt/Option, 0x0001 = Shift
        if event.state & 0x000C:  # Control or Alt pressed
            return None

        # Clear parity bit
        from input_sanitizer import clear_parity
        char = clear_parity(event.char)

        # Check if character is valid
        if not is_valid_input_char(char):
            # Block invalid character
            return 'break'

        # If parity bit was set, insert the cleared character instead
        if char != event.char:
            import tkinter as tk
            self.editor_text.text.insert(tk.INSERT, char)
            return 'break'

        # Allow valid character
        return None

    def _check_line_change(self):
        """Check if cursor moved off a line and trigger auto-sort if line number changed."""
        import tkinter as tk
        import re

        # Get current cursor position
        current_pos = self.editor_text.text.index(tk.INSERT)
        current_line_index = int(current_pos.split('.')[0])

        # If no previous line tracked, just update tracking
        if self.last_edited_line_index is None:
            self.last_edited_line_index = current_line_index
            self.last_edited_line_text = self.editor_text.text.get(
                f'{current_line_index}.0',
                f'{current_line_index}.end'
            )
            return

        # If still on same line, update tracking
        if current_line_index == self.last_edited_line_index:
            self.last_edited_line_text = self.editor_text.text.get(
                f'{current_line_index}.0',
                f'{current_line_index}.end'
            )
            return

        # Moved to different line - check if previous line's line number changed
        try:
            current_text = self.editor_text.text.get(
                f'{self.last_edited_line_index}.0',
                f'{self.last_edited_line_index}.end'
            )
        except tk.TclError:
            # Line no longer exists
            current_text = ""

        # Parse line numbers from old and new text
        old_match = re.match(r'^\s*(\d+)', self.last_edited_line_text) if self.last_edited_line_text else None
        new_match = re.match(r'^\s*(\d+)', current_text) if current_text else None

        old_line_num = int(old_match.group(1)) if old_match else None
        new_line_num = int(new_match.group(1)) if new_match else None

        # Trigger sort if:
        # 1. Line number changed on existing line (both old and new are not None), OR
        # 2. Line number was removed (old was not None, new is None and line has content)
        # DON'T sort if just clicking around without editing (old is None means we're just tracking)
        should_sort = False

        if old_line_num != new_line_num:
            if old_line_num is not None and new_line_num is not None:
                # Line number actually changed (user edited the number)
                should_sort = True
            elif old_line_num is not None and new_line_num is None and current_text.strip():
                # Line number was removed but line has content
                should_sort = True
            # If old_line_num is None, we're just clicking around, don't sort

        if should_sort:
            # Save editor to program (which parses all lines)
            success = self._save_editor_to_program()

            # Only refresh and sort if all lines parsed successfully
            # If there were errors, keep the editor as-is so user can fix them
            if success:
                # Refresh editor (which sorts by line number)
                self._refresh_editor()

                # Scroll to show the edited line in its new position
                self._scroll_to_line(new_line_num)

        # Update tracking for new line
        self.last_edited_line_index = current_line_index
        self.last_edited_line_text = self.editor_text.text.get(
            f'{current_line_index}.0',
            f'{current_line_index}.end'
        )

        # Check if current line has an error and display message
        current_line_text = self.editor_text.text.get(
            f'{current_line_index}.0',
            f'{current_line_index}.end'
        )
        match = re.match(r'^\s*(\d+)', current_line_text)
        if match:
            line_num = int(match.group(1))
            error_msg = self.editor_text.get_error_message(line_num)
            if error_msg:
                self._set_status(f"Error on line {line_num}: {error_msg}")
            else:
                # Current line is OK, but check if there are errors elsewhere in program
                if hasattr(self.editor_text, 'errors') and self.editor_text.errors:
                    error_count = len(self.editor_text.errors)
                    plural = "s" if error_count > 1 else ""
                    self._set_status(f"Syntax error{plural} in program - cannot run")

    def _on_ctrl_i(self, event=None):
        """Handle Ctrl+I - smart insert line.

        Returns 'break' to prevent tab insertion.
        """
        from debug_logger import debug_log
        debug_log("Ctrl+I handler called", level=1)
        self._smart_insert_line()
        debug_log("Ctrl+I handler returning 'break'", level=1)
        return 'break'

    def _smart_insert_line(self):
        """Smart insert - insert blank line between current and next line.

        Uses ui_helpers to calculate appropriate line number:
        - If gap exists, inserts at midpoint
        - If no gap, offers to renumber

        Triggered by Ctrl+I keyboard shortcut.
        """
        import tkinter as tk
        from tkinter import messagebox
        from ui.ui_helpers import calculate_midpoint, find_insert_line_number, needs_renumber_for_insert
        from debug_logger import debug_log
        import re

        # Get current line
        current_pos = self.editor_text.text.index(tk.INSERT)
        current_line_index = int(current_pos.split('.')[0])
        current_line_text = self.editor_text.text.get(
            f'{current_line_index}.0',
            f'{current_line_index}.end'
        ).strip()

        debug_log(f"Smart insert: line_index={current_line_index}, text={repr(current_line_text)}", level=1)

        # Parse current line number
        match = re.match(r'^(\d+)', current_line_text)
        if not match:
            debug_log(f"No match for line number in: {repr(current_line_text)}", level=1)
            messagebox.showinfo("Smart Insert", "Current line has no line number.\nAdd a line number first.")
            return

        current_line_num = int(match.group(1))
        debug_log(f"Current line number: {current_line_num}", level=1)

        # Get all line numbers sorted - parse directly from editor text
        all_line_numbers = []
        editor_content = self.editor_text.text.get('1.0', 'end')
        for line in editor_content.split('\n'):
            line_match = re.match(r'^\s*(\d+)', line)
            if line_match:
                all_line_numbers.append(int(line_match.group(1)))

        all_line_numbers = sorted(set(all_line_numbers))  # Remove duplicates and sort

        if not all_line_numbers:
            messagebox.showinfo("Smart Insert", "No program lines found.")
            return

        # Find the previous line before current (to insert between prev and current)
        prev_line_num = None
        for line_num in reversed(all_line_numbers):
            if line_num < current_line_num:
                prev_line_num = line_num
                break

        # Calculate insertion point (insert BEFORE current line)
        if prev_line_num is None:
            # At beginning of program - use current minus increment
            insert_num = max(1, current_line_num - self.auto_number_increment)
            # Make sure we don't conflict with current
            if insert_num >= current_line_num:
                insert_num = current_line_num - 1 if current_line_num > 1 else 1
        else:
            # Between previous and current lines - try midpoint
            midpoint = calculate_midpoint(prev_line_num, current_line_num)
            if midpoint is not None:
                insert_num = midpoint
            else:
                # No room - offer to renumber
                response = messagebox.askyesno(
                    "No Room",
                    f"No room between lines {prev_line_num} and {current_line_num}.\n\n"
                    f"Would you like to renumber the program to make room?"
                )
                if response:
                    # Renumber to make room
                    self._save_editor_to_program()
                    self.cmd_renum(f"10,0,10")
                    self._refresh_editor()
                return

        # Insert blank line BEFORE current line (at current line's position)
        # The new line will be inserted at the current line's text position,
        # pushing the current line down
        insert_index = current_line_index

        # Insert the new blank line
        new_line_text = f'{insert_num} \n'
        self.editor_text.text.insert(f'{insert_index}.0', new_line_text)

        # Trigger save and sort (this will reorder all lines by line number)
        success = self._save_editor_to_program()
        if not success:
            # Parse errors exist - don't refresh to preserve user's work
            # Just position cursor at the new line we inserted
            self.editor_text.text.mark_set('insert', f'{insert_index}.end')
            return

        self._refresh_editor()

        # After refresh, find where the new line ended up and position cursor there
        # Search for the line with our inserted line number
        editor_content = self.editor_text.text.get('1.0', 'end')
        lines = editor_content.split('\n')
        for idx, line in enumerate(lines):
            line_match = re.match(r'^\s*(\d+)', line)
            if line_match and int(line_match.group(1)) == insert_num:
                # Found our inserted line, position cursor after the line number AND space
                text_line_num = idx + 1  # Tk uses 1-based line numbers
                # Find position after line number and following space
                # Line format is "   25 " or "   25 PRINT" - find the space after digits
                after_number_match = re.match(r'^\s*\d+\s+', line)
                if after_number_match:
                    cursor_col = len(after_number_match.group(0))
                else:
                    # No space after number, position after the number
                    cursor_col = len(line_match.group(0))
                self.editor_text.text.mark_set(tk.INSERT, f'{text_line_num}.{cursor_col}')
                self.editor_text.text.see(f'{text_line_num}.0')  # Scroll to show it
                break

    def _scroll_to_line(self, line_number):
        """Scroll editor to show the specified BASIC line number.

        Args:
            line_number: BASIC line number to scroll to
        """
        import tkinter as tk

        # Find which editor line contains this BASIC line number
        editor_content = self.editor_text.text.get(1.0, tk.END)
        editor_lines = editor_content.split('\n')

        import re
        for i, line_text in enumerate(editor_lines):
            match = re.match(r'^\s*(\d+)', line_text)
            if match and int(match.group(1)) == line_number:
                # Found it - scroll to this line (1-indexed)
                editor_line_index = i + 1
                self.editor_text.text.see(f'{editor_line_index}.0')
                # Set cursor at start of code (after line number)
                # Find where code starts (after line number and space)
                code_start_match = re.match(r'^\s*\d+\s+', line_text)
                if code_start_match:
                    col = len(code_start_match.group(0))
                else:
                    col = 0
                self.editor_text.text.mark_set(tk.INSERT, f'{editor_line_index}.{col}')
                break

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

    def _highlight_current_statement(self, line_number, char_start, char_end):
        """Highlight the current statement being executed in the editor.

        Args:
            line_number: BASIC line number (e.g., 10, 20, 30)
            char_start: Character position from start of line
            char_end: Character position end
        """
        if not self.editor_text or not line_number:
            return

        # Configure highlighting tag if not already configured
        if 'current_statement' not in self.editor_text.text.tag_names():
            self.editor_text.text.tag_config(
                'current_statement',
                background='#ffeb3b',  # Yellow highlight
                foreground='black'
            )

        # Clear previous highlighting
        self._clear_statement_highlight()

        # Find the editor line containing this BASIC line number
        editor_content = self.editor_text.text.get('1.0', 'end')
        lines = editor_content.split('\n')

        for editor_line_idx, line_text in enumerate(lines, 1):
            # Check if this line starts with the BASIC line number
            import re
            match = re.match(r'^\s*(\d+)', line_text)
            if match and int(match.group(1)) == line_number:
                # Found the line - use char positions directly
                # Lines are displayed exactly as stored, so char_start/char_end
                # are relative to the line as displayed

                start_idx = f"{editor_line_idx}.{char_start}"
                end_idx = f"{editor_line_idx}.{char_end}"

                try:
                    self.editor_text.text.tag_add('current_statement', start_idx, end_idx)
                    # Scroll to make the statement visible
                    self.editor_text.text.see(start_idx)
                except tk.TclError:
                    # Invalid index - ignore
                    pass

                break

    def _clear_statement_highlight(self):
        """Remove statement highlighting from the editor."""
        if self.editor_text and 'current_statement' in self.editor_text.text.tag_names():
            self.editor_text.text.tag_remove('current_statement', '1.0', 'end')

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
                self._clear_statement_highlight()

            elif state.status == 'error':
                self.running = False
                self.paused_at_breakpoint = True  # Allow Continue to work after error
                error_msg = state.error_info.error_message if state.error_info else "Unknown error"
                line_num = state.error_info.error_line if state.error_info else "?"
                self._add_output(f"\n--- Execution error: {error_msg} ---\n")
                self._add_output("(Edit the line and click Continue to retry, or Stop to end)\n")
                self._set_status(f"Error at line {line_num} - Edit and Continue, or Stop")
                self._update_immediate_status()

                # Highlight the error statement (yellow highlight)
                from src.debug_logger import debug_log
                debug_log(f"Error state: line={state.current_line}, char_start={state.current_statement_char_start}, char_end={state.current_statement_char_end}", level=1)
                if state.current_statement_char_start > 0 or state.current_statement_char_end > 0:
                    debug_log(f"Highlighting error statement", level=1)
                    self._highlight_current_statement(state.current_line, state.current_statement_char_start, state.current_statement_char_end)
                else:
                    debug_log(f"NOT highlighting - char positions are 0", level=1)

                # Mark the error line with red ? indicator
                if line_num and line_num != "?":
                    try:
                        line_num_int = int(line_num)
                        from src.debug_logger import debug_log
                        debug_log(f"Setting error marker on line {line_num_int}: {error_msg}", level=1)
                        self.editor_text.set_error(line_num_int, True, error_msg)
                        debug_log(f"Error marker set successfully", level=1)
                    except (ValueError, AttributeError, TypeError) as e:
                        from src.debug_logger import debug_log
                        debug_log(f"Failed to set error marker: {e}", level=1)

                # Update stack and variables to show state at error
                if self.stack_visible:
                    self._update_stack()
                if self.variables_visible:
                    self._update_variables()

            elif state.status == 'at_breakpoint':
                self.running = False
                self.paused_at_breakpoint = True
                self._add_output(f"\n● Breakpoint hit at line {state.current_line}\n")
                self._set_status(f"Paused at line {state.current_line} - Ctrl+T=Step, Ctrl+G=Continue, Ctrl+X=Stop")
                self._update_immediate_status()
                # Highlight current statement when paused at breakpoint
                if state.current_statement_char_start > 0 or state.current_statement_char_end > 0:
                    self._highlight_current_statement(state.current_line, state.current_statement_char_start, state.current_statement_char_end)
                if self.stack_visible:
                    self._update_stack()
                if self.variables_visible:
                    self._update_variables()

            elif state.status == 'paused':
                self.running = False
                self.paused_at_breakpoint = True
                self._add_output(f"\n→ Paused at line {state.current_line}\n")
                self._set_status(f"Paused at line {state.current_line} - Ctrl+T=Step, Ctrl+G=Continue, Ctrl+X=Stop")
                self._update_immediate_status()
                # Highlight current statement when paused
                if state.current_statement_char_start > 0 or state.current_statement_char_end > 0:
                    self._highlight_current_statement(state.current_line, state.current_statement_char_start, state.current_statement_char_end)
                if self.stack_visible:
                    self._update_stack()
                if self.variables_visible:
                    self._update_variables()

            elif state.status == 'running':
                # Highlight current statement while running (brief flash effect)
                if state.current_statement_char_start > 0 or state.current_statement_char_end > 0:
                    self._highlight_current_statement(state.current_line, state.current_statement_char_start, state.current_statement_char_end)
                # Schedule next tick
                self.tick_timer_id = self.root.after(10, self._execute_tick)

        except Exception as e:
            import traceback
            self.running = False
            self.paused_at_breakpoint = True  # Allow Continue to work after exception

            # Gather context for debug logging
            context = {}
            if self.interpreter and hasattr(self.interpreter, 'state'):
                state = self.interpreter.state
                context['current_line'] = state.current_line
                context['status'] = state.status
                if state.error_info:
                    context['error_line'] = state.error_info.error_line

            # Log error (outputs to stderr in debug mode)
            error_msg = debug_log_error(
                "Execution error",
                exception=e,
                context=context
            )

            # Display error in UI
            self._add_output(f"\n--- {error_msg} ---\n")
            if is_debug_mode():
                self._add_output("(Full traceback sent to stderr - check console)\n")
            else:
                self._add_output(traceback.format_exc())
            self._add_output("(Edit the line and click Continue to retry, or Stop to end)\n")

            # Get error line from state
            error_line = context.get('error_line', '?')
            self._set_status(f"Error at line {error_line} - Edit and Continue, or Stop")
            self._update_immediate_status()

            # Highlight the error statement (yellow highlight)
            if self.interpreter and hasattr(self.interpreter, 'state'):
                state = self.interpreter.state
                from src.debug_logger import debug_log
                debug_log(f"Exception handler: line={state.current_line}, char_start={state.current_statement_char_start}, char_end={state.current_statement_char_end}", level=1)
                if state.current_statement_char_start > 0 or state.current_statement_char_end > 0:
                    self._highlight_current_statement(state.current_line, state.current_statement_char_start, state.current_statement_char_end)

            # Mark the error line with red ? indicator
            if error_line and error_line != "?":
                try:
                    error_line_int = int(error_line)
                    from src.debug_logger import debug_log
                    debug_log(f"Setting error marker on line {error_line_int} (from exception handler)", level=1)
                    self.editor_text.set_error(error_line_int, True, str(e))
                except (ValueError, AttributeError, TypeError) as marker_error:
                    from src.debug_logger import debug_log
                    debug_log(f"Failed to set error marker: {marker_error}", level=1)

            # Update stack and variables to show state at error
            if self.stack_visible:
                self._update_stack()
            if self.variables_visible:
                self._update_variables()

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
            tk_io = TkIOHandler(self._add_output, self.root)
            self.interpreter = Interpreter(self.runtime, tk_io, limits=create_local_limits())

            # Wire up interpreter to use Tk UI's command methods (MERGE, LOAD, FILES, etc.)
            self.interpreter.interactive_mode = self

            # Start tick-based execution
            state = self.interpreter.start()
            if state.status == 'error':
                self._add_output(f"\n--- Setup error: {state.error_info.error_message if state.error_info else 'Unknown'} ---\n")
                self._set_status("Error")
                return

            # Set breakpoints if any
            if self.breakpoints:
                self.interpreter.state.breakpoints = self.breakpoints.copy()

            # Update immediate mode executor context to use program's runtime and interpreter
            if self.immediate_executor:
                self.immediate_executor.set_context(self.runtime, self.interpreter)
            self._update_immediate_status()

            # Start running
            self.running = True
            self.paused_at_breakpoint = False

            # Schedule first tick
            self.tick_timer_id = self.root.after(10, self._execute_tick)

        except Exception as e:
            import traceback

            # Log error (outputs to stderr in debug mode)
            error_msg = debug_log_error(
                "Runtime initialization error",
                exception=e,
                context={'phase': 'program setup'}
            )

            # Display error in UI
            self._add_output(f"\n--- {error_msg} ---\n")
            if is_debug_mode():
                self._add_output("(Full traceback sent to stderr - check console)\n")
            else:
                self._add_output(traceback.format_exc())

            self._set_status("Error")

    def cmd_list(self, args: str = "") -> None:
        """Execute LIST command - list program lines."""
        self._menu_clear_output()
        lines = self.program.get_lines()
        for line_num, line_text in lines:
            self._add_output(line_text + "\n")

    def _get_editor_content(self) -> str:
        """Get current editor content.

        Returns:
            Current text in editor
        """
        import tkinter as tk
        return self.editor_text.text.get(1.0, tk.END)

    def cmd_new(self) -> None:
        """Execute NEW command - clear program."""
        import tkinter as tk

        # Stop current autosave
        self.auto_save.stop_autosave()

        self.program.clear()
        self.editor_text.text.delete(1.0, tk.END)
        self._menu_clear_output()
        self._set_status("New program")

        # Start autosave for new file
        self.auto_save.start_autosave(
            'untitled.bas',
            self._get_editor_content,
            interval=30
        )

    def cmd_save(self, filename: str) -> None:
        """Execute SAVE command - save to file."""
        try:
            self.program.save_to_file(filename)
            self._set_status(f"Saved to {filename}")

            # Clean up autosave after successful save
            self.auto_save.cleanup_after_save(filename)

            # Restart autosave with new filename
            self.auto_save.stop_autosave()
            self.auto_save.start_autosave(
                filename,
                self._get_editor_content,
                interval=30
            )
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
                    # Mark line as having error with message
                    self.editor_text.set_error(line_num, True, error)
            if success:
                self._refresh_editor()
                # Re-validate to show error markers for loaded lines
                self._validate_editor_syntax()
                self._set_status(f"Loaded from {filename}")

                # Start autosave for loaded file
                self.auto_save.stop_autosave()
                self.auto_save.start_autosave(
                    filename,
                    self._get_editor_content,
                    interval=30
                )
        except Exception as e:
            self._add_output(f"Load error: {e}\n")
            self._set_status("Load error")

    def cmd_merge(self, filename: str) -> None:
        """Execute MERGE command - merge file into current program.

        MERGE adds or replaces lines from a file without clearing existing lines.
        - Lines with matching line numbers are replaced
        - New line numbers are added
        - Existing lines not in the file are kept
        """
        try:
            success, errors, lines_added, lines_replaced = self.program.merge_from_file(filename)
            if errors:
                for line_num, error in errors:
                    self._add_output(f"Parse error at line {line_num}: {error}\n")
                    # Mark line as having error with message
                    self.editor_text.set_error(line_num, True, error)
            if success:
                self._refresh_editor()
                # Re-validate to show error markers for merged lines
                self._validate_editor_syntax()
                self._add_output(f"Merged from {filename}\n")
                self._add_output(f"{lines_added} line(s) added, {lines_replaced} line(s) replaced\n")
                self._set_status(f"Merged from {filename}")
            else:
                self._add_output("No lines merged\n")
                self._set_status("Merge failed")
        except FileNotFoundError:
            self._add_output(f"?File not found: {filename}\n")
            self._set_status("File not found")
        except Exception as e:
            self._add_output(f"Merge error: {e}\n")
            self._set_status("Merge error")

    def cmd_files(self, filespec: str = "") -> None:
        """Execute FILES command - display directory listing.

        FILES - List all files in current directory
        FILES "*.BAS" - List files matching pattern
        """
        from ui.ui_helpers import list_files

        try:
            files = list_files(filespec)
            pattern = filespec if filespec else "*"

            if not files:
                self._add_output(f"No files matching: {pattern}\n")
                return

            # Display files (one per line with size)
            self._add_output(f"\nDirectory listing for: {pattern}\n")
            self._add_output("-" * 50 + "\n")
            for filename, size, is_dir in files:
                if is_dir:
                    self._add_output(f"{filename:<30}        <DIR>\n")
                elif size is not None:
                    self._add_output(f"{filename:<30} {size:>12} bytes\n")
                else:
                    self._add_output(f"{filename:<30}            ?\n")

            self._add_output(f"\n{len(files)} file(s)\n")

        except Exception as e:
            self._add_output(f"?Error listing files: {e}\n")

    def cmd_delete(self, args: str) -> None:
        """Execute DELETE command - delete line range using ui_helpers.

        Syntax:
            DELETE 40       - Delete single line 40
            DELETE 40-100   - Delete lines 40 through 100 (inclusive)
            DELETE -40      - Delete all lines up to and including 40
            DELETE 40-      - Delete from line 40 to end of program
        """
        from ui.ui_helpers import delete_lines_from_program

        try:
            # Delete using consolidated function
            deleted = delete_lines_from_program(self.program, args, runtime=None)

            # Refresh the editor display
            self._refresh_editor()

            # Show confirmation
            if len(deleted) == 1:
                self._write_output(f"Deleted line {deleted[0]}")
            else:
                self._write_output(f"Deleted {len(deleted)} lines ({min(deleted)}-{max(deleted)})")

        except ValueError as e:
            self._write_output(f"?{e}")
        except Exception as e:
            self._write_output(f"?Error during delete: {e}")

    def cmd_renum(self, args: str) -> None:
        """Execute RENUM command - renumber lines using AST serialization.

        Uses AST-based approach:
        1. Build line number mapping (old -> new)
        2. Walk AST and update all line number references
        3. Serialize AST back to source
        4. Refresh editor display

        This ensures AST is the single source of truth.
        """
        from ui.ui_helpers import renum_program

        try:
            # Use consolidated RENUM implementation
            old_lines, line_map = renum_program(
                self.program,
                args,
                self.interpreter.interactive_mode._renum_statement,
                runtime=None  # Tk UI doesn't have a persistent runtime
            )

            # Refresh the editor display
            self._refresh_editor()

            # Calculate range for message
            final_num = max(self.program.lines.keys()) if self.program.lines else 10
            new_start = min(self.program.lines.keys()) if self.program.lines else 10
            self._add_output(f"Renumbered ({new_start} to {final_num})\n")

        except ValueError as e:
            self._add_output(f"?{e}\n")
        except Exception as e:
            import traceback
            self._add_output(f"Error during renumber: {e}\n")
            self._add_output(traceback.format_exc())

    def cmd_cont(self) -> None:
        """Execute CONT command - continue after STOP.

        Resumes execution after:
        - STOP statement
        - Ctrl+C/Break
        - END statement (in some cases)

        Invalid if program was edited after stopping.
        """
        # Check if runtime exists and is in stopped state
        if not self.runtime or not self.runtime.stopped:
            self._write_output("?Can't continue")
            return

        try:
            # Clear stopped flag
            self.runtime.stopped = False

            # Restore execution position
            self.runtime.current_line = self.runtime.stop_line
            self.runtime.current_stmt_index = self.runtime.stop_stmt_index
            self.runtime.halted = False

            # Resume tick-based execution
            # The interpreter will continue from the saved position
            if self.interpreter:
                # Start ticking again
                self.is_running = True
                self._set_status("Running")
                self._tick()

        except Exception as e:
            self._write_output(f"?Error continuing: {e}")

    # Immediate mode methods

    def _focus_immediate_entry(self):
        """Focus the immediate mode entry widget when clicking in immediate mode area."""
        if self.immediate_entry:
            self.immediate_entry.focus_force()

    def _update_immediate_status(self):
        """Update immediate mode panel status based on interpreter state."""
        import tkinter as tk

        if not self.immediate_executor or not self.immediate_entry or not self.immediate_prompt_label:
            return

        if self.immediate_executor.can_execute_immediate():
            # Safe to execute - enable input
            # Update prompt label color based on current state
            if hasattr(self.interpreter, 'state') and self.interpreter.state:
                status = self.interpreter.state.status
                if status == 'at_breakpoint':
                    self.immediate_prompt_label.config(text="Breakpoint >", fg="orange")
                elif status == 'error':
                    self.immediate_prompt_label.config(text="Error >", fg="red")
                elif status == 'paused':
                    self.immediate_prompt_label.config(text="Paused >", fg="orange")
                elif self.paused_at_breakpoint:
                    # Might be paused after error/breakpoint but status changed
                    self.immediate_prompt_label.config(text="Paused >", fg="orange")
                else:
                    self.immediate_prompt_label.config(text="Ok >", fg="green")
            else:
                self.immediate_prompt_label.config(text="Ok >", fg="green")
            self.immediate_entry.config(state=tk.NORMAL)
        else:
            # Not safe - disable input
            status = self.interpreter.state.status if hasattr(self.interpreter, 'state') else 'unknown'
            self.immediate_prompt_label.config(text=f"[{status}] >", fg="red")
            self.immediate_entry.config(state=tk.DISABLED)

    def _execute_immediate(self):
        """Execute immediate mode command."""
        import tkinter as tk
        from tkinter import messagebox

        if not self.immediate_executor or not self.immediate_entry:
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

        # Execute (don't echo the command or add "Ok" - just show results)
        success, output = self.immediate_executor.execute(command)

        # Show output if any
        if output:
            self._add_immediate_output(output)

        if not success:
            # Only show error dialog on failure
            messagebox.showerror("Error", "Immediate mode error")

        # Clear input
        self.immediate_entry.delete(0, tk.END)

        # Update variables/stack windows if they exist
        if hasattr(self, 'variables_window') and self.variables_window:
            self._update_variables()
        if hasattr(self, 'stack_window') and self.stack_window and self.stack_visible:
            self._update_stack()

    def _add_immediate_output(self, text):
        """Add text to main output pane (immediate mode has no history widget)."""
        self._add_output(text)

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
    
    def __init__(self, output_callback, root=None):
        """Initialize Tk IOHandler.

        Args:
            output_callback: Function to call with output text (str) -> None
            root: Tk root window (needed for dialogs)
        """
        self.output_callback = output_callback
        self.input_callback = None  # Will be set when INPUT is needed
        self.root = root  # Tk root window for dialogs

    def output(self, text: str, end: str = '\n') -> None:
        """Output text to Tk output pane."""
        full_text = text + end
        if self.output_callback:
            self.output_callback(full_text)

    def input(self, prompt: str = '') -> str:
        """Input from user via modal dialog.

        Used by INPUT statement for reading comma-separated values.
        Shows a simple input dialog with the prompt.
        """
        from tkinter import simpledialog

        # Show prompt in output first
        if prompt:
            self.output(prompt, end='')

        # Show modal input dialog
        result = simpledialog.askstring(
            "INPUT",
            prompt if prompt else "Enter value:",
            parent=self.root
        )

        # If user clicked Cancel, raise exception (mimics Ctrl+C)
        if result is None:
            raise KeyboardInterrupt("Input cancelled")

        # Echo the input to output
        self.output(result)

        return result

    def input_line(self, prompt: str = '') -> str:
        """Input complete line from user via modal dialog.

        Used by LINE INPUT statement for reading entire line as string.
        Identical to input() for Tk UI.
        """
        from tkinter import simpledialog

        # Show prompt in output first
        if prompt:
            self.output(prompt, end='')

        # Show modal input dialog
        result = simpledialog.askstring(
            "LINE INPUT",
            prompt if prompt else "Enter line:",
            parent=self.root
        )

        # If user clicked Cancel, raise exception (mimics Ctrl+C)
        if result is None:
            raise KeyboardInterrupt("Input cancelled")

        # Echo the input to output
        self.output(result)

        return result

    def input_char(self, blocking: bool = True) -> str:
        """Input single character via modal dialog.

        Used by INKEY$ and INPUT$ for single character input.
        For Tk UI, shows a simple input dialog limited to 1 character.
        """
        if not blocking:
            # Non-blocking: no key available (would need background monitoring)
            return ""

        from tkinter import simpledialog

        # Show modal input dialog
        result = simpledialog.askstring(
            "INPUT$ (Single Character)",
            "Enter a single character:",
            parent=self.root
        )

        # If user clicked Cancel, return empty string
        if result is None:
            return ""

        # Return first character only
        return result[0] if result else ""
    
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
