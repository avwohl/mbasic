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

import time
from ast_nodes import DataStatementNode, DefFnStatementNode


def split_variable_name_and_suffix(full_name):
    """
    Split a full variable name into base name and type suffix.

    Args:
        full_name: Full variable name like 'err%', 'x$', 'foo!'

    Returns:
        tuple: (base_name, type_suffix) or (base_name, None) if no suffix

    Examples:
        'err%' -> ('err', '%')
        'x$' -> ('x', '$')
        'foo' -> ('foo', None)
    """
    if full_name and full_name[-1] in '$%!#':
        return (full_name[:-1], full_name[-1])
    return (full_name, None)


class Runtime:
    """Runtime state for BASIC program execution"""

    def __init__(self, ast_or_line_table, line_text_map=None):
        """Initialize runtime.

        Args:
            ast_or_line_table: Either a ProgramNode AST (old style) or a dict {line_num: LineNode} (new style)
            line_text_map: Optional dict {line_num: line_text} for error messages
        """
        # Support both old-style (full AST) and new-style (line table dict)
        if isinstance(ast_or_line_table, dict):
            self.ast = None
            self.line_table_dict = ast_or_line_table
        else:
            self.ast = ast_or_line_table
            self.line_table_dict = None

        # Variable storage (PRIVATE - use get_variable/set_variable methods)
        # Each variable is stored as: name_with_suffix -> {'value': val, 'last_read': {...}, 'last_write': {...}}
        # Note: line -1 in last_write indicates debugger/prompt/internal set (not from program execution)
        self._variables = {}
        self._arrays = {}             # name_with_suffix -> {'dims': [...], 'data': [...]}
        self.common_vars = []         # List of variable names declared in COMMON (order matters!)
        self.array_base = 0           # Array index base (0 or 1, set by OPTION BASE)
        self.option_base_executed = False  # Track if OPTION BASE has been executed (can only execute once)

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
        self.line_text_map = line_text_map or {}  # line_number -> source text (for error messages)

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

        # Trace flag (TRON/TROFF)
        self.trace_on = False             # True if execution trace is enabled

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

    def get_variable(self, name, type_suffix=None, def_type_map=None, token=None):
        """
        Get variable value for program execution, tracking read access.

        This method MUST be called with a token for normal program execution.
        For debugging/inspection without tracking, use get_variable_for_debugger().

        Args:
            name: Variable name (e.g., 'x', 'foo')
            type_suffix: Type suffix ($, %, !, #) or None
            def_type_map: Optional DEF type mapping
            token: REQUIRED - Token object with line and position info for tracking

        Returns:
            Variable value (default 0 for numeric, "" for string)

        Raises:
            ValueError: If token is None (use get_variable_for_debugger instead)
        """
        if token is None:
            raise ValueError("get_variable() requires token parameter. Use get_variable_for_debugger() for debugging.")

        # Resolve full variable name
        full_name, resolved_suffix = self._resolve_variable_name(name, type_suffix, def_type_map)

        # Initialize variable entry if needed
        if full_name not in self._variables:
            # Create with default value
            default_value = "" if resolved_suffix == '$' else 0
            self._variables[full_name] = {
                'value': default_value,
                'last_read': None,
                'last_write': None
            }

        # Track read access
        self._variables[full_name]['last_read'] = {
            'line': getattr(token, 'line', self.current_line.line_number if self.current_line else None),
            'position': getattr(token, 'position', None),
            'timestamp': time.perf_counter()  # High precision timestamp for debugging
        }

        # Return value
        return self._variables[full_name]['value']

    def set_variable(self, name, type_suffix, value, def_type_map=None, token=None, debugger_set=False):
        """
        Set variable value for program execution, tracking write access.

        This method MUST be called with a token for normal program execution.
        For debugger writes, pass debugger_set=True (token can be None).

        Args:
            name: Variable name
            type_suffix: Type suffix or None
            value: New value
            def_type_map: Optional DEF type mapping
            token: REQUIRED (unless debugger_set=True) - Token with line and position
            debugger_set: True if this set is from debugger, not program execution

        Raises:
            ValueError: If token is None and debugger_set is False
        """
        if token is None and not debugger_set:
            raise ValueError("set_variable() requires token parameter. Use debugger_set=True for debugger writes.")

        # Resolve full variable name
        full_name, _ = self._resolve_variable_name(name, type_suffix, def_type_map)

        # Initialize variable entry if needed
        if full_name not in self._variables:
            self._variables[full_name] = {
                'value': None,
                'last_read': None,
                'last_write': None
            }

        # Set value
        self._variables[full_name]['value'] = value

        # Update last_write tracking
        if debugger_set:
            # Debugger/prompt set: use line -1 as sentinel
            self._variables[full_name]['last_write'] = {
                'line': -1,
                'position': None,
                'timestamp': time.perf_counter()
            }
        elif token is not None:
            # Normal program execution or internal set (token.line may be -1 for internal/system variables)
            self._variables[full_name]['last_write'] = {
                'line': getattr(token, 'line', self.current_line.line_number if self.current_line else None),
                'position': getattr(token, 'position', None),
                'timestamp': time.perf_counter()  # High precision timestamp for debugging
            }

    def get_variable_for_debugger(self, name, type_suffix=None, def_type_map=None):
        """
        Get variable value for debugger/inspector WITHOUT updating access tracking.

        This method is intended ONLY for debugger/inspector use to read variable
        values without affecting the access tracking (last_read/last_write). For normal
        program execution, use get_variable() with a token.

        Args:
            name: Variable name (e.g., 'x', 'foo')
            type_suffix: Type suffix ($, %, !, #) or None
            def_type_map: Optional DEF type mapping

        Returns:
            Variable value (default 0 for numeric, "" for string)
        """
        # Resolve full variable name
        full_name, resolved_suffix = self._resolve_variable_name(name, type_suffix, def_type_map)

        # Return existing value or default (no tracking)
        if full_name in self._variables:
            return self._variables[full_name]['value']

        # Default values
        if resolved_suffix == '$':
            return ""
        else:
            return 0

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
        var_entry = self._variables.get(full_name)
        return var_entry['value'] if var_entry else None

    def set_variable_raw(self, full_name, value):
        """
        Set variable by full name (e.g., 'err%', 'erl%').

        Use this only for special cases like system variables.
        For normal variables, use set_variable() instead.

        This now calls set_variable() internally for uniform handling.
        Uses a fake token with line=-1 to indicate internal/system setting.

        Args:
            full_name: Full variable name with suffix (lowercase)
            value: Value to set
        """
        # Split the variable name from the type suffix using utility function
        name, type_suffix = split_variable_name_and_suffix(full_name)

        # Create a fake token with line=-1 to indicate internal/system setting
        class FakeToken:
            def __init__(self):
                self.line = -1
                self.position = None

        fake_token = FakeToken()

        # Call set_variable for uniform handling
        self.set_variable(name, type_suffix, value, token=fake_token)

    def clear_variables(self):
        """Clear all variables."""
        self._variables.clear()

    def clear_arrays(self):
        """Clear all arrays."""
        self._arrays.clear()


    def update_variables(self, variables):
        """
        Bulk update variables.

        Args:
            variables: list of variable dicts (from get_all_variables())
                      Each dict contains: name, type_suffix, is_array, value/dimensions,
                      last_read, last_write
        """
        for var_info in variables:
            # Reconstruct full name
            full_name = var_info['name'] + var_info['type_suffix']

            if var_info['is_array']:
                # Restore array
                self._arrays[full_name] = {
                    'dims': var_info['dimensions'],
                    'data': [0] * self._calculate_array_size(var_info['dimensions'])
                }
            else:
                # Restore scalar variable
                self._variables[full_name] = {
                    'value': var_info['value'],
                    'last_read': var_info.get('last_read'),
                    'last_write': var_info.get('last_write')
                }

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

    def get_array_element(self, name, type_suffix, subscripts, def_type_map=None, token=None):
        """
        Get array element value, optionally tracking read access.

        Args:
            name: Array name
            type_suffix: Type suffix or None
            subscripts: List of subscript values
            def_type_map: Optional DEF type mapping
            token: Optional token object with line and position info for tracking.
                   If None, read access is not tracked (for debugger use).

        Returns:
            Array element value
        """
        # Resolve full array name
        full_name, _ = self._resolve_variable_name(name, type_suffix, def_type_map)

        # Auto-dimension array to (10) if not explicitly dimensioned (MBASIC behavior)
        if full_name not in self._arrays:
            # Determine number of dimensions from subscripts
            num_dims = len(subscripts)
            # Default dimension size is 10 for each dimension
            default_dims = [10] * num_dims
            self.dimension_array(name, type_suffix, default_dims, def_type_map)

        array_info = self._arrays[full_name]
        dims = array_info['dims']
        data = array_info['data']

        # Calculate flat index using global array_base
        index = self._calculate_array_index(subscripts, dims, self.array_base)

        # Bounds check
        if index < 0 or index >= len(data):
            raise RuntimeError(f"Array subscript out of range: {full_name}{subscripts}")

        # Track read access if token is provided
        if token is not None:
            # Create tracking key for this array element
            element_key = f"{full_name}[{','.join(map(str, subscripts))}]"

            # Initialize tracking dict if needed
            if not hasattr(self, '_array_element_tracking'):
                self._array_element_tracking = {}

            if element_key not in self._array_element_tracking:
                self._array_element_tracking[element_key] = {
                    'last_read': None,
                    'last_write': None
                }

            # Update read tracking
            self._array_element_tracking[element_key]['last_read'] = {
                'line': getattr(token, 'line', self.current_line.line_number if self.current_line else None),
                'position': getattr(token, 'position', None),
                'timestamp': time.perf_counter()
            }

        return data[index]

    def set_array_element(self, name, type_suffix, subscripts, value, def_type_map=None, token=None):
        """
        Set array element value, optionally tracking write access.

        Args:
            name: Array name
            type_suffix: Type suffix or None
            subscripts: List of subscript values
            value: Value to set
            def_type_map: Optional DEF type mapping
            token: Optional token object with line and position info for tracking.
                   If None, write access is not tracked.
        """
        # Resolve full array name
        full_name, _ = self._resolve_variable_name(name, type_suffix, def_type_map)

        # Auto-dimension array to (10) if not explicitly dimensioned (MBASIC behavior)
        if full_name not in self._arrays:
            # Determine number of dimensions from subscripts
            num_dims = len(subscripts)
            # Default dimension size is 10 for each dimension
            default_dims = [10] * num_dims
            self.dimension_array(name, type_suffix, default_dims, def_type_map)

        array_info = self._arrays[full_name]
        dims = array_info['dims']
        data = array_info['data']

        # Calculate flat index using global array_base
        index = self._calculate_array_index(subscripts, dims, self.array_base)

        if index < 0 or index >= len(data):
            raise RuntimeError(f"Array subscript out of range: {full_name}{subscripts}")

        data[index] = value

        # Track write access if token is provided
        if token is not None:
            # Create tracking key for this array element
            element_key = f"{full_name}[{','.join(map(str, subscripts))}]"

            # Initialize tracking dict if needed
            if not hasattr(self, '_array_element_tracking'):
                self._array_element_tracking = {}

            if element_key not in self._array_element_tracking:
                self._array_element_tracking[element_key] = {
                    'last_read': None,
                    'last_write': None
                }

            # Update write tracking
            self._array_element_tracking[element_key]['last_write'] = {
                'line': getattr(token, 'line', self.current_line.line_number if self.current_line else None),
                'position': getattr(token, 'position', None),
                'timestamp': time.perf_counter()
            }

    def get_array_element_for_debugger(self, name, type_suffix, subscripts, def_type_map=None):
        """
        Get array element value for debugger/inspector WITHOUT updating access tracking.

        This method is intended ONLY for debugger/inspector use to read array element
        values without affecting the access tracking. For normal program execution,
        use get_array_element() with a token.

        Args:
            name: Array name
            type_suffix: Type suffix or None
            subscripts: List of subscript values
            def_type_map: Optional DEF type mapping

        Returns:
            Array element value
        """
        # Simply call get_array_element without a token (no tracking)
        return self.get_array_element(name, type_suffix, subscripts, def_type_map, token=None)

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
            'data': [default_value] * total_size
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

    # ========================================================================
    # Debugging and Inspection Interface
    # ========================================================================

    def get_all_variables(self):
        """Export all variables with structured type information.

        Returns detailed information about each variable including:
        - Base name (without type suffix)
        - Type suffix character
        - For scalars: current value
        - For arrays: dimensions and base
        - Access tracking: last_read and last_write info

        Returns:
            list: List of dictionaries with variable information
                  Each dict contains:
                  - 'name': Base name (e.g., 'x', 'counter', 'msg')
                  - 'type_suffix': Type character ($, %, !, #)
                  - 'is_array': Boolean
                  - 'value': Current value (scalars only)
                  - 'dimensions': List of dimension sizes (arrays only)
                  - 'base': Array base 0 or 1 (arrays only)
                  - 'last_read': {'line': int, 'position': int, 'timestamp': float} or None
                  - 'last_write': {'line': int, 'position': int, 'timestamp': float} or None

        Example:
            [
                {'name': 'counter', 'type_suffix': '%', 'is_array': False, 'value': 42,
                 'last_read': {'line': 20, 'position': 5, 'timestamp': 1234.567},
                 'last_write': {'line': 10, 'position': 4, 'timestamp': 1234.500}},
                {'name': 'msg', 'type_suffix': '$', 'is_array': False, 'value': 'hello',
                 'last_read': None, 'last_write': {'line': 15, 'position': 2, 'timestamp': 1234.200}},
                {'name': 'matrix', 'type_suffix': '%', 'is_array': True,
                 'dimensions': [10, 5], 'base': 0, 'last_read': None, 'last_write': None}
            ]

        Note: line -1 in last_write indicates debugger/prompt set
        """
        result = []

        # Helper to parse full name into base name and suffix
        def parse_name(full_name):
            if not full_name:
                return full_name, '!'

            last_char = full_name[-1]
            if last_char in ('$', '%', '!', '#'):
                return full_name[:-1], last_char
            else:
                # No suffix - assume single precision
                return full_name, '!'

        # Process scalar variables
        for full_name, var_entry in self._variables.items():
            base_name, type_suffix = parse_name(full_name)

            var_info = {
                'name': base_name,
                'type_suffix': type_suffix,
                'is_array': False,
                'value': var_entry['value'],
                'last_read': var_entry['last_read'],
                'last_write': var_entry['last_write']
            }

            result.append(var_info)

        # Process arrays
        for full_name, array_data in self._arrays.items():
            base_name, type_suffix = parse_name(full_name)

            var_info = {
                'name': base_name,
                'type_suffix': type_suffix,
                'is_array': True,
                'dimensions': array_data['dims'],
                'base': self.array_base,  # Global OPTION BASE setting
                'last_read': None,  # Arrays don't track access yet
                'last_write': None
            }

            result.append(var_info)

        return result

    def get_gosub_stack(self):
        """Export GOSUB call stack.

        Returns a list of line numbers representing GOSUB return points,
        ordered from oldest to newest (bottom to top of stack).

        Returns:
            list: Line numbers where GOSUB was called
                 Example: [100, 500, 1000]  # Called GOSUB at lines 100, 500, 1000

        Note: The first element is the oldest GOSUB, the last is the most recent.
        """
        # Extract just the line numbers from the stack
        return [line_num for line_num, stmt_idx in self.gosub_stack]

    def get_for_loop_stack(self):
        """Export FOR loop stack in nesting order.

        Returns information about all active FOR loops, including the loop
        variable, current value, end value, step, and line number.

        Returns:
            list: List of dictionaries with FOR loop information in nesting order.
                 The first entry is the outermost loop (entered first),
                 and the last entry is the innermost loop (entered most recently).

                 Example: [
                     {'var': 'I', 'current': 5, 'end': 10, 'step': 1, 'line': 100},
                     {'var': 'J', 'current': 2, 'end': 5, 'step': 1, 'line': 150}
                 ]
                 In this example, I is the outer loop and J is the inner loop.

        Note: The order reflects nesting level based on execution order (when each
              FOR was entered), not source line order. This is correct for BASIC
              where GOTOs can cause FOR loops to be entered in any line order.
        """
        result = []
        for var_name, loop_info in self.for_loops.items():
            # Get current value of loop variable
            current_value = self.variables.get(var_name, 0)

            result.append({
                'var': var_name,
                'current': current_value,
                'end': loop_info.get('end', 0),
                'step': loop_info.get('step', 1),
                'line': loop_info.get('return_line', 0)
            })

        return result

    def get_while_loop_stack(self):
        """Export WHILE loop stack in nesting order.

        Returns information about all active WHILE loops, including the
        line number where the WHILE statement is located.

        Returns:
            list: List of dictionaries with WHILE loop information in nesting order.
                 The first entry is the outermost loop (entered first),
                 and the last entry is the innermost loop (entered most recently).

                 Example: [
                     {'line': 100},
                     {'line': 150}
                 ]
                 In this example, the WHILE at line 100 is the outer loop
                 and the WHILE at line 150 is the inner loop.

        Note: The order reflects nesting level based on execution order (when each
              WHILE was entered), not source line order. This is correct for BASIC
              where GOTOs can cause WHILE loops to be entered in any line order.
              The list maintains the stack order from bottom to top.
        """
        result = []
        for loop_info in self.while_loops:
            result.append({
                'line': loop_info.get('while_line', 0)
            })

        return result
