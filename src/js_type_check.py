"""Static string/number typing of expressions, for the Type mismatch (error 13) checks.

In BASIC the type of an expression is known from the text alone: a name with
$ is a string, a literal in quotes is a string, a function has a fixed result
type. MBASIC 5.21 finds a string where a number is wanted (or the other way
round) when the statement runs, so the error is trappable with ON ERROR and
carries the right line. The JavaScript backend uses this module to write the
check into the code of the statement, where the mismatch is, instead of
failing in the compiler or computing a value (1+"a" gave "1a", "a"*2 gave
"aa" and -"a" crashed the compiler).

The kinds are 's' (string), 'n' (number) and '*' (either).
"""

from src.tokens import TokenType
from src.string_temps import _STRING_FUNCTIONS

#: The operators two strings may use: concatenation and the comparisons.
#: The interpreter has the same set (_STRING_BINARY_OPS).
STRING_BINARY_OPS = frozenset((
    TokenType.PLUS, TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS_THAN,
    TokenType.GREATER_THAN, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL))

#: The comparisons give a number (-1 or 0) whatever they compare.
_COMPARISONS = STRING_BINARY_OPS - {TokenType.PLUS}


def function_base_name(func) -> str:
    """The name of a built-in function, upper case, without a $."""
    return func.name.upper().rstrip('$')


def expr_kind(expr) -> str:
    """'s' when the expression is a string, else 'n'."""
    kind = type(expr).__name__
    if kind == 'StringNode':
        return 's'
    if kind == 'VariableNode':
        return 's' if expr.type_suffix == '$' else 'n'
    if kind == 'UnaryOpNode':
        # Unary + passes a string through (PRINT +"a" prints a on the binary)
        return expr_kind(expr.operand) if expr.operator == TokenType.PLUS else 'n'
    if kind == 'BinaryOpNode':
        if expr.operator == TokenType.PLUS and expr_kind(expr.left) == 's':
            return 's'
        return 'n'
    if kind == 'FunctionCallNode':
        name = function_base_name(expr)
        if name.startswith('FN'):
            return 's' if getattr(expr, 'type_suffix', None) == '$' else 'n'
        return 's' if name in _STRING_FUNCTIONS else 'n'
    return 'n'


def binary_mismatch(expr) -> bool:
    """True when the operands of a binary operator cannot be used together."""
    left, right = expr_kind(expr.left), expr_kind(expr.right)
    if left != right:
        return True
    return left == 's' and expr.operator not in STRING_BINARY_OPS


def unary_mismatch(expr) -> bool:
    """True for - or NOT given a string (unary + is allowed)."""
    return expr.operator != TokenType.PLUS and expr_kind(expr.operand) == 's'


#: Built-in functions whose arguments are all numbers (measured on 5.21).
_NUMERIC_ARGS = frozenset((
    'ABS', 'INT', 'SQR', 'SIN', 'COS', 'TAN', 'ATN', 'LOG', 'EXP', 'RND', 'SGN',
    'FIX', 'CINT', 'CSNG', 'CDBL', 'CHR', 'SPACE', 'HEX', 'OCT', 'MKI', 'MKS',
    'MKD', 'STR', 'PEEK', 'INP', 'TAB', 'SPC', 'EOF', 'LOF', 'LOC', 'INPUT'))

#: Built-in functions whose arguments are all strings.
_STRING_ARGS = frozenset(('LEN', 'ASC', 'VAL', 'CVI', 'CVS', 'CVD'))


def builtin_arg_kinds(name: str, count: int):
    """The kind wanted for each argument of a built-in function.

    Returns a list of 'n', 's' or '*'. FRE, POS and LPOS take either (their
    argument is a dummy) and USR is left to its own check, so they are all '*'.
    """
    if name in _NUMERIC_ARGS:
        return ['n'] * count
    if name in _STRING_ARGS:
        return ['s'] * count
    if name in ('LEFT', 'RIGHT'):
        return ['s', 'n', 'n'][:count]
    if name == 'MID':
        return ['s', 'n', 'n'][:count]
    if name == 'INSTR':
        # INSTR([start,] string, string)
        return ['n', 's', 's'] if count == 3 else ['s', 's'][:count]
    if name == 'STRING':
        # STRING$(count, character code or string)
        return ['n', '*'][:count]
    return ['*'] * count
