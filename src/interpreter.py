"""
MBASIC 5.21 Interpreter

Executes BASIC programs from AST.
"""

import sys
import signal
from runtime import Runtime
from basic_builtins import BuiltinFunctions
from tokens import TokenType
import ast_nodes


class Interpreter:
    """Execute MBASIC AST"""

    def __init__(self, runtime):
        self.runtime = runtime
        self.builtins = BuiltinFunctions(runtime)

    def _setup_break_handler(self):
        """Setup Ctrl+C handler to set break flag"""
        def signal_handler(sig, frame):
            self.runtime.break_requested = True

        # Save old handler to restore later
        self.old_signal_handler = signal.signal(signal.SIGINT, signal_handler)

    def _restore_break_handler(self):
        """Restore original Ctrl+C handler"""
        if hasattr(self, 'old_signal_handler'):
            signal.signal(signal.SIGINT, self.old_signal_handler)

    def run(self):
        """Execute the program from start to finish"""
        # Setup runtime tables
        self.runtime.setup()

        # Setup Ctrl+C handler
        self._setup_break_handler()

        try:
            # Execute from the beginning
            self._run_loop(start_index=0)
        finally:
            # Restore original handler
            self._restore_break_handler()

    def run_from_current(self):
        """Resume execution from current position (for CONT after STOP)

        Does NOT call setup() - preserves all state.
        Starts from runtime.current_line instead of from beginning.
        """
        # Find the current line's index
        if self.runtime.current_line is None:
            raise RuntimeError("No current line to continue from")

        line_number = self.runtime.current_line.line_number
        try:
            line_index = self.runtime.line_order.index(line_number)
        except ValueError:
            raise RuntimeError(f"Current line {line_number} not found in program")

        # Setup Ctrl+C handler
        self._setup_break_handler()

        try:
            # Execute from current position
            self._run_loop(start_index=line_index)
        finally:
            # Restore original handler
            self._restore_break_handler()

    def _run_loop(self, start_index=0):
        """Internal: Execute the main interpreter loop

        Args:
            start_index: Line index to start from (0 for RUN, current for CONT)
        """
        # Execute lines in sequential order
        line_index = start_index
        is_first_line = True  # Track if this is the first line (for CONT)
        while line_index < len(self.runtime.line_order) and not self.runtime.halted:
            # Check for Ctrl+C break
            if self.runtime.break_requested:
                self.runtime.break_requested = False
                # Set stopped state like STOP command
                self.runtime.stopped = True
                self.runtime.stop_line = self.runtime.current_line
                self.runtime.stop_stmt_index = self.runtime.current_stmt_index
                print()  # Newline after ^C
                print(f"Break in {self.runtime.current_line.line_number if self.runtime.current_line else '?'}")
                return

            line_number = self.runtime.line_order[line_index]
            line_node = self.runtime.line_table[line_number]

            import os
            if os.environ.get('DEBUG'):
                print(f"DEBUG: Outer loop: line_index={line_index}, line_number={line_number}")

            self.runtime.current_line = line_node

            # Check if we're returning from GOSUB with a specific statement index
            # OR if we're continuing from STOP at a specific statement index
            if self.runtime.next_stmt_index is not None:
                self.runtime.current_stmt_index = self.runtime.next_stmt_index
                self.runtime.next_stmt_index = None
            elif is_first_line and line_index == start_index and self.runtime.current_stmt_index > 0:
                # Continuing from STOP - use saved statement index (only on first iteration)
                pass
            else:
                self.runtime.current_stmt_index = 0

            # Clear first line flag after handling
            if is_first_line:
                is_first_line = False

            # Execute all statements on this line
            while self.runtime.current_stmt_index < len(line_node.statements):
                if self.runtime.halted:
                    break

                stmt = line_node.statements[self.runtime.current_stmt_index]

                # Execute statement with error handling
                try:
                    import os
                    if os.environ.get('DEBUG'):
                        print(f"DEBUG: Executing line {line_node.line_number} stmt {self.runtime.current_stmt_index}: {type(stmt).__name__}")
                    self.execute_statement(stmt)
                except Exception as e:
                    # Check if we have an error handler
                    if self.runtime.error_handler is not None and not self.runtime.in_error_handler:
                        # Handle the error
                        import os
                        error_code = self._map_exception_to_error_code(e)
                        if os.environ.get('DEBUG'):
                            print(f"DEBUG: Caught error: {e}, handler={self.runtime.error_handler}, error_code={error_code}")
                        self._invoke_error_handler(error_code, line_node.line_number, self.runtime.current_stmt_index)

                        # Break out of statement loop - we're jumping to error handler
                        if os.environ.get('DEBUG'):
                            print(f"DEBUG: Breaking to jump to error handler line {self.runtime.error_handler}")
                        break
                    else:
                        # No error handler or we're already in error handler - re-raise
                        if os.environ.get('DEBUG'):
                            print(f"DEBUG: Re-raising error: {e}, handler={self.runtime.error_handler}, in_handler={self.runtime.in_error_handler}, line={line_node.line_number}")
                            import traceback
                            traceback.print_exc()
                        raise

                # Check if we need to jump
                if self.runtime.next_line is not None:
                    # Break to jump to new line (will be handled by after-loop code)
                    import os
                    if os.environ.get('DEBUG'):
                        print(f"DEBUG: In-loop detected jump to line {self.runtime.next_line}, breaking to after-loop handler")
                    break

                self.runtime.current_stmt_index += 1

            # After executing all statements on the line, check if we need to jump
            # This handles jumps from error handlers
            import os
            if os.environ.get('DEBUG'):
                print(f"DEBUG: After-loop check, next_line={self.runtime.next_line}, halted={self.runtime.halted}")
            if self.runtime.next_line is not None:
                target_line = self.runtime.next_line
                self.runtime.next_line = None

                # Find target line index
                try:
                    line_index = self.runtime.line_order.index(target_line)
                    import os
                    if os.environ.get('DEBUG'):
                        print(f"DEBUG: After-loop jump to line {target_line}, index {line_index}")
                except ValueError:
                    raise RuntimeError(f"Undefined line number: {target_line}")
            else:
                # No jump, proceed to next line
                line_index += 1

    def _map_exception_to_error_code(self, exception):
        """Map Python exception to MBASIC error code"""
        error_msg = str(exception).lower()

        # Division by zero
        if isinstance(exception, ZeroDivisionError) or "division by zero" in error_msg:
            return 11  # Division by zero

        # Type mismatch
        if isinstance(exception, (TypeError, ValueError)):
            # Check for specific type mismatch messages
            if "type mismatch" in error_msg or "invalid literal" in error_msg:
                return 13  # Type mismatch
            return 5  # Illegal function call

        # Out of range
        if isinstance(exception, IndexError) or "subscript out of range" in error_msg:
            return 9  # Subscript out of range

        # Key errors (undefined variable/function)
        if isinstance(exception, KeyError) or "undefined" in error_msg:
            if "function" in error_msg:
                return 18  # Undefined user function
            return 8  # Undefined line number

        # Out of data
        if "out of data" in error_msg:
            return 4  # Out of DATA

        # NEXT without FOR
        if "next without for" in error_msg:
            return 1  # NEXT without FOR

        # RETURN without GOSUB
        if "return without gosub" in error_msg:
            return 3  # RETURN without GOSUB

        # Overflow
        if isinstance(exception, OverflowError):
            return 6  # Overflow

        # Default to illegal function call
        return 5  # Illegal function call

    def _invoke_error_handler(self, error_code, error_line, error_stmt_index):
        """Invoke the error handler"""
        # Set error state
        self.runtime.error_occurred = True
        self.runtime.error_line = error_line
        self.runtime.error_stmt_index = error_stmt_index
        self.runtime.in_error_handler = True

        # Set ERR% and ERL% system variables
        self.runtime.set_variable_raw('err%', error_code)
        self.runtime.set_variable_raw('erl%', error_line)

        # Jump to error handler
        if self.runtime.error_handler_is_gosub:
            # ON ERROR GOSUB - push return address
            self.runtime.push_gosub(error_line, error_stmt_index + 1)

        # Jump to error handler line
        self.runtime.next_line = self.runtime.error_handler
        self.runtime.next_stmt_index = 0

    def find_matching_wend(self, start_line, start_stmt):
        """Find the matching WEND for a WHILE statement

        Args:
            start_line: Line number where WHILE is located
            start_stmt: Statement index where WHILE is located

        Returns:
            (line_number, stmt_index) of matching WEND, or None if not found
        """
        # Start searching from the statement after the WHILE
        depth = 1  # Track nesting depth

        # Get the line index to start searching
        try:
            line_idx = self.runtime.line_order.index(start_line)
        except ValueError:
            return None

        # Start from the next statement in the same line
        stmt_idx = start_stmt + 1

        while line_idx < len(self.runtime.line_order):
            line_num = self.runtime.line_order[line_idx]
            line = self.runtime.line_table[line_num]

            # Search through statements in this line
            while stmt_idx < len(line.statements):
                stmt = line.statements[stmt_idx]

                if isinstance(stmt, ast_nodes.WhileStatementNode):
                    depth += 1
                elif isinstance(stmt, ast_nodes.WendStatementNode):
                    depth -= 1
                    if depth == 0:
                        # Found matching WEND
                        return (line_num, stmt_idx)

                stmt_idx += 1

            # Move to next line
            line_idx += 1
            stmt_idx = 0  # Start from first statement in next line

        return None

    def execute_statement(self, stmt):
        """Execute a single statement"""
        # Get statement type name
        stmt_type = type(stmt).__name__

        # Dispatch to appropriate handler
        handler_name = f"execute_{stmt_type.replace('Node', '').replace('Statement', '').lower()}"
        handler = getattr(self, handler_name, None)

        if handler:
            handler(stmt)
        else:
            raise NotImplementedError(f"Statement not implemented: {stmt_type}")

    # ========================================================================
    # Statement Execution
    # ========================================================================

    def execute_let(self, stmt):
        """Execute LET (assignment) statement"""
        value = self.evaluate_expression(stmt.expression)

        # Type coercion based on type suffix
        if stmt.variable.type_suffix == '%':
            # Integer - truncate towards zero
            value = int(value)
        elif stmt.variable.type_suffix == '$':
            # String
            value = str(value)
        elif stmt.variable.type_suffix in ('!', '#', None):
            # Single or double precision float (or no suffix) - ensure it's numeric
            if not isinstance(value, (int, float)):
                value = float(value) if value else 0

        if stmt.variable.subscripts:
            # Array assignment
            subscripts = [int(self.evaluate_expression(sub)) for sub in stmt.variable.subscripts]
            self.runtime.set_array_element(
                stmt.variable.name,
                stmt.variable.type_suffix,
                subscripts,
                value
            )
        else:
            # Simple variable assignment
            self.runtime.set_variable(
                stmt.variable.name,
                stmt.variable.type_suffix,
                value
            )

    def execute_print(self, stmt):
        """Execute PRINT statement"""
        output_parts = []

        for i, expr in enumerate(stmt.expressions):
            value = self.evaluate_expression(expr)

            # Convert to string
            if isinstance(value, float):
                # Format numbers like BASIC does
                if value == int(value):
                    s = str(int(value))
                else:
                    s = str(value)
                # Add space for positive numbers
                if value >= 0:
                    s = " " + s
                s = s + " "
            else:
                s = str(value)

            output_parts.append(s)

        # Handle separators
        output = ""
        for i, part in enumerate(output_parts):
            output += part
            if i < len(stmt.separators):
                sep = stmt.separators[i]
                if sep == ',':
                    # Tab to next zone (14-character zones in MBASIC)
                    current_len = len(output)
                    next_zone = ((current_len // 14) + 1) * 14
                    output += " " * (next_zone - current_len)
                elif sep == ';':
                    # No spacing (already handled in number formatting)
                    pass
                elif sep == '\n':
                    # Newline
                    output += '\n'

        # Print output (don't add newline if last separator was ; or , or \n)
        if stmt.separators and stmt.separators[-1] in [';', ',', '\n']:
            print(output, end='')
        else:
            print(output)

    def execute_if(self, stmt):
        """Execute IF statement"""
        condition = self.evaluate_expression(stmt.condition)

        # In BASIC, any non-zero value is true
        if condition:
            # Execute THEN clause
            if stmt.then_line_number is not None:
                # THEN line_number
                self.runtime.next_line = stmt.then_line_number
            elif stmt.then_statements:
                # THEN statement(s)
                for then_stmt in stmt.then_statements:
                    self.execute_statement(then_stmt)
                    if self.runtime.next_line is not None:
                        break
        else:
            # Execute ELSE clause
            if stmt.else_line_number is not None:
                # ELSE line_number
                self.runtime.next_line = stmt.else_line_number
            elif stmt.else_statements:
                # ELSE statement(s)
                for else_stmt in stmt.else_statements:
                    self.execute_statement(else_stmt)
                    if self.runtime.next_line is not None:
                        break

    def execute_goto(self, stmt):
        """Execute GOTO statement"""
        # If we're in an error handler and GOTOing out, clear the error state
        if self.runtime.in_error_handler:
            self.runtime.in_error_handler = False
            self.runtime.error_occurred = False
        self.runtime.next_line = stmt.line_number

    def execute_gosub(self, stmt):
        """Execute GOSUB statement"""
        # Push return address
        self.runtime.push_gosub(
            self.runtime.current_line.line_number,
            self.runtime.current_stmt_index + 1
        )

        # Jump to subroutine
        self.runtime.next_line = stmt.line_number

    def execute_return(self, stmt):
        """Execute RETURN statement"""
        # Pop return address
        return_line, return_stmt = self.runtime.pop_gosub()

        # If returning from error handler, clear error state
        if self.runtime.in_error_handler:
            self.runtime.in_error_handler = False
            self.runtime.error_occurred = False

        # Validate that the return address still exists
        if return_line not in self.runtime.line_table:
            raise RuntimeError(f"RETURN error: line {return_line} no longer exists")

        line_node = self.runtime.line_table[return_line]
        # return_stmt can be == len(statements), meaning "past the end, go to next line"
        # but it can't be > len(statements)
        if return_stmt > len(line_node.statements):
            raise RuntimeError(f"RETURN error: statement {return_stmt} in line {return_line} no longer exists")

        # Jump back to the line and statement after GOSUB
        self.runtime.next_line = return_line
        self.runtime.next_stmt_index = return_stmt

    def execute_for(self, stmt):
        """Execute FOR statement"""
        # Evaluate start, end, step
        start = self.evaluate_expression(stmt.start_expr)
        end = self.evaluate_expression(stmt.end_expr)
        step = self.evaluate_expression(stmt.step_expr) if stmt.step_expr else 1

        # Set loop variable to start
        var_name = stmt.variable.name + (stmt.variable.type_suffix or "")
        self.runtime.set_variable(stmt.variable.name, stmt.variable.type_suffix, start)

        # Register loop
        self.runtime.push_for_loop(
            var_name,
            end,
            step,
            self.runtime.current_line.line_number,
            self.runtime.current_stmt_index
        )

    def execute_next(self, stmt):
        """Execute NEXT statement

        Syntax: NEXT [variable [, variable ...]]

        NEXT I, J, K is equivalent to: NEXT I: NEXT J: NEXT K
        If any loop continues (not finished), we jump back and stop processing.
        """
        # Determine which variables to process
        if stmt.variables:
            # Process variables in order: NEXT I, J means close I first, then J
            var_list = stmt.variables
        else:
            # NEXT without variable - use innermost loop
            if not self.runtime.for_loops:
                raise RuntimeError("NEXT without FOR")
            var_list = []  # Will process one loop below

        # If no variables specified, process innermost loop only
        if not var_list:
            var_name = list(self.runtime.for_loops.keys())[-1]
            self._execute_next_single(var_name)
        else:
            # Process each variable in order
            for var_node in var_list:
                var_name = var_node.name + (var_node.type_suffix or "")
                # Process this NEXT
                should_continue = self._execute_next_single(var_name)
                # If this loop continues (jumps back), don't process remaining variables
                if should_continue:
                    return

    def _execute_next_single(self, var_name):
        """Execute NEXT for a single variable.

        Returns:
            True if loop continues (jumped back), False if loop finished
        """
        # Get loop info
        loop_info = self.runtime.get_for_loop(var_name)
        if not loop_info:
            raise RuntimeError(f"NEXT without FOR: {var_name}")

        # Increment loop variable
        current = self.runtime.get_variable(var_name.rstrip('$%!#'), var_name[-1] if var_name[-1] in '$%!#' else None)
        step = loop_info['step']
        new_value = current + step

        # Check if loop should continue
        if (step > 0 and new_value <= loop_info['end']) or (step < 0 and new_value >= loop_info['end']):
            # Validate that the FOR return address still exists
            return_line = loop_info['return_line']
            return_stmt = loop_info['return_stmt']

            if return_line not in self.runtime.line_table:
                raise RuntimeError(f"NEXT error: FOR loop line {return_line} no longer exists")

            line_node = self.runtime.line_table[return_line]
            # return_stmt can be == len(statements), meaning the FOR is the last statement
            # but it can't be > len(statements)
            if return_stmt > len(line_node.statements):
                raise RuntimeError(f"NEXT error: FOR statement in line {return_line} no longer exists")

            # Continue loop - update variable and jump to statement AFTER the FOR
            self.runtime.set_variable(var_name.rstrip('$%!#'), var_name[-1] if var_name[-1] in '$%!#' else None, new_value)
            self.runtime.next_line = return_line
            # Resume at the statement AFTER the FOR statement
            self.runtime.next_stmt_index = return_stmt + 1
            return True  # Loop continues
        else:
            # Loop finished
            self.runtime.pop_for_loop(var_name)
            return False  # Loop finished

    def execute_while(self, stmt):
        """Execute WHILE statement"""
        # Evaluate the condition
        condition = self.evaluate_expression(stmt.condition)

        if not condition:
            # Condition is false - skip to after matching WEND
            wend_pos = self.find_matching_wend(
                self.runtime.current_line.line_number,
                self.runtime.current_stmt_index
            )

            if wend_pos is None:
                raise RuntimeError(f"WHILE without matching WEND at line {self.runtime.current_line.line_number}")

            wend_line, wend_stmt = wend_pos

            # Jump to the statement AFTER the WEND
            self.runtime.next_line = wend_line
            self.runtime.next_stmt_index = wend_stmt + 1
        else:
            # Condition is true - enter the loop
            # Push loop info so WEND knows where to return
            self.runtime.push_while_loop(
                self.runtime.current_line.line_number,
                self.runtime.current_stmt_index
            )

    def execute_wend(self, stmt):
        """Execute WEND statement"""
        # Pop the matching WHILE loop info
        loop_info = self.runtime.peek_while_loop()

        if loop_info is None:
            raise RuntimeError(f"WEND without matching WHILE at line {self.runtime.current_line.line_number}")

        # Jump back to the WHILE statement to re-evaluate the condition
        # The WHILE will either continue the loop or exit and pop the loop
        self.runtime.next_line = loop_info['while_line']
        self.runtime.next_stmt_index = loop_info['while_stmt']

        # Remove the loop from the stack since we're jumping back to WHILE
        # which will re-push if the condition is still true
        self.runtime.pop_while_loop()

    def execute_onerror(self, stmt):
        """Execute ON ERROR GOTO/GOSUB statement"""
        # Set error handler
        # Line number 0 means disable error handling (ON ERROR GOTO 0)
        if stmt.line_number == 0:
            self.runtime.error_handler = None
            self.runtime.error_handler_is_gosub = False
        else:
            self.runtime.error_handler = stmt.line_number
            self.runtime.error_handler_is_gosub = stmt.is_gosub

    def execute_resume(self, stmt):
        """Execute RESUME statement"""
        if not self.runtime.error_occurred:
            raise RuntimeError("RESUME without error")

        # Clear error state
        self.runtime.error_occurred = False
        self.runtime.in_error_handler = False
        self.runtime.set_variable_raw('err%', 0)

        # Determine where to resume
        if stmt.line_number is None or stmt.line_number == 0:
            # RESUME or RESUME 0 - retry the statement that caused the error
            if self.runtime.error_line is None:
                raise RuntimeError("No error line to resume to")
            self.runtime.next_line = self.runtime.error_line
            self.runtime.next_stmt_index = self.runtime.error_stmt_index
        elif stmt.line_number == -1:
            # RESUME NEXT - continue at statement after the error
            if self.runtime.error_line is None:
                raise RuntimeError("No error line to resume from")

            # Check if there's another statement on the same line
            error_line = self.runtime.line_table[self.runtime.error_line]
            import os
            if os.environ.get('DEBUG'):
                print(f"DEBUG: RESUME NEXT from error_line={self.runtime.error_line}, error_stmt_index={self.runtime.error_stmt_index}, line has {len(error_line.statements)} statements")
            if self.runtime.error_stmt_index + 1 < len(error_line.statements):
                # There's another statement on the same line
                self.runtime.next_line = self.runtime.error_line
                self.runtime.next_stmt_index = self.runtime.error_stmt_index + 1
                if os.environ.get('DEBUG'):
                    print(f"DEBUG: RESUME NEXT to line {self.runtime.next_line} stmt {self.runtime.next_stmt_index}")
            else:
                # No more statements on this line, go to next line
                try:
                    error_line_index = self.runtime.line_order.index(self.runtime.error_line)
                    if os.environ.get('DEBUG'):
                        print(f"DEBUG: error_line_index={error_line_index}, len(line_order)={len(self.runtime.line_order)}, line_order={self.runtime.line_order}")
                    if error_line_index + 1 < len(self.runtime.line_order):
                        next_line_num = self.runtime.line_order[error_line_index + 1]
                        self.runtime.next_line = next_line_num
                        self.runtime.next_stmt_index = 0
                        if os.environ.get('DEBUG'):
                            print(f"DEBUG: RESUME NEXT to next line {self.runtime.next_line}")
                    else:
                        # No next line, program ends
                        self.runtime.halted = True
                        if os.environ.get('DEBUG'):
                            print(f"DEBUG: RESUME NEXT - no next line, halting")
                except ValueError:
                    raise RuntimeError(f"Error line {self.runtime.error_line} not found")
        else:
            # RESUME line_number - jump to specific line
            self.runtime.next_line = stmt.line_number
            self.runtime.next_stmt_index = 0

    def execute_end(self, stmt):
        """Execute END statement"""
        self.runtime.halted = True

    def execute_remark(self, stmt):
        """Execute REM statement (do nothing)"""
        pass

    def execute_deftype(self, stmt):
        """Execute DEFINT/DEFSNG/DEFDBL/DEFSTR statement (do nothing at runtime)"""
        # These are compile-time directives handled by the parser
        # At runtime, they do nothing
        pass

    def execute_data(self, stmt):
        """Execute DATA statement (do nothing, data already indexed)"""
        pass

    def execute_read(self, stmt):
        """Execute READ statement"""
        for var_node in stmt.variables:
            # Read next data value (returns AST node)
            data_node = self.runtime.read_data()

            # Evaluate the data node to get actual value
            value = self.evaluate_expression(data_node)

            # Convert to appropriate type based on variable suffix
            if var_node.type_suffix == '$':
                value = str(value)
            elif var_node.type_suffix == '%':
                value = int(value)
            else:
                # Ensure numeric types are float
                if not isinstance(value, (int, float)):
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        value = 0

            # Store in variable
            if var_node.subscripts:
                subscripts = [int(self.evaluate_expression(sub)) for sub in var_node.subscripts]
                self.runtime.set_array_element(var_node.name, var_node.type_suffix, subscripts, value)
            else:
                self.runtime.set_variable(var_node.name, var_node.type_suffix, value)

    def execute_restore(self, stmt):
        """Execute RESTORE statement"""
        self.runtime.restore_data(stmt.line_number if hasattr(stmt, 'line_number') else None)

    def execute_dim(self, stmt):
        """Execute DIM statement"""
        for array_def in stmt.arrays:
            # array_def is an ArrayDeclNode with name and dimensions
            dimensions = [int(self.evaluate_expression(dim)) for dim in array_def.dimensions]
            # Extract type suffix from name if present
            name = array_def.name
            type_suffix = None
            if name and name[-1] in '$%!#':
                type_suffix = name[-1]
                name = name[:-1]
            self.runtime.dimension_array(name, type_suffix, dimensions)

    def execute_erase(self, stmt):
        """Execute ERASE statement

        ERASE removes arrays from memory to reclaim space.
        After ERASE, the array must be re-dimensioned with DIM before use.

        Syntax: ERASE array1, array2, ...
        """
        for array_name in stmt.array_names:
            # Array name already includes type suffix from parser
            # Delete using raw method (already have full name)
            self.runtime.delete_array_raw(array_name)

    def execute_clear(self, stmt):
        """Execute CLEAR statement

        CLEAR resets all variables and closes all open files.
        Optional arguments for string space and stack space are parsed but ignored.

        Syntax: CLEAR [,[string_space][,stack_space]]

        Effects:
        - All simple variables are deleted
        - All arrays are erased
        - All open files are closed
        - COMMON variables list is preserved (for CHAIN compatibility)
        - String space and stack space parameters are ignored (as requested)
        """
        # Clear all variables
        self.runtime.clear_variables()

        # Clear all arrays
        self.runtime.clear_arrays()

        # Close all open files
        for file_num in list(self.runtime.files.keys()):
            try:
                file_obj = self.runtime.files[file_num]
                if hasattr(file_obj, 'close'):
                    file_obj.close()
            except:
                pass
        self.runtime.files.clear()
        self.runtime.field_buffers.clear()

        # Note: We preserve runtime.common_vars for CHAIN compatibility
        # Note: We ignore string_space and stack_space parameters as requested

    def execute_optionbase(self, stmt):
        """Execute OPTION BASE statement

        Sets the lower bound for array indices.
        Must be executed before any DIM statements.

        Syntax: OPTION BASE 0 | 1
        """
        self.runtime.array_base = stmt.base

    def execute_error(self, stmt):
        """Execute ERROR statement

        Simulates an error with the specified error code.
        Sets ERR and ERL, then raises a RuntimeError.

        Syntax: ERROR error_code
        """
        error_code = int(self.evaluate_expression(stmt.error_code))

        # Set error information in variable table (integer variables, lowercase)
        self.runtime.set_variable_raw('err%', error_code)
        if self.runtime.current_line:
            self.runtime.set_variable_raw('erl%', self.runtime.current_line.line_number)
        else:
            self.runtime.set_variable_raw('erl%', 0)

        # Raise the error
        raise RuntimeError(f"ERROR {error_code}")

    def execute_input(self, stmt):
        """Execute INPUT statement"""
        # Show prompt if any
        if stmt.prompt:
            print(stmt.prompt, end='')
        else:
            print("? ", end='')

        # Read input
        line = input()

        # Parse comma-separated values
        values = [v.strip() for v in line.split(',')]

        # Assign to variables
        for i, var_node in enumerate(stmt.variables):
            if i >= len(values):
                raise RuntimeError("Input past end of file")

            value = values[i]

            # Convert type
            if var_node.type_suffix == '$':
                value = str(value)
            else:
                try:
                    value = float(value)
                except ValueError:
                    value = 0

            # Store
            if var_node.subscripts:
                subscripts = [int(self.evaluate_expression(sub)) for sub in var_node.subscripts]
                self.runtime.set_array_element(var_node.name, var_node.type_suffix, subscripts, value)
            else:
                self.runtime.set_variable(var_node.name, var_node.type_suffix, value)

    def execute_load(self, stmt):
        """Execute LOAD statement"""
        # Evaluate filename expression
        filename = self.evaluate_expression(stmt.filename)
        if not isinstance(filename, str):
            raise RuntimeError("LOAD requires string filename")

        # Delegate to interactive mode if available
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            self.interactive_mode.cmd_load(filename)
        else:
            raise RuntimeError("LOAD not available in this context")

    def execute_save(self, stmt):
        """Execute SAVE statement"""
        # Evaluate filename expression
        filename = self.evaluate_expression(stmt.filename)
        if not isinstance(filename, str):
            raise RuntimeError("SAVE requires string filename")

        # Delegate to interactive mode if available
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            self.interactive_mode.cmd_save(filename)
        else:
            raise RuntimeError("SAVE not available in this context")

    def execute_run(self, stmt):
        """Execute RUN statement"""
        # RUN can optionally specify a line number or filename
        if hasattr(stmt, 'line_number') and stmt.line_number:
            # RUN line_number - start at specific line
            self.runtime.next_line = stmt.line_number
        elif hasattr(stmt, 'filename') and stmt.filename:
            # RUN "filename" - load and run file
            filename = self.evaluate_expression(stmt.filename)
            if hasattr(self, 'interactive_mode') and self.interactive_mode:
                self.interactive_mode.cmd_load(filename)
                self.interactive_mode.cmd_run()
            else:
                raise RuntimeError("RUN filename not available in this context")
        else:
            # RUN without arguments - restart from beginning
            if hasattr(self, 'interactive_mode') and self.interactive_mode:
                self.interactive_mode.cmd_run()
            else:
                # In non-interactive context, just restart
                self.runtime.halted = True

    def execute_common(self, stmt):
        """Execute COMMON statement

        COMMON variable1, variable2, array1(), ...

        Declares variables to be shared across CHAIN operations.
        Variable order and type matter, not names.
        """
        # Add variable names to common_vars list in order
        for var_name in stmt.variables:
            # Note: We store the variable name as-is
            if var_name not in self.runtime.common_vars:
                self.runtime.common_vars.append(var_name)

    def execute_chain(self, stmt):
        """Execute CHAIN statement

        CHAIN [MERGE] filename$ [, [line_number] [, ALL] [, DELETE range]]

        Loads and executes another BASIC program, optionally:
        - MERGE: Merges program as overlay instead of replacing
        - line_number: Starts execution at specified line
        - ALL: Passes all variables to the new program
        - DELETE range: Deletes line range after merge
        """
        # Evaluate filename
        filename = self.evaluate_expression(stmt.filename)
        if not isinstance(filename, str):
            raise RuntimeError("CHAIN requires string filename")

        # Evaluate starting line if provided
        start_line = None
        if stmt.start_line:
            start_line = int(self.evaluate_expression(stmt.start_line))

        # Delegate to interactive mode if available
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            self.interactive_mode.cmd_chain(
                filename,
                start_line=start_line,
                merge=stmt.merge,
                all_flag=stmt.all_flag,
                delete_range=stmt.delete_range
            )
        else:
            raise RuntimeError("CHAIN not available in this context")

    def execute_system(self, stmt):
        """Execute SYSTEM statement - exit to OS"""
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            self.interactive_mode.cmd_system()
        else:
            # In non-interactive context, just halt
            print("Goodbye")
            sys.exit(0)

    def execute_merge(self, stmt):
        """Execute MERGE statement"""
        # Evaluate filename expression
        filename = self.evaluate_expression(stmt.filename)
        if not isinstance(filename, str):
            raise RuntimeError("MERGE requires string filename")

        # Delegate to interactive mode if available
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            self.interactive_mode.cmd_merge(filename)
        else:
            raise RuntimeError("MERGE not available in this context")

    def execute_new(self, stmt):
        """Execute NEW statement"""
        # Delegate to interactive mode if available
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            self.interactive_mode.cmd_new()
        else:
            # In non-interactive context, just clear variables
            self.runtime.clear_variables()
            self.runtime.clear_arrays()

    def execute_delete(self, stmt):
        """Execute DELETE statement"""
        # Evaluate start and end expressions
        if stmt.start:
            start = int(self.evaluate_expression(stmt.start))
        else:
            start = None

        if stmt.end:
            end = int(self.evaluate_expression(stmt.end))
        else:
            end = None

        # Delegate to interactive mode if available
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            # Build args string for cmd_delete
            if start and end:
                args = f"{start}-{end}"
            elif start:
                args = f"{start}-"
            elif end:
                args = f"-{end}"
            else:
                args = "-"
            self.interactive_mode.cmd_delete(args)
        else:
            raise RuntimeError("DELETE not available in this context")

    def execute_renum(self, stmt):
        """Execute RENUM statement"""
        # Evaluate new_start and increment expressions
        new_start = 10
        increment = 10

        if stmt.new_start:
            new_start = int(self.evaluate_expression(stmt.new_start))

        if stmt.increment:
            increment = int(self.evaluate_expression(stmt.increment))

        # Delegate to interactive mode if available
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            # Build args string for cmd_renum
            if stmt.new_start and stmt.increment:
                args = f"{new_start},{increment}"
            elif stmt.new_start:
                args = str(new_start)
            else:
                args = ""
            self.interactive_mode.cmd_renum(args)
        else:
            raise RuntimeError("RENUM not available in this context")

    def execute_files(self, stmt):
        """Execute FILES statement"""
        # Evaluate filespec expression
        filespec = ""
        if stmt.filespec:
            filespec = self.evaluate_expression(stmt.filespec)
            if not isinstance(filespec, str):
                raise RuntimeError("FILES requires string filespec")

        # Delegate to interactive mode if available
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            self.interactive_mode.cmd_files(filespec)
        else:
            # In non-interactive context, just list files
            import glob
            import os
            pattern = filespec if filespec else "*.bas"
            files = sorted(glob.glob(pattern))
            if files:
                for filename in files:
                    size = os.path.getsize(filename)
                    print(f"{filename:<20} {size:>8} bytes")
                print(f"\n{len(files)} File(s)")
            else:
                print(f"No files matching: {pattern}")

    def execute_list(self, stmt):
        """Execute LIST statement"""
        # Evaluate start and end expressions
        start = None
        end = None

        if stmt.start:
            start = int(self.evaluate_expression(stmt.start))

        if stmt.end:
            end = int(self.evaluate_expression(stmt.end))

        # Build args string for cmd_list
        args = ""
        if start is not None and end is not None:
            if stmt.single_line:
                # Single line: LIST 100
                args = str(start)
            else:
                # Range: LIST 10-50
                args = f"{start}-{end}"
        elif start is not None:
            # From start to end: LIST 10-
            args = f"{start}-"
        elif end is not None:
            # From beginning to end: LIST -50
            args = f"-{end}"
        # else: LIST with no args lists all

        # Delegate to interactive mode if available
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            self.interactive_mode.cmd_list(args)
        else:
            raise RuntimeError("LIST not available in this context")

    def execute_stop(self, stmt):
        """Execute STOP statement

        STOP pauses program execution and returns to interactive mode.
        All state is preserved:
        - Variables and arrays
        - GOSUB return stack
        - FOR loop stack
        - Current execution position

        User can examine/modify variables, edit lines, then use CONT to resume.
        """
        # Save the current execution position
        # We need to resume from the NEXT statement after STOP
        self.runtime.stopped = True
        self.runtime.stop_line = self.runtime.current_line
        self.runtime.stop_stmt_index = self.runtime.current_stmt_index + 1

        # Print "Break in <line>" message
        if self.runtime.current_line:
            print(f"Break in {self.runtime.current_line.line_number}")
        else:
            print("Break")

        # Halt execution (returns to interactive mode)
        self.runtime.halted = True

    def execute_cont(self, stmt):
        """Execute CONT statement

        CONT resumes execution after a STOP or Break (Ctrl+C).
        Only works in interactive mode.
        """
        if not hasattr(self, 'interactive_mode') or not self.interactive_mode:
            raise RuntimeError("CONT only available in interactive mode")

        if not self.runtime.stopped:
            raise RuntimeError("Can't continue - no program stopped")

        # Resume execution from where we stopped
        self.interactive_mode.cmd_cont()

    # ========================================================================
    # Expression Evaluation
    # ========================================================================

    def evaluate_expression(self, expr):
        """Evaluate an expression node"""
        expr_type = type(expr).__name__

        handler_name = f"evaluate_{expr_type.replace('Node', '').lower()}"
        handler = getattr(self, handler_name, None)

        if handler:
            return handler(expr)
        else:
            raise NotImplementedError(f"Expression not implemented: {expr_type}")

    def evaluate_number(self, expr):
        """Evaluate number literal"""
        return expr.value

    def evaluate_string(self, expr):
        """Evaluate string literal"""
        return expr.value

    def evaluate_variable(self, expr):
        """Evaluate variable reference"""
        if expr.subscripts:
            # Array access
            subscripts = [int(self.evaluate_expression(sub)) for sub in expr.subscripts]
            return self.runtime.get_array_element(expr.name, expr.type_suffix, subscripts)
        else:
            # Simple variable
            return self.runtime.get_variable(expr.name, expr.type_suffix)

    def evaluate_binaryop(self, expr):
        """Evaluate binary operation"""
        left = self.evaluate_expression(expr.left)
        right = self.evaluate_expression(expr.right)

        op = expr.operator

        # Arithmetic
        if op == TokenType.PLUS:
            return left + right
        elif op == TokenType.MINUS:
            return left - right
        elif op == TokenType.MULTIPLY:
            return left * right
        elif op == TokenType.DIVIDE:
            if right == 0:
                raise RuntimeError("Division by zero")
            return left / right
        elif op == TokenType.BACKSLASH:  # Integer division
            if right == 0:
                raise RuntimeError("Division by zero")
            return int(left // right)
        elif op == TokenType.POWER:
            return left ** right
        elif op == TokenType.MOD:
            return left % right

        # Relational
        elif op == TokenType.EQUAL:
            return -1 if left == right else 0
        elif op == TokenType.NOT_EQUAL:
            return -1 if left != right else 0
        elif op == TokenType.LESS_THAN:
            return -1 if left < right else 0
        elif op == TokenType.GREATER_THAN:
            return -1 if left > right else 0
        elif op == TokenType.LESS_EQUAL:
            return -1 if left <= right else 0
        elif op == TokenType.GREATER_EQUAL:
            return -1 if left >= right else 0

        # Logical (bitwise in BASIC)
        elif op == TokenType.AND:
            return int(left) & int(right)
        elif op == TokenType.OR:
            return int(left) | int(right)
        elif op == TokenType.XOR:
            return int(left) ^ int(right)

        else:
            raise NotImplementedError(f"Binary operator not implemented: {op}")

    def evaluate_unaryop(self, expr):
        """Evaluate unary operation"""
        operand = self.evaluate_expression(expr.operand)

        if expr.operator == TokenType.MINUS:
            return -operand
        elif expr.operator == TokenType.NOT:
            return ~int(operand)
        elif expr.operator == TokenType.PLUS:
            return operand
        else:
            raise NotImplementedError(f"Unary operator not implemented: {expr.operator}")

    def evaluate_builtinfunction(self, expr):
        """Evaluate built-in function call"""
        # Get function name
        func_name = expr.name

        # Evaluate arguments
        args = [self.evaluate_expression(arg) for arg in expr.arguments]

        # Call builtin function
        func = getattr(self.builtins, func_name, None)
        if not func:
            raise RuntimeError(f"Unknown function: {func_name}")

        return func(*args)

    def evaluate_functioncall(self, expr):
        """Evaluate function call (built-in or user-defined)"""
        # First, check if it's a built-in function
        func = getattr(self.builtins, expr.name, None)
        if func:
            # It's a builtin function
            args = [self.evaluate_expression(arg) for arg in expr.arguments]
            return func(*args)

        # Not a builtin, check for user-defined function
        func_def = self.runtime.user_functions.get(expr.name)
        if not func_def:
            raise RuntimeError(f"Undefined function: {expr.name}")

        # Evaluate arguments
        args = [self.evaluate_expression(arg) for arg in expr.arguments]

        # Save parameter values (function parameters shadow variables)
        saved_vars = {}
        for i, param in enumerate(func_def.parameters):
            param_name = param.name + (param.type_suffix or "")
            saved_vars[param_name] = self.runtime.get_variable(param.name, param.type_suffix)
            if i < len(args):
                self.runtime.set_variable(param.name, param.type_suffix, args[i])

        # Evaluate function expression
        result = self.evaluate_expression(func_def.expression)

        # Restore parameter values
        for param_name, saved_value in saved_vars.items():
            self.runtime.set_variable(param_name.rstrip('$%!#'), param_name[-1] if param_name[-1] in '$%!#' else None, saved_value)

        return result
