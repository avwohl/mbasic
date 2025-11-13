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
- Program counter (PC) based execution
"""

import time
from src.ast_nodes import DataStatementNode, DefFnStatementNode
from src.pc import PC, StatementTable


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
        # Store input for setup() - will be processed into statement_table
        # Can be either ProgramNode AST or dict {line_num: LineNode}
        self._ast_or_line_table = ast_or_line_table

        # Variable storage (PRIVATE - use get_variable/set_variable methods)
        # Each variable is stored as: name_with_suffix -> {'value': val, 'last_read': {...}, 'last_write': {...}, 'original_case': str}
        # Note: The 'original_case' field stores the canonical case for display (determined by case_conflict policy).
        #       Despite its misleading name, this field contains the policy-resolved canonical case variant,
        #       not the original case as first typed. See _check_case_conflict() for resolution logic.
        # Note: line -1 in last_write indicates non-program execution sources:
        #       1. System/internal variables (ERR%, ERL%) via set_variable_raw() with FakeToken(line=-1)
        #       2. Debugger/interactive prompt via set_variable() with debugger_set=True (always uses line=-1)
        #       Both use line=-1, making them indistinguishable from each other in last_write alone.
        #       However, line=-1 distinguishes these special sources from normal program execution (line >= 0).
        self._variables = {}
        self._arrays = {}             # name_with_suffix -> {'dims': [...], 'data': [...]}

        # Case tracking for conflict detection (settings.case_conflict)
        # Stored separately from variable entries for efficient tracking:
        # Maps normalized name (lowercase) to list of all case variants seen: {'targetangle': [('TargetAngle', line, col), ('targetangle', line, col)]}
        self._variable_case_variants = {}

        # Array element tracking for per-element read/write timestamps
        self._array_element_tracking = {}

        self.common_vars = []         # List of variable names declared in COMMON (order matters!)
        self.array_base = 0           # Array index base (0 or 1, set by OPTION BASE)
        self.option_base_executed = False  # Track if OPTION BASE has been executed (can only execute once)

        # Execution control - NEW PC-based design
        self.pc = PC.halted()      # Current program counter (line, stmt_offset)
        self.npc = None               # Next program counter (set by GOTO/GOSUB/etc., None = sequential)
        self.statement_table = StatementTable()  # Ordered collection of statements indexed by PC

        # Unified execution stack - tracks GOSUB and WHILE only (FOR loops use variable-indexed approach)
        # Each entry: {'type': 'GOSUB'|'WHILE', ...type-specific fields...}
        self.execution_stack = []

        # FOR loop state storage - maps variable name to loop state
        # var_name -> {'pc': PC object, 'end': end_value, 'step': step_value}
        self.for_loop_states = {}

        # Line text mapping (for error messages)
        self.line_text_map = line_text_map or {}  # line_number -> source text (for error messages)

        # DATA statements
        self.data_items = []          # [value, value, ...]
        self.data_pointer = 0         # Current READ position
        self.data_line_map = {}       # {data_index: line_number} - tracks which line each data item came from

        # User-defined functions
        self.user_functions = {}      # fn_name -> DefFnStatementNode

        # Note: Type defaults (DEFINT, DEFSNG, etc.) are collected by parser's def_type_map
        # at parse time (Parser class), but runtime also uses def_type_map via
        # _resolve_variable_name() to determine variable types when no explicit suffix is present

        # File I/O
        self.files = {}               # file_number -> file_handle
        self.field_buffers = {}       # file_number -> buffer_dict

        # Error handling registration (ON ERROR GOTO/GOSUB)
        self.error_handler = None     # Line number for registered error handler
        self.error_handler_is_gosub = False  # True if ON ERROR GOSUB, False if ON ERROR GOTO
        # Note: Actual error state (occurred/active) is tracked in state.error_info, not here
        # Runtime only stores the registered handler location, not whether an error occurred
        # Error PC and details are stored in ErrorInfo (interpreter.py state)
        # ERL%, ERS%, and ERR% system variables are set from ErrorInfo

        # Random number seed
        self.rnd_last = 0.5

        # Breakpoints - persist across runs (not cleared by RUN/CLEAR)
        self.breakpoints = set()          # Set of PC objects for breakpoints

        # Break handling (Ctrl+C)
        self.break_requested = False      # True when Ctrl+C pressed during execution

        # Trace flag (TRON/TROFF)
        self.trace_on = False             # True if execution trace is enabled
        self.trace_detail = 'line'        # 'line' or 'statement' - controls trace output format

        # Initialize system variables ERR% and ERL% to 0
        # These are integer type variables set by error handling code
        self.set_variable_raw('err%', 0)
        self.set_variable_raw('erl%', 0)

    def setup(self):
        """
        Initialize runtime by building lookup tables.
        Call this once before execution starts.
        """
        # Determine which lines to process from input
        if isinstance(self._ast_or_line_table, dict):
            # New style: dict {line_num: LineNode} already provided
            lines_to_process = self._ast_or_line_table.values()
        else:
            # Old style: ProgramNode AST - extract lines
            lines_to_process = self._ast_or_line_table.lines

        # Build statement table and extract DATA values and DEF FN definitions
        for line in lines_to_process:
            for stmt_offset, stmt in enumerate(line.statements):
                # Add to statement table with PC
                pc = PC(line.line_number, stmt_offset)
                self.statement_table.add(pc, stmt)

                # Extract DATA and DEF FN
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

        # Initialize PC to first statement
        self.pc = self.statement_table.first_pc()

        return self

    def is_paused_at_statement(self):
        """Check if halted at a valid statement (not past end).

        Returns:
            bool: True if halted at a statement (paused/breakpoint), False if past end or not halted
        """
        if self.pc.is_running():
            return False

        pc = self.pc
        if pc.line is None:
            return False  # Past end of program

        # PC.__eq__ only compares position (line, statement), not state (stop_reason, error)
        # so this lookup works correctly regardless of whether PC is running or stopped
        stmt = self.statement_table.get(pc)
        return stmt is not None  # True if at a valid statement

    @staticmethod
    def _resolve_variable_name(name, type_suffix, def_type_map=None):
        """
        Resolve the full variable name with type suffix.

        This is the standard method for determining the storage key for a variable,
        applying BASIC type resolution rules (explicit suffix > DEF type > default).
        For special cases like system variables (ERR%, ERL%), see set_variable_raw().

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
            case_conflict_policy = settings_manager.get("case_conflict", "first_wins")

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
            token: REQUIRED - A token object must be provided (ValueError raised if None).
                   The token enables source location tracking for this variable access.

                   Token attributes have fallback behavior:
                   - token.line: Used for tracking if present, otherwise falls back to self.pc.line_num
                   - token.position: Used for tracking if present, otherwise falls back to None

                   Why token object is required: Even with attribute fallbacks, the token object
                   itself is mandatory to distinguish intentional program execution (which must
                   provide a token) from debugging/inspection (which should use get_variable_for_debugger()).
                   This design prevents accidental omission of tracking during normal execution.

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
                'original_case': canonical_case  # Canonical case for display (field name is misleading, see module header)
            }
        else:
            # Always update to canonical case (for prefer_upper/prefer_lower/prefer_mixed policies)
            # Note: The field name is misleading - it stores canonical case not original (see module header)
            self._variables[full_name]['original_case'] = canonical_case

        # Track read access
        self._variables[full_name]['last_read'] = {
            'line': getattr(token, 'line', self.pc.line_num if self.pc and not self.pc.halted() else None),
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
            debugger_set: True if this set is from debugger/interactive prompt, not program execution
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
        # Note: If not debugger_set, token is guaranteed to be non-None by the ValueError check above.
        # Debugger sets skip case conflict checking because they don't have source location context
        # and are used for internal/system variables that don't need case consistency enforcement.
        if not debugger_set:
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
            from src.ast_nodes import TypeInfo
            var_type = TypeInfo.from_suffix(resolved_suffix)
            limits.allocate_variable(full_name, value, var_type)

        # Initialize variable entry if needed
        if full_name not in self._variables:
            self._variables[full_name] = {
                'value': None,
                'last_read': None,
                'last_write': None,
                'original_case': canonical_case  # Canonical case for display (field name is misleading, see module header)
            }
        else:
            # Always update to canonical case (for prefer_upper/prefer_lower/prefer_mixed policies)
            # Note: The field name is misleading - it stores canonical case not original (see module header)
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
            # Non-debugger path: normal program execution (token.line >= 0) OR internal/system set (token.line = -1)
            # Both use this branch; line value from token distinguishes them
            self._variables[full_name]['last_write'] = {
                'line': getattr(token, 'line', self.pc.line_num if self.pc and not self.pc.halted() else None),
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

        Convenience wrapper for system/internal variable updates (ERR%, ERL%, etc.).
        Internally calls set_variable() with a FakeToken(line=-1) to mark this as
        a system/internal set (not from program execution).

        The line=-1 marker in last_write indicates system/internal variables.
        However, debugger sets also use line=-1 (via debugger_set=True),
        making them indistinguishable from system variables in last_write alone.
        Both are distinguished from normal program execution (line >= 0).

        For normal program variables, prefer set_variable() which accepts separate
        name and type_suffix parameters.

        Args:
            full_name: Full variable name with suffix (lowercase)
            value: Value to set
        """
        # Split the variable name from the type suffix using utility function
        name, type_suffix = split_variable_name_and_suffix(full_name)

        # Create a fake token with line=-1 to indicate internal/system setting
        # (see _variables comment in __init__ for details on line=-1 usage)
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

    def bind_for_loop(self, var_name, pc, end_value, step_value):
        """
        Bind a variable to a FOR loop.

        Args:
            var_name: Variable name with suffix (lowercase)
            pc: PC object pointing to the FOR statement
            end_value: Loop end value (evaluated once at FOR time)
            step_value: Loop step value (evaluated once at FOR time)
        """
        self.for_loop_states[var_name] = {
            'pc': pc,
            'end': end_value,
            'step': step_value
        }

    def get_for_loop_state(self, var_name):
        """
        Get the FOR loop state for a variable.

        Args:
            var_name: Variable name with suffix (lowercase)

        Returns:
            dict with keys 'pc', 'end', 'step' or None if not bound to a loop
        """
        return self.for_loop_states.get(var_name)

    def unbind_for_loop(self, var_name):
        """
        Unbind a variable from its FOR loop.

        Args:
            var_name: Variable name with suffix (lowercase)
        """
        if var_name in self.for_loop_states:
            del self.for_loop_states[var_name]


    def update_variables(self, variables):
        """
        Bulk update variables.

        Args:
            variables: list of variable dicts (from get_all_variables())
                      Each dict contains: name, type_suffix, is_array, value/dimensions,
                      last_read, last_write, original_case (for case preservation)
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
                # Restore scalar variable with original_case preservation
                self._variables[full_name] = {
                    'value': var_info['value'],
                    'last_read': var_info.get('last_read'),
                    'last_write': var_info.get('last_write'),
                    'original_case': var_info.get('original_case', var_info['name'])  # Preserve canonical case
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
        Get array element value, tracking read access if token is provided.

        Auto-dimensioning: If the array has not been explicitly dimensioned via DIM,
        it will be automatically dimensioned to (10, 10, ...) with one dimension
        per subscript. This matches MBASIC-80 5.21 behavior.

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
                'line': getattr(token, 'line', self.pc.line_num if self.pc and not self.pc.halted() else None),
                'position': getattr(token, 'position', None),
                'timestamp': time.perf_counter()
            }
            array_info['last_read_subscripts'] = list(subscripts)  # Store copy of subscripts
            array_info['last_read'] = tracking_info

            # Create tracking key for this array element (for per-element tracking)
            element_key = f"{full_name}[{','.join(map(str, subscripts))}]"

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

        Auto-dimensioning: If the array has not been explicitly dimensioned via DIM,
        it will be automatically dimensioned to (10, 10, ...) with one dimension
        per subscript. This matches MBASIC-80 5.21 behavior.

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
                'line': getattr(token, 'line', self.pc.line_num if self.pc and not self.pc.halted() else None),
                'position': getattr(token, 'position', None),
                'timestamp': time.perf_counter()
            }
            array_info['last_write_subscripts'] = list(subscripts)  # Store copy of subscripts
            array_info['last_write'] = tracking_info

            # Create tracking key for this array element (for per-element tracking)
            element_key = f"{full_name}[{','.join(map(str, subscripts))}]"

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
                'line': getattr(token, 'line', self.pc.line_num if self.pc and not self.pc.halted() else None),
                'position': getattr(token, 'position', None),
                'timestamp': time.perf_counter()
            }

        # Create array with access tracking
        self._arrays[full_name] = {
            'dims': dimensions,
            'data': [default_value] * total_size,
            'last_read_subscripts': None,  # Last accessed subscripts for read
            'last_write_subscripts': None,  # Last accessed subscripts for write
            'last_read': tracking_info,  # Track DIM location (initialization sets read timestamp for debugger)
            'last_write': tracking_info  # Track DIM location (array initialization counts as write)
        }
        # Note: DIM is tracked as both read and write to provide consistent debugger display.
        # While DIM is technically allocation/initialization (write-only operation), setting
        # last_read to the DIM location ensures that debuggers/inspectors can show "Last accessed"
        # information even for arrays that have never been explicitly read. Without this, an
        # unaccessed array would show no last_read info, which could be confusing. The DIM location
        # provides useful context about where the array was created.

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
        """Register a FOR loop by binding the variable to loop state.

        Variable-indexed approach: Each variable is bound to one FOR loop at a time.
        This allows jumping out of loops and reusing variables (Super Star Trek pattern).

        When NEXT executes, it looks up the loop state and does increment logic.
        """
        from src.debug_logger import debug_log
        from src.pc import PC

        # Verbose debug logging (only if MBASIC_DEBUG_LEVEL=2)
        debug_log(
            f"push_for_loop({var_name}) at line {return_line}",
            level=2
        )

        # Create PC pointing to the FOR statement
        for_pc = PC.running_at(return_line, return_stmt_index)

        # Bind variable to this FOR loop
        # If variable already bound (jumped out of previous loop), this just overwrites it
        self.bind_for_loop(var_name, for_pc, end_value, step_value)

        debug_log(
            f"push_for_loop({var_name}) complete - bound to PC({return_line},{return_stmt_index})",
            level=2
        )

    def pop_for_loop(self, var_name):
        """Remove a FOR loop binding from the variable."""
        self.unbind_for_loop(var_name)

    def get_for_loop(self, var_name):
        """Get FOR loop info for a variable.

        Returns:
            dict with keys: 'end', 'step', 'return_line', 'return_stmt'
            or None if variable not bound to a FOR loop
        """
        loop_state = self.get_for_loop_state(var_name)
        if loop_state is None:
            return None

        # Return loop info in the format expected by interpreter
        return {
            'end': loop_state['end'],
            'step': loop_state['step'],
            'return_line': loop_state['pc'].line,
            'return_stmt': loop_state['pc'].statement
        }

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
        - FOR loops: FOR line still exists (tracked separately in for_loop_states)
        - GOSUB: return_line still exists
        - WHILE loops: while_line still exists

        Invalid entries are removed from the stack.
        """
        removed_entries = []
        messages = []

        # Validate execution stack (GOSUB and WHILE only)
        i = 0
        while i < len(self.execution_stack):
            entry = self.execution_stack[i]
            entry_type = entry['type']
            should_remove = False

            if entry_type == 'GOSUB':
                return_line = entry['return_line']

                # Check if return line still exists
                if not self.statement_table.line_exists(return_line):
                    should_remove = True
                    messages.append(f"GOSUB removed - return line {return_line} no longer exists")

            elif entry_type == 'WHILE':
                while_line = entry.get('while_line')

                # Check if while line still exists
                if while_line and not self.statement_table.line_exists(while_line):
                    should_remove = True
                    messages.append(f"WHILE loop removed - line {while_line} no longer exists")

            if should_remove:
                removed_entry = self.execution_stack.pop(i)
                removed_entries.append(removed_entry)
                # Don't increment i - we removed an entry so next entry is now at position i
            else:
                i += 1

        # Validate FOR loop states (tracked separately)
        for var_name in list(self.for_loop_states.keys()):
            loop_state = self.for_loop_states[var_name]
            for_line = loop_state['pc'].line

            # Check if FOR line still exists
            if not self.statement_table.line_exists(for_line):
                del self.for_loop_states[var_name]
                messages.append(f"FOR {var_name} loop removed - line {for_line} no longer exists")
                removed_entries.append({'type': 'FOR', 'var': var_name, 'return_line': for_line})

        # Stack is valid if we processed everything (even if we removed some entries)
        return (True, removed_entries, messages)

    def has_error_handler(self):
        """
        Check if an error handler is installed (ON ERROR GOTO).

        Returns:
            True if error_handler is set, False otherwise
        """
        return self.error_handler is not None

    def has_active_loop(self, var_name=None):
        """
        Check if a FOR loop is active.

        Args:
            var_name: Optional loop variable name to check for specific loop

        Returns:
            True if loop exists, False otherwise
        """
        if var_name is None:
            # Check if any FOR loop is active
            return len(self.for_loop_states) > 0
        else:
            # Check for specific loop variable
            return var_name in self.for_loop_states

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
                  - 'original_case': Canonical case for display (e.g., 'TargetAngle', 'Counter')
                  - 'last_read': {'line': int, 'position': int, 'timestamp': float} or None
                  - 'last_write': {'line': int, 'position': int, 'timestamp': float} or None

        Example:
            [
                {'name': 'counter', 'type_suffix': '%', 'is_array': False, 'value': 42,
                 'original_case': 'Counter',
                 'last_read': {'line': 20, 'position': 5, 'timestamp': 1234.567},
                 'last_write': {'line': 10, 'position': 4, 'timestamp': 1234.500}},
                {'name': 'msg', 'type_suffix': '$', 'is_array': False, 'value': 'hello',
                 'original_case': 'msg',
                 'last_read': None, 'last_write': {'line': 15, 'position': 2, 'timestamp': 1234.200}},
                {'name': 'matrix', 'type_suffix': '%', 'is_array': True,
                 'dimensions': [10, 5], 'base': 0, 'original_case': 'Matrix',
                 'last_read': None, 'last_write': None}
            ]

        Note: line -1 in last_write indicates system/internal set (not from program execution)
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
                # No explicit suffix - default to single precision (!)
                # Note: In normal operation, all names in _variables have resolved type suffixes
                # from _resolve_variable_name() which applies DEF type rules. This fallback
                # is defensive programming for robustness - it should not occur in practice,
                # but protects against potential edge cases in legacy code or future changes.
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
                'last_write': var_entry['last_write'],
                'original_case': var_entry.get('original_case', base_name)  # Include canonical case for display
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
                'original_case': array_data.get('original_case', base_name),  # Include canonical case for display
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
        """Export GOSUB call stack with statement-level precision.

        Returns a list of (line_number, stmt_offset) tuples representing GOSUB return points,
        ordered from oldest to newest (bottom to top of stack).

        Returns:
            list: Tuples of (line_number, stmt_offset) where GOSUB was called
                 Example: [(100, 0), (500, 2), (1000, 1)]
                 This represents GOSUB called from:
                   - line 100, statement offset 0 (1st statement)
                   - line 500, statement offset 2 (3rd statement)
                   - line 1000, statement offset 1 (2nd statement)

                 Note: stmt_offset uses 0-based indexing (offset 0 = 1st statement, offset 1 = 2nd statement, etc.)

        Note: The first element is the oldest GOSUB, the last is the most recent.
        """
        # Extract return line and statement offset from GOSUB entries in the execution stack
        return [(entry['return_line'], entry['return_stmt'])
                for entry in self.execution_stack if entry['type'] == 'GOSUB']

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
                     'from_line': 60,      # Redundant with return_line (kept for backward compatibility)
                     'return_line': 60,    # Line to return to after RETURN
                     'return_stmt': 0      # Statement offset to return to
                 }

                 Note: 'from_line' is redundant with 'return_line' - both contain the same value
                       (the line number to return to after RETURN). The 'from_line' field exists
                       for backward compatibility with code that expects it. Use 'return_line'
                       for new code as it more clearly indicates the field's purpose.

                 For FOR loops:
                 {
                     'type': 'FOR',
                     'var': 'I',
                     'current': 5,
                     'end': 10,
                     'step': 1,
                     'line': 100,
                     'stmt': 0             # Statement offset
                 }

                 For WHILE loops:
                 {
                     'type': 'WHILE',
                     'line': 150,
                     'stmt': 0             # Statement offset
                 }

                 Example with nested control flow:
                 [
                     {'type': 'FOR', 'var': 'I', 'current': 1, 'end': 10, 'step': 1, 'line': 100, 'stmt': 0},
                     {'type': 'GOSUB', 'from_line': 130, 'return_line': 130, 'return_stmt': 0},
                     {'type': 'WHILE', 'line': 500, 'stmt': 0}
                 ]

                 This shows: FOR I at line 100, statement offset 0 (1st statement), then GOSUB (will return to line 130, offset 0),
                 then WHILE at line 500, statement offset 0 (innermost).
                 Proper unwinding would be: WEND, RETURN (to line 130), NEXT I.

        Note: The order reflects nesting level based on execution order (when each
              structure was entered), not source line order.
        """
        result = []
        for entry in self.execution_stack:
            if entry['type'] == 'GOSUB':
                result.append({
                    'type': 'GOSUB',
                    'from_line': entry.get('return_line', 0),  # Line to return to
                    'return_line': entry.get('return_line', 0),
                    'return_stmt': entry.get('return_stmt', 0)  # Statement offset
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
                    'line': entry.get('return_line', 0),
                    'stmt': entry.get('return_stmt', 0)  # Statement offset
                })
            elif entry['type'] == 'WHILE':
                result.append({
                    'type': 'WHILE',
                    'line': entry.get('while_line', 0),
                    'stmt': entry.get('while_stmt', 0)  # Statement offset
                })

        return result

    # Backward compatibility alias
    def get_loop_stack(self):
        """Deprecated (as of 2025-10-25): Use get_execution_stack() instead.

        This is a compatibility alias maintained for backward compatibility.
        get_execution_stack() provides the same functionality with a clearer name
        (execution stack vs loop stack).

        Deprecated since: 2025-10-25 (commit cda25c84)
        Will be removed: No earlier than 2026-01-01
        """
        return self.get_execution_stack()

    # ========================================================================
    # Breakpoint Management
    # ========================================================================

    def set_breakpoint(self, line_or_pc, stmt_offset=None):
        """Add a breakpoint at the specified line or statement.

        Args:
            line_or_pc: Line number (int) or PC object for breakpoint
            stmt_offset: Optional statement offset. If None, breaks on entire line.
                        Ignored if line_or_pc is a PC object.
                        Note: Uses 0-based indexing (offset 0 = 1st statement, offset 1 = 2nd statement, offset 2 = 3rd statement, etc.)

        Examples:
            set_breakpoint(100)           # Line-level (entire line)
            set_breakpoint(100, 2)        # Statement-level (line 100, statement offset 2 = 3rd statement)
            set_breakpoint(PC(100, 2))    # PC object (preferred)
        """
        from src.pc import PC
        if isinstance(line_or_pc, PC):
            # PC object passed directly
            self.breakpoints.add(line_or_pc)
        elif stmt_offset is not None:
            # Statement-level: (line, offset)
            self.breakpoints.add(PC(line_or_pc, stmt_offset))
        else:
            # Line-level: Create PC with statement=0 (will match any statement on line due to PC.__eq__)
            self.breakpoints.add(PC(line_or_pc, 0))

    def clear_breakpoint(self, line_or_pc, stmt_offset=None):
        """Remove a breakpoint at the specified line or statement.

        Args:
            line_or_pc: Line number (int) or PC object for breakpoint
            stmt_offset: Optional statement offset. If None, removes line-level breakpoint.
                        Ignored if line_or_pc is a PC object.

        Examples:
            clear_breakpoint(100)           # Line-level
            clear_breakpoint(100, 2)        # Statement-level
            clear_breakpoint(PC(100, 2))    # PC object (preferred)
        """
        from src.pc import PC
        if isinstance(line_or_pc, PC):
            # PC object passed directly
            self.breakpoints.discard(line_or_pc)
        elif stmt_offset is not None:
            # Statement-level: (line, offset)
            self.breakpoints.discard(PC(line_or_pc, stmt_offset))
        else:
            # Line-level: Create PC with statement=0 to match set_breakpoint behavior
            self.breakpoints.discard(PC(line_or_pc, 0))

    def clear_breakpoints(self):
        """Clear all breakpoints."""
        self.breakpoints.clear()

    def reset_for_run(self, ast_or_line_table, line_text_map=None):
        """Reset runtime for RUN command - like CLEAR + reload program.

        Equivalent to:
        - CLEAR (clear variables, arrays, files, DATA pointer, etc.)
        - Reload program and rebuild statement table
        - Reset PC to start

        Preserves:
        - Breakpoints (persist across runs)
        - common_vars (preserved for CHAIN compatibility)

        Args:
            ast_or_line_table: New program AST or line table
            line_text_map: Optional line text map for error messages
        """
        # Store new program
        self._ast_or_line_table = ast_or_line_table
        self.line_text_map = line_text_map or {}

        # Clear variables and arrays
        self._variables.clear()
        self._arrays.clear()
        self._variable_case_variants.clear()

        # Reset array base (can be set again by OPTION BASE)
        self.array_base = 0
        self.option_base_executed = False

        # Clear execution state
        self.execution_stack.clear()
        self.for_loop_states.clear()

        # Clear DATA
        self.data_items.clear()
        self.data_pointer = 0
        self.data_line_map.clear()

        # Clear user functions
        self.user_functions.clear()

        # Close all files
        for file_num in list(self.files.keys()):
            try:
                file_obj = self.files[file_num]
                if hasattr(file_obj, 'close'):
                    file_obj.close()
            except:
                pass
        self.files.clear()
        self.field_buffers.clear()

        # Clear error handling
        self.error_handler = None
        self.error_handler_is_gosub = False

        # Reset RND
        self.rnd_last = 0.5

        # Reset break handling
        self.break_requested = False

        # Reset trace
        self.trace_on = False
        self.trace_detail = 'line'

        # Reinitialize system variables
        self.set_variable_raw('err%', 0)
        self.set_variable_raw('erl%', 0)

        # Rebuild statement table and PC (like setup())
        self.statement_table = StatementTable()
        self.pc = PC.halted()
        self.npc = None

        # Process program lines to rebuild statement table
        if isinstance(self._ast_or_line_table, dict):
            lines_to_process = self._ast_or_line_table.values()
        else:
            lines_to_process = self._ast_or_line_table.lines

        for line in lines_to_process:
            for stmt_offset, stmt in enumerate(line.statements):
                pc = PC(line.line_number, stmt_offset)
                self.statement_table.add(pc, stmt)

                # Extract DATA and DEF FN
                if isinstance(stmt, DataStatementNode):
                    for value in stmt.values:
                        data_index = len(self.data_items)
                        if isinstance(value, list):
                            for v in value:
                                self.data_line_map[len(self.data_items)] = line.line_number
                                self.data_items.append(v)
                        else:
                            self.data_line_map[data_index] = line.line_number
                            self.data_items.append(value)
                elif isinstance(stmt, DefFnStatementNode):
                    self.user_functions[stmt.name] = stmt

        # Initialize PC to first statement
        self.pc = self.statement_table.first_pc()

        # NOTE: self.breakpoints is NOT cleared - breakpoints persist across RUN
        # NOTE: self.common_vars is NOT cleared - preserved for CHAIN compatibility

        return self

