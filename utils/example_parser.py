"""
Example demonstrating the MBASIC parser usage
"""

from lexer import tokenize
from parser import parse
from ast_nodes import *


def print_ast(node, indent=0):
    """Pretty print AST"""
    prefix = "  " * indent

    if isinstance(node, ProgramNode):
        print(f"{prefix}Program ({len(node.lines)} lines)")
        print(f"{prefix}  DEF types: {sum(1 for v in node.def_type_statements.values() if v == 'INTEGER')} INTEGER types")
        for line in node.lines:
            print_ast(line, indent + 1)

    elif isinstance(node, LineNode):
        print(f"{prefix}Line {node.line_number}:")
        for stmt in node.statements:
            print_ast(stmt, indent + 1)

    elif isinstance(node, PrintStatementNode):
        print(f"{prefix}PRINT {len(node.expressions)} expression(s)")

    elif isinstance(node, InputStatementNode):
        print(f"{prefix}INPUT {len(node.variables)} variable(s)")

    elif isinstance(node, LetStatementNode):
        print(f"{prefix}{node.variable.name} = <expression>")

    elif isinstance(node, IfStatementNode):
        if node.then_line_number:
            print(f"{prefix}IF <condition> THEN {node.then_line_number}")
        else:
            print(f"{prefix}IF <condition> THEN {len(node.then_statements)} statement(s)")

    elif isinstance(node, ForStatementNode):
        step = f" STEP {node.step_expr}" if node.step_expr else ""
        print(f"{prefix}FOR {node.variable.name} = <start> TO <end>{step}")

    elif isinstance(node, NextStatementNode):
        vars = ", ".join(v.name for v in node.variables) if node.variables else ""
        print(f"{prefix}NEXT {vars}")

    elif isinstance(node, WhileStatementNode):
        print(f"{prefix}WHILE <condition>")

    elif isinstance(node, WendStatementNode):
        print(f"{prefix}WEND")

    elif isinstance(node, GotoStatementNode):
        print(f"{prefix}GOTO {node.line_number}")

    elif isinstance(node, GosubStatementNode):
        print(f"{prefix}GOSUB {node.line_number}")

    elif isinstance(node, ReturnStatementNode):
        print(f"{prefix}RETURN")

    elif isinstance(node, OnGotoStatementNode):
        lines = ", ".join(str(ln) for ln in node.line_numbers)
        print(f"{prefix}ON <expr> GOTO {lines}")

    elif isinstance(node, OnGosubStatementNode):
        lines = ", ".join(str(ln) for ln in node.line_numbers)
        print(f"{prefix}ON <expr> GOSUB {lines}")

    elif isinstance(node, DimStatementNode):
        arrays = ", ".join(f"{a.name}({len(a.dimensions)})" for a in node.arrays)
        print(f"{prefix}DIM {arrays}")

    elif isinstance(node, DefTypeStatementNode):
        letters = ", ".join(sorted(node.letters))
        print(f"{prefix}DEF{node.var_type[:3]} {letters}")

    elif isinstance(node, ReadStatementNode):
        print(f"{prefix}READ {len(node.variables)} variable(s)")

    elif isinstance(node, DataStatementNode):
        print(f"{prefix}DATA {len(node.values)} value(s)")

    elif isinstance(node, RestoreStatementNode):
        line = f" {node.line_number}" if node.line_number else ""
        print(f"{prefix}RESTORE{line}")

    elif isinstance(node, EndStatementNode):
        print(f"{prefix}END")

    elif isinstance(node, StopStatementNode):
        print(f"{prefix}STOP")

    elif isinstance(node, RemarkStatementNode):
        text = node.text[:50] + "..." if len(node.text) > 50 else node.text
        print(f"{prefix}REM {text}")

    elif isinstance(node, SwapStatementNode):
        print(f"{prefix}SWAP {node.var1.name}, {node.var2.name}")

    elif isinstance(node, ClearStatementNode):
        print(f"{prefix}CLEAR")

    elif isinstance(node, WidthStatementNode):
        print(f"{prefix}WIDTH <expr>")

    elif isinstance(node, OnErrorStatementNode):
        print(f"{prefix}ON ERROR GOTO {node.line_number}")

    else:
        print(f"{prefix}{type(node).__name__}")


def main():
    """Example usage of the parser"""

    # Example 1: Simple program
    print("=" * 60)
    print("Example 1: Simple Program")
    print("=" * 60)

    code1 = """10 PRINT "Hello, World!"
20 END
"""

    print("Source code:")
    print(code1)

    tokens = tokenize(code1)
    ast = parse(tokens)

    print("\nAST:")
    print_ast(ast)

    # Example 2: Program with loops
    print("\n" + "=" * 60)
    print("Example 2: Program with Loops")
    print("=" * 60)

    code2 = """10 DEFINT A-Z
20 FOR I = 1 TO 10
30   PRINT I
40 NEXT I
50 END
"""

    print("Source code:")
    print(code2)

    tokens = tokenize(code2)
    ast = parse(tokens)

    print("\nAST:")
    print_ast(ast)

    # Example 3: Program with conditionals
    print("\n" + "=" * 60)
    print("Example 3: Program with Conditionals")
    print("=" * 60)

    code3 = """10 INPUT "Enter a number"; X
20 IF X > 0 THEN 40
30 PRINT "Number is not positive"
40 PRINT "Done"
50 END
"""

    print("Source code:")
    print(code3)

    tokens = tokenize(code3)
    ast = parse(tokens)

    print("\nAST:")
    print_ast(ast)

    # Example 4: Real program from corpus
    print("\n" + "=" * 60)
    print("Example 4: Real MBASIC Program (hanoi.bas)")
    print("=" * 60)

    with open('bas_out/hanoi.bas', 'r') as f:
        code4 = f.read()

    print(f"File size: {len(code4)} bytes")

    tokens = tokenize(code4)
    ast = parse(tokens)

    print(f"\nParsed {len(ast.lines)} lines")

    # Count statement types
    stmt_counts = {}
    for line in ast.lines:
        for stmt in line.statements:
            stmt_type = type(stmt).__name__
            stmt_counts[stmt_type] = stmt_counts.get(stmt_type, 0) + 1

    print("\nStatement counts:")
    for stmt_type, count in sorted(stmt_counts.items()):
        print(f"  {stmt_type:30} {count:3}")

    print("\n✓ Parser successfully handled all examples!")


if __name__ == '__main__':
    main()
