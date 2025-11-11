#!/usr/bin/env python3
"""
Code Generation Backend Interface

This module defines the abstract interface for code generation backends.
Different backends can generate code for different target platforms:
- C code for z88dk (CP/M, Z80)
- Assembly for various processors
- Other high-level languages

Each backend receives a fully analyzed AST from the semantic analyzer
and generates executable code in the target language.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Set, Optional, Any
from src.ast_nodes import *
from src.semantic_analyzer import SymbolTable, VarType


class CodeGenBackend(ABC):
    """Abstract base class for code generation backends"""

    def __init__(self, symbols: SymbolTable):
        """
        Initialize the backend with symbol table information.

        Args:
            symbols: Symbol table from semantic analysis
        """
        self.symbols = symbols
        self.errors: List[str] = []
        self.warnings: List[str] = []

    @abstractmethod
    def generate(self, program: ProgramNode) -> str:
        """
        Generate code for the entire program.

        Args:
            program: Fully analyzed AST

        Returns:
            Generated source code as a string
        """
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """Return the file extension for generated code (e.g., '.c', '.asm')"""
        pass

    @abstractmethod
    def get_compiler_command(self, source_file: str, output_file: str) -> List[str]:
        """
        Return the command to compile the generated code.

        Args:
            source_file: Path to generated source file
            output_file: Desired output executable path

        Returns:
            List of command arguments (e.g., ['gcc', '-o', 'output', 'source.c'])
        """
        pass


class Z88dkCBackend(CodeGenBackend):
    """
    C code generator for z88dk compiler targeting CP/M on Z80.

    Supports:
    - Integer variables (BASIC ! suffix maps to C int)
    - FOR/NEXT loops
    - PRINT statements for integers
    - String variables and operations (using mb25_string runtime)

    Known limitations (not yet implemented):
    - Arrays (partial - string arrays need work)
    - Complex expressions beyond simple binary operations
    """

    def __init__(self, symbols: SymbolTable):
        super().__init__(symbols)
        self.indent_level = 0
        self.line_labels: Set[int] = set()  # Line numbers that need labels
        self.gosub_return_counter = 0  # Counter for unique GOSUB return labels
        self.total_gosubs = 0  # Total number of GOSUB statements in program
        self.string_count = 0  # Total number of string descriptors needed
        self.string_ids = {}  # Maps variable name to string ID
        self.next_temp_id = 0  # For temporary string allocation
        self.max_temps_per_statement = 5  # Estimate max temporaries needed

        # DATA/READ/RESTORE support
        self.data_values: List[Any] = []  # All DATA values in order
        self.data_types: List[str] = []  # Type of each DATA value ('int', 'float', 'string')

        # DEF FN user-defined functions
        self.def_fn_functions: List[DefFnStatementNode] = []

    def get_file_extension(self) -> str:
        return '.c'

    def get_compiler_command(self, source_file: str, output_file: str) -> List[str]:
        """Return z88dk.zcc command for CP/M compilation.

        Requirements:
        - z88dk must be installed and z88dk.zcc must be in your PATH
        - Installation options:
          * Ubuntu/Debian: sudo snap install z88dk (then add /snap/bin to PATH)
          * Build from source: https://github.com/z88dk/z88dk
          * Docker: docker pull z88dk/z88dk

        The compiler uses /usr/bin/env to find z88dk.zcc in PATH, making it
        portable across different installation methods.

        CPU Target:
        - Default: Z80 (z88dk's +cpm defaults to Z80)
        - Note: -m8080 flag has linking issues with printf in current z88dk
        - Most CP/M systems use Z80 anyway (backwards compatible with 8080)
        """
        # z88dk.zcc +cpm source.c -create-app -o output
        # +cpm: Target CP/M operating system (defaults to Z80)
        # -create-app: Generate .COM executable
        # -lm: Link math library for floating point support
        # Note: -m8080 would be more compatible but has printf linking issues
        return ['/usr/bin/env', 'z88dk.zcc', '+cpm', source_file,
                '-create-app', '-lm', '-o', output_file]

    def indent(self) -> str:
        """Return current indentation string"""
        return '    ' * self.indent_level

    def generate(self, program: ProgramNode) -> str:
        """Generate C code for the program"""
        # First pass: count GOSUB statements
        self._count_gosubs(program)

        # Count strings and allocate IDs
        self._count_strings_and_allocate_ids(program)

        # Collect line numbers that are referenced (for labels)
        self._collect_line_labels(program)

        # Collect DATA values for static initialization
        self._collect_data_values(program)

        # Collect DEF FN functions
        self._collect_def_fn(program)

        code = []

        # Header
        code.append('/* Generated by MBASIC-2025 compiler */')
        code.append('/* Target: CP/M via z88dk */')
        code.append('')

        # String system defines and includes
        if self.string_count > 0:
            code.append(f'#define MB25_NUM_STRINGS {self.string_count}')
            code.append('#define MB25_POOL_SIZE 8192  /* 8KB string pool */')
            code.append('#include "mb25_string.h"')
            code.append('')
            # Generate string ID defines
            for var_name, str_id in sorted(self.string_ids.items(), key=lambda x: x[1]):
                code.append(f'#define STR_{self._mangle_string_name(var_name)} {str_id}')
            code.append('')

        code.append('#include <stdio.h>')
        code.append('#include <stdlib.h>')
        code.append('#include <string.h>')
        code.append('#include <math.h>')
        code.append('')

        # Generate DEF FN functions before main
        if self.def_fn_functions:
            code.extend(self._generate_def_fn_functions())
            code.append('')

        # Main function
        code.append('int main() {')
        self.indent_level += 1

        # Initialize string system if needed
        if self.string_count > 0:
            code.append(self.indent() + '/* Initialize string system */')
            code.append(self.indent() + 'if (mb25_init(MB25_POOL_SIZE) != MB25_SUCCESS) {')
            self.indent_level += 1
            code.append(self.indent() + 'fprintf(stderr, "?Out of memory\\n");')
            code.append(self.indent() + 'return 1;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

        # Variable declarations
        var_decls = self._generate_variable_declarations()
        if var_decls:
            code.extend(var_decls)
            code.append('')

        # GOSUB return stack - for implementing GOSUB/RETURN
        code.append(self.indent() + '/* GOSUB return stack */')
        code.append(self.indent() + 'int gosub_stack[100];  /* Return IDs (0, 1, 2...) - not line numbers */')
        code.append(self.indent() + 'int gosub_sp = 0;      /* Stack pointer */')
        code.append('')

        # Generate DATA array if we have DATA statements
        if self.data_values:
            code.extend(self._generate_data_array())
            code.append('')

        # Generate code for each line
        for line_node in program.lines:
            code.extend(self._generate_line(line_node))

        # End main
        self.indent_level -= 1
        code.append('')

        # Cleanup string system if needed
        if self.string_count > 0:
            code.append('    mb25_cleanup();')

        code.append('    return 0;')
        code.append('}')
        code.append('')

        return '\n'.join(code)

    def _count_strings_and_allocate_ids(self, program: ProgramNode):
        """Count string variables and allocate string IDs"""
        current_id = 0

        # Allocate IDs for string variables from symbol table
        for var_name, var_info in self.symbols.variables.items():
            if var_info.var_type == VarType.STRING:
                if var_info.is_array:
                    # For arrays, allocate IDs for all elements
                    # TODO: Need proper array dimension info from symbol table
                    # For now, allocate a reasonable default
                    array_size = 11  # Default DIM A$(10) = 0-10 = 11 elements
                    self.string_ids[var_name] = current_id
                    current_id += array_size
                else:
                    self.string_ids[var_name] = current_id
                    current_id += 1

        # Reserve space for temporaries (for complex expressions)
        # Estimate based on program complexity
        temp_count = self._estimate_temp_strings_needed(program)
        if temp_count > 0:
            self.string_ids['_TEMP_BASE'] = current_id
            current_id += temp_count
            self.next_temp_id = self.string_ids['_TEMP_BASE']
        else:
            self.next_temp_id = 0

        self.string_count = current_id

    def _estimate_temp_strings_needed(self, program: ProgramNode) -> int:
        """Estimate the maximum number of temporary strings needed"""
        max_temps = 0
        has_any_strings = False

        for line_node in program.lines:
            for stmt in line_node.statements:
                # Count complexity of string expressions in this statement
                temps_needed = self._count_expression_temps(stmt)
                if temps_needed > 0:
                    has_any_strings = True
                max_temps = max(max_temps, temps_needed)

        # Only add buffer if we actually have strings
        if has_any_strings:
            return max_temps + 3
        else:
            return 0

    def _count_expression_temps(self, node) -> int:
        """Count temporary strings needed for an expression or statement"""
        if isinstance(node, PrintStatementNode):
            # Only count string expressions that need temps
            string_count = 0
            for expr in node.expressions:
                if self._expression_produces_string(expr):
                    string_count += 1
            return string_count
        elif isinstance(node, LetStatementNode):
            # Only count if it's a string assignment
            if self._expression_produces_string(node.expression):
                return self._count_concat_depth(node.expression)
            return 0
        elif isinstance(node, IfStatementNode):
            # IF statements might have string operations in THEN/ELSE parts
            max_temps = 0
            if node.then_statements:
                for stmt in node.then_statements:
                    max_temps = max(max_temps, self._count_expression_temps(stmt))
            if node.else_statements:
                for stmt in node.else_statements:
                    max_temps = max(max_temps, self._count_expression_temps(stmt))
            return max_temps
        # For other statements that don't use strings
        return 0

    def _expression_produces_string(self, expr) -> bool:
        """Check if an expression produces a string result"""
        return self._get_expression_type(expr) == VarType.STRING

    def _count_concat_depth(self, expr) -> int:
        """Count depth of concatenation operations"""
        if isinstance(expr, BinaryOpNode) and expr.operator == TokenType.PLUS:
            # For string concatenation
            left_depth = self._count_concat_depth(expr.left)
            right_depth = self._count_concat_depth(expr.right)
            return left_depth + right_depth + 1
        return 0

    def _mangle_string_name(self, basic_name: str) -> str:
        """Convert BASIC string variable name to valid C identifier for defines"""
        # Remove $ suffix and make uppercase for defines
        name = basic_name.rstrip('$').upper()
        # Replace any non-alphanumeric with underscore
        name = ''.join(c if c.isalnum() else '_' for c in name)
        return name

    def _count_gosubs(self, program: ProgramNode):
        """Count total number of GOSUB statements in the program"""
        self.total_gosubs = 0
        for line_node in program.lines:
            for stmt in line_node.statements:
                if isinstance(stmt, GosubStatementNode):
                    self.total_gosubs += 1

    def _collect_line_labels(self, program: ProgramNode):
        """
        Collect all line numbers that need labels (referenced by GOTO, GOSUB, etc.)
        For now, we'll label all lines to keep it simple.
        """
        for line_node in program.lines:
            self.line_labels.add(line_node.line_number)

    def _collect_data_values(self, program: ProgramNode):
        """Collect all DATA statement values for static initialization"""
        self.data_values = []
        self.data_types = []

        for line_node in program.lines:
            for stmt in line_node.statements:
                if isinstance(stmt, DataStatementNode):
                    for value_expr in stmt.values:
                        # Evaluate constant expressions
                        if isinstance(value_expr, NumberNode):
                            self.data_values.append(value_expr.value)
                            # Determine if it's int or float
                            # Check if the value is a whole number
                            if isinstance(value_expr.value, (int, float)) and value_expr.value == int(value_expr.value):
                                self.data_types.append('int')
                                # Store as int
                                self.data_values[-1] = int(value_expr.value)
                            else:
                                self.data_types.append('float')
                        elif isinstance(value_expr, StringNode):
                            self.data_values.append(value_expr.value)
                            self.data_types.append('string')
                        elif isinstance(value_expr, UnaryOpNode) and value_expr.operator == TokenType.MINUS:
                            # Handle negative numbers
                            if isinstance(value_expr.operand, NumberNode):
                                val = -value_expr.operand.value
                                self.data_values.append(val)
                                if isinstance(val, int):
                                    self.data_types.append('int')
                                else:
                                    self.data_types.append('float')
                            else:
                                self.warnings.append(f"Complex expression in DATA not supported: {type(value_expr.operand).__name__}")
                        else:
                            self.warnings.append(f"Complex expression in DATA not supported: {type(value_expr).__name__}")

    def _collect_def_fn(self, program: ProgramNode):
        """Collect all DEF FN functions for generation before main()"""
        self.def_fn_functions = []
        for line_node in program.lines:
            for stmt in line_node.statements:
                if isinstance(stmt, DefFnStatementNode):
                    self.def_fn_functions.append(stmt)

    def _generate_variable_declarations(self) -> List[str]:
        """Generate C variable declarations from symbol table"""
        decls = []

        # Group by type for cleaner output
        integers = []
        singles = []
        doubles = []

        # First, handle arrays
        arrays = []
        seen_arrays = set()  # Track which arrays we've already declared
        for var_name, var_info in self.symbols.variables.items():
            if var_info.is_array and var_info.flattened_size is not None:
                # Generate array declaration (skip duplicates without dimension info)
                var_name_c = self._mangle_variable_name(var_name)

                # Skip if we've already declared this array
                if var_name_c in seen_arrays:
                    continue
                seen_arrays.add(var_name_c)

                if var_info.var_type == VarType.STRING:
                    # String arrays need special handling with mb25_string
                    continue  # Skip for now, TODO: implement string arrays

                # Calculate total size for flattened array
                total_size = var_info.flattened_size or 1

                if var_info.var_type == VarType.INTEGER:
                    arrays.append(f'int {var_name_c}[{total_size}];')
                elif var_info.var_type == VarType.SINGLE:
                    arrays.append(f'float {var_name_c}[{total_size}];')
                elif var_info.var_type == VarType.DOUBLE:
                    arrays.append(f'double {var_name_c}[{total_size}];')
                continue  # Don't process as regular variable

        # Then, handle regular variables
        for var_name, var_info in self.symbols.variables.items():
            if var_info.is_array:
                continue  # Already handled above

            # Skip string variables - they're handled by mb25_string system
            if var_info.var_type == VarType.STRING:
                continue

            c_name = self._mangle_variable_name(var_name)

            if var_info.var_type == VarType.INTEGER:
                integers.append(c_name)
            elif var_info.var_type == VarType.SINGLE:
                singles.append(c_name)
            elif var_info.var_type == VarType.DOUBLE:
                doubles.append(c_name)

        # Generate declarations
        # Arrays first
        if arrays:
            decls.append(self.indent() + '/* Arrays */')
            for array_decl in arrays:
                decls.append(self.indent() + array_decl)

        # Then regular variables
        if integers:
            decls.append(self.indent() + 'int ' + ', '.join(integers) + ';')
        if singles:
            decls.append(self.indent() + 'float ' + ', '.join(singles) + ';')
        if doubles:
            decls.append(self.indent() + 'double ' + ', '.join(doubles) + ';')

        # Add buffer for INPUT if we have strings
        if self.string_count > 0:
            decls.append(self.indent() + 'char input_buffer[256];  /* For INPUT statements */')

        return decls

    def _mangle_variable_name(self, basic_name: str) -> str:
        """
        Convert BASIC variable name to valid C identifier.

        BASIC allows names like "I!", "COUNT%", "VALUE#"
        C needs alphanumeric + underscore, no type suffixes.

        Transformations applied:
        1. Remove type suffix (!%#$)
        2. Convert to lowercase for consistency
        3. Add 'v_' prefix if name conflicts with C keywords
        """
        # Remove type suffix
        name = basic_name.rstrip('!%#$')

        # Make lowercase for consistency
        name = name.lower()

        # Add prefix to avoid C keyword conflicts
        if name in ('int', 'float', 'double', 'char', 'void', 'if', 'for', 'while', 'return'):
            name = 'v_' + name

        return name

    def _generate_line(self, line_node: LineNode) -> List[str]:
        """Generate code for one line of BASIC"""
        code = []

        # Add line label if needed
        if line_node.line_number in self.line_labels:
            # Use goto label syntax: line_100:
            code.append(f'line_{line_node.line_number}:')

        # Generate code for each statement on the line
        for stmt in line_node.statements:
            stmt_code = self._generate_statement(stmt)
            if stmt_code:
                code.extend(stmt_code)

        return code

    def _generate_statement(self, stmt: Any) -> List[str]:
        """Generate code for a single statement"""
        if isinstance(stmt, PrintStatementNode):
            return self._generate_print(stmt)
        elif isinstance(stmt, ForStatementNode):
            return self._generate_for(stmt)
        elif isinstance(stmt, NextStatementNode):
            return self._generate_next(stmt)
        elif isinstance(stmt, LetStatementNode):
            return self._generate_assignment(stmt)
        elif isinstance(stmt, InputStatementNode):
            return self._generate_input(stmt)
        elif isinstance(stmt, IfStatementNode):
            return self._generate_if(stmt)
        elif isinstance(stmt, EndStatementNode):
            return self._generate_end(stmt)
        elif isinstance(stmt, RemarkStatementNode):
            return self._generate_remark(stmt)
        elif isinstance(stmt, WhileStatementNode):
            return self._generate_while(stmt)
        elif isinstance(stmt, WendStatementNode):
            return self._generate_wend(stmt)
        elif isinstance(stmt, GotoStatementNode):
            return self._generate_goto(stmt)
        elif isinstance(stmt, DimStatementNode):
            return self._generate_dim(stmt)
        elif isinstance(stmt, DataStatementNode):
            return self._generate_data(stmt)
        elif isinstance(stmt, ReadStatementNode):
            return self._generate_read(stmt)
        elif isinstance(stmt, RestoreStatementNode):
            return self._generate_restore(stmt)
        elif isinstance(stmt, GosubStatementNode):
            return self._generate_gosub(stmt)
        elif isinstance(stmt, ReturnStatementNode):
            return self._generate_return(stmt)
        elif isinstance(stmt, OnGotoStatementNode):
            return self._generate_on_goto(stmt)
        elif isinstance(stmt, OnGosubStatementNode):
            return self._generate_on_gosub(stmt)
        elif isinstance(stmt, PokeStatementNode):
            return self._generate_poke(stmt)
        elif isinstance(stmt, OutStatementNode):
            return self._generate_out(stmt)
        elif isinstance(stmt, DefFnStatementNode):
            return self._generate_def_fn(stmt)
        elif isinstance(stmt, SwapStatementNode):
            return self._generate_swap(stmt)
        elif isinstance(stmt, RandomizeStatementNode):
            return self._generate_randomize(stmt)
        else:
            # Unsupported statement
            self.warnings.append(f"Unsupported statement type: {type(stmt).__name__}")
            return [self.indent() + f'/* Unsupported: {type(stmt).__name__} */']

    def _get_expression_type(self, expr: Any) -> VarType:
        """Determine the type of an expression"""
        if isinstance(expr, NumberNode):
            # Check if it's a float or integer
            if isinstance(expr.value, float) and expr.value != int(expr.value):
                return VarType.SINGLE  # Default float type
            else:
                return VarType.INTEGER
        elif isinstance(expr, StringNode):
            return VarType.STRING
        elif isinstance(expr, VariableNode):
            var_name = expr.name.upper()
            if var_name in self.symbols.variables:
                return self.symbols.variables[var_name].var_type
            else:
                return VarType.SINGLE  # Default
        elif isinstance(expr, BinaryOpNode):
            # For string concatenation
            left_type = self._get_expression_type(expr.left)
            if left_type == VarType.STRING:
                return VarType.STRING
            # For numeric operations
            return left_type
        elif isinstance(expr, FunctionCallNode):
            # String functions (parser removes $ from function names)
            if expr.name.upper() in ('LEFT', 'RIGHT', 'MID', 'CHR', 'STR', 'STRING$',
                                    'SPACE', 'HEX', 'OCT', 'INKEY', 'INKEY$',
                                    'INPUT$'):
                return VarType.STRING
            # LEN returns integer
            elif expr.name.upper() == 'LEN':
                return VarType.INTEGER
            # ASC returns integer
            elif expr.name.upper() == 'ASC':
                return VarType.INTEGER
            # INSTR returns integer (position)
            elif expr.name.upper() == 'INSTR':
                return VarType.INTEGER
            # VAL returns numeric
            elif expr.name.upper() == 'VAL':
                return VarType.SINGLE
            else:
                return VarType.SINGLE  # Default for other functions
        else:
            return VarType.SINGLE  # Default

    def _get_format_specifier(self, var_type: VarType) -> str:
        """Get printf format specifier for a variable type"""
        if var_type == VarType.INTEGER:
            return '%d'
        elif var_type == VarType.SINGLE:
            return '%g'  # %g uses shortest representation (no trailing zeros)
        elif var_type == VarType.DOUBLE:
            return '%lg'  # %lg for double
        elif var_type == VarType.STRING:
            return '%s'
        else:
            return '%g'

    def _generate_print(self, stmt: PrintStatementNode) -> List[str]:
        """Generate PRINT statement code"""
        code = []

        if stmt.file_number:
            self.warnings.append("PRINT to file not supported yet")
            return [self.indent() + '/* PRINT to file not supported */']

        # Print each expression with appropriate format
        for i, expr in enumerate(stmt.expressions):
            separator = stmt.separators[i] if i < len(stmt.separators) else None

            # Determine format based on expression type
            expr_type = self._get_expression_type(expr)

            if expr_type == VarType.STRING:
                # For strings, need to convert to C string
                str_expr = self._generate_string_expression(expr)
                code.append(self.indent() + '{')
                self.indent_level += 1
                code.append(self.indent() + f'char *temp_str = mb25_to_c_string({str_expr});')
                code.append(self.indent() + 'if (temp_str) {')
                self.indent_level += 1

                if separator == ';':
                    code.append(self.indent() + 'printf("%s", temp_str);')
                elif separator == ',':
                    code.append(self.indent() + 'printf("%s ", temp_str);')
                else:
                    code.append(self.indent() + 'printf("%s\\n", temp_str);')

                code.append(self.indent() + 'free(temp_str);')
                self.indent_level -= 1
                code.append(self.indent() + '}')
                self.indent_level -= 1
                code.append(self.indent() + '}')
            else:
                # Numeric types
                c_expr = self._generate_expression(expr)
                fmt = self._get_format_specifier(expr_type)

                if separator == ';':
                    code.append(self.indent() + f'printf("{fmt}", {c_expr});')
                elif separator == ',':
                    code.append(self.indent() + f'printf("{fmt} ", {c_expr});')
                else:
                    code.append(self.indent() + f'printf("{fmt}\\n", {c_expr});')

        # If no expressions or last separator was ; add newline
        if not stmt.expressions or (stmt.separators and stmt.separators[-1] != ';'):
            if not stmt.expressions:
                code.append(self.indent() + 'printf("\\n");')

        return code

    def _generate_for(self, stmt: ForStatementNode) -> List[str]:
        """Generate FOR loop code"""
        code = []

        var_name = self._mangle_variable_name(stmt.variable.name)
        start = self._generate_expression(stmt.start_expr)
        end = self._generate_expression(stmt.end_expr)
        step = '1'
        if stmt.step_expr:
            step = self._generate_expression(stmt.step_expr)

        # Generate C for loop
        # BASIC: FOR I = 1 TO 10 STEP 2
        # C: for (i = 1; i <= 10; i += 2)

        # Determine comparison operator based on step
        # LIMITATION: Currently only handles positive steps correctly
        # Negative steps (e.g., FOR I = 10 TO 1 STEP -1) would generate incorrect C code
        # and loop indefinitely. This is a known limitation that requires runtime step detection.
        comp = '<='

        code.append(self.indent() + f'for ({var_name} = {start}; {var_name} {comp} {end}; {var_name} += {step}) {{')
        self.indent_level += 1

        return code

    def _generate_next(self, stmt: NextStatementNode) -> List[str]:
        """Generate NEXT statement (close FOR loop)"""
        self.indent_level -= 1
        return [self.indent() + '}']

    def _generate_assignment(self, stmt: LetStatementNode) -> List[str]:
        """Generate assignment statement"""
        # Check if it's a string assignment
        var_type = self._get_expression_type(stmt.variable)

        # Handle array assignment - check if variable has subscripts
        if hasattr(stmt.variable, 'subscripts') and stmt.variable.subscripts is not None and len(stmt.variable.subscripts) > 0:
            # Array element assignment
            array_access = self._generate_array_access(stmt.variable)
            expr = self._generate_expression(stmt.expression)
            return [self.indent() + f'{array_access} = {expr};']

        if var_type == VarType.STRING:
            # String assignment
            var_str_id = self._get_string_id(stmt.variable.name)

            if isinstance(stmt.expression, StringNode):
                # String literal assignment
                return [self.indent() + f'mb25_string_alloc_const({var_str_id}, "{self._escape_string(stmt.expression.value)}");']
            elif isinstance(stmt.expression, VariableNode):
                # Simple variable copy
                src_str_id = self._get_string_id(stmt.expression.name)
                return [self.indent() + f'mb25_string_copy({var_str_id}, {src_str_id});']
            elif isinstance(stmt.expression, FunctionCallNode):
                # String function result
                func_code = self._generate_string_function_statement(stmt.expression, var_str_id)
                return [self.indent() + f'{func_code};']
            elif isinstance(stmt.expression, BinaryOpNode) and stmt.expression.operator == TokenType.PLUS:
                # String concatenation - generate step by step
                return self._generate_concat_assignment(var_str_id, stmt.expression)
            else:
                # Other string expression
                self.warnings.append(f"Unsupported string expression: {type(stmt.expression).__name__}")
                return [self.indent() + f'/* Unsupported string expression */']
        else:
            # Numeric assignment
            var_name = self._mangle_variable_name(stmt.variable.name)
            expr = self._generate_expression(stmt.expression)
            return [self.indent() + f'{var_name} = {expr};']

    def _generate_input(self, stmt: InputStatementNode) -> List[str]:
        """Generate INPUT statement"""
        code = []

        if stmt.file_number:
            self.warnings.append("INPUT from file not supported yet")
            return [self.indent() + '/* INPUT from file not supported */']

        # Generate prompt
        if stmt.prompt:
            # Check if it's a string literal
            if isinstance(stmt.prompt, StringNode):
                prompt_str = stmt.prompt.value
            else:
                # For expressions, we'd need to evaluate - not implemented yet
                prompt_str = ""
                self.warnings.append("Complex prompt expressions not yet supported")

            # Add question mark if not suppressed
            if not stmt.suppress_question:
                prompt_str += "? "

            code.append(self.indent() + f'printf("{self._escape_string(prompt_str)}");')
        elif not stmt.suppress_question:
            # No prompt but show "? " unless suppressed
            code.append(self.indent() + 'printf("? ");')

        # Generate input for each variable
        for i, var_node in enumerate(stmt.variables):
            var_type = self._get_expression_type(var_node)

            if var_type == VarType.STRING:
                # String input
                var_str_id = self._get_string_id(var_node.name)
                code.append(self.indent() + 'if (fgets(input_buffer, 256, stdin)) {')
                self.indent_level += 1
                code.append(self.indent() + 'size_t len = strlen(input_buffer);')
                code.append(self.indent() + 'if (len > 0 && input_buffer[len-1] == \'\\n\') {')
                self.indent_level += 1
                code.append(self.indent() + 'input_buffer[len-1] = \'\\0\';')
                self.indent_level -= 1
                code.append(self.indent() + '}')
                code.append(self.indent() + f'mb25_string_alloc_init({var_str_id}, input_buffer);')
                self.indent_level -= 1
                code.append(self.indent() + '}')
            else:
                # Numeric input
                var_name = self._mangle_variable_name(var_node.name)
                if var_type == VarType.INTEGER:
                    code.append(self.indent() + f'scanf("%d", &{var_name});')
                else:
                    code.append(self.indent() + f'scanf("%f", &{var_name});')

            # If there are more variables, show another prompt
            if i < len(stmt.variables) - 1:
                code.append(self.indent() + 'printf("?? ");  /* Next variable prompt */')

        return code

    def _generate_end(self, stmt: EndStatementNode) -> List[str]:
        """Generate END statement"""
        return [self.indent() + 'return 0;']

    def _generate_remark(self, stmt: RemarkStatementNode) -> List[str]:
        """Generate REM statement as C comment"""
        # Convert BASIC comment to C comment
        comment_text = stmt.text.strip()
        if comment_text:
            return [self.indent() + f'/* {comment_text} */']
        else:
            return []  # Empty comment, skip it

    def _generate_while(self, stmt: WhileStatementNode) -> List[str]:
        """Generate WHILE statement"""
        code = []
        condition = self._generate_expression(stmt.condition)
        code.append(self.indent() + f'while ({condition}) {{')
        self.indent_level += 1
        return code

    def _generate_wend(self, stmt: WendStatementNode) -> List[str]:
        """Generate WEND statement (close WHILE loop)"""
        self.indent_level -= 1
        return [self.indent() + '}']

    def _generate_if(self, stmt: IfStatementNode) -> List[str]:
        """Generate IF/THEN/ELSE statement"""
        code = []

        # Generate condition
        condition = self._generate_expression(stmt.condition)

        # Check if it's a simple GOTO style (IF...THEN line_number)
        if stmt.then_line_number is not None:
            code.append(self.indent() + f'if ({condition}) {{')
            self.indent_level += 1
            code.append(self.indent() + f'goto line_{stmt.then_line_number};')
            self.indent_level -= 1
            code.append(self.indent() + '}')

            if stmt.else_line_number is not None:
                code.append(self.indent() + 'else {')
                self.indent_level += 1
                code.append(self.indent() + f'goto line_{stmt.else_line_number};')
                self.indent_level -= 1
                code.append(self.indent() + '}')
        else:
            # Regular IF with statements
            code.append(self.indent() + f'if ({condition}) {{')
            self.indent_level += 1

            # Generate THEN statements
            if stmt.then_statements:
                for then_stmt in stmt.then_statements:
                    code.extend(self._generate_statement(then_stmt))

            self.indent_level -= 1

            # Generate ELSE statements if present
            if stmt.else_statements:
                code.append(self.indent() + '} else {')
                self.indent_level += 1
                for else_stmt in stmt.else_statements:
                    code.extend(self._generate_statement(else_stmt))
                self.indent_level -= 1
                code.append(self.indent() + '}')
            else:
                code.append(self.indent() + '}')

        return code

    def _generate_goto(self, stmt: GotoStatementNode) -> List[str]:
        """Generate GOTO statement"""
        return [self.indent() + f'goto line_{stmt.line_number};']

    def _generate_dim(self, stmt: DimStatementNode) -> List[str]:
        """Generate DIM statement

        Arrays are already declared at the top of main(), so DIM is mostly
        a no-op in C. However, we might want to initialize them here.
        """
        code = []
        # For now, DIM is handled at declaration time
        # We could add array initialization here if needed
        # e.g., memset(array, 0, sizeof(array));
        return code

    def _generate_data_array(self) -> List[str]:
        """Generate static DATA array and pointer"""
        code = []
        code.append(self.indent() + '/* DATA values */')

        # Check if we have any DATA values
        if not self.data_values:
            return code

        # Generate numeric data array for int/float values
        code.append(self.indent() + f'static const float data_numeric[{len(self.data_values)}] = {{')
        self.indent_level += 1
        for i, (val, typ) in enumerate(zip(self.data_values, self.data_types)):
            if typ == 'int':
                code.append(self.indent() + f'{int(val)}.0f,  /* int: {int(val)} */')
            elif typ == 'float':
                code.append(self.indent() + f'{float(val):.6f}f,  /* float: {float(val)} */')
            elif typ == 'string':
                # Use 0 as placeholder for string values
                code.append(self.indent() + f'0.0f,  /* string placeholder */')
        self.indent_level -= 1
        code.append(self.indent() + '};')

        # Generate string data array if we have any strings
        string_count = sum(1 for t in self.data_types if t == 'string')
        if string_count > 0:
            code.append(self.indent() + f'static const char *data_strings[{len(self.data_values)}] = {{')
            self.indent_level += 1
            for i, (val, typ) in enumerate(zip(self.data_values, self.data_types)):
                if typ == 'string':
                    # Escape quotes in string
                    escaped_str = val.replace('\\', '\\\\').replace('"', '\\"')
                    code.append(self.indent() + f'"{escaped_str}",')
                else:
                    code.append(self.indent() + 'NULL,  /* numeric */')
            self.indent_level -= 1
            code.append(self.indent() + '};')

        # Generate type array
        code.append(self.indent() + f'static const char data_types[{len(self.data_types)}] = {{')
        self.indent_level += 1
        type_chars = {'int': 'I', 'float': 'F', 'string': 'S'}
        for typ in self.data_types:
            code.append(self.indent() + f"'{type_chars[typ]}',")
        self.indent_level -= 1
        code.append(self.indent() + '};')

        # Generate data pointer
        code.append(self.indent() + 'int data_pointer = 0;')

        return code

    def _generate_data(self, stmt: DataStatementNode) -> List[str]:
        """Generate DATA statement - no-op since data is handled statically"""
        # DATA values are collected during analysis and generated as static array
        return []

    def _generate_read(self, stmt: ReadStatementNode) -> List[str]:
        """Generate READ statement"""
        code = []

        for var_node in stmt.variables:
            # Check if we're out of data
            code.append(self.indent() + f'if (data_pointer >= {len(self.data_values)}) {{')
            self.indent_level += 1
            code.append(self.indent() + 'fprintf(stderr, "?Out of DATA\\n");')
            code.append(self.indent() + 'return 1;')
            self.indent_level -= 1
            code.append(self.indent() + '}')

            # Read value based on variable type
            var_type = self._get_expression_type(var_node)
            var_name = self._mangle_variable_name(var_node.name)

            if var_type == VarType.STRING:
                # String variable - read from appropriate source based on DATA type
                str_id = self._get_string_id(var_node.name)
                code.append(self.indent() + 'if (data_types[data_pointer] == \'S\') {')
                self.indent_level += 1
                # Read string directly
                code.append(self.indent() + f'mb25_string_alloc_const({str_id}, data_strings[data_pointer]);')
                self.indent_level -= 1
                code.append(self.indent() + '} else if (data_types[data_pointer] == \'I\' || data_types[data_pointer] == \'F\') {')
                self.indent_level += 1
                # Convert number to string
                code.append(self.indent() + 'char _num_str[32];')
                code.append(self.indent() + f'sprintf(_num_str, "%g", data_numeric[data_pointer]);')
                code.append(self.indent() + f'mb25_string_alloc_init({str_id}, _num_str);')
                self.indent_level -= 1
                code.append(self.indent() + '}')
            elif var_type == VarType.INTEGER:
                # Integer variable - read from appropriate source based on DATA type
                code.append(self.indent() + 'if (data_types[data_pointer] == \'I\' || data_types[data_pointer] == \'F\') {')
                self.indent_level += 1
                code.append(self.indent() + f'{var_name} = (int)data_numeric[data_pointer];')
                self.indent_level -= 1
                code.append(self.indent() + '} else if (data_types[data_pointer] == \'S\') {')
                self.indent_level += 1
                # Convert string to int
                code.append(self.indent() + f'{var_name} = data_strings[data_pointer] ? atoi(data_strings[data_pointer]) : 0;')
                self.indent_level -= 1
                code.append(self.indent() + '}')
            else:
                # Float/double variable - read from appropriate source based on DATA type
                code.append(self.indent() + 'if (data_types[data_pointer] == \'I\' || data_types[data_pointer] == \'F\') {')
                self.indent_level += 1
                code.append(self.indent() + f'{var_name} = data_numeric[data_pointer];')
                self.indent_level -= 1
                code.append(self.indent() + '} else if (data_types[data_pointer] == \'S\') {')
                self.indent_level += 1
                # Convert string to float
                code.append(self.indent() + f'{var_name} = data_strings[data_pointer] ? atof(data_strings[data_pointer]) : 0.0;')
                self.indent_level -= 1
                code.append(self.indent() + '}')

            code.append(self.indent() + 'data_pointer++;')

        return code

    def _generate_restore(self, stmt: RestoreStatementNode) -> List[str]:
        """Generate RESTORE statement"""
        code = []

        if stmt.line_number is None:
            # RESTORE without line number - reset to beginning
            code.append(self.indent() + 'data_pointer = 0;')
        else:
            # RESTORE with line number - not fully supported in compiled version
            # For simplicity, just reset to beginning
            code.append(self.indent() + '/* RESTORE to specific line not supported - resetting to beginning */')
            code.append(self.indent() + 'data_pointer = 0;')
            self.warnings.append(f"RESTORE to line {stmt.line_number} not supported - resetting to beginning")

        return code

    def _generate_array_access(self, var_node: VariableNode) -> str:
        """Generate C code for array access

        BASIC arrays can be multi-dimensional, but we flatten them to 1D in C.
        The semantic analyzer has already computed the flattened index expression.
        """
        var_name = self._mangle_variable_name(var_node.name)
        # Need to include type suffix when looking up in symbol table
        lookup_name = var_node.name.upper()
        if var_node.type_suffix and var_node.explicit_type_suffix:
            # Only add suffix if it was explicitly in the source
            lookup_name += var_node.type_suffix
        var_info = self.symbols.variables.get(lookup_name)

        # If not found, try without suffix (for implicitly typed variables)
        if not var_info:
            var_info = self.symbols.variables.get(var_node.name.upper())

        if not var_info or not var_info.is_array:
            self.warnings.append(f"Variable {var_node.name} is not an array")
            return var_name

        # If the semantic analyzer has already flattened the subscripts
        # (it should have transformed multi-dimensional to single index)
        if len(var_node.subscripts) == 1:
            # Simple 1D access or already flattened
            index = self._generate_expression(var_node.subscripts[0])
            return f'{var_name}[{index}]'
        else:
            # Multi-dimensional - need to flatten
            # Calculate flattened index: for A(i,j,k) with dims (d1,d2,d3)
            # index = i*(d2+1)*(d3+1) + j*(d3+1) + k (for OPTION BASE 0)
            dimensions = var_info.dimensions or []
            if not dimensions:
                self.warnings.append(f"No dimension info for array {var_node.name}")
                return var_name

            # Build the flattened index expression
            index_parts = []
            for i, subscript in enumerate(var_node.subscripts):
                sub_expr = self._generate_expression(subscript)

                # Calculate stride for this dimension
                stride = 1
                for j in range(i + 1, len(dimensions)):
                    # Assuming OPTION BASE 0 by default
                    stride *= (dimensions[j] + 1)

                if stride > 1:
                    index_parts.append(f'({sub_expr} * {stride})')
                else:
                    index_parts.append(sub_expr)

            flattened_index = ' + '.join(index_parts)
            return f'{var_name}[{flattened_index}]'

    def _generate_gosub(self, stmt: GosubStatementNode) -> List[str]:
        """Generate GOSUB statement with proper return mechanism"""
        code = []
        # Each GOSUB gets a unique return label
        return_id = self.gosub_return_counter
        self.gosub_return_counter += 1

        # Push return ID onto stack
        code.append(self.indent() + f'gosub_stack[gosub_sp++] = {return_id};  /* Push return ID */')
        code.append(self.indent() + f'goto line_{stmt.line_number};  /* Jump to subroutine */')
        code.append(f'gosub_return_{return_id}:  /* Return point */')
        return code

    def _generate_return(self, stmt: ReturnStatementNode) -> List[str]:
        """Generate RETURN statement"""
        code = []
        # Pop return ID from stack and jump to appropriate return point
        code.append(self.indent() + 'if (gosub_sp > 0) {')
        self.indent_level += 1
        code.append(self.indent() + 'switch (gosub_stack[--gosub_sp]) {')
        self.indent_level += 1

        # Generate case statements for each GOSUB in the program
        # (iterating over GOSUB count from the first pass)
        for return_id in range(self.total_gosubs):
            code.append(self.indent() + f'case {return_id}: goto gosub_return_{return_id};')

        # Default case (should never happen if program is correct)
        code.append(self.indent() + 'default: break;  /* Error: invalid return address */')

        self.indent_level -= 1
        code.append(self.indent() + '}')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        return code

    def _generate_on_goto(self, stmt: OnGotoStatementNode) -> List[str]:
        """Generate ON...GOTO statement

        ON expr GOTO line1, line2, ...
        If expr = 1, goto line1; if expr = 2, goto line2; etc.
        If expr is out of range, fall through to next statement.
        """
        code = []
        index_expr = self._generate_expression(stmt.expression)

        # Generate switch statement
        code.append(self.indent() + f'switch ((int)({index_expr})) {{')
        self.indent_level += 1

        # Generate cases for each line number
        for i, line_num in enumerate(stmt.line_numbers, 1):
            code.append(self.indent() + f'case {i}: goto line_{line_num};')

        # Default case - fall through
        code.append(self.indent() + 'default: break;  /* Out of range - fall through */')

        self.indent_level -= 1
        code.append(self.indent() + '}')

        return code

    def _generate_on_gosub(self, stmt: OnGosubStatementNode) -> List[str]:
        """Generate ON...GOSUB statement

        ON expr GOSUB line1, line2, ...
        If expr = 1, gosub line1; if expr = 2, gosub line2; etc.
        If expr is out of range, fall through to next statement.
        """
        code = []
        index_expr = self._generate_expression(stmt.expression)

        # Generate switch statement
        code.append(self.indent() + f'switch ((int)({index_expr})) {{')
        self.indent_level += 1

        # Generate cases for each line number
        for i, line_num in enumerate(stmt.line_numbers, 1):
            code.append(self.indent() + f'case {i}:')
            self.indent_level += 1

            # Push return address and jump
            return_id = self.gosub_return_counter
            self.gosub_return_counter += 1
            code.append(self.indent() + f'gosub_stack[gosub_sp++] = {return_id};')
            code.append(self.indent() + f'goto line_{line_num};')
            code.append(f'gosub_return_{return_id}:')
            code.append(self.indent() + 'break;')

            self.indent_level -= 1

        # Default case - fall through
        code.append(self.indent() + 'default: break;  /* Out of range - fall through */')

        self.indent_level -= 1
        code.append(self.indent() + '}')

        return code

    def _generate_poke(self, stmt: PokeStatementNode) -> List[str]:
        """Generate POKE statement

        POKE address, value - Write byte to memory
        In compiled C code, this is generally unsafe/unsupported
        """
        code = []
        addr_expr = self._generate_expression(stmt.address)
        value_expr = self._generate_expression(stmt.value)

        # For safety, we'll generate a comment but not actually do the POKE
        # Real implementation would need proper memory management
        code.append(self.indent() + f'/* POKE {addr_expr}, {value_expr} - memory writes not supported in compiled code */')

        # Optionally, could warn at compile time
        self.warnings.append("POKE statement not fully supported in compiled code")

        return code

    def _generate_out(self, stmt: OutStatementNode) -> List[str]:
        """Generate OUT statement

        OUT port, value - Write byte to I/O port
        In compiled C code, this requires platform-specific implementation
        """
        code = []
        port_expr = self._generate_expression(stmt.port)
        value_expr = self._generate_expression(stmt.value)

        # For z88dk/CP/M, we could potentially use outp() function if available
        # But for safety, we'll just generate a comment
        code.append(self.indent() + f'/* OUT {port_expr}, {value_expr} - I/O port writes not supported in compiled code */')

        # Could potentially use z88dk's outp() for real implementation:
        # code.append(self.indent() + f'outp({port_expr}, {value_expr});')

        self.warnings.append("OUT statement not fully supported in compiled code")

        return code

    def _generate_def_fn(self, stmt: DefFnStatementNode) -> List[str]:
        """Generate DEF FN statement - no-op since functions are generated before main()"""
        # The actual function is generated before main()
        # This is just a placeholder in the flow
        return []

    def _generate_def_fn_functions(self) -> List[str]:
        """Generate C functions for all DEF FN definitions"""
        code = []
        code.append('/* User-defined functions (DEF FN) */')

        for fn_stmt in self.def_fn_functions:
            # Determine return type from function name
            return_type = 'double'  # Default to double
            if fn_stmt.name.endswith('%'):
                return_type = 'int'
            elif fn_stmt.name.endswith('$'):
                # String functions would need special handling
                self.warnings.append(f"String DEF FN functions not yet supported: {fn_stmt.name}")
                continue

            # Function name without type suffix
            # fn_stmt.name already includes 'fn' prefix from parser
            func_name = fn_stmt.name.lower().rstrip('%!#$')
            # Replace 'fn' prefix with 'fn_' for C naming
            if func_name.startswith('fn'):
                func_name = 'fn_' + func_name[2:]
            else:
                func_name = 'fn_' + func_name

            # Generate function signature
            params = []
            if fn_stmt.parameters:
                for param in fn_stmt.parameters:
                    param_type = 'double'
                    if param.name.endswith('%'):
                        param_type = 'int'
                    elif param.name.endswith('$'):
                        # String parameters would need special handling
                        self.warnings.append(f"String parameters in DEF FN not yet supported")
                        param_type = 'char*'
                    param_name = self._mangle_variable_name(param.name)
                    params.append(f'{param_type} {param_name}')

            if params:
                code.append(f'{return_type} {func_name}({", ".join(params)}) {{')
            else:
                code.append(f'{return_type} {func_name}(void) {{')

            # Generate function body - just return the expression
            self.indent_level += 1
            expr_code = self._generate_expression(fn_stmt.expression)
            code.append(self.indent() + f'return {expr_code};')
            self.indent_level -= 1
            code.append('}')

        return code

    def _generate_swap(self, stmt: SwapStatementNode) -> List[str]:
        """Generate SWAP statement

        SWAP var1, var2 - Exchange values of two variables
        """
        code = []

        # Get variable types
        var1_type = self._get_expression_type(stmt.var1)
        var2_type = self._get_expression_type(stmt.var2)

        # Check that types match
        if var1_type != var2_type:
            self.warnings.append(f"SWAP between different types not supported")
            return [self.indent() + '/* Type mismatch in SWAP */']

        if var1_type == VarType.STRING:
            # For strings, swap the string IDs
            var1_id = self._get_string_id(stmt.var1.name)
            var2_id = self._get_string_id(stmt.var2.name)
            code.append(self.indent() + '{')
            self.indent_level += 1
            code.append(self.indent() + 'mb25_string temp_str;')
            code.append(self.indent() + f'mb25_string_copy(&temp_str, &mb25_strings[{var1_id}]);')
            code.append(self.indent() + f'mb25_string_copy(&mb25_strings[{var1_id}], &mb25_strings[{var2_id}]);')
            code.append(self.indent() + f'mb25_string_copy(&mb25_strings[{var2_id}], &temp_str);')
            self.indent_level -= 1
            code.append(self.indent() + '}')
        else:
            # For numeric types
            var1_name = self._generate_variable_reference(stmt.var1)
            var2_name = self._generate_variable_reference(stmt.var2)

            # Determine temp variable type
            c_type = 'int' if var1_type == VarType.INTEGER else 'double'

            code.append(self.indent() + '{')
            self.indent_level += 1
            code.append(self.indent() + f'{c_type} _temp = {var1_name};')
            code.append(self.indent() + f'{var1_name} = {var2_name};')
            code.append(self.indent() + f'{var2_name} = _temp;')
            self.indent_level -= 1
            code.append(self.indent() + '}')

        return code

    def _generate_randomize(self, stmt: RandomizeStatementNode) -> List[str]:
        """Generate RANDOMIZE statement

        RANDOMIZE [seed] - Initialize random number generator
        """
        code = []

        if stmt.seed is not None:
            # Use provided seed
            seed_expr = self._generate_expression(stmt.seed)
            code.append(self.indent() + f'srand((unsigned int)({seed_expr}));')
        else:
            # Use time as seed (requires time.h)
            code.append(self.indent() + 'srand((unsigned int)time(NULL));')
            # Note: We'd need to include time.h for this

        return code

    def _generate_variable_reference(self, var_node: VariableNode) -> str:
        """Generate C code for a variable reference (for SWAP)"""
        if var_node.subscripts:
            # Array element
            return self._generate_array_access(var_node)
        else:
            # Simple variable
            return self._mangle_variable_name(var_node.name)

    def _generate_expression(self, expr: Any) -> str:
        """Generate C code for an expression"""
        # Check if it's a string expression
        expr_type = self._get_expression_type(expr)
        if expr_type == VarType.STRING:
            # This shouldn't be called for strings - use _generate_string_expression
            self.warnings.append("String expression in numeric context")
            return '0  /* string in numeric context */'

        if isinstance(expr, NumberNode):
            # Format numbers appropriately - if it's a whole number, output as integer
            if isinstance(expr.value, (int, float)) and expr.value == int(expr.value):
                return str(int(expr.value))
            else:
                return str(expr.value)
        elif isinstance(expr, VariableNode):
            # Check if it's an array access
            if expr.subscripts:
                return self._generate_array_access(expr)
            else:
                return self._mangle_variable_name(expr.name)
        elif isinstance(expr, BinaryOpNode):
            return self._generate_binary_op(expr)
        elif isinstance(expr, UnaryOpNode):
            return self._generate_unary_op(expr)
        elif isinstance(expr, FunctionCallNode):
            return self._generate_function_call(expr)
        else:
            self.warnings.append(f"Unsupported expression type: {type(expr).__name__}")
            return '0  /* unsupported expression */'

    def _generate_string_expression(self, expr: Any) -> str:
        """Generate C code for a string expression"""
        if isinstance(expr, StringNode):
            # String literal - allocate as constant
            temp_id = self._get_temp_string_id()
            return f'mb25_string_alloc_const({temp_id}, "{self._escape_string(expr.value)}"), {temp_id}'
        elif isinstance(expr, VariableNode):
            # String variable reference
            return self._get_string_id(expr.name)
        elif isinstance(expr, BinaryOpNode) and expr.operator == TokenType.PLUS:
            # String concatenation
            left_str = self._generate_string_expression(expr.left)
            right_str = self._generate_string_expression(expr.right)
            result_id = self._get_temp_string_id()
            return f'mb25_string_concat({result_id}, {left_str}, {right_str}), {result_id}'
        elif isinstance(expr, FunctionCallNode):
            return self._generate_string_function(expr)
        else:
            self.warnings.append(f"Unsupported string expression: {type(expr).__name__}")
            return '0  /* unsupported string expression */'

    def _generate_string_function(self, expr: FunctionCallNode) -> str:
        """Generate code for string functions"""
        func_name = expr.name.upper()
        result_id = self._get_temp_string_id()

        if func_name == 'LEFT':
            if len(expr.arguments) != 2:
                self.warnings.append("LEFT$ requires 2 arguments")
                return '0'
            str_arg = self._generate_string_expression(expr.arguments[0])
            len_arg = self._generate_expression(expr.arguments[1])
            return f'mb25_string_left({result_id}, {str_arg}, {len_arg}), {result_id}'

        elif func_name == 'RIGHT':
            if len(expr.arguments) != 2:
                self.warnings.append("RIGHT$ requires 2 arguments")
                return '0'
            str_arg = self._generate_string_expression(expr.arguments[0])
            len_arg = self._generate_expression(expr.arguments[1])
            return f'mb25_string_right({result_id}, {str_arg}, {len_arg}), {result_id}'

        elif func_name == 'MID':
            if len(expr.arguments) < 2 or len(expr.arguments) > 3:
                self.warnings.append("MID$ requires 2 or 3 arguments")
                return '0'
            str_arg = self._generate_string_expression(expr.arguments[0])
            start_arg = self._generate_expression(expr.arguments[1])
            if len(expr.arguments) == 3:
                len_arg = self._generate_expression(expr.arguments[2])
                return f'mb25_string_mid({result_id}, {str_arg}, {start_arg}, {len_arg}), {result_id}'
            else:
                # MID$ without length - to end of string
                return f'mb25_string_mid({result_id}, {str_arg}, {start_arg}, 255), {result_id}'

        elif func_name == 'CHR':
            if len(expr.arguments) != 1:
                self.warnings.append("CHR$ requires 1 argument")
                return '0'
            code_arg = self._generate_expression(expr.arguments[0])
            # Create a single-character string
            return f'({{ char _chr[2] = {{(char){code_arg}, \'\\0\'}}; mb25_string_alloc_init({result_id}, _chr); }}), {result_id}'

        elif func_name == 'STR':
            if len(expr.arguments) != 1:
                self.warnings.append("STR$ requires 1 argument")
                return '0'
            num_arg = self._generate_expression(expr.arguments[0])
            # Convert number to string
            return f'({{ char _str[32]; sprintf(_str, "%g", (double){num_arg}); mb25_string_alloc_init({result_id}, _str); }}), {result_id}'

        elif func_name == 'SPACE':
            if len(expr.arguments) != 1:
                self.warnings.append("SPACE$ requires 1 argument")
                return '0'
            count_arg = self._generate_expression(expr.arguments[0])
            # Create string of spaces
            return f'({{ int _n = {count_arg}; char *_sp = malloc(_n+1); if(_sp) {{ memset(_sp, \' \', _n); _sp[_n] = \'\\0\'; mb25_string_alloc_init({result_id}, _sp); free(_sp); }} }}), {result_id}'

        elif func_name == 'STRING$':
            if len(expr.arguments) != 2:
                self.warnings.append("STRING$ requires 2 arguments")
                return '0'
            count_arg = self._generate_expression(expr.arguments[0])
            # Second arg can be either a number (ASCII code) or string (use first char)
            if self._get_expression_type(expr.arguments[1]) == VarType.STRING:
                str_arg = self._generate_string_expression(expr.arguments[1])
                return f'({{ int _n = {count_arg}; uint8_t *_data = mb25_get_data({str_arg}); char _ch = (_data && mb25_get_length({str_arg}) > 0) ? _data[0] : \' \'; char *_s = malloc(_n+1); if(_s) {{ memset(_s, _ch, _n); _s[_n] = \'\\0\'; mb25_string_alloc_init({result_id}, _s); free(_s); }} }}), {result_id}'
            else:
                char_arg = self._generate_expression(expr.arguments[1])
                return f'({{ int _n = {count_arg}; char _ch = (char){char_arg}; char *_s = malloc(_n+1); if(_s) {{ memset(_s, _ch, _n); _s[_n] = \'\\0\'; mb25_string_alloc_init({result_id}, _s); free(_s); }} }}), {result_id}'

        elif func_name == 'HEX':
            if len(expr.arguments) != 1:
                self.warnings.append("HEX$ requires 1 argument")
                return '0'
            num_arg = self._generate_expression(expr.arguments[0])
            # Convert number to hex string
            return f'({{ char _hex[17]; sprintf(_hex, "%X", (int){num_arg}); mb25_string_alloc_init({result_id}, _hex); }}), {result_id}'

        elif func_name == 'OCT':
            if len(expr.arguments) != 1:
                self.warnings.append("OCT$ requires 1 argument")
                return '0'
            num_arg = self._generate_expression(expr.arguments[0])
            # Convert number to octal string
            return f'({{ char _oct[23]; sprintf(_oct, "%o", (int){num_arg}); mb25_string_alloc_init({result_id}, _oct); }}), {result_id}'

        elif func_name == 'INKEY' or func_name == 'INKEY$':
            # INKEY$ reads a key without waiting (non-blocking)
            # For compiled code, this is runtime-specific
            self.warnings.append("INKEY$ requires runtime support - returning empty string")
            return f'mb25_string_alloc_init({result_id}, ""), {result_id}'

        else:
            self.warnings.append(f"Unsupported string function: {func_name}")
            return '0'

    def _generate_function_call(self, expr: FunctionCallNode) -> str:
        """Generate code for numeric function calls"""
        func_name = expr.name.upper()

        # Check if it's a user-defined function (starts with FN)
        if func_name.startswith('FN'):
            # Generate call to user-defined function
            c_func_name = 'fn_' + func_name[2:].rstrip('%!#$').lower()
            args = []
            for arg in expr.arguments:
                args.append(self._generate_expression(arg))
            if args:
                return f'{c_func_name}({", ".join(args)})'
            else:
                return f'{c_func_name}()'

        if func_name == 'LEN':
            if len(expr.arguments) != 1:
                self.warnings.append("LEN requires 1 argument")
                return '0'
            str_arg = self._generate_string_expression(expr.arguments[0])
            return f'mb25_get_length({str_arg})'

        elif func_name == 'ASC':
            if len(expr.arguments) != 1:
                self.warnings.append("ASC requires 1 argument")
                return '0'
            str_arg = self._generate_string_expression(expr.arguments[0])
            return f'({{ uint8_t *_data = mb25_get_data({str_arg}); (_data && mb25_get_length({str_arg}) > 0) ? _data[0] : 0; }})'

        elif func_name == 'VAL':
            if len(expr.arguments) != 1:
                self.warnings.append("VAL requires 1 argument")
                return '0'
            str_arg = self._generate_string_expression(expr.arguments[0])
            return f'({{ char *_s = mb25_to_c_string({str_arg}); double _v = _s ? atof(_s) : 0; if (_s) free(_s); _v; }})'

        elif func_name == 'INSTR':
            # INSTR can have 2 or 3 arguments: INSTR([start,] string1, string2)
            if len(expr.arguments) < 2 or len(expr.arguments) > 3:
                self.warnings.append("INSTR requires 2 or 3 arguments")
                return '0'

            if len(expr.arguments) == 2:
                # INSTR(string1, string2) - search from beginning
                str1_arg = self._generate_string_expression(expr.arguments[0])
                str2_arg = self._generate_string_expression(expr.arguments[1])
                return f'({{ char *_s1 = mb25_to_c_string({str1_arg}); char *_s2 = mb25_to_c_string({str2_arg}); ' \
                       f'int _pos = 0; if (_s1 && _s2) {{ char *_p = strstr(_s1, _s2); _pos = _p ? (_p - _s1 + 1) : 0; }} ' \
                       f'if (_s1) free(_s1); if (_s2) free(_s2); _pos; }})'
            else:
                # INSTR(start, string1, string2) - search from position
                start_arg = self._generate_expression(expr.arguments[0])
                str1_arg = self._generate_string_expression(expr.arguments[1])
                str2_arg = self._generate_string_expression(expr.arguments[2])
                return f'({{ int _start = {start_arg}; char *_s1 = mb25_to_c_string({str1_arg}); char *_s2 = mb25_to_c_string({str2_arg}); ' \
                       f'int _pos = 0; if (_s1 && _s2 && _start > 0) {{ int _len = strlen(_s1); if (_start <= _len) ' \
                       f'{{ char *_p = strstr(_s1 + _start - 1, _s2); _pos = _p ? (_p - _s1 + 1) : 0; }} }} ' \
                       f'if (_s1) free(_s1); if (_s2) free(_s2); _pos; }})'

        # Math functions - single argument
        elif func_name in ('ABS', 'SGN', 'INT', 'FIX', 'SIN', 'COS', 'TAN', 'ATN', 'EXP', 'LOG', 'SQR'):
            if len(expr.arguments) != 1:
                self.warnings.append(f"{func_name} requires 1 argument")
                return '0'
            arg = self._generate_expression(expr.arguments[0])

            # Map BASIC functions to C functions
            if func_name == 'ABS':
                return f'fabs({arg})'
            elif func_name == 'SGN':
                # SGN returns -1, 0, or 1
                return f'(({arg}) > 0 ? 1 : ({arg}) < 0 ? -1 : 0)'
            elif func_name == 'INT':
                # INT truncates towards negative infinity
                return f'floor({arg})'
            elif func_name == 'FIX':
                # FIX truncates towards zero
                return f'trunc({arg})'
            elif func_name == 'SIN':
                return f'sin({arg})'
            elif func_name == 'COS':
                return f'cos({arg})'
            elif func_name == 'TAN':
                return f'tan({arg})'
            elif func_name == 'ATN':
                return f'atan({arg})'
            elif func_name == 'EXP':
                return f'exp({arg})'
            elif func_name == 'LOG':
                return f'log({arg})'  # Natural log in C
            elif func_name == 'SQR':
                return f'sqrt({arg})'
            else:
                self.warnings.append(f"Function {func_name} not yet implemented")
                return '0'

        # RND function - random number
        elif func_name == 'RND':
            if len(expr.arguments) == 0:
                # RND without arguments - return random [0, 1)
                return '((float)rand() / (float)RAND_MAX)'
            elif len(expr.arguments) == 1:
                # RND(n) - n>0: same sequence, n<0: reseed, n=0: repeat last
                arg = self._generate_expression(expr.arguments[0])
                # Simplified implementation - just return random regardless of arg
                # A full implementation would need to handle seed management
                return f'(({arg}), ((float)rand() / (float)RAND_MAX))'
            else:
                self.warnings.append("RND requires 0 or 1 argument")
                return '0'

        # Type conversion functions
        elif func_name == 'CINT':
            if len(expr.arguments) != 1:
                self.warnings.append("CINT requires 1 argument")
                return '0'
            arg = self._generate_expression(expr.arguments[0])
            return f'((int)round({arg}))'

        elif func_name == 'CSNG':
            if len(expr.arguments) != 1:
                self.warnings.append("CSNG requires 1 argument")
                return '0'
            arg = self._generate_expression(expr.arguments[0])
            return f'((float)({arg}))'

        elif func_name == 'CDBL':
            if len(expr.arguments) != 1:
                self.warnings.append("CDBL requires 1 argument")
                return '0'
            arg = self._generate_expression(expr.arguments[0])
            return f'((double)({arg}))'

        # PEEK function - read memory byte
        elif func_name == 'PEEK':
            if len(expr.arguments) != 1:
                self.warnings.append("PEEK requires 1 argument")
                return '0'
            addr = self._generate_expression(expr.arguments[0])
            # For safety, return 0 in compiled code
            # Real implementation would need memory management
            self.warnings.append("PEEK not fully supported - returns 0")
            return '0'

        # INP function - read I/O port
        elif func_name == 'INP':
            if len(expr.arguments) != 1:
                self.warnings.append("INP requires 1 argument")
                return '0'
            port = self._generate_expression(expr.arguments[0])
            # For safety, return 0 in compiled code
            # Real implementation would need I/O port access
            self.warnings.append("INP not fully supported - returns 0")
            return '0'

        else:
            # Other numeric functions not yet implemented
            self.warnings.append(f"Function {func_name} not yet implemented")
            return '0'

    def _get_string_id(self, var_name: str) -> str:
        """Get the string ID for a variable"""
        upper_name = var_name.upper()
        if upper_name in self.string_ids:
            return f'STR_{self._mangle_string_name(upper_name)}'
        else:
            self.warnings.append(f"Unknown string variable: {var_name}")
            return '0'

    def _get_temp_string_id(self) -> str:
        """Allocate a temporary string ID"""
        # Reuse temporaries within a statement
        base_temp = self.string_ids.get('_TEMP_BASE', 0)
        # Use modulo to wrap around and reuse temps
        temp_offset = (self.next_temp_id - base_temp) % self.max_temps_per_statement
        temp_id = base_temp + temp_offset
        self.next_temp_id += 1
        return str(temp_id)

    def _reset_temp_strings(self):
        """Reset temporary string allocation for next statement"""
        self.next_temp_id = self.string_ids.get('_TEMP_BASE', 0)

    def _escape_string(self, s: str) -> str:
        """Escape a string for C"""
        # Basic escaping for C strings
        s = s.replace('\\', '\\\\')
        s = s.replace('"', '\\"')
        s = s.replace('\n', '\\n')
        s = s.replace('\r', '\\r')
        s = s.replace('\t', '\\t')
        return s

    def _generate_string_function_statement(self, expr: FunctionCallNode, result_id: str) -> str:
        """Generate code for string function directly into result variable"""
        func_name = expr.name.upper()

        if func_name == 'LEFT':
            if len(expr.arguments) != 2:
                self.warnings.append("LEFT$ requires 2 arguments")
                return '/* LEFT$ error */'
            str_arg = self._get_string_var_id(expr.arguments[0])
            len_arg = self._generate_expression(expr.arguments[1])
            return f'mb25_string_left({result_id}, {str_arg}, {len_arg})'

        elif func_name == 'RIGHT':
            if len(expr.arguments) != 2:
                self.warnings.append("RIGHT$ requires 2 arguments")
                return '/* RIGHT$ error */'
            str_arg = self._get_string_var_id(expr.arguments[0])
            len_arg = self._generate_expression(expr.arguments[1])
            return f'mb25_string_right({result_id}, {str_arg}, {len_arg})'

        elif func_name == 'MID':
            if len(expr.arguments) < 2 or len(expr.arguments) > 3:
                self.warnings.append("MID$ requires 2 or 3 arguments")
                return '/* MID$ error */'
            str_arg = self._get_string_var_id(expr.arguments[0])
            start_arg = self._generate_expression(expr.arguments[1])
            if len(expr.arguments) == 3:
                len_arg = self._generate_expression(expr.arguments[2])
                return f'mb25_string_mid({result_id}, {str_arg}, {start_arg}, {len_arg})'
            else:
                return f'mb25_string_mid({result_id}, {str_arg}, {start_arg}, 255)'

        elif func_name == 'CHR':
            if len(expr.arguments) != 1:
                self.warnings.append("CHR$ requires 1 argument")
                return '/* CHR$ error */'
            code_arg = self._generate_expression(expr.arguments[0])
            return f'{{ char _chr[2] = {{(char){code_arg}, \'\\0\'}}; mb25_string_alloc_init({result_id}, _chr); }}'

        elif func_name == 'STR':
            if len(expr.arguments) != 1:
                self.warnings.append("STR$ requires 1 argument")
                return '/* STR$ error */'
            num_arg = self._generate_expression(expr.arguments[0])
            return f'{{ char _str[32]; sprintf(_str, "%g", (double){num_arg}); mb25_string_alloc_init({result_id}, _str); }}'

        elif func_name == 'SPACE':
            if len(expr.arguments) != 1:
                self.warnings.append("SPACE$ requires 1 argument")
                return '/* SPACE$ error */'
            count_arg = self._generate_expression(expr.arguments[0])
            return f'{{ int _n = {count_arg}; char *_sp = malloc(_n+1); if(_sp) {{ memset(_sp, \' \', _n); _sp[_n] = \'\\0\'; mb25_string_alloc_init({result_id}, _sp); free(_sp); }} }}'

        elif func_name == 'STRING$':
            if len(expr.arguments) != 2:
                self.warnings.append("STRING$ requires 2 arguments")
                return '/* STRING$ error */'
            count_arg = self._generate_expression(expr.arguments[0])
            # Second arg can be number or string
            if self._get_expression_type(expr.arguments[1]) == VarType.STRING:
                str_arg = self._get_string_var_id(expr.arguments[1])
                return f'{{ int _n = {count_arg}; uint8_t *_data = mb25_get_data({str_arg}); char _ch = (_data && mb25_get_length({str_arg}) > 0) ? _data[0] : \' \'; char *_s = malloc(_n+1); if(_s) {{ memset(_s, _ch, _n); _s[_n] = \'\\0\'; mb25_string_alloc_init({result_id}, _s); free(_s); }} }}'
            else:
                char_arg = self._generate_expression(expr.arguments[1])
                return f'{{ int _n = {count_arg}; char _ch = (char){char_arg}; char *_s = malloc(_n+1); if(_s) {{ memset(_s, _ch, _n); _s[_n] = \'\\0\'; mb25_string_alloc_init({result_id}, _s); free(_s); }} }}'

        elif func_name == 'HEX':
            if len(expr.arguments) != 1:
                self.warnings.append("HEX$ requires 1 argument")
                return '/* HEX$ error */'
            num_arg = self._generate_expression(expr.arguments[0])
            return f'{{ char _hex[17]; sprintf(_hex, "%X", (int){num_arg}); mb25_string_alloc_init({result_id}, _hex); }}'

        elif func_name == 'OCT':
            if len(expr.arguments) != 1:
                self.warnings.append("OCT$ requires 1 argument")
                return '/* OCT$ error */'
            num_arg = self._generate_expression(expr.arguments[0])
            return f'{{ char _oct[23]; sprintf(_oct, "%o", (int){num_arg}); mb25_string_alloc_init({result_id}, _oct); }}'

        else:
            self.warnings.append(f"Unsupported string function: {func_name}")
            return '/* unsupported function */'

    def _get_string_var_id(self, expr) -> str:
        """Get string ID for a variable or expression"""
        if isinstance(expr, VariableNode):
            return self._get_string_id(expr.name)
        else:
            # For complex expressions, need to evaluate into temp
            return self._generate_string_expression(expr)

    def _generate_concat_assignment(self, dest_id: str, expr: BinaryOpNode) -> List[str]:
        """Generate string concatenation assignment step by step"""
        code = []
        self._reset_temp_strings()  # Reset temp allocation

        # Collect all concatenated parts
        parts = []
        self._collect_concat_parts(expr, parts)

        # Generate concatenation steps
        if len(parts) == 2:
            # Simple two-part concat
            left_id = self._get_concat_part_id(parts[0])
            right_id = self._get_concat_part_id(parts[1])
            code.append(self.indent() + f'mb25_string_concat({dest_id}, {left_id}, {right_id});')
        else:
            # Multi-part concatenation - do it step by step
            temp1 = self._get_temp_string_id()
            left_id = self._get_concat_part_id(parts[0])
            right_id = self._get_concat_part_id(parts[1])
            code.append(self.indent() + f'mb25_string_concat({temp1}, {left_id}, {right_id});')

            for i in range(2, len(parts) - 1):
                temp2 = self._get_temp_string_id()
                part_id = self._get_concat_part_id(parts[i])
                code.append(self.indent() + f'mb25_string_concat({temp2}, {temp1}, {part_id});')
                temp1 = temp2

            # Final concat into destination
            last_id = self._get_concat_part_id(parts[-1])
            code.append(self.indent() + f'mb25_string_concat({dest_id}, {temp1}, {last_id});')

        return code

    def _collect_concat_parts(self, expr, parts):
        """Recursively collect all parts of a concatenation"""
        if isinstance(expr, BinaryOpNode) and expr.operator == TokenType.PLUS:
            self._collect_concat_parts(expr.left, parts)
            self._collect_concat_parts(expr.right, parts)
        else:
            parts.append(expr)

    def _get_concat_part_id(self, expr) -> str:
        """Get string ID for a concatenation part"""
        if isinstance(expr, StringNode):
            temp_id = self._get_temp_string_id()
            # Need to allocate the constant first
            return f'(mb25_string_alloc_const({temp_id}, "{self._escape_string(expr.value)}"), {temp_id})'
        elif isinstance(expr, VariableNode):
            return self._get_string_id(expr.name)
        else:
            return self._generate_string_expression(expr)

    def _generate_binary_op(self, expr: BinaryOpNode) -> str:
        """Generate C code for binary operation"""
        left = self._generate_expression(expr.left)
        right = self._generate_expression(expr.right)

        # Map BASIC operators to C operators
        op_map = {
            TokenType.PLUS: '+',
            TokenType.MINUS: '-',
            TokenType.MULTIPLY: '*',
            TokenType.DIVIDE: '/',
            TokenType.POWER: '**',  # Need to handle this specially
            TokenType.EQUAL: '==',
            TokenType.NOT_EQUAL: '!=',
            TokenType.LESS_THAN: '<',
            TokenType.LESS_EQUAL: '<=',
            TokenType.GREATER_THAN: '>',
            TokenType.GREATER_EQUAL: '>=',
            TokenType.AND: '&&',
            TokenType.OR: '||',
        }

        c_op = op_map.get(expr.operator, '?')

        # Special handling for power operator (not in C)
        if expr.operator == TokenType.POWER:
            # Use pow() function from math.h
            return f'pow({left}, {right})'

        return f'({left} {c_op} {right})'

    def _generate_unary_op(self, expr: UnaryOpNode) -> str:
        """Generate C code for unary operation"""
        operand = self._generate_expression(expr.operand)

        if expr.operator == TokenType.MINUS:
            return f'(-{operand})'
        elif expr.operator == TokenType.PLUS:
            return f'(+{operand})'
        elif expr.operator == TokenType.NOT:
            # In BASIC, NOT is bitwise. In C conditions, use logical not
            # For compatibility, we'll use bitwise NOT (~) but in conditions it will work as logical
            return f'(!{operand})'
        else:
            return operand
