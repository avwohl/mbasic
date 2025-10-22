"""
Test suite for MBASIC parser
"""

import sys
from lexer import tokenize
from parser import parse, ParseError
from ast_nodes import *


def test_simple_program():
    """Test parsing a simple program"""
    code = """10 PRINT "Hello, World!"
20 END
"""

    print("Testing simple program:")
    print(code)

    try:
        tokens = tokenize(code)
        print(f"Lexer produced {len(tokens)} tokens")

        ast = parse(tokens)
        print(f"Parser produced AST with {len(ast.lines)} lines")

        for line in ast.lines:
            print(f"  Line {line.line_number}: {len(line.statements)} statement(s)")
            for stmt in line.statements:
                print(f"    - {type(stmt).__name__}")

        print("✓ Test passed\n")
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}\n")
        return False


def test_assignment():
    """Test parsing assignment statements"""
    code = """10 X = 5
20 Y$ = "Hello"
30 Z% = X + 10
"""

    print("Testing assignment:")
    print(code)

    try:
        tokens = tokenize(code)
        ast = parse(tokens)

        print(f"Parsed {len(ast.lines)} lines")

        for line in ast.lines:
            for stmt in line.statements:
                if isinstance(stmt, LetStatementNode):
                    print(f"  Line {line.line_number}: {stmt.variable.name} = <expression>")

        print("✓ Test passed\n")
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}\n")
        return False


def test_expressions():
    """Test parsing expressions"""
    code = """10 X = 5 + 3 * 2
20 Y = (A + B) / 2
30 Z = 2 ^ 3 ^ 2
"""

    print("Testing expressions:")
    print(code)

    try:
        tokens = tokenize(code)
        ast = parse(tokens)

        print(f"Parsed {len(ast.lines)} lines with expressions")
        print("✓ Test passed\n")
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}\n")
        return False


def test_goto_gosub():
    """Test GOTO and GOSUB"""
    code = """10 GOTO 30
20 PRINT "Skipped"
30 GOSUB 100
40 END
100 PRINT "Subroutine"
110 RETURN
"""

    print("Testing GOTO/GOSUB:")
    print(code)

    try:
        tokens = tokenize(code)
        ast = parse(tokens)

        print(f"Parsed {len(ast.lines)} lines")

        for line in ast.lines:
            for stmt in line.statements:
                if isinstance(stmt, GotoStatementNode):
                    print(f"  Line {line.line_number}: GOTO {stmt.line_number}")
                elif isinstance(stmt, GosubStatementNode):
                    print(f"  Line {line.line_number}: GOSUB {stmt.line_number}")
                elif isinstance(stmt, ReturnStatementNode):
                    print(f"  Line {line.line_number}: RETURN")

        print("✓ Test passed\n")
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}\n")
        return False


def test_defint():
    """Test DEFINT type declaration"""
    code = """10 DEFINT A-Z
20 X = 5
30 Y = 10
"""

    print("Testing DEFINT:")
    print(code)

    try:
        tokens = tokenize(code)
        ast = parse(tokens)

        print(f"DEF type map: {ast.def_type_statements}")
        print("✓ Test passed\n")
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}\n")
        return False


def test_print_variations():
    """Test various PRINT statement formats"""
    code = """10 PRINT "Hello"
20 PRINT "A"; "B"
30 PRINT X, Y, Z
40 PRINT "Value="; X;
50 ? "Question mark"
"""

    print("Testing PRINT variations:")
    print(code)

    try:
        tokens = tokenize(code)
        ast = parse(tokens)

        print(f"Parsed {len(ast.lines)} lines")

        for line in ast.lines:
            for stmt in line.statements:
                if isinstance(stmt, PrintStatementNode):
                    print(f"  Line {line.line_number}: PRINT {len(stmt.expressions)} expr(s), {len(stmt.separators)} sep(s)")

        print("✓ Test passed\n")
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}\n")
        return False


def test_input():
    """Test INPUT statement"""
    code = """10 INPUT "Enter name"; N$
20 INPUT X, Y, Z
"""

    print("Testing INPUT:")
    print(code)

    try:
        tokens = tokenize(code)
        ast = parse(tokens)

        print(f"Parsed {len(ast.lines)} lines")

        for line in ast.lines:
            for stmt in line.statements:
                if isinstance(stmt, InputStatementNode):
                    has_prompt = "with" if stmt.prompt else "without"
                    print(f"  Line {line.line_number}: INPUT {has_prompt} prompt, {len(stmt.variables)} var(s)")

        print("✓ Test passed\n")
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}\n")
        return False


def test_remark():
    """Test REM and REMARK comments"""
    code = """10 REM This is a comment
20 REMARK This is also a comment
30 PRINT "Hello"
"""

    print("Testing REM/REMARK:")
    print(code)

    try:
        tokens = tokenize(code)
        ast = parse(tokens)

        print(f"Parsed {len(ast.lines)} lines")

        for line in ast.lines:
            for stmt in line.statements:
                if isinstance(stmt, RemarkStatementNode):
                    print(f"  Line {line.line_number}: REM {stmt.text[:30]}...")

        print("✓ Test passed\n")
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}\n")
        return False


def test_operators():
    """Test operator precedence"""
    code = """10 X = 2 + 3 * 4
20 Y = (2 + 3) * 4
30 Z = 2 ^ 3 ^ 2
40 A = NOT X AND Y OR Z
"""

    print("Testing operators:")
    print(code)

    try:
        tokens = tokenize(code)
        ast = parse(tokens)

        print(f"Parsed {len(ast.lines)} lines with complex expressions")
        print("✓ Test passed\n")
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}\n")
        return False


def test_functions():
    """Test built-in function calls"""
    code = """10 X = SQR(25)
20 Y$ = CHR$(65)
30 Z = INT(3.14)
40 A$ = LEFT$("Hello", 3)
"""

    print("Testing functions:")
    print(code)

    try:
        tokens = tokenize(code)
        ast = parse(tokens)

        print(f"Parsed {len(ast.lines)} lines with function calls")

        for line in ast.lines:
            for stmt in line.statements:
                if isinstance(stmt, LetStatementNode):
                    if isinstance(stmt.expression, FunctionCallNode):
                        print(f"  Line {line.line_number}: {stmt.variable.name} = {stmt.expression.name}(...)")

        print("✓ Test passed\n")
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}\n")
        return False


def test_real_program():
    """Test with a small real program"""
    code = """10 REMARK  Simple calculator
20 DEFINT A-Z
30 PRINT "Enter two numbers"
40 INPUT X, Y
50 PRINT "Sum ="; X + Y
60 PRINT "Product ="; X * Y
70 END
"""

    print("Testing real program:")
    print(code)

    try:
        tokens = tokenize(code)
        ast = parse(tokens)

        print(f"Parsed {len(ast.lines)} lines")
        print(f"DEF type map has {len([v for v in ast.def_type_statements.values() if v == 'INTEGER'])} INTEGER types")

        print("✓ Test passed\n")
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all parser tests"""
    print("=" * 60)
    print("MBASIC Parser Test Suite")
    print("=" * 60)
    print()

    tests = [
        test_simple_program,
        test_assignment,
        test_expressions,
        test_goto_gosub,
        test_defint,
        test_print_variations,
        test_input,
        test_remark,
        test_operators,
        test_functions,
        test_real_program,
    ]

    passed = 0
    failed = 0

    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
