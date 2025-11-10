"""Debug commands extension for CLI backend.

Adds debugging capabilities to the CLI including:
- BREAK command to set/clear breakpoints
- STEP command for single-stepping
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
        """Add debug commands to help system (not yet implemented)"""
        # TODO: Integrate debug commands with help system
        pass

    def cmd_break(self, args=""):
        """BREAK command - set/clear/list breakpoints.

        Breakpoints can be set before or during execution, but only on existing
        program lines. If you try to set a breakpoint on a non-existent line,
        an error message will be displayed.

        During program execution, when a breakpoint is reached, execution pauses
        at that statement.

        Usage:
            BREAK           - List all breakpoints
            BREAK 100       - Set breakpoint at line 100 (if line exists)
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
        """STEP command - execute one statement and pause.

        Executes a single statement (not a full line). If a line contains multiple
        statements separated by colons, each statement is executed separately.

        This implements statement-level stepping similar to the curses UI 'Step Statement'
        command (Ctrl+T). The curses UI also has a separate 'Step Line' command (Ctrl+K)
        which is not available in the CLI.

        After each step, displays the current line number in format: [{line_num}]

        Usage:
            STEP        - Execute next statement and pause
            STEP n      - Execute n statements
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

                # Check if program ended
                if self.interactive.program_interpreter.state.program_ended:
                    self.interactive.io_handler.output("Program ended")
                    self.stepping = False
                    break

            except Exception as e:
                self.interactive.io_handler.output(f"Error during step: {e}")
                self.stepping = False
                break

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
        """Execute a single statement (not a full line).

        Uses the interpreter's tick() or execute_next() method to execute
        one statement at the current program counter position.

        Note: The actual statement-level granularity depends on the interpreter's
        implementation of tick()/execute_next(). These methods are expected to
        advance the program counter by one statement, handling colon-separated
        statements separately. If the interpreter executes full lines instead,
        this method will behave as line-level stepping rather than statement-level.
        """
        if self.interactive.program_interpreter:
            # Use interpreter's tick() method if available
            if hasattr(self.interactive.program_interpreter, 'tick'):
                self.interactive.program_interpreter.tick()
            else:
                # Fallback to execute_next
                self.interactive.program_interpreter.execute_next()

    def enhance_run_command(self):
        """Enhance RUN command to support breakpoints"""
        # Store original cmd_run
        original_run = self.interactive.cmd_run

        def enhanced_run(start_line=None):
            """Enhanced RUN with breakpoint support

            Args:
                start_line: Optional line number to start execution at
            """
            # Call original to set up runtime/interpreter
            original_run(start_line=start_line)

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
    interactive_mode.cmd_stack = debugger.cmd_stack

    # Enhance RUN command
    debugger.enhance_run_command()

    return debugger