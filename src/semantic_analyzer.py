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

    def evaluate(self, expr) -> Optional[Union[int, float, str]]:
        """
        Attempt to evaluate an expression as a compile-time constant.
        Returns None if expression cannot be evaluated (contains variables, etc.)
        """
        if isinstance(expr, NumberNode):
            return expr.value

        if isinstance(expr, StringNode):
            return expr.value

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
                TokenType.AND: 'AND',
                TokenType.OR: 'OR',
                TokenType.XOR: 'XOR',
                TokenType.EQV: 'EQV',
                TokenType.IMP: 'IMP',
            }
            op_str = op_map.get(expr.operator, str(expr.operator))
            op = op_str.upper() if isinstance(op_str, str) else str(op_str)
            try:
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

        # Cannot evaluate - contains variables or function calls
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

        # DIM statement - validate and evaluate subscripts
        if isinstance(stmt, DimStatementNode):
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

        # Check for variable references in expressions
        if hasattr(stmt, 'expression'):
            self._analyze_expression(stmt.expression)

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

            # Evaluate all subscripts as constant expressions
            dimensions = []
            for subscript in array_decl.dimensions:
                const_val = self.evaluator.evaluate_to_int(subscript)

                if const_val is None:
                    # In compiler, subscripts must be integer constants
                    # But we're extending this to allow constant expressions!
                    raise SemanticError(
                        f"Array subscript must be a constant expression in {var_name}",
                        self.current_line
                    )

                if const_val < 0:
                    raise SemanticError(
                        f"Array subscript cannot be negative in {var_name}",
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
        """Analyze assignment - track variable usage"""
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

        # Analyze the expression
        self._analyze_expression(stmt.expression)

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

    def _analyze_expression(self, expr):
        """Analyze an expression - track variable usage"""
        if expr is None:
            return

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
                    self._analyze_expression(subscript)

        elif isinstance(expr, BinaryOpNode):
            self._analyze_expression(expr.left)
            self._analyze_expression(expr.right)

        elif isinstance(expr, UnaryOpNode):
            self._analyze_expression(expr.operand)

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
                    self._analyze_expression(arg)

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
10 REM Test program
20 DIM A(10), B(5, 5)
30 DIM C(2+3)
40 FOR I% = 1 TO 10
50   A(I%) = I% * 2
60 NEXT I%
70 DEF FN DOUBLE(X) = X * 2
80 PRINT FN DOUBLE(5)
90 ON ERROR GOTO 1000
100 END
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
