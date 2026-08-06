#!/usr/bin/env python3
"""Re-serialising an expression must not change what it means.

RENUM takes a program apart and puts it back together, so serialize_expression()
has to bracket a sub-expression whenever leaving the brackets off would let it
re-parse differently. The table it uses for that, _OPERATOR_PRECEDENCE in
src/ui/ui_helpers.py, has to agree with the parser's precedence climb - and it
had drifted twice:

* The key for `\\` was 'INT_DIVIDE'. The AST carries the TokenType, whose name
  is BACKSLASH, so the lookup never matched and `\\` fell to the default of 0.
  It was bracketed as a child whether it needed it or not, and never bracketed
  a child of its own, which turned (A + B) \\ C into A + B \\ C.
* `\\` and MOD were at the same level as * and / . When the parser was corrected
  to MBASIC's four levels, (12 \\ 2) * 3 would have come back out as
  12 \\ 2 * 3 - which now reads as 12 \\ (2 * 3), a different number.

Each case below is round-tripped: parse, serialize, parse again, and compare the
shape of the two trees.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.lexer import Lexer
from src.parser import Parser
from src.ui.ui_helpers import serialize_expression

results = []


def check(condition, label):
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}: {label}")


def expression_of(source):
    program = Parser(Lexer(f'10 X = {source}').tokenize()).parse()
    return program.lines[0].statements[0].expression


def shape(node):
    """The structure alone - line and column move when text is re-emitted."""
    kind = type(node).__name__
    if kind == 'BinaryOpNode':
        return (getattr(node.operator, 'name', str(node.operator)),
                shape(node.left), shape(node.right))
    if kind == 'UnaryOpNode':
        return ('unary' + getattr(node.operator, 'name', str(node.operator)),
                shape(node.operand))
    if kind == 'NumberNode':
        return ('number', node.value)
    if kind == 'VariableNode':
        return ('var', node.name)
    return (kind,)


EXPRESSIONS = [
    # \ and MOD against * and / - the precedence that was wrong.
    '(12 \\ 2) * 3', '12 \\ (2 * 3)', '12 \\ 2 * 3',
    '(12 MOD 5) * 2', '12 MOD (5 * 2)', '12 MOD 5 * 2',
    '2 * 6 \\ 4', '(2 * 6) \\ 4',
    # \ and MOD against each other, and against themselves. Both are
    # left-associative, so the right operand is the one needing brackets.
    '(A \\ B) MOD C', 'A \\ (B MOD C)', 'A MOD B \\ C', '(A MOD B) \\ C',
    '(A MOD B) MOD C', 'A MOD (B MOD C)',
    '(A \\ B) \\ C', 'A \\ (B \\ C)',
    # \ and MOD against + and - , which are looser than both.
    '(A + B) \\ C', 'A + B \\ C', '(A + B) MOD C', 'A + B MOD C',
    '1 + 12 \\ 4', '(1 + 12) \\ 4',
    # and against AND, looser again.
    'A AND B \\ C', '(A AND B) \\ C',
    # The operators that were already right, so the fix did not disturb them.
    '1 + 2 * 3', '(1 + 2) * 3',
    'A - (B - C)', '(A - B) - C',
    'A / (B / C)', '(A / B) / C',
    '2 ^ 3 ^ 2', '(2 ^ 3) ^ 2',
    'A = B AND C = D', '(A = B) OR (C = D)',
]


def test_expressions_survive_a_round_trip():
    print("Re-serialised expressions keep their meaning")
    print("-" * 60)
    for source in EXPRESSIONS:
        original = expression_of(source)
        emitted = serialize_expression(original)
        again = expression_of(emitted)
        ok = shape(again) == shape(original)
        check(ok, f"{source:22} -> {emitted}"
              + ("" if ok else "   (re-parses differently)"))


if __name__ == "__main__":
    print("Operator bracketing in serialize_expression")
    print("=" * 60)

    test_expressions_survive_a_round_trip()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
