"""
MBASIC 5.21 Interpreter

Executes BASIC programs from AST.
"""

import sys
from runtime import Runtime
from basic_builtins import BuiltinFunctions
from tokens import TokenType
import ast_nodes


class Interpreter:
    """Execute MBASIC AST"""

    def __init__(self, runtime):
        self.runtime = runtime
        self.builtins = BuiltinFunctions(runtime)

    def run(self):
        """Execute the program from start to finish"""
        # Setup runtime tables
        self.runtime.setup()

        # Execute lines in sequential order
        line_index = 0
        while line_index < len(self.runtime.line_order) and not self.runtime.halted:
            line_number = self.runtime.line_order[line_index]
            line_node = self.runtime.line_table[line_number]

            self.runtime.current_line = line_node

            # Check if we're returning from GOSUB with a specific statement index
            if self.runtime.next_stmt_index is not None:
                self.runtime.current_stmt_index = self.runtime.next_stmt_index
                self.runtime.next_stmt_index = None
            else:
                self.runtime.current_stmt_index = 0

            # Execute all statements on this line
            while self.runtime.current_stmt_index < len(line_node.statements):
                if self.runtime.halted:
                    break

                stmt = line_node.statements[self.runtime.current_stmt_index]
                self.execute_statement(stmt)

                # Check if we need to jump
                if self.runtime.next_line is not None:
                    target_line = self.runtime.next_line
                    self.runtime.next_line = None

                    # Find target line index
                    try:
                        line_index = self.runtime.line_order.index(target_line)
                    except ValueError:
                        raise RuntimeError(f"Undefined line number: {target_line}")

                    # Break to jump to new line (next_stmt_index will be handled at top of outer loop)
                    break

                self.runtime.current_stmt_index += 1
            else:
                # No jump, proceed to next line
                line_index += 1

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

        # Print output (don't add newline if last separator was ; or ,)
        if stmt.separators and stmt.separators[-1] in [';', ',']:
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
        """Execute NEXT statement"""
        # Get variable name
        if stmt.variables:
            var_node = stmt.variables[0]
            var_name = var_node.name + (var_node.type_suffix or "")
        else:
            # NEXT without variable - use innermost loop
            if not self.runtime.for_loops:
                raise RuntimeError("NEXT without FOR")
            var_name = list(self.runtime.for_loops.keys())[-1]

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
            # Continue loop - update variable and jump to statement AFTER the FOR
            self.runtime.set_variable(var_name.rstrip('$%!#'), var_name[-1] if var_name[-1] in '$%!#' else None, new_value)
            self.runtime.next_line = loop_info['return_line']
            # Resume at the statement AFTER the FOR statement
            self.runtime.next_stmt_index = loop_info['return_stmt'] + 1
        else:
            # Loop finished
            self.runtime.pop_for_loop(var_name)

    def execute_while(self, stmt):
        """Execute WHILE statement (just mark position)"""
        # WHILE is handled by checking condition and jumping to WEND or past it
        condition = self.evaluate_expression(stmt.condition)

        if not condition:
            # Skip to matching WEND
            # Find the matching WEND statement
            # For now, throw error - full implementation needs loop tracking
            raise NotImplementedError("WHILE/WEND not fully implemented yet")

    def execute_end(self, stmt):
        """Execute END statement"""
        self.runtime.halted = True

    def execute_stop(self, stmt):
        """Execute STOP statement"""
        self.runtime.halted = True

    def execute_remark(self, stmt):
        """Execute REM statement (do nothing)"""
        pass

    def execute_data(self, stmt):
        """Execute DATA statement (do nothing, data already indexed)"""
        pass

    def execute_read(self, stmt):
        """Execute READ statement"""
        for var_node in stmt.variables:
            # Read next data value
            value = self.runtime.read_data()

            # Convert to appropriate type based on variable suffix
            if var_node.type_suffix == '$':
                value = str(value)
            else:
                value = float(value) if not isinstance(value, (int, float)) else value

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
            var_node = array_def  # It's a VariableNode with subscripts
            dimensions = [int(self.evaluate_expression(sub)) for sub in var_node.subscripts]
            self.runtime.dimension_array(var_node.name, var_node.type_suffix, dimensions)

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
        """Evaluate user-defined function call (DEF FN)"""
        # Get function definition
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
