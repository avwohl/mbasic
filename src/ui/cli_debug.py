"""Debug commands extension for CLI backend.

Adds debugging capabilities to the CLI including:
- BREAK command to set/clear breakpoints
- STEP command for single-stepping
- WATCH command for variable inspection
- STACK command for call stack viewing
"""

class CLIDebugger:
    """Debugging extension for CLI mode"""

    def __init__(self, interactive_mode):
        """Initialize debugger with reference to interactive mode.

        Args:
            interactive_mode: The InteractiveMode instance to extend
        """
        self.interactive = interactive_mode
        self.breakpoints = set()  # Set of line numbers
        self.stepping = False  # Single-step mode
        self.watching = set()  # Variable names to watch

        # Add debug commands to interactive mode
        self._register_commands()

    def _register_commands(self):
        """Register debug commands with interactive mode"""
        # Store original start method
        original_start = self.interactive.start

        # Wrap start to add our commands
        def enhanced_start():
            # Add help for debug commands
            self._add_debug_help()
            # Call original
            original_start()

        self.interactive.start = enhanced_start

    def _add_debug_help(self):
        """Add debug commands to help system"""
        # This would integrate with help system
        pass

    def cmd_break(self, args=""):
        """BREAK command - set/clear/list breakpoints.

        Usage:
            BREAK           - List all breakpoints
            BREAK 100       - Set breakpoint at line 100
            BREAK 100-      - Clear breakpoint at line 100
            BREAK CLEAR     - Clear all breakpoints
        """
        args = args.strip()

        if not args:
            # List breakpoints
            if self.breakpoints:
                self.interactive.io_handler.output("Breakpoints set at:")
                for line_num in sorted(self.breakpoints):
                    self.interactive.io_handler.output(f"  Line {line_num}")
            else:
                self.interactive.io_handler.output("No breakpoints set")

        elif args.upper() == "CLEAR":
            # Clear all breakpoints
            self.breakpoints.clear()
            self.interactive.io_handler.output("All breakpoints cleared")

        elif args.endswith("-"):
            # Clear specific breakpoint
            try:
                line_num = int(args[:-1])
                if line_num in self.breakpoints:
                    self.breakpoints.discard(line_num)
                    self.interactive.io_handler.output(f"Breakpoint cleared at line {line_num}")
                else:
                    self.interactive.io_handler.output(f"No breakpoint at line {line_num}")
            except ValueError:
                self.interactive.io_handler.output("Invalid line number")

        else:
            # Set breakpoint
            try:
                line_num = int(args)
                # Check if line exists
                if line_num in self.interactive.program.lines:
                    self.breakpoints.add(line_num)
                    self.interactive.io_handler.output(f"Breakpoint set at line {line_num}")
                else:
                    self.interactive.io_handler.output(f"Line {line_num} does not exist")
            except ValueError:
                self.interactive.io_handler.output("Invalid line number")

    def cmd_step(self, args=""):
        """STEP command - execute one line/statement.

        Usage:
            STEP        - Execute next line and pause
            STEP n      - Execute n lines
        """
        if not self.interactive.program_runtime:
            self.interactive.io_handler.output("No program running. Use RUN first.")
            return

        # Set stepping mode
        self.stepping = True

        # Determine step count
        step_count = 1
        if args.strip():
            try:
                step_count = int(args.strip())
            except ValueError:
                self.interactive.io_handler.output("Invalid step count")
                return

        # Execute steps
        for i in range(step_count):
            try:
                # Execute one step
                self._execute_single_step()

                # Show current position
                if self.interactive.program_runtime.current_line:
                    line_num = self.interactive.program_runtime.current_line.line_number
                    self.interactive.io_handler.output(f"[{line_num}]")

                    # Show watched variables
                    self._show_watched_variables()

                # Check if program ended
                if self.interactive.program_interpreter.state.program_ended:
                    self.interactive.io_handler.output("Program ended")
                    self.stepping = False
                    break

            except Exception as e:
                self.interactive.io_handler.output(f"Error during step: {e}")
                self.stepping = False
                break

    def cmd_watch(self, args=""):
        """WATCH command - add/remove variable watch.

        Usage:
            WATCH           - List watched variables
            WATCH A         - Add variable A to watch list
            WATCH A-        - Remove variable A from watch list
            WATCH CLEAR     - Clear all watches
        """
        args = args.strip().upper()

        if not args:
            # List watches
            if self.watching:
                self.interactive.io_handler.output("Watching variables:")
                for var_name in sorted(self.watching):
                    value = self._get_variable_value(var_name)
                    self.interactive.io_handler.output(f"  {var_name} = {value}")
            else:
                self.interactive.io_handler.output("No variables being watched")

        elif args == "CLEAR":
            # Clear all watches
            self.watching.clear()
            self.interactive.io_handler.output("All watches cleared")

        elif args.endswith("-"):
            # Remove watch
            var_name = args[:-1]
            if var_name in self.watching:
                self.watching.discard(var_name)
                self.interactive.io_handler.output(f"Stopped watching {var_name}")
            else:
                self.interactive.io_handler.output(f"Not watching {var_name}")

        else:
            # Add watch
            var_name = args
            self.watching.add(var_name)
            value = self._get_variable_value(var_name)
            self.interactive.io_handler.output(f"Watching {var_name} = {value}")

    def cmd_stack(self, args=""):
        """STACK command - show call stack.

        Shows current GOSUB call stack and FOR loop stack.
        """
        if not self.interactive.program_runtime:
            self.interactive.io_handler.output("No program running")
            return

        runtime = self.interactive.program_runtime

        # Show GOSUB stack
        if hasattr(runtime, 'return_stack') and runtime.return_stack:
            self.interactive.io_handler.output("GOSUB call stack:")
            for i, return_line in enumerate(runtime.return_stack):
                self.interactive.io_handler.output(f"  {i+1}: Line {return_line}")
        else:
            self.interactive.io_handler.output("No active GOSUB calls")

        # Show FOR loop stack
        if hasattr(runtime, 'for_stack') and runtime.for_stack:
            self.interactive.io_handler.output("FOR loop stack:")
            for i, for_info in enumerate(runtime.for_stack):
                var_name = for_info.get('variable', '?')
                current = for_info.get('current', '?')
                limit = for_info.get('limit', '?')
                self.interactive.io_handler.output(
                    f"  {i+1}: {var_name} = {current} TO {limit}"
                )
        else:
            self.interactive.io_handler.output("No active FOR loops")

    def _execute_single_step(self):
        """Execute a single line/statement"""
        if self.interactive.program_interpreter:
            # Use interpreter's tick() method if available
            if hasattr(self.interactive.program_interpreter, 'tick'):
                self.interactive.program_interpreter.tick()
            else:
                # Fallback to execute_next
                self.interactive.program_interpreter.execute_next()

    def _get_variable_value(self, var_name):
        """Get current value of a variable"""
        if not self.interactive.program_runtime:
            return "N/A"

        try:
            return self.interactive.program_runtime.get_variable(var_name)
        except:
            return "undefined"

    def _show_watched_variables(self):
        """Display all watched variables"""
        if self.watching:
            for var_name in sorted(self.watching):
                value = self._get_variable_value(var_name)
                self.interactive.io_handler.output(f"  {var_name} = {value}")

    def enhance_run_command(self):
        """Enhance RUN command to support breakpoints"""
        # Store original cmd_run
        original_run = self.interactive.cmd_run

        def enhanced_run():
            """Enhanced RUN with breakpoint support"""
            # Call original to set up runtime/interpreter
            original_run()

            # If we have breakpoints, modify interpreter behavior
            if self.breakpoints and self.interactive.program_interpreter:
                self._install_breakpoint_handler()

        # Replace cmd_run
        self.interactive.cmd_run = enhanced_run

    def _install_breakpoint_handler(self):
        """Install breakpoint checking in interpreter"""
        interpreter = self.interactive.program_interpreter

        # Store original execute method
        if hasattr(interpreter, 'execute_next'):
            original_execute = interpreter.execute_next

            def breakpoint_execute():
                """Execute with breakpoint checking"""
                # Check current line for breakpoint
                if interpreter.runtime.current_line:
                    line_num = interpreter.runtime.current_line.line_number
                    if line_num in self.breakpoints:
                        self.interactive.io_handler.output(
                            f"Breakpoint hit at line {line_num}"
                        )
                        # Show line content
                        if line_num in self.interactive.program.lines:
                            line_text = self.interactive.program.lines[line_num].original_text
                            self.interactive.io_handler.output(f"  {line_num} {line_text}")

                        # Show watched variables
                        self._show_watched_variables()

                        # Enter stepping mode
                        self.stepping = True
                        return  # Pause execution

                # Call original
                original_execute()

            # Replace execute_next
            interpreter.execute_next = breakpoint_execute


def add_debug_commands(interactive_mode):
    """Add debug commands to an InteractiveMode instance.

    Args:
        interactive_mode: The InteractiveMode to enhance

    Returns:
        CLIDebugger instance
    """
    debugger = CLIDebugger(interactive_mode)

    # Add commands as methods
    interactive_mode.cmd_break = debugger.cmd_break
    interactive_mode.cmd_step = debugger.cmd_step
    interactive_mode.cmd_watch = debugger.cmd_watch
    interactive_mode.cmd_stack = debugger.cmd_stack

    # Enhance RUN command
    debugger.enhance_run_command()

    return debugger