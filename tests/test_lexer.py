"""
Test cases for MBASIC 5.21 lexer
"""
import sys
from pathlib import Path

# Add src directory to path so we can import compiler modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from lexer import tokenize, LexerError
from tokens import TokenType


def test_numbers():
    """Test various number formats"""
    print("Testing numbers...")

    # Integer (use PRINT to avoid line number confusion)
    tokens = tokenize("PRINT 123")
    assert tokens[0].type == TokenType.PRINT
    assert tokens[1].type == TokenType.NUMBER
    assert tokens[1].value == 123

    # Fixed point
    tokens = tokenize("X = 3.14159")
    assert tokens[2].type == TokenType.NUMBER
    assert abs(tokens[2].value - 3.14159) < 0.00001

    # Scientific notation with E
    tokens = tokenize("X = 1.5E+10")
    assert tokens[2].type == TokenType.NUMBER
    assert tokens[2].value == 1.5e10

    # Scientific notation with D
    tokens = tokenize("X = 2.5D-5")
    assert tokens[2].type == TokenType.NUMBER
    assert abs(tokens[2].value - 2.5e-5) < 1e-10

    # Hexadecimal
    tokens = tokenize("X = &HFF")
    assert tokens[2].type == TokenType.NUMBER
    assert tokens[2].value == 255

    # Octal with &O
    tokens = tokenize("X = &O77")
    assert tokens[2].type == TokenType.NUMBER
    assert tokens[2].value == 63

    # Octal with &
    tokens = tokenize("X = &77")
    assert tokens[2].type == TokenType.NUMBER
    assert tokens[2].value == 63

    print("  ✓ Number tests passed")


def test_strings():
    """Test string literals"""
    print("Testing strings...")

    tokens = tokenize('"Hello, World!"')
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == "Hello, World!"

    tokens = tokenize('""')
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == ""

    print("  ✓ String tests passed")


def test_identifiers():
    """Test identifiers with type suffixes"""
    print("Testing identifiers...")

    # Simple identifier (lexer normalizes to lowercase)
    tokens = tokenize("COUNT")
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "count"

    # String variable
    tokens = tokenize("NAME$")
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "name$"

    # Integer variable
    tokens = tokenize("INDEX%")
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "index%"

    # Single precision variable
    tokens = tokenize("VALUE!")
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "value!"

    # Double precision variable
    tokens = tokenize("TOTAL#")
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "total#"

    print("  ✓ Identifier tests passed")


def test_keywords():
    """Test keyword recognition"""
    print("Testing keywords...")

    tokens = tokenize("PRINT")
    assert tokens[0].type == TokenType.PRINT

    tokens = tokenize("FOR")
    assert tokens[0].type == TokenType.FOR

    tokens = tokenize("GOTO")
    assert tokens[0].type == TokenType.GOTO

    tokens = tokenize("IF")
    assert tokens[0].type == TokenType.IF

    tokens = tokenize("THEN")
    assert tokens[0].type == TokenType.THEN

    print("  ✓ Keyword tests passed")


def test_string_functions():
    """Test string functions with $ suffix"""
    print("Testing string functions...")

    tokens = tokenize("LEFT$")
    assert tokens[0].type == TokenType.LEFT
    assert tokens[0].value == "left$"

    tokens = tokenize("RIGHT$")
    assert tokens[0].type == TokenType.RIGHT
    assert tokens[0].value == "right$"

    tokens = tokenize("MID$")
    assert tokens[0].type == TokenType.MID
    assert tokens[0].value == "mid$"

    tokens = tokenize("CHR$")
    assert tokens[0].type == TokenType.CHR
    assert tokens[0].value == "chr$"

    tokens = tokenize("STR$")
    assert tokens[0].type == TokenType.STR
    assert tokens[0].value == "str$"

    tokens = tokenize("INKEY$")
    assert tokens[0].type == TokenType.INKEY
    assert tokens[0].value == "inkey$"

    print("  ✓ String function tests passed")


def test_operators():
    """Test operator tokenization"""
    print("Testing operators...")

    # Arithmetic
    tokens = tokenize("+ - * / ^ \\")
    assert tokens[0].type == TokenType.PLUS
    assert tokens[1].type == TokenType.MINUS
    assert tokens[2].type == TokenType.MULTIPLY
    assert tokens[3].type == TokenType.DIVIDE
    assert tokens[4].type == TokenType.POWER
    assert tokens[5].type == TokenType.BACKSLASH

    # Relational
    tokens = tokenize("= <> < > <= >=")
    assert tokens[0].type == TokenType.EQUAL
    assert tokens[1].type == TokenType.NOT_EQUAL
    assert tokens[2].type == TokenType.LESS_THAN
    assert tokens[3].type == TokenType.GREATER_THAN
    assert tokens[4].type == TokenType.LESS_EQUAL
    assert tokens[5].type == TokenType.GREATER_EQUAL

    # Alternative not equal
    tokens = tokenize("><")
    assert tokens[0].type == TokenType.NOT_EQUAL

    # Logical (keywords)
    tokens = tokenize("AND OR NOT")
    assert tokens[0].type == TokenType.AND
    assert tokens[1].type == TokenType.OR
    assert tokens[2].type == TokenType.NOT

    print("  ✓ Operator tests passed")


def test_line_numbers():
    """Test line number handling"""
    print("Testing line numbers...")

    tokens = tokenize("10 PRINT")
    assert tokens[0].type == TokenType.LINE_NUMBER
    assert tokens[0].value == 10
    assert tokens[1].type == TokenType.PRINT

    tokens = tokenize("65529 END")
    assert tokens[0].type == TokenType.LINE_NUMBER
    assert tokens[0].value == 65529

    print("  ✓ Line number tests passed")


def test_comments():
    """Test comment handling"""
    print("Testing comments...")

    # REM comment
    tokens = tokenize("10 REM This is a comment")
    assert tokens[0].type == TokenType.LINE_NUMBER
    assert tokens[1].type == TokenType.REM
    assert tokens[2].type == TokenType.NEWLINE or tokens[2].type == TokenType.EOF

    # Apostrophe comment
    tokens = tokenize("20 ' This is also a comment")
    assert tokens[0].type == TokenType.LINE_NUMBER
    assert tokens[1].type == TokenType.APOSTROPHE

    print("  ✓ Comment tests passed")


def test_complete_statement():
    """Test a complete BASIC statement"""
    print("Testing complete statement...")

    code = '10 FOR I% = 1 TO 10: PRINT I%: NEXT I%'
    tokens = tokenize(code)

    assert tokens[0].type == TokenType.LINE_NUMBER
    assert tokens[0].value == 10
    assert tokens[1].type == TokenType.FOR
    assert tokens[2].type == TokenType.IDENTIFIER
    assert tokens[2].value == "i%"
    assert tokens[3].type == TokenType.EQUAL
    assert tokens[4].type == TokenType.NUMBER
    assert tokens[4].value == 1
    assert tokens[5].type == TokenType.TO
    assert tokens[6].type == TokenType.NUMBER
    assert tokens[6].value == 10
    assert tokens[7].type == TokenType.COLON
    assert tokens[8].type == TokenType.PRINT
    assert tokens[9].type == TokenType.IDENTIFIER
    assert tokens[9].value == "i%"
    assert tokens[10].type == TokenType.COLON
    assert tokens[11].type == TokenType.NEXT
    assert tokens[12].type == TokenType.IDENTIFIER
    assert tokens[12].value == "i%"

    print("  ✓ Complete statement test passed")


def test_multiline_program():
    """Test a multi-line program"""
    print("Testing multi-line program...")

    code = """10 PRINT "Hello, World!"
20 INPUT "Enter your name"; NAME$
30 PRINT "Hello, "; NAME$
40 END
"""

    tokens = tokenize(code)

    # Check first line
    assert tokens[0].type == TokenType.LINE_NUMBER
    assert tokens[0].value == 10
    assert tokens[1].type == TokenType.PRINT
    assert tokens[2].type == TokenType.STRING
    assert tokens[2].value == "Hello, World!"
    assert tokens[3].type == TokenType.NEWLINE

    # Find line 20
    idx = 4
    assert tokens[idx].type == TokenType.LINE_NUMBER
    assert tokens[idx].value == 20

    print("  ✓ Multi-line program test passed")


def test_question_mark():
    """Test ? as shorthand for PRINT"""
    print("Testing ? shorthand...")

    tokens = tokenize('10 ? "Hello"')
    assert tokens[0].type == TokenType.LINE_NUMBER
    assert tokens[1].type == TokenType.QUESTION
    assert tokens[2].type == TokenType.STRING

    print("  ✓ Question mark test passed")


def run_all_tests():
    """Run all lexer tests"""
    print("\n" + "="*50)
    print("MBASIC 5.21 Lexer Tests")
    print("="*50 + "\n")

    try:
        test_numbers()
        test_strings()
        test_identifiers()
        test_keywords()
        test_string_functions()
        test_operators()
        test_line_numbers()
        test_comments()
        test_complete_statement()
        test_multiline_program()
        test_question_mark()

        print("\n" + "="*50)
        print("All tests passed! ✓")
        print("="*50 + "\n")
        return 0

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except LexerError as e:
        print(f"\n✗ Lexer error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
