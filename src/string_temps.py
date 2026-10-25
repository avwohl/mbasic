"""String temporaries: what a string expression asks of MBASIC 5.21's ten.

MBASIC 5.21 has 10 string temporaries (numtmp in bistrs.mac). A string
literal, a string function result and the result of + each use one until the
parent operator or function has used it. A string variable or an array element
uses none. A left operand, or an earlier argument, stays in its temporary
while the next one is worked out, so a nest such as CHR$(65)+(CHR$(65)+(...))
holds one more temporary at each level. When an eleventh is needed the binary
stops with String formula too complex (error 16). Measured: ten CHR$ results in
a nest work, eleven fail; literals count the same; variables do not count.

The interpreter checks an expression before it runs it, and the JavaScript
backend does the same when it writes the expression.
"""

from src.tokens import TokenType

#: How many string temporaries MBASIC 5.21 has.
STRING_TEMPORARIES = 10

#: The built-in functions that make a string (their names in the parse tree
#: have no $, except INPUT$ and STRING$).
_STRING_FUNCTIONS = frozenset({
    'CHR', 'STR', 'LEFT', 'RIGHT', 'MID', 'STRING', 'SPACE', 'HEX', 'OCT',
    'INKEY', 'INPUT', 'MKI', 'MKS', 'MKD', 'DATE', 'TIME', 'ENVIRON',
})


def string_temps(expr):
    """What an expression asks of the ten string temporaries.

    Returns (peak, held, is_string): the most temporaries in use at one time
    while the expression is worked out, how many its result keeps (1 for a
    string made by a literal, function or +, else 0), and whether the result
    is a string.

    Worked out once per node and kept on the node, as the numbers are. The
    DEF FN body is not looked into.
    """
    cached = getattr(expr, '_mb_temps', None)
    if cached is not None:
        return cached
    kind = type(expr).__name__
    if kind == 'StringNode':
        temps = (1, 1, True)
    elif kind == 'VariableNode':
        peak = max((string_temps(sub)[0] for sub in expr.subscripts or ()), default=0)
        temps = (peak, 0, expr.type_suffix == '$')
    elif kind == 'BinaryOpNode':
        left_peak, left_held, left_string = string_temps(expr.left)
        right_peak, _, _ = string_temps(expr.right)
        peak = max(left_peak, left_held + right_peak)
        # a + with a string on the left is a concatenation
        if left_string and expr.operator == TokenType.PLUS:
            temps = (max(peak, 1), 1, True)
        else:
            temps = (peak, 0, False)
    elif kind == 'UnaryOpNode':
        peak, _, _ = string_temps(expr.operand)
        temps = (peak, 0, False)
    elif kind == 'FunctionCallNode':
        peak = held = 0
        for arg in expr.arguments:
            arg_peak, arg_held, _ = string_temps(arg)
            peak = max(peak, held + arg_peak)
            held += arg_held
        name = expr.name.rstrip('$')
        if name.lower().startswith('fn'):
            is_string = expr.type_suffix == '$'
        else:
            is_string = name.upper() in _STRING_FUNCTIONS
        temps = (max(peak, 1) if is_string else peak, 1 if is_string else 0, is_string)
    else:
        temps = (0, 0, False)
    try:
        expr._mb_temps = temps
    except AttributeError:
        pass                        # a node with __slots__: recompute
    return temps
