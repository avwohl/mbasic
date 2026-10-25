#!/usr/bin/env python3
"""
INPUT and INPUT # in the interpreter follow MBASIC 5.21 (GitHub issue #10).

Each expected text below was measured on the real MBASIC 5.21 binary under
cpmemu, with the answers sent half a second apart. The harness acts like a
terminal: it prints each answer and a line end after the prompt.

Keyboard INPUT: "? " unless a comma follows the prompt, quoted fields, blanks,
?Redo from start for a bad value or a wrong count, no variable assigned from a
bad line. File INPUT #: fields come from the stream, no Redo, a bad number is 0.
"""

import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.interpreter import Interpreter
from src.iohandler.base import IOHandler
from src.lexer import Lexer
from src.parser import Parser
from src.runtime import Runtime

results = []


def check(actual, expected, label):
    ok = actual == expected
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}: {label}")
    if not ok:
        print(f"   expected: {expected!r}")
        print(f"   actual:   {actual!r}")


class Handler(IOHandler):
    def __init__(self):
        self.parts = []

    def output(self, text, end='\n'):
        self.parts.append(str(text) + end)

    def input(self, prompt=''):
        return ""

    def input_line(self, prompt=''):
        return ""

    def input_char(self, blocking=True):
        return ""

    def clear_screen(self):
        pass

    def error(self, message):
        self.parts.append(f"Error: {message}\n")

    def debug(self, message):
        pass


def run(source, answers=()):
    """Run a program, answering each INPUT prompt like a terminal. Returns the screen text."""
    handler = Handler()
    ast = Parser(Lexer(source).tokenize()).parse()
    runtime = Runtime({line.line_number: line for line in ast.lines})
    interpreter = Interpreter(runtime, handler)
    state = interpreter.start()
    pending = list(answers)
    for _ in range(1000):
        try:
            state = interpreter.tick(mode='run', max_statements=1000)
        except Exception as error:  # tick re-raises the error after recording it
            handler.parts.append(f"ERROR: {error}\n")
            break
        if state.input_prompt is not None:
            answer = pending.pop(0)
            handler.parts.append(answer + "\n")
            interpreter.provide_input(answer)
        elif not runtime.pc.is_running():
            break
    return ''.join(handler.parts)


# -- the rows of the table in issue #10 ---------------------------------------

def test_comma_prompt_has_no_question_mark():
    check(run('10 INPUT "P",X\n20 PRINT X\n', ["7"]), "P7\n 7 \n", 'INPUT "P",X shows P, not P?')


def test_semicolon_prompt_has_question_mark():
    check(run('10 INPUT "P";X\n20 PRINT X\n', ["7"]), "P? 7\n 7 \n", 'INPUT "P";X shows P?')


def test_no_prompt_has_question_mark():
    check(run('10 INPUT X\n20 PRINT X\n', ["7"]), "? 7\n 7 \n", "INPUT X shows ?")


def test_redo_on_bad_number():
    check(run('10 INPUT "N";N\n20 PRINT N\n', ["abc", "9"]),
          "N? abc\n?Redo from start\nN? 9\n 9 \n", "a bad number asks again with the same prompt")


def test_quoted_field_holds_a_comma():
    check(run('10 INPUT A$,B$\n20 PRINT A$;"|";B$\n', ['"x,y",z']), '? "x,y",z\nx,y|z\n',
          'A$ = x,y and B$ = z for "x,y",z')


def test_too_many_values_then_good_line():
    check(run('10 INPUT C,D\n20 PRINT C;D\n', ["1,2,3", "4,5"]),
          "? 1,2,3\n?Redo from start\n? 4,5\n 4  5 \n", "too many values give Redo")


def test_too_few_values_redo():
    check(run('10 INPUT C,D\n20 PRINT C;D\n', ["1", "4,5"]),
          "? 1\n?Redo from start\n? 4,5\n 4  5 \n", "too few values give Redo, not Input past end")


def test_input_semicolon_keeps_question_mark():
    check(run('10 INPUT; "S";E\n20 PRINT E\n', ["6"]), "S? 6\n 6 \n", 'INPUT; "S";E shows S?')


# -- more keyboard rules ------------------------------------------------------

def test_no_variable_is_assigned_from_a_bad_line():
    check(run('10 A=5\n20 INPUT A,B\n30 PRINT A;B\n', ["1,x", "2,3"]),
          "? 1,x\n?Redo from start\n? 2,3\n 2  3 \n", "good field before a bad one is not kept (checked by the retry)")
    check(run('10 A=5:B=6\n20 INPUT A,B\n30 PRINT A;B\n', ["1,x", "7,8"]).count("?Redo"), 1, "one Redo")


def test_blanks_and_empty_fields():
    check(run('10 INPUT A,B,C\n20 PRINT A;B;C\n', [" 1 2 ,, 3"]), "?  1 2 ,, 3\n 12  0  3 \n",
          "blanks inside a number are ignored, an empty field is 0")
    check(run('10 INPUT A$,B$\n20 PRINT "[";A$;"][";B$;"]"\n', ["  x y  , z "]), "?   x y  , z \n[x y][z]\n",
          "blanks around a string field are dropped")
    check(run('10 INPUT A$,B$\n20 PRINT "[";A$;"][";B$;"]"\n', [","]), "? ,\n[][]\n", "empty string fields")


def test_hex_and_octal():
    check(run('10 INPUT A,B,C\n20 PRINT A;B;C\n', ["&H1F,&O17,&HFFFF"]), "? &H1F,&O17,&HFFFF\n 31  15 -1 \n",
          "&H and &O numbers")
    check(run('10 INPUT A\n20 PRINT A\n', ["&H12345"]), "? &H12345\nERROR: Overflow\n",
          "&H over 16 bits is an Overflow error, not a Redo")


def test_integer_variable_rounds_and_overflows():
    check(run('10 INPUT A%,B%\n20 PRINT A%;B%\n', ["1.5,-2.5"]), "? 1.5,-2.5\n 2 -3 \n",
          "an integer variable rounds, halves away from zero")
    check(run('10 INPUT A%\n20 PRINT A%\n', ["40000"]), "? 40000\nERROR: Overflow\n",
          "40000 into an integer variable is an Overflow error, not a Redo")


def test_float_overflow_asks_again():
    check(run('10 INPUT C\n20 PRINT C\n', ["1e50", "5"]), "? 1e50\nOverflow\n?Redo from start\n? 5\n 5 \n",
          "1e50 prints Overflow and Redo")


def test_quoted_number_and_text_after_quote_are_redo():
    check(run('10 INPUT A\n20 PRINT A\n', ['"5"', "6"]), '? "5"\n?Redo from start\n? 6\n 6 \n', "quoted number")
    check(run('10 INPUT A$\n20 PRINT A$\n', ['"a"b', "c"]), '? "a"b\n?Redo from start\n? c\nc\n',
          "text after a closing quote")


def test_unterminated_quote_and_trailing_blank_after_quote():
    check(run('10 INPUT A$\n20 PRINT "[";A$;"]"\n', ['"abc']), '? "abc\n[abc]\n', "closing quote may be missing")
    check(run('10 INPUT A$,B$\n20 PRINT "[";A$;"][";B$;"]"\n', [' x y , "q" ']), '?  x y , "q" \n[x y][q]\n',
          "blank after a closing quote is fine")


def test_exponent_forms():
    check(run('10 INPUT A,B#\n20 PRINT A;B#\n', ["1d2,1e3"]), "? 1d2,1e3\n 100  1000 \n", "D and E exponents")


# -- INPUT # ------------------------------------------------------------------

def file_program(tmp, content_lines, reads):
    """Write the data with PRINT #, read it back with the given statements."""
    path = str(Path(tmp) / "T.DAT")
    lines = ['5 Q$=CHR$(34)', f'10 OPEN "O",1,"{path}"']
    n = 20
    for text in content_lines:
        lines.append(f'{n} PRINT #1,{text}')
        n += 1
    lines.append(f'{n} CLOSE 1')
    n += 1
    lines.append(f'{n} OPEN "I",1,"{path}"')
    n += 1
    for read in reads:
        lines.append(f'{n} {read}')
        n += 1
    return '\n'.join(lines) + '\n'


def test_file_input():
    with tempfile.TemporaryDirectory() as tmp:
        src = file_program(tmp, ['"a,b"', 'Q$;"x,y";Q$;" , z"', '" 1 2 ,3"', '"4"', '"  q  ,"', '"abc,5"'], [
            'INPUT #1,A$,B$', 'PRINT "[";A$;"][";B$;"]"',
            'INPUT #1,C$,D$', 'PRINT "[";C$;"][";D$;"]"',
            'INPUT #1,E,F', 'PRINT E;F',
            'INPUT #1,G,H$', 'PRINT G;"[";H$;"]"',
            'INPUT #1,I$,J$', 'PRINT "[";I$;"][";J$;"]"',
            'INPUT #1,K$,L$', 'PRINT "[";K$;"][";L$;"]"',
        ])
        check(run(src), "[a][b]\n[x,y][z]\n 1  2 \n 3 [4]\n[q][]\n[abc][5]\n",
              "INPUT # splits like MBASIC: quotes, blank-ended numbers, empty field at a line end")


def test_file_input_bad_number_is_zero_and_no_redo():
    with tempfile.TemporaryDirectory() as tmp:
        src = file_program(tmp, ['"abc,12xyz"', '"&H10,1d2"'],
                           ['INPUT #1,A,B', 'PRINT A;B', 'INPUT #1,C,D', 'PRINT C;D'])
        check(run(src), " 0  12 \n 16  100 \n", "a bad number in a file is read as 0, 12xyz as 12, no Redo")


def test_file_input_quoted_number_field_and_blank_lines():
    with tempfile.TemporaryDirectory() as tmp:
        src = file_program(tmp, ['""', '"a"', '"b,c"'],
                           ['INPUT #1,A$', 'PRINT "[";A$;"]"', 'INPUT #1,B$', 'PRINT "[";B$;"]"',
                            'INPUT #1,C$,D$', 'PRINT "[";C$;"][";D$;"]"'])
        check(run(src), "[]\n[a]\n[b][c]\n", "a blank line is an empty field")


def test_file_input_quote_spans_lines_and_text_after_quote():
    with tempfile.TemporaryDirectory() as tmp:
        src = file_program(tmp, ['Q$;"one"', '"two";Q$;"abc,def"'],
                           ['INPUT #1,A$', 'PRINT "[";A$;"]"', 'INPUT #1,B$,C$', 'PRINT "[";B$;"][";C$;"]"'])
        # The quote before "one" is closed by the quote on the next line, so the string holds
        # the line end. Text after a closing quote starts the next field (abc), then def.
        check(run(src), "[one\ntwo]\n[abc][def]\n",
              "a quoted string runs across the line end; text after a quote starts the next field")


def test_file_input_overflow():
    with tempfile.TemporaryDirectory() as tmp:
        src = file_program(tmp, ['"40000"', '"1e50"'], ['INPUT #1,A%'])
        check(run(src), "ERROR: Overflow\n", "40000 into an integer variable is Overflow")
    with tempfile.TemporaryDirectory() as tmp:
        src = file_program(tmp, ['"1e50"'], ['INPUT #1,A', 'PRINT A'])
        check(run(src), "Overflow\n 1.70141E+38 \n", "1e50 into a single prints Overflow and keeps the largest number")


def test_file_input_past_end():
    with tempfile.TemporaryDirectory() as tmp:
        src = file_program(tmp, ['"a"'], ['INPUT #1,A$', 'INPUT #1,B$'])
        check(run(src).startswith("ERROR: Input past end"), True, "reading past the end is an error")


def test_file_input_numeric_target_ignores_quotes():
    # Measured on real MBASIC 5.21: a quote is no quote when the target is a number.
    with tempfile.TemporaryDirectory() as tmp:
        src = file_program(tmp, ['Q$;"5";Q$;",6"', 'Q$;"a,b";Q$;",7,8"', 'Q$;"x";Q$;"y,9"', '"w"', 'Q$;"un"', '"term"'], [
            'INPUT #1,A,B', 'PRINT A;B', 'INPUT #1,A,B,C', 'PRINT A;B;C',
            'INPUT #1,A,B', 'PRINT A;B', 'INPUT #1,A,B', 'PRINT A;B', 'INPUT #1,A,B', 'PRINT A;B'])
        check(run(src), " 0  6 \n 0  0  7 \n 8  0 \n 9  0 \n 0  0 \n",
              "a quote in a numeric field makes 0 and an unterminated quote does not run to the end of the file")


def test_blank_after_radix_prefix_is_redo():
    check(run('10 INPUT A\n20 PRINT A\n', [" &H 10", "&H10"]),
          "?  &H 10\n?Redo from start\n? &H10\n 16 \n", "a blank after &H gives Redo")
    check(run('10 INPUT A\n20 PRINT A\n', ["1 E 2"]), "? 1 E 2\n 100 \n", "blanks inside a decimal number are ignored")


def test_empty_prompt_with_comma_or_semicolon():
    check(run('10 INPUT "",A\n20 PRINT "A=";A\n', ["5"]), "5\nA= 5 \n", 'INPUT "",A shows no prompt and goes on')
    check(run('10 INPUT "";A\n20 PRINT "A=";A\n', ["5"]), "? 5\nA= 5 \n", 'INPUT "";A shows ?')
    check(run('10 INPUT;A\n20 PRINT "A=";A\n', ["5"]), "? 5\nA= 5 \n", "INPUT;A shows ?")


def test_percent_suffix_rounds_and_exponent_suffix_is_redo():
    prog = '10 INPUT A\n20 PRINT A\n'
    check(run(prog, ["1.5%"]), "? 1.5%\n 2 \n", "1.5% is 2")
    check(run(prog, ["-1.5%"]), "? -1.5%\n-2 \n", "-1.5% is -2")
    check(run(prog, ["2.5%"]), "? 2.5%\n 3 \n", "2.5% is 3")
    check(run(prog, ["5!"]), "? 5!\n 5 \n", "5! is 5")
    check(run(prog, ["5 #"]), "? 5 #\n 5 \n", "5 # is 5")
    for bad in ["1E5%", "1e5#", "1E5!", "1d1%", "1%%", "5%5", "&H1%"]:
        check(run(prog, [bad, "3"]), f"? {bad}\n?Redo from start\n? 3\n 3 \n", f"{bad} is a Redo")
    check(run(prog, ["40000%"]), "? 40000%\nERROR: Overflow\n", "40000% is Overflow even for a single")


def test_bare_ampersand_and_octal_without_o():
    prog = '10 INPUT A\n20 PRINT A\n'
    check(run(prog, ["&"]), "? &\n 0 \n", "& alone is 0")
    check(run(prog, ["&10"]), "? &10\n 8 \n", "&10 is octal 8")
    check(run(prog, ["&1 0"]), "? &1 0\n 8 \n", "&1 0 is octal 8")
    check(run(prog, ["&O"]), "? &O\n 0 \n", "&O alone is 0")
    for bad in ["&8", "&O8", "&o7 8", "&O8x", "&9"]:
        check(run(prog, [bad]), f"? {bad}\nERROR: Syntax error\n", f"{bad} is a Syntax error, not a Redo")
    for bad in ["&H-1", "&O-1", "&Oa", "&Z", "&H1G", "&O7x", "&h ff", "&H 1", "&H1 0"]:
        check(run(prog, [bad, "3"]), f"? {bad}\n?Redo from start\n? 3\n 3 \n", f"{bad} is a Redo")


def test_blanks_in_octal_allowed_not_in_hex():
    prog = '10 INPUT A\n20 PRINT A\n'
    check(run(prog, ["&o 7"]), "? &o 7\n 7 \n", "&o 7 is 7")
    check(run(prog, ["&O 17"]), "? &O 17\n 15 \n", "&O 17 is 15")
    check(run(prog, ["&O1 7"]), "? &O1 7\n 15 \n", "&O1 7 is 15")


def test_file_input_octal_and_percent():
    with tempfile.TemporaryDirectory() as tmp:
        src = file_program(tmp, ['"&O 17,&H 10,1e5%,&10,1.5%,-2.5%,&"'],
                           ['FOR I=1 TO 9:INPUT #1,A:PRINT A;:NEXT','PRINT'])
        check(run(src), " 0  17  0  10  100000  8  2 -3  0 \n", "file numbers: blank ends a number, & is octal, % rounds")
    with tempfile.TemporaryDirectory() as tmp:
        src = file_program(tmp, ['"40000%"'], ['INPUT #1,A'])
        check(run(src), "ERROR: Overflow\n", "40000% from a file is Overflow")


def test_line_input_unchanged():
    check(run('10 LINE INPUT "L";L$\n20 PRINT "[";L$;"]"\n', [' a, "b" ']), 'L a, "b" \n[ a, "b" ]\n',
          "LINE INPUT keeps the whole line")


if __name__ == "__main__":
    for name, func in list(globals().items()):
        if name.startswith("test_") and callable(func):
            print(f"\n{name}")
            func()
    sys.exit(0 if all(results) else 1)
