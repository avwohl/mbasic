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
        # Each variable is stored as: name_with_suffix -> {'value': val, 'last_read': {...}, 'last_write': {...}, 'original_case': str, 'case_variants': [...]}
        # Note: line -1 in last_write indicates debugger/prompt/internal set (not from program execution)
        self._variables = {}
        self._arrays = {}             # name_with_suffix -> {'dims': [...], 'data': [...]}

        # Case tracking for conflict detection (settings.variables.case_conflict)
        # Maps normalized name (lowercase) to list of all case variants seen: {'targetangle': [('TargetAngle', line, col), ('targetangle', line, col)]}
        self._variable_case_variants = {}

        self.common_vars = []         # List of variable names declared in COMMON (order matters!)
        self.array_base = 0           # Array index base (0 or 1, set by OPTION BASE)
        self.option_base_executed = False  # Track if OPTION BASE has been executed (can only execute once)

        # Execution control
        self.current_line = None      # Currently executing LineNode
        self.current_stmt_index = 0   # Index of current statement in line
        self.halted = False           # Program finished?
        self.next_line = None         # Set by GOTO/GOSUB for jump
        self.next_stmt_index = None   # Set by RETURN for precise return point

        # Unified execution stack - tracks all active control flow (GOSUB, FOR, WHILE) in nesting order
        # Each entry: {'type': 'GOSUB'|'FOR'|'WHILE', ...type-specific fields...}
        # This allows detection of improper nesting like GOSUB...FOR...RETURN...NEXT
        self.execution_stack = []
        # Quick lookup: var_name -> index in execution_stack (for FOR loops only)
        self.for_loop_vars = {}

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

    def _check_case_conflict(self, name, original_case, token, settings_manager=None):
        """
        Check for variable name case conflicts and handle according to settings.

        Args:
            name: Normalized lowercase name (e.g., 'targetangle')
            original_case: Original case from source (e.g., 'TargetAngle')
            token: Token with line and position info
            settings_manager: Optional SettingsManager for getting case_conflict setting

        Returns:
            str: The canonical case to use for this variable (might differ from original_case)

        Raises:
            RuntimeError: If case_conflict setting is 'error' and conflict detected
        """
        # Get the case conflict setting
        case_conflict_policy = "first_wins"  # Default
        if settings_manager:
            case_conflict_policy = settings_manager.get("variables.case_conflict", "first_wins")

        # Track this case variant
        if name not in self._variable_case_variants:
            self._variable_case_variants[name] = []

        variants = self._variable_case_variants[name]

        # Check if this exact case already exists
        for existing_case, existing_line, existing_col in variants:
            if existing_case == original_case:
                # Same case - no conflict
                return original_case

        # New case variant detected
        line_num = getattr(token, 'line', None)
        col_num = getattr(token, 'column', None)

        # If this is the first variant, just store it
        if not variants:
            variants.append((original_case, line_num, col_num))
            return original_case

        # Conflict detected! Handle according to policy
        if case_conflict_policy == "error":
            # Raise error showing all variants
            first_case, first_line, first_col = variants[0]
            error_msg = f"Variable name case conflict: '{first_case}' at line {first_line}"
            error_msg += f" vs '{original_case}' at line {line_num}"
            raise RuntimeError(error_msg)

        elif case_conflict_policy == "first_wins":
            # Use the first case seen (silent)
            first_case, _, _ = variants[0]
            # Still track this variant for inspection/debugging
            variants.append((original_case, line_num, col_num))
            return first_case

        elif case_conflict_policy == "prefer_upper":
            # Choose version with most uppercase letters
            all_cases = variants + [(original_case, line_num, col_num)]
            best_case = max(all_cases, key=lambda x: sum(1 for c in x[0] if c.isupper()))
            if (original_case, line_num, col_num) not in variants:
                variants.append((original_case, line_num, col_num))
            return best_case[0]

        elif case_conflict_policy == "prefer_lower":
            # Choose version with most lowercase letters
            all_cases = variants + [(original_case, line_num, col_num)]
            best_case = max(all_cases, key=lambda x: sum(1 for c in x[0] if c.islower()))
            if (original_case, line_num, col_num) not in variants:
                variants.append((original_case, line_num, col_num))
            return best_case[0]

        elif case_conflict_policy == "prefer_mixed":
            # Prefer mixed case (camelCase/PascalCase)
            # Mixed case = has both upper and lower
            all_cases = variants + [(original_case, line_num, col_num)]

            def mixed_score(case_str):
                has_upper = any(c.isupper() for c in case_str)
                has_lower = any(c.islower() for c in case_str)
                if has_upper and has_lower:
                    return 1  # Mixed case
                return 0  # All upper or all lower

            best_case = max(all_cases, key=lambda x: mixed_score(x[0]))
            if (original_case, line_num, col_num) not in variants:
                variants.append((original_case, line_num, col_num))
            return best_case[0]

        else:
            # Unknown policy - default to first_wins
            first_case, _, _ = variants[0]
            variants.append((original_case, line_num, col_num))
            return first_case

    def get_variable(self, name, type_suffix=None, def_type_map=None, token=None, original_case=None, settings_manager=None):
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

        # Check for case conflicts and get canonical case
        if original_case is None:
            original_case = name  # Fallback if not provided
        canonical_case = self._check_case_conflict(name, original_case, token, settings_manager)

        # Initialize variable entry if needed
        if full_name not in self._variables:
            # Create with default value
            default_value = "" if resolved_suffix == '$' else 0
            self._variables[full_name] = {
                'value': default_value,
                'last_read': None,
                'last_write': None,
                'original_case': canonical_case  # Store canonical case
            }
        else:
            # Always update original_case to canonical (for prefer_upper/prefer_lower/prefer_mixed policies)
            self._variables[full_name]['original_case'] = canonical_case

        # Track read access
        self._variables[full_name]['last_read'] = {
            'line': getattr(token, 'line', self.current_line.line_number if self.current_line else None),
            'position': getattr(token, 'position', None),
            'timestamp': time.perf_counter()  # High precision timestamp for debugging
        }

        # Return value
        return self._variables[full_name]['value']

    def set_variable(self, name, type_suffix, value, def_type_map=None, token=None, debugger_set=False, limits=None, original_case=None, settings_manager=None):
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
            limits: Optional ResourceLimits object for tracking
            original_case: Original case from source (for case preservation)
            settings_manager: Optional SettingsManager for case conflict handling

        Raises:
            ValueError: If token is None and debugger_set is False
        """
        if token is None and not debugger_set:
            raise ValueError("set_variable() requires token parameter. Use debugger_set=True for debugger writes.")

        # Resolve full variable name
        full_name, resolved_suffix = self._resolve_variable_name(name, type_suffix, def_type_map)

        # Check for case conflicts and get canonical case (skip for debugger sets)
        if not debugger_set and token is not None:
            if original_case is None:
                original_case = name  # Fallback if not provided
            canonical_case = self._check_case_conflict(name, original_case, token, settings_manager)
        else:
            canonical_case = original_case or name

        # Enforce 255 byte string limit (MBASIC 5.21 compatibility)
        if resolved_suffix == '$' and isinstance(value, str) and len(value) > 255:
            raise RuntimeError("String too long")

        # Check string length limit if limits provided and it's a string
        if limits and resolved_suffix == '$' and isinstance(value, str):
            limits.check_string_length(value)

        # Track variable memory if limits provided
        if limits and not debugger_set:
            from ast_nodes import TypeInfo
            var_type = TypeInfo.from_suffix(resolved_suffix)
            limits.allocate_variable(full_name, value, var_type)

        # Initialize variable entry if needed
        if full_name not in self._variables:
            self._variables[full_name] = {
                'value': None,
                'last_read': None,
                'last_write': None,
                'original_case': canonical_case  # Store canonical case
            }
        else:
            # Always update original_case to canonical (for prefer_upper/prefer_lower/prefer_mixed policies)
            self._variables[full_name]['original_case'] = canonical_case

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
            # Track at array level (for variables window display)
            tracking_info = {
                'line': getattr(token, 'line', self.current_line.line_number if self.current_line else None),
                'position': getattr(token, 'position', None),
                'timestamp': time.perf_counter()
            }
            array_info['last_read_subscripts'] = list(subscripts)  # Store copy of subscripts
            array_info['last_read'] = tracking_info

            # Create tracking key for this array element (for per-element tracking)
            element_key = f"{full_name}[{','.join(map(str, subscripts))}]"

            # Initialize tracking dict if needed
            if not hasattr(self, '_array_element_tracking'):
                self._array_element_tracking = {}

            if element_key not in self._array_element_tracking:
                self._array_element_tracking[element_key] = {
                    'last_read': None,
                    'last_write': None
                }

            # Update per-element read tracking
            self._array_element_tracking[element_key]['last_read'] = tracking_info

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
            # Track at array level (for variables window display)
            tracking_info = {
                'line': getattr(token, 'line', self.current_line.line_number if self.current_line else None),
                'position': getattr(token, 'position', None),
                'timestamp': time.perf_counter()
            }
            array_info['last_write_subscripts'] = list(subscripts)  # Store copy of subscripts
            array_info['last_write'] = tracking_info

            # Create tracking key for this array element (for per-element tracking)
            element_key = f"{full_name}[{','.join(map(str, subscripts))}]"

            # Initialize tracking dict if needed
            if not hasattr(self, '_array_element_tracking'):
                self._array_element_tracking = {}

            if element_key not in self._array_element_tracking:
                self._array_element_tracking[element_key] = {
                    'last_read': None,
                    'last_write': None
                }

            # Update per-element write tracking
            self._array_element_tracking[element_key]['last_write'] = tracking_info

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

    def dimension_array(self, name, type_suffix, dimensions, def_type_map=None, token=None):
        """
        Create/dimension an array.

        Args:
            name: Array name
            type_suffix: Type suffix or None
            dimensions: List of dimension sizes
            def_type_map: Optional DEF type mapping
            token: Optional token for tracking DIM statement location
        """
        import time

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

        # Track DIM as a write operation
        tracking_info = None
        if token is not None:
            tracking_info = {
                'line': getattr(token, 'line', self.current_line.line_number if self.current_line else None),
                'position': getattr(token, 'position', None),
                'timestamp': time.perf_counter()
            }

        # Create array with access tracking
        self._arrays[full_name] = {
            'dims': dimensions,
            'data': [default_value] * total_size,
            'last_read_subscripts': None,  # Last accessed subscripts for read
            'last_write_subscripts': None,  # Last accessed subscripts for write
            'last_read': tracking_info,  # DIM counts as both read and write
            'last_write': tracking_info
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
        """Push GOSUB return address onto unified execution stack"""
        gosub_entry = {
            'type': 'GOSUB',
            'return_line': return_line,
            'return_stmt': return_stmt_index
        }
        self.execution_stack.append(gosub_entry)

    def pop_gosub(self):
        """
        Pop GOSUB return address from unified execution stack.

        Returns:
            (return_line, return_stmt_index) tuple

        Raises:
            RuntimeError: If stack is empty or top is not a GOSUB
        """
        if not self.execution_stack:
            raise RuntimeError("RETURN without GOSUB")

        # Verify the top of stack is a GOSUB
        if self.execution_stack[-1]['type'] != 'GOSUB':
            # Error: trying to RETURN but top of stack is a loop
            entry_type = self.execution_stack[-1]['type']
            if entry_type == 'FOR':
                var_name = self.execution_stack[-1]['var']
                raise RuntimeError(f"RETURN without GOSUB - found FOR {var_name} loop instead")
            elif entry_type == 'WHILE':
                raise RuntimeError("RETURN without GOSUB - found WHILE loop instead")
            raise RuntimeError(f"RETURN without GOSUB - improper nesting")

        entry = self.execution_stack.pop()
        return (entry['return_line'], entry['return_stmt'])

    def push_for_loop(self, var_name, end_value, step_value, return_line, return_stmt_index):
        """Register a FOR loop on the unified execution stack"""
        from src.debug_logger import debug_log

        # Verbose debug logging (only if MBASIC_DEBUG_LEVEL=2)
        debug_log(
            f"push_for_loop({var_name}) at line {return_line}",
            context={'stack_size_before': len(self.execution_stack)},
            level=2
        )

        # Check if this variable already has an active FOR loop
        # This prevents nested FOR loops with the same variable (e.g., FOR I=1 TO 10 / FOR I=1 TO 5)
        if var_name in self.for_loop_vars:
            debug_log(
                f"ERROR: {var_name} already on stack at index {self.for_loop_vars[var_name]}!",
                level=1  # Always log errors
            )
            raise RuntimeError(f"FOR loop variable {var_name} already active - nested FOR loops with same variable not allowed")

        loop_entry = {
            'type': 'FOR',
            'var': var_name,
            'end': end_value,
            'step': step_value,
            'return_line': return_line,
            'return_stmt': return_stmt_index
        }
        self.execution_stack.append(loop_entry)
        # Track index for quick lookup by variable name
        self.for_loop_vars[var_name] = len(self.execution_stack) - 1

        debug_log(
            f"push_for_loop({var_name}) complete",
            context={'stack_size_after': len(self.execution_stack)},
            level=2
        )

    def pop_for_loop(self, var_name):
        """Remove a FOR loop - verifies it's on top of stack"""
        if var_name not in self.for_loop_vars:
            return  # No loop for this variable

        # Get the index of this FOR loop
        loop_index = self.for_loop_vars[var_name]

        # Verify this FOR loop is on top of the stack
        if loop_index != len(self.execution_stack) - 1:
            # Error: trying to exit a FOR loop that isn't the innermost control structure
            # This means there's improper nesting (e.g., FOR I / GOSUB / NEXT I / RETURN)
            raise RuntimeError(f"NEXT {var_name} without matching FOR - improper nesting")

        # Remove from stack
        self.execution_stack.pop()
        del self.for_loop_vars[var_name]

    def get_for_loop(self, var_name):
        """Get FOR loop info or None"""
        if var_name not in self.for_loop_vars:
            return None
        loop_index = self.for_loop_vars[var_name]
        return self.execution_stack[loop_index]

    def push_while_loop(self, while_line, while_stmt_index):
        """Register a WHILE loop on the unified execution stack"""
        loop_entry = {
            'type': 'WHILE',
            'while_line': while_line,
            'while_stmt': while_stmt_index
        }
        self.execution_stack.append(loop_entry)

    def pop_while_loop(self):
        """Remove most recent WHILE loop - verifies it's actually a WHILE"""
        if not self.execution_stack:
            return None

        # Verify the top of stack is a WHILE loop
        if self.execution_stack[-1]['type'] != 'WHILE':
            # Error: trying to WEND but top of stack is not a WHILE
            entry_type = self.execution_stack[-1]['type']
            if entry_type == 'FOR':
                var_name = self.execution_stack[-1]['var']
                raise RuntimeError(f"WEND without WHILE - found FOR {var_name} loop instead")
            elif entry_type == 'GOSUB':
                raise RuntimeError("WEND without WHILE - found GOSUB instead")
            raise RuntimeError("WEND without WHILE - improper nesting")

        return self.execution_stack.pop()

    def peek_while_loop(self):
        """Get most recent WHILE loop info without removing it"""
        # Find the most recent WHILE loop on the stack
        for i in range(len(self.execution_stack) - 1, -1, -1):
            if self.execution_stack[i]['type'] == 'WHILE':
                return self.execution_stack[i]
        return None

    def validate_stack(self):
        """Validate execution stack after program edits.

        Checks that all return addresses in the stack still point to valid lines.
        Returns a tuple: (valid, removed_entries, messages)
        - valid: True if stack is valid (possibly after removals)
        - removed_entries: List of stack entries that were removed
        - messages: List of warning messages for the user

        This is called when user edits code at a breakpoint and then continues.
        We validate that:
        - FOR loops: return_line still exists
        - GOSUB: return_line still exists
        - WHILE loops: while_line still exists

        Invalid entries are removed from the stack.
        """
        removed_entries = []
        messages = []

        # Validate each entry from bottom to top
        i = 0
        while i < len(self.execution_stack):
            entry = self.execution_stack[i]
            entry_type = entry['type']
            should_remove = False

            if entry_type == 'FOR':
                var_name = entry['var']
                return_line = entry['return_line']

                # Check if return line still exists
                if return_line not in self.line_table:
                    should_remove = True
                    messages.append(f"FOR {var_name} loop removed - line {return_line} no longer exists")

            elif entry_type == 'GOSUB':
                return_line = entry['return_line']

                # Check if return line still exists
                if return_line not in self.line_table:
                    should_remove = True
                    messages.append(f"GOSUB removed - return line {return_line} no longer exists")

            elif entry_type == 'WHILE':
                while_line = entry.get('while_line')

                # Check if while line still exists
                if while_line and while_line not in self.line_table:
                    should_remove = True
                    messages.append(f"WHILE loop removed - line {while_line} no longer exists")

            if should_remove:
                removed_entry = self.execution_stack.pop(i)
                removed_entries.append(removed_entry)

                # Clean up for_loop_vars tracking if it's a FOR loop
                if entry_type == 'FOR':
                    var_name = removed_entry['var']
                    if var_name in self.for_loop_vars:
                        del self.for_loop_vars[var_name]

                # Don't increment i - we removed an entry so next entry is now at position i
            else:
                i += 1

        # Stack is valid if we processed everything (even if we removed some entries)
        return (True, removed_entries, messages)

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
                'last_read': array_data.get('last_read'),  # Tracking info for array access
                'last_write': array_data.get('last_write'),
                'last_read_subscripts': array_data.get('last_read_subscripts'),  # Last accessed indexes
                'last_write_subscripts': array_data.get('last_write_subscripts')
            }

            # Get value of last accessed cell (prefer write over read)
            last_subscripts = array_data.get('last_write_subscripts') or array_data.get('last_read_subscripts')
            if last_subscripts:
                try:
                    # Use debugger method to avoid updating tracking
                    last_value = self.get_array_element_for_debugger(base_name, type_suffix, last_subscripts)
                    var_info['last_accessed_value'] = last_value
                    var_info['last_accessed_subscripts'] = last_subscripts
                except:
                    var_info['last_accessed_value'] = None
                    var_info['last_accessed_subscripts'] = None
            else:
                var_info['last_accessed_value'] = None
                var_info['last_accessed_subscripts'] = None

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
        # Extract just the return line numbers from GOSUB entries in the execution stack
        return [entry['return_line'] for entry in self.execution_stack if entry['type'] == 'GOSUB']

    def get_execution_stack(self):
        """Export unified execution stack (GOSUB, FOR, WHILE) in nesting order.

        Returns information about all active control flow structures,
        interleaved in the order they were entered. This allows detection of
        improper nesting like FOR...GOSUB...NEXT...RETURN.

        Returns:
            list: List of dictionaries with control flow information in nesting order.
                 The first entry is the outermost (entered first),
                 and the last entry is the innermost (entered most recently).

                 For GOSUB calls:
                 {
                     'type': 'GOSUB',
                     'from_line': 50,
                     'return_line': 60
                 }

                 For FOR loops:
                 {
                     'type': 'FOR',
                     'var': 'I',
                     'current': 5,
                     'end': 10,
                     'step': 1,
                     'line': 100
                 }

                 For WHILE loops:
                 {
                     'type': 'WHILE',
                     'line': 150
                 }

                 Example with nested control flow:
                 [
                     {'type': 'FOR', 'var': 'I', 'current': 1, 'end': 10, 'step': 1, 'line': 100},
                     {'type': 'GOSUB', 'from_line': 120, 'return_line': 130},
                     {'type': 'WHILE', 'line': 500}
                 ]

                 This shows: FOR I at 100, then GOSUB from 120, then WHILE at 500 (innermost).
                 Proper unwinding would be: WEND, RETURN, NEXT I.

        Note: The order reflects nesting level based on execution order (when each
              structure was entered), not source line order.
        """
        result = []
        for entry in self.execution_stack:
            if entry['type'] == 'GOSUB':
                result.append({
                    'type': 'GOSUB',
                    'from_line': entry.get('return_line', 0),  # Line to return to
                    'return_line': entry.get('return_line', 0)
                })
            elif entry['type'] == 'FOR':
                # Get current value of loop variable
                var_name = entry['var']
                # Parse variable name to get base name and type suffix
                base_name, type_suffix = split_variable_name_and_suffix(var_name)
                current_value = self.get_variable_for_debugger(base_name, type_suffix)

                result.append({
                    'type': 'FOR',
                    'var': var_name,
                    'current': current_value,
                    'end': entry.get('end', 0),
                    'step': entry.get('step', 1),
                    'line': entry.get('return_line', 0)
                })
            elif entry['type'] == 'WHILE':
                result.append({
                    'type': 'WHILE',
                    'line': entry.get('while_line', 0)
                })

        return result

    # Backward compatibility alias
    def get_loop_stack(self):
        """Deprecated: Use get_execution_stack() instead."""
        return self.get_execution_stack()
