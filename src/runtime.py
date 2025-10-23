"""
Runtime state management for MBASIC interpreter.

This module manages:
- Variable storage
- Array storage
- Control flow stacks (GOSUB, FOR loops)
- Line number resolution
- DATA statement indexing
- User-defined functions (DEF FN)
- File I/O state
"""

from ast_nodes import DataStatementNode, DefFnStatementNode


class Runtime:
    """Runtime state for BASIC program execution"""

    def __init__(self, ast_or_line_table):
        """Initialize runtime.

        Args:
            ast_or_line_table: Either a ProgramNode AST (old style) or a dict {line_num: LineNode} (new style)
        """
        # Support both old-style (full AST) and new-style (line table dict)
        if isinstance(ast_or_line_table, dict):
            self.ast = None
            self.line_table_dict = ast_or_line_table
        else:
            self.ast = ast_or_line_table
            self.line_table_dict = None

        # Variable storage (PRIVATE - use get_variable/set_variable methods)
        self._variables = {}          # name_with_suffix -> value
        self._arrays = {}             # name_with_suffix -> {'dims': [...], 'data': [...]}
        self.common_vars = []         # List of variable names declared in COMMON (order matters!)
        self.array_base = 0           # Array index base (0 or 1, set by OPTION BASE)

        # Execution control
        self.current_line = None      # Currently executing LineNode
        self.current_stmt_index = 0   # Index of current statement in line
        self.halted = False           # Program finished?
        self.next_line = None         # Set by GOTO/GOSUB for jump
        self.next_stmt_index = None   # Set by RETURN for precise return point

        # Control flow stacks
        self.gosub_stack = []         # [(return_line, return_stmt_index), ...]
        self.for_loops = {}           # var_name -> {'end': val, 'step': val, 'return_line': line, 'return_stmt': idx}
        self.while_loops = []         # [{'while_line': line, 'while_stmt': idx}, ...] - stack of active WHILE loops

        # Line number resolution
        self.line_table = {}          # line_number -> LineNode
        self.line_order = []          # [line_number, ...] in order

        # DATA statements
        self.data_items = []          # [value, value, ...]
        self.data_pointer = 0         # Current READ position
        self.data_line_map = {}       # {data_index: line_number} - tracks which line each data item came from

        # User-defined functions
        self.user_functions = {}      # fn_name -> DefFnStatementNode

        # Note: Type defaults (DEFINT, DEFSNG, etc.) are handled by Parser.def_type_map
        # at parse time, not at runtime

        # File I/O
        self.files = {}               # file_number -> file_handle
        self.field_buffers = {}       # file_number -> buffer_dict

        # Error handling
        self.error_handler = None     # Line number for ON ERROR GOTO/GOSUB
        self.error_handler_is_gosub = False  # True if ON ERROR GOSUB, False if ON ERROR GOTO
        self.error_occurred = False
        self.error_line = None        # Line number where error occurred (for ERL and RESUME)
        self.error_stmt_index = None  # Statement index where error occurred (for RESUME)
        self.in_error_handler = False # True if currently executing error handler

        # ERR and ERL are system variables (integer type), not functions
        # Initialize them in the variable table with % suffix (lowercase)
        # Note: Must do this after _variables is created but before methods are called
        # We'll initialize these after other attributes are set up

        # Random number seed
        self.rnd_last = 0.5

        # STOP/CONT state preservation
        self.stopped = False              # True if program stopped via STOP or Break
        self.stop_line = None             # Line where STOP occurred
        self.stop_stmt_index = None       # Statement index where STOP occurred

        # Break handling (Ctrl+C)
        self.break_requested = False      # True when Ctrl+C pressed during execution

        # Initialize system variables (ERR% and ERL%)
        self.set_variable_raw('err%', 0)
        self.set_variable_raw('erl%', 0)

    def setup(self):
        """
        Initialize runtime by building lookup tables.
        Call this once before execution starts.
        """
        # Build line number table
        if self.line_table_dict:
            # New style: line_table already provided, just populate line_order
            self.line_table = self.line_table_dict
            self.line_order = sorted(self.line_table.keys())
            lines_to_process = self.line_table.values()
        else:
            # Old style: build from AST
            for line in self.ast.lines:
                self.line_table[line.line_number] = line
                self.line_order.append(line.line_number)
            lines_to_process = self.ast.lines
            # Sort line numbers for sequential execution
            self.line_order.sort()

        # Extract DATA values and DEF FN definitions
        for line in lines_to_process:
            for stmt in line.statements:
                if isinstance(stmt, DataStatementNode):
                    # Store data values and track which line they came from
                    for value in stmt.values:
                        data_index = len(self.data_items)
                        if isinstance(value, list):
                            # Flatten nested lists
                            for v in value:
                                self.data_line_map[len(self.data_items)] = line.line_number
                                self.data_items.append(v)
                        else:
                            self.data_line_map[data_index] = line.line_number
                            self.data_items.append(value)
                elif isinstance(stmt, DefFnStatementNode):
                    self.user_functions[stmt.name] = stmt

        return self

    @staticmethod
    def _resolve_variable_name(name, type_suffix, def_type_map=None):
        """
        Resolve the full variable name with type suffix.

        This is the ONLY correct way to determine the storage key for a variable.

        Args:
            name: Variable base name (e.g., 'x', 'foo')
            type_suffix: Explicit type suffix ($, %, !, #) or None/empty string
            def_type_map: Optional dict mapping first letter to default TypeInfo

        Returns:
            tuple: (full_name, type_suffix) where full_name is lowercase name with suffix

        Examples:
            ('x', '%', None) -> ('x%', '%')
            ('x', None, {'x': TypeInfo.SINGLE}) -> ('x!', '!')
            ('x', '', {'x': TypeInfo.INTEGER}) -> ('x%', '%')
        """
        # Name should already be lowercase, but ensure it
        name = name.lower()

        # If explicit suffix provided, use it
        if type_suffix:
            return (name + type_suffix, type_suffix)

        # No explicit suffix - check DEF type map
        if def_type_map:
            first_letter = name[0]
            if first_letter in def_type_map:
                from parser import TypeInfo
                var_type = def_type_map[first_letter]
                if var_type == TypeInfo.STRING:
                    type_suffix = '$'
                elif var_type == TypeInfo.INTEGER:
                    type_suffix = '%'
                elif var_type == TypeInfo.DOUBLE:
                    type_suffix = '#'
                elif var_type == TypeInfo.SINGLE:
                    type_suffix = '!'
                else:
                    # Default to single if unknown
                    type_suffix = '!'
                return (name + type_suffix, type_suffix)

        # No DEF type map or not found - default to single precision
        return (name + '!', '!')

    def get_variable(self, name, type_suffix=None, def_type_map=None):
        """
        Get variable value, returning default if not set.

        Args:
            name: Variable name (e.g., 'x', 'foo')
            type_suffix: Type suffix ($, %, !, #) or None
            def_type_map: Optional DEF type mapping

        Returns:
            Variable value (default 0 for numeric, "" for string)
        """
        # Resolve full variable name
        full_name, resolved_suffix = self._resolve_variable_name(name, type_suffix, def_type_map)

        # Return existing value or default
        if full_name in self._variables:
            return self._variables[full_name]

        # Default values
        if resolved_suffix == '$':
            return ""
        else:
            return 0

    def set_variable(self, name, type_suffix, value, def_type_map=None):
        """
        Set variable value.

        Args:
            name: Variable name
            type_suffix: Type suffix or None
            value: New value
            def_type_map: Optional DEF type mapping
        """
        # Resolve full variable name
        full_name, _ = self._resolve_variable_name(name, type_suffix, def_type_map)
        self._variables[full_name] = value

    def get_variable_raw(self, full_name):
        """
        Get variable by full name (e.g., 'err%', 'erl%').

        Use this only for special cases like system variables.
        For normal variables, use get_variable() instead.

        Args:
            full_name: Full variable name with suffix (lowercase)

        Returns:
            Variable value or None if not found
        """
        return self._variables.get(full_name)

    def set_variable_raw(self, full_name, value):
        """
        Set variable by full name (e.g., 'err%', 'erl%').

        Use this only for special cases like system variables.
        For normal variables, use set_variable() instead.

        Args:
            full_name: Full variable name with suffix (lowercase)
            value: Value to set
        """
        self._variables[full_name] = value

    def clear_variables(self):
        """Clear all variables."""
        self._variables.clear()

    def clear_arrays(self):
        """Clear all arrays."""
        self._arrays.clear()

    def get_all_variables(self):
        """
        Get a copy of all variables.

        Returns:
            dict: Copy of variable table
        """
        return dict(self._variables)

    def get_all_arrays(self):
        """
        Get a copy of all arrays.

        Returns:
            dict: Copy of array table
        """
        return dict(self._arrays)

    def update_variables(self, variables):
        """
        Bulk update variables.

        Args:
            variables: dict of variable_name -> value
        """
        self._variables.update(variables)

    def update_arrays(self, arrays):
        """
        Bulk update arrays.

        Args:
            arrays: dict of array_name -> array_info
        """
        self._arrays.update(arrays)

    def variable_exists(self, full_name):
        """
        Check if a variable exists.

        Args:
            full_name: Full variable name with suffix (lowercase)

        Returns:
            bool: True if variable exists
        """
        return full_name in self._variables

    def array_exists(self, full_name):
        """
        Check if an array exists.

        Args:
            full_name: Full array name with suffix (lowercase)

        Returns:
            bool: True if array exists
        """
        return full_name in self._arrays

    def get_array_element(self, name, type_suffix, subscripts, def_type_map=None):
        """
        Get array element value.

        Args:
            name: Array name
            type_suffix: Type suffix or None
            subscripts: List of subscript values
            def_type_map: Optional DEF type mapping

        Returns:
            Array element value
        """
        # Resolve full array name
        full_name, _ = self._resolve_variable_name(name, type_suffix, def_type_map)

        if full_name not in self._arrays:
            raise RuntimeError(f"Array {full_name} not dimensioned")

        array_info = self._arrays[full_name]
        dims = array_info['dims']
        data = array_info['data']
        base = array_info.get('base', 0)  # Get stored base, default to 0 for old arrays

        # Calculate flat index
        index = self._calculate_array_index(subscripts, dims, base)

        # Bounds check
        if index < 0 or index >= len(data):
            raise RuntimeError(f"Array subscript out of range: {full_name}{subscripts}")

        return data[index]

    def set_array_element(self, name, type_suffix, subscripts, value, def_type_map=None):
        """
        Set array element value.

        Args:
            name: Array name
            type_suffix: Type suffix or None
            subscripts: List of subscript values
            value: Value to set
            def_type_map: Optional DEF type mapping
        """
        # Resolve full array name
        full_name, _ = self._resolve_variable_name(name, type_suffix, def_type_map)

        if full_name not in self._arrays:
            raise RuntimeError(f"Array {full_name} not dimensioned")

        array_info = self._arrays[full_name]
        dims = array_info['dims']
        data = array_info['data']
        base = array_info.get('base', 0)  # Get stored base, default to 0 for old arrays

        index = self._calculate_array_index(subscripts, dims, base)

        if index < 0 or index >= len(data):
            raise RuntimeError(f"Array subscript out of range: {full_name}{subscripts}")

        data[index] = value

    def _calculate_array_index(self, subscripts, dims, base=0):
        """
        Calculate flat array index from multi-dimensional subscripts.

        MBASIC uses row-major order.

        Args:
            subscripts: User-provided subscript values
            dims: Array dimension sizes
            base: Array base (0 or 1)
        """
        if len(subscripts) != len(dims):
            raise RuntimeError(f"Wrong number of subscripts: got {len(subscripts)}, expected {len(dims)}")

        index = 0
        multiplier = 1

        # Calculate index (row-major order)
        for i in range(len(dims) - 1, -1, -1):
            # Adjust subscript by base
            adjusted_subscript = subscripts[i] - base
            index += adjusted_subscript * multiplier

            # Multiplier depends on base
            if base == 0:
                multiplier *= (dims[i] + 1)  # 0-based: 0 to dim inclusive
            else:
                multiplier *= dims[i]  # 1-based: 1 to dim inclusive

        return index

    def dimension_array(self, name, type_suffix, dimensions, def_type_map=None):
        """
        Create/dimension an array.

        Args:
            name: Array name
            type_suffix: Type suffix or None
            dimensions: List of dimension sizes
            def_type_map: Optional DEF type mapping
        """
        # Resolve full array name
        full_name, resolved_suffix = self._resolve_variable_name(name, type_suffix, def_type_map)

        # Calculate total size based on array_base
        # If base is 0: DIM A(10) creates indices 0-10 (11 elements)
        # If base is 1: DIM A(10) creates indices 1-10 (10 elements)
        total_size = 1
        for dim in dimensions:
            if self.array_base == 0:
                total_size *= (dim + 1)  # 0-based: 0 to dim inclusive
            else:
                total_size *= dim  # 1-based: 1 to dim inclusive

        # Default value based on type
        if resolved_suffix == '$':
            default_value = ""
        else:
            default_value = 0

        # Create array
        self._arrays[full_name] = {
            'dims': dimensions,
            'data': [default_value] * total_size,
            'base': self.array_base  # Store base for later access validation
        }

    def delete_array(self, name, type_suffix=None, def_type_map=None):
        """
        Delete an array (for ERASE statement).

        Args:
            name: Array name
            type_suffix: Type suffix or None
            def_type_map: Optional DEF type mapping
        """
        # Resolve full array name
        full_name, _ = self._resolve_variable_name(name, type_suffix, def_type_map)

        if full_name in self._arrays:
            del self._arrays[full_name]

    def delete_array_raw(self, full_name):
        """
        Delete an array by full name.

        Use this when you already have the full name with suffix.

        Args:
            full_name: Full array name with suffix (lowercase)
        """
        if full_name in self._arrays:
            del self._arrays[full_name]

    def read_data(self):
        """
        Read next DATA value for READ statement.

        Returns:
            Next data value

        Raises:
            RuntimeError: If no more data
        """
        if self.data_pointer >= len(self.data_items):
            raise RuntimeError("Out of DATA")

        value = self.data_items[self.data_pointer]
        self.data_pointer += 1
        return value

    def restore_data(self, line_number=None):
        """
        RESTORE data pointer to beginning or to specific line.

        Args:
            line_number: Line to restore to, or None for beginning
        """
        if line_number is None:
            # Restore to beginning
            self.data_pointer = 0
        else:
            # Find first DATA item at or after specified line
            found = False
            for data_index in sorted(self.data_line_map.keys()):
                if self.data_line_map[data_index] >= line_number:
                    self.data_pointer = data_index
                    found = True
                    break

            if not found:
                # No DATA at or after that line - restore to end
                self.data_pointer = len(self.data_items)

    def push_gosub(self, return_line, return_stmt_index):
        """Push GOSUB return address"""
        self.gosub_stack.append((return_line, return_stmt_index))

    def pop_gosub(self):
        """
        Pop GOSUB return address.

        Returns:
            (return_line, return_stmt_index) tuple

        Raises:
            RuntimeError: If stack is empty
        """
        if not self.gosub_stack:
            raise RuntimeError("RETURN without GOSUB")
        return self.gosub_stack.pop()

    def push_for_loop(self, var_name, end_value, step_value, return_line, return_stmt_index):
        """Register a FOR loop"""
        self.for_loops[var_name] = {
            'end': end_value,
            'step': step_value,
            'return_line': return_line,
            'return_stmt': return_stmt_index
        }

    def pop_for_loop(self, var_name):
        """Remove a FOR loop"""
        if var_name in self.for_loops:
            del self.for_loops[var_name]

    def get_for_loop(self, var_name):
        """Get FOR loop info or None"""
        return self.for_loops.get(var_name)

    def push_while_loop(self, while_line, while_stmt_index):
        """Register a WHILE loop"""
        self.while_loops.append({
            'while_line': while_line,
            'while_stmt': while_stmt_index
        })

    def pop_while_loop(self):
        """Remove most recent WHILE loop"""
        if self.while_loops:
            return self.while_loops.pop()
        return None

    def peek_while_loop(self):
        """Get most recent WHILE loop info without removing it"""
        if self.while_loops:
            return self.while_loops[-1]
        return None

    def find_line(self, line_number):
        """
        Find LineNode by line number.

        Args:
            line_number: BASIC line number

        Returns:
            LineNode or None
        """
        return self.line_table.get(line_number)

    def get_next_line(self, current_line_number):
        """
        Get the next line number in sequence.

        Args:
            current_line_number: Current line number

        Returns:
            Next line number or None if at end
        """
        try:
            index = self.line_order.index(current_line_number)
            if index + 1 < len(self.line_order):
                return self.line_order[index + 1]
        except ValueError:
            pass
        return None
