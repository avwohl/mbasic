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

    def __init__(self, symbols: SymbolTable, config: Optional[Dict[str, Any]] = None):
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

        # File I/O support
        self.max_file_number = 0  # Track highest file number used

        # Binary data conversion helpers needed
        self.needs_mki_helper = False
        self.needs_mks_helper = False
        self.needs_mkd_helper = False
        self.needs_cvi_helper = False
        self.needs_cvs_helper = False
        self.needs_cvd_helper = False

        # Error handling support
        self.needs_error_handling = False
        self.error_handler_line = 0  # Line to jump to on error (0 = no handler)

        # Memory configuration (can be overridden via config)
        self.config = config or {}
        # CP/M: Stack pointer is AUTO-DETECTED by z88dk from BDOS entry (at 0x0006)
        # We only configure stack SIZE and heap SIZE
        # Note: String pool is malloc'd FROM heap, so heap must be >= pool + overhead
        self.stack_size = self.config.get('stack_size', 512)  # GOSUB/function call stack
        self.string_pool_size = self.config.get('string_pool_size', 2048)  # BASIC string data
        # Heap usage: pool_permanent + GC_temp + C_string_temps + file_I/O_buffers
        #           = pool_size   + pool_size + ~512          + ~512
        #           = 2 * pool_size + 1024
        default_heap = max(self.string_pool_size * 2 + 1024, 1024)
        self.heap_size = self.config.get('heap_size', default_heap)

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

        # Include mb25_string.c if we use strings
        cmd = ['/usr/bin/env', 'z88dk.zcc', '+cpm']

        # Add source files
        cmd.append(source_file)

        # Include mb25_string.c if we have strings
        if self.string_count > 0:
            import os
            # Look for mb25_string.c in the same directory as the source file
            source_dir = os.path.dirname(source_file) or '.'
            mb25_path = os.path.join(source_dir, 'mb25_string.c')
            mb25_include_dir = None
            if os.path.exists(mb25_path):
                cmd.append(mb25_path)
                mb25_include_dir = source_dir
            else:
                # Also try test_compile subdirectory (for development)
                mb25_path_alt = os.path.join('test_compile', 'mb25_string.c')
                if os.path.exists(mb25_path_alt):
                    cmd.append(mb25_path_alt)
                    mb25_include_dir = 'test_compile'

            # Add include directory for mb25_string.h
            if mb25_include_dir and mb25_include_dir != '.':
                cmd.extend(['-I' + mb25_include_dir])

        # Add compiler flags
        cmd.extend(['-create-app', '-lm', '-o', output_file])

        return cmd

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

        # Collect file I/O usage
        self._collect_file_usage(program)

        # Collect binary data function usage
        self._collect_binary_function_usage(program)

        # Collect error handling usage
        self._collect_error_handling(program)

        code = []

        # Header
        code.append('/* Generated by MBASIC-2025 compiler */')
        code.append('/* Target: CP/M via z88dk */')
        code.append('')
        code.append('/* Memory configuration */')
        code.append(f'/* Stack pointer auto-detected by z88dk from BDOS (address 0x0006) */')
        code.append(f'#pragma output CRT_STACK_SIZE = {self.stack_size}')
        code.append(f'#pragma output CLIB_MALLOC_HEAP_SIZE = {self.heap_size}')
        code.append('')

        # String system defines and includes
        if self.string_count > 0:
            code.append(f'#define MB25_NUM_STRINGS {self.string_count}')
            code.append(f'#define MB25_POOL_SIZE {self.string_pool_size}  /* String pool size */')
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
        code.append('#include <stdint.h>')
        if self.needs_error_handling:
            code.append('#include <setjmp.h>')
        code.append('')

        # Generate binary data conversion helper functions if needed
        if self.needs_mki_helper or self.needs_mks_helper or self.needs_mkd_helper or \
           self.needs_cvi_helper or self.needs_cvs_helper or self.needs_cvd_helper:
            code.append('/* Binary data conversion helper functions */')

            if self.needs_mki_helper:
                code.append('int mb25_mki(int str_id, int value) {')
                code.append('    int16_t i = (int16_t)value;')
                code.append('    mb25_string_assign(str_id, (uint8_t*)&i, 2);')
                code.append('    return str_id;')
                code.append('}')
                code.append('')

            if self.needs_mks_helper:
                code.append('int mb25_mks(int str_id, float value) {')
                code.append('    float f = value;')
                code.append('    mb25_string_assign(str_id, (uint8_t*)&f, 4);')
                code.append('    return str_id;')
                code.append('}')
                code.append('')

            if self.needs_mkd_helper:
                code.append('int mb25_mkd(int str_id, double value) {')
                code.append('    double d = value;')
                code.append('    mb25_string_assign(str_id, (uint8_t*)&d, 8);')
                code.append('    return str_id;')
                code.append('}')
                code.append('')

            if self.needs_cvi_helper:
                code.append('int mb25_cvi(int str_id) {')
                code.append('    uint8_t *data = mb25_get_data(str_id);')
                code.append('    if (data && mb25_get_length(str_id) >= 2) {')
                code.append('        return *(int16_t*)data;')
                code.append('    }')
                code.append('    return 0;')
                code.append('}')
                code.append('')

            if self.needs_cvs_helper:
                code.append('float mb25_cvs(int str_id) {')
                code.append('    uint8_t *data = mb25_get_data(str_id);')
                code.append('    if (data && mb25_get_length(str_id) >= 4) {')
                code.append('        return *(float*)data;')
                code.append('    }')
                code.append('    return 0.0f;')
                code.append('}')
                code.append('')

            if self.needs_cvd_helper:
                code.append('double mb25_cvd(int str_id) {')
                code.append('    uint8_t *data = mb25_get_data(str_id);')
                code.append('    if (data && mb25_get_length(str_id) >= 8) {')
                code.append('        return *(double*)data;')
                code.append('    }')
                code.append('    return 0.0;')
                code.append('}')
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

        # Error handling support
        if self.needs_error_handling:
            code.append(self.indent() + '/* Error handling support */')
            code.append(self.indent() + 'int basic_err = 0;  /* Current error code (ERR) */')
            code.append(self.indent() + 'int basic_erl = 0;  /* Error line number (ERL) */')
            code.append(self.indent() + 'int error_handler = 0;  /* Line number of error handler (0 = disabled) */')
            code.append(self.indent() + 'int error_resume_line = 0;  /* Line to resume after error */')
            code.append(self.indent() + 'jmp_buf error_jmp;  /* Jump buffer for error handling */')
            code.append('')

        # File I/O support
        if self.max_file_number > 0:
            code.append(self.indent() + '/* File I/O support */')
            code.append(self.indent() + f'FILE *file_handles[{self.max_file_number + 1}];  /* File handles indexed by file number */')
            code.append(self.indent() + f'char file_modes[{self.max_file_number + 1}];  /* File modes: I=input, O=output, R=random, A=append */')
            # Initialize all file handles to NULL
            code.append(self.indent() + 'int _i;')
            code.append(self.indent() + f'for (_i = 0; _i <= {self.max_file_number}; _i++) {{')
            self.indent_level += 1
            code.append(self.indent() + 'file_handles[_i] = NULL;')
            code.append(self.indent() + 'file_modes[_i] = 0;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

        # Generate DATA array if we have DATA statements
        if self.data_values:
            code.extend(self._generate_data_array())
            code.append('')

        # Setup error handling if needed
        if self.needs_error_handling:
            code.append(self.indent() + '/* Setup error handling */')
            code.append(self.indent() + 'if (setjmp(error_jmp) != 0) {')
            self.indent_level += 1
            code.append(self.indent() + '/* Jump here on error */')
            code.append(self.indent() + 'if (error_handler > 0) {')
            self.indent_level += 1
            code.append(self.indent() + 'goto handle_error;')
            self.indent_level -= 1
            code.append(self.indent() + '} else {')
            self.indent_level += 1
            code.append(self.indent() + 'fprintf(stderr, "?Error %d in line %d\\n", basic_err, basic_erl);')
            code.append(self.indent() + 'goto program_end;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

        # Generate code for each line
        for line_node in program.lines:
            code.extend(self._generate_line(line_node))

        # Add error handler jump point if needed
        if self.needs_error_handling:
            code.append('')
            code.append('handle_error:')
            code.append(self.indent() + '/* Jump to error handler line */')
            code.append(self.indent() + 'switch(error_handler) {')
            self.indent_level += 1
            # Collect all ON ERROR GOTO lines
            for line_node in program.lines:
                for stmt in line_node.statements:
                    if isinstance(stmt, OnErrorStatementNode) and stmt.line_number > 0:
                        code.append(self.indent() + f'case {stmt.line_number}: goto line_{stmt.line_number};')
            code.append(self.indent() + 'default: fprintf(stderr, "?Invalid error handler\\n"); goto program_end;')
            self.indent_level -= 1
            code.append(self.indent() + '}')

        # End main
        code.append('')
        code.append('program_end:')

        # Cleanup string system if needed
        if self.string_count > 0:
            code.append('    mb25_cleanup();')

        code.append('    return 0;')
        self.indent_level -= 1
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

    def _collect_file_usage(self, program: ProgramNode):
        """Collect maximum file number used for file I/O array"""
        self.max_file_number = 0
        for line_node in program.lines:
            for stmt in line_node.statements:
                # Check OPEN statements
                if isinstance(stmt, OpenStatementNode):
                    # For now, assume file numbers are constants
                    if isinstance(stmt.file_number, NumberNode):
                        file_num = int(stmt.file_number.value)
                        self.max_file_number = max(self.max_file_number, file_num)
                    else:
                        # If not constant, default to supporting up to 10 files
                        self.max_file_number = max(self.max_file_number, 10)
                # Check CLOSE, INPUT#, PRINT#, etc.
                elif hasattr(stmt, 'file_number') and stmt.file_number:
                    if isinstance(stmt.file_number, NumberNode):
                        file_num = int(stmt.file_number.value)
                        self.max_file_number = max(self.max_file_number, file_num)

    def _collect_binary_function_usage(self, program: ProgramNode):
        """Collect usage of binary data conversion functions to determine which helpers are needed"""
        for line_node in program.lines:
            for stmt in line_node.statements:
                self._check_binary_function_in_statement(stmt)

    def _check_binary_function_in_statement(self, stmt):
        """Recursively check for binary function usage in a statement"""
        if isinstance(stmt, LetStatementNode):
            self._check_binary_function_in_expression(stmt.expression)
        elif isinstance(stmt, PrintStatementNode):
            if hasattr(stmt, 'expressions'):
                for expr in stmt.expressions:
                    self._check_binary_function_in_expression(expr)
        elif isinstance(stmt, IfStatementNode):
            self._check_binary_function_in_expression(stmt.condition)
            if stmt.then_statements:
                for s in stmt.then_statements:
                    self._check_binary_function_in_statement(s)
            if stmt.else_statements:
                for s in stmt.else_statements:
                    self._check_binary_function_in_statement(s)
        # Add more statement types as needed

    def _check_binary_function_in_expression(self, expr):
        """Recursively check for binary function usage in an expression"""
        if isinstance(expr, FunctionCallNode):
            func_name = expr.name.upper()
            if func_name == 'MKI':
                self.needs_mki_helper = True
            elif func_name == 'MKS':
                self.needs_mks_helper = True
            elif func_name == 'MKD':
                self.needs_mkd_helper = True
            elif func_name == 'CVI':
                self.needs_cvi_helper = True
            elif func_name == 'CVS':
                self.needs_cvs_helper = True
            elif func_name == 'CVD':
                self.needs_cvd_helper = True
            # Check arguments recursively
            if hasattr(expr, 'arguments'):
                for arg in expr.arguments:
                    self._check_binary_function_in_expression(arg)
        elif isinstance(expr, BinaryOpNode):
            self._check_binary_function_in_expression(expr.left)
            self._check_binary_function_in_expression(expr.right)
        elif isinstance(expr, UnaryOpNode):
            self._check_binary_function_in_expression(expr.operand)
        # Add more expression types as needed

    def _collect_error_handling(self, program: ProgramNode):
        """Collect error handling usage"""
        for line_node in program.lines:
            for stmt in line_node.statements:
                if isinstance(stmt, OnErrorStatementNode):
                    self.needs_error_handling = True
                    # Track the initial error handler line
                    if self.error_handler_line == 0 and stmt.line_number > 0:
                        self.error_handler_line = stmt.line_number
                elif isinstance(stmt, ResumeStatementNode):
                    self.needs_error_handling = True
                elif isinstance(stmt, ErrorStatementNode):
                    self.needs_error_handling = True

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
        elif isinstance(stmt, OpenStatementNode):
            return self._generate_open(stmt)
        elif isinstance(stmt, CloseStatementNode):
            return self._generate_close(stmt)
        elif isinstance(stmt, LineInputStatementNode):
            return self._generate_line_input(stmt)
        elif isinstance(stmt, WriteStatementNode):
            return self._generate_write(stmt)
        elif isinstance(stmt, KillStatementNode):
            return self._generate_kill(stmt)
        elif isinstance(stmt, PrintUsingStatementNode):
            return self._generate_print_using(stmt)
        elif isinstance(stmt, ClsStatementNode):
            return self._generate_cls(stmt)
        elif isinstance(stmt, MidAssignmentStatementNode):
            return self._generate_mid_assignment(stmt)
        elif isinstance(stmt, OnErrorStatementNode):
            return self._generate_on_error(stmt)
        elif isinstance(stmt, ResumeStatementNode):
            return self._generate_resume(stmt)
        elif isinstance(stmt, ErrorStatementNode):
            return self._generate_error(stmt)
        elif isinstance(stmt, FieldStatementNode):
            return self._generate_field(stmt)
        elif isinstance(stmt, GetStatementNode):
            return self._generate_get(stmt)
        elif isinstance(stmt, PutStatementNode):
            return self._generate_put(stmt)
        elif isinstance(stmt, LsetStatementNode):
            return self._generate_lset(stmt)
        elif isinstance(stmt, RsetStatementNode):
            return self._generate_rset(stmt)
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
                                    'INPUT$', 'MKI', 'MKS', 'MKD'):
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

        # Determine output stream
        if stmt.file_number:
            # PRINT# to file
            file_num_expr = self._generate_expression(stmt.file_number)
            self.max_file_number = max(self.max_file_number, 255)  # Assume max 255 files
            file_ptr = f'file_handles[(int)({file_num_expr})]'

            # Check if file is open
            code.append(self.indent() + f'if ({file_ptr} == NULL) {{')
            self.indent_level += 1
            code.append(self.indent() + f'fprintf(stderr, "?File not open\\n");')
            code.append(self.indent() + 'return 1;')
            self.indent_level -= 1
            code.append(self.indent() + '}')

            # Use fprintf for file output
            output_func = 'fprintf'
            output_stream = file_ptr + ', '
        else:
            # Regular PRINT to stdout
            output_func = 'printf'
            output_stream = ''

        # Print each expression with appropriate format
        for i, expr in enumerate(stmt.expressions):
            separator = stmt.separators[i] if i < len(stmt.separators) else None

            # Check for special TAB() and SPC() functions first
            if isinstance(expr, FunctionCallNode):
                func_name = expr.name.upper()
                if func_name == 'TAB':
                    # TAB(n) - move to column n
                    if len(expr.arguments) != 1:
                        self.warnings.append("TAB requires 1 argument")
                    else:
                        tab_col = self._generate_expression(expr.arguments[0])
                        code.append(self.indent() + '{')
                        self.indent_level += 1
                        code.append(self.indent() + f'int _tab = (int)({tab_col});')
                        code.append(self.indent() + '/* TAB to column - simplified */')
                        code.append(self.indent() + 'for (int _i = 0; _i < _tab; _i++) {')
                        self.indent_level += 1
                        code.append(self.indent() + f'{output_func}({output_stream}" ");')
                        self.indent_level -= 1
                        code.append(self.indent() + '}')
                        self.indent_level -= 1
                        code.append(self.indent() + '}')
                    continue  # Skip normal expression handling
                elif func_name == 'SPC':
                    # SPC(n) - output n spaces
                    if len(expr.arguments) != 1:
                        self.warnings.append("SPC requires 1 argument")
                    else:
                        spc_count = self._generate_expression(expr.arguments[0])
                        code.append(self.indent() + '{')
                        self.indent_level += 1
                        code.append(self.indent() + f'int _spc = (int)({spc_count});')
                        code.append(self.indent() + 'for (int _i = 0; _i < _spc; _i++) {')
                        self.indent_level += 1
                        code.append(self.indent() + f'{output_func}({output_stream}" ");')
                        self.indent_level -= 1
                        code.append(self.indent() + '}')
                        self.indent_level -= 1
                        code.append(self.indent() + '}')
                    continue  # Skip normal expression handling

            # Determine format based on expression type
            expr_type = self._get_expression_type(expr)

            if expr_type == VarType.STRING:
                # For strings, need to convert to C string
                # Special handling for string literals
                if isinstance(expr, StringNode):
                    # Generate allocation separately for string literals
                    temp_id = self._get_temp_string_id()
                    code.append(self.indent() + '{')
                    self.indent_level += 1
                    code.append(self.indent() + f'mb25_string_alloc_const({temp_id}, "{self._escape_string(expr.value)}");')
                    code.append(self.indent() + f'char *temp_str = mb25_to_c_string({temp_id});')
                else:
                    # For variables and expressions, use existing generation
                    str_expr = self._generate_string_expression(expr)
                    code.append(self.indent() + '{')
                    self.indent_level += 1
                    code.append(self.indent() + f'char *temp_str = mb25_to_c_string({str_expr});')
                code.append(self.indent() + 'if (temp_str) {')
                self.indent_level += 1

                if separator == ';':
                    code.append(self.indent() + f'{output_func}({output_stream}"%s", temp_str);')
                elif separator == ',':
                    code.append(self.indent() + f'{output_func}({output_stream}"%s ", temp_str);')
                else:
                    # Use CRLF for CP/M compatibility
                    if stmt.file_number:
                        code.append(self.indent() + f'{output_func}({output_stream}"%s\\r\\n", temp_str);')
                    else:
                        code.append(self.indent() + f'{output_func}({output_stream}"%s\\n", temp_str);')

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
                    code.append(self.indent() + f'{output_func}({output_stream}"{fmt}", {c_expr});')
                elif separator == ',':
                    code.append(self.indent() + f'{output_func}({output_stream}"{fmt} ", {c_expr});')
                else:
                    # Use CRLF for CP/M compatibility when writing to files
                    if stmt.file_number:
                        code.append(self.indent() + f'{output_func}({output_stream}"{fmt}\\r\\n", {c_expr});')
                    else:
                        code.append(self.indent() + f'{output_func}({output_stream}"{fmt}\\n", {c_expr});')

        # If no expressions or last separator was ; add newline
        if not stmt.expressions or (stmt.separators and stmt.separators[-1] != ';'):
            if not stmt.expressions:
                if stmt.file_number:
                    file_num_expr = self._generate_expression(stmt.file_number)
                    file_ptr = f'file_handles[(int)({file_num_expr})]'
                    # Use CRLF for CP/M compatibility
                    code.append(self.indent() + f'fprintf({file_ptr}, "\\r\\n");')
                else:
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

        # Determine input stream
        if stmt.file_number:
            # INPUT# from file
            file_num_expr = self._generate_expression(stmt.file_number)
            self.max_file_number = max(self.max_file_number, 255)  # Assume max 255 files
            file_ptr = f'file_handles[(int)({file_num_expr})]'

            # Check if file is open
            code.append(self.indent() + f'if ({file_ptr} == NULL) {{')
            self.indent_level += 1
            code.append(self.indent() + f'fprintf(stderr, "?File not open\\n");')
            code.append(self.indent() + 'return 1;')
            self.indent_level -= 1
            code.append(self.indent() + '}')

            input_stream = file_ptr
        else:
            # Regular INPUT from stdin
            input_stream = 'stdin'

            # Generate prompt (only for keyboard input)
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

        # For file input with multiple variables, read entire line and parse
        if stmt.file_number and len(stmt.variables) > 1:
            # Read entire line first
            code.append(self.indent() + f'if (fgets(input_buffer, 256, {input_stream})) {{')
            self.indent_level += 1
            code.append(self.indent() + 'char *_ptr = input_buffer;')
            code.append(self.indent() + 'char _field[256];')

            # Parse each field from the line
            for i, var_node in enumerate(stmt.variables):
                var_type = self._get_expression_type(var_node)
                code.append(self.indent() + '/* Parse next field */')

                if var_type == VarType.STRING:
                    var_str_id = self._get_string_id(var_node.name)
                    # Handle quoted strings from WRITE#
                    code.append(self.indent() + 'if (*_ptr == \'\\"\') {')
                    self.indent_level += 1
                    code.append(self.indent() + '_ptr++; /* Skip opening quote */')
                    code.append(self.indent() + 'char *_end = strchr(_ptr, \'\\"\');')
                    code.append(self.indent() + 'if (_end) {')
                    self.indent_level += 1
                    code.append(self.indent() + 'int _len = _end - _ptr;')
                    code.append(self.indent() + 'strncpy(_field, _ptr, _len);')
                    code.append(self.indent() + '_field[_len] = \'\\0\';')
                    code.append(self.indent() + f'mb25_string_alloc_init({var_str_id}, _field);')
                    code.append(self.indent() + '_ptr = _end + 1; /* Skip closing quote */')
                    code.append(self.indent() + 'if (*_ptr == \',\') _ptr++; /* Skip comma */')
                    self.indent_level -= 1
                    code.append(self.indent() + '}')
                    self.indent_level -= 1
                    code.append(self.indent() + '} else {')
                    self.indent_level += 1
                    # Unquoted string - read until comma
                    code.append(self.indent() + '{')
                    self.indent_level += 1
                    code.append(self.indent() + 'char *_comma2 = strchr(_ptr, \',\');')
                    code.append(self.indent() + 'if (_comma2) {')
                    self.indent_level += 1
                    code.append(self.indent() + 'int _len = _comma2 - _ptr;')
                    code.append(self.indent() + 'strncpy(_field, _ptr, _len);')
                    code.append(self.indent() + '_field[_len] = \'\\0\';')
                    code.append(self.indent() + f'mb25_string_alloc_init({var_str_id}, _field);')
                    code.append(self.indent() + '_ptr = _comma2 + 1;')
                    self.indent_level -= 1
                    code.append(self.indent() + '} else {')
                    self.indent_level += 1
                    code.append(self.indent() + f'mb25_string_alloc_init({var_str_id}, _ptr);')
                    self.indent_level -= 1
                    code.append(self.indent() + '}')
                    self.indent_level -= 1
                    code.append(self.indent() + '}')
                    self.indent_level -= 1
                    code.append(self.indent() + '}')
                else:
                    # Numeric input
                    var_name = self._mangle_variable_name(var_node.name)
                    code.append(self.indent() + '{')
                    self.indent_level += 1
                    if var_type == VarType.INTEGER:
                        code.append(self.indent() + f'sscanf(_ptr, "%d", &{var_name});')
                    else:
                        code.append(self.indent() + f'sscanf(_ptr, "%f", &{var_name});')
                    # Skip to next comma
                    code.append(self.indent() + 'char *_comma3 = strchr(_ptr, \',\');')
                    code.append(self.indent() + 'if (_comma3) _ptr = _comma3 + 1;')
                    self.indent_level -= 1
                    code.append(self.indent() + '}')

            self.indent_level -= 1
            code.append(self.indent() + '}')
        else:
            # Single variable or keyboard input - use original logic
            for i, var_node in enumerate(stmt.variables):
                var_type = self._get_expression_type(var_node)

                if var_type == VarType.STRING:
                    # String input
                    var_str_id = self._get_string_id(var_node.name)
                    code.append(self.indent() + f'if (fgets(input_buffer, 256, {input_stream})) {{')
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
                        code.append(self.indent() + f'fscanf({input_stream}, "%d", &{var_name});')
                    else:
                        code.append(self.indent() + f'fscanf({input_stream}, "%f", &{var_name});')

                # If there are more variables and it's keyboard input, show another prompt
                if i < len(stmt.variables) - 1 and not stmt.file_number:
                    code.append(self.indent() + 'printf("?? ");  /* Next variable prompt */')

        return code

    def _generate_end(self, stmt: EndStatementNode) -> List[str]:
        """Generate END statement"""
        if self.needs_error_handling or self.string_count > 0:
            # Jump to cleanup code
            return [self.indent() + 'goto program_end;']
        else:
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

    def _generate_open(self, stmt: OpenStatementNode) -> List[str]:
        """Generate OPEN statement

        OPEN mode, #filenum, filename$ [, reclen]
        mode: "I" (input), "O" (output), "R" (random), "A" (append)
        """
        code = []

        # Get file number
        file_num_expr = self._generate_expression(stmt.file_number)

        # Get filename (need to handle string expression)
        if self._get_expression_type(stmt.filename) == VarType.STRING:
            filename_str_id = self._generate_string_expression(stmt.filename)
            # Convert to C string
            code.append(self.indent() + '{')
            self.indent_level += 1
            code.append(self.indent() + f'int _file_num = (int)({file_num_expr});')
            code.append(self.indent() + f'char *_filename = mb25_to_c_string({filename_str_id});')
            code.append(self.indent() + 'if (_filename) {')
            self.indent_level += 1

            # Determine C mode string based on BASIC mode
            c_mode = ''
            if stmt.mode == 'I':
                c_mode = 'r'  # Read
            elif stmt.mode == 'O':
                c_mode = 'w'  # Write (create/truncate)
            elif stmt.mode == 'A':
                c_mode = 'a'  # Append
            elif stmt.mode == 'R':
                c_mode = 'r+b'  # Random access (binary read/write)
            else:
                self.warnings.append(f"Unknown file mode: {stmt.mode}")
                c_mode = 'r'

            # Open the file
            code.append(self.indent() + f'if (_file_num >= 0 && _file_num <= {self.max_file_number}) {{')
            self.indent_level += 1
            code.append(self.indent() + f'file_handles[_file_num] = fopen(_filename, "{c_mode}");')
            code.append(self.indent() + f'file_modes[_file_num] = \'{stmt.mode}\';')
            code.append(self.indent() + 'if (!file_handles[_file_num]) {')
            self.indent_level += 1
            code.append(self.indent() + 'fprintf(stderr, "?File not found\\n");')
            # In a real implementation, should trigger ON ERROR GOTO if set
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')

            code.append(self.indent() + 'free(_filename);')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
        else:
            self.warnings.append("OPEN requires string filename")
            code.append(self.indent() + '/* OPEN error: filename must be string */')

        return code

    def _generate_close(self, stmt: CloseStatementNode) -> List[str]:
        """Generate CLOSE statement

        CLOSE - close all files
        CLOSE #n - close specific file
        CLOSE #n, #m - close multiple files
        """
        code = []

        if not stmt.file_numbers:
            # CLOSE without arguments - close all files
            code.append(self.indent() + '{')
            self.indent_level += 1
            code.append(self.indent() + 'int _i;')
            code.append(self.indent() + f'for (_i = 0; _i <= {self.max_file_number}; _i++) {{')
            self.indent_level += 1
            code.append(self.indent() + 'if (file_handles[_i]) {')
            self.indent_level += 1
            code.append(self.indent() + 'fclose(file_handles[_i]);')
            code.append(self.indent() + 'file_handles[_i] = NULL;')
            code.append(self.indent() + 'file_modes[_i] = 0;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
        else:
            # CLOSE specific files
            for file_num_expr in stmt.file_numbers:
                file_num = self._generate_expression(file_num_expr)
                code.append(self.indent() + '{')
                self.indent_level += 1
                code.append(self.indent() + f'int _file_num = (int)({file_num});')
                code.append(self.indent() + f'if (_file_num >= 0 && _file_num <= {self.max_file_number} && file_handles[_file_num]) {{')
                self.indent_level += 1
                code.append(self.indent() + 'fclose(file_handles[_file_num]);')
                code.append(self.indent() + 'file_handles[_file_num] = NULL;')
                code.append(self.indent() + 'file_modes[_file_num] = 0;')
                self.indent_level -= 1
                code.append(self.indent() + '}')
                self.indent_level -= 1
                code.append(self.indent() + '}')

        return code

    def _generate_line_input(self, stmt: LineInputStatementNode) -> List[str]:
        """Generate LINE INPUT statement - read entire line into string variable"""
        code = []

        # Determine input stream
        if stmt.file_number:
            # LINE INPUT# from file
            file_num_expr = self._generate_expression(stmt.file_number)
            self.max_file_number = max(self.max_file_number, 255)  # Assume max 255 files
            file_ptr = f'file_handles[(int)({file_num_expr})]'

            # Check if file is open
            code.append(self.indent() + f'if ({file_ptr} == NULL) {{')
            self.indent_level += 1
            code.append(self.indent() + f'fprintf(stderr, "?File not open\\n");')
            code.append(self.indent() + 'return 1;')
            self.indent_level -= 1
            code.append(self.indent() + '}')

            input_stream = file_ptr
        else:
            # Regular LINE INPUT from stdin
            input_stream = 'stdin'

            # Generate prompt (only for keyboard input)
            if stmt.prompt:
                # Check if it's a string literal
                if isinstance(stmt.prompt, StringNode):
                    prompt_str = stmt.prompt.value
                else:
                    # For expressions, we'd need to evaluate - not implemented yet
                    prompt_str = ""
                    self.warnings.append("Complex prompt expressions not yet supported")

                code.append(self.indent() + f'printf("{self._escape_string(prompt_str)}");')

        # LINE INPUT always reads a string into a string variable
        var_type = self._get_expression_type(stmt.variable)
        if var_type != VarType.STRING:
            self.warnings.append("LINE INPUT requires a string variable")
            return [self.indent() + '/* LINE INPUT requires a string variable */']

        # String input - read entire line including spaces
        var_str_id = self._get_string_id(stmt.variable.name)
        code.append(self.indent() + f'if (!fgets(input_buffer, 256, {input_stream})) {{')
        self.indent_level += 1
        # If fgets fails, we've hit EOF or an error - set a flag or break
        if stmt.file_number:
            # For file input, just leave the string unchanged and let EOF() handle it
            code.append(self.indent() + '/* EOF reached or read error */')
        else:
            # For keyboard input, set empty string
            code.append(self.indent() + f'mb25_string_alloc_init({var_str_id}, "");')
        self.indent_level -= 1
        code.append(self.indent() + '} else {')
        self.indent_level += 1
        code.append(self.indent() + 'size_t len = strlen(input_buffer);')
        code.append(self.indent() + 'if (len > 0 && input_buffer[len-1] == \'\\n\') {')
        self.indent_level += 1
        code.append(self.indent() + 'input_buffer[len-1] = \'\\0\';')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        # Check for CP/M ^Z EOF marker
        code.append(self.indent() + 'if (len > 0 && input_buffer[0] == 0x1A) {')
        self.indent_level += 1
        code.append(self.indent() + '/* CP/M EOF marker (^Z) detected */')
        code.append(self.indent() + f'mb25_string_alloc_init({var_str_id}, "");')
        if stmt.file_number:
            # Force EOF flag by seeking to end
            code.append(self.indent() + f'fseek({input_stream}, 0, SEEK_END);')
        self.indent_level -= 1
        code.append(self.indent() + '} else {')
        self.indent_level += 1
        code.append(self.indent() + f'mb25_string_alloc_init({var_str_id}, input_buffer);')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        self.indent_level -= 1
        code.append(self.indent() + '}')

        return code

    def _generate_kill(self, stmt: KillStatementNode) -> List[str]:
        """Generate KILL statement - delete file"""
        code = []

        # Generate the filename expression (must be a string)
        if self._get_expression_type(stmt.filename) != VarType.STRING:
            self.warnings.append("KILL requires a string filename")
            return [self.indent() + '/* KILL requires a string filename */']

        filename_str_id = self._generate_string_expression(stmt.filename)

        code.append(self.indent() + '{')
        self.indent_level += 1
        code.append(self.indent() + f'char *_filename = mb25_to_c_string({filename_str_id});')
        code.append(self.indent() + 'if (_filename) {')
        self.indent_level += 1
        code.append(self.indent() + 'if (remove(_filename) != 0) {')
        self.indent_level += 1
        code.append(self.indent() + 'fprintf(stderr, "?File not found\\n");')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent() + 'free(_filename);')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        self.indent_level -= 1
        code.append(self.indent() + '}')

        return code

    def _generate_cls(self, stmt: ClsStatementNode) -> List[str]:
        """Generate CLS statement - clear screen"""
        code = []
        # Use ANSI escape sequence to clear screen and move cursor to home
        # This works on most terminals that support ANSI
        code.append(self.indent() + 'printf("\\033[2J\\033[H");  /* Clear screen */')
        code.append(self.indent() + 'fflush(stdout);  /* Ensure it is displayed */')
        return code

    def _generate_mid_assignment(self, stmt: MidAssignmentStatementNode) -> List[str]:
        """Generate MID$ statement - replace substring in string variable"""
        code = []

        # Get the string variable ID
        if not isinstance(stmt.string_var, VariableNode):
            self.warnings.append("MID$ statement requires a string variable")
            return [self.indent() + '/* MID$ requires string variable */']

        var_str_id = self._get_string_id(stmt.string_var.name)

        # Get the replacement value
        if self._get_expression_type(stmt.value) != VarType.STRING:
            self.warnings.append("MID$ assignment requires string value")
            return [self.indent() + '/* MID$ requires string value */']

        value_str_expr = self._generate_string_expression(stmt.value)

        # Generate start position and length
        start_expr = self._generate_expression(stmt.start)
        length_expr = self._generate_expression(stmt.length)

        code.append(self.indent() + '{')
        self.indent_level += 1

        # Get current string data
        code.append(self.indent() + f'uint8_t *_data = mb25_get_data({var_str_id});')
        code.append(self.indent() + f'uint16_t _len = mb25_get_length({var_str_id});')

        # Get replacement string
        code.append(self.indent() + f'char *_repl = mb25_to_c_string({value_str_expr});')
        code.append(self.indent() + 'if (_data && _repl) {')
        self.indent_level += 1

        code.append(self.indent() + f'int _start = (int)({start_expr}) - 1;  /* Convert to 0-based */')
        code.append(self.indent() + f'int _repllen = (int)({length_expr});')
        code.append(self.indent() + 'int _srclen = strlen(_repl);')

        # Create new string with replacement
        code.append(self.indent() + 'char _temp[256];')
        code.append(self.indent() + 'memcpy(_temp, _data, _len);')
        code.append(self.indent() + '_temp[_len] = \'\\0\';')

        # Replace substring
        code.append(self.indent() + 'if (_start >= 0 && _start < _len) {')
        self.indent_level += 1
        code.append(self.indent() + 'int _copylen = (_srclen < _repllen) ? _srclen : _repllen;')
        code.append(self.indent() + 'if (_start + _copylen > _len) _copylen = _len - _start;')
        code.append(self.indent() + 'memcpy(_temp + _start, _repl, _copylen);')
        self.indent_level -= 1
        code.append(self.indent() + '}')

        # Store back to string variable
        code.append(self.indent() + f'mb25_string_alloc_init({var_str_id}, _temp);')

        code.append(self.indent() + 'free(_repl);')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        self.indent_level -= 1
        code.append(self.indent() + '}')

        return code

    def _generate_print_using(self, stmt: PrintUsingStatementNode) -> List[str]:
        """Generate PRINT USING statement - formatted output"""
        code = []

        # Get format string
        if self._get_expression_type(stmt.format_string) != VarType.STRING:
            self.warnings.append("PRINT USING requires a string format")
            return [self.indent() + '/* PRINT USING requires string format */']

        format_str_expr = self._generate_string_expression(stmt.format_string)

        # Determine output stream
        if stmt.file_number:
            # PRINT# USING to file
            file_num_expr = self._generate_expression(stmt.file_number)
            self.max_file_number = max(self.max_file_number, 255)
            file_ptr = f'file_handles[(int)({file_num_expr})]'

            # Check if file is open
            code.append(self.indent() + f'if ({file_ptr} == NULL) {{')
            self.indent_level += 1
            code.append(self.indent() + f'fprintf(stderr, "?File not open\\n");')
            code.append(self.indent() + 'return 1;')
            self.indent_level -= 1
            code.append(self.indent() + '}')

            output_func = 'fprintf'
            output_stream = file_ptr + ', '
        else:
            # Regular PRINT USING to stdout
            output_func = 'printf'
            output_stream = ''

        # Generate the formatting code
        code.append(self.indent() + '{')
        self.indent_level += 1

        # Get format string as C string
        code.append(self.indent() + f'char *_fmt = mb25_to_c_string({format_str_expr});')
        code.append(self.indent() + 'if (_fmt) {')
        self.indent_level += 1

        code.append(self.indent() + 'char _output[512];  /* Output buffer */')
        code.append(self.indent() + 'char *_out = _output;')
        code.append(self.indent() + 'char *_f = _fmt;  /* Format pointer */')

        # Process each expression with the format
        for i, expr in enumerate(stmt.expressions):
            expr_type = self._get_expression_type(expr)

            code.append(self.indent() + f'/* Format expression {i+1} */')

            if expr_type == VarType.STRING:
                # String expression
                str_expr = self._generate_string_expression(expr)
                code.append(self.indent() + '{')
                self.indent_level += 1
                code.append(self.indent() + f'char *_str = mb25_to_c_string({str_expr});')
                code.append(self.indent() + 'if (_str) {')
                self.indent_level += 1

                # Parse format for strings (!, &, or \...\)
                code.append(self.indent() + 'if (*_f == \'!\') {')
                self.indent_level += 1
                code.append(self.indent() + '/* Single character */')
                code.append(self.indent() + '*_out++ = _str[0] ? _str[0] : \' \';')
                code.append(self.indent() + '_f++;')
                self.indent_level -= 1
                code.append(self.indent() + '} else if (*_f == \'&\') {')
                self.indent_level += 1
                code.append(self.indent() + '/* Entire string */')
                code.append(self.indent() + 'strcpy(_out, _str);')
                code.append(self.indent() + '_out += strlen(_str);')
                code.append(self.indent() + '_f++;')
                self.indent_level -= 1
                code.append(self.indent() + '} else if (*_f == \'\\\\\') {')
                self.indent_level += 1
                code.append(self.indent() + '/* Fixed width field \\....\\ */')
                code.append(self.indent() + 'char *_end = strchr(_f + 1, \'\\\\\');')
                code.append(self.indent() + 'if (_end) {')
                self.indent_level += 1
                code.append(self.indent() + 'int _width = _end - _f + 1;')
                code.append(self.indent() + 'int _len = strlen(_str);')
                code.append(self.indent() + 'if (_len > _width) _len = _width;')
                code.append(self.indent() + 'memcpy(_out, _str, _len);')
                code.append(self.indent() + '_out += _len;')
                code.append(self.indent() + 'while (_len < _width) { *_out++ = \' \'; _len++; }')
                code.append(self.indent() + '_f = _end + 1;')
                self.indent_level -= 1
                code.append(self.indent() + '}')
                self.indent_level -= 1
                code.append(self.indent() + '}')

                code.append(self.indent() + 'free(_str);')
                self.indent_level -= 1
                code.append(self.indent() + '}')
                self.indent_level -= 1
                code.append(self.indent() + '}')
            else:
                # Numeric expression
                value = self._generate_expression(expr)
                code.append(self.indent() + '{')
                self.indent_level += 1
                code.append(self.indent() + f'double _val = (double)({value});')

                # Parse numeric format
                code.append(self.indent() + '/* Parse numeric format */')
                code.append(self.indent() + 'int _digits = 0, _decimals = -1;')
                code.append(self.indent() + 'int _has_comma = 0, _has_dollar = 0;')
                code.append(self.indent() + 'char *_fmt_start = _f;')

                # Count format specifiers
                code.append(self.indent() + 'while (*_f) {')
                self.indent_level += 1
                code.append(self.indent() + 'if (*_f == \'#\') _digits++;')
                code.append(self.indent() + 'else if (*_f == \'.\') _decimals = 0;')
                code.append(self.indent() + 'else if (*_f == \',\' && _decimals < 0) _has_comma = 1;')
                code.append(self.indent() + 'else if (*_f == \'$\') _has_dollar = 1;')
                code.append(self.indent() + 'else if (*_f != \'#\' && *_f != \'.\' && *_f != \',\') break;')
                code.append(self.indent() + 'if (_decimals >= 0 && *_f == \'#\') _decimals++;')
                code.append(self.indent() + '_f++;')
                self.indent_level -= 1
                code.append(self.indent() + '}')

                # Format the number
                code.append(self.indent() + 'if (_has_dollar) *_out++ = \'$\';')
                code.append(self.indent() + 'if (_decimals >= 0) {')
                self.indent_level += 1
                code.append(self.indent() + 'sprintf(_out, "%.*f", _decimals, _val);')
                self.indent_level -= 1
                code.append(self.indent() + '} else {')
                self.indent_level += 1
                code.append(self.indent() + 'sprintf(_out, "%.0f", _val);')
                self.indent_level -= 1
                code.append(self.indent() + '}')

                # Add commas if requested
                code.append(self.indent() + 'if (_has_comma) {')
                self.indent_level += 1
                code.append(self.indent() + '/* Add comma separators - simplified */')
                self.indent_level -= 1
                code.append(self.indent() + '}')

                code.append(self.indent() + '_out += strlen(_out);')
                self.indent_level -= 1
                code.append(self.indent() + '}')

            # Add space between values
            if i < len(stmt.expressions) - 1:
                code.append(self.indent() + '*_out++ = \' \';')

        code.append(self.indent() + '*_out = \'\\0\';  /* Null terminate */')

        # Output the formatted string
        if stmt.file_number:
            code.append(self.indent() + f'{output_func}({output_stream}"%s\\r\\n", _output);')
        else:
            code.append(self.indent() + f'{output_func}({output_stream}"%s\\n", _output);')

        code.append(self.indent() + 'free(_fmt);')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        self.indent_level -= 1
        code.append(self.indent() + '}')

        return code

    def _generate_write(self, stmt: WriteStatementNode) -> List[str]:
        """Generate WRITE statement - output with comma delimiters and quotes for strings"""
        code = []

        # Determine output stream
        if stmt.file_number:
            # WRITE# to file
            file_num_expr = self._generate_expression(stmt.file_number)
            self.max_file_number = max(self.max_file_number, 255)  # Assume max 255 files
            file_ptr = f'file_handles[(int)({file_num_expr})]'

            # Check if file is open
            code.append(self.indent() + f'if ({file_ptr} == NULL) {{')
            self.indent_level += 1
            code.append(self.indent() + f'fprintf(stderr, "?File not open\\n");')
            code.append(self.indent() + 'return 1;')
            self.indent_level -= 1
            code.append(self.indent() + '}')

            # Use fprintf for file output
            output_func = 'fprintf'
            output_stream = file_ptr + ', '
        else:
            # Regular WRITE to stdout
            output_func = 'printf'
            output_stream = ''

        # WRITE outputs each expression with proper formatting
        for i, expr in enumerate(stmt.expressions):
            # Add comma separator if not the first item
            if i > 0:
                code.append(self.indent() + f'{output_func}({output_stream}",");')

            # Determine format based on expression type
            expr_type = self._get_expression_type(expr)

            if expr_type == VarType.STRING:
                # For strings, output with quotes
                str_expr = self._generate_string_expression(expr)
                code.append(self.indent() + '{')
                self.indent_level += 1
                code.append(self.indent() + f'char *temp_str = mb25_to_c_string({str_expr});')
                code.append(self.indent() + 'if (temp_str) {')
                self.indent_level += 1
                # WRITE outputs strings with quotes
                code.append(self.indent() + f'{output_func}({output_stream}"\\"%s\\"", temp_str);')
                code.append(self.indent() + 'free(temp_str);')
                self.indent_level -= 1
                code.append(self.indent() + '}')
                self.indent_level -= 1
                code.append(self.indent() + '}')
            else:
                # Numeric expression - no quotes
                expr_type = self._get_expression_type(expr)
                format_spec = self._get_format_specifier(expr_type)
                value = self._generate_expression(expr)
                code.append(self.indent() + f'{output_func}({output_stream}"{format_spec}", {value});')

        # WRITE always ends with a newline (CRLF for files, LF for console)
        if stmt.file_number:
            code.append(self.indent() + f'{output_func}({output_stream}"\\r\\n");')
        else:
            code.append(self.indent() + f'{output_func}({output_stream}"\\n");')

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
                # Check for special built-in variables
                var_upper = expr.name.upper()
                if var_upper == 'ERR':
                    self.needs_error_handling = True
                    return 'basic_err'
                elif var_upper == 'ERL':
                    self.needs_error_handling = True
                    return 'basic_erl'
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
            # String literal - allocate as constant and return the ID
            temp_id = self._get_temp_string_id()
            # mb25_string_alloc_const allocates the string but returns error code
            # We need to call it and then use the string ID
            return f'(mb25_string_alloc_const({temp_id}, "{self._escape_string(expr.value)}"), {temp_id})'
        elif isinstance(expr, VariableNode):
            # String variable reference
            return str(self._get_string_id(expr.name))
        elif isinstance(expr, BinaryOpNode) and expr.operator == TokenType.PLUS:
            # String concatenation - need to generate inline concat and return result ID
            left_str = self._generate_string_expression(expr.left)
            right_str = self._generate_string_expression(expr.right)
            result_id = self._get_temp_string_id()
            # Generate inline concat expression and return the result ID
            return f'(mb25_string_concat({result_id}, {left_str}, {right_str}), {result_id})'
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
            return f'(mb25_string_left({result_id}, {str_arg}, {len_arg}), {result_id})'

        elif func_name == 'RIGHT':
            if len(expr.arguments) != 2:
                self.warnings.append("RIGHT$ requires 2 arguments")
                return '0'
            str_arg = self._generate_string_expression(expr.arguments[0])
            len_arg = self._generate_expression(expr.arguments[1])
            return f'(mb25_string_right({result_id}, {str_arg}, {len_arg}), {result_id})'

        elif func_name == 'MID':
            if len(expr.arguments) < 2 or len(expr.arguments) > 3:
                self.warnings.append("MID$ requires 2 or 3 arguments")
                return '0'
            str_arg = self._generate_string_expression(expr.arguments[0])
            start_arg = self._generate_expression(expr.arguments[1])
            if len(expr.arguments) == 3:
                len_arg = self._generate_expression(expr.arguments[2])
                return f'(mb25_string_mid({result_id}, {str_arg}, {start_arg}, {len_arg}), {result_id})'
            else:
                # MID$ without length - to end of string
                return f'(mb25_string_mid({result_id}, {str_arg}, {start_arg}, 255), {result_id})'

        elif func_name == 'CHR':
            if len(expr.arguments) != 1:
                self.warnings.append("CHR$ requires 1 argument")
                return '0'
            code_arg = self._generate_expression(expr.arguments[0])
            # Create a single-character string
            return f'({{ char _chr[2] = {{(char){code_arg}, \'\\0\'}}; mb25_string_alloc_init({result_id}, _chr); }}, {result_id})'

        elif func_name == 'STR':
            if len(expr.arguments) != 1:
                self.warnings.append("STR$ requires 1 argument")
                return '0'
            num_arg = self._generate_expression(expr.arguments[0])
            # Convert number to string
            return f'({{ char _str[32]; sprintf(_str, "%g", (double){num_arg}); mb25_string_alloc_init({result_id}, _str); }}, {result_id})'

        elif func_name == 'SPACE':
            if len(expr.arguments) != 1:
                self.warnings.append("SPACE$ requires 1 argument")
                return '0'
            count_arg = self._generate_expression(expr.arguments[0])
            # Create string of spaces
            return f'({{ int _n = {count_arg}; char *_sp = malloc(_n+1); if(_sp) {{ memset(_sp, \' \', _n); _sp[_n] = \'\\0\'; mb25_string_alloc_init({result_id}, _sp); free(_sp); }} }}, {result_id})'

        elif func_name == 'STRING$':
            if len(expr.arguments) != 2:
                self.warnings.append("STRING$ requires 2 arguments")
                return '0'
            count_arg = self._generate_expression(expr.arguments[0])
            # Second arg can be either a number (ASCII code) or string (use first char)
            if self._get_expression_type(expr.arguments[1]) == VarType.STRING:
                str_arg = self._generate_string_expression(expr.arguments[1])
                return f'({{ int _n = {count_arg}; uint8_t *_data = mb25_get_data({str_arg}); char _ch = (_data && mb25_get_length({str_arg}) > 0) ? _data[0] : \' \'; char *_s = malloc(_n+1); if(_s) {{ memset(_s, _ch, _n); _s[_n] = \'\\0\'; mb25_string_alloc_init({result_id}, _s); free(_s); }} }}, {result_id})'
            else:
                char_arg = self._generate_expression(expr.arguments[1])
                return f'({{ int _n = {count_arg}; char _ch = (char){char_arg}; char *_s = malloc(_n+1); if(_s) {{ memset(_s, _ch, _n); _s[_n] = \'\\0\'; mb25_string_alloc_init({result_id}, _s); free(_s); }} }}, {result_id})'

        elif func_name == 'HEX':
            if len(expr.arguments) != 1:
                self.warnings.append("HEX$ requires 1 argument")
                return '0'
            num_arg = self._generate_expression(expr.arguments[0])
            # Convert number to hex string
            return f'({{ char _hex[17]; sprintf(_hex, "%X", (int){num_arg}); mb25_string_alloc_init({result_id}, _hex); }}, {result_id})'

        elif func_name == 'OCT':
            if len(expr.arguments) != 1:
                self.warnings.append("OCT$ requires 1 argument")
                return '0'
            num_arg = self._generate_expression(expr.arguments[0])
            # Convert number to octal string
            return f'({{ char _oct[23]; sprintf(_oct, "%o", (int){num_arg}); mb25_string_alloc_init({result_id}, _oct); }}, {result_id})'

        elif func_name == 'INKEY' or func_name == 'INKEY$':
            # INKEY$ reads a key without waiting (non-blocking)
            # For compiled code, this is runtime-specific
            self.warnings.append("INKEY$ requires runtime support - returning empty string")
            return f'(mb25_string_alloc_init({result_id}, ""), {result_id})'

        elif func_name == 'MKI$' or func_name == 'MKI':
            # Convert integer to 2-byte string
            if len(expr.arguments) != 1:
                self.warnings.append("MKI$ requires 1 argument")
                return '0'
            num_arg = self._generate_expression(expr.arguments[0])
            # Generate helper function call for z88dk compatibility
            self.needs_mki_helper = True
            return f'mb25_mki({result_id}, {num_arg})'

        elif func_name == 'MKS$' or func_name == 'MKS':
            # Convert single to 4-byte string
            if len(expr.arguments) != 1:
                self.warnings.append("MKS$ requires 1 argument")
                return '0'
            num_arg = self._generate_expression(expr.arguments[0])
            # Generate helper function call for z88dk compatibility
            self.needs_mks_helper = True
            return f'mb25_mks({result_id}, {num_arg})'

        elif func_name == 'MKD$' or func_name == 'MKD':
            # Convert double to 8-byte string
            if len(expr.arguments) != 1:
                self.warnings.append("MKD$ requires 1 argument")
                return '0'
            num_arg = self._generate_expression(expr.arguments[0])
            # Generate helper function call for z88dk compatibility
            self.needs_mkd_helper = True
            return f'mb25_mkd({result_id}, {num_arg})'

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

        # Error handling functions
        elif func_name == 'ERR':
            # ERR returns current error code
            if len(expr.arguments) != 0:
                self.warnings.append("ERR takes no arguments")
                return '0'
            self.needs_error_handling = True
            return 'basic_err'

        elif func_name == 'ERL':
            # ERL returns error line number
            if len(expr.arguments) != 0:
                self.warnings.append("ERL takes no arguments")
                return '0'
            self.needs_error_handling = True
            return 'basic_erl'

        # File I/O functions
        elif func_name == 'EOF':
            if len(expr.arguments) != 1:
                self.warnings.append("EOF requires 1 argument (file number)")
                return '0'
            file_num = self._generate_expression(expr.arguments[0])
            self.max_file_number = max(self.max_file_number, 255)
            # EOF returns -1 (true) if end of file, 0 (false) otherwise
            return f'(file_handles[(int)({file_num})] ? feof(file_handles[(int)({file_num})]) : -1)'

        elif func_name == 'LOC':
            # LOC returns current position in file
            if len(expr.arguments) != 1:
                self.warnings.append("LOC requires 1 argument (file number)")
                return '0'
            file_num = self._generate_expression(expr.arguments[0])
            self.max_file_number = max(self.max_file_number, 255)
            # Use ftell to get current position, cast to float for BASIC compatibility
            return f'(file_handles[(int)({file_num})] ? (float)ftell(file_handles[(int)({file_num})]) : -1)'

        elif func_name == 'LOF':
            # LOF returns length of file
            if len(expr.arguments) != 1:
                self.warnings.append("LOF requires 1 argument (file number)")
                return '0'
            file_num = self._generate_expression(expr.arguments[0])
            self.max_file_number = max(self.max_file_number, 255)
            # Save position, seek to end, get position, restore position, cast to float
            return (f'(file_handles[(int)({file_num})] ? '
                   f'(float)({{ long _pos = ftell(file_handles[(int)({file_num})]); '
                   f'fseek(file_handles[(int)({file_num})], 0, SEEK_END); '
                   f'long _size = ftell(file_handles[(int)({file_num})]); '
                   f'fseek(file_handles[(int)({file_num})], _pos, SEEK_SET); '
                   f'_size; }}) : -1)')

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

        # Binary data conversion functions
        elif func_name == 'CVI':
            # Convert 2-byte string to integer
            if len(expr.arguments) != 1:
                self.warnings.append("CVI requires 1 argument")
                return '0'
            str_arg = self._generate_string_expression(expr.arguments[0])
            # Generate helper function call for z88dk compatibility
            self.needs_cvi_helper = True
            return f'mb25_cvi({str_arg})'

        elif func_name == 'CVS':
            # Convert 4-byte string to single
            if len(expr.arguments) != 1:
                self.warnings.append("CVS requires 1 argument")
                return '0'
            str_arg = self._generate_string_expression(expr.arguments[0])
            # Generate helper function call for z88dk compatibility
            self.needs_cvs_helper = True
            return f'mb25_cvs({str_arg})'

        elif func_name == 'CVD':
            # Convert 8-byte string to double
            if len(expr.arguments) != 1:
                self.warnings.append("CVD requires 1 argument")
                return '0'
            str_arg = self._generate_string_expression(expr.arguments[0])
            # Generate helper function call for z88dk compatibility
            self.needs_cvd_helper = True
            return f'mb25_cvd({str_arg})'

        # FRE function - return free memory
        elif func_name == 'FRE':
            # FRE(numeric) - return total free memory
            # FRE(string) - trigger garbage collection and return free string pool space
            if len(expr.arguments) > 1:
                self.warnings.append("FRE requires 0 or 1 argument")
                return '0'

            # Check if argument is present
            if len(expr.arguments) == 0:
                # FRE with no args - treat as FRE(0)
                return '16384  /* FRE() - free memory (simulated) */'

            # Check if argument is a string or numeric expression
            arg_type = self._get_expression_type(expr.arguments[0])
            if arg_type == VarType.STRING:
                # FRE("") or FRE(string_var) - trigger GC and return string pool free space
                # Evaluate the string argument (even though we don't use it, it may have side effects)
                str_arg = self._generate_string_expression(expr.arguments[0])
                return f'(mb25_garbage_collect(), mb25_get_free_space())'
            else:
                # FRE(0) or FRE(numeric) - return total free memory
                # Evaluate the numeric argument (side effects)
                num_arg = self._generate_expression(expr.arguments[0])
                return f'(({num_arg}), 16384)  /* FRE(n) - free memory (simulated) */'

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

        elif func_name == 'MKI':
            # Convert integer to 2-byte string
            if len(expr.arguments) != 1:
                self.warnings.append("MKI$ requires 1 argument")
                return '/* MKI$ error */'
            num_arg = self._generate_expression(expr.arguments[0])
            self.needs_mki_helper = True
            return f'mb25_mki({result_id}, {num_arg})'

        elif func_name == 'MKS':
            # Convert single to 4-byte string
            if len(expr.arguments) != 1:
                self.warnings.append("MKS$ requires 1 argument")
                return '/* MKS$ error */'
            num_arg = self._generate_expression(expr.arguments[0])
            self.needs_mks_helper = True
            return f'mb25_mks({result_id}, {num_arg})'

        elif func_name == 'MKD':
            # Convert double to 8-byte string
            if len(expr.arguments) != 1:
                self.warnings.append("MKD$ requires 1 argument")
                return '/* MKD$ error */'
            num_arg = self._generate_expression(expr.arguments[0])
            self.needs_mkd_helper = True
            return f'mb25_mkd({result_id}, {num_arg})'

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

    def _generate_on_error(self, stmt: OnErrorStatementNode) -> List[str]:
        """Generate ON ERROR GOTO/GOSUB statement"""
        code = []

        if stmt.line_number == 0:
            # ON ERROR GOTO 0 - disable error handling
            code.append(self.indent() + 'error_handler = 0;  /* Disable error handling */')
        else:
            # ON ERROR GOTO line_number - set error handler
            code.append(self.indent() + f'error_handler = {stmt.line_number};  /* Set error handler */')
            # Ensure the target line has a label
            self.line_labels.add(stmt.line_number)

        return code

    def _generate_resume(self, stmt: ResumeStatementNode) -> List[str]:
        """Generate RESUME statement"""
        code = []

        if stmt.line_number is None:
            # RESUME - retry the statement that caused the error
            code.append(self.indent() + '/* RESUME - retry error statement */')
            code.append(self.indent() + 'basic_err = 0;')
            code.append(self.indent() + 'basic_erl = 0;')
            code.append(self.indent() + 'if (error_resume_line > 0) {')
            self.indent_level += 1
            code.append(self.indent() + 'switch(error_resume_line) {')
            self.indent_level += 1
            # Would need to generate cases for each line that could cause errors
            code.append(self.indent() + '/* Jump to error line - not fully implemented */')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
        elif stmt.line_number == -1:
            # RESUME NEXT (parser uses -1 as sentinel for NEXT)
            code.append(self.indent() + '/* RESUME NEXT - continue after error */')
            code.append(self.indent() + 'basic_err = 0;')
            code.append(self.indent() + 'basic_erl = 0;')
            code.append(self.indent() + '/* Continue execution - handled by normal flow */')
        elif stmt.line_number == 0:
            # RESUME 0 - same as RESUME (retry error statement)
            code.append(self.indent() + '/* RESUME 0 - retry error statement */')
            code.append(self.indent() + 'basic_err = 0;')
            code.append(self.indent() + 'basic_erl = 0;')
            code.append(self.indent() + '/* Retry logic not fully implemented */')
        else:
            # RESUME line_number - continue at specific line
            code.append(self.indent() + f'/* RESUME {stmt.line_number} */')
            code.append(self.indent() + 'basic_err = 0;')
            code.append(self.indent() + 'basic_erl = 0;')
            code.append(self.indent() + f'goto line_{stmt.line_number};')
            # Ensure the target line has a label
            self.line_labels.add(stmt.line_number)

        return code

    def _generate_error(self, stmt: ErrorStatementNode) -> List[str]:
        """Generate ERROR statement - trigger an error"""
        code = []

        error_code = self._generate_expression(stmt.error_code)
        code.append(self.indent() + f'/* ERROR statement */')
        code.append(self.indent() + f'basic_err = (int)({error_code});')
        # Get current line number - would need to track this
        code.append(self.indent() + f'basic_erl = {stmt.line_num};  /* Current line number */')
        code.append(self.indent() + f'error_resume_line = {stmt.line_num};')
        code.append(self.indent() + 'longjmp(error_jmp, 1);  /* Trigger error handler */')

        return code

    def _generate_field(self, stmt: FieldStatementNode) -> List[str]:
        """Generate FIELD statement for random access files"""
        code = []
        code.append(self.indent() + '/* FIELD statement - random access file fields */')

        # FIELD defines the structure of a random access record
        # For now, we'll just note that it's not fully implemented
        file_num = self._generate_expression(stmt.file_number)

        code.append(self.indent() + f'/* FIELD #{file_num}: ')
        for width, var in stmt.fields:
            width_expr = self._generate_expression(width)
            var_name = var.name if hasattr(var, 'name') else str(var)
            code.append(f'{var_name}({width_expr}) ')
        code.append('*/')

        code.append(self.indent() + '/* Random access FIELD not fully implemented */')
        return code

    def _generate_get(self, stmt: GetStatementNode) -> List[str]:
        """Generate GET statement for random access files"""
        code = []
        code.append(self.indent() + '/* GET statement - read random access record */')

        file_num = self._generate_expression(stmt.file_number)
        self.max_file_number = max(self.max_file_number, 255)

        if stmt.record_number:
            rec_num = self._generate_expression(stmt.record_number)
            code.append(self.indent() + f'/* GET #{file_num}, {rec_num} */')
        else:
            code.append(self.indent() + f'/* GET #{file_num} (next record) */')

        # For now, just a placeholder
        code.append(self.indent() + '/* Random access GET not fully implemented */')
        code.append(self.indent() + f'/* Would read from file_handles[(int)({file_num})] */')

        return code

    def _generate_put(self, stmt: PutStatementNode) -> List[str]:
        """Generate PUT statement for random access files"""
        code = []
        code.append(self.indent() + '/* PUT statement - write random access record */')

        file_num = self._generate_expression(stmt.file_number)
        self.max_file_number = max(self.max_file_number, 255)

        if stmt.record_number:
            rec_num = self._generate_expression(stmt.record_number)
            code.append(self.indent() + f'/* PUT #{file_num}, {rec_num} */')
        else:
            code.append(self.indent() + f'/* PUT #{file_num} (next record) */')

        # For now, just a placeholder
        code.append(self.indent() + '/* Random access PUT not fully implemented */')
        code.append(self.indent() + f'/* Would write to file_handles[(int)({file_num})] */')

        return code

    def _generate_lset(self, stmt: LsetStatementNode) -> List[str]:
        """Generate LSET statement - left-justify string in field"""
        code = []
        code.append(self.indent() + '/* LSET - left justify in field */')

        # LSET is used to set values in FIELD variables for random access
        # For regular string variables, it can also left-justify
        var_id = self._get_string_id(stmt.variable.name)
        value_expr = self._generate_string_expression(stmt.expression)

        # For now, just do a regular string assignment
        # A full implementation would handle field variables specially
        code.append(self.indent() + f'mb25_string_copy({var_id}, {value_expr});')
        code.append(self.indent() + '/* LSET field padding not implemented */')

        return code

    def _generate_rset(self, stmt: RsetStatementNode) -> List[str]:
        """Generate RSET statement - right-justify string in field"""
        code = []
        code.append(self.indent() + '/* RSET - right justify in field */')

        # RSET is similar to LSET but right-justifies
        var_id = self._get_string_id(stmt.variable.name)
        value_expr = self._generate_string_expression(stmt.expression)

        # For now, just do a regular string assignment
        # A full implementation would handle field variables specially
        code.append(self.indent() + f'mb25_string_copy({var_id}, {value_expr});')
        code.append(self.indent() + '/* RSET field padding not implemented */')

        return code
