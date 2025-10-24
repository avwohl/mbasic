"""Visual UI backend stub for MBASIC interpreter.

This module provides a stub/template for visual UI implementations.
Visual UI developers should implement this interface for their chosen
framework (Kivy, BeeWare, Qt, etc.).
"""

from .base import UIBackend
from runtime import Runtime
from interpreter import Interpreter


class VisualBackend(UIBackend):
    """Visual UI backend stub.

    This is a minimal stub showing how to implement a visual UI backend.
    It provides the basic structure but does not include actual UI code.

    To create a visual UI:
    1. Choose your UI framework (Kivy, BeeWare, Qt, etc.)
    2. Subclass VisualBackend or UIBackend
    3. Implement start() to initialize and run your UI
    4. Implement command methods to respond to user actions
    5. Use self.io for all I/O (pass custom IOHandler)
    6. Use self.program for program management
    7. Create Interpreter with self.io for execution

    Example structure:
        class MyGUIBackend(VisualBackend):
            def start(self):
                self.init_widgets()
                self.load_program_into_editor()
                self.run_event_loop()

            def on_run_button_clicked(self):
                self.cmd_run()

            def on_line_edited(self, line_num, text):
                self.program.add_line(line_num, text)
    """

    def __init__(self, io_handler, program_manager):
        """Initialize visual backend.

        Args:
            io_handler: Custom IOHandler for your UI (e.g., GUIIOHandler)
            program_manager: ProgramManager instance
        """
        super().__init__(io_handler, program_manager)

        # Runtime and interpreter for program execution
        self.runtime = None
        self.interpreter = None

    def start(self) -> None:
        """Start the visual UI.

        Stub implementation. Override this to:
        1. Create your UI widgets
        2. Load program into editor if needed
        3. Start your UI event loop
        4. Return when user exits

        Example (pseudo-code):
            def start(self):
                self.window = MyWindow()
                self.editor = MyEditor(self.window)
                self.output = MyOutput(self.window)

                # Load program into editor
                for line_num, line_text in self.program.get_lines():
                    self.editor.add_line(line_num, line_text)

                # Connect signals
                self.window.run_button.connect(self.cmd_run)
                self.window.save_button.connect(lambda: self.cmd_save("program.bas"))

                # Run event loop
                self.window.show()
                self.app.exec()
        """
        print("VisualBackend.start() - Override this method")
        print("Create your UI here and start event loop")

    def cmd_run(self) -> None:
        """Execute RUN command - run the program.

        Override or use this implementation:
        1. Get program AST from ProgramManager
        2. Create Runtime and Interpreter
        3. Run the program
        4. Handle errors and display output
        """
        try:
            # Get program AST
            program_ast = self.program.get_program_ast()

            # Create runtime and interpreter
            self.runtime = Runtime(self.program.line_asts, self.program.lines)
            self.interpreter = Interpreter(self.runtime, self.io)

            # Run the program
            self.interpreter.run()

            self.io.output("Program finished")

        except Exception as e:
            self.io.error(f"Runtime error: {e}")

    def cmd_list(self, args: str = "") -> None:
        """Execute LIST command - list program lines.

        Example implementation:
            lines = self.program.get_lines()
            for line_num, line_text in lines:
                self.io.output(line_text)
        """
        lines = self.program.get_lines()
        for line_num, line_text in lines:
            self.io.output(line_text)

    def cmd_new(self) -> None:
        """Execute NEW command - clear program."""
        self.program.clear()
        self.io.output("Program cleared")

    def cmd_save(self, filename: str) -> None:
        """Execute SAVE command - save to file."""
        try:
            self.program.save_to_file(filename)
            self.io.output(f"Saved to {filename}")
        except Exception as e:
            self.io.error(f"Save error: {e}")

    def cmd_load(self, filename: str) -> None:
        """Execute LOAD command - load from file."""
        try:
            success, errors = self.program.load_from_file(filename)
            if errors:
                for line_num, error in errors:
                    self.io.error(error)
            if success:
                self.io.output(f"Loaded from {filename}")
                # Refresh editor display
                self.refresh_editor()
        except Exception as e:
            self.io.error(f"Load error: {e}")

    def refresh_editor(self) -> None:
        """Refresh editor display after loading.

        Override this to update your visual editor with loaded program.
        Example:
            self.editor.clear()
            for line_num, line_text in self.program.get_lines():
                self.editor.add_line(line_num, line_text)
        """
        pass

    def cmd_delete(self, args: str) -> None:
        """Execute DELETE command - delete line range."""
        # Parse args (e.g., "10-50" or "100")
        # Call self.program.delete_line() or delete_range()
        pass

    def cmd_renum(self, args: str) -> None:
        """Execute RENUM command - renumber lines."""
        # Parse args for new_start and increment
        # Call self.program.renumber()
        pass

    def cmd_cont(self) -> None:
        """Execute CONT command - continue after STOP."""
        # Resume execution if runtime is in stopped state
        pass
