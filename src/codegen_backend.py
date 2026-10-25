#!/usr/bin/env python3
"""
Code Generation Backend Interface

This module defines the abstract interface for code generation backends.
Different backends can generate code for different target platforms:
- C code for CP/M (8080 or Z80), in the uc80 dialect (preferred) or the
  z88dk dialect (alternate) - see docs/dev/TOOLCHAIN_POLICY.md
- Assembly for various processors
- Other high-level languages

Each backend receives a fully analyzed AST from the semantic analyzer
and generates executable code in the target language.
"""

import dataclasses
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Set, Optional, Any
from src.ast_nodes import *
from src.semantic_analyzer import SymbolTable, VarType
from src.number_format import numeric_digits, SINGLE_DIGITS, DOUBLE_DIGITS, INTEGER_DIGITS


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
    C code generator for z88dk compiler targeting CP/M on 8080 or Z80.

    Supports:
    - Integer variables (BASIC ! suffix maps to C int)
    - FOR/NEXT loops
    - PRINT statements for integers
    - String variables and operations (using mb25_string runtime)

    Anything this backend cannot compile correctly is a compile error
    (self.errors, shown by --compile-c, which then writes no C file).  A
    construct that would be compiled to different behaviour than the
    interpreter shows is never accepted silently.  Messages that are only
    advice go to self.warnings, which --compile-c also prints.
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
        self.temp_string_count = 0  # Size of the temporary-string pool

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
        # CP/M: String pool uses all available memory from __BSS_tail to SP-stack_reserve
        # No heap/malloc needed - pool address calculated at runtime
        self.stack_size = self.config.get('stack_size', 512)  # GOSUB/function call stack
        self.stack_reserve = self.config.get('stack_reserve', 1024)  # Safety margin for stack

        # C dialect to emit: 'uc80' (preferred) or 'z88dk' (alternate).
        # The two differ in how the string pool bootstraps and in printf conversions;
        # everything else is shared.  See docs/dev/TOOLCHAIN_POLICY.md.
        self.dialect = self.config.get('dialect', 'z88dk')

        # OPTION BASE (0 or 1) as the semantic analyzer saw it
        self.array_base = self.config.get('array_base', 0)
        # Number of subscripts each array is used with, by symbol-table key
        self.array_ranks: Dict[str, int] = {}
        # Dimension maxima of the arrays a DIM sizes, by key
        self.array_dims: Dict[str, List[int]] = {}
        # Keys of the plain (not subscripted) variables the program uses.  BASIC
        # keeps A and A(1) apart, and so do the C names: arrays end in _arr and
        # string arrays have their own STR_ macro.
        self.scalar_keys: Set[str] = set()
        # First-letter type defaults from DEFINT and friends
        self.def_suffix: Dict[str, str] = {}
        self.current_line = 0

    def get_file_extension(self) -> str:
        return '.c'

    def _unsupported(self, message: str) -> None:
        """Record a construct that cannot be compiled correctly.

        Compiling it anyway would write C that behaves differently from the
        interpreter, with nothing to tell the user.  --compile-c stops on any
        entry in self.errors.
        """
        where = f"line {self.current_line}: " if self.current_line else ""
        self.errors.append(where + message)

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
        - z88dk supports both 8080 and Z80 backends (-m8080 or default Z80)
        - Z80 is backwards compatible with 8080 and is used by most CP/M systems
        """
        # z88dk.zcc +cpm source.c -create-app -o output
        # +cpm: Target CP/M operating system (defaults to Z80, use -m8080 for 8080)
        # -create-app: Generate .COM executable
        # -lm: Link math library for floating point support

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
        # No -DAMALLOC: String pool allocated directly from __BSS_tail, no heap needed
        cmd.extend(['-create-app', '-lm', '-o', output_file])

        return cmd

    def indent(self) -> str:
        """Return current indentation string"""
        return '    ' * self.indent_level

    def generate(self, program: ProgramNode) -> str:
        """Generate C code for the program"""
        # First pass: count GOSUB statements
        self._count_gosubs(program)

        # Which arrays exist and how many subscripts each takes
        self._collect_array_usage(program)

        # Which NEXT closes which FOR
        self._pair_for_loops(program)

        self._warn_about_double_precision(program)
        self._warn_about_integer_overflow(program)
        self._warn_about_literal_range(program)

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

        # Numeric INPUT needs input_buffer even without string variables
        self.has_input = self._uses_input(program)

        # Collect binary data function usage
        self._collect_binary_function_usage(program)

        # Collect error handling usage
        self._collect_error_handling(program)

        code = []

        # Header
        uc80 = self.dialect == 'uc80'

        code.append('/* Generated by MBASIC-2025 compiler */')
        code.append(f'/* Target: CP/M via {"uc80" if uc80 else "z88dk"} */')
        code.append('')
        code.append('/* Memory configuration */')
        if uc80:
            code.append(f'/* String pool: end of BSS to SP-{self.stack_reserve} (all available memory) */')
            code.append(f'/* Stack reserve is honoured at run time; uc80 has no CRT_STACK_SIZE pragma. */')
            code.append('')
        else:
            code.append(f'/* String pool: __BSS_tail to SP-{self.stack_reserve} (all available memory) */')
            code.append(f'#pragma output CRT_STACK_SIZE = {self.stack_size}')
            code.append('')
            code.append('/* Note: z88dk automatically links only needed printf/scanf converters */')
            code.append('/* Do NOT use #pragma printf/scanf - it forces inclusion and increases size */')
            code.append('')

        # String system defines and includes.  The header is always needed: PRINT
        # and number formatting live in the same runtime as the strings.
        if self.string_count > 0:
            if uc80:
                # uc80 merges all translation units, so a #define here would disagree
                # with the copy of the header the runtime sees and silently corrupt
                # the descriptor array.  The build passes -DMB25_NUM_STRINGS instead.
                code.append(f'/* MB25_NUM_STRINGS={self.string_count} is passed with -D so that every */')
                code.append('/* translation unit agrees - uc80 compiles them together. */')
            else:
                code.append(f'#define MB25_NUM_STRINGS {self.string_count}')
        code.append('#include "mb25_string.h"')
        code.append('')
        if self.string_count > 0:
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

        # Helpers for string pool initialization (get SP and BSS_tail)
        if self.string_count > 0:
            if uc80:
                # uc80 has no inline assembly, and asm("...") is silently discarded
                # rather than rejected.  These live in runtime/strings/mb25_uc80_shim.mac,
                # which the build assembles separately and links as a .rel.
                code.append('/* Supplied by runtime/strings/mb25_uc80_shim.mac (uc80 has no inline asm) */')
                code.append('extern uint16_t _mb25_get_sp(void);')
                code.append('extern uint16_t _mb25_get_bss_tail(void);')
                code.append('')
            else:
                code.append('/* Get current stack pointer */')
                code.append('static uint16_t _mb25_get_sp(void) __naked {')
                code.append('#asm')
                code.append('    ld hl, 0')
                code.append('    add hl, sp')
                code.append('    ret')
                code.append('#endasm')
                code.append('}')
                code.append('')
                code.append('/* Get end of BSS (start of free memory) */')
                code.append('static uint16_t _mb25_get_bss_tail(void) __naked {')
                code.append('#asm')
                code.append('    EXTERN __BSS_tail')
                code.append('    ld hl, __BSS_tail')
                code.append('    ret')
                code.append('#endasm')
                code.append('}')
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

        # Initialize string system
        if self.string_count > 0:
            code.append(self.indent() + '/* Initialize string pool using all available memory */')
            code.append(self.indent() + '{')
            self.indent_level += 1
            code.append(self.indent() + 'uint16_t _bss_tail = _mb25_get_bss_tail();')
            code.append(self.indent() + 'uint16_t _pool_size = _mb25_get_sp() - ' + str(self.stack_reserve) + ' - _bss_tail;')
            code.append(self.indent() + 'if (mb25_init((uint8_t *)_bss_tail, _pool_size) != MB25_SUCCESS) {')
            self.indent_level += 1
            code.append(self.indent() + 'fprintf(stderr, "?Out of memory\\n");')
            code.append(self.indent() + 'return 1;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
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
        code.append(f'#define GOSUB_PUSH(id) do {{ if (gosub_sp >= {self.GOSUB_DEPTH}) {{ '
                    'fprintf(stderr, "?Out of memory\\n"); return 1; } '
                    'gosub_stack[gosub_sp++] = (id); } while (0)')
        code.append(self.indent() + f'int gosub_stack[{self.GOSUB_DEPTH}];  /* Return IDs (0, 1, 2...) - not line numbers */')
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
            code.append(self.indent() + f'unsigned char *file_record_buffers[{self.max_file_number + 1}];  /* Random file record buffers */')
            code.append(self.indent() + f'int file_record_sizes[{self.max_file_number + 1}];  /* Random file record sizes */')
            code.append(self.indent() + f'long file_record_numbers[{self.max_file_number + 1}];  /* Current record number (1-based) */')
            # Field variable mapping for LSET/RSET
            if self.string_count > 0:
                code.append(self.indent() + f'int field_var_files[{self.string_count}];  /* File number for each string var (-1 = not a field) */')
                code.append(self.indent() + f'int field_var_offsets[{self.string_count}];  /* Offset in record buffer for each field var */')
                code.append(self.indent() + f'int field_var_widths[{self.string_count}];  /* Width of field for each field var */')
            # Initialize all file handles to NULL
            code.append(self.indent() + 'int _i;')
            code.append(self.indent() + f'for (_i = 0; _i <= {self.max_file_number}; _i++) {{')
            self.indent_level += 1
            code.append(self.indent() + 'file_handles[_i] = NULL;')
            code.append(self.indent() + 'file_modes[_i] = 0;')
            code.append(self.indent() + 'file_record_buffers[_i] = NULL;')
            code.append(self.indent() + 'file_record_sizes[_i] = 0;')
            code.append(self.indent() + 'file_record_numbers[_i] = 0;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            # Initialize field mapping arrays
            if self.string_count > 0:
                code.append(self.indent() + f'for (_i = 0; _i < {self.string_count}; _i++) {{')
                self.indent_level += 1
                code.append(self.indent() + 'field_var_files[_i] = -1;')
                code.append(self.indent() + 'field_var_offsets[_i] = 0;')
                code.append(self.indent() + 'field_var_widths[_i] = 0;')
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
        code.append('    return 0;')
        if self.total_gosubs > 0 or any(isinstance(n, ReturnStatementNode)
                                        for line in program.lines for n in self._walk(line.statements)):
            code.append('')
            code.extend(self._gosub_dispatcher())
        self.indent_level -= 1
        code.append('}')
        code.append('')

        return '\n'.join(self._finalize_lines(code))

    def _finalize_lines(self, code: List[str]) -> List[str]:
        """Post-process the emitted C so it is valid C17, not just GCC-accepted.

        A label must be followed by a statement.  Codegen naturally produces
        `line_40:` directly before the `}` that closes a FOR body or an IF block,
        which GCC and z88dk accept as an extension but uc80 rejects (and C23 only
        legalised in 2023).  Emit an explicit null statement in that position.
        """
        label_only = re.compile(r'^\s*[A-Za-z_]\w*:\s*(/\*.*\*/\s*)?$')
        out = []
        for i, line in enumerate(code):
            if label_only.match(line):
                # Find the next line with content; if it closes the block, the label
                # would be dangling.
                nxt = next((c for c in code[i + 1:] if c.strip()), '')
                if nxt.lstrip().startswith('}'):
                    # the null statement goes before any trailing comment
                    line = re.sub(r':(\s*)(/\*.*\*/)?\s*$', r': ;\1\2', line).rstrip()
            out.append(line)
        return out

    def _count_strings_and_allocate_ids(self, program: ProgramNode):
        """Count string variables and allocate string IDs.

        A scalar takes one descriptor.  A string array takes one per element,
        in a run of consecutive IDs, so element n is the array's base ID + n.
        """
        current_id = 0

        scalar_strings = {name for name, info in self.symbols.variables.items()
                          if info.var_type == VarType.STRING and not info.is_array}
        scalar_strings |= {k for k in self.scalar_keys if self._key_type(k) == VarType.STRING}
        for var_name in sorted(scalar_strings):
            self.string_ids[var_name] = current_id
            current_id += 1

        for key in sorted(self.array_ranks):
            if self._key_type(key) == VarType.STRING:
                self.string_ids[key + '()'] = current_id
                current_id += self._array_total(key)

        # Reserve space for temporaries (for complex expressions)
        temp_count = self._estimate_temp_strings_needed(program)
        if temp_count > 0:
            self.string_ids['_TEMP_BASE'] = current_id
            current_id += temp_count
            self.next_temp_id = self.string_ids['_TEMP_BASE']
        else:
            self.next_temp_id = 0
        self.temp_string_count = temp_count

        self.string_count = current_id
        if current_id > 16383:
            self._unsupported(
                f"the program needs {current_id} string descriptors; the string "
                "runtime numbers them with 14 bits (16383 at most)")

    def _estimate_temp_strings_needed(self, program: ProgramNode) -> int:
        """Temporary string descriptors the busiest statement can need.

        Every string literal, string operation and function call in a
        statement may take one temporary.  Counting them all over-estimates,
        which only costs a few descriptors.  The temporaries are handed out
        round-robin, so a statement stays correct as long as the pool is at
        least as big as the number of temporaries that statement takes.
        """
        most = 0
        for line_node in program.lines:
            for stmt in line_node.statements:
                count = 0
                for n in self._walk(stmt):
                    if isinstance(n, (StringNode, FunctionCallNode, BinaryOpNode,
                                      MidAssignmentStatementNode)):
                        count += 1
                most = max(most, count)
        if most == 0:
            return 0
        return most + 3

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
            for node in self._walk(line_node.statements):
                if isinstance(node, GosubStatementNode):
                    self.total_gosubs += 1
                elif isinstance(node, OnGosubStatementNode):
                    self.total_gosubs += len(node.line_numbers)

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
                                self._unsupported(f"Complex expression in DATA not supported: {type(value_expr.operand).__name__}")
                        else:
                            self._unsupported(f"Complex expression in DATA not supported: {type(value_expr).__name__}")

    def _collect_def_fn(self, program: ProgramNode):
        """Collect all DEF FN functions for generation before main()"""
        self.def_fn_functions = []
        for line_node in program.lines:
            for stmt in line_node.statements:
                if isinstance(stmt, DefFnStatementNode):
                    self.def_fn_functions.append(stmt)

    def _uses_input(self, program: ProgramNode) -> bool:
        """True if the program has an INPUT statement anywhere.

        Numeric INPUT reads a line into input_buffer before converting it with
        atof, so the buffer must be declared even when the program has no
        string variables.
        """
        def scan(statements) -> bool:
            for stmt in statements or []:
                if isinstance(stmt, InputStatementNode):
                    return True
                if isinstance(stmt, IfStatementNode):
                    if scan(stmt.then_statements) or scan(stmt.else_statements):
                        return True
            return False

        return any(scan(line_node.statements) for line_node in program.lines)

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
                # A bare CLOSE closes every file, so it needs the full table
                elif isinstance(stmt, CloseStatementNode) and not stmt.file_numbers:
                    self.max_file_number = max(self.max_file_number, 255)
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
                elif isinstance(stmt, WriteStatementNode) and self._write_error_code(stmt):
                    self.needs_error_handling = True

    @staticmethod
    def _write_error_code(stmt) -> int:
        """Error a WRITE raises when it runs, 0 for none (see the WriteStatementNode fields)."""
        if getattr(stmt, 'bad_separator', False):
            return 2
        if stmt.file_number and not stmt.expressions and not getattr(stmt, 'file_comma', True):
            return 2
        if getattr(stmt, 'trailing_separator', None):
            return 22
        return 0

    # ------------------------------------------------------------------
    # Arrays
    # ------------------------------------------------------------------

    def _walk(self, node):
        """Yield an AST node and every AST node below it."""
        stack = [node]
        while stack:
            n = stack.pop()
            if isinstance(n, (list, tuple)):
                stack.extend(n)
            elif dataclasses.is_dataclass(n) and not isinstance(n, type):
                yield n
                for f in dataclasses.fields(n):
                    stack.append(getattr(n, f.name))

    def _array_key(self, var_node: Any) -> str:
        """Symbol-table style key of an array reference: NAME plus its suffix.

        The semantic analyzer keys a name without a suffix on '!', so this does.
        """
        base = getattr(var_node, 'name', '').upper()
        suffix = getattr(var_node, 'type_suffix', None)
        if not suffix and base and base[-1] in '$%!#':
            return base
        return base + (suffix or self.def_suffix.get(base[:1].lower(), '!'))

    def _key_type(self, key: str) -> VarType:
        """Type of a variable from the suffix on its key."""
        return {'%': VarType.INTEGER, '$': VarType.STRING,
                '#': VarType.DOUBLE}.get(key[-1], VarType.SINGLE)

    def _collect_array_usage(self, program: ProgramNode):
        """Find every array the program uses and how many subscripts it takes.

        The symbol table only knows the arrays that a DIM declares or that an
        assignment names; an array that is only read, or that is used without
        a DIM (so it has 11 elements per subscript), is missing from it.

        The semantic analyzer rewrites a read of A(I,J) into A(I*n+J), so a DIM
        gives the true number of subscripts and a use may show just one.
        """
        suffix_of = {VarType.INTEGER: '%', VarType.SINGLE: '!',
                     VarType.DOUBLE: '#', VarType.STRING: '$'}
        for line in program.lines:
            for n in self._walk(line.statements):
                if isinstance(n, DefTypeStatementNode):
                    for letter in n.letters:
                        self.def_suffix[letter.lower()] = suffix_of.get(n.var_type, '!')

        dimmed: Set[str] = set()
        used: Dict[str, int] = {}
        for line in program.lines:
            self.current_line = line.line_number
            for n in self._walk(line.statements):
                if isinstance(n, VariableNode):
                    key = self._array_key(n)
                    if n.subscripts:
                        used[key] = max(used.get(key, 0), len(n.subscripts))
                    elif n.subscripts is None and key[:-1] not in ('ERR', 'ERL'):
                        self.scalar_keys.add(key)
                elif isinstance(n, DimStatementNode):
                    for decl in n.arrays:
                        name = decl.name.upper()
                        if name[-1] not in '$%!#':
                            name += self.def_suffix.get(name[0].lower(), '!')
                        dimmed.add(name)
                        self.array_ranks[name] = len(decl.dimensions)
                        maxima = [self._constant_value(d) for d in decl.dimensions]
                        info = self.symbols.variables.get(name)
                        if any(m is None for m in maxima) and info is not None \
                                and info.dimensions:
                            maxima = list(info.dimensions)
                        if any(m is None for m in maxima):
                            self._unsupported(
                                f"DIM {name}: the size is not a constant the compiler can work out")
                            maxima = [10] * len(decl.dimensions)
                        self.array_dims[name] = [int(m) for m in maxima]
        for key, rank in used.items():
            if key not in dimmed:
                self.array_ranks[key] = rank
        self.current_line = 0

    def _array_sizes(self, key: str) -> List[int]:
        """Number of elements along each subscript of an array."""
        if key in self.array_dims:
            maxima = self.array_dims[key]
        else:
            # No DIM: BASIC gives every subscript 0..10
            maxima = [10] * self.array_ranks.get(key, 1)
        return [max(1, m + 1 - self.array_base) for m in maxima]

    def _array_total(self, key: str) -> int:
        total = 1
        for size in self._array_sizes(key):
            total *= size
        return total

    def _array_element_index(self, var_node: Any) -> str:
        """C expression for the zero-based flat index of an array element.

        Each subscript is rounded to an integer the way BASIC does, moved down
        by OPTION BASE, and range-checked by mb25_subscript(), which stops the
        program with "Subscript out of range" instead of writing past the array.
        The first subscript varies slowest, as in the interpreter's flattening.
        """
        key = self._array_key(var_node)
        sizes = self._array_sizes(key)
        if len(var_node.subscripts) == 1 and len(sizes) > 1:
            # Already flattened by the semantic analyzer, and already moved
            # down by OPTION BASE
            total = self._array_total(key)
            return f'mb25_subscript({self._integer_value(var_node.subscripts[0])}, {total}, 0)'
        if len(sizes) != len(var_node.subscripts):
            self._unsupported(
                f"array {key} has {len(sizes)} subscripts, used with {len(var_node.subscripts)}")
            return '0'
        parts = []
        for i, sub in enumerate(var_node.subscripts):
            stride = 1
            for size in sizes[i + 1:]:
                stride *= size
            expr = self._integer_value(sub)
            if self.array_base:
                expr = f'({expr} - {self.array_base})'
            expr = f'mb25_subscript({expr}, {sizes[i]}, {self.array_base or 0})'
            parts.append(f'{expr} * {stride}' if stride > 1 else expr)
        return ' + '.join(parts)

    def _str_number(self, arg: Any, result_id: str) -> str:
        """C call that stores STR$(arg) in the string result_id."""
        if self._numeric_kind(arg) == VarType.INTEGER:
            return f'mb25_str_int({result_id}, {self._integer_value(arg)})'
        kind = 1 if self._numeric_kind(arg) == VarType.DOUBLE else 0
        return f'mb25_str_num({result_id}, (double)({self._generate_expression(arg)}), {kind})'

    def _read_line(self, input_stream: str) -> str:
        """C condition that reads one line into input_buffer; true when it got one.

        At the end of the keyboard input the interpreter ends the program, so
        the compiled program does too (otherwise a loop that asks again would
        never stop).  A file reports the end through EOF() instead.
        """
        if input_stream == 'stdin':
            return 'fgets(input_buffer, 256, stdin) || mb25_input_eof()'
        return f'fgets(input_buffer, 256, {input_stream})'

    def _numeric_lvalue(self, var_node: Any) -> str:
        """C lvalue of a numeric variable or array element ('' for a string)."""
        if self._get_expression_type(var_node) == VarType.STRING:
            return ''
        if var_node.subscripts:
            return self._generate_array_access(var_node)
        return self._mangle_variable_name(self._canonical_basic_name(var_node))

    def _string_var_id(self, var_node: Any) -> str:
        """C expression for the string-pool ID of a string variable or element.

        A string array owns a run of consecutive descriptors starting at the ID
        the STR_<name> macro gives, so an element is that ID plus the flat index.
        """
        if getattr(var_node, 'subscripts', None):
            key = self._array_key(var_node)
            base = self._get_string_id(key + '()')
            return f'({base} + {self._array_element_index(var_node)})'
        return self._get_string_id(self._canonical_basic_name(var_node))

    # ------------------------------------------------------------------
    # Numeric types
    # ------------------------------------------------------------------

    def _numeric_kind(self, expr: Any) -> VarType:
        """INTEGER, SINGLE or DOUBLE for a numeric expression.

        Uses the interpreter's own rule (number_format.numeric_digits), so a
        compiled PRINT shows as many digits as an interpreted one.
        """
        digits = numeric_digits(expr)
        if digits == INTEGER_DIGITS:
            return VarType.INTEGER
        if digits == DOUBLE_DIGITS:
            return VarType.DOUBLE
        return VarType.SINGLE

    def _integer_value(self, expr: Any, checked: bool = False) -> str:
        """C int expression for a numeric expression, rounded like CINT.

        checked is True for the operands of \\, MOD, AND, OR, XOR, EQV, IMP and
        NOT: a value outside -32768..32767 after rounding is Overflow.
        """
        c_expr = self._generate_expression(expr)
        if self._get_expression_type(expr) == VarType.INTEGER:
            return c_expr
        return f'{"mb25_int16" if checked else "mb25_cint"}({c_expr})'

    def _generate_variable_declarations(self) -> List[str]:
        """Generate C variable declarations from symbol table"""
        decls = []

        # Group by type for cleaner output
        integers = []
        singles = []
        doubles = []

        # First, handle arrays.  String arrays have no C storage: their
        # elements are runs of descriptors in the string pool (see
        # _count_strings_and_allocate_ids).
        arrays = []
        array_clears = []
        for key in sorted(self.array_ranks):
            var_type = self._key_type(key)
            if var_type == VarType.STRING:
                continue
            c_name = self._mangle_variable_name(key) + '_arr'
            c_type = {VarType.INTEGER: 'int', VarType.DOUBLE: 'double'}.get(var_type, 'float')
            arrays.append(f'{c_type} {c_name}[{self._array_total(key)}];')
            array_clears.append(f'memset({c_name}, 0, sizeof({c_name}));')

        # Then, handle regular variables
        scalar_decls = {name: info.var_type for name, info in self.symbols.variables.items()
                        if not info.is_array}
        for key in self.scalar_keys:
            scalar_decls.setdefault(key, self._key_type(key))
        for var_name in sorted(scalar_decls):
            var_type = scalar_decls[var_name]

            # Skip string variables - they're handled by mb25_string system
            if var_type == VarType.STRING:
                continue

            c_name = self._mangle_variable_name(var_name)

            if var_type == VarType.INTEGER:
                integers.append(c_name)
            elif var_type == VarType.SINGLE:
                singles.append(c_name)
            elif var_type == VarType.DOUBLE:
                doubles.append(c_name)

        # Generate declarations
        # Arrays first
        if arrays:
            decls.append(self.indent() + '/* Arrays */')
            for array_decl in arrays:
                decls.append(self.indent() + array_decl)

        # Then regular variables
        # BASIC variables start at 0, so every C variable starts there too
        if integers:
            decls.append(self.indent() + 'int ' + ', '.join(f'{n} = 0' for n in integers) + ';')
        if singles:
            decls.append(self.indent() + 'float ' + ', '.join(f'{n} = 0' for n in singles) + ';')
        if doubles:
            decls.append(self.indent() + 'double ' + ', '.join(f'{n} = 0' for n in doubles) + ';')

        for clear in array_clears:
            decls.append(self.indent() + clear)

        # The end value and step of a FOR loop whose bounds are not constants
        for number, loop in sorted(self.for_vars.items()):
            c_type = {VarType.INTEGER: 'int', VarType.DOUBLE: 'double'}.get(
                self._get_expression_type(loop.variable), 'float')
            if self._constant_value(loop.end_expr) is None:
                decls.append(self.indent() + f'{c_type} _fe{number} = 0;')
            if loop.step_expr is not None and self._constant_value(loop.step_expr) is None:
                decls.append(self.indent() + f'{c_type} _fs{number} = 0;')

        # Buffer for INPUT: needed for string input, and for numeric input too
        # since that reads a line and converts it with atof.
        if self.string_count > 0 or getattr(self, 'has_input', False):
            decls.append(self.indent() + 'char input_buffer[256];  /* For INPUT statements */')

        return decls

    def _canonical_basic_name(self, var_node: Any) -> str:
        """BASIC name including its type suffix, as the symbol table keys it.

        The parser strips the suffix (A$ becomes VariableNode(name='a',
        type_suffix='$')), but the symbol table and the string-ID map are keyed
        on the suffixed name. Looking up the bare name silently missed, which
        made _mangle_variable_name emit a different C identifier for a reference
        (i) than for its declaration (i_int), and made every string variable
        collapse to ID 0 in _get_string_id.
        """
        base = getattr(var_node, 'name', '').upper()
        suffix = getattr(var_node, 'type_suffix', None)

        # The parser fills in type_suffix from the DEF tables even when the
        # source did not write one (DEFINT I makes a bare I carry '%'), so
        # honouring it is what keeps a reference consistent with its
        # declaration.
        if suffix and (base + suffix) in self.symbols.variables:
            return base + suffix
        if base in self.symbols.variables:
            return base

        # Deliberately do NOT search the other suffixes here. A variable the
        # analyzer never registered (SWAP only registers neither operand) would
        # then alias onto an unrelated variable that merely shares a base name:
        # `SWAP V, W` next to `V% = 42` silently became a swap of V% and W%,
        # turning a loud "Unknown symbol: v" build failure into a wrong answer.
        # Falling through leaves the name unresolved, which still fails loudly.
        return base + (suffix or '')

    # Names a BASIC variable must not take in C: the keywords, and the library and
    # runtime functions that the generated code calls.  BASIC lets a program use
    # any of them (REGISTER, FLOOR, EXIT) as a variable.
    _C_RESERVED = frozenset("""
        auto break case char const continue default do double else enum extern float
        for goto if inline int long register restrict return short signed sizeof static
        struct switch typedef union unsigned void volatile while near far main
        int_int float_int double_int double_dbl
        pow floor trunc sqrt sin cos tan atan exp log fabs round abs atoi atof strlen
        strchr strcpy strncpy strstr memcpy memset printf fprintf sprintf sscanf fscanf
        putchar fputc fputs fgets fopen fclose fseek ftell feof free malloc exit rand
        srand setjmp longjmp stdin stdout stderr size_t uint8_t uint16_t NULL
        data_pointer data_numeric data_strings data_types gosub_stack gosub_sp
        input_buffer file_handles file_modes basic_err basic_erl
        """.split())

    def _mangle_variable_name(self, basic_name: str) -> str:
        """
        Convert BASIC variable name to valid C identifier.

        In BASIC, FOO%, FOO!, FOO#, FOO$ are all DIFFERENT variables.
        We add type suffixes to distinguish them:
        - FOO (SINGLE/!) -> foo
        - FOO% (INTEGER) -> foo_int
        - FOO# (DOUBLE) -> foo_dbl
        - FOO$ (STRING) -> handled by string pool, not C variables

        Transformations applied:
        1. Extract base name (without type suffix)
        2. Convert to lowercase for consistency
        3. Add type suffix (_int, _dbl) to distinguish typed variables
        4. Add 'v_' prefix if name conflicts with C keywords
        """
        # Remove type suffix to get base name
        base_name = basic_name.rstrip('!%#$')

        # Make lowercase for consistency
        c_name = base_name.lower()

        # MBASIC allows '.' in names (REC.NUM, OLD.FILE), which is not a valid C
        # identifier character - `int rec.num;` made z88dk stop with
        # "Missing token, expecting ; got .". Same substitution as
        # _mangle_string_name. BASIC names cannot contain '_', so mapping '.'
        # to '_' cannot collide with another BASIC variable.
        c_name = ''.join(ch if ch.isalnum() else '_' for ch in c_name)

        # Add type suffix to distinguish different typed variables
        if basic_name.endswith('%'):
            c_name = c_name + '_int'
        elif basic_name.endswith('#'):
            c_name = c_name + '_dbl'
        # SINGLE (! or no suffix) gets no suffix - it's the default
        # STRING ($) is handled by string pool, not as C variables

        # Add prefix to avoid C keyword conflicts
        if c_name in self._C_RESERVED or c_name.startswith('mb25') or c_name.startswith('_'):
            c_name = 'v_' + c_name

        return c_name

    def _generate_line(self, line_node: LineNode) -> List[str]:
        """Generate code for one line of BASIC"""
        code = []
        self.current_line = line_node.line_number

        # Add line label if needed
        if line_node.line_number in self.line_labels:
            # Use goto label syntax: line_100:
            code.append(f'line_{line_node.line_number}:')
        # Run-time errors say which line they happened in.  REM and DATA
        # lines cannot fail, so they skip the store.
        if any(not isinstance(st, (RemarkStatementNode, DataStatementNode))
               for st in line_node.statements):
            code.append(self.indent() + f'mb25_line = {line_node.line_number}u;')

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
        elif isinstance(stmt, WaitStatementNode):
            return self._generate_wait(stmt)
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
        elif isinstance(stmt, ResetStatementNode):
            return self._generate_reset(stmt)
        elif isinstance(stmt, NameStatementNode):
            return self._generate_name(stmt)
        elif isinstance(stmt, FilesStatementNode):
            return self._generate_files(stmt)
        elif isinstance(stmt, PrintUsingStatementNode):
            return self._generate_print_using(stmt)
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
        elif isinstance(stmt, EraseStatementNode):
            return self._generate_erase(stmt)
        elif isinstance(stmt, WidthStatementNode):
            return self._generate_width(stmt)
        elif isinstance(stmt, LprintStatementNode):
            return self._generate_lprint(stmt)
        elif isinstance(stmt, ClearStatementNode):
            return self._generate_clear(stmt)
        elif isinstance(stmt, CallStatementNode):
            return self._generate_call(stmt)
        elif isinstance(stmt, ChainStatementNode):
            return self._generate_chain(stmt)
        elif isinstance(stmt, CommonStatementNode):
            return self._generate_common(stmt)
        elif isinstance(stmt, (DefTypeStatementNode, OptionBaseStatementNode)):
            # Handled when compiling: the parser typed every name, and
            # _array_sizes() applies OPTION BASE
            return []
        elif isinstance(stmt, SystemStatementNode):
            return [self.indent() + 'goto program_end;']
        elif isinstance(stmt, StopStatementNode):
            # The interpreter stops and offers CONT; a compiled program ends
            return [self.indent() + f'mb25_print_cstr("Break in {self.current_line}");',
                    self.indent() + 'mb25_print_nl();',
                    self.indent() + 'goto program_end;']
        else:
            # Unsupported statement
            self._unsupported(f"Unsupported statement type: {type(stmt).__name__}")
            return [self.indent() + f'/* Unsupported: {type(stmt).__name__} */']

    # How many GOSUBs can be active at once (2 bytes each)
    GOSUB_DEPTH = 256

    _STRING_FUNCTIONS = ('LEFT', 'RIGHT', 'MID', 'CHR', 'STR', 'STRING$', 'STRING',
                         'SPACE', 'HEX', 'OCT', 'INKEY', 'INKEY$', 'INPUT$',
                         'MKI', 'MKS', 'MKD')
    _INTEGER_FUNCTIONS = ('LEN', 'ASC', 'INSTR', 'CINT', 'EOF', 'CVI', 'PEEK', 'INP')
    _COMPARISONS = (TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS_THAN,
                    TokenType.LESS_EQUAL, TokenType.GREATER_THAN,
                    TokenType.GREATER_EQUAL)
    _LOGICAL = (TokenType.AND, TokenType.OR, TokenType.XOR, TokenType.EQV,
                TokenType.IMP)

    def _get_expression_type(self, expr: Any) -> VarType:
        """The type the C expression for this BASIC expression has.

        STRING for a string-pool ID, INTEGER for a C int, and SINGLE for
        anything C computes in floating point.  How many digits PRINT shows is
        a separate question, answered by _numeric_kind().
        """
        if isinstance(expr, NumberNode):
            # A whole number that fits an INTEGER is a C int
            if (isinstance(expr.value, (int, float)) and expr.value == int(expr.value)
                    and -32768 <= expr.value <= 32767
                    and not any(c in str(expr.literal).upper() for c in '.E#D!')):
                return VarType.INTEGER
            return self._numeric_kind(expr)
        elif isinstance(expr, StringNode):
            return VarType.STRING
        elif isinstance(expr, VariableNode):
            if expr.subscripts:
                return self._key_type(self._array_key(expr))
            # Resolve through the same helper the name mangler uses, so the
            # type we report here cannot disagree with the C identifier we
            # emit. (They did disagree: under DEFINT I, a bare I mangled to
            # i_int but typed as SINGLE, producing printf("%g", i_int).)
            var_info = self.symbols.variables.get(self._canonical_basic_name(expr))
            if var_info is not None:
                return var_info.var_type
            return self._numeric_kind(expr)
        elif isinstance(expr, (UnaryOpNode, BinaryOpNode)) and self._constant_value(expr) is not None:
            value = self._constant_value(expr)
            if value == int(value) and -32768 <= value <= 32767:
                return VarType.INTEGER
            return self._numeric_kind(expr)
        elif isinstance(expr, UnaryOpNode):
            if expr.operator == TokenType.NOT:
                return VarType.INTEGER
            return self._get_expression_type(expr.operand)
        elif isinstance(expr, BinaryOpNode):
            left = self._get_expression_type(expr.left)
            if expr.operator in self._COMPARISONS or expr.operator in self._LOGICAL \
                    or expr.operator in (TokenType.MOD, TokenType.BACKSLASH):
                return VarType.INTEGER
            if left == VarType.STRING:
                return VarType.STRING        # concatenation
            right = self._get_expression_type(expr.right)
            if expr.operator in (TokenType.DIVIDE, TokenType.POWER):
                return VarType.SINGLE
            if left == VarType.INTEGER and right == VarType.INTEGER:
                return VarType.INTEGER
            return VarType.SINGLE
        elif isinstance(expr, FunctionCallNode):
            name = expr.name.upper()
            if name.startswith('FN'):
                return self._key_type('X' + (expr.type_suffix or '!'))
            if name in self._STRING_FUNCTIONS:
                return VarType.STRING
            if name in self._INTEGER_FUNCTIONS:
                return VarType.INTEGER
            return VarType.SINGLE
        return VarType.SINGLE

    def _open_output_file(self, file_number: Any) -> List[str]:
        """Code that checks a PRINT#/WRITE# file is open and aims the runtime at it."""
        code = []
        file_num_expr = self._generate_expression(file_number)
        self.max_file_number = max(self.max_file_number, 255)  # Assume max 255 files
        file_ptr = f'file_handles[(int)({file_num_expr})]'
        code.append(self.indent() + f'if ({file_ptr} == NULL) {{')
        self.indent_level += 1
        code.append(self.indent() + 'mb25_fail("File not open");')
        code.append(self.indent() + 'return 1;')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent() + f'mb25_set_out({file_ptr});')
        return code

    def _print_number(self, expr: Any, write: bool = False) -> str:
        """C statement that prints one number the way MBASIC does.

        PRINT puts a space before a number that is not negative and one after
        it; WRITE (write=True) prints the digits alone.  How many digits show
        depends on the type of the expression (6 for single precision), not on
        its value - see number_format.numeric_digits().
        """
        kind = self._numeric_kind(expr)
        prefix = 'mb25_write_' if write else 'mb25_print_'
        if kind == VarType.INTEGER:
            return f'{prefix}int({self._integer_value(expr)});'
        c_expr = self._generate_expression(expr)
        return f'{prefix}num((double)({c_expr}), {1 if kind == VarType.DOUBLE else 0});'

    def _print_string(self, expr: Any) -> str:
        """C statement that prints one string expression."""
        if isinstance(expr, StringNode):
            return f'mb25_print_cstr("{self._escape_string(expr.value)}");'
        return f'mb25_print_string({self._generate_string_expression(expr)});'

    def _generate_print(self, stmt: PrintStatementNode) -> List[str]:
        """Generate PRINT statement code

        Everything goes through the mb25 runtime, which knows the cursor
        column: comma zones every 14 columns, TAB, the 80-column wrap and the
        number format (a leading space or minus sign, a trailing space, 6
        significant digits for a single) are all done there.
        """
        code = []
        if stmt.file_number:
            code.extend(self._open_output_file(stmt.file_number))

        for i, expr in enumerate(stmt.expressions):
            separator = stmt.separators[i] if i < len(stmt.separators) else '\n'

            if isinstance(expr, FunctionCallNode) and expr.name.upper() in ('TAB', 'SPC'):
                func_name = expr.name.upper()
                if len(expr.arguments) != 1:
                    self._unsupported(f"{func_name} needs 1 argument")
                    continue
                arg = self._integer_value(expr.arguments[0])
                code.append(self.indent() + f'mb25_print_{func_name.lower()}({arg});')
            elif self._get_expression_type(expr) == VarType.STRING:
                code.append(self.indent() + self._print_string(expr))
            else:
                code.append(self.indent() + self._print_number(expr))

            if separator == ',':
                code.append(self.indent() + 'mb25_print_zone();')
            elif separator != ';':
                code.append(self.indent() + 'mb25_print_nl();')

        if not stmt.expressions:
            code.append(self.indent() + 'mb25_print_nl();')

        if stmt.file_number:
            code.append(self.indent() + 'mb25_set_out(NULL);')
        return code

    def _warn_about_double_precision(self, program: ProgramNode):
        """uc80 has no 64-bit float: a double is stored in 32 bits.

        So a program that asks for double precision (a # variable, a literal
        with more than seven digits, DEFDBL, CDBL) gets about seven digits and
        prints them in D notation, where the interpreter shows sixteen.
        """
        if self.dialect != 'uc80':
            return
        uses_double = any(k.endswith('#') for k in list(self.scalar_keys) + list(self.array_ranks))
        if not uses_double:
            for line in program.lines:
                for n in self._walk(line.statements):
                    if (isinstance(n, NumberNode) and numeric_digits(n) == DOUBLE_DIGITS) \
                            or (isinstance(n, FunctionCallNode) and n.name.upper() == 'CDBL') \
                            or (isinstance(n, DefTypeStatementNode) and n.var_type == VarType.DOUBLE):
                        uses_double = True
                        break
                if uses_double:
                    break
        if uses_double:
            self.warnings.append(
                "double precision is stored in 32 bits by uc80: values keep about 7 digits, "
                "where the interpreter keeps 16")

    def _warn_about_literal_range(self, program: ProgramNode):
        """Say so when a number in the program is outside the uc80 float range.

        A uc80 float holds about 1.2E-38 to 1.7E38.  A bigger literal wraps to
        a small wrong value, and a smaller one becomes 0, with no error.
        """
        if self.dialect != 'uc80':
            return
        for line in program.lines:
            for n in self._walk(line.statements):
                if isinstance(n, NumberNode) and isinstance(n.value, (int, float)):
                    size = abs(float(n.value))
                    if size > 1.7e38 or 0 < size < 1.18e-38:
                        self.warnings.append(
                            f"line {line.line_number}: the number {n.value!r} is outside the "
                            "range of a uc80 float (about 1.2E-38 to 1.7E38) and is wrong in "
                            "the compiled program")
                        return

    def _warn_about_integer_overflow(self, program: ProgramNode):
        """Say so when integer + - * can wrap at 16 bits.

        The interpreter turns an integer result that does not fit into a
        single-precision number.  The C int wraps, and nothing tells the user.
        A sum of constants is worked out by the compiler and does not count.
        """
        for line in program.lines:
            for n in self._walk(line.statements):
                if (isinstance(n, BinaryOpNode)
                        and n.operator in (TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY)
                        and self._constant_value(n) is None
                        and self._get_expression_type(n) == VarType.INTEGER
                        and self._get_expression_type(n.left) == VarType.INTEGER
                        and self._get_expression_type(n.right) == VarType.INTEGER):
                    self.warnings.append(
                        f"line {line.line_number}: integer + - * wraps at 16 bits in the "
                        "compiled program; the interpreter gives a larger single-precision result")
                    return

    def _statements_in_order(self, statements):
        """The statements of a list in program order, IF branches included."""
        for stmt in statements:
            yield stmt
            if isinstance(stmt, IfStatementNode):
                yield from self._statements_in_order(stmt.then_statements or [])
                yield from self._statements_in_order(stmt.else_statements or [])

    def _pair_for_loops(self, program: ProgramNode):
        """Give each FOR a number and say which loops each NEXT closes.

        NEXT pairs with the FOR that is nearest above it in the program text,
        as it does in the JavaScript backend.  A C `for` block cannot do this:
        a NEXT may sit on another line than the body, inside an IF, or after a
        GOSUB that jumps around it.  So a loop is compiled to labels and gotos.
        """
        self.for_ids: Dict[int, int] = {}      # id(FOR node) -> loop number
        self.next_ids: Dict[int, List[int]] = {}   # id(NEXT node) -> loop numbers
        self.for_vars: Dict[int, Any] = {}     # loop number -> FOR node
        stack: List[Any] = []
        count = 0
        for line in program.lines:
            self.current_line = line.line_number
            for stmt in self._statements_in_order(line.statements):
                if isinstance(stmt, ForStatementNode):
                    count += 1
                    self.for_ids[id(stmt)] = count
                    self.for_vars[count] = stmt
                    stack.append((count, self._canonical_basic_name(stmt.variable)))
                elif isinstance(stmt, NextStatementNode):
                    closes = []
                    names = [self._canonical_basic_name(v) for v in stmt.variables or []]
                    for name in names or [None]:
                        if not stack:
                            self._unsupported("NEXT without FOR")
                            break
                        number, for_name = stack.pop()
                        if name is not None and name != for_name:
                            self._unsupported(f"NEXT {name} does not match the FOR {for_name}")
                        closes.append(number)
                    self.next_ids[id(stmt)] = closes
        if stack:
            self.current_line = self.for_vars[stack[-1][0]].line_num or 0
            self._unsupported("FOR without a NEXT below it (the C backend pairs each NEXT "
                              "with the nearest FOR above it in the text)")
        self.current_line = 0

    def _generate_for(self, stmt: ForStatementNode) -> List[str]:
        """Generate FOR loop code

        FOR v = a TO b STEP s becomes
            v = a; end = b; step = s;
          for_N_top:  if v is past end, goto for_N_end
        and the matching NEXT adds step to v and jumps back.  BASIC reads b and
        s once, when the loop starts.  A constant bound or step is written
        straight into the test.
        """
        code = []
        number = self.for_ids.get(id(stmt))
        if number is None:
            self._unsupported("FOR loop that the compiler could not pair with a NEXT")
            return code

        var_name = self._mangle_variable_name(self._canonical_basic_name(stmt.variable))
        start = self._generate_expression(stmt.start_expr)
        if self._get_expression_type(stmt.variable) == VarType.INTEGER:
            start = self._integer_value(stmt.start_expr)

        def constant_or_temp(expr, name):
            value = self._constant_value(expr)
            if value is not None:
                return self._number_literal(value), value
            return name, None

        end, end_const = constant_or_temp(stmt.end_expr, f'_fe{number}')
        if stmt.step_expr is None:
            step, step_const = '1', 1
        else:
            step, step_const = constant_or_temp(stmt.step_expr, f'_fs{number}')

        code.append(self.indent() + f'{var_name} = {start};')
        if end_const is None:
            code.append(self.indent() + f'_fe{number} = {self._generate_expression(stmt.end_expr)};')
        if step_const is None:
            code.append(self.indent() + f'_fs{number} = {self._generate_expression(stmt.step_expr)};')

        # The sign of STEP picks the direction of the test
        var_is_int = self._get_expression_type(stmt.variable) == VarType.INTEGER
        end_is_int = end_const is not None and float(end_const).is_integer() \
            or end_const is None and self._get_expression_type(stmt.end_expr) == VarType.INTEGER
        both_int = var_is_int and end_is_int
        past_up = self._compare(var_name, '>', end, both_int)
        past_down = self._compare(var_name, '<', end, both_int)
        # STEP 0 is over only when the variable equals the end (the sign of
        # var - end must equal the sign of the step, and that sign is 0).
        at_end = self._compare(var_name, '==', end, both_int)
        if step_const is None:
            test = (f'(({step}) == 0 ? ({at_end}) : '
                    f'(({step}) > 0 ? ({past_up}) : ({past_down})))')
        elif step_const == 0:
            test = at_end
        elif step_const > 0:
            test = past_up
        else:
            test = past_down
        code.append(f'for_{number}_top:')
        code.append(self.indent() + f'if ({test}) goto for_{number}_end;')
        return code

    def _generate_next(self, stmt: NextStatementNode) -> List[str]:
        """Generate NEXT statement: step the variable and test again.  NEXT J,I closes two loops."""
        code = []
        for number in self.next_ids.get(id(stmt), []):
            loop = self.for_vars[number]
            var_name = self._mangle_variable_name(self._canonical_basic_name(loop.variable))
            if loop.step_expr is None:
                step = '1'
            else:
                value = self._constant_value(loop.step_expr)
                step = self._number_literal(value) if value is not None else f'_fs{number}'
            code.append(self.indent() + f'{var_name} += {step};')
            code.append(self.indent() + f'goto for_{number}_top;')
            code.append(f'for_{number}_end: ;')
        return code

    def _generate_assignment(self, stmt: LetStatementNode) -> List[str]:
        """Generate assignment statement"""
        var_type = self._get_expression_type(stmt.variable)
        expr_type = self._get_expression_type(stmt.expression)

        if (var_type == VarType.STRING) != (expr_type == VarType.STRING):
            self._unsupported("assignment of a string to a number or a number to "
                              "a string (Type mismatch)")
            return []

        if var_type == VarType.STRING:
            dest = self._string_var_id(stmt.variable)
            expr = stmt.expression

            if isinstance(expr, StringNode):
                return [self.indent() + f'mb25_string_alloc_const({dest}, "{self._escape_string(expr.value)}");']
            elif isinstance(expr, VariableNode):
                return [self.indent() + f'mb25_string_copy({dest}, {self._string_var_id(expr)});']
            elif isinstance(expr, FunctionCallNode):
                func_code = self._generate_string_function_statement(expr, dest)
                return [self.indent() + f'{func_code};']
            elif isinstance(expr, BinaryOpNode) and expr.operator == TokenType.PLUS:
                return self._generate_concat_assignment(dest, expr)
            else:
                self._unsupported(f"string expression {type(expr).__name__}")
                return []

        # Numeric assignment
        if stmt.variable.subscripts:
            target = self._generate_array_access(stmt.variable)
        else:
            target = self._mangle_variable_name(self._canonical_basic_name(stmt.variable))
        if var_type == VarType.INTEGER:
            value = self._integer_value(stmt.expression)
        else:
            value = self._generate_expression(stmt.expression)
        return [self.indent() + f'{target} = {value};']

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
            code.append(self.indent() + f'mb25_fail("File not open");')
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
                    self._unsupported("Complex prompt expressions not yet supported")

                # A comma after the prompt leaves out the "? "; INPUT; does not
                if not stmt.prompt_comma:
                    prompt_str += "? "

                code.append(self.indent() + f'mb25_print_cstr("{self._escape_string(prompt_str)}");')
            else:
                code.append(self.indent() + 'mb25_print_cstr("? ");')

        # With several variables, read one line and split it at the commas
        if len(stmt.variables) > 1:
            # Read entire line first
            code.append(self.indent() + f'if ({self._read_line(input_stream)}) {{')
            self.indent_level += 1
            code.append(self.indent() + 'mb25_chomp(input_buffer);')
            code.append(self.indent() + 'char *_ptr = input_buffer;')
            code.append(self.indent() + 'char _field[256];')

            # Parse each field from the line
            for i, var_node in enumerate(stmt.variables):
                var_type = self._get_expression_type(var_node)
                code.append(self.indent() + '/* Parse next field */')

                if var_type == VarType.STRING:
                    var_str_id = self._string_var_id(var_node)
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
                    var_name = self._numeric_lvalue(var_node)
                    code.append(self.indent() + '{')
                    self.indent_level += 1
                    if var_type == VarType.INTEGER:
                        code.append(self.indent() + f'{var_name} = mb25_cint(mb25_atof(_ptr));')
                    else:
                        # atof, not sscanf("%f"): z88dk's scanf float converter
                        # is built against the f48 float pack and needs
                        # init_floatpack, which --math-mbf32 does not provide,
                        # so any numeric INPUT failed to link. atof is mbf32-safe.
                        code.append(self.indent() + f'{var_name} = mb25_atof(_ptr);')
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
                    var_str_id = self._string_var_id(var_node)
                    code.append(self.indent() + f'if ({self._read_line(input_stream)}) {{')
                    self.indent_level += 1
                    code.append(self.indent() + 'mb25_chomp(input_buffer);')
                    code.append(self.indent() + f'mb25_string_alloc_init({var_str_id}, input_buffer);')
                    self.indent_level -= 1
                    code.append(self.indent() + '}')
                else:
                    # Numeric input
                    var_name = self._numeric_lvalue(var_node)
                    # Read a line and convert it with atof: fscanf("%d") leaves
                    # the newline behind for the next INPUT, and the scanf float
                    # converter cannot link against --math-mbf32.
                    convert = 'mb25_cint(mb25_atof(input_buffer))' if var_type == VarType.INTEGER \
                        else 'mb25_atof(input_buffer)'
                    code.append(self.indent() + '{')
                    self.indent_level += 1
                    code.append(self.indent() + f'if ({self._read_line(input_stream)}) {{')
                    self.indent_level += 1
                    code.append(self.indent() + f'{var_name} = {convert};')
                    self.indent_level -= 1
                    code.append(self.indent() + '}')
                    self.indent_level -= 1
                    code.append(self.indent() + '}')

                # If there are more variables and it's keyboard input, show another prompt
                if i < len(stmt.variables) - 1 and not stmt.file_number:
                    code.append(self.indent() + 'mb25_print_cstr("?? ");  /* Next variable prompt */')

        if not stmt.file_number:
            code.append(self.indent() + 'mb25_set_col(0);  /* Enter moved the cursor to column 0 */')
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
        """Generate IF/THEN/ELSE statement

        Each branch is either a line number (a GOTO) or a list of statements,
        and the two kinds mix: IF X THEN PRINT "A" ELSE 160.
        """
        code = []
        condition = self._generate_expression(stmt.condition)

        def branch(line_number, statements):
            lines = []
            self.indent_level += 1
            if line_number is not None:
                lines.append(self.indent() + f'goto line_{line_number};')
            for inner in statements or []:
                lines.extend(self._generate_statement(inner))
            self.indent_level -= 1
            return lines

        code.append(self.indent() + f'if ({condition}) {{')
        code.extend(branch(stmt.then_line_number, stmt.then_statements))
        if stmt.else_line_number is not None or stmt.else_statements:
            code.append(self.indent() + '} else {')
            code.extend(branch(stmt.else_line_number, stmt.else_statements))
        code.append(self.indent() + '}')
        return code

    def _generate_goto(self, stmt: GotoStatementNode) -> List[str]:
        """Generate GOTO statement"""
        return [self.indent() + f'goto line_{stmt.line_number};']

    def _generate_dim(self, stmt: DimStatementNode) -> List[str]:
        """Generate DIM statement

        The size of every array is fixed when the program is compiled, so the
        storage exists from the start of main() and is zeroed there; DIM itself
        has nothing left to do.  (The semantic analyzer has already refused a
        DIM whose size is not a constant.)
        """
        return []

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
                code.append(self.indent() + f'{float(val)!r}f,  /* float: {float(val)} */')
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
                    code.append(self.indent() + f'"{self._escape_string(val)}",')
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
        """Generate READ statement

        The DATA arrays are only emitted for the kinds of value the program
        has: data_strings exists when some DATA item is text, so a READ must
        not name it otherwise.
        """
        code = []
        has_strings = 'string' in self.data_types
        has_numbers = any(t != 'string' for t in self.data_types)
        number_test = "data_types[data_pointer] == 'I' || data_types[data_pointer] == 'F'"

        if not self.data_values:
            # No DATA anywhere: the first READ is "Out of DATA"
            code.append(self.indent() + 'mb25_fail("Out of DATA");')
            code.append(self.indent() + 'return 1;')
            return code

        for var_node in stmt.variables:
            # Check if we're out of data
            code.append(self.indent() + f'if (data_pointer >= {len(self.data_values)}) {{')
            self.indent_level += 1
            code.append(self.indent() + 'mb25_fail("Out of DATA");')
            code.append(self.indent() + 'return 1;')
            self.indent_level -= 1
            code.append(self.indent() + '}')

            var_type = self._get_expression_type(var_node)
            target = self._numeric_lvalue(var_node)

            if var_type == VarType.STRING:
                str_id = self._string_var_id(var_node)
                if has_strings:
                    code.append(self.indent() + "if (data_types[data_pointer] == 'S') {")
                    code.append(self.indent() + f'    mb25_string_alloc_const({str_id}, data_strings[data_pointer]);')
                    code.append(self.indent() + ('} else {' if has_numbers else '}'))
                else:
                    code.append(self.indent() + '{')
                if has_numbers:
                    code.append(self.indent() + '    char _num_str[40];')
                    code.append(self.indent() + '    mb25_fmt_num(_num_str, data_numeric[data_pointer], 1);')
                    code.append(self.indent() + f'    mb25_string_alloc_init({str_id}, _num_str);')
                    code.append(self.indent() + '}')
                elif not has_strings:
                    code.append(self.indent() + '}')
            else:
                if var_type == VarType.INTEGER:
                    from_number = f'{target} = mb25_cint(data_numeric[data_pointer]);'
                    from_string = f'{target} = mb25_cint(mb25_atof(data_strings[data_pointer]));'
                else:
                    from_number = f'{target} = data_numeric[data_pointer];'
                    from_string = f'{target} = mb25_atof(data_strings[data_pointer]);'
                if has_numbers and has_strings:
                    code.append(self.indent() + f'if ({number_test}) {{')
                    code.append(self.indent() + f'    {from_number}')
                    code.append(self.indent() + '} else {')
                    code.append(self.indent() + f'    {from_string}')
                    code.append(self.indent() + '}')
                elif has_numbers:
                    code.append(self.indent() + from_number)
                else:
                    code.append(self.indent() + from_string)

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
            self._unsupported(f"RESTORE to line {stmt.line_number} not supported - resetting to beginning")

        return code

    def _generate_array_access(self, var_node: VariableNode) -> str:
        """C lvalue for a numeric array element.

        BASIC arrays can have several subscripts; the C array is flat, and
        _array_element_index() works out the position (with OPTION BASE and a
        range check).  A string array has no C lvalue: see _string_var_id().
        """
        key = self._array_key(var_node)
        return f'{self._mangle_variable_name(key)}_arr[{self._array_element_index(var_node)}]'

    def _generate_gosub(self, stmt: GosubStatementNode) -> List[str]:
        """Generate GOSUB statement with proper return mechanism"""
        code = []
        # Each GOSUB gets a unique return label
        return_id = self.gosub_return_counter
        self.gosub_return_counter += 1

        # Push return ID onto stack
        code.append(self.indent() + f'GOSUB_PUSH({return_id});  /* Push return ID */')
        code.append(self.indent() + f'goto line_{stmt.line_number};  /* Jump to subroutine */')
        code.append(f'gosub_return_{return_id}:  /* Return point */')
        code.append(self.indent() + f'mb25_line = {self.current_line}u;')
        return code

    def _generate_return(self, stmt: ReturnStatementNode) -> List[str]:
        """Generate RETURN statement

        Every RETURN jumps to one shared dispatcher (see _gosub_dispatcher).
        A switch at each RETURN made the code grow with the square of the
        number of GOSUBs: 70 subroutines gave a .com that did not fit in memory.
        """
        return [self.indent() + 'goto gosub_dispatch;']

    def _gosub_dispatcher(self) -> List[str]:
        """The code that sends RETURN back to the GOSUB that called."""
        code = ['gosub_dispatch:']
        code.append('    if (gosub_sp <= 0) {')
        code.append('        mb25_fail("RETURN without GOSUB");')
        code.append('        return 1;')
        code.append('    }')
        code.append('    switch (gosub_stack[--gosub_sp]) {')
        for return_id in range(self.total_gosubs):
            code.append(f'    case {return_id}: goto gosub_return_{return_id};')
        code.append('    default: break;')
        code.append('    }')
        code.append('    goto program_end;')
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
            code.append(self.indent() + f'GOSUB_PUSH({return_id});')
            code.append(self.indent() + f'goto line_{line_num};')
            code.append(f'gosub_return_{return_id}:')
            code.append(self.indent() + f'mb25_line = {self.current_line}u;')
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
        Direct memory access for CP/M programs
        """
        code = []
        addr_expr = self._generate_expression(stmt.address)
        value_expr = self._generate_expression(stmt.value)

        # Direct memory write
        code.append(self.indent() + f'*((unsigned char*)((int)({addr_expr}))) = (unsigned char)({value_expr});')

        return code

    def _generate_out(self, stmt: OutStatementNode) -> List[str]:
        """Generate OUT statement

        OUT port, value - Write byte to I/O port
        Uses z88dk outp() function for CP/M port I/O
        """
        code = []
        port_expr = self._generate_expression(stmt.port)
        value_expr = self._generate_expression(stmt.value)

        # Use z88dk's outp() function for port I/O
        code.append(self.indent() + f'outp((int)({port_expr}), (int)({value_expr}));')

        return code

    def _generate_wait(self, stmt: WaitStatementNode) -> List[str]:
        """Generate WAIT statement

        WAIT port, mask [, select]
        Waits until (INP(port) XOR select) AND mask <> 0
        If select is omitted, waits until INP(port) AND mask <> 0
        """
        code = []
        port_expr = self._generate_expression(stmt.port)
        mask_expr = self._generate_expression(stmt.mask)

        if stmt.select:
            select_expr = self._generate_expression(stmt.select)
            # Wait until (INP(port) XOR select) AND mask != 0
            code.append(self.indent() + '{')
            self.indent_level += 1
            code.append(self.indent() + f'int _port = (int)({port_expr});')
            code.append(self.indent() + f'int _mask = (int)({mask_expr});')
            code.append(self.indent() + f'int _select = (int)({select_expr});')
            code.append(self.indent() + 'while (((inp(_port) ^ _select) & _mask) == 0);')
            self.indent_level -= 1
            code.append(self.indent() + '}')
        else:
            # Wait until INP(port) AND mask != 0
            code.append(self.indent() + '{')
            self.indent_level += 1
            code.append(self.indent() + f'int _port = (int)({port_expr});')
            code.append(self.indent() + f'int _mask = (int)({mask_expr});')
            code.append(self.indent() + 'while ((inp(_port) & _mask) == 0);')
            self.indent_level -= 1
            code.append(self.indent() + '}')

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
            self.current_line = getattr(fn_stmt, 'line_num', 0) or 0
            if self._get_expression_type(fn_stmt.expression) == VarType.STRING or any(
                    getattr(p, 'type_suffix', None) == '$' for p in fn_stmt.parameters or []):
                self._unsupported(f"string DEF FN functions are not supported: {fn_stmt.name}")
                continue
            # Determine return type from function name
            return_type = 'double'  # Default to double
            if fn_stmt.name.endswith('%'):
                return_type = 'int'
            elif fn_stmt.name.endswith('$'):
                # String functions would need special handling
                self._unsupported(f"String DEF FN functions not yet supported: {fn_stmt.name}")
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
                        self._unsupported(f"String parameters in DEF FN not yet supported")
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

        SWAP var1, var2 - Exchange values of two variables.  Two strings
        exchange their descriptors, so no text is copied.
        """
        code = []
        var1_type = self._get_expression_type(stmt.var1)
        var2_type = self._get_expression_type(stmt.var2)

        if (var1_type == VarType.STRING) != (var2_type == VarType.STRING):
            self._unsupported("SWAP of a string and a number (Type mismatch)")
            return code
        if var1_type != var2_type:
            # BASIC stops with Type mismatch here too, but only at run time
            self._unsupported("SWAP of two variables of different types (Type mismatch)")
            return code

        if var1_type == VarType.STRING:
            code.append(self.indent() +
                        f'mb25_string_swap({self._string_var_id(stmt.var1)}, {self._string_var_id(stmt.var2)});')
        else:
            var1_name = self._generate_variable_reference(stmt.var1)
            var2_name = self._generate_variable_reference(stmt.var2)
            c_type = {VarType.INTEGER: 'int', VarType.DOUBLE: 'double'}.get(var1_type, 'float')
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
            # Convert to C string using temp pool (no malloc!)
            temp_id = self._get_temp_string_id()
            code.append(self.indent() + '{')
            self.indent_level += 1
            code.append(self.indent() + f'int _file_num = (int)({file_num_expr});')
            code.append(self.indent() + f'char *_filename = mb25_get_c_string_temp({filename_str_id}, {temp_id});')
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
                self._unsupported(f"Unknown file mode: {stmt.mode}")
                c_mode = 'r'

            # Open the file
            code.append(self.indent() + f'if (_file_num >= 0 && _file_num <= {self.max_file_number}) {{')
            self.indent_level += 1
            code.append(self.indent() + f'file_handles[_file_num] = fopen(_filename, "{c_mode}");')
            code.append(self.indent() + f'file_modes[_file_num] = \'{stmt.mode}\';')
            code.append(self.indent() + 'if (!file_handles[_file_num]) {')
            self.indent_level += 1
            code.append(self.indent() + 'mb25_fail("File not found");')
            # In a real implementation, should trigger ON ERROR GOTO if set
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')

            # No free needed - temp string will be GC'd
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
        else:
            self._unsupported("OPEN requires string filename")
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
            code.append(self.indent() + 'if (file_record_buffers[_i]) { free(file_record_buffers[_i]); file_record_buffers[_i] = NULL; }')
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
                code.append(self.indent() + 'if (file_record_buffers[_file_num]) { free(file_record_buffers[_file_num]); file_record_buffers[_file_num] = NULL; }')
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
            code.append(self.indent() + f'mb25_fail("File not open");')
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
                    self._unsupported("Complex prompt expressions not yet supported")

                code.append(self.indent() + f'mb25_print_cstr("{self._escape_string(prompt_str)}");')

        # LINE INPUT always reads a string into a string variable
        var_type = self._get_expression_type(stmt.variable)
        if var_type != VarType.STRING:
            self._unsupported("LINE INPUT requires a string variable")
            return [self.indent() + '/* LINE INPUT requires a string variable */']

        # String input - read entire line including spaces
        var_str_id = self._string_var_id(stmt.variable)
        code.append(self.indent() + f'if (!({self._read_line(input_stream)})) {{')
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
        code.append(self.indent() + 'mb25_chomp(input_buffer);')
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

        if not stmt.file_number:
            code.append(self.indent() + 'mb25_set_col(0);  /* Enter moved the cursor to column 0 */')
        return code

    def _generate_kill(self, stmt: KillStatementNode) -> List[str]:
        """Generate KILL statement - delete file"""
        code = []

        # Generate the filename expression (must be a string)
        if self._get_expression_type(stmt.filename) != VarType.STRING:
            self._unsupported("KILL requires a string filename")
            return [self.indent() + '/* KILL requires a string filename */']

        filename_str_id = self._generate_string_expression(stmt.filename)
        temp_id = self._get_temp_string_id()

        code.append(self.indent() + '{')
        self.indent_level += 1
        code.append(self.indent() + f'char *_filename = mb25_get_c_string_temp({filename_str_id}, {temp_id});')
        code.append(self.indent() + 'if (_filename) {')
        self.indent_level += 1
        code.append(self.indent() + 'if (remove(_filename) != 0) {')
        self.indent_level += 1
        code.append(self.indent() + 'mb25_fail("File not found");')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        # No free needed - temp string will be GC'd
        self.indent_level -= 1
        code.append(self.indent() + '}')
        self.indent_level -= 1
        code.append(self.indent() + '}')

        return code

    def _generate_mid_assignment(self, stmt: MidAssignmentStatementNode) -> List[str]:
        """Generate MID$ statement - replace substring in string variable"""
        code = []

        # Get the string variable ID
        if not isinstance(stmt.string_var, VariableNode):
            self._unsupported("MID$ statement requires a string variable")
            return [self.indent() + '/* MID$ requires string variable */']

        var_str_id = self._string_var_id(stmt.string_var)

        # Get the replacement value
        if self._get_expression_type(stmt.value) != VarType.STRING:
            self._unsupported("MID$ assignment requires string value")
            return [self.indent() + '/* MID$ requires string value */']

        value_str_expr = self._generate_string_expression(stmt.value)

        # Generate start position and length
        start_expr = self._integer_value(stmt.start)
        length_expr = self._integer_value(stmt.length) if stmt.length is not None else '255'

        code.append(self.indent() + '{')
        self.indent_level += 1

        # Get current string data
        code.append(self.indent() + f'uint8_t *_data = mb25_get_data({var_str_id});')
        code.append(self.indent() + f'uint16_t _len = mb25_get_length({var_str_id});')

        # Get replacement string using temp pool (no malloc!)
        temp_id = self._get_temp_string_id()
        code.append(self.indent() + f'char *_repl = mb25_get_c_string_temp({value_str_expr}, {temp_id});')
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

        # No free needed - temp string will be GC'd
        self.indent_level -= 1
        code.append(self.indent() + '}')
        self.indent_level -= 1
        code.append(self.indent() + '}')

        return code

    def _generate_print_using(self, stmt: PrintUsingStatementNode) -> List[str]:
        """PRINT USING is not supported.

        The code that this backend used to write for it printed the text %.*f
        for most formats (the uc80 printf has no '*' width) and got the field
        width wrong for the others, so a program that used it compiled to wrong
        output without a message.
        """
        self._unsupported("PRINT USING (the C backend has no formatter for it; "
                          "use the interpreter, or compile to JavaScript)")
        return []

    def _generate_write(self, stmt: WriteStatementNode) -> List[str]:
        """Generate WRITE statement - values separated by commas, strings quoted"""
        code = []
        if stmt.file_number:
            code.extend(self._open_output_file(stmt.file_number))

        for i, expr in enumerate(stmt.expressions):
            if i > 0:
                code.append(self.indent() + 'mb25_putc(\',\');')
            if self._get_expression_type(expr) == VarType.STRING:
                code.append(self.indent() + 'mb25_putc(\'"\');')
                code.append(self.indent() + self._print_string(expr))
                code.append(self.indent() + 'mb25_putc(\'"\');')
            else:
                code.append(self.indent() + self._print_number(expr, write=True))

        error_code = self._write_error_code(stmt)
        if error_code:
            # The items and a ',' go out with no end of line, then the error
            if stmt.expressions:
                code.append(self.indent() + 'mb25_putc(\',\');')
            if stmt.file_number:
                code.append(self.indent() + 'mb25_set_out(NULL);')
            message = 'Missing operand' if error_code == 22 else 'Syntax error'
            code.append(self.indent() + f'mb25_fail("{message}");')
            return code

        code.append(self.indent() + 'mb25_print_nl();')
        if stmt.file_number:
            code.append(self.indent() + 'mb25_set_out(NULL);')
        return code

    def _generate_variable_reference(self, var_node: VariableNode) -> str:
        """Generate C code for a variable reference (for SWAP)"""
        if var_node.subscripts:
            # Array element
            return self._generate_array_access(var_node)
        else:
            # Simple variable
            return self._mangle_variable_name(self._canonical_basic_name(var_node))

    def _constant_value(self, expr: Any):
        """The value of an expression made only of numbers and + - *, else None.

        BASIC adds, subtracts and multiplies two integers in single precision
        when the result does not fit 16 bits (PRINT 200*200 is 40000).  C ints
        would wrap, so such a constant is worked out here and written as the
        number it is.
        """
        if isinstance(expr, NumberNode):
            return expr.value
        if isinstance(expr, UnaryOpNode) and expr.operator in (TokenType.MINUS, TokenType.PLUS):
            v = self._constant_value(expr.operand)
            if v is None:
                return None
            return -v if expr.operator == TokenType.MINUS else v
        if isinstance(expr, BinaryOpNode) and expr.operator in (
                TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY):
            a = self._constant_value(expr.left)
            b = self._constant_value(expr.right)
            if a is None or b is None:
                return None
            if expr.operator == TokenType.PLUS:
                return a + b
            if expr.operator == TokenType.MINUS:
                return a - b
            return a * b
        return None

    def _number_literal(self, value: Any) -> str:
        """C text of a numeric constant: an int when it is a whole INTEGER."""
        if isinstance(value, (int, float)) and value == int(value) \
                and -32768 <= value <= 32767:
            return str(int(value))
        return repr(float(value))

    def _generate_expression(self, expr: Any) -> str:
        """Generate C code for an expression"""
        # Check if it's a string expression
        expr_type = self._get_expression_type(expr)
        if expr_type == VarType.STRING:
            # This shouldn't be called for strings - use _generate_string_expression
            self._unsupported("a string where a number is needed (Type mismatch)")
            return '0'

        if isinstance(expr, NumberNode):
            return self._number_literal(expr.value)
        elif isinstance(expr, (BinaryOpNode, UnaryOpNode)) and self._constant_value(expr) is not None:
            return self._number_literal(self._constant_value(expr))
        elif isinstance(expr, VariableNode):
            # Check if it's an array access
            if expr.subscripts:
                return self._generate_array_access(expr)
            else:
                # Check for special built-in variables
                var_upper = expr.name.upper()
                if var_upper == 'ERR':
                    self._unsupported(("ON ERROR GOTO, RESUME, ERROR, ERR and ERL (the C backend has no error "
                "handler: run-time errors end the program and ignore ON ERROR)"))
                    self.needs_error_handling = True
                    return 'basic_err'
                elif var_upper == 'ERL':
                    self._unsupported(("ON ERROR GOTO, RESUME, ERROR, ERR and ERL (the C backend has no error "
                "handler: run-time errors end the program and ignore ON ERROR)"))
                    self.needs_error_handling = True
                    return 'basic_erl'
                else:
                    return self._mangle_variable_name(self._canonical_basic_name(expr))
        elif isinstance(expr, BinaryOpNode):
            return self._generate_binary_op(expr)
        elif isinstance(expr, UnaryOpNode):
            return self._generate_unary_op(expr)
        elif isinstance(expr, FunctionCallNode):
            return self._generate_function_call(expr)
        else:
            self._unsupported(f"expression type {type(expr).__name__}")
            return '0'

    def _generate_string_expression(self, expr: Any) -> str:
        """Generate C code for a string expression"""
        if isinstance(expr, StringNode):
            # String literal - allocate as constant and return the ID
            temp_id = self._get_temp_string_id()
            # mb25_string_alloc_const allocates the string but returns error code
            # We need to call it and then use the string ID
            return f'(mb25_string_alloc_const({temp_id}, "{self._escape_string(expr.value)}"), {temp_id})'
        elif isinstance(expr, VariableNode):
            # String variable or array element
            return self._string_var_id(expr)
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
            self._unsupported(f"string expression {type(expr).__name__}")
            return '0'

    def _generate_string_function(self, expr: FunctionCallNode, result_id: Optional[str] = None) -> str:
        """Generate C for a string function: an expression whose value is the
        ID of the string that holds the result.

        result_id is the descriptor to build the result in; without one a
        temporary is taken.  The runtime builds the result in that descriptor
        and the expression evaluates to the same ID.
        """
        func_name = expr.name.upper()
        if result_id is None:
            result_id = self._get_temp_string_id()
        args = expr.arguments

        def need(count_min: int, count_max: int, label: str) -> bool:
            if not count_min <= len(args) <= count_max:
                self._unsupported(f"{label} needs {count_min}"
                                  + ("" if count_min == count_max else f" to {count_max}")
                                  + " argument(s)")
                return False
            return True

        if func_name in ('LEFT', 'RIGHT'):
            if not need(2, 2, func_name + '$'):
                return '0'
            str_arg = self._generate_string_expression(args[0])
            len_arg = self._integer_value(args[1])
            return f'(mb25_string_{func_name.lower()}({result_id}, {str_arg}, {len_arg}), {result_id})'

        elif func_name == 'MID':
            if not need(2, 3, 'MID$'):
                return '0'
            str_arg = self._generate_string_expression(args[0])
            start_arg = self._integer_value(args[1])
            len_arg = self._integer_value(args[2]) if len(args) == 3 else '255'
            return f'(mb25_string_mid({result_id}, {str_arg}, {start_arg}, {len_arg}), {result_id})'

        elif func_name == 'CHR':
            if not need(1, 1, 'CHR$'):
                return '0'
            return f'mb25_chr({result_id}, {self._integer_value(args[0])})'

        elif func_name == 'STR':
            if not need(1, 1, 'STR$'):
                return '0'
            return f'({self._str_number(args[0], result_id)}, {result_id})'

        elif func_name == 'SPACE':
            if not need(1, 1, 'SPACE$'):
                return '0'
            return f'mb25_string_of({result_id}, {self._integer_value(args[0])}, 32)'

        elif func_name in ('STRING$', 'STRING'):
            if not need(2, 2, 'STRING$'):
                return '0'
            count_arg = self._integer_value(args[0])
            if self._get_expression_type(args[1]) == VarType.STRING:
                return (f'mb25_string_of_first({result_id}, {count_arg}, '
                        f'{self._generate_string_expression(args[1])})')
            return f'mb25_string_of({result_id}, {count_arg}, {self._integer_value(args[1])})'

        elif func_name in ('HEX', 'OCT'):
            if not need(1, 1, func_name + '$'):
                return '0'
            base = 16 if func_name == 'HEX' else 8
            return f'mb25_radix({result_id}, {self._integer_value(args[0])}, {base})'

        elif func_name in ('INKEY', 'INKEY$'):
            self._unsupported("INKEY$ (the compiled program cannot poll the keyboard)")
            return '0'

        elif func_name in ('MKI$', 'MKI', 'MKS$', 'MKS', 'MKD$', 'MKD'):
            label = func_name.rstrip('$')
            if not need(1, 1, label + '$'):
                return '0'
            num_arg = self._generate_expression(args[0])
            setattr(self, f'needs_{label.lower()}_helper', True)
            return f'{label.lower().replace("mk", "mb25_mk")}({result_id}, {num_arg})'

        self._unsupported(f"string function {func_name}")
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
                self._unsupported("LEN requires 1 argument")
                return '0'
            return f'mb25_get_length({self._generate_string_expression(expr.arguments[0])})'

        elif func_name == 'ASC':
            if len(expr.arguments) != 1:
                self._unsupported("ASC requires 1 argument")
                return '0'
            return f'mb25_asc({self._generate_string_expression(expr.arguments[0])})'

        elif func_name == 'VAL':
            if len(expr.arguments) != 1:
                self._unsupported("VAL requires 1 argument")
                return '0'
            return f'mb25_val({self._generate_string_expression(expr.arguments[0])})'

        elif func_name == 'INSTR':
            # INSTR([start,] string1, string2)
            if len(expr.arguments) not in (2, 3):
                self._unsupported("INSTR requires 2 or 3 arguments")
                return '0'
            start = self._integer_value(expr.arguments[0]) if len(expr.arguments) == 3 else '1'
            str1 = self._generate_string_expression(expr.arguments[-2])
            str2 = self._generate_string_expression(expr.arguments[-1])
            return f'mb25_instr({start}, {str1}, {str2})'

        # Math functions - single argument
        elif func_name in ('ABS', 'SGN', 'INT', 'FIX', 'SIN', 'COS', 'TAN', 'ATN', 'EXP', 'LOG', 'SQR'):
            if len(expr.arguments) != 1:
                self._unsupported(f"{func_name} requires 1 argument")
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
                return f'mb25_int({arg})'
            elif func_name == 'FIX':
                # FIX truncates towards zero
                return f'mb25_fix({arg})'
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
                return f'mb25_sqr((double)({arg}))'
            else:
                self._unsupported(f"Function {func_name} not yet implemented")
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
                self._unsupported("RND requires 0 or 1 argument")
                return '0'

        # Error handling functions
        elif func_name == 'ERR':
            # ERR returns current error code
            if len(expr.arguments) != 0:
                self._unsupported("ERR takes no arguments")
                return '0'
            self._unsupported(("ON ERROR GOTO, RESUME, ERROR, ERR and ERL (the C backend has no error "
                "handler: run-time errors end the program and ignore ON ERROR)"))
            self.needs_error_handling = True
            return 'basic_err'

        elif func_name == 'ERL':
            # ERL returns error line number
            if len(expr.arguments) != 0:
                self._unsupported("ERL takes no arguments")
                return '0'
            self._unsupported(("ON ERROR GOTO, RESUME, ERROR, ERR and ERL (the C backend has no error "
                "handler: run-time errors end the program and ignore ON ERROR)"))
            self.needs_error_handling = True
            return 'basic_erl'

        # File I/O functions
        elif func_name == 'EOF':
            if len(expr.arguments) != 1:
                self._unsupported("EOF requires 1 argument (file number)")
                return '0'
            file_num = self._generate_expression(expr.arguments[0])
            self.max_file_number = max(self.max_file_number, 255)
            # EOF returns -1 (true) if end of file, 0 (false) otherwise
            return f'mb25_eof(file_handles[(int)({file_num})])'

        elif func_name == 'LOC':
            # LOC returns current position in file
            if len(expr.arguments) != 1:
                self._unsupported("LOC requires 1 argument (file number)")
                return '0'
            file_num = self._generate_expression(expr.arguments[0])
            self.max_file_number = max(self.max_file_number, 255)
            # Use ftell to get current position, cast to float for BASIC compatibility
            return f'(file_handles[(int)({file_num})] ? (float)ftell(file_handles[(int)({file_num})]) : -1)'

        elif func_name == 'LOF':
            # LOF returns length of file
            if len(expr.arguments) != 1:
                self._unsupported("LOF requires 1 argument (file number)")
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
                self._unsupported("CINT requires 1 argument")
                return '0'
            arg = self._generate_expression(expr.arguments[0])
            return f'mb25_cint({arg})'

        elif func_name == 'CSNG':
            if len(expr.arguments) != 1:
                self._unsupported("CSNG requires 1 argument")
                return '0'
            arg = self._generate_expression(expr.arguments[0])
            return f'((float)({arg}))'

        elif func_name == 'CDBL':
            if len(expr.arguments) != 1:
                self._unsupported("CDBL requires 1 argument")
                return '0'
            arg = self._generate_expression(expr.arguments[0])
            return f'((double)({arg}))'

        # Binary data conversion functions
        elif func_name == 'CVI':
            # Convert 2-byte string to integer
            if len(expr.arguments) != 1:
                self._unsupported("CVI requires 1 argument")
                return '0'
            str_arg = self._generate_string_expression(expr.arguments[0])
            # Generate helper function call for z88dk compatibility
            self.needs_cvi_helper = True
            return f'mb25_cvi({str_arg})'

        elif func_name == 'CVS':
            # Convert 4-byte string to single
            if len(expr.arguments) != 1:
                self._unsupported("CVS requires 1 argument")
                return '0'
            str_arg = self._generate_string_expression(expr.arguments[0])
            # Generate helper function call for z88dk compatibility
            self.needs_cvs_helper = True
            return f'mb25_cvs({str_arg})'

        elif func_name == 'CVD':
            # Convert 8-byte string to double
            if len(expr.arguments) != 1:
                self._unsupported("CVD requires 1 argument")
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
                self._unsupported("FRE requires 0 or 1 argument")
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
                return f'(mb25_garbage_collect(), (double)mb25_get_free_space())'
            else:
                # FRE(0) or FRE(numeric) - return total free memory
                # Evaluate the numeric argument (side effects)
                num_arg = self._generate_expression(expr.arguments[0])
                return f'(({num_arg}), 16384)  /* FRE(n) - free memory (simulated) */'

        # PEEK function - read memory byte
        elif func_name == 'PEEK':
            if len(expr.arguments) != 1:
                self._unsupported("PEEK requires 1 argument")
                return '0'
            addr = self._generate_expression(expr.arguments[0])
            # Direct memory access - read byte at address
            return f'(*((unsigned char*)((int)({addr}))))'

        # INP function - read I/O port
        elif func_name == 'INP':
            if len(expr.arguments) != 1:
                self._unsupported("INP requires 1 argument")
                return '0'
            port = self._generate_expression(expr.arguments[0])
            # z88dk provides inp() function for CP/M port I/O
            # Note: z88dk may use in() or inp() depending on target
            return f'inp((int)({port}))'

        # VARPTR function - get address of variable
        elif func_name == 'VARPTR':
            if len(expr.arguments) != 1:
                self._unsupported("VARPTR requires 1 argument")
                return '0'

            # Get the variable reference
            arg = expr.arguments[0]
            if isinstance(arg, VariableNode):
                var_name = arg.name.upper()
                # Get C variable name
                if var_name.endswith('$'):
                    # String variable - return address of string ID (stored as int)
                    # In our implementation, string variables store an int ID
                    c_var = self._mangle_variable_name(var_name)
                    return f'(float)((long)&{c_var})'
                elif var_name.endswith('%'):
                    # Integer variable
                    c_var = self._mangle_variable_name(var_name)
                    return f'(float)((long)&{c_var})'
                else:
                    # Float variable
                    c_var = self._mangle_variable_name(var_name)
                    return f'(float)((long)&{c_var})'
            elif isinstance(arg, ArrayAccessNode):
                # Array element - get address of specific element
                array_name = arg.array_name.upper()
                # For arrays, we need to calculate the element address
                c_array = self._mangle_variable_name(array_name)
                subscripts = [self._generate_expression(sub) for sub in arg.subscripts]
                subscript_str = ']['.join(subscripts)
                return f'(float)((long)&{c_array}[{subscript_str}])'
            else:
                self._unsupported("VARPTR requires a variable or array element")
                return '0'

        # USR function - call user machine language function
        elif func_name == 'USR':
            if len(expr.arguments) < 1:
                self._unsupported("USR requires at least 1 argument (address)")
                return '0'

            # First argument is the address to call
            addr = self._generate_expression(expr.arguments[0])

            if len(expr.arguments) == 1:
                # USR(addr) - call with no arguments, returns float
                return f'((float (*)(void))(int)({addr}))()'
            else:
                # USR(addr, arg1, arg2, ...) - call with arguments
                # In MBASIC, USR can take one argument passed in a register
                # For simplicity, we'll pass one float argument
                arg1 = self._generate_expression(expr.arguments[1])
                if len(expr.arguments) > 2:
                    self._unsupported("USR with multiple arguments not fully supported - only first argument passed")
                return f'((float (*)(float))(int)({addr}))({arg1})'

        else:
            # Other numeric functions not yet implemented
            self._unsupported(f"Function {func_name} not yet implemented")
            return '0'

    def _get_string_id(self, var_name: str) -> str:
        """Get the string ID for a variable"""
        upper_name = var_name.upper()
        if upper_name in self.string_ids:
            return f'STR_{self._mangle_string_name(upper_name)}'
        else:
            self._unsupported(f"Unknown string variable: {var_name}")
            return '0'

    def _get_temp_string_id(self) -> str:
        """Allocate a temporary string ID"""
        if self.temp_string_count == 0:
            self._unsupported("internal error: a temporary string was needed but none was reserved")
        # Reuse temporaries within a statement
        base_temp = self.string_ids.get('_TEMP_BASE', 0)
        # Use modulo to wrap around and reuse temps
        temp_offset = (self.next_temp_id - base_temp) % max(1, self.temp_string_count)
        temp_id = base_temp + temp_offset
        self.next_temp_id += 1
        return str(temp_id)

    def _reset_temp_strings(self):
        """Reset temporary string allocation for next statement"""
        self.next_temp_id = self.string_ids.get('_TEMP_BASE', 0)

    def _escape_string(self, s: str) -> str:
        """Escape text for a C string literal.

        uc80 has two faults in string literals, and this works around both:
        - It halves every run of backslashes, so one backslash needs four.
        - It deletes the word "near" (a leftover keyword): "a near b" comes out
          as "a  b".  Writing the word as two adjacent literals avoids that.
        Control characters and characters above 126 are written as octal
        escapes, which end after three digits and so cannot swallow the next
        character the way hexadecimal escapes can.
        """
        uc80 = self.dialect == 'uc80'
        out = []
        for ch in s:
            if ch == '\\':
                out.append('\\\\\\\\' if uc80 else '\\\\')
            elif ch == '"':
                out.append('\\"')
            elif ch == '\n':
                out.append('\\n')
            elif ch == '\r':
                out.append('\\r')
            elif ch == '\t':
                out.append('\\t')
            elif ord(ch) < 32 or ord(ch) >= 127:
                out.append('\\%03o' % (ord(ch) & 0xFF))
            else:
                out.append(ch)
        text = ''.join(out)
        if uc80:
            text = re.sub(r'\bnear\b', 'ne" "ar', text)
        return text

    def _generate_string_function_statement(self, expr: FunctionCallNode, result_id: str) -> str:
        """Generate C that builds a string function's result directly in a variable"""
        return self._generate_string_function(expr, result_id)

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
            return self._string_var_id(expr)
        else:
            return self._generate_string_expression(expr)

    def _generate_binary_op(self, expr: BinaryOpNode) -> str:
        """Generate C code for binary operation

        BASIC differs from C in several places:
        - / always divides in floating point (5/2 is 2.5), \\ and MOD work on
          integers rounded the way CINT rounds.
        - A comparison is -1 when true (not 1), and AND, OR, XOR, EQV, IMP
          and NOT work bit by bit on 16-bit integers.
        - Strings compare byte by byte.
        """
        op = expr.operator
        c_compare = {
            TokenType.EQUAL: '==', TokenType.NOT_EQUAL: '!=',
            TokenType.LESS_THAN: '<', TokenType.LESS_EQUAL: '<=',
            TokenType.GREATER_THAN: '>', TokenType.GREATER_EQUAL: '>=',
        }
        left_type = self._get_expression_type(expr.left)
        right_type = self._get_expression_type(expr.right)

        if left_type == VarType.STRING or right_type == VarType.STRING:
            if left_type != right_type or op not in c_compare:
                self._unsupported("a string mixed with a number in an expression "
                                  "(Type mismatch)")
                return '0'
            left = self._generate_string_expression(expr.left)
            right = self._generate_string_expression(expr.right)
            return f'(-(mb25_string_compare({left}, {right}) {c_compare[op]} 0))'

        if op in c_compare:
            left = self._generate_expression(expr.left)
            right = self._generate_expression(expr.right)
            both_int = left_type == VarType.INTEGER and right_type == VarType.INTEGER
            return f'(-({self._compare(left, c_compare[op], right, both_int)}))'

        if op in (TokenType.AND, TokenType.OR, TokenType.XOR, TokenType.EQV, TokenType.IMP,
                  TokenType.MOD, TokenType.BACKSLASH):
            a = self._integer_value(expr.left, checked=True)
            b = self._integer_value(expr.right, checked=True)
            return {
                TokenType.AND: f'({a} & {b})',
                TokenType.OR: f'({a} | {b})',
                TokenType.XOR: f'({a} ^ {b})',
                TokenType.EQV: f'(~({a} ^ {b}))',
                TokenType.IMP: f'((~{a}) | {b})',
                TokenType.MOD: f'mb25_imod({a}, {b})',
                TokenType.BACKSLASH: f'mb25_idiv({a}, {b})',
            }[op]

        left = self._generate_expression(expr.left)
        right = self._generate_expression(expr.right)
        if op == TokenType.DIVIDE:
            return f'((double)({left}) / ({right}))'
        if op == TokenType.POWER:
            return f'mb25_pow((double)({left}), (double)({right}))'
        c_op = {TokenType.PLUS: '+', TokenType.MINUS: '-', TokenType.MULTIPLY: '*'}.get(op)
        if c_op is None:
            self._unsupported(f"operator {getattr(op, 'name', op)}")
            return '0'
        # uc80 miscompiles a float times an int constant such as 8 or 16 (the
        # product comes out as the float itself), so a constant that meets a
        # float is written as a float constant.
        if left_type == VarType.INTEGER and right_type != VarType.INTEGER \
                and self._constant_value(expr.left) is not None:
            left = repr(float(self._constant_value(expr.left)))
        elif right_type == VarType.INTEGER and left_type != VarType.INTEGER \
                and self._constant_value(expr.right) is not None:
            right = repr(float(self._constant_value(expr.right)))
        return f'({left} {c_op} {right})'

    def _compare(self, left: str, c_op: str, right: str, both_int: bool) -> str:
        """C comparison of two numbers.

        uc80 compares two negative floats the wrong way round (-30 > -27 is
        true), so an ordering test on floats looks at the sign of the difference
        instead.  Equality is not affected.  Two ints compare directly.
        """
        if both_int or c_op in ('==', '!='):
            return f'{left} {c_op} {right}'
        return f'((double)({left}) - (double)({right})) {c_op} 0'

    def _generate_unary_op(self, expr: UnaryOpNode) -> str:
        """Generate C code for unary operation"""
        if expr.operator == TokenType.NOT:
            return f'(~{self._integer_value(expr.operand, checked=True)})'
        operand = self._generate_expression(expr.operand)
        if expr.operator == TokenType.MINUS:
            return f'(-{operand})'
        elif expr.operator == TokenType.PLUS:
            return f'(+{operand})'
        self._unsupported(f"unary operator {getattr(expr.operator, 'name', expr.operator)}")
        return '0'

    def _generate_on_error(self, stmt: OnErrorStatementNode) -> List[str]:
        """Generate ON ERROR GOTO/GOSUB statement"""
        code = []

        if stmt.line_number == 0:
            # ON ERROR GOTO 0 - disable error handling
            code.append(self.indent() + 'error_handler = 0;  /* Disable error handling */')
        else:
            self._unsupported(("ON ERROR GOTO, RESUME, ERROR, ERR and ERL (the C backend has no error "
                "handler: run-time errors end the program and ignore ON ERROR)"))
            # ON ERROR GOTO line_number - set error handler
            code.append(self.indent() + f'error_handler = {stmt.line_number};  /* Set error handler */')
            # Ensure the target line has a label
            self.line_labels.add(stmt.line_number)

        return code

    def _generate_resume(self, stmt: ResumeStatementNode) -> List[str]:
        """Generate RESUME statement"""
        code = []
        self._unsupported(("ON ERROR GOTO, RESUME, ERROR, ERR and ERL (the C backend has no error "
                "handler: run-time errors end the program and ignore ON ERROR)"))

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
        self._unsupported(("ON ERROR GOTO, RESUME, ERROR, ERR and ERL (the C backend has no error "
                "handler: run-time errors end the program and ignore ON ERROR)"))

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
        code.append(self.indent() + '/* FIELD statement - define random access record layout */')

        file_num = self._generate_expression(stmt.file_number)

        code.append(self.indent() + '{')
        self.indent_level += 1
        code.append(self.indent() + f'int _file_num = (int)({file_num});')
        code.append(self.indent() + f'if (_file_num >= 0 && _file_num <= {self.max_file_number}) {{')
        self.indent_level += 1

        # Calculate total record size and track field mappings
        code.append(self.indent() + 'int _rec_size = 0;')
        code.append(self.indent() + 'int _field_offset = 0;')
        code.append(self.indent() + 'int _field_width;')

        for width, var in stmt.fields:
            width_expr = self._generate_expression(width)
            code.append(self.indent() + f'_field_width = (int)({width_expr});')
            code.append(self.indent() + '_rec_size += _field_width;')

            # Map this variable to the field
            # Check if it's a string variable (has $ suffix)
            if var.name.endswith('$') or (hasattr(var, 'type_suffix') and var.type_suffix == '$'):
                var_id = self._string_var_id(var)
                # Extract the numeric ID from STR_VARNAME
                code.append(self.indent() + f'field_var_files[{var_id}] = _file_num;')
                code.append(self.indent() + f'field_var_offsets[{var_id}] = _field_offset;')
                code.append(self.indent() + f'field_var_widths[{var_id}] = _field_width;')

            code.append(self.indent() + '_field_offset += _field_width;')

        # Allocate record buffer if not already allocated or size changed
        code.append(self.indent() + 'if (file_record_buffers[_file_num] == NULL || file_record_sizes[_file_num] != _rec_size) {')
        self.indent_level += 1
        code.append(self.indent() + 'if (file_record_buffers[_file_num]) free(file_record_buffers[_file_num]);')
        code.append(self.indent() + 'file_record_buffers[_file_num] = (unsigned char *)malloc(_rec_size);')
        code.append(self.indent() + 'file_record_sizes[_file_num] = _rec_size;')
        code.append(self.indent() + 'if (file_record_buffers[_file_num]) memset(file_record_buffers[_file_num], 0, _rec_size);')
        self.indent_level -= 1
        code.append(self.indent() + '}')

        code.append(self.indent() + f'/* Record size: {len(stmt.fields)} fields, total {{}}_rec_size{{}} bytes */')

        self.indent_level -= 1
        code.append(self.indent() + '}')
        self.indent_level -= 1
        code.append(self.indent() + '}')

        return code

    def _generate_get(self, stmt: GetStatementNode) -> List[str]:
        """Generate GET statement for random access files"""
        code = []
        code.append(self.indent() + '/* GET statement - read random access record */')

        file_num = self._generate_expression(stmt.file_number)
        self.max_file_number = max(self.max_file_number, 255)

        code.append(self.indent() + '{')
        self.indent_level += 1
        code.append(self.indent() + f'int _file_num = (int)({file_num});')

        # Check file is open and buffer is allocated
        code.append(self.indent() + f'if (_file_num >= 0 && _file_num <= {self.max_file_number} && ')
        code.append('file_handles[_file_num] != NULL && file_record_buffers[_file_num] != NULL) {')
        self.indent_level += 1

        # Determine record number
        if stmt.record_number:
            rec_num = self._generate_expression(stmt.record_number)
            code.append(self.indent() + f'long _rec_num = (long)({rec_num});')
        else:
            # Use next record (current + 1)
            code.append(self.indent() + 'long _rec_num = file_record_numbers[_file_num] + 1;')

        # Seek to record position (records are 1-based)
        code.append(self.indent() + 'long _file_pos = (_rec_num - 1) * file_record_sizes[_file_num];')
        code.append(self.indent() + 'fseek(file_handles[_file_num], _file_pos, SEEK_SET);')

        # Read record into buffer
        code.append(self.indent() + 'size_t _bytes_read = fread(file_record_buffers[_file_num], 1, ')
        code.append('file_record_sizes[_file_num], file_handles[_file_num]);')

        # Update current record number
        code.append(self.indent() + 'file_record_numbers[_file_num] = _rec_num;')

        # Pad with zeros if short read (end of file)
        code.append(self.indent() + 'if (_bytes_read < file_record_sizes[_file_num]) {')
        self.indent_level += 1
        code.append(self.indent() + 'memset(file_record_buffers[_file_num] + _bytes_read, 0, ')
        code.append('file_record_sizes[_file_num] - _bytes_read);')
        self.indent_level -= 1
        code.append(self.indent() + '}')

        # Copy buffer contents to field variables
        if self.string_count > 0:
            code.append(self.indent() + '/* Copy buffer contents to field variables */')
            code.append(self.indent() + 'int _i;')
            code.append(self.indent() + f'for (_i = 0; _i < {self.string_count}; _i++) {{')
            self.indent_level += 1
            code.append(self.indent() + 'if (field_var_files[_i] == _file_num) {')
            self.indent_level += 1
            code.append(self.indent() + 'int _offset = field_var_offsets[_i];')
            code.append(self.indent() + 'int _width = field_var_widths[_i];')
            code.append(self.indent() + 'unsigned char *_src = file_record_buffers[_file_num] + _offset;')
            code.append(self.indent() + 'mb25_string_set_from_buf(_i, _src, _width);')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')

        self.indent_level -= 1
        code.append(self.indent() + '}')
        self.indent_level -= 1
        code.append(self.indent() + '}')

        return code

    def _generate_put(self, stmt: PutStatementNode) -> List[str]:
        """Generate PUT statement for random access files"""
        code = []
        code.append(self.indent() + '/* PUT statement - write random access record */')

        file_num = self._generate_expression(stmt.file_number)
        self.max_file_number = max(self.max_file_number, 255)

        code.append(self.indent() + '{')
        self.indent_level += 1
        code.append(self.indent() + f'int _file_num = (int)({file_num});')

        # Check file is open and buffer is allocated
        code.append(self.indent() + f'if (_file_num >= 0 && _file_num <= {self.max_file_number} && ')
        code.append('file_handles[_file_num] != NULL && file_record_buffers[_file_num] != NULL) {')
        self.indent_level += 1

        # Determine record number
        if stmt.record_number:
            rec_num = self._generate_expression(stmt.record_number)
            code.append(self.indent() + f'long _rec_num = (long)({rec_num});')
        else:
            # Use current record
            code.append(self.indent() + 'long _rec_num = file_record_numbers[_file_num];')
            code.append(self.indent() + 'if (_rec_num == 0) _rec_num = 1;  /* Default to record 1 */')

        # Seek to record position (records are 1-based)
        code.append(self.indent() + 'long _file_pos = (_rec_num - 1) * file_record_sizes[_file_num];')
        code.append(self.indent() + 'fseek(file_handles[_file_num], _file_pos, SEEK_SET);')

        # Write buffer to file
        code.append(self.indent() + 'fwrite(file_record_buffers[_file_num], 1, ')
        code.append('file_record_sizes[_file_num], file_handles[_file_num]);')

        # Update current record number
        code.append(self.indent() + 'file_record_numbers[_file_num] = _rec_num;')

        self.indent_level -= 1
        code.append(self.indent() + '}')
        self.indent_level -= 1
        code.append(self.indent() + '}')

        return code

    def _generate_lset(self, stmt: LsetStatementNode) -> List[str]:
        """Generate LSET statement - left-justify string in field"""
        code = []
        code.append(self.indent() + '/* LSET - left justify in field */')

        var_id = self._string_var_id(stmt.variable)
        value_expr = self._generate_string_expression(stmt.expression)

        # Check if this is a field variable
        code.append(self.indent() + '{')
        self.indent_level += 1
        code.append(self.indent() + f'int _str_id = {var_id};')
        code.append(self.indent() + 'if (field_var_files[_str_id] >= 0) {')
        self.indent_level += 1
        code.append(self.indent() + '/* Field variable - write to record buffer */')
        code.append(self.indent() + 'int _file_num = field_var_files[_str_id];')
        code.append(self.indent() + 'int _offset = field_var_offsets[_str_id];')
        code.append(self.indent() + 'int _width = field_var_widths[_str_id];')
        code.append(self.indent() + f'mb25_string *_src = &mb25_strings[{value_expr}];')
        code.append(self.indent() + 'unsigned char *_dest = file_record_buffers[_file_num] + _offset;')
        code.append(self.indent() + 'int _copy_len = _src->len < _width ? _src->len : _width;')
        code.append(self.indent() + '/* Copy string data (left-justified) */')
        code.append(self.indent() + 'memcpy(_dest, _src->data, _copy_len);')
        code.append(self.indent() + '/* Pad with spaces */')
        code.append(self.indent() + 'if (_copy_len < _width) memset(_dest + _copy_len, \' \', _width - _copy_len);')
        self.indent_level -= 1
        code.append(self.indent() + '} else {')
        self.indent_level += 1
        code.append(self.indent() + '/* Regular variable - just copy */')
        code.append(self.indent() + f'mb25_string_copy({var_id}, {value_expr});')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        self.indent_level -= 1
        code.append(self.indent() + '}')

        return code

    def _generate_rset(self, stmt: RsetStatementNode) -> List[str]:
        """Generate RSET statement - right-justify string in field"""
        code = []
        code.append(self.indent() + '/* RSET - right justify in field */')

        var_id = self._string_var_id(stmt.variable)
        value_expr = self._generate_string_expression(stmt.expression)

        # Check if this is a field variable
        code.append(self.indent() + '{')
        self.indent_level += 1
        code.append(self.indent() + f'int _str_id = {var_id};')
        code.append(self.indent() + 'if (field_var_files[_str_id] >= 0) {')
        self.indent_level += 1
        code.append(self.indent() + '/* Field variable - write to record buffer */')
        code.append(self.indent() + 'int _file_num = field_var_files[_str_id];')
        code.append(self.indent() + 'int _offset = field_var_offsets[_str_id];')
        code.append(self.indent() + 'int _width = field_var_widths[_str_id];')
        code.append(self.indent() + f'mb25_string *_src = &mb25_strings[{value_expr}];')
        code.append(self.indent() + 'unsigned char *_dest = file_record_buffers[_file_num] + _offset;')
        code.append(self.indent() + 'int _copy_len = _src->len < _width ? _src->len : _width;')
        code.append(self.indent() + '/* Pad with spaces (right-justify) */')
        code.append(self.indent() + 'int _pad_len = _width - _copy_len;')
        code.append(self.indent() + 'if (_pad_len > 0) memset(_dest, \' \', _pad_len);')
        code.append(self.indent() + '/* Copy string data */')
        code.append(self.indent() + 'memcpy(_dest + _pad_len, _src->data, _copy_len);')
        self.indent_level -= 1
        code.append(self.indent() + '} else {')
        self.indent_level += 1
        code.append(self.indent() + '/* Regular variable - just copy */')
        code.append(self.indent() + f'mb25_string_copy({var_id}, {value_expr});')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        self.indent_level -= 1
        code.append(self.indent() + '}')

        return code

    def _generate_erase(self, stmt: EraseStatementNode) -> List[str]:
        """Generate ERASE statement: empty the named arrays.

        An interpreted ERASE frees the array so that a later DIM can size it
        again.  Compiled arrays have a fixed size, so ERASE here clears the
        elements (0, or the empty string) and a later DIM of the same array
        changes nothing.  A DIM with another size is refused by the semantic
        analyzer.
        """
        code = []
        for name in stmt.array_names:
            name = name.upper()
            keys = [k for k in self.array_ranks
                    if k == name or (name[-1] not in '$%!#' and k[:-1] == name)]
            if not keys:
                self._unsupported(f"ERASE {name}: no such array")
                continue
            key = keys[0]
            total = self._array_total(key)
            if self._key_type(key) == VarType.STRING:
                base = self._get_string_id(key + '()')
                code.append(self.indent() + f'{{ int _e; for (_e = 0; _e < {total}; _e++) mb25_string_clear({base} + _e); }}')
            else:
                c_name = self._mangle_variable_name(key) + '_arr'
                code.append(self.indent() + f'memset({c_name}, 0, sizeof({c_name}));')
        return code

    def _generate_reset(self, stmt: ResetStatementNode) -> List[str]:
        """Generate RESET statement - close all open files

        RESET is equivalent to CLOSE with no arguments.
        It closes all open files and frees associated buffers.
        """
        code = []
        if self.max_file_number > 0:
            code.append(self.indent() + '/* RESET - close all files */')
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
            code.append(self.indent() + 'if (file_record_buffers[_i]) { free(file_record_buffers[_i]); file_record_buffers[_i] = NULL; }')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
        else:
            code.append(self.indent() + '/* RESET - no files to close */')
        return code

    def _generate_name(self, stmt: NameStatementNode) -> List[str]:
        """Generate NAME statement - rename file

        NAME oldfile$ AS newfile$ - renames a file on disk
        Uses C rename() function
        """
        code = []
        old_filename = self._generate_expression(stmt.old_filename)
        new_filename = self._generate_expression(stmt.new_filename)

        code.append(self.indent() + '{')
        self.indent_level += 1

        # For string expressions, need to extract the C string
        code.append(self.indent() + 'char _old_name[256];')
        code.append(self.indent() + 'char _new_name[256];')
        code.append(self.indent() + f'mb25_get_string_data({old_filename}, _old_name, sizeof(_old_name));')
        code.append(self.indent() + f'mb25_get_string_data({new_filename}, _new_name, sizeof(_new_name));')
        code.append(self.indent() + 'if (rename(_old_name, _new_name) != 0) {')
        self.indent_level += 1
        code.append(self.indent() + 'mb25_fail("File not found");')
        self.indent_level -= 1
        code.append(self.indent() + '}')

        self.indent_level -= 1
        code.append(self.indent() + '}')
        return code

    def _generate_files(self, stmt: FilesStatementNode) -> List[str]:
        """Generate FILES statement - directory listing

        FILES is a CP/M-specific feature that lists files.
        This would require BDOS calls which are beyond the scope of the compiler.
        We generate a comment and warning instead.
        """
        code = []
        code.append(self.indent() + '/* FILES statement not implemented - requires CP/M BDOS calls */')
        if stmt.filespec:
            filespec = self._generate_expression(stmt.filespec)
            code.append(self.indent() + f'/* Would list files matching: {filespec} */')
        else:
            code.append(self.indent() + '/* Would list all files */')
        self._unsupported("FILES statement not implemented - requires CP/M BDOS calls")
        return code

    def _generate_width(self, stmt: WidthStatementNode) -> List[str]:
        """Generate WIDTH statement - set output width

        WIDTH sets the line width for console or printer output.
        In compiled code, this is typically a terminal/display feature
        and cannot be easily implemented portably.
        """
        code = []
        width = self._generate_expression(stmt.width)
        code.append(self.indent() + f'/* WIDTH {width} - not implemented (display feature) */')
        if stmt.device:
            device = self._generate_expression(stmt.device)
            code.append(self.indent() + f'/* Device: {device} */')
        self.warnings.append("WIDTH statement not implemented in compiled code")
        return code

    def _generate_lprint(self, stmt: LprintStatementNode) -> List[str]:
        """Generate LPRINT statement.

        The compiled program has no printer, so LPRINT writes to the console
        exactly as PRINT does.
        """
        return self._generate_print(PrintStatementNode(
            expressions=stmt.expressions, separators=stmt.separators,
            file_number=stmt.file_number))

    def _generate_clear(self, stmt: ClearStatementNode) -> List[str]:
        """Generate CLEAR statement - clear variables and set memory limits

        CLEAR [string_space] [, stack_space]

        In the interpreter, CLEAR:
        - Closes all files
        - Clears all variables
        - Resets the stack
        - Optionally sets string space and stack space

        In compiled code, we cannot dynamically clear variables or adjust memory.
        We can only close files.
        """
        code = []
        code.append(self.indent() + '/* CLEAR - close all files (variable clearing not supported in compiled code) */')

        # Close all files (same as RESET) - only if files are actually used
        if self.max_file_number > 0:
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
            code.append(self.indent() + 'if (file_record_buffers[_i]) { free(file_record_buffers[_i]); file_record_buffers[_i] = NULL; }')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')

        if stmt.string_space or stmt.stack_space:
            msg = "CLEAR memory parameters ignored in compiled code"
            if stmt.string_space:
                msg += f" (string_space={self._generate_expression(stmt.string_space)})"
            if stmt.stack_space:
                msg += f" (stack_space={self._generate_expression(stmt.stack_space)})"
            self.warnings.append(msg)

        return code

    def _generate_call(self, stmt: CallStatementNode) -> List[str]:
        """Generate CALL statement - call machine language routine

        CALL address - Calls machine code at the specified address
        CALL routine(args) - Extended syntax with arguments

        We generate a function pointer call. This is dangerous but matches BASIC behavior.
        """
        code = []

        if stmt.arguments:
            # Extended syntax with arguments - not standard MBASIC 5.21
            self.warnings.append("CALL with arguments is not standard MBASIC 5.21 - may not work as expected")
            target = self._generate_expression(stmt.target)
            args = ', '.join(self._generate_expression(arg) for arg in stmt.arguments)
            code.append(self.indent() + f'/* CALL with arguments not fully supported */')
            code.append(self.indent() + f'((void (*)({", ".join(["float"] * len(stmt.arguments))}))(int)({target}))({args});')
        else:
            # Standard MBASIC 5.21 syntax - CALL address
            target = self._generate_expression(stmt.target)
            code.append(self.indent() + f'/* CALL machine language routine at address */')
            code.append(self.indent() + f'((void (*)(void))(int)({target}))();')

        return code

    def _generate_chain(self, stmt: ChainStatementNode) -> List[str]:
        """Generate CHAIN statement - chain to another program using CP/M warm boot

        Implements basic CHAIN "filename" using CP/M technique:
        1. Write command to CP/M command buffer at 0x0080
        2. Perform warm boot by jumping to 0x0000
        3. CCP reads 0x0080 and executes the command

        Note: MERGE, line number, ALL, and DELETE options are not supported
        (matching Microsoft BASCOM behavior - it only supports basic CHAIN "filename")
        """
        code = []

        # Warn about unsupported options (Microsoft BASCOM doesn't support these either)
        if stmt.merge:
            code.append(self.indent() + '/* MERGE option not supported in compiled code */')
            self._unsupported("CHAIN MERGE not supported - Microsoft BASCOM doesn't support this either")
        if stmt.start_line:
            code.append(self.indent() + '/* Start line not supported in compiled code */')
            self._unsupported("CHAIN line number not supported - Microsoft BASCOM doesn't support this either")
        if stmt.all_flag:
            code.append(self.indent() + '/* ALL option not supported in compiled code */')
            self._unsupported("CHAIN ALL not supported - use COMMON in interpreter mode")
        if stmt.delete_range:
            code.append(self.indent() + '/* DELETE option not supported in compiled code */')
            self._unsupported("CHAIN DELETE not supported - Microsoft BASCOM doesn't support this either")

        # Get filename as C string (need to handle string expression)
        if self._get_expression_type(stmt.filename) == VarType.STRING:
            filename_str_id = self._generate_string_expression(stmt.filename)
            temp_id = self._get_temp_string_id()
        else:
            self._unsupported("CHAIN requires string filename")
            code.append(self.indent() + '/* ERROR: CHAIN requires string filename */')
            return code

        code.append(self.indent() + '/* CHAIN to another program using CP/M warm boot */')
        code.append(self.indent() + '{')
        self.indent_level += 1

        # Generate code to build command string with .COM extension if needed
        code.append(self.indent() + 'char cmd_buf[128];')
        code.append(self.indent() + f'char *filename = mb25_get_c_string_temp({filename_str_id}, {temp_id});')
        code.append(self.indent() + 'int len;')
        code.append(self.indent() + 'char *p;')
        code.append(self.indent())

        # Build command - convert to 8.3 format with .COM extension
        code.append(self.indent() + '/* Convert to CP/M 8.3 format (8 chars name, 3 chars extension) */')
        code.append(self.indent() + 'p = strchr(filename, \'.\');')
        code.append(self.indent() + 'if (p) {')
        self.indent_level += 1
        code.append(self.indent() + '/* Has extension - copy name (max 8 chars) and extension (max 3 chars) */')
        code.append(self.indent() + 'int name_len = p - filename;')
        code.append(self.indent() + 'if (name_len > 8) name_len = 8;')
        code.append(self.indent() + 'strncpy(cmd_buf, filename, name_len);')
        code.append(self.indent() + 'cmd_buf[name_len] = \'.\';')
        code.append(self.indent() + 'len = name_len + 1;')
        code.append(self.indent() + '/* Copy extension (max 3 chars) */')
        code.append(self.indent() + 'int ext_len = strlen(p + 1);')
        code.append(self.indent() + 'if (ext_len > 3) ext_len = 3;')
        code.append(self.indent() + 'strncpy(cmd_buf + len, p + 1, ext_len);')
        code.append(self.indent() + 'len += ext_len;')
        code.append(self.indent() + 'cmd_buf[len] = 0;')
        self.indent_level -= 1
        code.append(self.indent() + '} else {')
        self.indent_level += 1
        code.append(self.indent() + '/* No extension - copy name (max 8 chars) and add .COM */')
        code.append(self.indent() + 'len = strlen(filename);')
        code.append(self.indent() + 'if (len > 8) len = 8;')
        code.append(self.indent() + 'strncpy(cmd_buf, filename, len);')
        code.append(self.indent() + 'strcpy(cmd_buf + len, ".COM");')
        code.append(self.indent() + 'len += 4;')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent())

        # Convert to uppercase (CP/M convention) - MUST be uppercase!
        code.append(self.indent() + '/* Convert to UPPERCASE (required by CP/M) */')
        code.append(self.indent() + 'for (p = cmd_buf; *p; p++) {')
        self.indent_level += 1
        code.append(self.indent() + 'if (*p >= \'a\' && *p <= \'z\') *p -= 32;')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent())

        # Write to CP/M command buffer at 0x0080
        code.append(self.indent() + '/* Write command to CP/M command buffer at 0x0080 */')
        code.append(self.indent() + '((unsigned char *)0x0080)[0] = len;  /* Length byte */')
        code.append(self.indent() + 'memcpy((char *)0x0081, cmd_buf, len);  /* Command string */')
        code.append(self.indent())

        # Perform CP/M warm boot
        code.append(self.indent() + '/* Perform CP/M warm boot - CCP will execute command at 0x0080 */')
        code.append(self.indent() + '/* Jump to 0x0000 (warm boot entry point) */')
        code.append(self.indent() + '((void (*)(void))0x0000)();')
        code.append(self.indent())

        # This point should never be reached
        code.append(self.indent() + '/* Should never reach here */')

        self.indent_level -= 1
        code.append(self.indent() + '}')

        return code

    def _generate_common(self, stmt: CommonStatementNode) -> List[str]:
        """Generate COMMON statement - declare shared variables for CHAIN

        COMMON declares variables that should be passed to CHAINed programs.
        Since CHAIN doesn't work in compiled code, COMMON is also not meaningful.
        We generate a comment for documentation purposes.
        """
        code = []
        code.append(self.indent() + f'/* COMMON {", ".join(stmt.variables)} - used with CHAIN (not supported) */')
        return code
