#!/usr/bin/env python3
"""
Semantic Analyzer for Microsoft BASIC Compiler

This module performs semantic analysis on the parsed AST for compilation.
Unlike the interpreter which does runtime checking, this performs static
analysis at compile time.

Key responsibilities:
1. Build symbol tables (variables, line numbers, functions)
2. Perform constant expression evaluation (for DIM subscripts)
3. Type inference and checking
4. Validate static loop nesting (FOR/NEXT, WHILE/WEND)
5. Check line number references
6. Detect unsupported compiler features
7. Flag statements requiring compilation switches
"""

from typing import Dict, List, Set, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from ast_nodes import *


class VarType(Enum):
    """Variable types in BASIC"""
    INTEGER = 1
    SINGLE = 2
    DOUBLE = 3
    STRING = 4


class SemanticError(Exception):
    """Semantic analysis error"""
    def __init__(self, message: str, line_num: Optional[int] = None):
        self.message = message
        self.line_num = line_num
        super().__init__(f"Line {line_num}: {message}" if line_num else message)


@dataclass
class VariableInfo:
    """Information about a variable"""
    name: str
    var_type: VarType
    is_array: bool = False
    dimensions: Optional[List[int]] = None  # For arrays, stores dimension sizes
    first_use_line: Optional[int] = None
    is_parameter: bool = False  # For DEF FN parameters


@dataclass
class FunctionInfo:
    """Information about a DEF FN function"""
    name: str
    return_type: VarType
    parameters: List[str]
    definition_line: int
    body_expr: Any  # The expression AST node


@dataclass
class LoopInfo:
    """Information about a loop for nesting validation"""
    loop_type: str  # "FOR" or "WHILE"
    variable: Optional[str]  # FOR loop variable
    start_line: int


@dataclass
class SymbolTable:
    """Symbol tables for the program"""
    variables: Dict[str, VariableInfo] = field(default_factory=dict)
    functions: Dict[str, FunctionInfo] = field(default_factory=dict)
    line_numbers: Set[int] = field(default_factory=set)
    labels: Dict[str, int] = field(default_factory=dict)  # For future named labels


class CompilerFlags:
    """Flags for features requiring compilation switches"""
    def __init__(self):
        self.needs_error_handling = False  # /E switch
        self.needs_resume = False  # /X switch
        self.needs_debug = False  # /D switch
        self.has_tron_troff = False

    def get_required_switches(self) -> List[str]:
        """Get list of required compilation switches"""
        switches = []
        if self.needs_resume:
            switches.append('/X')  # /X implies /E
        elif self.needs_error_handling:
            switches.append('/E')
        if self.needs_debug or self.has_tron_troff:
            switches.append('/D')
        return switches


class ConstantEvaluator:
    """Evaluates constant expressions at compile time"""

    def __init__(self, symbols: SymbolTable):
        self.symbols = symbols
        # Runtime constant tracking: maps variable names to their known constant values
        self.runtime_constants: Dict[str, Union[int, float, str]] = {}

    def set_constant(self, var_name: str, value: Union[int, float, str]):
        """Mark a variable as having a known constant value"""
        self.runtime_constants[var_name.upper()] = value

    def clear_constant(self, var_name: str):
        """Mark a variable as no longer having a known constant value"""
        var_name_upper = var_name.upper()
        if var_name_upper in self.runtime_constants:
            del self.runtime_constants[var_name_upper]

    def evaluate(self, expr) -> Optional[Union[int, float, str]]:
        """
        Attempt to evaluate an expression as a compile-time constant.
        Returns None if expression cannot be evaluated (contains variables, etc.)
        """
        if isinstance(expr, NumberNode):
            return expr.value

        if isinstance(expr, StringNode):
            return expr.value

        # Check if it's a variable with a known constant value
        if isinstance(expr, VariableNode):
            # Only simple variables (not arrays) can be runtime constants
            if expr.subscripts is None:
                var_name = expr.name.upper()
                if var_name in self.runtime_constants:
                    return self.runtime_constants[var_name]
            # Variable not known or is an array - cannot evaluate
            return None

        if isinstance(expr, BinaryOpNode):
            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)

            if left is None or right is None:
                return None

            # Perform the operation
            # operator is a TokenType, convert to string
            from tokens import TokenType
            op_map = {
                TokenType.PLUS: '+',
                TokenType.MINUS: '-',
                TokenType.MULTIPLY: '*',
                TokenType.DIVIDE: '/',
                TokenType.BACKSLASH: '\\',
                TokenType.POWER: '^',
                TokenType.MOD: 'MOD',
                TokenType.EQUAL: '=',
                TokenType.NOT_EQUAL: '<>',
                TokenType.LESS_THAN: '<',
                TokenType.GREATER_THAN: '>',
                TokenType.LESS_EQUAL: '<=',
                TokenType.GREATER_EQUAL: '>=',
                TokenType.AND: 'AND',
                TokenType.OR: 'OR',
                TokenType.XOR: 'XOR',
                TokenType.EQV: 'EQV',
                TokenType.IMP: 'IMP',
            }
            op_str = op_map.get(expr.operator, str(expr.operator))
            op = op_str.upper() if isinstance(op_str, str) else str(op_str)
            try:
                # Arithmetic operators
                if op == '+':
                    return left + right
                elif op == '-':
                    return left - right
                elif op == '*':
                    return left * right
                elif op == '/':
                    return left / right
                elif op == '\\':
                    return int(left) // int(right)
                elif op == 'MOD':
                    return int(left) % int(right)
                elif op == '^':
                    return left ** right
                # Relational operators (return -1 for true, 0 for false in BASIC)
                elif op == '=' or 'EQUAL' in str(expr.operator):
                    return -1 if left == right else 0
                elif op == '<>' or 'NOT_EQUAL' in str(expr.operator):
                    return -1 if left != right else 0
                elif op == '<' or 'LESS_THAN' in str(expr.operator):
                    return -1 if left < right else 0
                elif op == '>' or 'GREATER_THAN' in str(expr.operator):
                    return -1 if left > right else 0
                elif op == '<=' or 'LESS_EQUAL' in str(expr.operator):
                    return -1 if left <= right else 0
                elif op == '>=' or 'GREATER_EQUAL' in str(expr.operator):
                    return -1 if left >= right else 0
                # Logical operators
                elif op == 'AND':
                    return int(left) & int(right)
                elif op == 'OR':
                    return int(left) | int(right)
                elif op == 'XOR':
                    return int(left) ^ int(right)
                elif op == 'EQV':
                    return ~(int(left) ^ int(right))
                elif op == 'IMP':
                    return ~int(left) | int(right)
            except (ZeroDivisionError, ValueError, TypeError):
                return None

        if isinstance(expr, UnaryOpNode):
            operand = self.evaluate(expr.operand)
            if operand is None:
                return None

            from tokens import TokenType
            op_map = {
                TokenType.PLUS: '+',
                TokenType.MINUS: '-',
                TokenType.NOT: 'NOT',
            }
            op_str = op_map.get(expr.operator, str(expr.operator))
            op = op_str.upper() if isinstance(op_str, str) else str(op_str)

            if op == '-':
                return -operand
            elif op == '+':
                return operand
            elif op == 'NOT':
                return ~int(operand)

        # Try to evaluate function calls (for deterministic math functions and DEF FN)
        if isinstance(expr, FunctionCallNode):
            return self._evaluate_function(expr)

        # Cannot evaluate - contains variables or unknown expressions
        return None

    def _evaluate_def_fn(self, func_name: str, args: List[Union[int, float, str]]) -> Optional[Union[int, float, str]]:
        """
        Evaluate a user-defined DEF FN function at compile time.

        Args:
            func_name: The function name (e.g., "FNDOUBLE")
            args: List of evaluated argument values

        Returns:
            The evaluated result, or None if it cannot be evaluated
        """
        # Look up the function in the symbol table
        if func_name not in self.symbols.functions:
            return None

        func_info = self.symbols.functions[func_name]

        # Check that we have the right number of arguments
        if len(args) != len(func_info.parameters):
            return None

        # Save the current runtime constants state
        saved_constants = self.runtime_constants.copy()

        try:
            # Bind the arguments to the parameters
            for param_name, arg_value in zip(func_info.parameters, args):
                self.runtime_constants[param_name] = arg_value

            # Evaluate the function body expression
            result = self.evaluate(func_info.body_expr)

            return result

        finally:
            # Restore the original runtime constants state
            self.runtime_constants = saved_constants

    def _evaluate_function(self, func_call: FunctionCallNode) -> Optional[Union[int, float, str]]:
        """
        Evaluate deterministic math functions at compile time.

        Only pure mathematical functions can be evaluated - functions whose result
        depends ONLY on their input arguments and not on any external state.

        EXCLUDED (Non-Deterministic) Functions:
        - RND: Random number generator - different value each call
        - TIMER: System timer - changes with time
        - EOF, LOC, LOF: File I/O - depend on file state at runtime
        - INPUT$, INKEY$: Input functions - depend on user/keyboard input
        - PEEK, INP: Memory/port access - depend on runtime memory/hardware state
        - FRE: Free memory - changes during program execution
        - POS, CSRLIN: Cursor position - changes with output
        - VARPTR: Variable pointer - depends on runtime memory layout

        INCLUDED (Deterministic) Functions:
        - ABS, SQR, INT, FIX, SGN: Basic math
        - SIN, COS, TAN, ATN: Trigonometry
        - EXP, LOG: Exponential/logarithm
        - CINT, CSNG, CDBL: Type conversions
        """
        import math

        func_name = func_call.name.upper()

        # Check if it's a user-defined DEF FN function
        if func_name.startswith('FN'):
            # Evaluate all arguments first
            args = []
            if func_call.arguments:
                for arg in func_call.arguments:
                    arg_val = self.evaluate(arg)
                    if arg_val is None:
                        return None  # Cannot evaluate if any argument is non-constant
                    args.append(arg_val)

            # Try to evaluate the DEF FN function
            return self._evaluate_def_fn(func_name, args)

        # Non-deterministic functions - cannot evaluate at compile time
        # Random/Time functions
        if func_name in ('RND', 'TIMER'):
            return None

        # File I/O functions (depend on runtime file state)
        if func_name in ('EOF', 'LOC', 'LOF', 'INPUT$', 'INKEY$'):
            return None

        # System functions (depend on runtime state)
        if func_name in ('PEEK', 'INP', 'FRE', 'POS', 'CSRLIN', 'VARPTR'):
            return None

        # Evaluate all arguments first
        args = []
        if func_call.arguments:
            for arg in func_call.arguments:
                arg_val = self.evaluate(arg)
                if arg_val is None:
                    return None  # Cannot evaluate if any argument is non-constant
                args.append(arg_val)

        try:
            # Single-argument functions
            if len(args) == 1:
                x = args[0]

                if func_name == 'ABS':
                    return abs(x)
                elif func_name == 'SQR':
                    return math.sqrt(x)
                elif func_name == 'SIN':
                    return math.sin(x)
                elif func_name == 'COS':
                    return math.cos(x)
                elif func_name == 'TAN':
                    return math.tan(x)
                elif func_name == 'ATN':
                    return math.atan(x)
                elif func_name == 'EXP':
                    return math.exp(x)
                elif func_name == 'LOG':
                    return math.log(x)
                elif func_name == 'INT':
                    return int(x)
                elif func_name == 'FIX':
                    return int(x) if x >= 0 else -int(-x)
                elif func_name == 'SGN':
                    return -1 if x < 0 else (1 if x > 0 else 0)
                elif func_name == 'CINT':
                    return round(x)
                elif func_name == 'CSNG':
                    return float(x)
                elif func_name == 'CDBL':
                    return float(x)

            # Two-argument functions (none in standard BASIC, but prepared for extensions)
            elif len(args) == 2:
                # Could add MAX, MIN, etc. if they exist
                pass

            # Zero-argument functions
            elif len(args) == 0:
                if func_name == 'PI':
                    return math.pi
                # RND() is explicitly excluded above

        except (ValueError, ZeroDivisionError, OverflowError):
            # Math error - cannot evaluate
            return None

        # Unknown function or cannot evaluate
        return None

    def evaluate_to_int(self, expr) -> Optional[int]:
        """Evaluate expression and convert to integer, or None if not constant"""
        val = self.evaluate(expr)
        if val is None:
            return None
        try:
            return int(val)
        except (ValueError, TypeError):
            return None


class SemanticAnalyzer:
    """
    Semantic analyzer for BASIC compiler.

    Performs static analysis including:
    - Symbol table construction
    - Type inference and checking
    - Constant expression evaluation
    - Control flow validation
    - Compiler feature detection
    - Constant folding optimization
    """

    def __init__(self):
        self.symbols = SymbolTable()
        self.flags = CompilerFlags()
        self.evaluator = ConstantEvaluator(self.symbols)
        self.errors: List[SemanticError] = []
        self.warnings: List[str] = []

        # Tracking for static nesting validation
        self.loop_stack: List[LoopInfo] = []
        self.current_line: Optional[int] = None

        # Track what features are used
        self.unsupported_commands: List[Tuple[str, int]] = []

        # Constant folding optimization tracking
        self.folded_expressions: List[Tuple[int, str, Any]] = []  # (line, expr_desc, value)

    def analyze(self, program: ProgramNode) -> bool:
        """
        Analyze a program AST.
        Returns True if analysis succeeds, False if errors found.
        """
        self.errors.clear()
        self.warnings.clear()

        try:
            # First pass: collect all line numbers and DEF statements
            self._collect_symbols(program)

            # Second pass: validate statements and build complete symbol table
            self._analyze_statements(program)

            # Third pass: validate all line number references
            self._validate_line_references(program)

            # Generate warnings for required compilation switches
            self._check_compilation_switches()

        except SemanticError as e:
            self.errors.append(e)

        return len(self.errors) == 0

    def _collect_symbols(self, program: ProgramNode):
        """First pass: collect line numbers and DEF FN definitions"""
        for line in program.lines:
            if line.line_number is not None:
                self.symbols.line_numbers.add(line.line_number)

            # Look for DEF FN statements
            for stmt in line.statements:
                if isinstance(stmt, DefFnStatementNode):
                    self._register_function(stmt, line.line_number)

    def _register_function(self, stmt: DefFnStatementNode, line_num: Optional[int]):
        """Register a DEF FN function"""
        func_name = stmt.name.upper()

        if func_name in self.symbols.functions:
            raise SemanticError(
                f"Function {func_name} already defined",
                line_num
            )

        # Determine return type from function name suffix
        return_type = self._get_type_from_name(stmt.name)

        # Get parameter names - stmt.parameters is List[VariableNode]
        params = [p.name.upper() for p in stmt.parameters] if stmt.parameters else []

        self.symbols.functions[func_name] = FunctionInfo(
            name=func_name,
            return_type=return_type,
            parameters=params,
            definition_line=line_num or 0,
            body_expr=stmt.expression
        )

    def _analyze_statements(self, program: ProgramNode):
        """Second pass: analyze all statements"""
        for line in program.lines:
            self.current_line = line.line_number

            for stmt in line.statements:
                self._analyze_statement(stmt)

    def _analyze_statement(self, stmt):
        """Analyze a single statement"""

        # Check for unsupported compiler commands
        if isinstance(stmt, (ListStatementNode, LoadStatementNode,
                            SaveStatementNode, MergeStatementNode,
                            NewStatementNode, ContStatementNode,
                            DeleteStatementNode,
                            RenumStatementNode)):
            cmd_name = stmt.__class__.__name__.replace('Statement', '').upper()
            self.unsupported_commands.append((cmd_name, self.current_line))
            raise SemanticError(
                f"{cmd_name} not supported in compiler",
                self.current_line
            )

        # IF statement - handle compile-time evaluation
        if isinstance(stmt, IfStatementNode):
            self._analyze_if(stmt)

        # DIM statement - validate and evaluate subscripts
        elif isinstance(stmt, DimStatementNode):
            self._analyze_dim(stmt)

        # Assignment - track variable types
        elif isinstance(stmt, LetStatementNode):
            self._analyze_assignment(stmt)

        # FOR statement - track loop nesting
        elif isinstance(stmt, ForStatementNode):
            self._analyze_for(stmt)

        # NEXT statement - validate loop nesting
        elif isinstance(stmt, NextStatementNode):
            self._analyze_next(stmt)

        # WHILE statement
        elif isinstance(stmt, WhileStatementNode):
            self._analyze_while(stmt)

        # WEND statement
        elif isinstance(stmt, WendStatementNode):
            self._analyze_wend(stmt)

        # ON ERROR GOTO
        elif isinstance(stmt, OnErrorStatementNode):
            self.flags.needs_error_handling = True

        # RESUME
        elif isinstance(stmt, ResumeStatementNode):
            # stmt.line_number: None = RESUME, 0 = RESUME NEXT, int = RESUME line_number
            if stmt.line_number is None or stmt.line_number == 0:  # RESUME or RESUME NEXT
                self.flags.needs_resume = True
            else:
                self.flags.needs_error_handling = True

        # TRON/TROFF
        elif isinstance(stmt, (TronStatementNode, TroffStatementNode)):
            self.flags.has_tron_troff = True

        # COMMON - not supported in compiler
        elif isinstance(stmt, CommonStatementNode):
            raise SemanticError(
                "COMMON statement not supported in compiler",
                self.current_line
            )

        # ERASE - not supported in compiler
        elif isinstance(stmt, EraseStatementNode):
            raise SemanticError(
                "ERASE statement not supported in compiler - arrays cannot be redimensioned",
                self.current_line
            )

        # INPUT - variables are no longer constants after being read
        elif isinstance(stmt, InputStatementNode):
            for var in stmt.variables:
                self.evaluator.clear_constant(var.name)

        # READ - variables are no longer constants after being read
        elif isinstance(stmt, ReadStatementNode):
            for var in stmt.variables:
                self.evaluator.clear_constant(var.name)

        # LINE INPUT - variables are no longer constants
        elif isinstance(stmt, LineInputStatementNode):
            if hasattr(stmt, 'variable'):
                self.evaluator.clear_constant(stmt.variable.name)
            elif hasattr(stmt, 'variables'):
                for var in stmt.variables:
                    self.evaluator.clear_constant(var.name)

        # Check for variable references in expressions
        if hasattr(stmt, 'expression'):
            self._analyze_expression(stmt.expression)

    def _analyze_if(self, stmt: IfStatementNode):
        """Analyze IF statement - handle compile-time evaluation when possible"""

        # Try to evaluate the condition at compile time
        condition_value = self.evaluator.evaluate(stmt.condition)

        if condition_value is not None:
            # Condition can be evaluated at compile time!
            # In BASIC, 0 is false, non-zero is true
            is_true = (condition_value != 0)

            if is_true:
                # THEN branch will be taken
                if stmt.then_statements:
                    for then_stmt in stmt.then_statements:
                        self._analyze_statement(then_stmt)
                # Don't analyze ELSE branch - it won't execute
            else:
                # ELSE branch will be taken (or nothing if no ELSE)
                if stmt.else_statements:
                    for else_stmt in stmt.else_statements:
                        self._analyze_statement(else_stmt)
                # Don't analyze THEN branch - it won't execute
        else:
            # Cannot evaluate condition at compile time
            # Need to analyze both branches and merge constant states

            # Save current constant state
            constants_before = self.evaluator.runtime_constants.copy()

            # Analyze THEN branch
            then_constants = None
            if stmt.then_statements:
                for then_stmt in stmt.then_statements:
                    self._analyze_statement(then_stmt)
                then_constants = self.evaluator.runtime_constants.copy()

            # Restore state and analyze ELSE branch
            self.evaluator.runtime_constants = constants_before.copy()
            else_constants = None
            if stmt.else_statements:
                for else_stmt in stmt.else_statements:
                    self._analyze_statement(else_stmt)
                else_constants = self.evaluator.runtime_constants.copy()

            # Merge: a variable is only constant after the IF if it has the same
            # constant value in both branches (or only one branch exists)
            if then_constants is not None and else_constants is not None:
                # Both branches exist - keep only constants that are the same in both
                merged = {}
                for var_name in then_constants:
                    if var_name in else_constants:
                        if then_constants[var_name] == else_constants[var_name]:
                            merged[var_name] = then_constants[var_name]
                # Also keep constants that weren't modified in either branch
                for var_name in constants_before:
                    if var_name not in then_constants and var_name not in else_constants:
                        merged[var_name] = constants_before[var_name]
                self.evaluator.runtime_constants = merged
            elif then_constants is not None:
                # Only THEN branch exists
                self.evaluator.runtime_constants = then_constants
            elif else_constants is not None:
                # Only ELSE branch exists
                self.evaluator.runtime_constants = else_constants
            else:
                # No branches - restore original state
                self.evaluator.runtime_constants = constants_before

        # Analyze the condition expression itself for variable references
        # Don't track folding since we already evaluated it above
        self._analyze_expression(stmt.condition, track_folding=False)

    def _analyze_dim(self, stmt: DimStatementNode):
        """Analyze DIM statement - evaluate subscripts as constants"""
        for array_decl in stmt.arrays:
            var_name = array_decl.name.upper()

            # Check if already dimensioned
            if var_name in self.symbols.variables:
                var_info = self.symbols.variables[var_name]
                if var_info.is_array:
                    raise SemanticError(
                        f"Array {var_name} already dimensioned",
                        self.current_line
                    )

            # Evaluate all subscripts as constant expressions (or runtime-evaluable constants)
            dimensions = []
            for subscript in array_decl.dimensions:
                const_val = self.evaluator.evaluate_to_int(subscript)

                if const_val is None:
                    # Try to provide a helpful error message
                    if isinstance(subscript, VariableNode) and subscript.subscripts is None:
                        var_ref = subscript.name.upper()
                        if var_ref in self.evaluator.runtime_constants:
                            # Should have been evaluated - this is unexpected
                            raise SemanticError(
                                f"Internal error: variable {var_ref} is constant but couldn't evaluate",
                                self.current_line
                            )
                        else:
                            raise SemanticError(
                                f"Array subscript in {var_name} uses variable {var_ref} which has no known constant value at this point",
                                self.current_line
                            )
                    else:
                        raise SemanticError(
                            f"Array subscript in {var_name} must be a constant expression or variable with known constant value",
                            self.current_line
                        )

                if const_val < 0:
                    raise SemanticError(
                        f"Array subscript cannot be negative in {var_name} (evaluated to {const_val})",
                        self.current_line
                    )

                dimensions.append(const_val)

            # Register the array
            var_type = self._get_type_from_name(array_decl.name)
            self.symbols.variables[var_name] = VariableInfo(
                name=var_name,
                var_type=var_type,
                is_array=True,
                dimensions=dimensions,
                first_use_line=self.current_line
            )

    def _analyze_assignment(self, stmt: LetStatementNode):
        """Analyze assignment - track variable usage and constant values"""
        var_name = stmt.variable.name.upper()

        # Register variable if not seen before
        if var_name not in self.symbols.variables:
            var_type = self._get_type_from_name(stmt.variable.name)
            # VariableNode with subscripts is an array
            is_array = stmt.variable.subscripts is not None

            self.symbols.variables[var_name] = VariableInfo(
                name=var_name,
                var_type=var_type,
                is_array=is_array,
                first_use_line=self.current_line
            )

        # Check if array used without DIM
        if stmt.variable.subscripts is not None:
            var_info = self.symbols.variables[var_name]
            if not var_info.is_array or var_info.dimensions is None:
                # Will use default dimension of 10
                self.warnings.append(
                    f"Line {self.current_line}: Array {var_name} used without explicit DIM (will default to 10)"
                )

        # Note: Expression analysis is handled by the generic check in _analyze_statement

        # Track runtime constants: if this is a simple variable (not array) assignment
        # and the expression evaluates to a constant, track it
        if stmt.variable.subscripts is None:
            const_val = self.evaluator.evaluate(stmt.expression)
            if const_val is not None:
                # Variable now has a known constant value
                self.evaluator.set_constant(var_name, const_val)
            else:
                # Variable assigned a non-constant expression, clear it if it was constant
                self.evaluator.clear_constant(var_name)

    def _analyze_for(self, stmt: ForStatementNode):
        """Analyze FOR statement - track for loop nesting"""
        # stmt.variable is a VariableNode
        var_name = stmt.variable.name.upper()

        # Register loop variable
        if var_name not in self.symbols.variables:
            var_type = self._get_type_from_name(stmt.variable.name)
            self.symbols.variables[var_name] = VariableInfo(
                name=var_name,
                var_type=var_type,
                is_array=False,
                first_use_line=self.current_line
            )

        # Push onto loop stack
        self.loop_stack.append(LoopInfo(
            loop_type="FOR",
            variable=var_name,
            start_line=self.current_line or 0
        ))

        # Analyze expressions - note: start_expr, end_expr, step_expr
        self._analyze_expression(stmt.start_expr)
        self._analyze_expression(stmt.end_expr)
        if stmt.step_expr:
            self._analyze_expression(stmt.step_expr)

        # FOR loop variable is modified, so it's no longer a constant
        self.evaluator.clear_constant(var_name)

    def _analyze_next(self, stmt: NextStatementNode):
        """Analyze NEXT statement - validate loop nesting"""
        if not self.loop_stack:
            raise SemanticError(
                "NEXT without FOR",
                self.current_line
            )

        # Check for proper nesting
        loop_info = self.loop_stack[-1]

        if loop_info.loop_type != "FOR":
            raise SemanticError(
                f"NEXT found but current loop is {loop_info.loop_type} (started at line {loop_info.start_line})",
                self.current_line
            )

        # If NEXT has a variable, it must match the FOR variable
        # stmt.variables is List[VariableNode]
        if stmt.variables:
            for var_node in stmt.variables:
                var_name = var_node.name.upper()
                if var_name != loop_info.variable:
                    raise SemanticError(
                        f"NEXT {var_name} does not match FOR {loop_info.variable} (started at line {loop_info.start_line})",
                        self.current_line
                    )
                # Pop the loop
                self.loop_stack.pop()
        else:
            # NEXT without variable - matches innermost FOR
            self.loop_stack.pop()

    def _analyze_while(self, stmt: WhileStatementNode):
        """Analyze WHILE statement"""
        self.loop_stack.append(LoopInfo(
            loop_type="WHILE",
            variable=None,
            start_line=self.current_line or 0
        ))
        self._analyze_expression(stmt.condition)

    def _analyze_wend(self, stmt: WendStatementNode):
        """Analyze WEND statement - validate loop nesting"""
        if not self.loop_stack:
            raise SemanticError(
                "WEND without WHILE",
                self.current_line
            )

        loop_info = self.loop_stack[-1]
        if loop_info.loop_type != "WHILE":
            raise SemanticError(
                f"WEND found but current loop is {loop_info.loop_type} (started at line {loop_info.start_line})",
                self.current_line
            )

        self.loop_stack.pop()

    def _analyze_expression(self, expr, context: str = "expression", track_folding: bool = True):
        """
        Analyze an expression - track variable usage and perform constant folding.

        Args:
            expr: The expression node to analyze
            context: Description of where this expression appears (for reporting)
            track_folding: Whether to track this expression in folding optimizations
        """
        if expr is None:
            return

        # Try to fold this expression to a constant
        # Only track top-level expressions, not subexpressions
        folded_value = self.evaluator.evaluate(expr)
        if (folded_value is not None and
            not isinstance(expr, (NumberNode, StringNode)) and
            track_folding):
            # This is a constant expression that can be folded
            # (but skip if it's already a literal)
            expr_desc = self._describe_expression(expr)
            self.folded_expressions.append((self.current_line, expr_desc, folded_value))

        if isinstance(expr, VariableNode):
            var_name = expr.name.upper()
            if var_name not in self.symbols.variables:
                var_type = self._get_type_from_name(expr.name)
                # Check if this is an array (has subscripts)
                is_array = expr.subscripts is not None
                self.symbols.variables[var_name] = VariableInfo(
                    name=var_name,
                    var_type=var_type,
                    is_array=is_array,
                    first_use_line=self.current_line
                )

            # Analyze subscripts if present
            if expr.subscripts:
                for subscript in expr.subscripts:
                    self._analyze_expression(subscript, "array subscript", track_folding=False)

        elif isinstance(expr, BinaryOpNode):
            self._analyze_expression(expr.left, "binary operation", track_folding=False)
            self._analyze_expression(expr.right, "binary operation", track_folding=False)

        elif isinstance(expr, UnaryOpNode):
            self._analyze_expression(expr.operand, "unary operation", track_folding=False)

        elif isinstance(expr, FunctionCallNode):
            # Check if it's a DEF FN function
            func_name = expr.name.upper()
            if func_name.startswith('FN'):
                if func_name not in self.symbols.functions:
                    raise SemanticError(
                        f"Undefined function {func_name}",
                        self.current_line
                    )

            # Analyze arguments
            if expr.arguments:
                for arg in expr.arguments:
                    self._analyze_expression(arg, f"function argument", track_folding=False)

    def _describe_expression(self, expr) -> str:
        """Generate a human-readable description of an expression"""
        if isinstance(expr, NumberNode):
            return str(expr.value)
        elif isinstance(expr, StringNode):
            return f'"{expr.value}"'
        elif isinstance(expr, VariableNode):
            if expr.subscripts:
                return f"{expr.name}(...)"
            return expr.name
        elif isinstance(expr, BinaryOpNode):
            from tokens import TokenType
            op_map = {
                TokenType.PLUS: '+', TokenType.MINUS: '-',
                TokenType.MULTIPLY: '*', TokenType.DIVIDE: '/',
                TokenType.BACKSLASH: '\\', TokenType.POWER: '^',
                TokenType.MOD: 'MOD',
                TokenType.EQUAL: '=', TokenType.NOT_EQUAL: '<>',
                TokenType.LESS_THAN: '<', TokenType.GREATER_THAN: '>',
                TokenType.LESS_EQUAL: '<=', TokenType.GREATER_EQUAL: '>=',
                TokenType.AND: 'AND', TokenType.OR: 'OR',
                TokenType.XOR: 'XOR', TokenType.EQV: 'EQV',
                TokenType.IMP: 'IMP',
            }
            op = op_map.get(expr.operator, str(expr.operator))
            return f"({self._describe_expression(expr.left)} {op} {self._describe_expression(expr.right)})"
        elif isinstance(expr, UnaryOpNode):
            from tokens import TokenType
            if expr.operator == TokenType.NOT:
                return f"NOT {self._describe_expression(expr.operand)}"
            elif expr.operator == TokenType.MINUS:
                return f"-{self._describe_expression(expr.operand)}"
            else:
                return f"+{self._describe_expression(expr.operand)}"
        elif isinstance(expr, FunctionCallNode):
            args = ", ".join(self._describe_expression(arg) for arg in (expr.arguments or []))
            return f"{expr.name}({args})"
        else:
            return "expression"

    def _validate_line_references(self, program: ProgramNode):
        """Validate all GOTO/GOSUB/ON...GOTO references"""
        for line in program.lines:
            self.current_line = line.line_number
            for stmt in line.statements:
                self._check_line_references(stmt)

    def _check_line_references(self, stmt):
        """Check line number references in a statement"""
        if isinstance(stmt, (GotoStatementNode, GosubStatementNode)):
            # These use .line_number attribute
            if stmt.line_number not in self.symbols.line_numbers:
                raise SemanticError(
                    f"Undefined line {stmt.line_number}",
                    self.current_line
                )

        elif isinstance(stmt, OnGotoStatementNode):
            # OnGotoStatementNode uses .line_numbers (plural)
            for target in stmt.line_numbers:
                if target not in self.symbols.line_numbers:
                    raise SemanticError(
                        f"Undefined line {target} in ON...GOTO",
                        self.current_line
                    )

        elif isinstance(stmt, IfStatementNode):
            # IfStatementNode uses .then_line_number
            if stmt.then_line_number is not None:
                if stmt.then_line_number not in self.symbols.line_numbers:
                    raise SemanticError(
                        f"Undefined line {stmt.then_line_number}",
                        self.current_line
                    )

    def _check_compilation_switches(self):
        """Generate warnings for required compilation switches"""
        switches = self.flags.get_required_switches()
        if switches:
            self.warnings.append(
                f"Required compilation switches: {' '.join(switches)}"
            )

    def _get_type_from_name(self, name: str) -> VarType:
        """Determine variable type from name suffix"""
        if name.endswith('%'):
            return VarType.INTEGER
        elif name.endswith('!'):
            return VarType.SINGLE
        elif name.endswith('#'):
            return VarType.DOUBLE
        elif name.endswith('$'):
            return VarType.STRING
        else:
            # Default is SINGLE (can be overridden by DEF statements)
            return VarType.SINGLE

    def get_report(self) -> str:
        """Generate a semantic analysis report"""
        lines = []
        lines.append("=" * 70)
        lines.append("SEMANTIC ANALYSIS REPORT")
        lines.append("=" * 70)

        # Symbol table summary
        lines.append(f"\nSymbol Table Summary:")
        lines.append(f"  Variables: {len(self.symbols.variables)}")
        lines.append(f"  Functions: {len(self.symbols.functions)}")
        lines.append(f"  Line Numbers: {len(self.symbols.line_numbers)}")

        # Variables
        if self.symbols.variables:
            lines.append(f"\nVariables:")
            for var_name, var_info in sorted(self.symbols.variables.items()):
                if var_info.is_array:
                    dims = f"({','.join(map(str, var_info.dimensions))})" if var_info.dimensions else "(10)"
                    lines.append(f"  {var_name}{dims} : {var_info.var_type.name} (line {var_info.first_use_line})")
                else:
                    lines.append(f"  {var_name} : {var_info.var_type.name} (line {var_info.first_use_line})")

        # Functions
        if self.symbols.functions:
            lines.append(f"\nFunctions:")
            for func_name, func_info in sorted(self.symbols.functions.items()):
                params = ', '.join(func_info.parameters) if func_info.parameters else ''
                lines.append(f"  {func_name}({params}) : {func_info.return_type.name} (line {func_info.definition_line})")

        # Constant Folding Optimizations
        if self.folded_expressions:
            lines.append(f"\nConstant Folding Optimizations:")
            for line_num, expr_desc, value in self.folded_expressions:
                # Format the value nicely
                if isinstance(value, float):
                    value_str = f"{value:.6g}"  # Compact float formatting
                else:
                    value_str = str(value)
                lines.append(f"  Line {line_num}: {expr_desc} → {value_str}")

        # Compilation flags
        switches = self.flags.get_required_switches()
        if switches:
            lines.append(f"\nRequired Compilation Switches:")
            for switch in switches:
                lines.append(f"  {switch}")

        # Warnings
        if self.warnings:
            lines.append(f"\nWarnings:")
            for warning in self.warnings:
                lines.append(f"  {warning}")

        # Errors
        if self.errors:
            lines.append(f"\nErrors:")
            for error in self.errors:
                lines.append(f"  {error}")

        lines.append("=" * 70)
        return '\n'.join(lines)


if __name__ == '__main__':
    # Simple test
    import sys

    from lexer import tokenize
    from parser import Parser

    test_program = """
10 REM Test program - demonstrates runtime constant evaluation
20 REM Constants defined early
30 N% = 10
40 M% = N% * 2
50 REM Arrays using constant expressions and variables
60 DIM A(N%), B(5, M%), C(2+3)
70 TOTAL% = N% + M%
80 DIM D(TOTAL%)
90 REM DEF FN with constant evaluation
100 DEF FN DOUBLE(X) = X * 2
110 REM Loop (I% becomes non-constant)
120 FOR I% = 1 TO 10
130   A(I%) = FN DOUBLE(I%)
140 NEXT I%
150 REM Error handling
160 ON ERROR GOTO 1000
170 PRINT A(5)
180 END
1000 RESUME NEXT
"""

    print("Parsing test program...")
    tokens = tokenize(test_program)
    parser = Parser(tokens)
    program = parser.parse()

    print("\nPerforming semantic analysis...")
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    print(analyzer.get_report())

    if success:
        print("\n✓ Semantic analysis passed!")
    else:
        print("\n✗ Semantic analysis failed!")
        sys.exit(1)
