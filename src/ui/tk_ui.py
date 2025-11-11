"""Tkinter GUI backend for MBASIC interpreter.

This module provides a graphical UI using Python's tkinter library.
Tkinter provides a native GUI with buttons, menus, and text widgets,
making it suitable for a modern BASIC IDE experience.
"""

from .base import UIBackend
from src.runtime import Runtime
from src.interpreter import Interpreter
from .keybinding_loader import KeybindingLoader
from .recent_files import RecentFilesManager
from .auto_save import AutoSaveManager
from src.immediate_executor import ImmediateExecutor, OutputCapturingIOHandler
from src.iohandler.base import IOHandler
from src.input_sanitizer import sanitize_and_clear_parity, is_valid_input_char
from src.debug_logger import debug_log_error, is_debug_mode
from src.ui.variable_sorting import sort_variables, get_sort_mode_label, cycle_sort_mode, get_default_reverse_for_mode
from src.pc import PC
from src.ast_nodes import EndStatementNode
import tkinter as tk
from tkinter import filedialog, messagebox, font, scrolledtext, ttk, simpledialog


class _ImmediateModeToken:
    """Token for variable edits from immediate mode or variable editor.

    This class is instantiated when editing variables via the variable inspector
    (see _on_variable_double_click()). Used to mark variable changes that
    originate from the variable inspector or immediate mode, not from program
    execution. The line=-1 signals to runtime.set_variable() that this is a
    debugger/immediate mode edit, allowing correct variable tracking during debugging.
    """
    def __init__(self):
        self.line = -1
        self.position = None


class TkBackend(UIBackend):
    """Tkinter-based graphical UI backend.

    Provides a graphical UI with:
    - Menu bar (File, Edit, Run, Help)
    - Toolbar with common actions
    - 3-pane vertical layout (weights: 3:2:1 = total 6 units):
      * Editor with line numbers (top, ~50% = 3/6 - weight=3)
      * Output pane (middle, ~33% = 2/6 - weight=2)
        - Contains INPUT row (shown/hidden dynamically for INPUT statements)
      * Immediate mode input line (bottom, ~17% = 1/6 - weight=1)
    - File dialogs for Open/Save

    Usage:
        from src.ui.tk_ui import TkBackend, TkIOHandler
        from src.editing.manager import ProgramManager

        io = TkIOHandler()  # TkIOHandler created without backend reference initially
        def_type_map = {}  # Type suffix defaults for variables (DEFINT, DEFSNG, etc.)
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

        # Variables window state
        self.variables_window = None
        self.variables_tree = None
        self.variables_visible = False
        self.variables_sort_column = 'accessed'  # Current sort column (default: 'accessed' for last-accessed timestamp)
        self.variables_sort_reverse = True  # Sort direction: False=ascending, True=descending (default descending for timestamps)

        # Execution stack window state
        self.stack_window = None
        self.stack_tree = None
        self.stack_visible = False

        # Immediate mode widgets and executor
        # Note: immediate_history and immediate_status are always None in Tk UI
        # (Tk uses immediate_entry Entry widget directly instead of separate history/status widgets)
        # immediate_entry is the actual Entry widget created in start()
        self.immediate_executor = None
        self.immediate_history = None
        self.immediate_entry = None
        self.immediate_status = None

        # Editor auto-sort state
        self.last_edited_line_index = None  # Last editor line index (1-based)
        self.last_edited_line_text = None   # Content of last edited line

        # Editor auto-numbering configuration (load from settings system)
        from src.settings import get
        self.auto_number_enabled = get('auto_number')
        self.auto_number_start = get('auto_number_start')
        self.auto_number_increment = get('auto_number_step')

        # Tkinter widgets (created in start())
        self.root = None
        self.editor_text = None
        self.output_text = None
        self.status_label = None
        self.recent_files_menu = None  # Recent Files submenu
        self.variables_search_entry = None  # Variables window search entry
        self.variables_filter_text = ""  # Current filter text

        # INPUT row widgets (hidden until INPUT statement needs input)
        self.input_row = None
        self.input_label = None
        self.input_entry = None
        self.input_submit_btn = None
        self.input_queue = None  # Queue for coordinating INPUT with interpreter

        # Find/Replace state
        self.find_dialog = None
        self.replace_dialog = None
        self.find_text = ""
        self.replace_text = ""
        self.find_case_sensitive = False
        self.find_whole_word = False
        self.find_position = "1.0"  # Current search position in editor

    def start(self) -> None:
        """Start the Tkinter GUI.

        Creates the main window and starts the Tk event loop.
        """
        from .tk_widgets import LineNumberedText

        # Create main window
        self.root = tk.Tk()
        self.root.title("MBASIC-2025 - Modern MBASIC 5.21 Interpreter")
        self.root.geometry("1000x600")

        # Create menu bar
        self._create_menu()

        # Create toolbar
        self._create_toolbar()

        # Create main content area (split pane)
        paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Top pane: Editor with line numbers (weight=3, ~50% of space)
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
        self.editor_text.text.bind('<FocusIn>', self._on_focus_in)

        # Bind Enter key for auto-numbering
        self.editor_text.text.bind('<Return>', self._on_enter_key)

        # Bind Tab key to cycle focus (prevent tab character insertion)
        def on_editor_tab(e):
            self.immediate_entry.focus_set()
            return "break"  # Prevent tab character from being inserted
        self.editor_text.text.bind('<Tab>', on_editor_tab)

        # Bind Ctrl+I for smart insert line (must be on text widget to prevent tab)
        self.editor_text.text.bind('<Control-i>', self._on_ctrl_i)

        # Bind paste event for input sanitization
        self.editor_text.text.bind('<<Paste>>', self._on_paste)

        # Bind key press for input sanitization
        self.editor_text.text.bind('<Key>', self._on_key_press, add='+')

        # Set up editor context menu
        self._setup_editor_context_menu()

        # Middle pane: Output (weight=2, ~33% of space)
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

        # INPUT row (hidden by default, shown when INPUT statement needs input)
        # Visibility controlled via pack() when showing, pack_forget() when hiding
        self.input_row = ttk.Frame(output_frame, height=40)
        # Don't pack yet - will be packed when needed

        # Create INPUT prompt label
        self.input_label = tk.Label(self.input_row, text="", font=("Courier", 10), fg="blue")
        self.input_label.pack(side=tk.LEFT, padx=(5, 5))

        # Create INPUT entry field
        self.input_entry = tk.Entry(self.input_row, font=("Courier", 10),
                                    state='normal', takefocus=True,
                                    exportselection=False)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # Create submit button
        self.input_submit_btn = tk.Button(self.input_row, text="Submit",
                                          command=self._submit_input)
        self.input_submit_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Bind Enter key to submit
        self.input_entry.bind('<Return>', lambda e: self._submit_input())

        # Initialize input queue
        import queue
        self.input_queue = queue.Queue()

        # Bottom pane: Immediate Mode - just the input line (weight=1, ~17% of space)
        immediate_frame = ttk.Frame(paned)
        paned.add(immediate_frame, weight=1)

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

        # Bind Tab key to move focus to editor
        def on_immediate_tab(e):
            self.editor_text.text.focus_set()
            return "break"  # Prevent default Tab behavior
        self.immediate_entry.bind('<Tab>', on_immediate_tab)

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

        self.execute_btn = ttk.Button(input_frame, text="Enter", command=self._execute_immediate)
        self.execute_btn.pack(side=tk.LEFT)

        # Set immediate_history and immediate_status to None
        # These attributes are not currently used but are set to None for defensive programming
        # in case future code tries to access them (will get None instead of AttributeError)
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
        # Sync breakpoints from UI to runtime
        self.runtime.breakpoints = self.breakpoints.copy()

        # Create IOHandler that outputs to output pane
        tk_io = TkIOHandler(self._add_output, self.root, backend=self)
        self.interpreter = Interpreter(self.runtime, tk_io, limits=create_unlimited_limits())

        # Wire up interpreter to use Tk UI's command methods
        self.interpreter.interactive_mode = self

        # Initialize immediate executor to use the same runtime/interpreter
        immediate_io = OutputCapturingIOHandler()
        self.immediate_executor = ImmediateExecutor(runtime=self.runtime, interpreter=self.interpreter, io_handler=immediate_io)

        # Status bar
        self.status_label = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Create variables window (initially hidden)
        self._create_variables_window()

        # Create execution stack window (initially hidden)
        self._create_stack_window()

        # Load program into editor if already loaded
        self._refresh_editor()

        # Start event loop
        self.root.mainloop()

    def _create_menu(self):
        """Create menu bar."""

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
        edit_menu.add_command(label="Cut", command=self._menu_cut,
                             accelerator=self.keybindings.get_tk_accelerator('editor', 'cut'))
        edit_menu.add_command(label="Copy", command=self._menu_copy,
                             accelerator=self.keybindings.get_tk_accelerator('editor', 'copy'))
        edit_menu.add_command(label="Paste", command=self._menu_paste,
                             accelerator=self.keybindings.get_tk_accelerator('editor', 'paste'))
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", command=self._menu_find,
                             accelerator=self.keybindings.get_tk_accelerator('editor', 'find'))
        edit_menu.add_command(label="Find Next", command=self._find_next, accelerator="F3")
        edit_menu.add_command(label="Replace...", command=self._menu_replace,
                             accelerator=self.keybindings.get_tk_accelerator('editor', 'replace'))
        edit_menu.add_separator()
        edit_menu.add_command(label="Insert Line", command=self._smart_insert_line,
                             accelerator=self.keybindings.get_tk_accelerator('editor', 'smart_insert'))
        edit_menu.add_separator()
        edit_menu.add_command(label="Toggle Breakpoint", command=lambda: self.root.after(1, self._toggle_breakpoint),
                             accelerator=self.keybindings.get_tk_accelerator('editor', 'toggle_breakpoint'))
        edit_menu.add_command(label="Clear All Breakpoints", command=lambda: self.root.after(1, self._clear_all_breakpoints))
        edit_menu.add_separator()
        edit_menu.add_command(label="Settings...", command=self._menu_settings)

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
        view_menu.add_command(label="Variables", command=self._toggle_variables,
                             accelerator=self.keybindings.get_tk_accelerator('view', 'toggle_variables'))
        view_menu.add_command(label="Execution Stack", command=self._toggle_stack,
                             accelerator=self.keybindings.get_tk_accelerator('view', 'toggle_stack'))

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Help Topics", command=self._menu_help,
                             accelerator=self.keybindings.get_tk_accelerator('menu', 'help_topics'))
        help_menu.add_command(label="Games Library", command=self._menu_games_library)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._menu_about)

        # Bind keyboard shortcuts from config
        self.keybindings.bind_all_to_tk(self.root, 'menu', 'file_new', lambda e: self._menu_new())
        self.keybindings.bind_all_to_tk(self.root, 'menu', 'file_open', lambda e: self._menu_open())
        self.keybindings.bind_all_to_tk(self.root, 'menu', 'file_save', lambda e: self._menu_save())
        self.keybindings.bind_all_to_tk(self.root, 'menu', 'file_quit', lambda e: self._menu_exit())
        self.keybindings.bind_all_to_tk(self.root, 'menu', 'run_program', lambda e: self._menu_run())
        self.keybindings.bind_all_to_tk(self.root, 'menu', 'help_topics', lambda e: self._menu_help())

        # Editor shortcuts
        self.keybindings.bind_all_to_tk(self.root, 'editor', 'toggle_breakpoint', lambda e: self._toggle_breakpoint())
        self.keybindings.bind_all_to_tk(self.root, 'editor', 'find', lambda e: self._menu_find())
        self.keybindings.bind_all_to_tk(self.root, 'editor', 'replace', lambda e: self._menu_replace())

        # View shortcuts
        self.keybindings.bind_all_to_tk(self.root, 'view', 'toggle_variables', lambda e: self._toggle_variables())
        self.keybindings.bind_all_to_tk(self.root, 'view', 'toggle_stack', lambda e: self._toggle_stack())

        # Additional shortcuts
        self.root.bind('<F3>', lambda e: self._find_next())
        # Note: Ctrl+I is bound directly to editor text widget in start() (not root window)
        # to prevent tab key interference - see editor_text.text.bind('<Control-i>', ...)

    def _create_toolbar(self):
        """Create toolbar with common actions."""

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

        # Note: Toolbar has been simplified to show only essential execution controls.
        # Additional features are accessible via menus:
        # - List Program → Run > List Program
        # - New Program (clear) → File > New
        # - Clear Output → Run > Clear Output

    # Menu handlers

    def _menu_new(self):
        """File > New"""
        self.cmd_new()

    def _menu_open(self):
        """File > Open"""

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
        # If no program loaded, save editor first
        if not self.runtime.pc.is_running() and self.runtime.pc.line is None:
            success = self._save_editor_to_program()
            if not success:
                self._set_status("Cannot step - program has syntax errors")
                return
            # Initialize for stepping
            self.runtime.reset_for_run(self.program.line_asts, self.program.lines)
            state = self.interpreter.start()
            if state.error_info:
                self._add_output(f"\n--- Setup error: {state.error_info.error_message} ---\n")
                self._set_status("Error")
                return

        # Clear paused state to allow stepping through breakpoints
        self.paused_at_breakpoint = False

        try:
            state = self.interpreter.tick(mode='step_line', max_statements=100)

            # Handle interpreter state (error, halted, or running)
            if state.error_info:
                # Error state
                error_msg = state.error_info.error_message
                line_num = state.error_info.pc.line_num
                self._add_output(f"\n--- Error at line {line_num}: {error_msg} ---\n")
                self._set_status("Error")
                self._clear_statement_highlight()
            elif not self.runtime.pc.is_running():
                # Halted - check what's at PC to determine if we should highlight
                pc = self.runtime.pc
                if pc.line is None:
                    # Past end of program
                    self._add_output("\n--- Program finished ---\n")
                    self._set_status("Ready")
                    self._clear_statement_highlight()
                else:
                    # Get statement at PC to check if it's END or steppable
                    stmt = self.runtime.statement_table.get(pc)
                    if stmt and isinstance(stmt, EndStatementNode):
                        # Stopped at END statement - don't highlight
                        self._add_output("\n--- Program finished ---\n")
                        self._set_status("Ready")
                        self._clear_statement_highlight()
                    else:
                        # Paused at steppable statement - highlight it
                        self._add_output(f"→ Paused at line {pc.line}\n")
                        self._set_status(f"Paused at line {pc.line}")
                        # Highlight current statement
                        if state.current_statement_char_start > 0 or state.current_statement_char_end > 0:
                            self._highlight_current_statement(pc.line, state.current_statement_char_start, state.current_statement_char_end)

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
        # If no program loaded, save editor first
        if not self.runtime.pc.is_running() and self.runtime.pc.line is None:
            success = self._save_editor_to_program()
            if not success:
                self._set_status("Cannot step - program has syntax errors")
                return
            # Initialize for stepping
            self.runtime.reset_for_run(self.program.line_asts, self.program.lines)
            state = self.interpreter.start()
            if state.error_info:
                self._add_output(f"\n--- Setup error: {state.error_info.error_message} ---\n")
                self._set_status("Error")
                return

        # Clear paused state to allow stepping through breakpoints
        self.paused_at_breakpoint = False

        try:
            state = self.interpreter.tick(mode='step_statement', max_statements=1)

            # Handle interpreter state (error, halted, or running)
            if state.error_info:
                # Error state
                error_msg = state.error_info.error_message
                line_num = state.error_info.pc.line_num
                self._add_output(f"\n--- Error at line {line_num}: {error_msg} ---\n")
                self._set_status("Error")
                self._clear_statement_highlight()
            elif not self.runtime.pc.is_running():
                # Halted - check what's at PC to determine if we should highlight
                pc = self.runtime.pc
                if pc.line is None:
                    # Past end of program
                    self._add_output("\n--- Program finished ---\n")
                    self._set_status("Ready")
                    self._clear_statement_highlight()
                else:
                    # Get statement at PC to check if it's END or steppable
                    stmt = self.runtime.statement_table.get(pc)
                    if stmt and isinstance(stmt, EndStatementNode):
                        # Stopped at END statement - don't highlight
                        self._add_output("\n--- Program finished ---\n")
                        self._set_status("Ready")
                        self._clear_statement_highlight()
                    else:
                        # Paused at steppable statement - highlight it
                        stmt_info = f" statement {pc.statement + 1}" if pc and pc.statement > 0 else ""
                        self._add_output(f"→ Paused at line {pc.line}{stmt_info}\n")
                        self._set_status(f"Paused at line {pc.line}{stmt_info}")
                        # Highlight current statement
                        if state.current_statement_char_start > 0 or state.current_statement_char_end > 0:
                            self._highlight_current_statement(pc.line, state.current_statement_char_start, state.current_statement_char_end)

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

        if not self.interpreter or not self.paused_at_breakpoint:
            self._set_status("Not paused")
            return

        try:
            # If we're continuing from an error, re-parse the program to incorporate edits
            if self.interpreter.state.error_info:
                self._add_output("\n--- Re-parsing program after edit ---\n")

                # Clear all error markers first
                self.editor_text.clear_all_errors()

                # Get current editor text
                program_text = self.editor_text.get("1.0", tk.END)

                # Parse the updated program
                from src.parser import Parser
                from src.lexer import Lexer, create_keyword_case_manager
                try:
                    keyword_mgr = create_keyword_case_manager()
                    lexer = Lexer(program_text, keyword_case_manager=keyword_mgr)
                    tokens = lexer.tokenize()
                    parser = Parser(tokens)
                    program = parser.parse()
                except Exception as parse_error:
                    self._add_output(f"Parse error: {parse_error}\n")
                    self._add_output("Fix the syntax error and try again.\n")
                    self._set_status("Parse error - fix and retry")
                    return

                # Update the interpreter's runtime with new program
                # Rebuild statement_table from ProgramNode.lines
                for line in program.lines:
                    self.runtime.statement_table.replace_line(line.line_number, line)

                # Validate execution stack after program edits
                valid, removed_entries, messages = self.runtime.validate_stack()
                if removed_entries:
                    self._add_output("\n⚠️  Warning: Program edits invalidated execution stack:\n")
                    for msg in messages:
                        self._add_output(f"  • {msg}\n")
                    self._add_output(f"  {len(removed_entries)} stack entry(ies) removed\n\n")

                # Clear error state (halted flag already set)
                self.interpreter.state.error_info = None

                self._add_output("--- Program updated, resuming execution ---\n")

            # Resume execution
            self.running = True
            self.paused_at_breakpoint = False
            self._set_status("Continuing...")

            # Schedule next tick
            self.tick_timer_id = self.root.after(10, self._execute_tick)

        except Exception as e:
            import traceback
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
        """Toggle breakpoint on current statement (Ctrl+B)."""
        # Get current BASIC line number from cursor position
        line_number = self.editor_text.get_current_line_number()

        if not line_number:
            self._set_status("No line number at cursor")
            return

        # Get cursor position within the line to determine which statement
        cursor_pos = self.editor_text.text.index('insert')
        cursor_column = int(cursor_pos.split('.')[1])

        # Get the line text to determine character offset
        tk_line_num = int(cursor_pos.split('.')[0])
        line_text = self.editor_text.text.get(f'{tk_line_num}.0', f'{tk_line_num}.end')

        # Query the statement table to find which statement the cursor is in
        stmt_offset = 0
        # Get all statements for this line from the statement table
        for pc, stmt_node in self.runtime.statement_table.statements.items():
            if pc.line_num == line_number:
                # Check if cursor is within this statement's character range
                if stmt_node.char_start <= cursor_column <= stmt_node.char_end:
                    stmt_offset = pc.stmt_offset
                    break

        # Create PC object for this statement
        pc = PC(line_number, stmt_offset)

        # Toggle in breakpoints set
        if pc in self.breakpoints:
            self.breakpoints.remove(pc)
            self.editor_text.set_breakpoint(line_number, False)
            if stmt_offset > 0:
                self._set_status(f"Breakpoint removed from line {line_number}, statement {stmt_offset + 1}")
            else:
                self._set_status(f"Breakpoint removed from line {line_number}")
        else:
            self.breakpoints.add(pc)
            self.editor_text.set_breakpoint(line_number, True)
            if stmt_offset > 0:
                self._set_status(f"Breakpoint set on line {line_number}, statement {stmt_offset + 1}")
            else:
                self._set_status(f"Breakpoint set on line {line_number}")

        # Update runtime breakpoints
        self.runtime.breakpoints = self.breakpoints.copy()

    def _clear_all_breakpoints(self):
        """Clear all breakpoints."""
        # Clear all breakpoints from editor
        # Collect unique line numbers from PC objects
        line_numbers = set()
        for bp in list(self.breakpoints):
            if isinstance(bp, PC):
                line_numbers.add(bp.line_num)
            else:
                # Support legacy integer breakpoints
                line_numbers.add(bp)

        for line_number in line_numbers:
            self.editor_text.set_breakpoint(line_number, False)

        # Clear set
        self.breakpoints.clear()

        # Update runtime breakpoints
        self.runtime.breakpoints = self.breakpoints.copy()

        self._set_status("All breakpoints cleared")

    def _create_variables_window(self):
        """Create variables window (Toplevel)."""

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
        # Set initial heading text with down arrow (matches self.variables_sort_column='accessed', descending)
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

        Only the Variable column (column #0) is sortable - clicking it cycles through
        different sort modes (see _cycle_variable_sort() for the cycle order).
        Type and Value columns are not sortable.
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
        elif column == '#1':  # Value column (first data column)
            col_x = event.x - self.variables_tree.column('#0', 'width')
        elif column == '#2':  # Type column (second data column)
            col_x = event.x - self.variables_tree.column('#0', 'width') - self.variables_tree.column('Value', 'width')
        else:
            return

        # Determine click action based on horizontal position within column header:
        # - Left 20 pixels (arrow area) = toggle sort direction
        # - Rest of header = cycle/set sort column
        ARROW_CLICK_WIDTH = 20  # Width of clickable arrow area in pixels (typical arrow icon width for standard Tkinter theme)
        if col_x < ARROW_CLICK_WIDTH:
            self._toggle_variable_sort_direction()
        else:
            if column == '#0':  # Variable column - only sortable column
                self._cycle_variable_sort()
            # Type and Value columns are not sortable

    def _on_variable_double_click(self, event):
        """Handle double-click on variable to edit its value."""
        import re

        # Check if we clicked on a row (accept both 'tree' and 'cell' regions)
        # 'tree' = first column area, 'cell' = other column areas
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
        value_display = str(item_data['values'][0])  # Value column (first data column) - convert to string
        type_suffix_display = item_data['values'][1]  # Type column (second data column)

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

            # Update the variable using the runtime's set_variable method
            # Use _ImmediateModeToken to mark this as a debugger/immediate mode edit
            self.runtime.set_variable(
                base_name,
                suffix,
                new_value,
                token=_ImmediateModeToken()
            )

            # Refresh variables window
            self._update_variables()

            # Show confirmation in status
            self.status_label.config(text=f"Variable {variable_name} updated to {new_value}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update variable: {e}")

    def _edit_array_element(self, variable_name, type_suffix, value_display):
        """Edit any array element by typing subscripts.

        The dialog pre-fills with the last accessed subscripts and value if available,
        extracted from value_display (e.g., "[5,3]=42" portion).

        Args:
            variable_name: Array name with type suffix (e.g., "A%")
            type_suffix: Type character ($, %, !, #, or empty) - also embedded in variable_name
                        (parameter provided separately for convenience)
            value_display: Display string like "Array(10x10) [5,3]=42"
        """
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
        # OPTION BASE only allows 0 or 1 (validated by OPTION statement parser).
        # The else clause is defensive programming for unexpected values.
        if not default_subscripts and dimensions:
            array_base = self.runtime.array_base
            if array_base == 0:
                # OPTION BASE 0: use all zeros
                default_subscripts = ','.join(['0'] * len(dimensions))
            elif array_base == 1:
                # OPTION BASE 1: use all ones
                default_subscripts = ','.join(['1'] * len(dimensions))
            else:
                # Defensive fallback for invalid array_base (should not occur)
                default_subscripts = ','.join(['0'] * len(dimensions))

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

                # Update array element
                # Use _ImmediateModeToken to mark this as a debugger/immediate mode edit
                self.runtime.set_array_element(
                    base_name,
                    suffix,
                    subscripts,
                    new_value,
                    token=_ImmediateModeToken()
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
        self.variables_sort_column = cycle_sort_mode(self.variables_sort_column)

        # Update headers and display
        self._update_variable_headings()
        self._update_variables()

    def _update_variable_headings(self):
        """Update all variable window column headings to show current sort state."""
        # Determine arrow character based on sort direction
        arrow = '↓' if self.variables_sort_reverse else '↑'

        # Update Variable column heading to show current sort mode
        mode_label = get_sort_mode_label(self.variables_sort_column)
        var_text = f'{arrow} Variable ({mode_label})'
        self.variables_tree.heading('#0', text=var_text)
        self.variables_tree.heading('Value', text='  Value')
        self.variables_tree.heading('Type', text='  Type')

    def _update_variables(self):
        """Update variables window from runtime."""
        if not self.variables_visible or not self.runtime:
            return

        runtime = self.runtime
        interpreter = self.interpreter

        # Update resource usage
        if hasattr(interpreter, 'limits'):
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

        # Sort variables using common helper
        sorted_variables = sort_variables(variables, self.variables_sort_column, self.variables_sort_reverse)

        # Apply filter if present
        if self.variables_filter_text:
            filter_lower = self.variables_filter_text.lower()
            filtered_variables = []
            for var in sorted_variables:
                # Use original_case for filter matching (respects case conflict policy)
                display_name = var.get('original_case', var['name'])
                name = display_name + var['type_suffix']
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
            # Use original_case for display if available (respects case conflict policy)
            display_name = var.get('original_case', var['name'])
            name = display_name + var['type_suffix']
            type_name = type_map.get(var['type_suffix'], 'Unknown')

            if var['is_array']:
                # Display up to 4 dimensions, show "..." if more
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
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

    def _menu_help(self):
        """Help > Help Topics (F1) - Opens in web browser"""
        import webbrowser
        # Open help documentation in web browser
        from .web_help_launcher import open_help_in_browser
        open_help_in_browser(topic="ui/tk/", ui_type="tk")

    def _menu_games_library(self):
        """Help > Games Library - Opens games library in browser"""
        import webbrowser
        from ..docs_config import get_site_url
        # Library is at site root, not under /help/
        url = get_site_url("library/")
        webbrowser.open(url)

    def _context_help(self):
        """Show context-sensitive help for keyword at cursor"""
        try:
            # Get current cursor position
            cursor_pos = self.text_editor.index(tk.INSERT)

            # Get current line
            line = self.text_editor.get(f"{cursor_pos} linestart", f"{cursor_pos} lineend")

            # Get word at cursor
            # Find word boundaries
            col = int(cursor_pos.split('.')[1])
            start = col
            end = col

            # Expand left
            while start > 0 and (line[start-1].isalnum() or line[start-1] in '_$%'):
                start -= 1

            # Expand right
            while end < len(line) and (line[end].isalnum() or line[end] in '_$%'):
                end += 1

            keyword = line[start:end].upper().strip()

            if keyword:
                # Open help for specific keyword
                from .web_help_launcher import open_help_in_browser

                # Map to help topics (relative to DOCS_BASE_URL which already includes /help/)
                topic_map = {
                    'PRINT': 'common/statements/print',
                    'INPUT': 'common/statements/input',
                    'IF': 'common/statements/if',
                    'FOR': 'common/statements/for',
                    'NEXT': 'common/statements/next',
                    'GOTO': 'common/statements/goto',
                    'GOSUB': 'common/statements/gosub',
                    'RETURN': 'common/statements/return',
                    'DIM': 'common/statements/dim',
                    'LET': 'common/statements/let',
                    'REM': 'common/statements/rem',
                    'END': 'common/statements/end',
                    'STOP': 'common/statements/stop',
                    'RUN': 'common/statements/run',
                    'LIST': 'common/statements/list',
                    'NEW': 'common/statements/new',
                    'SAVE': 'common/statements/save',
                    'LOAD': 'common/statements/load',
                    'CLS': 'common/statements/cls',
                    'WHILE': 'common/statements/while',
                    'WEND': 'common/statements/wend',
                }

                topic = topic_map.get(keyword, "ui/tk/")
                open_help_in_browser(topic=topic, ui_type="tk")
            else:
                # No keyword, open general help
                self._menu_help()

        except Exception as e:
            # Fall back to general help
            self._menu_help()

    def _menu_about(self):
        """Help > About"""

        # Get help key from config
        help_keys = self.keybindings.get_all_keys('menu', 'help_topics')
        help_key_text = ' or '.join(help_keys) if help_keys else 'Ctrl+?'

        messagebox.showinfo(
            "About MBASIC-2025",
            "MBASIC-2025\n"
            "Modern MBASIC 5.21 Interpreter\n\n"
            "100% compatible with Microsoft BASIC-80 5.21\n"
            "Plus modern debugging and UI features\n\n"
            "Tkinter GUI Backend\n\n"
            f"Press {help_key_text} for help"
        )

    def _menu_settings(self):
        """Edit > Settings..."""
        from .tk_settings_dialog import SettingsDialog

        # Create and show settings dialog
        SettingsDialog(self.root)

    def _menu_find(self):
        """Edit > Find... (Ctrl+F)"""

        # Close any existing find dialog
        if self.find_dialog and self.find_dialog.winfo_exists():
            self.find_dialog.destroy()

        # Create find dialog
        self.find_dialog = tk.Toplevel(self.root)
        self.find_dialog.title("Find")
        self.find_dialog.geometry("400x150")
        self.find_dialog.transient(self.root)

        # Find text entry
        tk.Label(self.find_dialog, text="Find what:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        find_entry = tk.Entry(self.find_dialog, width=30)
        find_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        find_entry.insert(0, self.find_text)
        find_entry.focus_set()
        find_entry.select_range(0, tk.END)

        # Options frame
        options_frame = ttk.LabelFrame(self.find_dialog, text="Options")
        options_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        case_var = tk.BooleanVar(value=self.find_case_sensitive)
        tk.Checkbutton(options_frame, text="Case sensitive", variable=case_var).grid(row=0, column=0, sticky="w", padx=5)

        word_var = tk.BooleanVar(value=self.find_whole_word)
        tk.Checkbutton(options_frame, text="Whole word", variable=word_var).grid(row=0, column=1, sticky="w", padx=5)

        # Buttons
        button_frame = tk.Frame(self.find_dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        def do_find():
            self.find_text = find_entry.get()
            self.find_case_sensitive = case_var.get()
            self.find_whole_word = word_var.get()
            self.find_position = "1.0"  # Start from beginning
            self._find_next()
            self.find_dialog.destroy()

        ttk.Button(button_frame, text="Find Next", command=do_find).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.find_dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Enter key triggers find
        find_entry.bind('<Return>', lambda e: do_find())

    def _find_next(self):
        """Find next occurrence (F3)"""

        if not self.find_text:
            self._menu_find()
            return

        # Remove any existing highlighting
        self.editor_text.text.tag_remove("find_highlight", "1.0", tk.END)

        # Search options
        search_kwargs = {}
        if not self.find_case_sensitive:
            search_kwargs['nocase'] = True

        # Search from current position
        pos = self.editor_text.text.search(
            self.find_text,
            self.find_position,
            tk.END,
            **search_kwargs
        )

        if pos:
            # Found - highlight and scroll to it
            end_pos = f"{pos}+{len(self.find_text)}c"
            self.editor_text.text.tag_add("find_highlight", pos, end_pos)
            self.editor_text.text.tag_config("find_highlight", background="yellow", foreground="black")
            self.editor_text.text.see(pos)
            self.editor_text.text.mark_set("insert", end_pos)
            self.editor_text.text.focus_set()

            # Update position for next search
            self.find_position = end_pos
        else:
            # Not found - wrap to beginning
            if self.find_position != "1.0":
                self.find_position = "1.0"
                self._find_next()  # Try again from beginning
            else:
                # Really not found
                self._set_status(f"'{self.find_text}' not found")

    def _menu_replace(self):
        """Edit > Replace... (Ctrl+H)"""

        # Close any existing replace dialog
        if self.replace_dialog and self.replace_dialog.winfo_exists():
            self.replace_dialog.destroy()

        # Create replace dialog
        self.replace_dialog = tk.Toplevel(self.root)
        self.replace_dialog.title("Replace")
        self.replace_dialog.geometry("400x200")
        self.replace_dialog.transient(self.root)

        # Find text entry
        tk.Label(self.replace_dialog, text="Find what:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        find_entry = tk.Entry(self.replace_dialog, width=30)
        find_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        find_entry.insert(0, self.find_text)
        find_entry.focus_set()
        find_entry.select_range(0, tk.END)

        # Replace text entry
        tk.Label(self.replace_dialog, text="Replace with:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        replace_entry = tk.Entry(self.replace_dialog, width=30)
        replace_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        replace_entry.insert(0, self.replace_text)

        # Options frame
        options_frame = ttk.LabelFrame(self.replace_dialog, text="Options")
        options_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        case_var = tk.BooleanVar(value=self.find_case_sensitive)
        tk.Checkbutton(options_frame, text="Case sensitive", variable=case_var).grid(row=0, column=0, sticky="w", padx=5)

        word_var = tk.BooleanVar(value=self.find_whole_word)
        tk.Checkbutton(options_frame, text="Whole word", variable=word_var).grid(row=0, column=1, sticky="w", padx=5)

        # Buttons
        button_frame = tk.Frame(self.replace_dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        def do_find():
            self.find_text = find_entry.get()
            self.replace_text = replace_entry.get()
            self.find_case_sensitive = case_var.get()
            self.find_whole_word = word_var.get()
            self.find_position = "1.0"
            self._find_next()

        def do_replace():
            # Replace current selection if it matches
            try:
                sel_text = self.editor_text.text.get("sel.first", "sel.last")
                if sel_text == self.find_text or (not self.find_case_sensitive and sel_text.lower() == self.find_text.lower()):
                    self.editor_text.text.delete("sel.first", "sel.last")
                    self.editor_text.text.insert("sel.first", self.replace_text)
            except tk.TclError:
                pass  # No selection
            do_find()

        def do_replace_all():
            self.find_text = find_entry.get()
            self.replace_text = replace_entry.get()
            self.find_case_sensitive = case_var.get()
            self.find_whole_word = word_var.get()

            # Count replacements
            count = 0
            self.find_position = "1.0"

            while True:
                # Search for next occurrence
                search_kwargs = {}
                if not self.find_case_sensitive:
                    search_kwargs['nocase'] = True

                pos = self.editor_text.text.search(
                    self.find_text,
                    self.find_position,
                    tk.END,
                    **search_kwargs
                )

                if not pos:
                    break

                # Replace it
                end_pos = f"{pos}+{len(self.find_text)}c"
                self.editor_text.text.delete(pos, end_pos)
                self.editor_text.text.insert(pos, self.replace_text)

                # Move past this replacement
                self.find_position = f"{pos}+{len(self.replace_text)}c"
                count += 1

            self._set_status(f"Replaced {count} occurrences")
            self.replace_dialog.destroy()

        ttk.Button(button_frame, text="Find Next", command=do_find).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Replace", command=do_replace).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Replace All", command=do_replace_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Cancel", command=self.replace_dialog.destroy).pack(side=tk.LEFT, padx=2)

    # Helper methods

    def _refresh_editor(self):
        """Load program into editor widget.

        Line numbers are part of the text content as entered by user.
        No formatting is applied to preserve compatibility with real MBASIC.
        """

        self.editor_text.text.delete(1.0, tk.END)
        for line_num, line_text in self.program.get_lines():
            # Insert line exactly as stored from program manager - no formatting applied here
            # to preserve compatibility with real MBASIC for program text.
            # (Note: "formatting may occur elsewhere" refers to the Variables and Stack windows,
            # which DO format data for display - not the editor/program text itself)
            self.editor_text.text.insert(tk.END, line_text + "\n")

        # Clear error indicators
        self.editor_text.clear_all_errors()

    def _save_editor_to_program(self):
        """Save editor content back to program.

        Returns:
            bool: True if all lines parsed successfully, False if any errors occurred
        """

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

    def _sync_program_to_runtime(self):
        """Sync program to runtime, conditionally preserving PC.

        Updates runtime's statement_table and line_text_map from self.program.

        PC handling:
        - If running and not paused at breakpoint: Preserves PC and execution state
        - If paused at breakpoint: Resets PC to halted (prevents accidental resumption)
        - If not running: Resets PC to halted for safety

        This allows LIST and other commands to see the current program without
        accidentally triggering execution. When paused at a breakpoint, the PC is
        intentionally reset; when the user continues, the runtime state already
        has the correct PC.
        """
        from src.pc import PC

        # Preserve current PC if it's valid (execution in progress)
        # Otherwise ensure it stays halted
        old_pc = self.runtime.pc

        # Clear and rebuild statement table
        self.runtime.statement_table.statements.clear()
        self.runtime.statement_table._keys_cache = None

        # Update line text map
        self.runtime.line_text_map = dict(self.program.lines)

        # Rebuild statement table from program ASTs
        for line_num in sorted(self.program.line_asts.keys()):
            line_ast = self.program.line_asts[line_num]
            for stmt_offset, stmt in enumerate(line_ast.statements):
                pc = PC(line_num, stmt_offset)
                self.runtime.statement_table.add(pc, stmt)

        # Restore PC only if execution is actually running
        # Otherwise ensure halted (don't accidentally start execution)
        if self.running and not self.paused_at_breakpoint:
            # Execution is running - preserve execution state
            self.runtime.pc = old_pc
        else:
            # No execution in progress - ensure halted
            self.runtime.pc = PC.halted()

    def _validate_editor_syntax(self):
        """Validate syntax of all lines in editor and update error markers.

        Validates each line independently as entered - immediate feedback.
        """
        import re

        # Get editor content
        editor_content = self.editor_text.text.get(1.0, tk.END)

        # Clear existing error markers
        self.editor_text.clear_all_errors()

        # Collect errors to show in output
        errors_found = []

        # Check each line independently (per-line validation)
        # Note: This method is called:
        # - With 100ms delay after cursor movement/clicks (to avoid excessive validation during rapid editing)
        # - Immediately when focus leaves editor (to ensure validation before switching windows)
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
            # Only show full error list in output if there are multiple errors.
            # For single errors, the red ? icon in the editor is sufficient feedback.
            # This avoids cluttering the output pane with repetitive messages during editing.
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
        else:
            # No errors - clear any previous error status
            if self.status_label:
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
        # Clear yellow statement highlight when clicking and paused at breakpoint
        # (allows text selection to be visible). The highlight is restored when
        # execution resumes or when stepping to the next statement.
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

    def _on_focus_in(self, event):
        """Handle focus entering editor - show auto-number prompt if empty."""
        # Always ensure cursor is visible when focus enters
        # Force cursor to be visible by explicitly setting insert properties
        self.editor_text.text.config(insertwidth=2)  # Set cursor width
        self.editor_text.text.focus_force()  # Force focus to text widget

        # Ensure cursor position is visible
        try:
            cursor_pos = self.editor_text.text.index(tk.INSERT)
            self.editor_text.text.see(cursor_pos)
        except:
            # If there's any issue, set cursor to start
            self.editor_text.text.mark_set(tk.INSERT, "1.0")
            self.editor_text.text.see("1.0")

        if not self.auto_number_enabled:
            return

        # Check if editor is empty
        content = self.editor_text.text.get(1.0, tk.END).strip()
        if not content:
            # Editor is empty - insert initial line number
            self.editor_text.text.insert(1.0, f"{self.auto_number_start} ")
            self.editor_text.text.mark_set(tk.INSERT, "1.end")
            self.editor_text.text.see(tk.INSERT)  # Ensure cursor is visible
            return

        # Check if cursor is at start of empty line
        current_pos = self.editor_text.text.index(tk.INSERT)
        line_index = int(current_pos.split('.')[0])
        col_index = int(current_pos.split('.')[1])

        # Get current line text
        line_text = self.editor_text.text.get(f'{line_index}.0', f'{line_index}.end')

        # If at start of completely empty line, add line number
        if col_index == 0 and not line_text.strip():
            # Find what the next line number should be
            import re
            existing_lines = []
            all_text = self.editor_text.text.get(1.0, tk.END)
            for line in all_text.split('\n'):
                match = re.match(r'^\s*(\d+)', line)
                if match:
                    existing_lines.append(int(match.group(1)))

            if existing_lines:
                next_line_num = max(existing_lines) + self.auto_number_increment
            else:
                next_line_num = self.auto_number_start

            self.editor_text.text.insert(f'{line_index}.0', f"{next_line_num} ")
            self.editor_text.text.mark_set(tk.INSERT, f'{line_index}.end')
            self.editor_text.text.see(tk.INSERT)  # Ensure cursor is visible

    def _remove_blank_lines(self):
        """Remove all blank lines from the editor (except final line).

        Removes blank lines to keep program clean, but preserves the final
        line. Tk Text widgets always end with a newline character (Tk design -
        text content ends at last newline, so there's always an empty final line).

        Currently called only from _on_enter_key (after each Enter key press), not
        after pasting or other modifications. This provides cleanup when the user
        presses Enter to move to a new line.
        """

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
        import re
        from lexer import tokenize
        from parser import Parser

        if not self.auto_number_enabled:
            return None  # Allow default behavior

        # Check if there's a text selection - if yes, let default behavior handle it
        # (default behavior: delete selection, insert newline)
        try:
            if self.editor_text.text.tag_ranges(tk.SEL):
                # There's a selection - delete it and insert newline
                self.editor_text.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
                self.editor_text.text.insert(tk.INSERT, '\n')
                return 'break'
        except tk.TclError:
            # No selection
            pass

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

        # At this point, the editor may contain blank lines inserted by user actions.
        # Blank line removal is handled by _remove_blank_lines() which is scheduled
        # asynchronously after key presses via _on_key_press()

        # Find where current_line_num is now in the sorted editor
        # and find the next line number after it
        editor_content = self.editor_text.text.get('1.0', 'end')
        lines = editor_content.split('\n')
        current_line_text_index = None
        next_existing_line_num = None

        # Get all line numbers
        all_line_nums = []
        for idx, line in enumerate(lines):
            line_match = re.match(r'^\s*(\d+)', line)
            if line_match:
                line_num = int(line_match.group(1))
                all_line_nums.append(line_num)
                if line_num == current_line_num:
                    current_line_text_index = idx + 1  # Tk uses 1-based indexing

        # Find the next line number after current
        if all_line_nums:
            all_line_nums.sort()
            for ln in all_line_nums:
                if ln > current_line_num:
                    next_existing_line_num = ln
                    break

        # Calculate what the new line number should be
        if next_existing_line_num is None:
            # At end of program - use current + increment
            new_line_num = current_line_num + self.auto_number_increment
        else:
            # In middle - try to use current + increment if it fits
            tentative = current_line_num + self.auto_number_increment
            if tentative < next_existing_line_num:
                new_line_num = tentative
            else:
                # No room - try midpoint
                from src.ui.ui_helpers import calculate_midpoint
                midpoint = calculate_midpoint(current_line_num, next_existing_line_num)
                if midpoint is not None:
                    new_line_num = midpoint
                else:
                    # No room at all - offer to renumber
                    response = messagebox.askyesno(
                        "No Room",
                        f"No room to insert line between {current_line_num} and {next_existing_line_num}.\n\n"
                        f"Would you like to renumber the program to make room?"
                    )
                    if response:
                        # Renumber to make room
                        self._save_editor_to_program()
                        self.cmd_renum(f"10,0,10")
                        self._refresh_editor()
                        # After renumber, user can try again
                    else:
                        # User declined - just move to next line
                        if current_line_text_index is not None:
                            next_line_index = current_line_text_index + 1
                            self.editor_text.text.mark_set(tk.INSERT, f'{next_line_index}.0')
                            self.editor_text.text.see(f'{next_line_index}.0')
                    return 'break'

        # Insert the new line number
        if next_existing_line_num is None:
            # At end - add at bottom
            last_char = self.editor_text.text.get("end-2c", "end-1c")
            if last_char != '\n':
                self.editor_text.text.insert(tk.END, '\n')
            self.editor_text.text.insert(tk.END, f'{new_line_num} ')
            self.editor_text.text.mark_set(tk.INSERT, tk.END)
            self.editor_text.text.see(tk.END)
        else:
            # In middle - insert after current line
            if current_line_text_index is not None:
                insert_at_index = current_line_text_index + 1
                self.editor_text.text.insert(f'{insert_at_index}.0', f'{new_line_num} \n')
                self.editor_text.text.mark_set(tk.INSERT, f'{insert_at_index}.{len(str(new_line_num)) + 1}')
                self.editor_text.text.see(f'{insert_at_index}.0')

        return 'break'  # Prevent default Enter behavior

    def _on_paste(self, event):
        """Handle paste event - sanitize clipboard content.

        Returns:
            'break' to prevent default paste, None to allow it
        """

        try:
            # Get clipboard content
            clipboard_text = self.root.clipboard_get()

            # Sanitize: clear parity bits and filter control characters
            sanitized_text, was_modified = sanitize_and_clear_parity(clipboard_text)

            # Check if this is a simple inline paste (no newlines, pasting into existing line)
            import re
            if '\n' not in sanitized_text:
                # Single line paste - check if current line has existing content
                current_pos = self.editor_text.text.index(tk.INSERT)
                current_line_index = int(current_pos.split('.')[0])
                current_line_text = self.editor_text.text.get(
                    f'{current_line_index}.0',
                    f'{current_line_index}.end'
                ).strip()

                # If current line has content (not blank), do simple inline paste
                # (cursor can be at start, middle, or end - we just paste at cursor position)
                if current_line_text:
                    # Delete selected text if any
                    try:
                        self.editor_text.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    except tk.TclError:
                        pass

                    # Simple inline paste
                    self.editor_text.text.insert(tk.INSERT, sanitized_text)

                    if was_modified:
                        self._set_status("Pasted content was sanitized (control characters removed)")

                    return 'break'

            # Multi-line paste or single-line paste into blank line - use auto-numbering logic
            # Note: Single-line paste into existing line uses different logic (inline paste above).
            # The auto-numbering path handles:
            # 1. Multi-line paste: sanitized_text contains \n → multiple lines to process
            # 2. Single-line paste into blank line: current_line_text empty → one line to process
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
                    # Blank line (skip unless it's the last line)
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

            # Check if current line only has an auto-number prompt (e.g., "100 " from FocusIn)
            # If so, delete it before pasting to avoid duplication
            current_pos = self.editor_text.text.index(tk.INSERT)
            current_line_index = int(current_pos.split('.')[0])
            current_line_text = self.editor_text.text.get(
                f'{current_line_index}.0',
                f'{current_line_index}.end'
            )
            # Check if line is just a number followed by space(s) (auto-number prompt)
            if re.match(r'^\d+\s+$', current_line_text):
                # Delete the auto-number prompt line
                self.editor_text.text.delete(f'{current_line_index}.0', f'{current_line_index}.end')
                # Move cursor to start of line
                self.editor_text.text.mark_set(tk.INSERT, f'{current_line_index}.0')

            self.editor_text.text.insert(tk.INSERT, sanitized_text)

            # After multi-line paste, if cursor is at start of empty line, add auto-number prompt
            if '\n' in sanitized_text and self.auto_number_enabled:
                current_pos = self.editor_text.text.index(tk.INSERT)
                line_index = int(current_pos.split('.')[0])
                col_index = int(current_pos.split('.')[1])
                line_text = self.editor_text.text.get(f'{line_index}.0', f'{line_index}.end')

                # If at start of empty line, add next line number
                if col_index == 0 and not line_text.strip():
                    # Find what the next line number should be
                    existing_lines = []
                    all_text = self.editor_text.text.get(1.0, tk.END)
                    for line in all_text.split('\n'):
                        match = re.match(r'^\s*(\d+)', line)
                        if match:
                            existing_lines.append(int(match.group(1)))

                    if existing_lines:
                        next_line_num = max(existing_lines) + self.auto_number_increment
                    else:
                        next_line_num = self.auto_number_start

                    self.editor_text.text.insert(f'{line_index}.0', f"{next_line_num} ")
                    self.editor_text.text.mark_set(tk.INSERT, f'{line_index}.end')

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
        # Clear yellow statement highlight on any keypress when paused at breakpoint
        # Clears on ANY key (even arrows/function keys) because: 1) user interaction during
        # debugging suggests intent to modify/inspect code, making highlight less relevant,
        # and 2) prevents visual artifacts when text IS modified (highlight is tag-based and
        # editing shifts character positions, causing highlight to drift or split incorrectly).
        if self.paused_at_breakpoint:
            self._clear_statement_highlight()

        # Schedule blank line removal after key is processed
        self.root.after(10, self._remove_blank_lines)

        # Ignore special keys (arrows, function keys, modifiers, etc.)
        if len(event.char) != 1:
            return None

        # Allow backspace and delete - these modify text via deletion, not by inserting
        # printable characters. We explicitly allow them here before validation logic.
        # Note: These are control characters (ASCII 8 and 127) but we need them for
        # text editing. Other control characters are blocked by validation later.
        char_code = ord(event.char)
        if char_code in (8, 127):  # Backspace (0x08) or Delete (0x7F)
            return None

        # Allow keyboard shortcuts with Control or Alt modifier keys to propagate
        # This ensures shortcuts like Ctrl+B, Ctrl+S, etc. reach their handlers
        # event.state contains modifier flags:
        # 0x0004 = Control, 0x0008 = Alt/Option, 0x0001 = Shift
        if event.state & 0x000C:  # Control or Alt pressed
            return None

        # Clear parity bit
        from src.input_sanitizer import clear_parity
        char = clear_parity(event.char)

        # Check if character is valid
        if not is_valid_input_char(char):
            # Block invalid character
            return 'break'

        # If parity bit was set, insert the cleared character instead
        if char != event.char:
            self.editor_text.text.insert(tk.INSERT, char)
            return 'break'

        # Allow valid character
        return None

    def _check_line_change(self):
        """Check if cursor moved off a line and trigger auto-sort if line number changed."""
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

        # Determine if program needs to be re-sorted:
        # 1. Line number changed on existing line (both old and new are not None), OR
        # 2. Line number was removed (old was not None, new is None and line has content)
        #
        # Don't trigger sort when:
        # - old_line_num is None: First time tracking this line (cursor just moved here, no editing yet)
        # - This prevents unnecessary re-sorting when user clicks around without making changes
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
        self._smart_insert_line()
        return 'break'

    def _smart_insert_line(self):
        """Smart insert - insert blank line between current and next line.

        Uses ui_helpers to calculate appropriate line number:
        - If gap exists, inserts at midpoint
        - If no gap, offers to renumber

        Triggered by Ctrl+I keyboard shortcut.
        """
        from src.ui.ui_helpers import calculate_midpoint
        import re

        # Get current line BEFORE refresh
        current_pos = self.editor_text.text.index(tk.INSERT)
        current_line_index = int(current_pos.split('.')[0])
        current_line_text = self.editor_text.text.get(
            f'{current_line_index}.0',
            f'{current_line_index}.end'
        ).strip()

        # Parse current line number BEFORE refresh
        match = re.match(r'^(\d+)', current_line_text)
        if not match:
            messagebox.showinfo("Smart Insert", "Current line has no line number.\nAdd a line number first.")
            return

        current_line_num = int(match.group(1))
        # Save the editor to program to get rid of any blank numbered lines
        self._save_editor_to_program()
        self._refresh_editor()

        # Now find the line with current_line_num in the refreshed editor
        # and move cursor back to it, and build all_line_numbers at the same time
        all_line_numbers = []
        restored_line_index = None
        editor_content = self.editor_text.text.get('1.0', 'end')
        for idx, line in enumerate(editor_content.split('\n')):
            line_match = re.match(r'^\s*(\d+)', line)
            if line_match:
                line_num = int(line_match.group(1))
                all_line_numbers.append(line_num)
                if line_num == current_line_num:
                    restored_line_index = idx + 1  # Tk uses 1-based indexing

        # Restore cursor to the original line number
        if restored_line_index is not None:
            self.editor_text.text.mark_set(tk.INSERT, f'{restored_line_index}.0')
            self.editor_text.text.see(f'{restored_line_index}.0')

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

        # DON'T save to program yet - the line only has a line number with no statement,
        # so _save_editor_to_program() will skip it (only saves lines with statements).
        # Just position the cursor on the new line so user can start typing. The line
        # will be saved to program when:
        # 1. User types a statement and triggers _on_key_release -> _save_editor_to_program()
        # 2. User switches focus or saves the file
        # Note: This line won't be removed by _remove_blank_lines() because it contains
        # the line number (not completely blank), but it won't be saved to the program
        # until content is added.

        # Position cursor at the end of the line number (ready to type code)
        col_pos = len(f'{insert_num} ')
        self.editor_text.text.mark_set('insert', f'{insert_index}.{col_pos}')
        self.editor_text.text.see(f'{insert_index}.0')

    def _scroll_to_line(self, line_number):
        """Scroll editor to show the specified BASIC line number.

        Args:
            line_number: BASIC line number to scroll to
        """

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
                # Found the line - use char positions for highlighting
                # Note: char_start/char_end from runtime are 0-based column offsets within the line.
                # Tk text widget uses 0-based column indexing, so these offsets directly map to
                # Tk indices. The parser ensures positions match the displayed line formatting.
                # If highlighting fails (try/except below), it indicates a mismatch between
                # runtime coordinate system and editor display (which would require investigation).

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

            # Handle interpreter state (input needed, error, halted, or running)
            if state.input_prompt is not None:
                # INPUT statement needs user input - pause execution
                self.running = False
                # Update UI state to enable immediate pane for input
                self._update_immediate_status()
                # Clear and focus immediate entry for user input
                self.immediate_entry.delete(0, tk.END)
                self.immediate_entry.focus_force()
                # Don't schedule next tick - will resume when user provides input
                return

            elif state.error_info:
                # Error state
                self.running = False
                self.paused_at_breakpoint = True  # Allow Continue to work after error
                error_msg = state.error_info.error_message
                line_num = state.error_info.pc.line_num
                self._add_output(f"\n--- Execution error: {error_msg} ---\n")
                self._add_output("(Edit the line and click Continue to retry, or Stop to end)\n")
                self._set_status(f"Error at line {line_num} - Edit and Continue, or Stop")
                self._update_immediate_status()

                # Highlight the error statement (yellow highlight)
                if state.current_statement_char_start > 0 or state.current_statement_char_end > 0:
                    self._highlight_current_statement(state.current_line, state.current_statement_char_start, state.current_statement_char_end)

                # Mark the error line with red ? indicator
                if line_num and line_num != "?":
                    try:
                        line_num_int = int(line_num)
                        self.editor_text.set_error(line_num_int, True, error_msg)
                    except (ValueError, AttributeError, TypeError) as e:
                        pass
                # Update stack and variables to show state at error
                if self.stack_visible:
                    self._update_stack()
                if self.variables_visible:
                    self._update_variables()

            elif not self.runtime.pc.is_running():
                # Halted - check what's at PC to determine if done or paused
                self.running = False
                pc = self.runtime.pc
                if pc.line is None:
                    # Past end of program
                    self._add_output("\n--- Program finished ---\n")
                    self._set_status("Ready")
                    self._update_immediate_status()
                    self._clear_statement_highlight()
                else:
                    # Get statement at PC to check if it's END or steppable
                    stmt = self.runtime.statement_table.get(pc)
                    if stmt and stmt.__class__.__name__ == 'EndStatementNode':
                        # Stopped at END statement - don't highlight
                        self._add_output("\n--- Program finished ---\n")
                        self._set_status("Ready")
                        self._update_immediate_status()
                        self._clear_statement_highlight()
                    else:
                        # Paused at steppable statement - highlight it
                        self.paused_at_breakpoint = True
                        self._add_output(f"\n→ Paused at line {state.current_line}\n")
                        self._set_status(f"Paused at line {state.current_line} - Use toolbar: Step/Stmt/Cont/Stop")
                        self._update_immediate_status()
                        # Highlight current statement when paused
                        if state.current_statement_char_start > 0 or state.current_statement_char_end > 0:
                            self._highlight_current_statement(state.current_line, state.current_statement_char_start, state.current_statement_char_end)
                        if self.stack_visible:
                            self._update_stack()
                        if self.variables_visible:
                            self._update_variables()

            else:
                # Running - highlight current statement (brief flash effect)
                if state.current_statement_char_start > 0 or state.current_statement_char_end > 0:
                    self._highlight_current_statement(state.current_line, state.current_statement_char_start, state.current_statement_char_end)
                # Schedule next tick
                self.tick_timer_id = self.root.after(10, self._execute_tick)

        except Exception as e:
            import traceback
            self.running = False
            self.paused_at_breakpoint = True  # Allow Continue to work after exception

            # Gather context for debug logging
            state = self.interpreter.state
            context = {
                'current_line': state.current_line,
                'halted': not self.runtime.pc.is_running(),
                'pc': str(self.runtime.pc)
            }
            if state.error_info:
                context['error_line'] = state.error_info.pc.line_num

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
            state = self.interpreter.state
            if state.current_statement_char_start > 0 or state.current_statement_char_end > 0:
                self._highlight_current_statement(state.current_line, state.current_statement_char_start, state.current_statement_char_end)

            # Mark the error line with red ? indicator
            if error_line and error_line != "?":
                try:
                    error_line_int = int(error_line)
                    self.editor_text.set_error(error_line_int, True, str(e))
                except (ValueError, AttributeError, TypeError) as marker_error:
                    pass
            # Update stack and variables to show state at error
            if self.stack_visible:
                self._update_stack()
            if self.variables_visible:
                self._update_variables()

    # UIBackend interface methods

    def cmd_run(self, start_line=None) -> None:
        """Execute RUN command - run the program.

        Args:
            start_line: Optional line number to start execution at (for RUN line_number)
        """
        try:
            # Clear output
            self._menu_clear_output()
            self._set_status("Running...")

            # Get program AST
            program_ast = self.program.get_program_ast()

            # Reset runtime with current program - RUN clears variables and starts execution
            # Preserves breakpoints (unlike CLEAR which removes program entirely)
            self.runtime.reset_for_run(self.program.line_asts, self.program.lines)

            # Update interpreter's IO handler to output to execution pane
            # (reuse existing interpreter - don't create new one!)
            tk_io = TkIOHandler(self._add_output, self.root, backend=self)
            self.interpreter.io = tk_io

            # Start interpreter (sets up statement table, etc.)
            state = self.interpreter.start()
            if state.error_info:
                self._add_output(f"\n--- Setup error: {state.error_info.error_message} ---\n")
                self._set_status("Error")
                self.running = False
                return

            # If empty program, just show Ready (variables cleared, nothing to execute)
            if not self.program.lines:
                self._set_status('Ready')
                self.running = False
                return

            # If start_line is specified, set PC AFTER start() has called setup()
            # because setup() resets PC to first line
            if start_line is not None:
                from src.runtime import PC
                # Verify the line exists
                if start_line not in self.program.line_asts:
                    self._add_output(f"?Undefined line {start_line}\n")
                    self._set_status("Error")
                    self.running = False
                    return
                # Set PC to start at the specified line (after start() has built statement table)
                self.runtime.pc = PC.from_line(start_line)

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
        return self.editor_text.text.get(1.0, tk.END)

    def cmd_new(self) -> None:
        """Execute NEW command - clear program."""

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
        from src.ui.ui_helpers import list_files

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
        from src.ui.ui_helpers import delete_lines_from_program

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
        from src.ui.ui_helpers import renum_program

        try:
            # Use consolidated RENUM implementation
            old_lines, line_map = renum_program(
                self.program,
                args,
                self._renum_statement,
                runtime=None  # RENUM doesn't need runtime (operates on program structure)
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

    def _renum_statement(self, stmt, line_map):
        """Recursively update line number references in a statement

        Args:
            stmt: Statement node to update
            line_map: dict mapping old line numbers to new line numbers
        """
        import src.ast_nodes as ast_nodes

        stmt_type = type(stmt).__name__

        # GOTO statement
        if stmt_type == 'GotoStatementNode':
            if stmt.line_number in line_map:
                stmt.line_number = line_map[stmt.line_number]

        # GOSUB statement
        elif stmt_type == 'GosubStatementNode':
            if stmt.line_number in line_map:
                stmt.line_number = line_map[stmt.line_number]

        # ON...GOTO/GOSUB statement
        elif stmt_type == 'OnGotoStatementNode' or stmt_type == 'OnGosubStatementNode':
            stmt.target_lines = [
                line_map.get(line, line) for line in stmt.target_lines
            ]

        # IF statement with line number jumps
        elif stmt_type == 'IfStatementNode':
            if stmt.then_line_number is not None and stmt.then_line_number in line_map:
                stmt.then_line_number = line_map[stmt.then_line_number]
            if stmt.else_line_number is not None and stmt.else_line_number in line_map:
                stmt.else_line_number = line_map[stmt.else_line_number]

            # Check for "IF ERL = line_number" pattern
            # According to manual: if ERL is on left side of =, right side is a line number
            if stmt.condition:
                self._renum_erl_comparison(stmt.condition, line_map)

            # Also update statements within THEN/ELSE blocks
            if stmt.then_statements:
                for then_stmt in stmt.then_statements:
                    self._renum_statement(then_stmt, line_map)
            if stmt.else_statements:
                for else_stmt in stmt.else_statements:
                    self._renum_statement(else_stmt, line_map)

        # RESTORE statement
        elif stmt_type == 'RestoreStatementNode':
            if stmt.line_number_expr and hasattr(stmt.line_number_expr, 'value'):
                # It's a literal number
                if stmt.line_number_expr.value in line_map:
                    stmt.line_number_expr.value = line_map[stmt.line_number_expr.value]

        # RUN statement
        elif stmt_type == 'RunStatementNode':
            if hasattr(stmt, 'line_number') and stmt.line_number in line_map:
                stmt.line_number = line_map[stmt.line_number]

        # ON ERROR GOTO statement
        elif stmt_type == 'OnErrorStatementNode':
            if stmt.line_number is not None and stmt.line_number in line_map:
                stmt.line_number = line_map[stmt.line_number]

    def _renum_erl_comparison(self, expr, line_map):
        """Handle ERL = line_number patterns in expressions

        According to MBASIC manual: if ERL appears on the left side of =,
        the number on the right side is treated as a line number reference.

        Also handles: ERL <> line, ERL < line, ERL > line, etc.

        Args:
            expr: Expression node to check
            line_map: dict mapping old line numbers to new line numbers
        """
        # Check if this is a binary operation (comparison)
        if type(expr).__name__ != 'BinaryOpNode':
            return

        # Check if left side is ERL (a VariableNode with name 'ERL')
        left = expr.left
        if type(left).__name__ == 'VariableNode' and left.name == 'ERL':
            # Right side should be renumbered if it's a literal number
            right = expr.right
            if type(right).__name__ == 'NumberNode':
                # Check if this number is a line number in our program
                if right.value in line_map:
                    right.value = line_map[right.value]

    def cmd_cont(self) -> None:
        """Execute CONT command - continue after STOP.

        Resumes execution after:
        - STOP statement
        - Ctrl+C/Break
        - END statement (in some cases)

        Validation: Requires runtime exists and PC is not running.

        The interpreter moves NPC to PC when STOP is executed (see execute_stop()
        in interpreter.py). CONT resumes tick-based execution, which continues from
        the PC position.
        """
        # Check if runtime exists and is in stopped state
        if not self.runtime or self.runtime.pc.is_running():
            self._write_output("?Can't continue")
            return

        try:
            # The interpreter maintains the execution position in PC (moved by STOP).
            # When CONT is executed, tick() will continue from runtime.pc, which was
            # set by execute_stop() to point to the next statement after STOP.
            # No additional position restoration is needed here.

            # Resume tick-based execution from saved PC
            self.running = True
            self._set_status("Running")
            self._execute_tick()

        except Exception as e:
            self._write_output(f"?Error continuing: {e}")

    # Immediate mode methods

    def _focus_immediate_entry(self):
        """Focus the immediate mode entry widget when clicking in immediate mode area."""
        if self.immediate_entry:
            self.immediate_entry.focus_force()

    def _update_immediate_status(self):
        """Update immediate mode panel status based on interpreter state."""

        if not self.immediate_executor or not self.immediate_entry or not self.immediate_prompt_label:
            return

        # Check if safe to execute - use both can_execute_immediate() AND self.running flag
        # The 'not self.running' check prevents immediate mode execution when a program is running,
        # even if the tick hasn't completed yet. This prevents race conditions where immediate
        # mode could execute while the program is still running but between tick cycles.
        can_exec_immediate = self.immediate_executor.can_execute_immediate()
        can_execute = can_exec_immediate and not self.running

        if can_execute:
            # Safe to execute - enable input
            # Update prompt label color based on current state using microprocessor model
            state = self.interpreter.state
            if state.error_info:
                self.immediate_prompt_label.config(text="Error >", fg="red")
            elif not self.runtime.pc.is_running():
                if self.paused_at_breakpoint:
                    self.immediate_prompt_label.config(text="Paused >", fg="orange")
                else:
                    self.immediate_prompt_label.config(text="Ok >", fg="green")
            else:
                self.immediate_prompt_label.config(text="Ok >", fg="green")
            self.immediate_entry.config(state=tk.NORMAL)
        else:
            # Not safe - disable input (program is running)
            # UNLESS we're waiting for INPUT from the user
            if self.interpreter and self.interpreter.state.input_prompt is not None:
                # Enable input for INPUT statement
                self.immediate_prompt_label.config(text=self.interpreter.state.input_prompt, fg="blue")
                self.immediate_entry.config(state=tk.NORMAL)
            else:
                # Program is running, disable input
                self.immediate_prompt_label.config(text="[running] >", fg="red")
                self.immediate_entry.config(state=tk.DISABLED)

    def _execute_immediate(self):
        """Execute immediate mode command."""

        if not self.immediate_executor or not self.immediate_entry:
            messagebox.showwarning("Warning", "Immediate mode not initialized")
            return

        command = self.immediate_entry.get().strip()
        if not command:
            return

        # Check if interpreter is waiting for INPUT during program execution
        if self.interpreter and self.interpreter.state.input_prompt is not None:
            # Provide input to the running program
            value = command
            self.immediate_entry.delete(0, tk.END)
            self._add_output(value + '\n')
            self.interpreter.provide_input(value)
            self.immediate_prompt_label.config(text="Ok >")
            self.running = True
            self.tick_timer_id = self.root.after(10, self._execute_tick)
            return

        # Check if safe to execute
        if not self.immediate_executor.can_execute_immediate():
            self._add_immediate_output("Cannot execute while program is running\n")
            messagebox.showwarning("Warning", "Cannot execute while program is running")
            return

        # Parse editor content into program (in case user typed lines directly)
        # This updates self.program but doesn't affect runtime yet
        self._save_editor_to_program()

        # Sync program to runtime (but don't reset PC - keep current execution state)
        # This allows LIST to work, but doesn't start execution
        self._sync_program_to_runtime()

        # Execute without echoing (GUI design choice that deviates from typical BASIC
        # behavior: command is visible in entry field, and "Ok" prompt is unnecessary
        # in GUI context - only results are shown. Traditional BASIC echoes to output.)
        success, output = self.immediate_executor.execute(command)

        # Show output if any
        if output:
            self._add_immediate_output(output)

        if not success:
            # Only show error dialog on failure
            messagebox.showerror("Error", "Immediate mode error")

        # Clear input
        self.immediate_entry.delete(0, tk.END)

        # If statement set NPC (like RUN/GOTO), move it to PC
        # This is what the tick loop does after executing a statement
        if self.runtime.npc is not None:
            self.runtime.pc = self.runtime.npc
            self.runtime.npc = None

        # Check if interpreter has work to do (after RUN statement)
        # Use has_work() to check if the interpreter is ready to execute (e.g., after RUN command).
        # This is the only location in tk_ui.py that calls has_work().
        has_work = self.interpreter.has_work()
        if has_work:
            # Start execution if not already running
            if not self.running:
                # Switch interpreter IO to output to main output pane (not immediate output)
                tk_io = TkIOHandler(self._add_output, self.root, backend=self)
                self.interpreter.io = tk_io

                # Initialize interpreter state for execution
                # NOTE: Don't call interpreter.start() because it calls runtime.setup()
                # which resets PC to the first statement. The RUN command has already
                # set PC to the correct line (e.g., RUN 120 sets PC to line 120).
                # Instead, we manually perform minimal initialization here.
                #
                # MAINTENANCE RISK: This duplicates part of start()'s logic (see interpreter.start()
                # in src/interpreter.py). If start() changes, this code may need to be updated to
                # match. We only replicate the minimal setup needed (marking first line) while
                # avoiding the full initialization that start() does:
                #   - runtime.setup() (rebuilds tables, resets PC) <- THIS is what we avoid
                #   - Creates new InterpreterState
                #   - Sets up Ctrl+C handler
                # This tradeoff is necessary because RUN [line_number] in immediate mode must
                # preserve the PC set by the RUN command rather than resetting to first statement.
                # TODO: Consider refactoring start() to accept an optional parameter that allows
                # skipping runtime.setup() for cases like RUN [line_number], reducing duplication.
                self.interpreter.state.is_first_line = True

                self._set_status('Running...')
                self.running = True
                self.root.after(10, self._execute_tick)

        # Update variables/stack windows if they exist
        if self.variables_window:
            self._update_variables()
        if self.stack_window and self.stack_visible:
            self._update_stack()

    def _add_immediate_output(self, text):
        """Add text to main output pane.

        Note: This method name is historical/misleading - it actually adds to the
        main output pane, not a separate immediate output pane. It simply forwards
        to _add_output(). In the Tk UI, immediate mode output goes to the main
        output pane. self.immediate_history is always None (see __init__).
        """
        self._add_output(text)

    def _setup_editor_context_menu(self):
        """Setup right-click context menu for editor text widget."""

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
        self.editor_text.text.tag_add(tk.SEL, "1.0", tk.END)
        self.editor_text.text.mark_set(tk.INSERT, "1.0")
        self.editor_text.text.see(tk.INSERT)

    def _setup_output_context_menu(self):
        """Setup right-click context menu for output text widget."""

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
        """Setup right-click context menu for immediate history widget.

        DEAD CODE: This method is never called because immediate_history is always
        None in the Tk UI (see __init__). Retained for potential future use if
        immediate mode gets its own output widget. Related dead code:
        _copy_immediate_selection() and _select_all_immediate().
        """
        if self.immediate_history is None:
            return  # Nothing to set up

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
        try:
            selected_text = self.output_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except tk.TclError:
            pass  # No selection

    def _select_all_output(self):
        """Select all text in output widget."""
        self.output_text.tag_add(tk.SEL, "1.0", tk.END)
        self.output_text.mark_set(tk.INSERT, "1.0")
        self.output_text.see(tk.INSERT)

    def _copy_immediate_selection(self):
        """Copy selected text from immediate history widget to clipboard."""
        try:
            selected_text = self.immediate_history.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except tk.TclError:
            pass  # No selection

    def _select_all_immediate(self):
        """Select all text in immediate history widget."""
        self.immediate_history.tag_add(tk.SEL, "1.0", tk.END)
        self.immediate_history.mark_set(tk.INSERT, "1.0")
        self.immediate_history.see(tk.INSERT)

    def _show_input_row(self, prompt: str = ''):
        """Show the INPUT row with prompt."""

        if self.input_row and self.input_label and self.input_entry:
            # Set prompt text
            self.input_label.config(text=prompt)

            # Clear entry field
            self.input_entry.delete(0, tk.END)

            # Pack the input row (makes it visible)
            self.input_row.pack(fill=tk.X, padx=5, pady=(0, 5))

            # Focus on input field
            self.input_entry.focus_force()

    def _hide_input_row(self):
        """Hide the INPUT row."""
        if self.input_row:
            self.input_row.pack_forget()

    def _submit_input(self):
        """Submit INPUT value from inline input field."""

        if not self.input_entry:
            return

        value = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        self._hide_input_row()

        # Check if interpreter is waiting for input during program execution
        if self.interpreter and self.interpreter.state.input_prompt is not None:
            # Echo input to output
            self._add_output(value + '\n')

            # Provide input to interpreter
            self.interpreter.provide_input(value)

            # Resume execution
            self.running = True
            self.tick_timer_id = self.root.after(10, self._execute_tick)
        elif self.input_queue:
            # Synchronous input() call - put in queue
            self.input_queue.put(value)


class TkIOHandler(IOHandler):
    """IOHandler that routes output to Tk output pane.

    This handler captures program output and sends it to the Tk UI's
    output text widget via a callback function.

    Input strategy rationale:
    - INPUT statement: Uses inline input field when backend available (allowing the user to
      see program output context while typing input), otherwise uses modal dialog as fallback.
      This is availability-based, not a UI preference.
    - LINE INPUT statement: Always uses modal dialog for consistent UX. This is intentional
      because LINE INPUT reads entire lines including whitespace, and the modal dialog provides
      a clearer visual indication that the full line (including spaces) will be captured.
      The inline field is optimized for short INPUT responses, while LINE INPUT often requires
      more careful multi-word input.
    """
    
    def __init__(self, output_callback, root=None, backend=None):
        """Initialize Tk IOHandler.

        Args:
            output_callback: Function to call with output text (str) -> None
            root: Tk root window (needed for dialogs)
            backend: TkBackend instance for accessing INPUT row controls
        """
        self.output_callback = output_callback
        self.input_callback = None  # Will be set when INPUT is needed
        self.root = root  # Tk root window for dialogs
        self.backend = backend  # TkBackend for INPUT row access

    def output(self, text: str, end: str = '\n') -> None:
        """Output text to Tk output pane."""
        full_text = text + end
        if self.output_callback:
            self.output_callback(full_text)

    def input(self, prompt: str = '') -> str:
        """Input from user via inline input field (with fallback to modal dialog).

        Used by INPUT statement to read user input.

        Returns the raw string entered by user. The interpreter handles parsing
        of comma-separated values for INPUT statements with multiple variables.
        Prefers inline input field below output pane when backend is available,
        but falls back to modal dialog if backend is not available.
        """
        # Show prompt in output first
        if prompt:
            self.output(prompt, end='')

        # Use inline input if backend available
        if self.backend and hasattr(self.backend, '_show_input_row'):
            # Show input row
            self.backend._show_input_row(prompt)

            # Block until user submits input (queue blocks)
            result = self.backend.input_queue.get()

            # Hide input row
            self.backend._hide_input_row()

            # Echo input to output
            self.output(result)

            return result
        else:
            # Fallback to dialog if backend not available

            result = simpledialog.askstring(
                "INPUT",
                prompt if prompt else "Enter value:",
                parent=self.root
            )

            if result is None:
                raise KeyboardInterrupt("Input cancelled")

            self.output(result)
            return result

    def input_line(self, prompt: str = '') -> str:
        """Input complete line from user via modal dialog.

        Used by LINE INPUT statement for reading entire line as string.
        Unlike input() which prefers inline input field, this ALWAYS uses
        a modal dialog regardless of backend availability.
        """

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
        """Clear screen - no-op for Tk UI.

        Design decision: GUI output is persistent for review. Users can manually
        clear output via Run > Clear Output menu if desired. CLS command is ignored
        to preserve output history during program execution.
        """
        pass
    
    def error(self, message: str) -> None:
        """Output error message."""
        if self.output_callback:
            self.output_callback(f"ERROR: {message}\n")
    
    def debug(self, message: str) -> None:
        """Output debug message."""
        if self.output_callback:
            self.output_callback(f"DEBUG: {message}\n")
