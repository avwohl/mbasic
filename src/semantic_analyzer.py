#!/usr/bin/env python3
"""
Semantic Analyzer for MBASIC Compiler

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
from src.ast_nodes import *
from src.tokens import TokenType


class VarType(Enum):
    """Variable types in BASIC"""
    INTEGER = 1
    SINGLE = 2
    DOUBLE = 3
    STRING = 4


class IntegerSize(Enum):
    """Size of integer variable (for optimization)"""
    INT8_SIGNED = 1      # 8-bit signed: -128 to 127
    INT8_UNSIGNED = 2    # 8-bit unsigned: 0 to 255
    INT16_SIGNED = 3     # 16-bit signed: -32768 to 32767
    INT16_UNSIGNED = 4   # 16-bit unsigned: 0 to 65535
    INT32 = 5            # 32-bit: full range (conservative fallback)


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
    dimensions: Optional[List[int]] = None  # For arrays, stores dimension sizes (original multi-dimensional)
    flattened_size: Optional[int] = None  # Total size after flattening (product of all dimensions)
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


@dataclass
class CommonSubexpression:
    """Information about a common subexpression"""
    expression_hash: str  # Canonical representation for equivalence checking
    expression_desc: str  # Human-readable description
    first_line: int  # Line where first encountered
    occurrences: List[int] = field(default_factory=list)  # Lines where it appears
    variables_used: Set[str] = field(default_factory=set)  # Variables referenced in expression
    temp_var_name: Optional[str] = None  # Suggested temporary variable name


@dataclass
class SubroutineInfo:
    """Information about a subroutine"""
    start_line: int  # Line number where subroutine starts
    end_line: Optional[int] = None  # Line number of RETURN statement
    variables_modified: Set[str] = field(default_factory=set)  # Variables written in subroutine
    variables_read: Set[str] = field(default_factory=set)  # Variables read in subroutine
    calls_other_subs: Set[int] = field(default_factory=set)  # Other subroutines called (GOSUB targets)
    analyzed: bool = False  # Whether we've analyzed this subroutine


class LoopType(Enum):
    """Types of loops"""
    FOR = "FOR"
    WHILE = "WHILE"
    IF_GOTO = "IF-GOTO"  # Loop using IF...THEN GOTO


@dataclass
class LoopInvariant:
    """Information about a loop-invariant expression"""
    expression_hash: str  # Hash of the invariant expression
    expression_desc: str  # Human-readable description
    first_line: int  # First occurrence in loop
    occurrences: List[int] = field(default_factory=list)  # All occurrences in loop
    can_hoist: bool = True  # Whether it's safe to hoist out of loop
    reason_no_hoist: Optional[str] = None  # Why it can't be hoisted


@dataclass
class LoopAnalysis:
    """Comprehensive loop analysis information"""
    loop_type: LoopType
    start_line: int  # Line where loop begins
    end_line: Optional[int] = None  # Line where loop ends

    # Loop control
    control_variable: Optional[str] = None  # FOR loop variable or WHILE condition variable
    start_value: Optional[Any] = None  # FOR loop start (if constant)
    end_value: Optional[Any] = None  # FOR loop end (if constant)
    step_value: Optional[Any] = None  # FOR loop step (if constant)
    iteration_count: Optional[int] = None  # Number of iterations (if determinable)

    # Variables modified in loop body
    variables_modified: Set[str] = field(default_factory=set)
    variables_read: Set[str] = field(default_factory=set)

    # Loop-invariant expressions (CSEs that can be hoisted)
    invariants: Dict[str, LoopInvariant] = field(default_factory=dict)  # hash -> invariant

    # Nested loops
    contains_loops: List[int] = field(default_factory=list)  # Start lines of nested loops
    nested_in: Optional[int] = None  # Start line of parent loop (if nested)

    # Optimization potential
    can_unroll: bool = False  # Whether loop can be unrolled
    unroll_factor: Optional[int] = None  # Suggested unroll factor
    has_side_effects: bool = False  # Contains I/O, GOSUB, etc.


@dataclass
class ReachabilityInfo:
    """Information about code reachability for dead code detection"""
    reachable_lines: Set[int] = field(default_factory=set)  # Lines that can be reached
    unreachable_lines: Set[int] = field(default_factory=set)  # Dead code
    goto_targets: Set[int] = field(default_factory=set)  # All GOTO/GOSUB targets
    # Track control flow terminating statements
    terminating_lines: Set[int] = field(default_factory=set)  # Lines with END, STOP, etc.


@dataclass
class StrengthReduction:
    """Information about a strength reduction optimization"""
    line: int  # Line number where reduction was applied
    original_expr: str  # Original expression (e.g., "X * 2")
    reduced_expr: str  # Reduced expression (e.g., "X + X")
    reduction_type: str  # Type of reduction (e.g., "multiply by 2 -> add", "X^2 -> X*X")
    savings: str  # Description of savings (e.g., "Replace MUL with ADD")


@dataclass
class ExpressionReassociation:
    """Information about an expression reassociation optimization"""
    line: int  # Line number where reassociation was applied
    original_expr: str  # Original expression (e.g., "(A + 1) + 2")
    reassociated_expr: str  # Reassociated expression (e.g., "A + 3")
    operation: str  # Type of operation (e.g., "addition chain", "multiplication chain")
    savings: str  # Description of savings (e.g., "Fold 2 constants into 1")


@dataclass
class CopyPropagation:
    """Information about a copy propagation opportunity"""
    line: int  # Line number where copy was detected
    copy_var: str  # Variable being assigned (the copy)
    source_var: str  # Variable being copied from (the source)
    propagation_count: int = 0  # Number of times this copy could be propagated
    propagated_lines: List[int] = field(default_factory=list)  # Lines where propagation occurred


@dataclass
class ForwardSubstitution:
    """Information about a forward substitution opportunity"""
    line: int  # Line number where variable is assigned
    variable: str  # Variable being assigned
    expression: str  # Expression being assigned (for display)
    expression_node: Any  # The actual expression AST node
    use_line: Optional[int] = None  # Line where variable is used (if single-use)
    use_count: int = 0  # Number of times variable is used
    can_substitute: bool = False  # Whether substitution is safe
    reason: str = ""  # Why substitution can/cannot be done


@dataclass
class BranchOptimization:
    """Information about a branch optimization opportunity"""
    line: int  # Line number of the IF statement
    condition: str  # The condition expression (for display)
    is_constant: bool  # Whether the condition is a constant
    constant_value: Optional[Any] = None  # The constant value (if constant)
    always_true: bool = False  # Branch always taken
    always_false: bool = False  # Branch never taken
    then_target: Optional[int] = None  # Line number of THEN branch
    else_target: Optional[int] = None  # Line number of ELSE branch
    unreachable_branch: Optional[str] = None  # "THEN" or "ELSE" if unreachable


@dataclass
class UninitializedVariableWarning:
    """Warning about a potentially uninitialized variable"""
    line: int  # Line where uninitialized use occurs
    variable: str  # Variable name
    context: str  # Description of where it's used (e.g., "in expression", "in PRINT")


@dataclass
class ValueRange:
    """Represents a range of possible values for a variable"""
    min_value: Optional[Union[int, float]] = None  # Minimum possible value (None = unbounded)
    max_value: Optional[Union[int, float]] = None  # Maximum possible value (None = unbounded)
    is_constant: bool = False  # True if min_value == max_value (known constant)

    def __repr__(self):
        if self.is_constant and self.min_value is not None:
            return f"[{self.min_value}]"
        elif self.min_value is not None and self.max_value is not None:
            return f"[{self.min_value}, {self.max_value}]"
        elif self.min_value is not None:
            return f"[{self.min_value}, +∞)"
        elif self.max_value is not None:
            return f"(-∞, {self.max_value}]"
        else:
            return "(-∞, +∞)"

    def intersect(self, other: 'ValueRange') -> 'ValueRange':
        """Compute intersection of two ranges"""
        new_min = None
        new_max = None

        # Compute min
        if self.min_value is not None and other.min_value is not None:
            new_min = max(self.min_value, other.min_value)
        elif self.min_value is not None:
            new_min = self.min_value
        elif other.min_value is not None:
            new_min = other.min_value

        # Compute max
        if self.max_value is not None and other.max_value is not None:
            new_max = min(self.max_value, other.max_value)
        elif self.max_value is not None:
            new_max = self.max_value
        elif other.max_value is not None:
            new_max = other.max_value

        is_const = (new_min is not None and new_max is not None and new_min == new_max)
        return ValueRange(new_min, new_max, is_const)

    def union(self, other: 'ValueRange') -> 'ValueRange':
        """Compute union of two ranges (conservative merge)"""
        new_min = None
        new_max = None

        # Compute min (take the minimum of both)
        if self.min_value is not None and other.min_value is not None:
            new_min = min(self.min_value, other.min_value)
        # If either is unbounded below, result is unbounded below

        # Compute max (take the maximum of both)
        if self.max_value is not None and other.max_value is not None:
            new_max = max(self.max_value, other.max_value)
        # If either is unbounded above, result is unbounded above

        is_const = (new_min is not None and new_max is not None and new_min == new_max)
        return ValueRange(new_min, new_max, is_const)


@dataclass
class RangeAnalysisInfo:
    """Information from range analysis"""
    line: int  # Line where range was determined
    variable: str  # Variable name
    range: ValueRange  # The determined range
    context: str  # Description (e.g., "after IF X > 0", "in THEN branch")
    enabled_optimization: Optional[str] = None  # What optimization this enabled


@dataclass
class LiveVariableInfo:
    """Information from live variable analysis"""
    line: int  # Line number
    live_vars: Set[str] = field(default_factory=set)  # Variables live at this point
    dead_writes: Set[str] = field(default_factory=set)  # Variables written but never read


@dataclass
class DeadWrite:
    """Information about a write to a variable that is never read"""
    line: int  # Line where variable is written
    variable: str  # Variable name
    reason: str  # Why it's considered dead (e.g., "never read", "overwritten before read")


@dataclass
class StringConstantPool:
    """Information about a pooled string constant"""
    value: str  # The string value
    pool_id: str  # Suggested pool identifier (e.g., "STR1$")
    occurrences: List[int] = field(default_factory=list)  # Lines where this string appears
    size: int = 0  # Length of the string

    def __post_init__(self):
        self.size = len(self.value)


@dataclass
class BuiltinFunctionPurity:
    """Information about built-in function purity for optimization"""
    function_name: str
    is_pure: bool  # True if function has no side effects and same inputs -> same outputs
    reason: str  # Why it's pure or impure


@dataclass
class ArrayBoundsViolation:
    """Information about a detected array bounds violation"""
    line: int
    array_name: str
    dimension_index: int  # Which dimension (0-based)
    subscript_value: Union[int, float]
    lower_bound: int  # Valid lower bound
    upper_bound: int  # Valid upper bound
    access_type: str  # "read" or "write"


@dataclass
class AliasInfo:
    """Information about potential aliasing between variables/arrays"""
    var1: str
    var2: str
    alias_type: str  # "definite", "possible", "none"
    reason: str  # Why they might alias
    impact: str  # Impact on optimizations


@dataclass
class AvailableExpression:
    """Information about available expressions (computed on all paths)"""
    expression_hash: str  # Canonical representation
    expression_desc: str  # Human-readable description
    first_computed_line: int  # Where first computed
    available_at_lines: List[int] = field(default_factory=list)  # Lines where available from all paths
    variables_used: Set[str] = field(default_factory=set)  # Variables in expression
    killed_at_lines: List[int] = field(default_factory=list)  # Lines where expression becomes unavailable
    redundant_computations: int = 0  # How many redundant computations could be eliminated


@dataclass
class StringConcatInLoop:
    """Information about string concatenation inside loops"""
    loop_start_line: int  # Line where loop starts
    loop_type: str  # "FOR", "WHILE", "IF-GOTO"
    string_var: str  # String variable being concatenated to
    concat_lines: List[int] = field(default_factory=list)  # Lines where concatenation occurs
    iteration_count: Optional[int] = None  # Known iteration count (for FOR loops)
    estimated_allocations: int = 0  # Estimated number of temporary string allocations
    impact: str = ""  # Performance impact description


@dataclass
class IntegerInferenceAnalysis:
    """Information about inferred variable types (INTEGER vs DOUBLE)"""
    variable: str  # Variable name
    inferred_type: str  # "INTEGER", "DOUBLE", "SINGLE", "STRING" (or explicit type suffix)
    confidence: str  # "HIGH", "MEDIUM", "LOW"
    reasons: List[str] = field(default_factory=list)  # Why this type was inferred
    assignment_lines: List[int] = field(default_factory=list)  # Lines where variable is assigned
    usage_lines: List[int] = field(default_factory=list)  # Lines where variable is used
    performance_impact: str = ""  # Estimated performance impact of this inference


@dataclass
class TypeBinding:
    """Represents a type binding for a variable at a specific program point"""
    variable: str  # Variable name (without suffix)
    line: int  # Line number where this binding occurs
    type_name: str  # "INTEGER", "SINGLE", "DOUBLE", "STRING"
    reason: str  # Why this type was assigned
    depends_on_previous: bool = False  # Does this assignment depend on previous value?
    can_rebind: bool = True  # Can we safely re-bind to a different type?
    promotion_from: Optional[str] = None  # Phase 2: promoted from this type (e.g., "INTEGER")
    promotion_reason: str = ""  # Phase 2: why promotion occurred


@dataclass
class TypePromotion:
    """Represents a type promotion (widening conversion) at a program point"""
    variable: str  # Variable being promoted
    line: int  # Line where promotion occurs
    from_type: str  # Source type (e.g., "INTEGER")
    to_type: str  # Target type (e.g., "DOUBLE")
    reason: str  # Why promotion is needed
    expression: str = ""  # The expression causing promotion
    is_safe: bool = True  # Whether promotion preserves value (INT→DOUBLE is safe)


@dataclass
class IntegerRangeInfo:
    """Range information for integer size inference"""
    variable: str  # Variable name
    integer_size: IntegerSize  # Inferred size (8/16/32-bit)
    min_value: Optional[int] = None  # Minimum possible value
    max_value: Optional[int] = None  # Maximum possible value
    is_constant: bool = False  # Always the same value?
    constant_value: Optional[int] = None  # If constant, what value?
    reason: str = ""  # Why this size was chosen
    line: int = 0  # Where determined


@dataclass
class InductionVariable:
    """Information about an induction variable in a loop"""
    variable: str  # Variable name (e.g., "I")
    loop_start_line: int  # Line where loop starts
    is_primary: bool = False  # True if this is the loop control variable (FOR I = ...)

    # Linear relationship: variable = base + coefficient * primary_iv
    # For primary IV: coefficient = step, base = start
    # For derived IV: e.g., J = I * 2, coefficient = 2, base_var = "I"
    base_value: Optional[Any] = None  # Constant base (for primary IV, this is start value)
    coefficient: Optional[Any] = None  # Multiplier (step for primary, or derived relationship)
    base_var: Optional[str] = None  # For derived IVs: base variable name

    # Optimization opportunities
    related_expressions: List[Tuple[int, str, str]] = field(default_factory=list)  # (line, expr_desc, optimized_desc)
    strength_reduction_opportunities: int = 0  # Count of optimizable expressions


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
        # Note: TokenType is already imported from src.tokens at the top
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

        # Note: TokenType is already imported from src.tokens at the top
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

        # Common Subexpression Elimination (CSE) tracking
        self.common_subexpressions: Dict[str, CommonSubexpression] = {}  # hash -> CSE info
        self.available_expressions: Dict[str, Any] = {}  # hash -> expression node (currently available)
        self.cse_counter = 0  # For generating unique temporary variable names

        # Subroutine tracking (for GOSUB analysis)
        self.subroutines: Dict[int, SubroutineInfo] = {}  # line_number -> SubroutineInfo
        self.gosub_targets: Set[int] = set()  # All line numbers that are GOSUB targets

        # Loop analysis tracking
        self.loops: Dict[int, LoopAnalysis] = {}  # start_line -> LoopAnalysis
        self.loop_analysis_stack: List[LoopAnalysis] = []  # Stack for nested loop analysis
        self.current_loop: Optional[LoopAnalysis] = None  # Currently analyzing loop

        # Array handling
        self.array_base: int = 0  # 0 or 1, set by OPTION BASE statement

        # Reachability analysis
        self.reachability = ReachabilityInfo()

        # Strength reduction tracking
        self.strength_reductions: List[StrengthReduction] = []

        # Expression reassociation tracking
        self.expression_reassociations: List[ExpressionReassociation] = []

        # Copy propagation tracking
        self.copy_propagations: List[CopyPropagation] = []
        self.active_copies: Dict[str, str] = {}  # copy_var -> source_var (currently active copies)

        # Forward substitution tracking
        self.forward_substitutions: List[ForwardSubstitution] = []
        self.variable_assignments: Dict[str, Tuple[int, Any, str]] = {}  # var_name -> (line, expr_node, expr_desc)
        self.variable_usage_count: Dict[str, int] = {}  # var_name -> count
        self.variable_usage_lines: Dict[str, List[int]] = {}  # var_name -> [line1, line2, ...]

        # Branch optimization tracking
        self.branch_optimizations: List[BranchOptimization] = []

        # Uninitialized variable tracking
        self.uninitialized_warnings: List[UninitializedVariableWarning] = []
        self.initialized_variables: Set[str] = set()  # Variables that have been assigned

        # Induction variable tracking
        self.induction_variables: List[InductionVariable] = []  # All detected induction variables
        self.active_ivs: Dict[str, InductionVariable] = {}  # var_name -> IV (currently in a loop)

        # Range analysis tracking
        self.range_info: List[RangeAnalysisInfo] = []  # All range analysis results
        self.active_ranges: Dict[str, ValueRange] = {}  # var_name -> current known range

        # Live variable analysis tracking
        self.live_var_info: Dict[int, LiveVariableInfo] = {}  # line -> live variable info
        self.dead_writes: List[DeadWrite] = []  # All detected dead writes

        # String constant pooling tracking
        self.string_pool: Dict[str, StringConstantPool] = {}  # string_value -> pool info
        self.string_pool_counter = 0  # For generating unique pool IDs

        # Built-in function purity tracking
        self.builtin_function_calls: Dict[str, List[int]] = {}  # func_name -> [line1, line2, ...]
        self.impure_function_calls: List[Tuple[int, str, str]] = []  # (line, func_name, reason)

        # Array bounds checking tracking
        self.array_bounds_violations: List[ArrayBoundsViolation] = []

        # Alias analysis tracking
        self.alias_info: List[AliasInfo] = []
        self.array_element_accesses: Dict[str, List[Tuple[int, str]]] = {}  # array_name -> [(line, access_pattern)]

        # Available expression analysis tracking
        self.available_expr_analysis: List[AvailableExpression] = []  # All available expression analysis results
        self.expr_computations: Dict[str, List[int]] = {}  # expr_hash -> [line1, line2, ...] all computation points

        # String concatenation in loops tracking
        self.string_concat_in_loops: List[StringConcatInLoop] = []  # All detected string concatenations in loops

        # Type rebinding tracking (Phase 1: FOR loops and sequential assignments)
        self.type_bindings: List[TypeBinding] = []  # All type bindings discovered
        self.variable_type_versions: Dict[str, List[TypeBinding]] = {}  # var_name -> [binding1, binding2, ...]
        self.can_rebind_variable: Dict[str, bool] = {}  # var_name -> can safely rebind?

        # Type promotion tracking (Phase 2: INT→DOUBLE widening conversions)
        self.type_promotions: List[TypePromotion] = []  # All promotions detected
        self.variable_current_type: Dict[str, str] = {}  # var_name -> current type at each point
        self.promotion_points: Dict[str, List[int]] = {}  # var_name -> [lines where promoted]

        # Integer size inference tracking (8/16/32-bit optimization)
        self.integer_ranges: List[IntegerRangeInfo] = []  # All integer size inferences
        self.variable_integer_size: Dict[str, IntegerRangeInfo] = {}  # var_name -> size info

        # Iterative optimization tracking
        self.optimization_iterations = 0  # Number of iterations performed
        self.optimization_converged = False  # Whether fixed point was reached

    def analyze(self, program: ProgramNode, max_iterations: int = 5,
                enable_integer_size_inference: bool = True) -> bool:
        """
        Analyze a program AST with iterative optimization.

        Args:
            program: The AST to analyze
            max_iterations: Maximum optimization iterations (default 5)
            enable_integer_size_inference: Enable 8/16/32-bit integer optimization (default True)
                If False, all integers use 32-bit signed math (smaller code size)

        Returns:
            True if analysis succeeds, False if errors found

        The analysis runs in three phases:
        1. Structural analysis (once): symbols, subroutines, statements, line references
        2. Iterative optimization (until convergence): analyses that can cascade
        3. Final reporting (once): warnings and statistics

        Note on integer size inference:
        - When enabled: Analyzes 8/16/32-bit opportunities (10-20x faster on 8080!)
        - When disabled: Uses 32-bit signed for all integers (smaller generated code)
        - Trade-off: Speed vs code size. Enable for performance, disable if code size matters.
        """
        self.errors.clear()
        self.warnings.clear()
        self.optimization_iterations = 0
        self.optimization_converged = False

        try:
            # ============================================================
            # PHASE 1: STRUCTURAL ANALYSIS (Run Once)
            # ============================================================
            # These establish program structure and don't benefit from iteration

            # Collect all symbols, DEF statements, and GOSUB targets
            self._collect_symbols(program)

            # Analyze subroutines to determine what they modify
            self._analyze_subroutines(program)

            # Validate statements and build complete symbol table
            self._analyze_statements(program)

            # Validate all line number references
            self._validate_line_references(program)

            # ============================================================
            # PHASE 2: ITERATIVE OPTIMIZATION (Until Convergence)
            # ============================================================
            # These analyses can cascade - run until fixed point reached

            for iteration in range(1, max_iterations + 1):
                self.optimization_iterations = iteration

                # Count optimizations BEFORE clearing (to detect if iteration changed anything)
                count_before = self._count_optimizations() if iteration > 1 else 0

                # Clear stale optimization state from previous iteration
                if iteration > 1:
                    self._clear_iterative_state()

                # Run analyses that can benefit from cascading
                self._analyze_loop_invariants()
                self._analyze_reachability(program)
                self._analyze_forward_substitution(program)
                self._analyze_live_variables(program)
                self._analyze_available_expressions(program)
                self._analyze_variable_type_bindings(program)
                self._analyze_type_promotions(program)  # Phase 2: detect INT→DOUBLE promotions

                # Integer size inference (optional - controlled by flag)
                if enable_integer_size_inference:
                    self._analyze_integer_sizes(program)  # 8/16/32-bit optimization

                # Count optimizations after this iteration
                count_after = self._count_optimizations()

                # Check for convergence (same count as before we cleared and re-ran)
                if iteration > 1 and count_after == count_before:
                    self.optimization_converged = True
                    break

            # Warn if we hit the iteration limit
            if not self.optimization_converged:
                self.warnings.append(
                    f"Optimization iteration limit reached ({max_iterations}). "
                    f"Some optimization opportunities may have been missed."
                )

            # ============================================================
            # PHASE 3: FINAL REPORTING (Run Once)
            # ============================================================
            # These are for warnings/reports and don't affect other optimizations

            # String constant pooling
            self._analyze_string_constants(program)

            # Built-in function purity analysis
            self._analyze_function_purity(program)

            # Array bounds checking
            self._analyze_array_bounds(program)

            # Alias analysis
            self._analyze_aliases(program)

            # String concatenation in loops
            self._analyze_string_concat_in_loops(program)

            # Generate warnings for required compilation switches
            self._check_compilation_switches()

        except SemanticError as e:
            self.errors.append(e)

        return len(self.errors) == 0

    def _collect_symbols(self, program: ProgramNode):
        """First pass: collect line numbers, DEF FN definitions, GOSUB targets, and OPTION BASE"""
        for line in program.lines:
            if line.line_number is not None:
                self.symbols.line_numbers.add(line.line_number)

            # Look for DEF FN statements, GOSUB targets, and OPTION BASE
            for stmt in line.statements:
                if isinstance(stmt, DefFnStatementNode):
                    self._register_function(stmt, line.line_number)
                elif isinstance(stmt, GosubStatementNode):
                    # Record this as a GOSUB target (potential subroutine)
                    self.gosub_targets.add(stmt.line_number)
                elif isinstance(stmt, OptionBaseStatementNode):
                    # Collect OPTION BASE declarations (global, compile-time)
                    self._collect_option_base(stmt, line.line_number)

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

    def _collect_option_base(self, stmt: OptionBaseStatementNode, line_num: Optional[int]):
        """
        Collect OPTION BASE declarations (first pass).

        OPTION BASE is global and compile-time:
        - Multiple OPTION BASE statements are allowed but must all be the same value
        - The value applies to the entire program regardless of where it appears
        """
        if stmt.base not in (0, 1):
            raise SemanticError(
                f"OPTION BASE must be 0 or 1, got {stmt.base}",
                line_num
            )

        # Check for conflicts with previously seen OPTION BASE
        if hasattr(self, '_first_option_base_value'):
            if self._first_option_base_value != stmt.base:
                raise SemanticError(
                    f"Conflicting OPTION BASE: line {self._first_option_base_line} set to {self._first_option_base_value}, "
                    f"but line {line_num} set to {stmt.base}. OPTION BASE must be consistent throughout the program.",
                    line_num
                )
        else:
            # First OPTION BASE seen
            self._first_option_base_value = stmt.base
            self._first_option_base_line = line_num
            self.array_base = stmt.base

    def _analyze_subroutines(self, program: ProgramNode):
        """
        Second pass: analyze subroutines to determine what variables they modify.

        For each GOSUB target, we analyze from that line until we hit a RETURN,
        tracking which variables are modified.
        """
        # Build a map of line numbers to statements for quick lookup
        line_map = {}
        for line in program.lines:
            if line.line_number is not None:
                line_map[line.line_number] = line

        # Analyze each GOSUB target as a potential subroutine
        for target_line in self.gosub_targets:
            if target_line not in line_map:
                continue  # Will be caught as error in validation pass

            # Initialize subroutine info
            sub_info = SubroutineInfo(start_line=target_line)
            self.subroutines[target_line] = sub_info

            # Analyze statements from target until RETURN
            current_line_num = target_line
            in_subroutine = True

            while in_subroutine and current_line_num in line_map:
                line = line_map[current_line_num]

                for stmt in line.statements:
                    # Check if this is a RETURN
                    if isinstance(stmt, ReturnStatementNode):
                        sub_info.end_line = current_line_num
                        in_subroutine = False
                        break

                    # Track variable modifications
                    if isinstance(stmt, LetStatementNode):
                        var_name = stmt.variable.name.upper()
                        sub_info.variables_modified.add(var_name)

                    # Track FOR loops (modify loop variable)
                    elif isinstance(stmt, ForStatementNode):
                        var_name = stmt.variable.name.upper()
                        sub_info.variables_modified.add(var_name)

                    # Track INPUT/READ (modify variables)
                    elif isinstance(stmt, InputStatementNode):
                        for var in stmt.variables:
                            sub_info.variables_modified.add(var.name.upper())

                    elif isinstance(stmt, ReadStatementNode):
                        for var in stmt.variables:
                            sub_info.variables_modified.add(var.name.upper())

                    elif isinstance(stmt, LineInputStatementNode):
                        if hasattr(stmt, 'variable'):
                            sub_info.variables_modified.add(stmt.variable.name.upper())
                        elif hasattr(stmt, 'variables'):
                            for var in stmt.variables:
                                sub_info.variables_modified.add(var.name.upper())

                    # Track nested GOSUB calls
                    elif isinstance(stmt, GosubStatementNode):
                        sub_info.calls_other_subs.add(stmt.line_number)

                # Move to next line
                # Find the next line number in sequence
                next_line_num = None
                for line_num in sorted(line_map.keys()):
                    if line_num > current_line_num:
                        next_line_num = line_num
                        break

                if next_line_num is None:
                    # No more lines
                    break

                current_line_num = next_line_num

            sub_info.analyzed = True

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

        # DEF FN - analyze function body with parameters marked as initialized
        elif isinstance(stmt, DefFnStatementNode):
            # Save current state
            saved_initialized = self.initialized_variables.copy()
            # Mark parameters as initialized (they are function arguments)
            for param in stmt.parameters:
                self.initialized_variables.add(param.name.upper())
            # Analyze the function body
            self._analyze_expression(stmt.expression, "DEF FN body")
            # Restore state (DEF FN has local scope)
            self.initialized_variables = saved_initialized

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

        # OPTION BASE statement
        elif isinstance(stmt, OptionBaseStatementNode):
            self._analyze_option_base(stmt)

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

        # COMMON - generates comment only (used with CHAIN which is also unsupported)
        elif isinstance(stmt, CommonStatementNode):
            # Issue warning but allow compilation
            self.warnings.append(
                f"Line {self.current_line}: COMMON is only meaningful with CHAIN (not supported in compiled code)"
            )

        # ERASE - not supported in compiler (matches Microsoft BASIC Compiler)
        elif isinstance(stmt, EraseStatementNode):
            # Issue warning but allow compilation
            self.warnings.append(
                f"Line {self.current_line}: ERASE not supported in compiled code - arrays cannot be deallocated (matches Microsoft BASIC Compiler)"
            )

        # INPUT - variables are no longer constants after being read
        elif isinstance(stmt, InputStatementNode):
            for var in stmt.variables:
                # Analyze the variable to ensure it's in the symbol table
                self._analyze_expression(var, "INPUT")
                self._invalidate_expressions(var.name)
                self.evaluator.clear_constant(var.name)
                # INPUT initializes the variable
                self.initialized_variables.add(var.name.upper())

        # READ - variables are no longer constants after being read
        elif isinstance(stmt, ReadStatementNode):
            for var in stmt.variables:
                # Analyze the variable to ensure it's in the symbol table
                self._analyze_expression(var, "READ")
                self._invalidate_expressions(var.name)
                self.evaluator.clear_constant(var.name)
                # READ initializes the variable
                self.initialized_variables.add(var.name.upper())

        # LINE INPUT - variables are no longer constants
        elif isinstance(stmt, LineInputStatementNode):
            if hasattr(stmt, 'variable'):
                # Analyze the variable to ensure it's in the symbol table
                self._analyze_expression(stmt.variable, "LINE INPUT")
                self._invalidate_expressions(stmt.variable.name)
                self.evaluator.clear_constant(stmt.variable.name)
                # LINE INPUT initializes the variable
                self.initialized_variables.add(stmt.variable.name.upper())
            elif hasattr(stmt, 'variables'):
                for var in stmt.variables:
                    # Analyze the variable to ensure it's in the symbol table
                    self._analyze_expression(var, "LINE INPUT")
                    self._invalidate_expressions(var.name)
                    self.evaluator.clear_constant(var.name)
                    # LINE INPUT initializes the variable
                    self.initialized_variables.add(var.name.upper())

        # GOSUB - subroutine call (conservative: invalidate all state)
        elif isinstance(stmt, GosubStatementNode):
            self._analyze_gosub(stmt)

        # PRINT - analyze all expressions
        elif isinstance(stmt, PrintStatementNode):
            for expr in stmt.expressions:
                if expr is not None:  # Skip TAB() separators which are None
                    self._analyze_expression(expr, "print")

        # Check for variable references in expressions
        # (but skip DEF FN - already handled above with proper parameter scope)
        if hasattr(stmt, 'expression') and not isinstance(stmt, DefFnStatementNode):
            self._analyze_expression(stmt.expression)

        # For LET/assignment statements, also analyze the LHS variable's subscripts
        if isinstance(stmt, LetStatementNode) and stmt.variable.subscripts:
            # Check for IV strength reduction BEFORE analyzing (which transforms expressions)
            if self.current_loop:
                for subscript in stmt.variable.subscripts:
                    self._detect_iv_strength_reduction(stmt.variable.name.upper(), subscript)
            # Now analyze and transform the subscripts
            for subscript in stmt.variable.subscripts:
                self._analyze_expression(subscript, "array subscript", track_folding=False, track_cse=True)

    def _analyze_gosub(self, stmt: GosubStatementNode):
        """
        Analyze GOSUB statement.

        Uses subroutine analysis to determine what variables the subroutine modifies,
        then invalidates only those variables (and expressions using them).
        """
        target_line = stmt.line_number

        # Get subroutine info if available
        if target_line in self.subroutines:
            sub_info = self.subroutines[target_line]

            # Get all variables modified by this subroutine (including transitive calls)
            modified_vars = self._get_all_modified_variables(target_line)

            # Invalidate runtime constants for modified variables
            for var_name in modified_vars:
                if var_name in self.evaluator.runtime_constants:
                    del self.evaluator.runtime_constants[var_name]

            # Invalidate available expressions that use modified variables
            for var_name in modified_vars:
                self._invalidate_expressions(var_name)

        else:
            # Subroutine not analyzed (shouldn't happen, but be conservative)
            self.evaluator.runtime_constants.clear()
            self._clear_all_available_expressions()

    def _get_all_modified_variables(self, sub_line: int, visited: Optional[Set[int]] = None) -> Set[str]:
        """
        Get all variables modified by a subroutine, including transitively
        through nested GOSUB calls.
        """
        if visited is None:
            visited = set()

        # Avoid infinite recursion
        if sub_line in visited:
            return set()

        visited.add(sub_line)

        if sub_line not in self.subroutines:
            # Unknown subroutine - conservatively assume it modifies everything
            # Return all known variables
            return set(self.symbols.variables.keys())

        sub_info = self.subroutines[sub_line]
        modified = sub_info.variables_modified.copy()

        # Add variables modified by nested subroutine calls
        for nested_sub in sub_info.calls_other_subs:
            nested_modified = self._get_all_modified_variables(nested_sub, visited)
            modified.update(nested_modified)

        return modified

    def _analyze_loop_invariants(self):
        """
        Identify loop-invariant expressions that can be hoisted out of loops.

        An expression is loop-invariant if:
        1. It appears multiple times within the loop
        2. None of its variables are modified within the loop
        3. It has no side effects (I/O, function calls with side effects)
        """
        for loop_start, loop in self.loops.items():
            if loop.end_line is None:
                continue  # Loop not properly closed

            # Check each CSE to see if it occurs in this loop and is invariant
            for cse_hash, cse in self.common_subexpressions.items():
                # Check if CSE occurs within loop bounds
                all_cse_lines = [cse.first_line] + cse.occurrences
                cse_in_loop = [line for line in all_cse_lines
                              if loop.start_line <= line <= loop.end_line]

                if len(cse_in_loop) >= 2:  # CSE occurs multiple times in loop
                    # Check if invariant: no variables used by CSE are modified in loop
                    is_invariant = not (cse.variables_used & loop.variables_modified)

                    if is_invariant:
                        invariant = LoopInvariant(
                            expression_hash=cse_hash,
                            expression_desc=cse.expression_desc,
                            first_line=min(cse_in_loop),
                            occurrences=[l for l in cse_in_loop if l != min(cse_in_loop)],
                            can_hoist=True
                        )
                        loop.invariants[cse_hash] = invariant
                    else:
                        # Expression uses loop-modified variables, not invariant
                        reason = f"Uses loop variables: {', '.join(sorted(cse.variables_used & loop.variables_modified))}"
                        invariant = LoopInvariant(
                            expression_hash=cse_hash,
                            expression_desc=cse.expression_desc,
                            first_line=min(cse_in_loop),
                            occurrences=[l for l in cse_in_loop if l != min(cse_in_loop)],
                            can_hoist=False,
                            reason_no_hoist=reason
                        )
                        loop.invariants[cse_hash] = invariant

    def _detect_derived_induction_variable(self, var_name: str, expr: Any):
        """
        Detect derived induction variables in a loop.

        A derived IV has the form:
        - J = I * constant (linear relationship to primary IV)
        - J = I + constant
        - J = I (simple copy of IV)

        where I is the primary induction variable (loop control variable).
        """
        if not self.current_loop or not self.current_loop.control_variable:
            return

        primary_iv_name = self.current_loop.control_variable
        primary_iv = self.active_ivs.get(primary_iv_name)

        if not primary_iv:
            return  # No primary IV active

        # Check for patterns:
        # 1. J = I (copy of IV)
        if isinstance(expr, VariableNode) and expr.subscripts is None:
            if expr.name.upper() == primary_iv_name:
                # J = I (coefficient = 1, base = 0)
                iv = InductionVariable(
                    variable=var_name,
                    loop_start_line=self.current_loop.start_line,
                    is_primary=False,
                    base_value=0,
                    coefficient=1,
                    base_var=primary_iv_name
                )
                self.active_ivs[var_name] = iv
                self.induction_variables.append(iv)
                return

        # 2. J = I * constant or J = constant * I
        if isinstance(expr, BinaryOpNode) and expr.operator == TokenType.MULTIPLY:
            left_is_iv = (isinstance(expr.left, VariableNode) and
                         expr.left.subscripts is None and
                         expr.left.name.upper() == primary_iv_name)
            right_is_iv = (isinstance(expr.right, VariableNode) and
                          expr.right.subscripts is None and
                          expr.right.name.upper() == primary_iv_name)

            if left_is_iv:
                # J = I * constant
                const_val = self.evaluator.evaluate(expr.right)
                if const_val is not None:
                    iv = InductionVariable(
                        variable=var_name,
                        loop_start_line=self.current_loop.start_line,
                        is_primary=False,
                        base_value=0,
                        coefficient=const_val,
                        base_var=primary_iv_name
                    )
                    self.active_ivs[var_name] = iv
                    self.induction_variables.append(iv)
            elif right_is_iv:
                # J = constant * I
                const_val = self.evaluator.evaluate(expr.left)
                if const_val is not None:
                    iv = InductionVariable(
                        variable=var_name,
                        loop_start_line=self.current_loop.start_line,
                        is_primary=False,
                        base_value=0,
                        coefficient=const_val,
                        base_var=primary_iv_name
                    )
                    self.active_ivs[var_name] = iv
                    self.induction_variables.append(iv)
            return

        # 3. J = I + constant or J = constant + I
        if isinstance(expr, BinaryOpNode) and expr.operator == TokenType.PLUS:
            left_is_iv = (isinstance(expr.left, VariableNode) and
                         expr.left.subscripts is None and
                         expr.left.name.upper() == primary_iv_name)
            right_is_iv = (isinstance(expr.right, VariableNode) and
                          expr.right.subscripts is None and
                          expr.right.name.upper() == primary_iv_name)

            if left_is_iv:
                # J = I + constant
                const_val = self.evaluator.evaluate(expr.right)
                if const_val is not None:
                    iv = InductionVariable(
                        variable=var_name,
                        loop_start_line=self.current_loop.start_line,
                        is_primary=False,
                        base_value=const_val,
                        coefficient=1,
                        base_var=primary_iv_name
                    )
                    self.active_ivs[var_name] = iv
                    self.induction_variables.append(iv)
            elif right_is_iv:
                # J = constant + I
                const_val = self.evaluator.evaluate(expr.left)
                if const_val is not None:
                    iv = InductionVariable(
                        variable=var_name,
                        loop_start_line=self.current_loop.start_line,
                        is_primary=False,
                        base_value=const_val,
                        coefficient=1,
                        base_var=primary_iv_name
                    )
                    self.active_ivs[var_name] = iv
                    self.induction_variables.append(iv)
            return

    def _clear_loop_ivs(self, loop_start_line: int):
        """Clear induction variables when exiting a loop"""
        to_remove = []
        for var_name, iv in self.active_ivs.items():
            if iv.loop_start_line == loop_start_line:
                to_remove.append(var_name)
        for var_name in to_remove:
            del self.active_ivs[var_name]

    def _detect_iv_strength_reduction(self, array_name: str, subscript_expr: Any):
        """
        Detect strength reduction opportunities for array subscripts using induction variables.

        Pattern: A(I * constant) can be optimized to:
        - Initialize: ptr = start * constant
        - Each iteration: ptr = ptr + step * constant (instead of I * constant)

        This replaces multiplication with addition in the loop body.
        """
        if not self.current_loop:
            return

        # First, recursively check sub-expressions (e.g., for "I*10 + J", check "I*10" and "J")
        if isinstance(subscript_expr, BinaryOpNode):
            self._detect_iv_strength_reduction(array_name, subscript_expr.left)
            self._detect_iv_strength_reduction(array_name, subscript_expr.right)

        # Check for pattern: I * constant or constant * I for ANY active IV, not just current loop
        if isinstance(subscript_expr, BinaryOpNode) and subscript_expr.operator == TokenType.MULTIPLY:
            # Check all active IVs (including outer loop IVs in nested loops)
            for iv_name, iv_info in self.active_ivs.items():
                if not iv_info.is_primary:
                    continue

                left_is_iv = (isinstance(subscript_expr.left, VariableNode) and
                             subscript_expr.left.subscripts is None and
                             subscript_expr.left.name.upper() == iv_name)
                right_is_iv = (isinstance(subscript_expr.right, VariableNode) and
                              subscript_expr.right.subscripts is None and
                              subscript_expr.right.name.upper() == iv_name)

                if left_is_iv:
                    # IV * constant
                    const_val = self.evaluator.evaluate(subscript_expr.right)
                    if const_val is not None:
                        expr_desc = f"{array_name}({iv_name} * {const_val})"
                        optimized_desc = f"Use pointer increment by {const_val} instead of multiply"
                        iv_info.related_expressions.append((self.current_line, expr_desc, optimized_desc))
                        iv_info.strength_reduction_opportunities += 1
                        return  # Found match, stop checking
                elif right_is_iv:
                    # constant * IV
                    const_val = self.evaluator.evaluate(subscript_expr.left)
                    if const_val is not None:
                        expr_desc = f"{array_name}({const_val} * {iv_name})"
                        optimized_desc = f"Use pointer increment by {const_val} instead of multiply"
                        iv_info.related_expressions.append((self.current_line, expr_desc, optimized_desc))
                        iv_info.strength_reduction_opportunities += 1
                        return  # Found match, stop checking

        # Check for pattern using derived IV: J where J = I * constant
        elif isinstance(subscript_expr, VariableNode) and subscript_expr.subscripts is None:
            derived_var = subscript_expr.name.upper()
            derived_iv = self.active_ivs.get(derived_var)

            if derived_iv and not derived_iv.is_primary:
                # Using a derived IV in array subscript
                # Find the base IV
                base_iv = self.active_ivs.get(derived_iv.base_var)
                if base_iv and base_iv.is_primary:
                    expr_desc = f"{array_name}({derived_var})"
                    if derived_iv.coefficient != 1:
                        optimized_desc = f"Derived IV: increment {derived_var} by {derived_iv.coefficient} instead of computing from {derived_iv.base_var}"
                    else:
                        optimized_desc = f"Derived IV: use {derived_var} directly (tracks {derived_iv.base_var})"
                    base_iv.related_expressions.append((self.current_line, expr_desc, optimized_desc))
                    base_iv.strength_reduction_opportunities += 1

    def _analyze_if(self, stmt: IfStatementNode):
        """Analyze IF statement - handle compile-time evaluation when possible"""

        # Detect IF-GOTO loops (backward jumps)
        if stmt.then_line_number is not None and self.current_line is not None:
            if stmt.then_line_number < self.current_line:
                # This is a backward jump - potential loop!
                # Check if we've already registered this as a loop
                if stmt.then_line_number not in self.loops:
                    # Create a new IF-GOTO loop
                    loop = LoopAnalysis(
                        loop_type=LoopType.IF_GOTO,
                        start_line=stmt.then_line_number,
                        end_line=self.current_line,
                    )
                    self.loops[stmt.then_line_number] = loop
                else:
                    # Update the end line if this is a later backward jump to the same target
                    existing_loop = self.loops[stmt.then_line_number]
                    if existing_loop.loop_type == LoopType.IF_GOTO:
                        if existing_loop.end_line is None or self.current_line > existing_loop.end_line:
                            existing_loop.end_line = self.current_line

        # Try to evaluate the condition at compile time
        condition_value = self.evaluator.evaluate(stmt.condition)

        # Track branch optimization opportunity
        condition_desc = self._describe_expression(stmt.condition)
        branch_opt = BranchOptimization(
            line=self.current_line or 0,
            condition=condition_desc,
            is_constant=(condition_value is not None),
            constant_value=condition_value,
            then_target=stmt.then_line_number,
            else_target=stmt.else_line_number
        )

        if condition_value is not None:
            # Condition can be evaluated at compile time!
            # In BASIC, 0 is false, non-zero is true
            is_true = (condition_value != 0)

            branch_opt.always_true = is_true
            branch_opt.always_false = not is_true

            if is_true:
                # THEN branch always taken, ELSE is unreachable
                if stmt.else_statements or stmt.else_line_number:
                    branch_opt.unreachable_branch = "ELSE"
            else:
                # ELSE branch always taken (or nothing), THEN is unreachable
                if stmt.then_statements or stmt.then_line_number:
                    branch_opt.unreachable_branch = "THEN"

            self.branch_optimizations.append(branch_opt)

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
            # Need to analyze both branches and merge constant states AND available expressions

            # Save current state (both constants and available expressions)
            constants_before = self.evaluator.runtime_constants.copy()
            available_before = self.available_expressions.copy()
            ranges_before = self.active_ranges.copy()

            # Extract ranges from the condition for both branches
            then_ranges = self._extract_range_from_condition(stmt.condition, then_branch=True)
            else_ranges = self._extract_range_from_condition(stmt.condition, then_branch=False)

            # Analyze THEN branch
            then_constants = None
            then_available = None
            then_final_ranges = None
            if stmt.then_statements:
                # Apply THEN-specific ranges
                self._apply_ranges(then_ranges, f"IF condition (THEN branch)")

                for then_stmt in stmt.then_statements:
                    self._analyze_statement(then_stmt)
                then_constants = self.evaluator.runtime_constants.copy()
                then_available = self.available_expressions.copy()
                then_final_ranges = self.active_ranges.copy()

            # Restore state and analyze ELSE branch
            self.evaluator.runtime_constants = constants_before.copy()
            self.available_expressions = available_before.copy()
            self.active_ranges = ranges_before.copy()
            else_constants = None
            else_available = None
            else_final_ranges = None
            if stmt.else_statements:
                # Apply ELSE-specific ranges
                self._apply_ranges(else_ranges, f"IF condition (ELSE branch)")

                for else_stmt in stmt.else_statements:
                    self._analyze_statement(else_stmt)
                else_constants = self.evaluator.runtime_constants.copy()
                else_available = self.available_expressions.copy()
                else_final_ranges = self.active_ranges.copy()

            # Merge runtime constants: a variable is only constant after the IF if it has the same
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

            # Merge available expressions: an expression is available after the IF if:
            # 1. It was available before and is still available in both branches, OR
            # 2. It was computed in both branches (new in both)
            if then_available is not None and else_available is not None:
                # Both branches exist - keep expressions available in both
                merged_available = {}

                # First, keep expressions that were available before and still are in both branches
                for expr_hash in available_before:
                    if expr_hash in then_available and expr_hash in else_available:
                        # Use the earlier line number (from before the IF)
                        merged_available[expr_hash] = available_before[expr_hash]

                # Second, add expressions that were computed in BOTH branches (even if new)
                for expr_hash in then_available:
                    if expr_hash in else_available and expr_hash not in merged_available:
                        # This expression was computed in both branches
                        # Use the earlier of the two occurrences
                        merged_available[expr_hash] = min(then_available[expr_hash],
                                                         else_available[expr_hash])

                self.available_expressions = merged_available
            elif then_available is not None:
                # Only THEN branch exists - use its available expressions
                self.available_expressions = then_available
            elif else_available is not None:
                # Only ELSE branch exists - use its available expressions
                self.available_expressions = else_available
            else:
                # No branches - restore original state
                self.available_expressions = available_before

            # Merge ranges: take the union of ranges from both branches
            if then_final_ranges is not None and else_final_ranges is not None:
                # Both branches exist - merge ranges conservatively
                merged_ranges = {}

                # Get all variables that have ranges in either branch
                all_vars = set(then_final_ranges.keys()) | set(else_final_ranges.keys())

                for var_name in all_vars:
                    then_range = then_final_ranges.get(var_name)
                    else_range = else_final_ranges.get(var_name)

                    if then_range and else_range:
                        # Variable has range in both branches - merge with union
                        merged_ranges[var_name] = then_range.union(else_range)
                    elif then_range:
                        # Only in THEN branch - union with unbounded (from ELSE)
                        merged_ranges[var_name] = then_range.union(ValueRange())
                    elif else_range:
                        # Only in ELSE branch - union with unbounded (from THEN)
                        merged_ranges[var_name] = else_range.union(ValueRange())

                self.active_ranges = merged_ranges
            elif then_final_ranges is not None:
                # Only THEN branch exists
                self.active_ranges = then_final_ranges
            elif else_final_ranges is not None:
                # Only ELSE branch exists
                self.active_ranges = else_final_ranges
            else:
                # No branches - restore original state
                self.active_ranges = ranges_before

        # Analyze the condition expression itself for variable references
        # Don't track folding since we already evaluated it above
        self._analyze_expression(stmt.condition, track_folding=False)

    def _flatten_array_subscripts(self, var_name: str, subscripts: List, dimensions: List[int]) -> 'ExpressionNode':
        """
        Transform multi-dimensional array subscripts into a single flattened index.

        For OPTION BASE 0 (row-major order):
            A(i, j, k) with DIM A(d1, d2, d3) becomes:
            A(i * (d2+1) * (d3+1) + j * (d3+1) + k)

        For OPTION BASE 1:
            A(i, j, k) with DIM A(d1, d2, d3) becomes:
            A((i-1) * d2 * d3 + (j-1) * d3 + (k-1))

        This uses row-major order (rightmost index varies fastest).
        """
        if len(subscripts) == 1:
            # Already 1D, return as-is
            return subscripts[0]

        # Build the flattened index expression
        # Formula: idx = s[0] * stride[0] + s[1] * stride[1] + ... + s[n-1]
        # where stride[i] = product of (dim[i+1] * dim[i+2] * ... * dim[n-1])

        # Calculate strides for each dimension
        strides = []
        for i in range(len(dimensions)):
            stride = 1
            for j in range(i + 1, len(dimensions)):
                if self.array_base == 0:
                    stride *= (dimensions[j] + 1)
                else:
                    stride *= dimensions[j]
            strides.append(stride)

        # Build the expression: sum of (subscript[i] * stride[i])
        # For BASE 1, we need to subtract 1 from each subscript first
        terms = []
        for i, (sub, stride) in enumerate(zip(subscripts, strides)):
            if self.array_base == 1:
                # Subtract 1 from subscript: (sub - 1)
                adjusted_sub = BinaryOpNode(
                    operator=TokenType.MINUS,
                    left=sub,
                    right=NumberNode(1, 0, 0),
                    line_num=sub.line_num if hasattr(sub, 'line_num') else 0,
                    column=sub.column if hasattr(sub, 'column') else 0
                )
            else:
                adjusted_sub = sub

            # Multiply by stride
            if stride > 1:
                term = BinaryOpNode(
                    operator=TokenType.MULTIPLY,
                    left=adjusted_sub,
                    right=NumberNode(stride, 0, 0),
                    line_num=sub.line_num if hasattr(sub, 'line_num') else 0,
                    column=sub.column if hasattr(sub, 'column') else 0
                )
            else:
                term = adjusted_sub

            terms.append(term)

        # Sum all terms
        result = terms[0]
        for term in terms[1:]:
            result = BinaryOpNode(
                operator=TokenType.PLUS,
                left=result,
                right=term,
                line_num=term.line_num if hasattr(term, 'line_num') else 0,
                column=term.column if hasattr(term, 'column') else 0
            )

        return result

    def _analyze_option_base(self, stmt: OptionBaseStatementNode):
        """
        Analyze OPTION BASE statement (third pass).

        Note: OPTION BASE is already processed in the first pass (_collect_option_base)
        because it's a global compile-time declaration. This method is called during
        statement analysis but doesn't need to do anything since the global array_base
        is already set.
        """
        # Nothing to do - already handled in first pass
        pass

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

            # Calculate flattened size for multi-dimensional arrays
            # Each dimension is stored as the maximum index, so actual size is (dim + 1 - base)
            flattened_size = 1
            for dim in dimensions:
                # dim is the maximum index value
                # For OPTION BASE 0: size = dim + 1
                # For OPTION BASE 1: size = dim (since indices go from 1 to dim)
                if self.array_base == 0:
                    flattened_size *= (dim + 1)
                else:  # array_base == 1
                    flattened_size *= dim

            # Register the array
            var_type = self._get_type_from_name(array_decl.name)
            self.symbols.variables[var_name] = VariableInfo(
                name=var_name,
                var_type=var_type,
                is_array=True,
                dimensions=dimensions,
                flattened_size=flattened_size,
                first_use_line=self.current_line
            )

    def _analyze_assignment(self, stmt: LetStatementNode):
        """Analyze assignment - track variable usage and constant values"""
        var_name = stmt.variable.name.upper()

        # Register variable if not seen before
        if var_name not in self.symbols.variables:
            var_type = self._get_type_from_variable_node(stmt.variable)
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

        # Track that this variable is now initialized
        if stmt.variable.subscripts is None:
            self.initialized_variables.add(var_name)

        # Track variable modification in current loop
        if self.current_loop:
            self.current_loop.variables_modified.add(var_name)

        # Invalidate CSE: any expression using this variable is no longer available
        self._invalidate_expressions(var_name)

        # Clear range information: variable is being reassigned
        self._clear_range(var_name)

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

            # Copy propagation: Check if this is a simple copy (Y = X)
            # Only for simple variables (not arrays) assigned from simple variables
            if isinstance(stmt.expression, VariableNode) and stmt.expression.subscripts is None:
                source_var = stmt.expression.name.upper()
                # Don't track self-assignment (X = X)
                if source_var != var_name:
                    # Record this as an active copy
                    self.active_copies[var_name] = source_var
                    # Create a copy propagation record
                    self.copy_propagations.append(CopyPropagation(
                        line=self.current_line,
                        copy_var=var_name,
                        source_var=source_var
                    ))
            else:
                # Not a simple copy, invalidate if it was one
                if var_name in self.active_copies:
                    del self.active_copies[var_name]

            # Induction variable detection: Check if this is a derived IV
            # Pattern: J = I * constant or J = I + constant (where I is primary IV)
            if self.current_loop:
                self._detect_derived_induction_variable(var_name, stmt.expression)

            # Forward substitution tracking: Record this assignment
            # We'll analyze usage counts later in a second pass
            expr_desc = self._describe_expression(stmt.expression)
            self.variable_assignments[var_name] = (self.current_line, stmt.expression, expr_desc)
        else:
            # Array assignment, invalidate copy if it was one
            if var_name in self.active_copies:
                del self.active_copies[var_name]

    def _analyze_for(self, stmt: ForStatementNode):
        """Analyze FOR statement - comprehensive loop analysis"""
        # stmt.variable is a VariableNode
        var_name = stmt.variable.name.upper()

        # Register loop variable
        if var_name not in self.symbols.variables:
            var_type = self._get_type_from_variable_node(stmt.variable)
            self.symbols.variables[var_name] = VariableInfo(
                name=var_name,
                var_type=var_type,
                is_array=False,
                first_use_line=self.current_line
            )

        # FOR loop variable is initialized by the loop
        self.initialized_variables.add(var_name)

        # Create loop analysis structure
        loop_analysis = LoopAnalysis(
            loop_type=LoopType.FOR,
            start_line=self.current_line or 0,
            control_variable=var_name
        )

        # Try to determine loop bounds (for iteration count and unrolling)
        start_val = self.evaluator.evaluate(stmt.start_expr)
        end_val = self.evaluator.evaluate(stmt.end_expr)
        step_val = self.evaluator.evaluate(stmt.step_expr) if stmt.step_expr else 1

        if start_val is not None:
            loop_analysis.start_value = start_val
        if end_val is not None:
            loop_analysis.end_value = end_val
        if step_val is not None:
            loop_analysis.step_value = step_val

        # Calculate iteration count if all bounds are constant
        if start_val is not None and end_val is not None and step_val is not None and step_val != 0:
            try:
                iterations = int((end_val - start_val) / step_val) + 1
                if iterations > 0:
                    loop_analysis.iteration_count = iterations
                    # Consider unrolling small loops
                    if 2 <= iterations <= 10:
                        loop_analysis.can_unroll = True
                        loop_analysis.unroll_factor = iterations
            except (ValueError, ZeroDivisionError):
                pass

        # Track that this variable is modified by the loop
        loop_analysis.variables_modified.add(var_name)

        # Set up for nested loop tracking
        if self.current_loop:
            # We're inside another loop - track nesting
            loop_analysis.nested_in = self.current_loop.start_line
            self.current_loop.contains_loops.append(loop_analysis.start_line)

        # Save current loop context and push new loop
        self.loop_analysis_stack.append(self.current_loop)
        self.current_loop = loop_analysis

        # Store loop analysis
        self.loops[loop_analysis.start_line] = loop_analysis

        # Push onto old loop stack for validation
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

        # FOR loop variable is modified, so invalidate CSE and clear constant
        self._invalidate_expressions(var_name)
        self.evaluator.clear_constant(var_name)

        # Create primary induction variable
        iv = InductionVariable(
            variable=var_name,
            loop_start_line=self.current_line or 0,
            is_primary=True,
            base_value=start_val,
            coefficient=step_val
        )
        self.active_ivs[var_name] = iv
        self.induction_variables.append(iv)

    def _analyze_next(self, stmt: NextStatementNode):
        """Analyze NEXT statement - validate loop nesting and close loop"""
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

                # Close loop analysis
                if self.current_loop and self.current_loop.control_variable == var_name:
                    self.current_loop.end_line = self.current_line
                    # Clear induction variables for this loop
                    self._clear_loop_ivs(self.current_loop.start_line)
                    # Restore previous loop context
                    if self.loop_analysis_stack:
                        self.current_loop = self.loop_analysis_stack.pop()
        else:
            # NEXT without variable - matches innermost FOR
            self.loop_stack.pop()

            # Close loop analysis
            if self.current_loop:
                self.current_loop.end_line = self.current_line
                # Clear induction variables for this loop
                self._clear_loop_ivs(self.current_loop.start_line)
                # Restore previous loop context
                if self.loop_analysis_stack:
                    self.current_loop = self.loop_analysis_stack.pop()

    def _analyze_while(self, stmt: WhileStatementNode):
        """Analyze WHILE statement"""
        self.loop_stack.append(LoopInfo(
            loop_type="WHILE",
            variable=None,
            start_line=self.current_line or 0
        ))
        self._analyze_expression(stmt.condition)

        # Create loop analysis structure
        loop = LoopAnalysis(
            loop_type=LoopType.WHILE,
            start_line=self.current_line or 0,
            control_variable=None,  # WHILE loops don't have a single control variable
        )

        # Track nesting
        if self.current_loop:
            loop.nested_in = self.current_loop.start_line
            self.current_loop.contains_loops.append(loop.start_line)

        # Push current loop to stack and set as current
        if self.current_loop:
            self.loop_analysis_stack.append(self.current_loop)
        self.current_loop = loop
        self.loops[loop.start_line] = loop

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

        # Close loop analysis
        if self.current_loop and self.current_loop.loop_type == LoopType.WHILE:
            self.current_loop.end_line = self.current_line
            # Restore previous loop context
            if self.loop_analysis_stack:
                self.current_loop = self.loop_analysis_stack.pop()
            else:
                self.current_loop = None

    def _extract_range_from_condition(self, condition, then_branch: bool) -> Dict[str, ValueRange]:
        """
        Extract value ranges from a conditional expression.

        Args:
            condition: The condition expression (e.g., X > 5)
            then_branch: True if analyzing THEN branch, False for ELSE

        Returns:
            Dictionary mapping variable names to their ranges
        """
        ranges = {}

        if not isinstance(condition, BinaryOpNode):
            return ranges

        # Handle relational operators
        op = condition.operator
        left = condition.left
        right = condition.right

        # Only handle simple cases: variable compared to constant
        var_node = None
        const_value = None

        # Check if left is variable and right is constant
        if isinstance(left, VariableNode) and left.subscripts is None:
            const_value = self.evaluator.evaluate(right)
            if const_value is not None:
                var_node = left
                left_is_var = True
        # Check if right is variable and left is constant
        elif isinstance(right, VariableNode) and right.subscripts is None:
            const_value = self.evaluator.evaluate(left)
            if const_value is not None:
                var_node = right
                left_is_var = False

        if var_node is None or const_value is None:
            return ranges

        # Skip if const_value is not a number (e.g., string comparison)
        if not isinstance(const_value, (int, float)):
            return ranges

        var_name = var_node.name.upper()

        # Determine the range based on operator and branch
        # For THEN branch, condition is true
        # For ELSE branch, condition is false (invert it)

        if left_is_var:
            # Variable on left: X > 5, X >= 5, X < 5, X <= 5, X = 5, X <> 5
            if op == TokenType.GREATER_THAN:
                if then_branch:
                    # X > const means X in (const, +∞)
                    ranges[var_name] = ValueRange(min_value=const_value + (1 if isinstance(const_value, int) else 0.001))
                else:
                    # NOT(X > const) means X <= const
                    ranges[var_name] = ValueRange(max_value=const_value)
            elif op == TokenType.GREATER_EQUAL:
                if then_branch:
                    # X >= const
                    ranges[var_name] = ValueRange(min_value=const_value)
                else:
                    # NOT(X >= const) means X < const
                    ranges[var_name] = ValueRange(max_value=const_value - (1 if isinstance(const_value, int) else 0.001))
            elif op == TokenType.LESS_THAN:
                if then_branch:
                    # X < const
                    ranges[var_name] = ValueRange(max_value=const_value - (1 if isinstance(const_value, int) else 0.001))
                else:
                    # NOT(X < const) means X >= const
                    ranges[var_name] = ValueRange(min_value=const_value)
            elif op == TokenType.LESS_EQUAL:
                if then_branch:
                    # X <= const
                    ranges[var_name] = ValueRange(max_value=const_value)
                else:
                    # NOT(X <= const) means X > const
                    ranges[var_name] = ValueRange(min_value=const_value + (1 if isinstance(const_value, int) else 0.001))
            elif op == TokenType.EQUAL:
                if then_branch:
                    # X = const
                    ranges[var_name] = ValueRange(min_value=const_value, max_value=const_value, is_constant=True)
                # For ELSE (X <> const), range is unbounded
            elif op == TokenType.NOT_EQUAL:
                if not then_branch:
                    # NOT(X <> const) means X = const
                    ranges[var_name] = ValueRange(min_value=const_value, max_value=const_value, is_constant=True)
                # For THEN (X <> const), range is unbounded
        else:
            # Constant on left: 5 > X, 5 >= X, 5 < X, 5 <= X, 5 = X, 5 <> X
            # Flip the operator
            if op == TokenType.GREATER_THAN:
                if then_branch:
                    # const > X means X < const
                    ranges[var_name] = ValueRange(max_value=const_value - (1 if isinstance(const_value, int) else 0.001))
                else:
                    # NOT(const > X) means X >= const
                    ranges[var_name] = ValueRange(min_value=const_value)
            elif op == TokenType.GREATER_EQUAL:
                if then_branch:
                    # const >= X means X <= const
                    ranges[var_name] = ValueRange(max_value=const_value)
                else:
                    # NOT(const >= X) means X > const
                    ranges[var_name] = ValueRange(min_value=const_value + (1 if isinstance(const_value, int) else 0.001))
            elif op == TokenType.LESS_THAN:
                if then_branch:
                    # const < X means X > const
                    ranges[var_name] = ValueRange(min_value=const_value + (1 if isinstance(const_value, int) else 0.001))
                else:
                    # NOT(const < X) means X <= const
                    ranges[var_name] = ValueRange(max_value=const_value)
            elif op == TokenType.LESS_EQUAL:
                if then_branch:
                    # const <= X means X >= const
                    ranges[var_name] = ValueRange(min_value=const_value)
                else:
                    # NOT(const <= X) means X < const
                    ranges[var_name] = ValueRange(max_value=const_value - (1 if isinstance(const_value, int) else 0.001))
            elif op == TokenType.EQUAL:
                if then_branch:
                    # const = X means X = const
                    ranges[var_name] = ValueRange(min_value=const_value, max_value=const_value, is_constant=True)
            elif op == TokenType.NOT_EQUAL:
                if not then_branch:
                    # NOT(const <> X) means X = const
                    ranges[var_name] = ValueRange(min_value=const_value, max_value=const_value, is_constant=True)

        return ranges

    def _apply_ranges(self, ranges: Dict[str, ValueRange], context: str):
        """Apply ranges to active_ranges, intersecting with existing ranges"""
        for var_name, new_range in ranges.items():
            if var_name in self.active_ranges:
                # Intersect with existing range
                self.active_ranges[var_name] = self.active_ranges[var_name].intersect(new_range)
            else:
                # New range
                self.active_ranges[var_name] = new_range

            # Record this range analysis
            self.range_info.append(RangeAnalysisInfo(
                line=self.current_line or 0,
                variable=var_name,
                range=self.active_ranges[var_name],
                context=context
            ))

            # Check if this range is a constant - if so, add to runtime constants!
            if self.active_ranges[var_name].is_constant:
                const_val = self.active_ranges[var_name].min_value
                if const_val is not None:
                    # Record that this enabled constant propagation
                    self.range_info[-1].enabled_optimization = f"Constant propagation: {var_name} = {const_val}"
                    self.evaluator.set_constant(var_name, const_val)

    def _clear_range(self, var_name: str):
        """Clear range information for a variable (when it's reassigned)"""
        var_name_upper = var_name.upper()
        if var_name_upper in self.active_ranges:
            del self.active_ranges[var_name_upper]

    def _analyze_expression(self, expr, context: str = "expression", track_folding: bool = True, track_cse: bool = True):
        """
        Analyze an expression - track variable usage, perform constant folding, and track CSE.

        Args:
            expr: The expression node to analyze
            context: Description of where this expression appears (for reporting)
            track_folding: Whether to track this expression in folding optimizations
            track_cse: Whether to track this expression for CSE
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

        # Track for common subexpression elimination (only for top-level expressions)
        if track_cse:
            self._track_expression_for_cse(expr)

        if isinstance(expr, VariableNode):
            var_name = expr.name.upper()
            if var_name not in self.symbols.variables:
                var_type = self._get_type_from_variable_node(expr)
                # Check if this is an array (has subscripts)
                is_array = expr.subscripts is not None
                self.symbols.variables[var_name] = VariableInfo(
                    name=var_name,
                    var_type=var_type,
                    is_array=is_array,
                    first_use_line=self.current_line
                )

            # Check for uninitialized variable use (only for simple variables, not arrays)
            # Note: BASIC defaults all variables to 0, but this is still a useful warning
            if expr.subscripts is None and var_name not in self.initialized_variables:
                # Check if this is in a DIM statement or FOR loop (those initialize)
                # Skip warnings for FOR loop variables as they're initialized by the FOR statement
                if context not in ("DIM", "FOR start", "FOR end", "FOR step"):
                    self.uninitialized_warnings.append(UninitializedVariableWarning(
                        line=self.current_line or 0,
                        variable=var_name,
                        context=context
                    ))

            # Track copy propagation opportunities:
            # If this variable is a copy of another variable, record a propagation opportunity
            if expr.subscripts is None and var_name in self.active_copies:
                # Find the copy record for this variable
                for copy_rec in self.copy_propagations:
                    if copy_rec.copy_var == var_name:
                        copy_rec.propagation_count += 1
                        copy_rec.propagated_lines.append(self.current_line)
                        break

            # Analyze and flatten subscripts if present
            if expr.subscripts:
                # Check for IV strength reduction BEFORE analyzing (which transforms expressions)
                if self.current_loop:
                    for subscript in expr.subscripts:
                        self._detect_iv_strength_reduction(var_name, subscript)

                # Now analyze each subscript expression
                for subscript in expr.subscripts:
                    self._analyze_expression(subscript, "array subscript", track_folding=False, track_cse=True)

                # If multi-dimensional, flatten the subscripts
                if len(expr.subscripts) > 1:
                    var_info = self.symbols.variables.get(var_name)
                    if var_info and var_info.is_array and var_info.dimensions:
                        # Transform multi-dimensional subscripts to flat index
                        flattened = self._flatten_array_subscripts(var_name, expr.subscripts, var_info.dimensions)
                        # Replace the subscripts list with a single flattened expression
                        expr.subscripts = [flattened]

        elif isinstance(expr, BinaryOpNode):
            # First analyze child expressions
            self._analyze_expression(expr.left, "binary operation", track_folding=False, track_cse=True)
            self._analyze_expression(expr.right, "binary operation", track_folding=False, track_cse=True)

            # Apply expression reassociation first (groups constants together)
            reassociated = self._apply_expression_reassociation(expr)
            if reassociated is not None:
                # Replace the expression node's internals with the reassociated version
                if isinstance(reassociated, BinaryOpNode):
                    expr.left = reassociated.left
                    expr.operator = reassociated.operator
                    expr.right = reassociated.right
                elif isinstance(reassociated, NumberNode):
                    # The whole expression became a constant
                    pass

            # Apply strength reduction if possible
            reduced = self._apply_strength_reduction(expr)
            if reduced is not None:
                # Replace the expression node's internals with the reduced version
                # This allows the transformation to propagate up the tree
                if isinstance(reduced, BinaryOpNode):
                    expr.left = reduced.left
                    expr.operator = reduced.operator
                    expr.right = reduced.right
                elif isinstance(reduced, NumberNode):
                    # Can't change type, but note it's been reduced
                    pass
                elif isinstance(reduced, VariableNode):
                    # Can't change type, but note it's been reduced
                    pass

        elif isinstance(expr, UnaryOpNode):
            # First analyze the operand
            self._analyze_expression(expr.operand, "unary operation", track_folding=False, track_cse=True)

            # Apply algebraic simplification if possible
            reduced = self._apply_algebraic_simplification(expr)
            if reduced is not None:
                # Replace the expression node's internals with the reduced version
                if isinstance(reduced, UnaryOpNode):
                    expr.operator = reduced.operator
                    expr.operand = reduced.operand
                elif isinstance(reduced, NumberNode):
                    # Can't change type, but note it's been reduced
                    pass
                # else it's some other expression type (e.g., VariableNode from double NOT)

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
                    self._analyze_expression(arg, f"function argument", track_folding=False, track_cse=True)

    def _hash_expression(self, expr) -> str:
        """
        Generate a canonical hash/representation for expression equivalence checking.
        Two expressions with the same hash are considered equivalent.
        """
        if expr is None:
            return "NULL"

        if isinstance(expr, NumberNode):
            return f"NUM:{expr.value}"

        if isinstance(expr, StringNode):
            return f"STR:{expr.value}"

        if isinstance(expr, VariableNode):
            var_name = expr.name.upper()
            if expr.subscripts:
                # Array access - include subscript hashes
                subscript_hashes = ",".join(self._hash_expression(sub) for sub in expr.subscripts)
                return f"ARRAY:{var_name}[{subscript_hashes}]"
            return f"VAR:{var_name}"

        if isinstance(expr, BinaryOpNode):
            # Use operator type name for consistency
            op_str = str(expr.operator)
            left_hash = self._hash_expression(expr.left)
            right_hash = self._hash_expression(expr.right)
            return f"BIN:{op_str}({left_hash},{right_hash})"

        if isinstance(expr, UnaryOpNode):
            op_str = str(expr.operator)
            operand_hash = self._hash_expression(expr.operand)
            return f"UNARY:{op_str}({operand_hash})"

        if isinstance(expr, FunctionCallNode):
            func_name = expr.name.upper()
            if expr.arguments:
                arg_hashes = ",".join(self._hash_expression(arg) for arg in expr.arguments)
                return f"FUNC:{func_name}({arg_hashes})"
            return f"FUNC:{func_name}()"

        # Unknown expression type
        return f"UNKNOWN:{type(expr).__name__}"

    def _get_expression_variables(self, expr) -> Set[str]:
        """
        Get all variables referenced in an expression.
        Used to determine when a CSE becomes invalid (variable modified).
        """
        variables = set()

        if isinstance(expr, VariableNode):
            variables.add(expr.name.upper())
            # Also check array subscripts
            if expr.subscripts:
                for subscript in expr.subscripts:
                    variables.update(self._get_expression_variables(subscript))

        elif isinstance(expr, BinaryOpNode):
            variables.update(self._get_expression_variables(expr.left))
            variables.update(self._get_expression_variables(expr.right))

        elif isinstance(expr, UnaryOpNode):
            variables.update(self._get_expression_variables(expr.operand))

        elif isinstance(expr, FunctionCallNode):
            if expr.arguments:
                for arg in expr.arguments:
                    variables.update(self._get_expression_variables(arg))

        return variables

    def _is_cse_candidate(self, expr) -> bool:
        """
        Determine if an expression is a candidate for CSE.

        Criteria:
        - Not a simple literal (number/string)
        - Not a simple variable reference (no subscripts)
        - Contains computation that could be expensive
        """
        # Literals are not CSE candidates
        if isinstance(expr, (NumberNode, StringNode)):
            return False

        # Simple variable references are not CSE candidates
        if isinstance(expr, VariableNode) and expr.subscripts is None:
            return False

        # Everything else is a candidate:
        # - Array accesses (subscript evaluation)
        # - Binary/unary operations
        # - Function calls
        return True

    def _track_expression_for_cse(self, expr):
        """
        Track an expression for common subexpression elimination.
        If this expression has been seen before and is still available,
        record it as a common subexpression.
        """
        if not self._is_cse_candidate(expr):
            return

        # Note: We DO track expressions even if they can be constant-folded,
        # because:
        # 1. They represent repeated computations in the source code
        # 2. Constant folding might not be possible in all contexts
        # 3. It's useful to show programmers where they're repeating expressions

        expr_hash = self._hash_expression(expr)
        expr_desc = self._describe_expression(expr)
        expr_vars = self._get_expression_variables(expr)

        if expr_hash in self.available_expressions:
            # This expression has been seen before and is still available!
            if expr_hash in self.common_subexpressions:
                # Already tracking this CSE - add another occurrence
                self.common_subexpressions[expr_hash].occurrences.append(self.current_line)
            else:
                # First time seeing this expression again - create CSE record
                cse = CommonSubexpression(
                    expression_hash=expr_hash,
                    expression_desc=expr_desc,
                    first_line=self.available_expressions[expr_hash],
                    occurrences=[self.current_line],
                    variables_used=expr_vars
                )
                # Generate a suggested temporary variable name
                self.cse_counter += 1
                cse.temp_var_name = f"T{self.cse_counter}#"
                self.common_subexpressions[expr_hash] = cse
        else:
            # First time seeing this expression - mark it as available
            self.available_expressions[expr_hash] = self.current_line

    def _invalidate_expressions(self, var_name: str):
        """
        Invalidate all available expressions that reference a variable.
        Called when a variable is modified (assignment, INPUT, READ, FOR loop, etc.)
        Also invalidates copy propagation for this variable.
        """
        var_name_upper = var_name.upper()
        to_remove = []

        for expr_hash in list(self.available_expressions.keys()):
            # Check if this expression uses the variable
            # For CSEs, we have the variables stored
            if expr_hash in self.common_subexpressions:
                cse = self.common_subexpressions[expr_hash]
                if var_name_upper in cse.variables_used:
                    to_remove.append(expr_hash)
            else:
                # For non-CSE available expressions, we need to check by re-parsing the hash
                # The hash contains variable names, so we can do a simple check
                if f"VAR:{var_name_upper}" in expr_hash or f"ARRAY:{var_name_upper}" in expr_hash:
                    to_remove.append(expr_hash)

        # Remove invalidated expressions
        for expr_hash in to_remove:
            if expr_hash in self.available_expressions:
                del self.available_expressions[expr_hash]

        # Invalidate copy propagation:
        # 1. If this variable is a copy, it's no longer valid
        if var_name_upper in self.active_copies:
            del self.active_copies[var_name_upper]

        # 2. If this variable is the source of other copies, invalidate those too
        copies_to_remove = []
        for copy_var, source_var in self.active_copies.items():
            if source_var == var_name_upper:
                copies_to_remove.append(copy_var)

        for copy_var in copies_to_remove:
            del self.active_copies[copy_var]

    def _clear_all_available_expressions(self):
        """
        Clear all available expressions.
        Called at control flow boundaries (IF, GOTO, etc.) where we can't
        guarantee expression availability.
        """
        self.available_expressions.clear()

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
        # Note: TokenType is already imported from src.tokens at the top
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
        # Note: TokenType is already imported from src.tokens at the top
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

    def _apply_algebraic_simplification(self, expr) -> Optional[Any]:
        """
        Apply algebraic simplifications to unary operations (NOT, negation).

        Returns the transformed expression node, or None if no reduction applies.
        """
        if not isinstance(expr, UnaryOpNode):
            return None

        # Note: TokenType is already imported from src.tokens at the top

        original_desc = self._describe_expression(expr)
        reduction_type = None
        savings = None
        new_expr = None

        # NOT optimizations
        if expr.operator == TokenType.NOT:
            # NOT(NOT X) -> X (double negation elimination)
            if isinstance(expr.operand, UnaryOpNode) and expr.operand.operator == TokenType.NOT:
                new_expr = expr.operand.operand
                reduction_type = "double NOT -> identity"
                savings = "Eliminate double negation"

            # Relational operator inversion: NOT(A op B) -> A op' B
            elif isinstance(expr.operand, BinaryOpNode):
                op = expr.operand.operator
                inverted_op = None

                # Map each relational operator to its inverse
                if op == TokenType.GREATER_THAN:
                    inverted_op = TokenType.LESS_EQUAL
                    reduction_type = "NOT(A > B) -> A <= B"
                elif op == TokenType.LESS_THAN:
                    inverted_op = TokenType.GREATER_EQUAL
                    reduction_type = "NOT(A < B) -> A >= B"
                elif op == TokenType.GREATER_EQUAL:
                    inverted_op = TokenType.LESS_THAN
                    reduction_type = "NOT(A >= B) -> A < B"
                elif op == TokenType.LESS_EQUAL:
                    inverted_op = TokenType.GREATER_THAN
                    reduction_type = "NOT(A <= B) -> A > B"
                elif op == TokenType.EQUAL:
                    inverted_op = TokenType.NOT_EQUAL
                    reduction_type = "NOT(A = B) -> A <> B"
                elif op == TokenType.NOT_EQUAL:
                    inverted_op = TokenType.EQUAL
                    reduction_type = "NOT(A <> B) -> A = B"
                # De Morgan's laws
                elif op == TokenType.AND:
                    # NOT(A AND B) -> (NOT A) OR (NOT B)
                    new_expr = BinaryOpNode(
                        left=UnaryOpNode(operator=TokenType.NOT, operand=expr.operand.left),
                        operator=TokenType.OR,
                        right=UnaryOpNode(operator=TokenType.NOT, operand=expr.operand.right)
                    )
                    reduction_type = "De Morgan: NOT(A AND B) -> (NOT A) OR (NOT B)"
                    savings = "Apply De Morgan's law"
                elif op == TokenType.OR:
                    # NOT(A OR B) -> (NOT A) AND (NOT B)
                    new_expr = BinaryOpNode(
                        left=UnaryOpNode(operator=TokenType.NOT, operand=expr.operand.left),
                        operator=TokenType.AND,
                        right=UnaryOpNode(operator=TokenType.NOT, operand=expr.operand.right)
                    )
                    reduction_type = "De Morgan: NOT(A OR B) -> (NOT A) AND (NOT B)"
                    savings = "Apply De Morgan's law"

                # If we found an inverted operator, create the new expression
                if inverted_op is not None:
                    new_expr = BinaryOpNode(
                        left=expr.operand.left,
                        operator=inverted_op,
                        right=expr.operand.right
                    )
                    savings = "Eliminate NOT by inverting relational operator"

            # NOT(0) -> -1, NOT(-1) -> 0
            if new_expr is None:
                operand_val = self.evaluator.evaluate(expr.operand)
                if operand_val is not None:
                    if operand_val == 0:
                        new_expr = NumberNode(value=-1.0, literal="-1")
                        reduction_type = "NOT FALSE -> TRUE"
                        savings = "Constant folding"
                    elif operand_val == -1:
                        new_expr = NumberNode(value=0.0, literal="0")
                        reduction_type = "NOT TRUE -> FALSE"
                        savings = "Constant folding"

        # Negation optimizations
        elif expr.operator == TokenType.MINUS:
            # -(-X) -> X (double negation)
            if isinstance(expr.operand, UnaryOpNode) and expr.operand.operator == TokenType.MINUS:
                new_expr = expr.operand.operand
                reduction_type = "double negation -> identity"
                savings = "Eliminate double negation"

            # -(0) -> 0
            operand_val = self.evaluator.evaluate(expr.operand)
            if operand_val == 0:
                new_expr = NumberNode(value=0.0, literal="0")
                reduction_type = "negate 0 -> 0"
                savings = "Constant folding"

        # Record the simplification if found
        if reduction_type and self.current_line is not None:
            reduced_desc = self._describe_expression(new_expr) if new_expr else original_desc
            self.strength_reductions.append(StrengthReduction(
                line=self.current_line,
                original_expr=original_desc,
                reduced_expr=reduced_desc,
                reduction_type=reduction_type,
                savings=savings or ""
            ))

        return new_expr

    def _apply_strength_reduction(self, expr) -> Optional[Any]:
        """
        Apply strength reduction to transform expensive operations into cheaper ones.

        Returns the transformed expression node, or None if no reduction applies.

        Transformations:
        1. X * 2^n -> X << n (or X + X for n=1)
        2. X / 2^n -> X >> n
        3. X * 1 -> X
        4. X * 0 -> 0
        5. X + 0 -> X
        6. X - 0 -> X
        7. X ^ 2 -> X * X
        8. X ^ small_int -> repeated multiplication
        9. Boolean: X AND TRUE -> X, X OR FALSE -> X, etc.
        """
        if not isinstance(expr, BinaryOpNode):
            return None

        # Note: TokenType is already imported from src.tokens at the top
        import math

        original_desc = self._describe_expression(expr)
        reduction_type = None
        savings = None
        new_expr = None

        # Get values for constant operands
        left_val = self.evaluator.evaluate(expr.left)
        right_val = self.evaluator.evaluate(expr.right)

        # Multiplication by power of 2 -> bit shift or addition
        if expr.operator == TokenType.MULTIPLY:
            # X * 2 -> X + X (replace MUL with ADD)
            if right_val == 2:
                new_expr = BinaryOpNode(
                    left=expr.left,
                    operator=TokenType.PLUS,
                    right=expr.left
                )
                reduction_type = "multiply by 2 -> addition"
                savings = "Replace MUL with ADD"
            elif left_val == 2:
                new_expr = BinaryOpNode(
                    left=expr.right,
                    operator=TokenType.PLUS,
                    right=expr.right
                )
                reduction_type = "multiply by 2 -> addition"
                savings = "Replace MUL with ADD"

            # X * 1 -> X
            elif right_val == 1:
                new_expr = expr.left
                reduction_type = "multiply by 1 -> identity"
                savings = "Eliminate MUL"
            elif left_val == 1:
                new_expr = expr.right
                reduction_type = "multiply by 1 -> identity"
                savings = "Eliminate MUL"

            # X * 0 -> 0
            elif right_val == 0:
                new_expr = NumberNode(value=0.0, literal="0")
                reduction_type = "multiply by 0 -> constant"
                savings = "Eliminate MUL, replace with 0"
            elif left_val == 0:
                new_expr = NumberNode(value=0.0, literal="0")
                reduction_type = "multiply by 0 -> constant"
                savings = "Eliminate MUL, replace with 0"

            # X * 4 -> (X + X) + (X + X) or X * 2^n for larger powers
            elif right_val is not None and isinstance(right_val, (int, float)) and right_val > 0:
                # Check if it's an integer value (might be stored as float)
                if right_val == int(right_val):
                    int_val = int(right_val)
                    # Check if power of 2
                    if int_val > 2 and (int_val & (int_val - 1)) == 0:
                        # Power of 2 > 2 - suggest shift (note: BASIC doesn't have << but good to track)
                        shift_amount = int(math.log2(int_val))
                        reduction_type = f"multiply by {int_val} -> shift left {shift_amount}"
                        savings = f"Replace MUL with shift/repeated addition"
                        # Don't actually transform since BASIC doesn't have <<
                        # But track the opportunity
            elif left_val is not None and isinstance(left_val, (int, float)) and left_val > 0:
                if left_val == int(left_val):
                    int_val = int(left_val)
                    if int_val > 2 and (int_val & (int_val - 1)) == 0:
                        shift_amount = int(math.log2(int_val))
                        reduction_type = f"multiply by {int_val} -> shift left {shift_amount}"
                        savings = f"Replace MUL with shift/repeated addition"

        # Division by power of 2 -> bit shift (for integers)
        elif expr.operator == TokenType.BACKSLASH:  # Integer division in BASIC
            if right_val is not None and isinstance(right_val, (int, float)) and right_val > 0:
                if right_val == int(right_val):
                    int_val = int(right_val)
                    if int_val > 0 and (int_val & (int_val - 1)) == 0:
                        shift_amount = int(math.log2(int_val))
                        reduction_type = f"integer division by {int_val} -> shift right {shift_amount}"
                        savings = "Replace DIV with shift"
                        # Don't transform, just track
            # X \ 1 -> X
            elif right_val == 1:
                new_expr = expr.left
                reduction_type = "divide by 1 -> identity"
                savings = "Eliminate DIV"

        # Regular division optimizations
        elif expr.operator == TokenType.DIVIDE:
            # X / 1 -> X
            if right_val == 1:
                new_expr = expr.left
                reduction_type = "divide by 1 -> identity"
                savings = "Eliminate DIV"

        # Addition optimizations
        elif expr.operator == TokenType.PLUS:
            # X + 0 -> X
            if right_val == 0:
                new_expr = expr.left
                reduction_type = "add 0 -> identity"
                savings = "Eliminate ADD"
            elif left_val == 0:
                new_expr = expr.right
                reduction_type = "add 0 -> identity"
                savings = "Eliminate ADD"

        # Subtraction optimizations
        elif expr.operator == TokenType.MINUS:
            # X - 0 -> X
            if right_val == 0:
                new_expr = expr.left
                reduction_type = "subtract 0 -> identity"
                savings = "Eliminate SUB"
            # X - X -> 0 (if same variable)
            elif (isinstance(expr.left, VariableNode) and
                  isinstance(expr.right, VariableNode) and
                  expr.left.name.upper() == expr.right.name.upper() and
                  expr.left.subscripts is None and expr.right.subscripts is None):
                new_expr = NumberNode(value=0.0, literal="0")
                reduction_type = "subtract self -> constant"
                savings = "Eliminate SUB, replace with 0"

        # Exponentiation optimizations
        elif expr.operator == TokenType.POWER:
            # X ^ 2 -> X * X
            if right_val == 2:
                new_expr = BinaryOpNode(
                    left=expr.left,
                    operator=TokenType.MULTIPLY,
                    right=expr.left
                )
                reduction_type = "power of 2 -> multiplication"
                savings = "Replace POW with MUL"
            # X ^ 1 -> X
            elif right_val == 1:
                new_expr = expr.left
                reduction_type = "power of 1 -> identity"
                savings = "Eliminate POW"
            # X ^ 0 -> 1
            elif right_val == 0:
                new_expr = NumberNode(value=1.0, literal="1")
                reduction_type = "power of 0 -> constant"
                savings = "Eliminate POW, replace with 1"
            # X ^ 3 -> X * X * X (for small integers)
            elif right_val in [3, 4]:
                # Build repeated multiplication
                result = expr.left
                for _ in range(int(right_val) - 1):
                    result = BinaryOpNode(
                        left=result,
                        operator=TokenType.MULTIPLY,
                        right=expr.left
                    )
                new_expr = result
                reduction_type = f"power of {int(right_val)} -> repeated multiplication"
                savings = f"Replace POW with {int(right_val)-1} MUL operations"

        # Boolean/Logical optimizations (BASIC uses -1 for TRUE, 0 for FALSE)
        elif expr.operator == TokenType.AND:
            # X AND 0 -> 0 (FALSE)
            if right_val == 0:
                new_expr = NumberNode(value=0.0, literal="0")
                reduction_type = "AND with FALSE -> FALSE"
                savings = "Eliminate AND, replace with 0"
            elif left_val == 0:
                new_expr = NumberNode(value=0.0, literal="0")
                reduction_type = "AND with FALSE -> FALSE"
                savings = "Eliminate AND, replace with 0"
            # X AND -1 -> X (TRUE in BASIC is -1)
            elif right_val == -1:
                new_expr = expr.left
                reduction_type = "AND with TRUE -> identity"
                savings = "Eliminate AND"
            elif left_val == -1:
                new_expr = expr.right
                reduction_type = "AND with TRUE -> identity"
                savings = "Eliminate AND"
            # X AND X -> X
            elif (isinstance(expr.left, VariableNode) and
                  isinstance(expr.right, VariableNode) and
                  expr.left.name.upper() == expr.right.name.upper() and
                  expr.left.subscripts is None and expr.right.subscripts is None):
                new_expr = expr.left
                reduction_type = "AND with self -> identity"
                savings = "Eliminate AND"
            # Absorption law: (A OR B) AND A -> A
            elif (isinstance(expr.left, BinaryOpNode) and
                  expr.left.operator == TokenType.OR and
                  isinstance(expr.right, VariableNode)):
                # Check if right operand matches either side of OR
                if (isinstance(expr.left.left, VariableNode) and
                    expr.left.left.name.upper() == expr.right.name.upper() and
                    expr.left.left.subscripts is None and expr.right.subscripts is None):
                    new_expr = expr.right
                    reduction_type = "Absorption: (A OR B) AND A -> A"
                    savings = "Eliminate redundant AND and OR"
                elif (isinstance(expr.left.right, VariableNode) and
                      expr.left.right.name.upper() == expr.right.name.upper() and
                      expr.left.right.subscripts is None and expr.right.subscripts is None):
                    new_expr = expr.right
                    reduction_type = "Absorption: (B OR A) AND A -> A"
                    savings = "Eliminate redundant AND and OR"
            # Absorption law: A AND (A OR B) -> A
            elif (isinstance(expr.right, BinaryOpNode) and
                  expr.right.operator == TokenType.OR and
                  isinstance(expr.left, VariableNode)):
                # Check if left operand matches either side of OR
                if (isinstance(expr.right.left, VariableNode) and
                    expr.right.left.name.upper() == expr.left.name.upper() and
                    expr.right.left.subscripts is None and expr.left.subscripts is None):
                    new_expr = expr.left
                    reduction_type = "Absorption: A AND (A OR B) -> A"
                    savings = "Eliminate redundant AND and OR"
                elif (isinstance(expr.right.right, VariableNode) and
                      expr.right.right.name.upper() == expr.left.name.upper() and
                      expr.right.right.subscripts is None and expr.left.subscripts is None):
                    new_expr = expr.left
                    reduction_type = "Absorption: A AND (B OR A) -> A"
                    savings = "Eliminate redundant AND and OR"

        elif expr.operator == TokenType.OR:
            # X OR -1 -> -1 (TRUE)
            if right_val == -1:
                new_expr = NumberNode(value=-1.0, literal="-1")
                reduction_type = "OR with TRUE -> TRUE"
                savings = "Eliminate OR, replace with -1"
            elif left_val == -1:
                new_expr = NumberNode(value=-1.0, literal="-1")
                reduction_type = "OR with TRUE -> TRUE"
                savings = "Eliminate OR, replace with -1"
            # X OR 0 -> X (FALSE)
            elif right_val == 0:
                new_expr = expr.left
                reduction_type = "OR with FALSE -> identity"
                savings = "Eliminate OR"
            elif left_val == 0:
                new_expr = expr.right
                reduction_type = "OR with FALSE -> identity"
                savings = "Eliminate OR"
            # X OR X -> X
            elif (isinstance(expr.left, VariableNode) and
                  isinstance(expr.right, VariableNode) and
                  expr.left.name.upper() == expr.right.name.upper() and
                  expr.left.subscripts is None and expr.right.subscripts is None):
                new_expr = expr.left
                reduction_type = "OR with self -> identity"
                savings = "Eliminate OR"
            # Absorption law: (A AND B) OR A -> A
            elif (isinstance(expr.left, BinaryOpNode) and
                  expr.left.operator == TokenType.AND and
                  isinstance(expr.right, VariableNode)):
                # Check if right operand matches either side of AND
                if (isinstance(expr.left.left, VariableNode) and
                    expr.left.left.name.upper() == expr.right.name.upper() and
                    expr.left.left.subscripts is None and expr.right.subscripts is None):
                    new_expr = expr.right
                    reduction_type = "Absorption: (A AND B) OR A -> A"
                    savings = "Eliminate redundant OR and AND"
                elif (isinstance(expr.left.right, VariableNode) and
                      expr.left.right.name.upper() == expr.right.name.upper() and
                      expr.left.right.subscripts is None and expr.right.subscripts is None):
                    new_expr = expr.right
                    reduction_type = "Absorption: (B AND A) OR A -> A"
                    savings = "Eliminate redundant OR and AND"
            # Absorption law: A OR (A AND B) -> A
            elif (isinstance(expr.right, BinaryOpNode) and
                  expr.right.operator == TokenType.AND and
                  isinstance(expr.left, VariableNode)):
                # Check if left operand matches either side of AND
                if (isinstance(expr.right.left, VariableNode) and
                    expr.right.left.name.upper() == expr.left.name.upper() and
                    expr.right.left.subscripts is None and expr.left.subscripts is None):
                    new_expr = expr.left
                    reduction_type = "Absorption: A OR (A AND B) -> A"
                    savings = "Eliminate redundant OR and AND"
                elif (isinstance(expr.right.right, VariableNode) and
                      expr.right.right.name.upper() == expr.left.name.upper() and
                      expr.right.right.subscripts is None and expr.left.subscripts is None):
                    new_expr = expr.left
                    reduction_type = "Absorption: A OR (B AND A) -> A"
                    savings = "Eliminate redundant OR and AND"

        elif expr.operator == TokenType.XOR:
            # X XOR 0 -> X
            if right_val == 0:
                new_expr = expr.left
                reduction_type = "XOR with 0 -> identity"
                savings = "Eliminate XOR"
            elif left_val == 0:
                new_expr = expr.right
                reduction_type = "XOR with 0 -> identity"
                savings = "Eliminate XOR"
            # X XOR X -> 0
            elif (isinstance(expr.left, VariableNode) and
                  isinstance(expr.right, VariableNode) and
                  expr.left.name.upper() == expr.right.name.upper() and
                  expr.left.subscripts is None and expr.right.subscripts is None):
                new_expr = NumberNode(value=0.0, literal="0")
                reduction_type = "XOR with self -> 0"
                savings = "Eliminate XOR, replace with 0"

        # If we found a reduction, record it
        if reduction_type and self.current_line is not None:
            reduced_desc = self._describe_expression(new_expr) if new_expr else original_desc
            self.strength_reductions.append(StrengthReduction(
                line=self.current_line,
                original_expr=original_desc,
                reduced_expr=reduced_desc,
                reduction_type=reduction_type,
                savings=savings or ""
            ))

        return new_expr

    def _apply_expression_reassociation(self, expr) -> Optional[Any]:
        """
        Apply expression reassociation to rearrange associative operations
        and expose constant folding opportunities.

        Reassociates chains of associative operations (+ and *) to group constants together.

        Examples:
        - (A + 1) + 2 → A + 3
        - (A * 2) * 3 → A * 6
        - 2 + (A + 3) → A + 5
        - (A * B) * 2 * 3 → (A * B) * 6

        Returns the transformed expression node, or None if no reassociation applies.
        """
        if not isinstance(expr, BinaryOpNode):
            return None

        # Note: TokenType is already imported from src.tokens at the top

        # Only handle associative operations
        if expr.operator not in (TokenType.PLUS, TokenType.MULTIPLY):
            return None

        # Collect all terms/factors in the chain
        terms = []
        self._collect_associative_chain(expr, expr.operator, terms)

        # Need at least 2 terms to reassociate
        if len(terms) < 2:
            return None

        # Separate constants from non-constants
        constants = []
        non_constants = []

        for term in terms:
            val = self.evaluator.evaluate(term)
            if val is not None:
                # Only reassociate numeric constants, not strings
                if isinstance(val, (int, float)):
                    constants.append((term, val))
                else:
                    non_constants.append(term)
            else:
                non_constants.append(term)

        # Need at least 2 constants to benefit from reassociation
        if len(constants) < 2:
            return None

        # Fold all constants together
        if expr.operator == TokenType.PLUS:
            folded_value = sum(val for _, val in constants)
            operation = "addition chain"
        else:  # MULTIPLY
            folded_value = 1.0
            for _, val in constants:
                folded_value *= val
            operation = "multiplication chain"

        # Create the folded constant node
        if isinstance(folded_value, float) and folded_value.is_integer():
            folded_node = NumberNode(value=folded_value, literal=str(int(folded_value)))
        else:
            folded_node = NumberNode(value=folded_value, literal=str(folded_value))

        # Build the new expression: non_constants op folded_constant
        if len(non_constants) == 0:
            # All constants - just return the folded value
            new_expr = folded_node
        elif len(non_constants) == 1:
            # One non-constant and the folded constant
            # For addition: A + 5 or 5 + A (prefer A + 5)
            # For multiplication: A * 6 or 6 * A (prefer A * 6)
            new_expr = BinaryOpNode(
                left=non_constants[0],
                operator=expr.operator,
                right=folded_node
            )
        else:
            # Multiple non-constants: build left-associative chain
            # (A * B) * C * ... * folded_constant
            new_expr = non_constants[0]
            for term in non_constants[1:]:
                new_expr = BinaryOpNode(
                    left=new_expr,
                    operator=expr.operator,
                    right=term
                )
            # Add the folded constant at the end
            new_expr = BinaryOpNode(
                left=new_expr,
                operator=expr.operator,
                right=folded_node
            )

        # Record the reassociation
        original_desc = self._describe_expression(expr)
        reassociated_desc = self._describe_expression(new_expr)

        # Only record if the expression actually changed
        if original_desc != reassociated_desc:
            self.expression_reassociations.append(ExpressionReassociation(
                line=self.current_line,
                original_expr=original_desc,
                reassociated_expr=reassociated_desc,
                operation=operation,
                savings=f"Fold {len(constants)} constants into 1"
            ))
            return new_expr

        return None

    def _collect_associative_chain(self, expr, operator: TokenType, terms: List):
        """
        Recursively collect all terms/factors in an associative chain.

        For example, given (A + B) + (C + 1):
        - Collects [A, B, C, 1] for operator PLUS

        Args:
            expr: Current expression node
            operator: The associative operator (PLUS or MULTIPLY)
            terms: List to accumulate terms into
        """
        if isinstance(expr, BinaryOpNode) and expr.operator == operator:
            # Recursively collect from left and right
            self._collect_associative_chain(expr.left, operator, terms)
            self._collect_associative_chain(expr.right, operator, terms)
        else:
            # Base case: not the same operator, add as a term
            terms.append(expr)

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

    def _analyze_reachability(self, program: ProgramNode):
        """
        Analyze code reachability and detect dead code.

        Algorithm:
        1. Mark all GOTO/GOSUB/IF-THEN line number targets
        2. Start from first line, mark as reachable
        3. Follow control flow (sequential, GOTO, GOSUB, IF, loops)
        4. Stop at END, STOP, RETURN (without active GOSUB context)
        5. Any line not marked reachable is dead code
        """
        if not program.lines:
            return

        # Collect all GOTO/GOSUB targets
        for line in program.lines:
            for stmt in line.statements:
                self._collect_goto_targets(stmt)

        # Mark the first line as reachable (program entry point)
        if program.lines[0].line_number is not None:
            self.reachability.reachable_lines.add(program.lines[0].line_number)

        # Build a map of line numbers to their index in the program
        line_map = {}
        for idx, line in enumerate(program.lines):
            if line.line_number is not None:
                line_map[line.line_number] = idx

        # Perform reachability analysis using worklist algorithm
        worklist = [program.lines[0].line_number] if program.lines[0].line_number else []

        while worklist:
            current_line_num = worklist.pop(0)

            if current_line_num not in line_map:
                continue

            line_idx = line_map[current_line_num]
            line = program.lines[line_idx]

            # Analyze control flow from this line's statements
            continues_to_next = True  # Whether control flows to next line

            for stmt in line.statements:
                # Check if this statement terminates control flow
                if isinstance(stmt, (EndStatementNode, StopStatementNode, ReturnStatementNode)):
                    self.reachability.terminating_lines.add(current_line_num)
                    continues_to_next = False
                    break

                # GOTO transfers control
                elif isinstance(stmt, GotoStatementNode):
                    if stmt.line_number not in self.reachability.reachable_lines:
                        self.reachability.reachable_lines.add(stmt.line_number)
                        worklist.append(stmt.line_number)
                    continues_to_next = False  # GOTO doesn't fall through
                    break

                # GOSUB transfers control but returns
                elif isinstance(stmt, GosubStatementNode):
                    if stmt.line_number not in self.reachability.reachable_lines:
                        self.reachability.reachable_lines.add(stmt.line_number)
                        worklist.append(stmt.line_number)
                    # GOSUB continues to next line after RETURN

                # IF-THEN with line number
                elif isinstance(stmt, IfStatementNode):
                    if stmt.then_line_number is not None:
                        # Conditional GOTO
                        if stmt.then_line_number not in self.reachability.reachable_lines:
                            self.reachability.reachable_lines.add(stmt.then_line_number)
                            worklist.append(stmt.then_line_number)
                        # Falls through if condition is false
                    if stmt.else_line_number is not None:
                        if stmt.else_line_number not in self.reachability.reachable_lines:
                            self.reachability.reachable_lines.add(stmt.else_line_number)
                            worklist.append(stmt.else_line_number)

                # ON...GOTO
                elif isinstance(stmt, OnGotoStatementNode):
                    for target in stmt.line_numbers:
                        if target not in self.reachability.reachable_lines:
                            self.reachability.reachable_lines.add(target)
                            worklist.append(target)
                    # Falls through if value is out of range

            # If control continues to next line
            if continues_to_next and line_idx + 1 < len(program.lines):
                next_line = program.lines[line_idx + 1]
                if next_line.line_number is not None:
                    if next_line.line_number not in self.reachability.reachable_lines:
                        self.reachability.reachable_lines.add(next_line.line_number)
                        worklist.append(next_line.line_number)

        # Determine unreachable lines
        for line in program.lines:
            if line.line_number is not None:
                if line.line_number not in self.reachability.reachable_lines:
                    # Skip lines that are just REM or empty
                    has_real_code = False
                    for stmt in line.statements:
                        if not isinstance(stmt, (RemarkStatementNode, type(None))):
                            has_real_code = True
                            break

                    if has_real_code:
                        self.reachability.unreachable_lines.add(line.line_number)
                        self.warnings.append(
                            f"Line {line.line_number}: Unreachable code (dead code)"
                        )

    def _collect_goto_targets(self, stmt):
        """Collect all GOTO/GOSUB target line numbers"""
        if isinstance(stmt, (GotoStatementNode, GosubStatementNode)):
            self.reachability.goto_targets.add(stmt.line_number)
        elif isinstance(stmt, OnGotoStatementNode):
            for target in stmt.line_numbers:
                self.reachability.goto_targets.add(target)
        elif isinstance(stmt, IfStatementNode):
            if stmt.then_line_number is not None:
                self.reachability.goto_targets.add(stmt.then_line_number)
            if stmt.else_line_number is not None:
                self.reachability.goto_targets.add(stmt.else_line_number)

    def _analyze_forward_substitution(self, program: ProgramNode):
        """
        Analyze forward substitution opportunities.

        Identifies variables that are:
        1. Assigned a non-trivial expression
        2. Used exactly once after assignment
        3. Not modified between assignment and use
        4. Safe to substitute (no side effects)
        """
        # Count variable usages in expressions (not assignments)
        usage_counts: Dict[str, int] = {}
        usage_lines: Dict[str, List[int]] = {}

        for line in program.lines:
            if line.line_number is None:
                continue

            for stmt in line.statements:
                # Count uses in expressions (but not the LHS of assignments)
                if isinstance(stmt, LetStatementNode):
                    # Count uses in the RHS expression
                    self._count_variable_uses_in_expr(stmt.expression, usage_counts, usage_lines, line.line_number)
                elif isinstance(stmt, IfStatementNode):
                    self._count_variable_uses_in_expr(stmt.condition, usage_counts, usage_lines, line.line_number)
                elif isinstance(stmt, PrintStatementNode):
                    for expr in stmt.expressions:
                        self._count_variable_uses_in_expr(expr, usage_counts, usage_lines, line.line_number)
                elif isinstance(stmt, ForStatementNode):
                    self._count_variable_uses_in_expr(stmt.start_expr, usage_counts, usage_lines, line.line_number)
                    self._count_variable_uses_in_expr(stmt.end_expr, usage_counts, usage_lines, line.line_number)
                    if stmt.step_expr:
                        self._count_variable_uses_in_expr(stmt.step_expr, usage_counts, usage_lines, line.line_number)
                # Add more statement types as needed

        # Analyze each assignment for substitution opportunities
        for var_name, (assign_line, expr_node, expr_desc) in self.variable_assignments.items():
            use_count = usage_counts.get(var_name, 0)

            # Create substitution record
            subst = ForwardSubstitution(
                line=assign_line,
                variable=var_name,
                expression=expr_desc,
                expression_node=expr_node,
                use_count=use_count
            )

            # Determine if substitution is viable
            if use_count == 0:
                subst.can_substitute = False
                subst.reason = "Variable never used (dead store)"
            elif use_count == 1:
                # Single use - candidate for substitution
                use_line = usage_lines[var_name][0]
                subst.use_line = use_line

                # Check if expression is complex enough to warrant tracking
                # Skip trivial assignments like X = 5 or X = Y
                if isinstance(expr_node, (NumberNode, StringNode)):
                    subst.can_substitute = False
                    subst.reason = "Expression is a simple constant (already optimized)"
                elif isinstance(expr_node, VariableNode) and expr_node.subscripts is None:
                    subst.can_substitute = False
                    subst.reason = "Expression is a simple variable (use copy propagation)"
                elif use_line <= assign_line:
                    subst.can_substitute = False
                    subst.reason = "Variable used before assignment"
                else:
                    # Check for potential issues
                    if self._has_side_effects(expr_node):
                        subst.can_substitute = False
                        subst.reason = "Expression has side effects (function calls)"
                    else:
                        subst.can_substitute = True
                        subst.reason = f"Single use at line {use_line}, safe to substitute"
            else:
                # Multiple uses
                subst.can_substitute = False
                subst.reason = f"Variable used {use_count} times (would duplicate computation)"

            self.forward_substitutions.append(subst)

    def _count_variable_uses_in_expr(self, expr, usage_counts: Dict[str, int],
                                     usage_lines: Dict[str, List[int]], line_num: int):
        """Recursively count variable uses in an expression"""
        if expr is None:
            return

        if isinstance(expr, VariableNode):
            var_name = expr.name.upper()
            # Only count simple variable reads, not array accesses
            if expr.subscripts is None:
                if var_name not in usage_counts:
                    usage_counts[var_name] = 0
                    usage_lines[var_name] = []
                usage_counts[var_name] += 1
                usage_lines[var_name].append(line_num)
            else:
                # Count uses in array subscripts
                for sub in expr.subscripts:
                    self._count_variable_uses_in_expr(sub, usage_counts, usage_lines, line_num)
        elif isinstance(expr, BinaryOpNode):
            self._count_variable_uses_in_expr(expr.left, usage_counts, usage_lines, line_num)
            self._count_variable_uses_in_expr(expr.right, usage_counts, usage_lines, line_num)
        elif isinstance(expr, UnaryOpNode):
            self._count_variable_uses_in_expr(expr.operand, usage_counts, usage_lines, line_num)
        elif isinstance(expr, FunctionCallNode):
            if expr.arguments:
                for arg in expr.arguments:
                    self._count_variable_uses_in_expr(arg, usage_counts, usage_lines, line_num)

    def _has_side_effects(self, expr) -> bool:
        """Check if an expression has side effects (function calls, etc.)"""
        if isinstance(expr, FunctionCallNode):
            return True  # Function calls may have side effects
        elif isinstance(expr, BinaryOpNode):
            return self._has_side_effects(expr.left) or self._has_side_effects(expr.right)
        elif isinstance(expr, UnaryOpNode):
            return self._has_side_effects(expr.operand)
        return False

    def _analyze_live_variables(self, program: ProgramNode):
        """
        Perform live variable analysis (backward dataflow analysis).

        A variable is "live" at a point if its current value will be used later.
        This analysis identifies:
        1. Which variables are live at each program point
        2. Dead writes (variables written but never read before being overwritten or program end)
        """
        # Build a mapping of line numbers to their statements
        line_map: Dict[int, List[Any]] = {}
        all_lines = []

        for line in program.lines:
            if line.line_number is not None:
                line_map[line.line_number] = line.statements
                all_lines.append(line.line_number)

        if not all_lines:
            return

        # Sort lines (for backward iteration)
        all_lines.sort()

        # Live variables at each program point (after each line)
        live_after: Dict[int, Set[str]] = {}

        # Initialize: no variables live after the last line
        for line_num in all_lines:
            live_after[line_num] = set()

        # Iterate backwards until fixpoint (variables don't change)
        changed = True
        max_iterations = 100  # Prevent infinite loops
        iteration = 0

        while changed and iteration < max_iterations:
            changed = False
            iteration += 1

            # Process lines in reverse order
            for i in range(len(all_lines) - 1, -1, -1):
                line_num = all_lines[i]
                statements = line_map[line_num]

                # Start with live variables after this line
                live = live_after[line_num].copy()

                # Process statements in reverse order
                for stmt in reversed(statements):
                    # Update live set based on statement
                    self._update_live_set_for_statement(stmt, live, line_num, all_lines)

                # live now contains the live variables BEFORE this line
                # Propagate to predecessors
                for pred_line in self._get_predecessors(line_num, all_lines, line_map):
                    old_live = live_after[pred_line].copy()
                    live_after[pred_line] = live_after[pred_line].union(live)
                    if live_after[pred_line] != old_live:
                        changed = True

        # Store results and detect dead writes
        for line_num in all_lines:
            self.live_var_info[line_num] = LiveVariableInfo(
                line=line_num,
                live_vars=live_after[line_num].copy()
            )

        # Detect dead writes: assignments where the variable is not live afterwards
        for line_num in all_lines:
            statements = line_map[line_num]
            live_after_line = live_after[line_num]

            for stmt in statements:
                self._check_statement_for_dead_writes(stmt, line_num, live_after_line)

    def _check_statement_for_dead_writes(self, stmt, line_num: int, live_after_line: Set[str]):
        """Recursively check a statement for dead writes"""
        if isinstance(stmt, LetStatementNode):
            var_name = stmt.variable.name.upper()

            # Skip array assignments (harder to analyze)
            if stmt.variable.subscripts is not None:
                return

            # Check if this variable is live after the assignment
            if var_name not in live_after_line:
                # This is a dead write!
                self.dead_writes.append(DeadWrite(
                    line=line_num,
                    variable=var_name,
                    reason="Variable written but never read afterwards"
                ))
                # Add to the live var info for this line
                if line_num in self.live_var_info:
                    self.live_var_info[line_num].dead_writes.add(var_name)

        elif isinstance(stmt, IfStatementNode):
            # Check inline statements in THEN and ELSE branches
            if stmt.then_statements:
                for then_stmt in stmt.then_statements:
                    self._check_statement_for_dead_writes(then_stmt, line_num, live_after_line)
            if stmt.else_statements:
                for else_stmt in stmt.else_statements:
                    self._check_statement_for_dead_writes(else_stmt, line_num, live_after_line)

    def _update_live_set_for_statement(self, stmt, live: Set[str], current_line: int, all_lines: List[int]):
        """Update the live variable set when processing a statement backwards"""

        if isinstance(stmt, LetStatementNode):
            # Assignment: var = expr
            var_name = stmt.variable.name.upper()

            # Skip arrays (harder to track)
            if stmt.variable.subscripts is None:
                # Variable is defined here, so it's not live before this point
                # (unless it's used in the RHS)
                live.discard(var_name)

            # Variables used in the RHS expression are live before this statement
            self._add_expr_vars_to_live(stmt.expression, live)

            # Variables used in array subscripts are live
            if stmt.variable.subscripts:
                for subscript in stmt.variable.subscripts:
                    self._add_expr_vars_to_live(subscript, live)

        elif isinstance(stmt, IfStatementNode):
            # Variables in condition are live
            self._add_expr_vars_to_live(stmt.condition, live)

            # Process inline statements in THEN and ELSE branches
            if stmt.then_statements:
                for then_stmt in stmt.then_statements:
                    self._update_live_set_for_statement(then_stmt, live, current_line, all_lines)
            if stmt.else_statements:
                for else_stmt in stmt.else_statements:
                    self._update_live_set_for_statement(else_stmt, live, current_line, all_lines)

        elif isinstance(stmt, ForStatementNode):
            # Loop variable is defined by FOR
            var_name = stmt.variable.name.upper()
            # (Note: it's also used, so we don't remove it from live set)

            # Variables in start, end, step expressions are live
            self._add_expr_vars_to_live(stmt.start_expr, live)
            self._add_expr_vars_to_live(stmt.end_expr, live)
            if stmt.step_expr:
                self._add_expr_vars_to_live(stmt.step_expr, live)

        elif isinstance(stmt, PrintStatementNode):
            # Variables in print expressions are live
            for expr in stmt.expressions:
                if expr is not None:
                    self._add_expr_vars_to_live(expr, live)

        elif isinstance(stmt, InputStatementNode):
            # INPUT defines variables, so they're not live before this
            for var in stmt.variables:
                if isinstance(var, VariableNode) and var.subscripts is None:
                    live.discard(var.name.upper())

        elif isinstance(stmt, ReadStatementNode):
            # READ defines variables
            for var in stmt.variables:
                if isinstance(var, VariableNode) and var.subscripts is None:
                    live.discard(var.name.upper())

        # Add more statement types as needed

    def _add_expr_vars_to_live(self, expr, live: Set[str]):
        """Add all variables used in an expression to the live set"""
        if expr is None:
            return

        if isinstance(expr, VariableNode):
            # Simple variable or array reference
            live.add(expr.name.upper())
            # Also process subscripts
            if expr.subscripts:
                for subscript in expr.subscripts:
                    self._add_expr_vars_to_live(subscript, live)

        elif isinstance(expr, BinaryOpNode):
            self._add_expr_vars_to_live(expr.left, live)
            self._add_expr_vars_to_live(expr.right, live)

        elif isinstance(expr, UnaryOpNode):
            self._add_expr_vars_to_live(expr.operand, live)

        elif isinstance(expr, FunctionCallNode):
            # Variables in function arguments are live
            for arg in expr.arguments:
                self._add_expr_vars_to_live(arg, live)

        # Numbers, strings, etc. don't add variables

    def _get_predecessors(self, line_num: int, all_lines: List[int],
                          line_map: Dict[int, List[Any]]) -> List[int]:
        """Get all lines that can transfer control to this line"""
        predecessors = []

        # Sequential predecessor (line just before this one)
        idx = all_lines.index(line_num)
        if idx > 0:
            prev_line = all_lines[idx - 1]
            # Check if previous line can fall through
            statements = line_map[prev_line]
            if statements:
                last_stmt = statements[-1]
                # If last statement is not an unconditional jump, can fall through
                if not isinstance(last_stmt, (GotoStatementNode, EndStatementNode, StopStatementNode)):
                    predecessors.append(prev_line)

        # Find all GOTO/GOSUB/IF-GOTO that target this line
        for other_line in all_lines:
            statements = line_map[other_line]
            for stmt in statements:
                if isinstance(stmt, GotoStatementNode):
                    if stmt.line_number == line_num:
                        predecessors.append(other_line)
                elif isinstance(stmt, IfStatementNode):
                    if stmt.then_line_number == line_num or stmt.else_line_number == line_num:
                        predecessors.append(other_line)
                # For/Next also creates control flow, but we approximate here

        return predecessors

    def _analyze_string_constants(self, program: ProgramNode):
        """
        Analyze string constants for pooling opportunities.

        Detects duplicate string constants and suggests storing each unique
        string once for reuse throughout the program.
        """
        # Track all string constants and their locations
        string_occurrences: Dict[str, List[int]] = {}

        for line in program.lines:
            if line.line_number is None:
                continue

            for stmt in line.statements:
                self._collect_string_constants_from_statement(stmt, line.line_number, string_occurrences)

        # Build string pool for strings that appear more than once
        for string_value, lines in string_occurrences.items():
            if len(lines) > 1:  # Only pool strings that appear multiple times
                self.string_pool_counter += 1
                pool_id = f"STR{self.string_pool_counter}$"

                self.string_pool[string_value] = StringConstantPool(
                    value=string_value,
                    pool_id=pool_id,
                    occurrences=lines
                )

    def _collect_string_constants_from_statement(self, stmt, line_num: int,
                                                  string_occurrences: Dict[str, List[int]]):
        """Recursively collect string constants from a statement"""
        if isinstance(stmt, LetStatementNode):
            self._collect_strings_from_expr(stmt.expression, line_num, string_occurrences)

        elif isinstance(stmt, IfStatementNode):
            self._collect_strings_from_expr(stmt.condition, line_num, string_occurrences)
            # Process inline statements
            if stmt.then_statements:
                for then_stmt in stmt.then_statements:
                    self._collect_string_constants_from_statement(then_stmt, line_num, string_occurrences)
            if stmt.else_statements:
                for else_stmt in stmt.else_statements:
                    self._collect_string_constants_from_statement(else_stmt, line_num, string_occurrences)

        elif isinstance(stmt, PrintStatementNode):
            for expr in stmt.expressions:
                if expr is not None:
                    self._collect_strings_from_expr(expr, line_num, string_occurrences)

        elif isinstance(stmt, ForStatementNode):
            self._collect_strings_from_expr(stmt.start_expr, line_num, string_occurrences)
            self._collect_strings_from_expr(stmt.end_expr, line_num, string_occurrences)
            if stmt.step_expr:
                self._collect_strings_from_expr(stmt.step_expr, line_num, string_occurrences)

        elif isinstance(stmt, DataStatementNode):
            # DATA statements contain expression nodes
            for value_expr in stmt.values:
                self._collect_strings_from_expr(value_expr, line_num, string_occurrences)

    def _collect_strings_from_expr(self, expr, line_num: int, string_occurrences: Dict[str, List[int]]):
        """Recursively collect string constants from an expression"""
        if expr is None:
            return

        if isinstance(expr, StringNode):
            string_value = expr.value
            if string_value not in string_occurrences:
                string_occurrences[string_value] = []
            string_occurrences[string_value].append(line_num)

        elif isinstance(expr, BinaryOpNode):
            self._collect_strings_from_expr(expr.left, line_num, string_occurrences)
            self._collect_strings_from_expr(expr.right, line_num, string_occurrences)

        elif isinstance(expr, UnaryOpNode):
            self._collect_strings_from_expr(expr.operand, line_num, string_occurrences)

        elif isinstance(expr, FunctionCallNode):
            for arg in expr.arguments:
                self._collect_strings_from_expr(arg, line_num, string_occurrences)

        elif isinstance(expr, VariableNode):
            # Check subscripts
            if expr.subscripts:
                for subscript in expr.subscripts:
                    self._collect_strings_from_expr(subscript, line_num, string_occurrences)

    def _is_pure_builtin_function(self, func_name: str) -> Tuple[bool, str]:
        """
        Determine if a built-in function is pure (no side effects, deterministic).

        Returns: (is_pure, reason)
        """
        # Normalize function name to uppercase
        func_name = func_name.upper()

        # IMPURE functions (have side effects or non-deterministic)
        impure_functions = {
            'RND': 'Random number generator - non-deterministic, maintains state',
            'INKEY': 'Reads keyboard input - I/O operation, non-deterministic',
            'INPUT': 'Reads user input - I/O operation, non-deterministic',
            'EOF': 'Checks file status - I/O operation, stateful',
            'LOC': 'Returns file position - I/O operation, stateful',
            'LOF': 'Returns file length - I/O operation, stateful',
            'INP': 'Reads from I/O port - I/O operation, side effects',
            'PEEK': 'Reads memory - can have side effects (memory-mapped I/O)',
            'USR': 'Calls machine language - unknown side effects',
            'POS': 'Returns cursor position - stateful (depends on previous output)',
        }

        if func_name in impure_functions:
            return False, impure_functions[func_name]

        # PURE functions (deterministic, no side effects)
        pure_functions = {
            # Math functions
            'ABS': 'Absolute value - pure mathematical function',
            'SIN': 'Sine - pure mathematical function',
            'COS': 'Cosine - pure mathematical function',
            'TAN': 'Tangent - pure mathematical function',
            'ATN': 'Arctangent - pure mathematical function',
            'EXP': 'Exponential - pure mathematical function',
            'LOG': 'Natural logarithm - pure mathematical function',
            'SQR': 'Square root - pure mathematical function',
            'INT': 'Integer truncation - pure mathematical function',
            'FIX': 'Fix (truncate towards zero) - pure mathematical function',
            'SGN': 'Sign function - pure mathematical function',
            'CINT': 'Convert to integer - pure mathematical function',
            'CSNG': 'Convert to single - pure type conversion',
            'CDBL': 'Convert to double - pure type conversion',

            # String functions
            'ASC': 'ASCII value of character - pure function',
            'VAL': 'String to number conversion - pure function',
            'LEN': 'String length - pure function',
            'LEFT': 'Left substring - pure function',
            'RIGHT': 'Right substring - pure function',
            'MID': 'Middle substring - pure function',
            'CHR': 'Character from ASCII - pure function',
            'STR': 'Number to string - pure function',
            'SPACE': 'Generate spaces - pure function',
            'STRING': 'Replicate character - pure function',
            'INSTR': 'Find substring - pure function',
            'HEX': 'Hexadecimal conversion - pure function',
            'OCT': 'Octal conversion - pure function',

            # Binary conversion functions
            'CVI': 'Convert bytes to integer - pure function',
            'CVS': 'Convert bytes to single - pure function',
            'CVD': 'Convert bytes to double - pure function',
            'MKI': 'Convert integer to bytes - pure function',
            'MKS': 'Convert single to bytes - pure function',
            'MKD': 'Convert double to bytes - pure function',
        }

        if func_name in pure_functions:
            return True, pure_functions[func_name]

        # Unknown function - assume impure to be safe
        return False, 'Unknown function - assumed impure for safety'

    def _analyze_function_purity(self, program: ProgramNode):
        """Analyze all built-in function calls and track purity information"""
        self.builtin_function_calls.clear()
        self.impure_function_calls.clear()

        # Walk through all lines and collect function calls
        for line in program.lines:
            for stmt in line.statements:
                self._collect_function_calls_from_statement(stmt, line.line_number)

    def _collect_function_calls_from_statement(self, stmt, line_num: int):
        """Recursively collect function calls from a statement"""
        if stmt is None:
            return

        # Note: All node types are already imported from src.ast_nodes at the top

        if isinstance(stmt, LetStatementNode):
            self._collect_function_calls_from_expr(stmt.expression, line_num)

        elif isinstance(stmt, IfStatementNode):
            self._collect_function_calls_from_expr(stmt.condition, line_num)
            # Process inline statements
            if stmt.then_statements:
                for then_stmt in stmt.then_statements:
                    self._collect_function_calls_from_statement(then_stmt, line_num)
            if stmt.else_statements:
                for else_stmt in stmt.else_statements:
                    self._collect_function_calls_from_statement(else_stmt, line_num)

        elif isinstance(stmt, PrintStatementNode):
            for expr in stmt.expressions:
                if expr is not None:
                    self._collect_function_calls_from_expr(expr, line_num)

        elif isinstance(stmt, ForStatementNode):
            self._collect_function_calls_from_expr(stmt.start_expr, line_num)
            self._collect_function_calls_from_expr(stmt.end_expr, line_num)
            if stmt.step_expr:
                self._collect_function_calls_from_expr(stmt.step_expr, line_num)

        elif isinstance(stmt, InputStatementNode):
            if stmt.prompt:
                self._collect_function_calls_from_expr(stmt.prompt, line_num)

        elif isinstance(stmt, DataStatementNode):
            for value_expr in stmt.values:
                self._collect_function_calls_from_expr(value_expr, line_num)

    def _collect_function_calls_from_expr(self, expr, line_num: int):
        """Recursively collect function calls from an expression"""
        if expr is None:
            return

        # Note: All node types are already imported from src.ast_nodes at the top

        if isinstance(expr, FunctionCallNode):
            func_name = expr.name.upper()

            # Track this function call
            if func_name not in self.builtin_function_calls:
                self.builtin_function_calls[func_name] = []
            self.builtin_function_calls[func_name].append(line_num)

            # Check purity
            is_pure, reason = self._is_pure_builtin_function(func_name)
            if not is_pure:
                self.impure_function_calls.append((line_num, func_name, reason))

            # Recursively check arguments
            for arg in expr.arguments:
                self._collect_function_calls_from_expr(arg, line_num)

        elif isinstance(expr, BinaryOpNode):
            self._collect_function_calls_from_expr(expr.left, line_num)
            self._collect_function_calls_from_expr(expr.right, line_num)

        elif isinstance(expr, UnaryOpNode):
            self._collect_function_calls_from_expr(expr.operand, line_num)

        elif isinstance(expr, VariableNode):
            # Check subscripts
            if expr.subscripts:
                for subscript in expr.subscripts:
                    self._collect_function_calls_from_expr(subscript, line_num)

    def _analyze_array_bounds(self, program: ProgramNode):
        """
        Analyze array accesses and detect out-of-bounds accesses with constant indices.
        """
        self.array_bounds_violations.clear()

        # Walk through all lines and check array accesses
        for line in program.lines:
            for stmt in line.statements:
                self._check_array_bounds_in_statement(stmt, line.line_number)

    def _check_array_bounds_in_statement(self, stmt, line_num: int):
        """Recursively check array bounds in a statement"""
        if stmt is None:
            return

        # Note: All node types are already imported from src.ast_nodes at the top

        if isinstance(stmt, LetStatementNode):
            # Check LHS (if it's an array write)
            if isinstance(stmt.variable, VariableNode) and stmt.variable.subscripts:
                self._check_array_access(stmt.variable, line_num, "write")
            # Check RHS
            self._check_array_bounds_in_expr(stmt.expression, line_num)

        elif isinstance(stmt, IfStatementNode):
            self._check_array_bounds_in_expr(stmt.condition, line_num)
            # Process inline statements
            if stmt.then_statements:
                for then_stmt in stmt.then_statements:
                    self._check_array_bounds_in_statement(then_stmt, line_num)
            if stmt.else_statements:
                for else_stmt in stmt.else_statements:
                    self._check_array_bounds_in_statement(else_stmt, line_num)

        elif isinstance(stmt, PrintStatementNode):
            for expr in stmt.expressions:
                if expr is not None:
                    self._check_array_bounds_in_expr(expr, line_num)

        elif isinstance(stmt, ForStatementNode):
            self._check_array_bounds_in_expr(stmt.start_expr, line_num)
            self._check_array_bounds_in_expr(stmt.end_expr, line_num)
            if stmt.step_expr:
                self._check_array_bounds_in_expr(stmt.step_expr, line_num)

        elif isinstance(stmt, InputStatementNode):
            # Check array variables being assigned by INPUT
            for var in stmt.variables:
                if isinstance(var, VariableNode) and var.subscripts:
                    self._check_array_access(var, line_num, "write")

        elif isinstance(stmt, ReadStatementNode):
            # Check array variables being assigned by READ
            for var in stmt.variables:
                if isinstance(var, VariableNode) and var.subscripts:
                    self._check_array_access(var, line_num, "write")

        elif isinstance(stmt, DataStatementNode):
            for value_expr in stmt.values:
                self._check_array_bounds_in_expr(value_expr, line_num)

    def _check_array_bounds_in_expr(self, expr, line_num: int):
        """Recursively check array bounds in an expression"""
        if expr is None:
            return

        # Note: All node types are already imported from src.ast_nodes at the top

        if isinstance(expr, VariableNode):
            if expr.subscripts:
                self._check_array_access(expr, line_num, "read")
                # Also check subscript expressions themselves
                for subscript in expr.subscripts:
                    self._check_array_bounds_in_expr(subscript, line_num)

        elif isinstance(expr, FunctionCallNode):
            for arg in expr.arguments:
                self._check_array_bounds_in_expr(arg, line_num)

        elif isinstance(expr, BinaryOpNode):
            self._check_array_bounds_in_expr(expr.left, line_num)
            self._check_array_bounds_in_expr(expr.right, line_num)

        elif isinstance(expr, UnaryOpNode):
            self._check_array_bounds_in_expr(expr.operand, line_num)

    def _check_array_access(self, var_node, line_num: int, access_type: str):
        """Check if an array access with constant indices is within bounds"""
        # Note: All node types are already imported from src.ast_nodes at the top

        if not isinstance(var_node, VariableNode) or not var_node.subscripts:
            return

        array_name = var_node.name.upper()

        # Check if this is a declared array
        if array_name not in self.symbols.variables:
            return

        var_info = self.symbols.variables[array_name]
        if not var_info.dimensions:
            return  # Not an array

        # Check each subscript
        for dim_idx, subscript_expr in enumerate(var_node.subscripts):
            # Try to evaluate the subscript as a constant
            subscript_value = self.evaluator.evaluate(subscript_expr)

            if subscript_value is not None:
                # We have a constant subscript - check bounds
                if dim_idx < len(var_info.dimensions):
                    upper_bound = var_info.dimensions[dim_idx]
                    lower_bound = self.array_base

                    # Check if out of bounds
                    if subscript_value < lower_bound or subscript_value > upper_bound:
                        violation = ArrayBoundsViolation(
                            line=line_num,
                            array_name=array_name,
                            dimension_index=dim_idx,
                            subscript_value=subscript_value,
                            lower_bound=lower_bound,
                            upper_bound=upper_bound,
                            access_type=access_type
                        )
                        self.array_bounds_violations.append(violation)

    def _analyze_aliases(self, program: ProgramNode):
        """
        Analyze potential aliasing between variables and array elements.

        In BASIC, aliasing is limited since there are no pointers, but we can detect:
        1. Array elements that might refer to the same memory (A(I) and A(J))
        2. Overlapping array accesses that prevent optimization
        3. DEF FN parameter shadowing
        """
        self.alias_info.clear()
        self.array_element_accesses.clear()

        # Collect all array element accesses
        for line in program.lines:
            for stmt in line.statements:
                self._collect_array_accesses_from_statement(stmt, line.line_number)

        # Analyze potential aliasing in array accesses
        for array_name, accesses in self.array_element_accesses.items():
            if len(accesses) < 2:
                continue  # Need at least 2 accesses to have aliasing

            # Check for potential overlapping accesses
            for i in range(len(accesses)):
                for j in range(i + 1, len(accesses)):
                    line1, pattern1 = accesses[i]
                    line2, pattern2 = accesses[j]

                    # Determine if they might alias
                    alias_type, reason = self._check_array_alias(array_name, pattern1, pattern2)

                    if alias_type != "none":
                        impact = self._get_alias_impact(alias_type)
                        alias = AliasInfo(
                            var1=f"{array_name}{pattern1}",
                            var2=f"{array_name}{pattern2}",
                            alias_type=alias_type,
                            reason=reason,
                            impact=impact
                        )
                        self.alias_info.append(alias)

    def _collect_array_accesses_from_statement(self, stmt, line_num: int):
        """Collect array access patterns from a statement"""
        if stmt is None:
            return

        # Note: All node types are already imported from src.ast_nodes at the top

        if isinstance(stmt, LetStatementNode):
            # Check LHS
            if isinstance(stmt.variable, VariableNode) and stmt.variable.subscripts:
                self._record_array_access(stmt.variable, line_num)
            # Check RHS
            self._collect_array_accesses_from_expr(stmt.expression, line_num)

        elif isinstance(stmt, IfStatementNode):
            self._collect_array_accesses_from_expr(stmt.condition, line_num)
            if stmt.then_statements:
                for then_stmt in stmt.then_statements:
                    self._collect_array_accesses_from_statement(then_stmt, line_num)
            if stmt.else_statements:
                for else_stmt in stmt.else_statements:
                    self._collect_array_accesses_from_statement(else_stmt, line_num)

        elif isinstance(stmt, PrintStatementNode):
            for expr in stmt.expressions:
                if expr is not None:
                    self._collect_array_accesses_from_expr(expr, line_num)

        elif isinstance(stmt, ForStatementNode):
            self._collect_array_accesses_from_expr(stmt.start_expr, line_num)
            self._collect_array_accesses_from_expr(stmt.end_expr, line_num)
            if stmt.step_expr:
                self._collect_array_accesses_from_expr(stmt.step_expr, line_num)

    def _collect_array_accesses_from_expr(self, expr, line_num: int):
        """Collect array accesses from an expression"""
        if expr is None:
            return

        # Note: All node types are already imported from src.ast_nodes at the top

        if isinstance(expr, VariableNode):
            if expr.subscripts:
                self._record_array_access(expr, line_num)
                # Also check subscript expressions
                for subscript in expr.subscripts:
                    self._collect_array_accesses_from_expr(subscript, line_num)

        elif isinstance(expr, FunctionCallNode):
            for arg in expr.arguments:
                self._collect_array_accesses_from_expr(arg, line_num)

        elif isinstance(expr, BinaryOpNode):
            self._collect_array_accesses_from_expr(expr.left, line_num)
            self._collect_array_accesses_from_expr(expr.right, line_num)

        elif isinstance(expr, UnaryOpNode):
            self._collect_array_accesses_from_expr(expr.operand, line_num)

    def _record_array_access(self, var_node, line_num: int):
        """Record an array access pattern"""
        # Note: All node types are already imported from src.ast_nodes at the top

        if not isinstance(var_node, VariableNode) or not var_node.subscripts:
            return

        array_name = var_node.name.upper()

        # Build access pattern string
        subscript_strs = []
        for subscript in var_node.subscripts:
            # Try to get a meaningful pattern
            val = self.evaluator.evaluate(subscript)
            if val is not None:
                subscript_strs.append(str(int(val)))
            elif isinstance(subscript, VariableNode):
                subscript_strs.append(subscript.name.upper())
            else:
                subscript_strs.append("?")

        pattern = f"({', '.join(subscript_strs)})"

        if array_name not in self.array_element_accesses:
            self.array_element_accesses[array_name] = []
        self.array_element_accesses[array_name].append((line_num, pattern))

    def _check_array_alias(self, array_name: str, pattern1: str, pattern2: str) -> Tuple[str, str]:
        """
        Check if two array access patterns might alias.
        Returns: (alias_type, reason)
        """
        # Same pattern = definite alias
        if pattern1 == pattern2:
            return ("definite", f"Same subscript pattern: {pattern1}")

        # Extract subscripts from patterns
        sub1 = pattern1.strip("()").split(", ")
        sub2 = pattern2.strip("()").split(", ")

        if len(sub1) != len(sub2):
            return ("none", "Different number of dimensions")

        # Check each dimension
        for i, (s1, s2) in enumerate(zip(sub1, sub2)):
            # Both are constants
            if s1.lstrip('-').isdigit() and s2.lstrip('-').isdigit():
                if s1 != s2:
                    return ("none", f"Different constant indices in dimension {i+1}: {s1} vs {s2}")
            # At least one is variable
            elif not s1.lstrip('-').isdigit() or not s2.lstrip('-').isdigit():
                # Variable indices - might alias
                if s1 == s2:
                    # Same variable
                    return ("definite", f"Same variable in subscript: {s1}")
                else:
                    # Different variables - might still alias
                    return ("possible", f"Different variables in dimension {i+1}: {s1} vs {s2} (could have same value)")

        # All constant dimensions matched
        return ("definite", "All subscripts are identical")

    def _get_alias_impact(self, alias_type: str) -> str:
        """Determine the impact of aliasing on optimizations"""
        if alias_type == "definite":
            return "Cannot CSE across writes to this location; must reload values"
        elif alias_type == "possible":
            return "Conservative: must assume aliasing; limits CSE and loop optimizations"
        else:
            return "No impact"

    def _analyze_available_expressions(self, program: ProgramNode):
        """
        Perform available expression analysis.

        An expression is "available" at a point if:
        1. It has been computed on ALL paths leading to that point
        2. None of its operands have been modified since computation

        This is more sophisticated than simple CSE because it considers
        control flow - an expression must be computed on every path, not just seen once.
        """
        self.available_expr_analysis.clear()
        self.expr_computations.clear()

        # Build control flow graph representation
        line_to_index = {}
        for idx, line in enumerate(program.lines):
            line_to_index[line.line_number] = idx

        # First pass: collect all expression computations
        for line in program.lines:
            for stmt in line.statements:
                self._collect_expr_computations_from_statement(stmt, line.line_number)

        # Second pass: for each expression computed multiple times,
        # analyze if it's available at subsequent computation points
        for expr_hash, computation_lines in self.expr_computations.items():
            if len(computation_lines) < 2:
                continue  # Need at least 2 computations for optimization

            # Get expression description and variables
            # We'll reconstruct this from the first computation
            first_line = computation_lines[0]
            expr_desc = None
            expr_vars = set()

            # Find the expression node at first_line to get description
            for line in program.lines:
                if line.line_number == first_line:
                    expr_desc, expr_vars = self._find_expr_info_in_line(line, expr_hash)
                    break

            if not expr_desc:
                continue

            # Analyze availability at each subsequent computation
            available_at = []
            killed_at = []
            redundant_count = 0

            for i in range(1, len(computation_lines)):
                current_line = computation_lines[i]
                previous_line = computation_lines[i-1]

                # Check if expression is available at current_line
                # (computed at previous_line and variables not modified in between)
                is_available = self._is_expr_available_between_lines(
                    program, previous_line, current_line, expr_vars, line_to_index
                )

                if is_available:
                    available_at.append(current_line)
                    redundant_count += 1
                else:
                    killed_at.append(current_line)

            # Create available expression record
            if len(available_at) > 0:
                avail_expr = AvailableExpression(
                    expression_hash=expr_hash,
                    expression_desc=expr_desc,
                    first_computed_line=computation_lines[0],
                    available_at_lines=available_at,
                    variables_used=expr_vars,
                    killed_at_lines=killed_at,
                    redundant_computations=redundant_count
                )
                self.available_expr_analysis.append(avail_expr)

    def _collect_expr_computations_from_statement(self, stmt, line_num: int):
        """Collect all expression computations from a statement"""
        if stmt is None:
            return

        # Note: All statement node types are already imported from src.ast_nodes at the top

        if isinstance(stmt, LetStatementNode):
            self._collect_expr_computations_from_expr(stmt.expression, line_num)

        elif isinstance(stmt, IfStatementNode):
            self._collect_expr_computations_from_expr(stmt.condition, line_num)
            if stmt.then_statements:
                for then_stmt in stmt.then_statements:
                    self._collect_expr_computations_from_statement(then_stmt, line_num)
            if stmt.else_statements:
                for else_stmt in stmt.else_statements:
                    self._collect_expr_computations_from_statement(else_stmt, line_num)

        elif isinstance(stmt, PrintStatementNode):
            for expr in stmt.expressions:
                if expr is not None:
                    self._collect_expr_computations_from_expr(expr, line_num)

        elif isinstance(stmt, ForStatementNode):
            self._collect_expr_computations_from_expr(stmt.start_expr, line_num)
            self._collect_expr_computations_from_expr(stmt.end_expr, line_num)
            if stmt.step_expr:
                self._collect_expr_computations_from_expr(stmt.step_expr, line_num)

        elif isinstance(stmt, WhileStatementNode):
            self._collect_expr_computations_from_expr(stmt.condition, line_num)

    def _collect_expr_computations_from_expr(self, expr, line_num: int):
        """Collect computations from an expression recursively"""
        if expr is None:
            return

        # Note: All expression node types are already imported from src.ast_nodes at the top

        # Only track non-trivial expressions (binary ops, function calls)
        if isinstance(expr, BinaryOpNode):
            expr_hash = self._hash_expression(expr)
            if expr_hash not in self.expr_computations:
                self.expr_computations[expr_hash] = []
            self.expr_computations[expr_hash].append(line_num)

            # Recurse into subexpressions
            self._collect_expr_computations_from_expr(expr.left, line_num)
            self._collect_expr_computations_from_expr(expr.right, line_num)

        elif isinstance(expr, UnaryOpNode):
            # Skip trivial unary operations like simple negation
            self._collect_expr_computations_from_expr(expr.operand, line_num)

        elif isinstance(expr, FunctionCallNode):
            expr_hash = self._hash_expression(expr)
            if expr_hash not in self.expr_computations:
                self.expr_computations[expr_hash] = []
            self.expr_computations[expr_hash].append(line_num)

            # Recurse into arguments
            for arg in expr.arguments:
                self._collect_expr_computations_from_expr(arg, line_num)

        elif isinstance(expr, VariableNode):
            # Check array subscripts
            if expr.subscripts:
                for subscript in expr.subscripts:
                    self._collect_expr_computations_from_expr(subscript, line_num)

    def _find_expr_info_in_line(self, line, expr_hash: str) -> Tuple[Optional[str], Set[str]]:
        """Find expression description and variables for a given hash in a line"""
        for stmt in line.statements:
            result = self._find_expr_info_in_statement(stmt, expr_hash)
            if result[0] is not None:
                return result
        return (None, set())

    def _find_expr_info_in_statement(self, stmt, expr_hash: str) -> Tuple[Optional[str], Set[str]]:
        """Recursively search for expression in statement"""
        if stmt is None:
            return (None, set())

        # Note: All node types are already imported from src.ast_nodes at the top

        if isinstance(stmt, LetStatementNode):
            return self._find_expr_info_in_expr(stmt.expression, expr_hash)

        elif isinstance(stmt, IfStatementNode):
            result = self._find_expr_info_in_expr(stmt.condition, expr_hash)
            if result[0]:
                return result
            if stmt.then_statements:
                for then_stmt in stmt.then_statements:
                    result = self._find_expr_info_in_statement(then_stmt, expr_hash)
                    if result[0]:
                        return result
            if stmt.else_statements:
                for else_stmt in stmt.else_statements:
                    result = self._find_expr_info_in_statement(else_stmt, expr_hash)
                    if result[0]:
                        return result

        elif isinstance(stmt, PrintStatementNode):
            for expr in stmt.expressions:
                if expr is not None:
                    result = self._find_expr_info_in_expr(expr, expr_hash)
                    if result[0]:
                        return result

        elif isinstance(stmt, ForStatementNode):
            for expr in [stmt.start_expr, stmt.end_expr, stmt.step_expr]:
                if expr is not None:
                    result = self._find_expr_info_in_expr(expr, expr_hash)
                    if result[0]:
                        return result

        elif isinstance(stmt, WhileStatementNode):
            return self._find_expr_info_in_expr(stmt.condition, expr_hash)

        return (None, set())

    def _find_expr_info_in_expr(self, expr, expr_hash: str) -> Tuple[Optional[str], Set[str]]:
        """Check if this expression matches the hash"""
        if expr is None:
            return (None, set())

        test_hash = self._hash_expression(expr)
        if test_hash == expr_hash:
            desc = self._describe_expression(expr)
            vars_used = self._get_expression_variables(expr)
            return (desc, vars_used)

        # Recurse into subexpressions
        # Note: All node types are already imported from src.ast_nodes at the top

        if isinstance(expr, BinaryOpNode):
            result = self._find_expr_info_in_expr(expr.left, expr_hash)
            if result[0]:
                return result
            return self._find_expr_info_in_expr(expr.right, expr_hash)

        elif isinstance(expr, UnaryOpNode):
            return self._find_expr_info_in_expr(expr.operand, expr_hash)

        elif isinstance(expr, FunctionCallNode):
            for arg in expr.arguments:
                result = self._find_expr_info_in_expr(arg, expr_hash)
                if result[0]:
                    return result

        elif isinstance(expr, VariableNode):
            if expr.subscripts:
                for subscript in expr.subscripts:
                    result = self._find_expr_info_in_expr(subscript, expr_hash)
                    if result[0]:
                        return result

        return (None, set())

    def _is_expr_available_between_lines(self, program: ProgramNode,
                                          start_line: int, end_line: int,
                                          expr_vars: Set[str],
                                          line_to_index: Dict[int, int]) -> bool:
        """
        Check if an expression is available between two lines.
        Returns True if none of the expression's variables are modified between start and end.
        """
        if start_line not in line_to_index or end_line not in line_to_index:
            return False

        start_idx = line_to_index[start_line]
        end_idx = line_to_index[end_line]

        # Check all lines between start and end (exclusive)
        for idx in range(start_idx + 1, end_idx):
            line = program.lines[idx]
            # Check if any variable in expr_vars is modified in this line
            modified_vars = self._get_modified_variables_in_line(line)
            if any(var in expr_vars for var in modified_vars):
                return False  # Expression is killed

        return True  # Expression remains available

    def _get_modified_variables_in_line(self, line) -> Set[str]:
        """Get all variables modified in a line"""
        modified = set()

        # Note: All node types are already imported from src.ast_nodes at the top

        for stmt in line.statements:
            if isinstance(stmt, LetStatementNode):
                if isinstance(stmt.variable, VariableNode):
                    modified.add(stmt.variable.name.upper())

            elif isinstance(stmt, ForStatementNode):
                # stmt.variable is a VariableNode
                from parser import VariableNode as VarNode
                if isinstance(stmt.variable, VarNode):
                    modified.add(stmt.variable.name.upper())
                elif isinstance(stmt.variable, str):
                    modified.add(stmt.variable.upper())

            elif isinstance(stmt, InputStatementNode):
                for var in stmt.variables:
                    if isinstance(var, VariableNode):
                        modified.add(var.name.upper())

            elif isinstance(stmt, ReadStatementNode):
                for var in stmt.variables:
                    if isinstance(var, VariableNode):
                        modified.add(var.name.upper())

        return modified

    def _analyze_string_concat_in_loops(self, program: ProgramNode):
        """
        Detect string concatenation inside loops.

        String concatenation in loops is inefficient in BASIC because:
        1. Each concatenation creates a new temporary string
        2. In a loop with N iterations, this creates N-1 temporary allocations
        3. Better to use an array or pre-allocate
        """
        self.string_concat_in_loops.clear()

        # Analyze each loop
        for loop_start_line, loop_info in self.loops.items():
            # Find all string concatenations in this loop
            string_concats = self._find_string_concats_in_loop(program, loop_info)

            for string_var, concat_lines in string_concats.items():
                if len(concat_lines) == 0:
                    continue

                # Estimate allocations
                estimated_allocations = len(concat_lines)
                if loop_info.iteration_count:
                    estimated_allocations = len(concat_lines) * loop_info.iteration_count

                # Determine impact
                impact = self._get_string_concat_impact(loop_info, estimated_allocations)

                concat_info = StringConcatInLoop(
                    loop_start_line=loop_start_line,
                    loop_type=loop_info.loop_type.value,
                    string_var=string_var,
                    concat_lines=concat_lines,
                    iteration_count=loop_info.iteration_count,
                    estimated_allocations=estimated_allocations,
                    impact=impact
                )
                self.string_concat_in_loops.append(concat_info)

    def _find_string_concats_in_loop(self, program: ProgramNode, loop_info) -> Dict[str, List[int]]:
        """Find all string concatenation operations in a loop"""
        string_concats = {}  # var_name -> [line1, line2, ...]

        # Get all lines in the loop
        loop_lines = []
        in_loop = False
        for line in program.lines:
            if line.line_number == loop_info.start_line:
                in_loop = True
            if in_loop:
                loop_lines.append(line)
            if loop_info.end_line and line.line_number == loop_info.end_line:
                break

        # Check each line for string concatenation
        for line in loop_lines:
            for stmt in line.statements:
                self._check_stmt_for_string_concat(stmt, line.line_number, string_concats)

        return string_concats

    def _check_stmt_for_string_concat(self, stmt, line_num: int, string_concats: Dict[str, List[int]]):
        """Check if a statement contains string concatenation to itself"""
        if stmt is None:
            return

        # Note: All node types are already imported from src.ast_nodes at the top

        if isinstance(stmt, LetStatementNode):
            # Check if this is a string variable
            if isinstance(stmt.variable, VariableNode):
                # Get full variable name with type suffix
                var_name = stmt.variable.name.upper()
                if stmt.variable.type_suffix:
                    var_name += stmt.variable.type_suffix

                # Only track string variables (ending with $)
                if not var_name.endswith('$'):
                    return

                # Check if RHS contains concatenation with same variable
                # Pattern: A$ = A$ + something or A$ = something + A$
                if self._is_self_concat(stmt.expression, var_name):
                    if var_name not in string_concats:
                        string_concats[var_name] = []
                    string_concats[var_name].append(line_num)

    def _is_self_concat(self, expr, var_name: str) -> bool:
        """Check if expression is a concatenation with the variable itself"""
        if expr is None:
            return False

        # Note: All node types are already imported from src.ast_nodes at the top
        # Note: TokenType is already imported from src.tokens at the top

        if isinstance(expr, BinaryOpNode):
            # Check for PLUS operator (string concatenation in BASIC)
            if expr.operator == TokenType.PLUS:
                # Check if either side references the variable
                left_has_var = self._expr_contains_variable(expr.left, var_name)
                right_has_var = self._expr_contains_variable(expr.right, var_name)
                return left_has_var or right_has_var

        return False

    def _expr_contains_variable(self, expr, var_name: str) -> bool:
        """Check if expression contains a reference to the given variable"""
        if expr is None:
            return False

        # Note: All node types are already imported from src.ast_nodes at the top

        if isinstance(expr, VariableNode):
            # Get full variable name with type suffix
            full_name = expr.name.upper()
            if expr.type_suffix:
                full_name += expr.type_suffix
            return full_name == var_name

        elif isinstance(expr, BinaryOpNode):
            return (self._expr_contains_variable(expr.left, var_name) or
                    self._expr_contains_variable(expr.right, var_name))

        elif isinstance(expr, UnaryOpNode):
            return self._expr_contains_variable(expr.operand, var_name)

        elif isinstance(expr, FunctionCallNode):
            return any(self._expr_contains_variable(arg, var_name) for arg in expr.arguments)

        return False

    def _analyze_variable_type_bindings(self, program: ProgramNode):
        """
        Analyze variable type bindings to detect type re-binding opportunities.
        Phase 1: FOR loops and sequential independent assignments.
        """
        self.type_bindings.clear()
        self.variable_type_versions.clear()
        self.can_rebind_variable.clear()

        # Process each line in order
        for line in program.lines:
            for stmt in line.statements:
                self._analyze_stmt_for_type_binding(stmt, line.line_number)

        # Now analyze which variables can be re-bound
        for var_name, bindings in self.variable_type_versions.items():
            if len(bindings) <= 1:
                # Only one binding, no re-binding needed
                self.can_rebind_variable[var_name] = False
                continue

            # Check if all bindings have different types
            types = [b.type_name for b in bindings]
            if len(set(types)) == 1:
                # All same type, no re-binding needed
                self.can_rebind_variable[var_name] = False
                continue

            # Check if all bindings can be re-bound
            all_can_rebind = all(b.can_rebind for b in bindings)
            self.can_rebind_variable[var_name] = all_can_rebind

    def _analyze_stmt_for_type_binding(self, stmt, line_num: int):
        """Analyze a statement to detect type bindings"""
        if stmt is None:
            return

        # Note: All node types are already imported from src.ast_nodes at the top

        # LET statement
        if isinstance(stmt, LetStatementNode):
            if isinstance(stmt.variable, VariableNode):
                var_name = stmt.variable.name.upper()
                if stmt.variable.type_suffix:
                    var_name += stmt.variable.type_suffix

                # Skip string variables for now
                if var_name.endswith('$'):
                    return

                # Infer type from expression
                type_name = self._infer_expression_type(stmt.expression)
                depends_on_previous = self._expr_contains_variable(stmt.expression, var_name)

                binding = TypeBinding(
                    variable=var_name,
                    line=line_num,
                    type_name=type_name,
                    reason=f"Assignment from {type_name} expression",
                    depends_on_previous=depends_on_previous,
                    can_rebind=not depends_on_previous  # Can rebind if no dependency
                )

                self.type_bindings.append(binding)
                if var_name not in self.variable_type_versions:
                    self.variable_type_versions[var_name] = []
                self.variable_type_versions[var_name].append(binding)

        # FOR statement
        elif isinstance(stmt, ForStatementNode):
            if isinstance(stmt.variable, VariableNode):
                var_name = stmt.variable.name.upper()
                if stmt.variable.type_suffix:
                    var_name += stmt.variable.type_suffix

                # Check if loop bounds are INTEGER
                start_int = self._is_integer_valued_expression(stmt.start_expr)
                end_int = self._is_integer_valued_expression(stmt.end_expr)
                step_int = True
                if stmt.step_expr:
                    step_int = self._is_integer_valued_expression(stmt.step_expr)

                if start_int and end_int and step_int:
                    type_name = "INTEGER"
                    reason = "FOR loop with INTEGER bounds"
                else:
                    type_name = "DOUBLE"
                    reason = "FOR loop with DOUBLE bounds"

                # FOR loop always overwrites, so can rebind
                binding = TypeBinding(
                    variable=var_name,
                    line=line_num,
                    type_name=type_name,
                    reason=reason,
                    depends_on_previous=False,  # FOR overwrites completely
                    can_rebind=True  # Can always rebind for FOR loops
                )

                self.type_bindings.append(binding)
                if var_name not in self.variable_type_versions:
                    self.variable_type_versions[var_name] = []
                self.variable_type_versions[var_name].append(binding)

        # INPUT/READ (ambiguous types - would need explicit type)
        elif isinstance(stmt, (InputStatementNode, ReadStatementNode)):
            # For now, skip INPUT/READ as they're ambiguous
            pass

    def _infer_expression_type(self, expr) -> str:
        """Infer the type of an expression"""
        if self._is_integer_valued_expression(expr):
            return "INTEGER"
        # For now, default to DOUBLE for anything not provably INTEGER
        return "DOUBLE"

    def _is_integer_valued_expression(self, expr) -> bool:
        """
        Check if an expression produces an INTEGER value.
        Used for type rebinding analysis.
        """
        if expr is None:
            return False

        # Note: All node types are already imported from src.ast_nodes at the top
        # Note: TokenType is already imported from src.tokens at the top

        # Integer literal
        if isinstance(expr, NumberNode):
            # Check if it's an integer (no decimal point, no exponent)
            if isinstance(expr.value, int):
                return True
            # Check if the literal field (original source) is an integer
            if hasattr(expr, 'literal'):
                # If literal is an int, it's an integer (e.g., 10)
                if isinstance(expr.literal, int):
                    return True
                # If literal is a float, it had a decimal point (e.g., 10.0)
                if isinstance(expr.literal, float):
                    return False  # Even if it's a whole number, it had a decimal point
                # Check if literal is a string without decimal point
                if isinstance(expr.literal, str) and '.' not in expr.literal and 'e' not in expr.literal.lower():
                    return True
            # Fallback: if value is a whole number but we don't have literal info
            # This shouldn't happen but be conservative
            return False

        # Variable reference - check if variable has INTEGER type
        if isinstance(expr, VariableNode):
            var_name = expr.name.upper()
            if expr.type_suffix:
                var_name += expr.type_suffix
                # Explicit INTEGER suffix
                if expr.type_suffix == '%':
                    return True

            # Check if we've already inferred this variable's type
            if var_name in self.variable_type_versions:
                bindings = self.variable_type_versions[var_name]
                if bindings and bindings[-1].type_name == "INTEGER":
                    return True

            # If we have an explicit DOUBLE or STRING suffix and no INTEGER inference, it's not INTEGER
            if expr.type_suffix in ('#', '$'):
                return False

            # Default: not integer (includes '!' suffix without INTEGER inference)
            return False

        # Binary operation
        if isinstance(expr, BinaryOpNode):
            left_int = self._is_integer_valued_expression(expr.left)
            right_int = self._is_integer_valued_expression(expr.right)

            # Both operands must be INTEGER for result to be INTEGER
            if not (left_int and right_int):
                return False

            # Check operator
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
                TokenType.NOT: 'NOT',
                TokenType.EQV: 'EQV',
                TokenType.IMP: 'IMP',
                TokenType.EQUAL: '=',
                TokenType.NOT_EQUAL: '<>',
                TokenType.LESS_THAN: '<',
                TokenType.GREATER_THAN: '>',
                TokenType.LESS_EQUAL: '<=',
                TokenType.GREATER_EQUAL: '>=',
            }
            op_str = op_map.get(expr.operator, str(expr.operator))
            op = op_str.upper() if isinstance(op_str, str) else str(op_str)

            # INTEGER operations
            if op in ('+', '-', '*', '\\', 'MOD', 'AND', 'OR', 'XOR', 'NOT', 'EQV', 'IMP'):
                return True

            # Comparison operations return INTEGER (-1 or 0)
            if op in ('=', '<>', '<', '>', '<=', '>='):
                return True

            # Floating-point division always produces float
            if op == '/':
                return False

            # Exponentiation might produce float
            if op == '^':
                return False  # Conservative

            return False

        # Unary operation
        if isinstance(expr, UnaryOpNode):
            op_map = {
                TokenType.MINUS: '-',
                TokenType.PLUS: '+',
                TokenType.NOT: 'NOT',
            }
            op_str = op_map.get(expr.operator, str(expr.operator))
            op = op_str.upper() if isinstance(op_str, str) else str(op_str)

            operand_int = self._is_integer_valued_expression(expr.operand)

            # Unary minus/plus preserves type
            if op in ('-', '+'):
                return operand_int

            # NOT is always integer
            if op == 'NOT':
                return True

            return False

        # Function call - check if it returns INTEGER
        if isinstance(expr, FunctionCallNode):
            func_name = expr.name.upper()
            # Functions that return INTEGER
            integer_functions = {
                'LEN', 'ASC', 'INSTR', 'FIX', 'INT', 'CINT',
                'POS', 'EOF', 'LOC', 'LOF', 'CSRLIN', 'PEEK',
                'INP', 'SGN', 'ABS',  # ABS might return INTEGER if arg is INTEGER
            }
            if func_name in integer_functions:
                return True

            return False

        return False

    # =================================================================
    # TYPE PROMOTION ANALYSIS (Phase 2)
    # =================================================================

    def _analyze_type_promotions(self, program):
        """
        Analyze type promotions - Phase 2 of type rebinding strategy.

        Detects where INTEGER variables need promotion to DOUBLE in mixed-type expressions.
        Examples:
          X = 10        ' X is INTEGER
          Y = X + 0.5   ' X promoted to DOUBLE
        """
        for line in program.lines:
            for stmt in line.statements:
                if isinstance(stmt, LetStatementNode):
                    self._check_expression_for_promotions(stmt.expression, line.line_number, stmt.variable.name.upper())

    def _check_expression_for_promotions(self, expr, line: int, _result_var: str = ""):
        """
        Check an expression for type promotions.

        If we have INTEGER variables used in DOUBLE context, record promotions.
        """
        if expr is None:
            return

        # Binary operation - check for mixed types
        if isinstance(expr, BinaryOpNode):
            left_type = self._infer_expression_type(expr.left)
            right_type = self._infer_expression_type(expr.right)

            # Mixed-type expression: one INTEGER, one DOUBLE
            if left_type != right_type:
                # INTEGER + DOUBLE → promote INTEGER to DOUBLE
                if left_type == "INTEGER" and right_type == "DOUBLE":
                    self._record_promotion_from_expression(expr.left, line, "Mixed-type binary operation")
                elif left_type == "DOUBLE" and right_type == "INTEGER":
                    self._record_promotion_from_expression(expr.right, line, "Mixed-type binary operation")

            # Recurse into subexpressions
            self._check_expression_for_promotions(expr.left, line)
            self._check_expression_for_promotions(expr.right, line)

    def _record_promotion_from_expression(self, expr, line: int, reason: str):
        """
        Record a type promotion for a variable in an expression.
        """
        if isinstance(expr, VariableNode):
            var_name = expr.name.upper()
            if expr.type_suffix:
                var_name += expr.type_suffix

            # Only promote if we know it's currently INTEGER
            if var_name in self.variable_current_type:
                current_type = self.variable_current_type[var_name]
            else:
                # Infer from type suffix or bindings
                if expr.type_suffix == '%':
                    current_type = "INTEGER"
                elif expr.type_suffix == '!':
                    current_type = "SINGLE"
                elif expr.type_suffix == '#':
                    current_type = "DOUBLE"
                else:
                    # Check type bindings
                    if var_name in self.variable_type_versions:
                        bindings = self.variable_type_versions[var_name]
                        if bindings:
                            current_type = bindings[-1].type_name
                        else:
                            return  # No type info, skip
                    else:
                        return  # No type info, skip

            # Only record promotion if it's a widening conversion
            if current_type == "INTEGER":
                target_type = "DOUBLE"
                is_safe = True

                # Create promotion record
                promotion = TypePromotion(
                    variable=var_name,
                    line=line,
                    from_type=current_type,
                    to_type=target_type,
                    reason=reason,
                    expression=f"{var_name} (INTEGER) → DOUBLE",
                    is_safe=is_safe
                )

                self.type_promotions.append(promotion)

                # Track promotion point
                if var_name not in self.promotion_points:
                    self.promotion_points[var_name] = []
                self.promotion_points[var_name].append(line)

    def _can_promote_safely(self, from_type: str, to_type: str) -> bool:
        """
        Check if type promotion is safe (value-preserving).

        Safe promotions:
          INTEGER → DOUBLE: Always safe (all integers fit exactly in DOUBLE)
          SINGLE → DOUBLE: Always safe (DOUBLE has more precision)

        Unsafe promotions:
          DOUBLE → INTEGER: Not safe (fractional part lost, overflow possible)
          SINGLE → INTEGER: Not safe (fractional part lost)
        """
        safe_promotions = {
            ("INTEGER", "SINGLE"),
            ("INTEGER", "DOUBLE"),
            ("SINGLE", "DOUBLE"),
        }
        return (from_type, to_type) in safe_promotions

    # =================================================================
    # INTEGER SIZE INFERENCE (8/16/32-bit optimization)
    # =================================================================

    def _analyze_integer_sizes(self, program):
        """
        Analyze integer sizes for optimization (8-bit, 16-bit, 32-bit).

        Detects when variables can use smaller integer types:
        - FOR I = 1 TO 10: I can be 8-bit unsigned (0-255)
        - C = ASC(A$): C is 8-bit unsigned (0-255)
        - FOR I = -50 TO 50: I is 8-bit signed (-128 to 127)
        """
        for line in program.lines:
            for stmt in line.statements:
                # Analyze FOR loops for counter size
                if isinstance(stmt, ForStatementNode):
                    self._analyze_for_loop_integer_size(stmt, line.line_number)

                # Analyze assignments for function returns
                elif isinstance(stmt, LetStatementNode):
                    self._analyze_assignment_integer_size(stmt, line.line_number)

    def _analyze_for_loop_integer_size(self, stmt: ForStatementNode, line: int):
        """Determine optimal integer size for FOR loop counter"""
        var_name = stmt.variable.name.upper()
        if stmt.variable.type_suffix:
            var_name += stmt.variable.type_suffix

        # Try to evaluate loop bounds
        start_val = self.evaluator.evaluate(stmt.start_expr)
        end_val = self.evaluator.evaluate(stmt.end_expr)
        step_val = self.evaluator.evaluate(stmt.step_expr) if stmt.step_expr else 1

        if start_val is not None and end_val is not None and step_val is not None:
            # Determine actual range
            if step_val > 0:
                min_val = start_val
                max_val = end_val
            elif step_val < 0:
                min_val = end_val
                max_val = start_val
            else:
                # Step is 0 - infinite loop, be conservative
                min_val = min(start_val, end_val)
                max_val = max(start_val, end_val)

            # Infer size from range
            integer_size = self._infer_size_from_range(min_val, max_val)

            # Create range info
            range_info = IntegerRangeInfo(
                variable=var_name,
                integer_size=integer_size,
                min_value=min_val,
                max_value=max_val,
                is_constant=False,
                reason=f"FOR loop with constant bounds ({min_val} to {max_val})",
                line=line
            )

            self.integer_ranges.append(range_info)
            self.variable_integer_size[var_name] = range_info

    def _analyze_assignment_integer_size(self, stmt: LetStatementNode, line: int):
        """Analyze assignment for integer size (especially function returns)"""
        var_name = stmt.variable.name.upper()
        if stmt.variable.type_suffix:
            var_name += stmt.variable.type_suffix

        # Check if RHS is a function call that returns known size
        if isinstance(stmt.expression, FunctionCallNode):
            func_name = stmt.expression.name.upper()
            integer_size = self._get_function_return_size(func_name)

            if integer_size != IntegerSize.INT32:  # Only record if we know something useful
                # Get range for this size
                min_val, max_val = self._get_range_for_size(integer_size)

                range_info = IntegerRangeInfo(
                    variable=var_name,
                    integer_size=integer_size,
                    min_value=min_val,
                    max_value=max_val,
                    is_constant=False,
                    reason=f"Result of {func_name}() which returns {integer_size.name}",
                    line=line
                )

                self.integer_ranges.append(range_info)
                self.variable_integer_size[var_name] = range_info

    def _get_function_return_size(self, func_name: str) -> IntegerSize:
        """Determine integer size of function return value"""
        func_upper = func_name.upper()

        # String functions return UNSIGNED 8-bit (0-255)
        if func_upper in {'LEN', 'ASC', 'PEEK', 'INP', 'INSTR'}:
            return IntegerSize.INT8_UNSIGNED

        # Small-range functions return SIGNED 8-bit or UNSIGNED 8-bit
        if func_upper == 'POS':  # Cursor position 0-79
            return IntegerSize.INT8_UNSIGNED
        if func_upper == 'CSRLIN':  # Cursor line 0-24
            return IntegerSize.INT8_UNSIGNED
        if func_upper == 'SGN':  # Sign: -1, 0, or 1
            return IntegerSize.INT8_SIGNED
        if func_upper == 'EOF':  # 0 or -1
            return IntegerSize.INT8_SIGNED

        # 16-bit functions
        if func_upper in {'LOF', 'FRE', 'VARPTR', 'CVI'}:
            return IntegerSize.INT16_UNSIGNED

        # Unknown - be conservative
        return IntegerSize.INT32

    def _infer_size_from_range(self, min_val: int, max_val: int) -> IntegerSize:
        """Infer integer size from value range"""
        # Check if negative (needs signed)
        if min_val < 0:
            # Signed range
            if -128 <= min_val <= 127 and -128 <= max_val <= 127:
                return IntegerSize.INT8_SIGNED
            elif -32768 <= min_val <= 32767 and -32768 <= max_val <= 32767:
                return IntegerSize.INT16_SIGNED
            else:
                return IntegerSize.INT32
        else:
            # Unsigned range (0 or positive)
            if max_val <= 255:
                return IntegerSize.INT8_UNSIGNED
            elif max_val <= 65535:
                return IntegerSize.INT16_UNSIGNED
            else:
                return IntegerSize.INT32

    def _get_range_for_size(self, size: IntegerSize) -> Tuple[int, int]:
        """Get min/max range for a given integer size"""
        if size == IntegerSize.INT8_SIGNED:
            return (-128, 127)
        elif size == IntegerSize.INT8_UNSIGNED:
            return (0, 255)
        elif size == IntegerSize.INT16_SIGNED:
            return (-32768, 32767)
        elif size == IntegerSize.INT16_UNSIGNED:
            return (0, 65535)
        else:  # INT32
            return (-2147483648, 2147483647)

    def _get_string_concat_impact(self, loop_info, estimated_allocations: int) -> str:
        """Determine the performance impact of string concatenation in a loop"""
        if loop_info.iteration_count:
            if loop_info.iteration_count <= 10:
                return f"Low impact: {loop_info.iteration_count} iterations, {estimated_allocations} allocations"
            elif loop_info.iteration_count <= 100:
                return f"Medium impact: {loop_info.iteration_count} iterations, {estimated_allocations} allocations"
            else:
                return f"HIGH IMPACT: {loop_info.iteration_count} iterations, {estimated_allocations} allocations"
        else:
            return f"Unknown impact: iteration count not determined, {estimated_allocations} concatenations per iteration"

    def _check_compilation_switches(self):
        """Generate warnings for required compilation switches"""
        switches = self.flags.get_required_switches()
        if switches:
            self.warnings.append(
                f"Required compilation switches: {' '.join(switches)}"
            )

    def _clear_iterative_state(self):
        """
        Clear optimization state that can become stale between iterations.

        This includes all analyses that depend on other optimizations:
        - CSE (affected by forward substitution)
        - Reachability (affected by constant folding, boolean simplification)
        - Forward substitution (affected by dead code elimination)
        - Live variables (affected by forward substitution, dead code)
        - Type rebinding (affected by constant folding)
        - Strength reduction, etc.

        Structural data (symbols, subroutines, loops) is NOT cleared.
        """
        # CSE
        self.common_subexpressions.clear()
        self.available_expressions.clear()
        # Don't reset cse_counter - we want unique temp names across iterations

        # Reachability
        self.reachability = ReachabilityInfo()

        # Forward substitution - only clear analysis results, not structural data
        self.forward_substitutions.clear()
        # NOTE: variable_assignments is structural (populated in Phase 1) - do NOT clear
        # NOTE: variable_usage_count/lines are unused instance vars (analysis uses local vars)

        # Live variables
        self.live_var_info.clear()
        self.dead_writes.clear()

        # Type rebinding
        self.type_bindings.clear()
        self.variable_type_versions.clear()
        self.can_rebind_variable.clear()

        # Type promotion (Phase 2)
        self.type_promotions.clear()
        self.variable_current_type.clear()
        self.promotion_points.clear()

        # Integer size inference
        self.integer_ranges.clear()
        self.variable_integer_size.clear()

        # Strength reduction
        self.strength_reductions.clear()

        # Expression reassociation
        self.expression_reassociations.clear()

        # Copy propagation
        self.copy_propagations.clear()
        self.active_copies.clear()

        # Branch optimization
        self.branch_optimizations.clear()

        # Uninitialized variable warnings
        self.uninitialized_warnings.clear()
        self.initialized_variables.clear()

        # Induction variables
        self.induction_variables.clear()
        self.active_ivs.clear()

        # Range analysis - NOTE: range_info is structural (based on FOR loop bounds)
        # and is populated during _analyze_statements(), so we DON'T clear it.
        # However, active_ranges (runtime tracking) should be cleared.
        # self.range_info.clear()  # DO NOT CLEAR - structural data
        self.active_ranges.clear()

        # Available expression analysis
        self.available_expr_analysis.clear()

        # Reset constant evaluator runtime constants
        # (these are derived and may change with optimizations)
        self.evaluator.runtime_constants.clear()

        # Note: We DON'T clear:
        # - self.symbols (structural)
        # - self.subroutines (structural)
        # - self.gosub_targets (structural)
        # - self.loops (structural)
        # - self.folded_expressions (accumulates, deduplicated)
        # - Reporting-only data (recalculated once at end)

    def _count_optimizations(self) -> int:
        """
        Count total optimizations found.
        Used to detect convergence - if count doesn't change, we've reached fixed point.
        """
        return (
            len(self.common_subexpressions) +
            len(self.reachability.unreachable_lines) +
            len(self.forward_substitutions) +
            len(self.dead_writes) +
            len(self.type_bindings) +
            len(self.type_promotions) +
            len(self.integer_ranges) +
            len(self.strength_reductions) +
            len(self.expression_reassociations) +
            len(self.copy_propagations) +
            len(self.branch_optimizations) +
            len(self.uninitialized_warnings) +
            len(self.induction_variables) +
            len(self.range_info) +
            len(self.available_expr_analysis)
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

    def _get_type_from_variable_node(self, var_node) -> VarType:
        """Determine variable type from VariableNode (uses type_suffix attribute)"""
        suffix = var_node.type_suffix
        if suffix == '%':
            return VarType.INTEGER
        elif suffix == '!':
            return VarType.SINGLE
        elif suffix == '#':
            return VarType.DOUBLE
        elif suffix == '$':
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

        # Optimization iteration statistics
        if self.optimization_iterations > 0:
            lines.append(f"\nOptimization Iterations: {self.optimization_iterations}")
            if self.optimization_converged:
                lines.append(f"  ✓ Converged to fixed point (no more improvements found)")
            else:
                lines.append(f"  ⚠ Iteration limit reached - some optimizations may have been missed")

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

        # Strength Reduction Optimizations
        if self.strength_reductions:
            lines.append(f"\nStrength Reduction Optimizations:")
            lines.append(f"  Found {len(self.strength_reductions)} strength reduction(s)")
            lines.append("")
            for sr in self.strength_reductions:
                lines.append(f"  Line {sr.line}: {sr.original_expr} → {sr.reduced_expr}")
                lines.append(f"    Type: {sr.reduction_type}")
                lines.append(f"    Savings: {sr.savings}")
                lines.append("")

        # Expression Reassociation Optimizations
        if self.expression_reassociations:
            lines.append(f"\nExpression Reassociation Optimizations:")
            lines.append(f"  Found {len(self.expression_reassociations)} reassociation(s)")
            lines.append("")
            for er in self.expression_reassociations:
                lines.append(f"  Line {er.line}: {er.original_expr} → {er.reassociated_expr}")
                lines.append(f"    Operation: {er.operation}")
                lines.append(f"    Savings: {er.savings}")
                lines.append("")

        # Copy Propagation Optimizations
        if self.copy_propagations:
            lines.append(f"\nCopy Propagation Optimizations:")
            lines.append(f"  Found {len(self.copy_propagations)} copy assignment(s)")
            lines.append("")

            # Show copies with propagation opportunities
            propagatable = [cp for cp in self.copy_propagations if cp.propagation_count > 0]
            non_propagatable = [cp for cp in self.copy_propagations if cp.propagation_count == 0]

            if propagatable:
                lines.append(f"  Copies with propagation opportunities:")
                for cp in propagatable:
                    lines.append(f"    Line {cp.line}: {cp.copy_var} = {cp.source_var}")
                    lines.append(f"      Can propagate {cp.propagation_count} time(s)")
                    lines.append(f"      At lines: {', '.join(map(str, cp.propagated_lines))}")
                    lines.append(f"      Suggestion: Replace {cp.copy_var} with {cp.source_var}")
                    lines.append("")

            if non_propagatable:
                lines.append(f"  Copies with no propagation opportunities:")
                for cp in non_propagatable:
                    lines.append(f"    Line {cp.line}: {cp.copy_var} = {cp.source_var} (not used)")
                lines.append("")

        # Forward Substitution Optimizations
        if self.forward_substitutions:
            lines.append(f"\nForward Substitution Optimizations:")
            lines.append(f"  Found {len(self.forward_substitutions)} assignment(s) analyzed")
            lines.append("")

            # Separate by substitutability
            substitutable = [fs for fs in self.forward_substitutions if fs.can_substitute]
            dead_stores = [fs for fs in self.forward_substitutions if fs.use_count == 0]
            multi_use = [fs for fs in self.forward_substitutions if fs.use_count > 1 and not fs.can_substitute]

            if substitutable:
                lines.append(f"  Variables with single-use substitution opportunities:")
                for fs in substitutable:
                    lines.append(f"    Line {fs.line}: {fs.variable} = {fs.expression}")
                    lines.append(f"      Used once at line {fs.use_line}")
                    lines.append(f"      Suggestion: Substitute expression directly at use site")
                    lines.append(f"      Eliminates temporary variable")
                    lines.append("")

            if dead_stores:
                lines.append(f"  Variables that are never used (dead stores):")
                for fs in dead_stores:
                    lines.append(f"    Line {fs.line}: {fs.variable} = {fs.expression}")
                    lines.append(f"      Variable assigned but never read")
                    lines.append(f"      Suggestion: Remove assignment")
                    lines.append("")

            if multi_use:
                lines.append(f"  Variables used multiple times (substitution not beneficial):")
                for fs in multi_use[:5]:  # Limit to first 5
                    lines.append(f"    Line {fs.line}: {fs.variable} = {fs.expression}")
                    lines.append(f"      Used {fs.use_count} times")
                if len(multi_use) > 5:
                    lines.append(f"    ... and {len(multi_use) - 5} more")
                lines.append("")

        # Branch Optimization
        if self.branch_optimizations:
            lines.append(f"\nBranch Optimization:")

            constant_branches = [bo for bo in self.branch_optimizations if bo.is_constant]

            if constant_branches:
                lines.append(f"  Found {len(constant_branches)} constant condition(s)")
                lines.append("")

                always_true = [bo for bo in constant_branches if bo.always_true]
                always_false = [bo for bo in constant_branches if bo.always_false]

                if always_true:
                    lines.append(f"  Conditions that are always TRUE:")
                    for bo in always_true:
                        lines.append(f"    Line {bo.line}: IF {bo.condition}")
                        lines.append(f"      Evaluates to: {bo.constant_value} (always TRUE)")
                        if bo.unreachable_branch:
                            lines.append(f"      Unreachable branch: {bo.unreachable_branch}")
                            if bo.unreachable_branch == "ELSE" and bo.else_target:
                                lines.append(f"        Dead code: GOTO {bo.else_target}")
                        lines.append(f"      Suggestion: Remove IF, keep THEN branch")
                        lines.append("")

                if always_false:
                    lines.append(f"  Conditions that are always FALSE:")
                    for bo in always_false:
                        lines.append(f"    Line {bo.line}: IF {bo.condition}")
                        lines.append(f"      Evaluates to: {bo.constant_value} (always FALSE)")
                        if bo.unreachable_branch:
                            lines.append(f"      Unreachable branch: {bo.unreachable_branch}")
                            if bo.unreachable_branch == "THEN" and bo.then_target:
                                lines.append(f"        Dead code: GOTO {bo.then_target}")
                        if bo.else_target:
                            lines.append(f"      Suggestion: Remove IF, keep ELSE branch (GOTO {bo.else_target})")
                        else:
                            lines.append(f"      Suggestion: Remove IF statement entirely")
                        lines.append("")

        # Uninitialized Variable Warnings
        if self.uninitialized_warnings:
            lines.append(f"\nUninitialized Variable Warnings:")
            lines.append(f"  Found {len(self.uninitialized_warnings)} potential use(s) of uninitialized variable(s)")
            lines.append("")

            # Group warnings by variable
            warnings_by_var = {}
            for warning in self.uninitialized_warnings:
                var_name = warning.variable
                if var_name not in warnings_by_var:
                    warnings_by_var[var_name] = []
                warnings_by_var[var_name].append(warning)

            for var_name, warnings in sorted(warnings_by_var.items()):
                lines.append(f"  Variable: {var_name}")
                if len(warnings) == 1:
                    w = warnings[0]
                    lines.append(f"    Line {w.line}: Used before assignment in {w.context}")
                else:
                    lines.append(f"    Used before assignment at {len(warnings)} location(s):")
                    for w in warnings:
                        lines.append(f"      Line {w.line}: {w.context}")
                lines.append(f"    Note: BASIC defaults uninitialized variables to 0")
                lines.append(f"    Suggestion: Explicitly initialize before use to avoid bugs")
                lines.append("")

        # Range Analysis
        if self.range_info:
            lines.append(f"\nRange Analysis:")
            lines.append(f"  Found {len(self.range_info)} value range determination(s)")
            lines.append("")

            # Group by variable
            ranges_by_var = {}
            for range_info in self.range_info:
                var_name = range_info.variable
                if var_name not in ranges_by_var:
                    ranges_by_var[var_name] = []
                ranges_by_var[var_name].append(range_info)

            for var_name, range_list in sorted(ranges_by_var.items()):
                lines.append(f"  Variable: {var_name}")
                for r in range_list:
                    lines.append(f"    Line {r.line}: {r.range} ({r.context})")
                    if r.enabled_optimization:
                        lines.append(f"      Enabled: {r.enabled_optimization}")
                lines.append("")

        # Live Variable Analysis
        if self.dead_writes:
            lines.append(f"\nLive Variable Analysis:")
            lines.append(f"  Found {len(self.dead_writes)} dead write(s)")
            lines.append("")

            # Group by variable
            dead_by_var = {}
            for dw in self.dead_writes:
                var_name = dw.variable
                if var_name not in dead_by_var:
                    dead_by_var[var_name] = []
                dead_by_var[var_name].append(dw)

            lines.append("  Dead Writes (variables written but never read):")
            for var_name, dead_list in sorted(dead_by_var.items()):
                lines.append(f"  Variable: {var_name}")
                for dw in dead_list:
                    lines.append(f"    Line {dw.line}: {dw.reason}")
                lines.append(f"    Suggestion: Remove assignment or use the variable")
                lines.append("")

        # String Constant Pooling
        if self.string_pool:
            lines.append(f"\nString Constant Pooling:")
            lines.append(f"  Found {len(self.string_pool)} duplicate string constant(s)")
            lines.append("")

            # Sort by number of occurrences (most frequent first)
            sorted_strings = sorted(self.string_pool.values(),
                                  key=lambda s: len(s.occurrences),
                                  reverse=True)

            total_bytes_saved = 0
            for pool_entry in sorted_strings:
                num_occurrences = len(pool_entry.occurrences)
                bytes_per_copy = pool_entry.size
                # Each duplicate saves the string bytes (keeping one copy)
                bytes_saved = bytes_per_copy * (num_occurrences - 1)
                total_bytes_saved += bytes_saved

                lines.append(f"  String: \"{pool_entry.value}\"")
                lines.append(f"    Appears {num_occurrences} times at lines: {', '.join(map(str, pool_entry.occurrences))}")
                lines.append(f"    Size: {pool_entry.size} bytes")
                lines.append(f"    Suggested pool ID: {pool_entry.pool_id}")
                lines.append(f"    Savings: {bytes_saved} bytes (storing {num_occurrences} copies as 1)")
                lines.append("")

            if total_bytes_saved > 0:
                lines.append(f"  Total potential memory savings: {total_bytes_saved} bytes")
                lines.append(f"  Recommendation: Define pooled strings at program start")
                lines.append(f"    Example: 10 {sorted_strings[0].pool_id} = \"{sorted_strings[0].value}\"")
                lines.append("")

        # Common Subexpression Elimination (CSE)
        if self.common_subexpressions:
            lines.append(f"\nCommon Subexpression Elimination (CSE):")
            lines.append(f"  Found {len(self.common_subexpressions)} common subexpression(s)")
            lines.append("")

            # Sort by first occurrence line number
            sorted_cses = sorted(self.common_subexpressions.values(),
                               key=lambda cse: cse.first_line)

            for cse in sorted_cses:
                lines.append(f"  Expression: {cse.expression_desc}")
                lines.append(f"    Computed {len(cse.occurrences) + 1} times total")
                lines.append(f"    First at line {cse.first_line}")
                lines.append(f"    Recomputed at lines: {', '.join(map(str, cse.occurrences))}")
                if cse.variables_used:
                    lines.append(f"    Variables used: {', '.join(sorted(cse.variables_used))}")
                lines.append(f"    Suggested temp variable: {cse.temp_var_name}")
                lines.append("")

        # Loop Analysis and Optimizations
        if self.loops:
            lines.append(f"\nLoop Analysis:")
            lines.append(f"  Found {len(self.loops)} loop(s)")
            lines.append("")

            # Sort loops by start line
            sorted_loops = sorted(self.loops.items(), key=lambda x: x[0])

            for start_line, loop in sorted_loops:
                lines.append(f"  Loop at line {start_line} ({loop.loop_type.value}):")
                lines.append(f"    End line: {loop.end_line}")

                if loop.control_variable:
                    lines.append(f"    Control variable: {loop.control_variable}")

                if loop.iteration_count is not None:
                    lines.append(f"    Iteration count: {loop.iteration_count}")

                if loop.can_unroll:
                    lines.append(f"    ✓ Can be unrolled (factor: {loop.unroll_factor})")

                if loop.nested_in:
                    lines.append(f"    Nested in loop at line {loop.nested_in}")

                if loop.contains_loops:
                    lines.append(f"    Contains nested loops at: {', '.join(map(str, loop.contains_loops))}")

                if loop.variables_modified:
                    lines.append(f"    Modifies variables: {', '.join(sorted(loop.variables_modified))}")

                # Loop-invariant code motion opportunities
                if loop.invariants:
                    hoistable = [inv for inv in loop.invariants.values() if inv.can_hoist]
                    non_hoistable = [inv for inv in loop.invariants.values() if not inv.can_hoist]

                    if hoistable:
                        lines.append(f"    ✓ Loop-invariant expressions that can be hoisted:")
                        for inv in sorted(hoistable, key=lambda x: x.first_line):
                            lines.append(f"      • {inv.expression_desc}")
                            lines.append(f"        Computed {len(inv.occurrences) + 1} times at lines: {inv.first_line}, {', '.join(map(str, inv.occurrences))}")

                    if non_hoistable:
                        lines.append(f"    Note: Non-hoistable expressions:")
                        for inv in sorted(non_hoistable, key=lambda x: x.first_line):
                            lines.append(f"      • {inv.expression_desc} - {inv.reason_no_hoist}")

                lines.append("")

        # Induction Variable Analysis
        if self.induction_variables:
            lines.append(f"\nInduction Variable Analysis:")
            lines.append(f"  Found {len(self.induction_variables)} induction variable(s)")
            lines.append("")

            # Group by loop
            ivs_by_loop: Dict[int, List[InductionVariable]] = {}
            for iv in self.induction_variables:
                if iv.loop_start_line not in ivs_by_loop:
                    ivs_by_loop[iv.loop_start_line] = []
                ivs_by_loop[iv.loop_start_line].append(iv)

            for loop_start, ivs in sorted(ivs_by_loop.items()):
                lines.append(f"  Loop at line {loop_start}:")

                # Primary IVs
                primary_ivs = [iv for iv in ivs if iv.is_primary]
                for iv in primary_ivs:
                    lines.append(f"    Primary IV: {iv.variable}")
                    if iv.base_value is not None:
                        lines.append(f"      Start: {iv.base_value}")
                    if iv.coefficient is not None:
                        lines.append(f"      Step: {iv.coefficient}")
                    if iv.strength_reduction_opportunities > 0:
                        lines.append(f"      ✓ {iv.strength_reduction_opportunities} optimization opportunity(s)")
                        for line_num, expr_desc, optimized_desc in iv.related_expressions:
                            lines.append(f"        Line {line_num}: {expr_desc}")
                            lines.append(f"          → {optimized_desc}")

                # Derived IVs
                derived_ivs = [iv for iv in ivs if not iv.is_primary]
                if derived_ivs:
                    lines.append(f"    Derived IVs:")
                    for iv in derived_ivs:
                        relationship = f"{iv.variable} = "
                        if iv.base_value != 0:
                            relationship += f"{iv.base_value} + "
                        if iv.coefficient != 1:
                            relationship += f"{iv.coefficient} * "
                        relationship += iv.base_var
                        lines.append(f"      • {relationship}")
                        if iv.strength_reduction_opportunities > 0:
                            lines.append(f"        ✓ {iv.strength_reduction_opportunities} optimization opportunity(s)")
                            for line_num, expr_desc, optimized_desc in iv.related_expressions:
                                lines.append(f"          Line {line_num}: {expr_desc}")
                                lines.append(f"            → {optimized_desc}")

                lines.append("")

        # Subroutine Analysis
        if self.subroutines:
            lines.append(f"\nSubroutine Analysis:")
            lines.append(f"  Found {len(self.subroutines)} subroutine(s)")
            lines.append("")

            sorted_subs = sorted(self.subroutines.items(), key=lambda x: x[0])

            for line_num, sub_info in sorted_subs:
                lines.append(f"  Subroutine at line {line_num}:")
                if sub_info.end_line:
                    lines.append(f"    End line: {sub_info.end_line}")

                if sub_info.variables_modified:
                    lines.append(f"    Modifies: {', '.join(sorted(sub_info.variables_modified))}")
                else:
                    lines.append(f"    Modifies: (none - read-only)")

                if sub_info.calls_other_subs:
                    lines.append(f"    Calls subroutines at: {', '.join(map(str, sorted(sub_info.calls_other_subs)))}")

                lines.append("")

        # Compilation flags
        switches = self.flags.get_required_switches()
        if switches:
            lines.append(f"\nRequired Compilation Switches:")
            for switch in switches:
                lines.append(f"  {switch}")

        # Built-in Function Purity Analysis
        if self.builtin_function_calls or self.impure_function_calls:
            lines.append(f"\nBuilt-in Function Purity Analysis:")

            # Summary
            total_calls = sum(len(calls) for calls in self.builtin_function_calls.values())
            pure_calls = total_calls - len(self.impure_function_calls)
            lines.append(f"  Total built-in function calls: {total_calls}")
            lines.append(f"  Pure function calls: {pure_calls}")
            lines.append(f"  Impure function calls: {len(self.impure_function_calls)}")
            lines.append("")

            # List all function calls
            if self.builtin_function_calls:
                lines.append("  Functions used:")
                sorted_funcs = sorted(self.builtin_function_calls.items())
                for func_name, call_lines in sorted_funcs:
                    is_pure, reason = self._is_pure_builtin_function(func_name)
                    purity_str = "PURE" if is_pure else "IMPURE"
                    lines.append(f"    {func_name}: {purity_str} - {len(call_lines)} call(s)")
                    if not is_pure:
                        lines.append(f"      Reason: {reason}")
                        lines.append(f"      Lines: {', '.join(map(str, call_lines))}")
                lines.append("")

            # Impure function warnings
            if self.impure_function_calls:
                lines.append("  ⚠ Impure Function Calls Detected:")
                lines.append("  These functions have side effects or are non-deterministic,")
                lines.append("  which limits optimization opportunities (CSE, constant folding).")
                lines.append("")

                # Group by function name
                impure_by_func: Dict[str, List[int]] = {}
                for line_num, func_name, reason in self.impure_function_calls:
                    if func_name not in impure_by_func:
                        impure_by_func[func_name] = []
                    impure_by_func[func_name].append(line_num)

                for func_name in sorted(impure_by_func.keys()):
                    call_lines = impure_by_func[func_name]
                    is_pure, reason = self._is_pure_builtin_function(func_name)
                    lines.append(f"    {func_name}:")
                    lines.append(f"      Reason: {reason}")
                    lines.append(f"      Called at lines: {', '.join(map(str, sorted(call_lines)))}")
                    lines.append(f"      Impact: Cannot CSE or constant-fold expressions containing {func_name}()")
                    lines.append("")

            # Optimization impact
            if pure_calls > 0:
                lines.append("  ✓ Optimization Opportunities:")
                lines.append(f"    • {pure_calls} pure function call(s) can be:")
                lines.append(f"      - Common subexpression eliminated (if called with same arguments)")
                lines.append(f"      - Constant folded (if all arguments are constants)")
                lines.append(f"      - Moved out of loops (if arguments don't change in loop)")
                lines.append("")

        # Alias Analysis
        if self.alias_info:
            lines.append(f"\nAlias Analysis:")
            lines.append(f"  Found {len(self.alias_info)} potential alias(es)")
            lines.append("")

            # Group by alias type
            definite_aliases = [a for a in self.alias_info if a.alias_type == "definite"]
            possible_aliases = [a for a in self.alias_info if a.alias_type == "possible"]

            if definite_aliases:
                lines.append(f"  Definite Aliases ({len(definite_aliases)}):")
                for alias in definite_aliases:
                    lines.append(f"    {alias.var1} and {alias.var2}")
                    lines.append(f"      Reason: {alias.reason}")
                    lines.append(f"      Impact: {alias.impact}")
                    lines.append("")

            if possible_aliases:
                lines.append(f"  Possible Aliases ({len(possible_aliases)}):")
                for alias in possible_aliases:
                    lines.append(f"    {alias.var1} and {alias.var2}")
                    lines.append(f"      Reason: {alias.reason}")
                    lines.append(f"      Impact: {alias.impact}")
                    lines.append("")

            # Summary of impact
            if self.alias_info:
                lines.append("  Optimization Impact:")
                lines.append(f"    • {len(definite_aliases)} definite alias(es) require conservative handling")
                lines.append(f"    • {len(possible_aliases)} possible alias(es) require worst-case assumptions")
                lines.append("    • Aliasing prevents aggressive CSE and loop optimizations")
                lines.append("    • Use distinct variables or constant indices to avoid aliasing")
                lines.append("")

        # Array Bounds Violations
        if self.array_bounds_violations:
            lines.append(f"\nArray Bounds Analysis:")
            lines.append(f"  Found {len(self.array_bounds_violations)} bounds violation(s)")
            lines.append("")

            # Group by severity and type
            for violation in sorted(self.array_bounds_violations, key=lambda v: v.line):
                dim_suffix = "" if violation.dimension_index == 0 else f" (dimension {violation.dimension_index + 1})"
                lines.append(f"  ⚠ Line {violation.line}: {violation.array_name}{dim_suffix}")
                lines.append(f"      Access type: {violation.access_type}")
                lines.append(f"      Index value: {violation.subscript_value}")
                lines.append(f"      Valid range: [{violation.lower_bound}, {violation.upper_bound}]")

                if violation.subscript_value < violation.lower_bound:
                    lines.append(f"      Error: Index {violation.subscript_value} is below lower bound {violation.lower_bound}")
                else:
                    lines.append(f"      Error: Index {violation.subscript_value} exceeds upper bound {violation.upper_bound}")

                lines.append(f"      Impact: Will cause runtime error (Subscript out of range)")
                lines.append("")

        # Type Rebinding Analysis
        if self.type_bindings:
            lines.append(f"\nType Rebinding Analysis (Phase 1):")
            lines.append(f"  Found {len(self.variable_type_versions)} variable(s) with type bindings")
            lines.append("")

            # Find variables that can be re-bound
            rebindable_vars = [var for var, can_rebind in self.can_rebind_variable.items() if can_rebind]

            if rebindable_vars:
                lines.append(f"  Variables that can be re-bound ({len(rebindable_vars)}):")
                for var_name in sorted(rebindable_vars):
                    bindings = self.variable_type_versions[var_name]
                    types = [b.type_name for b in bindings]
                    if len(set(types)) > 1:  # Only show if types actually change
                        lines.append(f"    {var_name}:")
                        for binding in bindings:
                            depends = " (depends on previous)" if binding.depends_on_previous else ""
                            lines.append(f"      Line {binding.line}: {binding.type_name} - {binding.reason}{depends}")

                        # Show the type sequence
                        type_seq = " → ".join(types)
                        lines.append(f"      Type sequence: {type_seq}")
                        lines.append(f"      ✓ Can optimize with type re-binding")
                        lines.append("")

            # Show variables with type conflicts (cannot rebind)
            non_rebindable = [var for var, can_rebind in self.can_rebind_variable.items()
                            if not can_rebind and len(self.variable_type_versions[var]) > 1]
            if non_rebindable:
                lines.append(f"  Variables with dependencies (cannot re-bind): {len(non_rebindable)}")
                for var_name in sorted(non_rebindable)[:5]:  # Limit to first 5
                    bindings = self.variable_type_versions[var_name]
                    lines.append(f"    {var_name}: {len(bindings)} assignments, has data dependencies")
                if len(non_rebindable) > 5:
                    lines.append(f"    ... and {len(non_rebindable) - 5} more")
                lines.append("")

        # Type Promotion Analysis (Phase 2)
        if self.type_promotions:
            lines.append(f"\nType Promotion Analysis (Phase 2):")
            lines.append(f"  Found {len(self.type_promotions)} type promotion(s)")
            lines.append("")

            # Group by variable
            promotions_by_var: Dict[str, List[TypePromotion]] = {}
            for promotion in self.type_promotions:
                if promotion.variable not in promotions_by_var:
                    promotions_by_var[promotion.variable] = []
                promotions_by_var[promotion.variable].append(promotion)

            # Show promotions
            for var_name in sorted(promotions_by_var.keys()):
                var_promotions = promotions_by_var[var_name]
                lines.append(f"  {var_name}:")
                for promo in var_promotions:
                    safety = "✓ Safe" if promo.is_safe else "⚠ May lose precision"
                    lines.append(f"    Line {promo.line}: {promo.from_type} → {promo.to_type} ({safety})")
                    lines.append(f"      Reason: {promo.reason}")
                    if promo.expression:
                        lines.append(f"      Expression: {promo.expression}")
                lines.append("")

        # Integer Size Inference (8/16/32-bit optimization)
        if self.integer_ranges:
            lines.append(f"\nInteger Size Inference (8/16/32-bit optimization):")
            lines.append(f"  Found {len(self.integer_ranges)} variable(s) with optimizable integer sizes")
            lines.append("")

            # Group by size
            by_size: Dict[IntegerSize, List[IntegerRangeInfo]] = {}
            for range_info in self.integer_ranges:
                if range_info.integer_size not in by_size:
                    by_size[range_info.integer_size] = []
                by_size[range_info.integer_size].append(range_info)

            # Show 8-bit unsigned (most common and important!)
            if IntegerSize.INT8_UNSIGNED in by_size:
                ranges = by_size[IntegerSize.INT8_UNSIGNED]
                lines.append(f"  8-bit UNSIGNED (0-255): {len(ranges)} variable(s)")
                for r in sorted(ranges, key=lambda x: x.variable):
                    lines.append(f"    {r.variable}: range {r.min_value}-{r.max_value}")
                    lines.append(f"      Line {r.line}: {r.reason}")
                lines.append("")

            # Show 8-bit signed
            if IntegerSize.INT8_SIGNED in by_size:
                ranges = by_size[IntegerSize.INT8_SIGNED]
                lines.append(f"  8-bit SIGNED (-128 to 127): {len(ranges)} variable(s)")
                for r in sorted(ranges, key=lambda x: x.variable):
                    lines.append(f"    {r.variable}: range {r.min_value}-{r.max_value}")
                    lines.append(f"      Line {r.line}: {r.reason}")
                lines.append("")

            # Show 16-bit unsigned
            if IntegerSize.INT16_UNSIGNED in by_size:
                ranges = by_size[IntegerSize.INT16_UNSIGNED]
                lines.append(f"  16-bit UNSIGNED (0-65535): {len(ranges)} variable(s)")
                for r in sorted(ranges, key=lambda x: x.variable):
                    lines.append(f"    {r.variable}: range {r.min_value}-{r.max_value}")
                    lines.append(f"      Line {r.line}: {r.reason}")
                lines.append("")

            # Show 16-bit signed
            if IntegerSize.INT16_SIGNED in by_size:
                ranges = by_size[IntegerSize.INT16_SIGNED]
                lines.append(f"  16-bit SIGNED (-32768 to 32767): {len(ranges)} variable(s)")
                for r in sorted(ranges, key=lambda x: x.variable):
                    lines.append(f"    {r.variable}: range {r.min_value}-{r.max_value}")
                    lines.append(f"      Line {r.line}: {r.reason}")
                lines.append("")

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

    def compile(self, program: ProgramNode, backend_name: str = 'z88dk',
                output_file: str = 'a.out') -> bool:
        """
        Compile the analyzed program using the specified backend.

        Args:
            program: The analyzed AST to compile
            backend_name: Name of backend to use ('z88dk', etc.)
            output_file: Desired output executable name

        Returns:
            True if compilation succeeds, False on error
        """
        import subprocess
        import os
        from pathlib import Path
        from src.codegen_backend import Z88dkCBackend

        # Select backend
        if backend_name == 'z88dk':
            backend = Z88dkCBackend(self.symbols)
        else:
            self.errors.append(f"Unknown backend: {backend_name}")
            return False

        # Generate source code
        print(f"Generating code with {backend_name} backend...")
        try:
            source_code = backend.generate(program)
        except Exception as e:
            self.errors.append(f"Code generation failed: {e}")
            return False

        # Write source file
        source_ext = backend.get_file_extension()
        source_file = output_file + source_ext
        print(f"Writing {source_file}...")
        try:
            with open(source_file, 'w') as f:
                f.write(source_code)
        except IOError as e:
            self.errors.append(f"Failed to write source file: {e}")
            return False

        # Compile with backend's compiler
        compile_cmd = backend.get_compiler_command(source_file, output_file)
        print(f"Compiling: {' '.join(compile_cmd)}")
        try:
            result = subprocess.run(compile_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.errors.append(f"Compilation failed:\n{result.stderr}")
                return False
        except Exception as e:
            self.errors.append(f"Compiler invocation failed: {e}")
            return False

        # z88dk creates both OUTPUT.COM and output files, clean up and rename
        if backend_name == 'z88dk':
            # z88dk creates UPPERCASE.COM, rename to lowercase
            uppercase_com = output_file.upper() + '.COM'
            lowercase_com = output_file.lower() + '.com'
            if os.path.exists(uppercase_com):
                print(f"Renaming {uppercase_com} to {lowercase_com}...")
                os.rename(uppercase_com, lowercase_com)
                print(f"Created: {lowercase_com}")
            else:
                self.warnings.append(f"Expected output {uppercase_com} not found")

            # z88dk also creates a file without extension, remove it
            if os.path.exists(output_file):
                os.remove(output_file)

        # Report backend warnings
        if backend.warnings:
            self.warnings.extend(backend.warnings)

        print(f"Compilation successful!")
        return True


if __name__ == '__main__':
    # Simple test
    import sys

    from src.lexer import tokenize
    from src.parser import Parser

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
