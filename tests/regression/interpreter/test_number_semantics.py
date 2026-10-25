#!/usr/bin/env python3
"""
Overflow, domain errors, VAL, &H/&O constants and HEX$/OCT$ against real MBASIC 5.21.

The programs in tests/regression/integration/fixtures/number_semantics/ each have a
.real file: what MBASIC 5.21 printed for the program under cpmemu. The interpreter
must print the same. (The JavaScript backend is checked against the same files by
tests/regression/integration/test_js_number_semantics.py.)

Left out on purpose, because the project does not emulate the MBF range (docs/dev/
MBASIC_521_DIVERGENCES_TODO.md, section 10): results that MBF cannot hold but IEEE
can (2^127, EXP(88), 1D300/1D-300) and the last digits of decimal literals.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.lexer import Lexer, LexerOverflow  # noqa: E402
from src.number_format import (exceeds_range, machine_infinity, radix_word,  # noqa: E402
                               format_number, DOUBLE_DIGITS, SINGLE_DIGITS)
from src.input_fields import val_text  # noqa: E402
from src.editing.manager import ProgramManager  # noqa: E402

FIXTURES = PROJECT_ROOT / "tests" / "regression" / "integration" / "fixtures" / "number_semantics"

results = []


def check(condition, label):
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}: {label}")


def run_program(path):
    """What the interpreter prints for a program file (CLI, RUN, SYSTEM)."""
    run = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "mbasic"), str(path), "--ui", "cli"],
        cwd=PROJECT_ROOT, input="RUN\nSYSTEM\n", capture_output=True, text=True, timeout=120)
    lines = run.stdout.split("\n")
    start = lines.index("Ok") + 1
    end = max(i for i, line in enumerate(lines) if line == "Goodbye")
    if lines[end - 1] == "Ok":             # the Ok that follows RUN
        end -= 1
    return "\n".join(lines[start:end])


def test_programs_match_real_mbasic():
    print("\nPrograms against the output of real MBASIC 5.21")
    print("-" * 60)
    for bas in sorted(FIXTURES.glob("*.bas")):
        expected = (FIXTURES / (bas.stem + ".real")).read_text().rstrip("\n")
        got = run_program(bas).rstrip("\n")
        ok = got == expected
        check(ok, f"{bas.name}")
        if not ok:
            want_lines, got_lines = expected.split("\n"), got.split("\n")
            for i, (w, g) in enumerate(zip(want_lines, got_lines)):
                if w != g:
                    print(f"    line {i + 1}: want {w!r}, got {g!r}")
                    break
            else:
                print(f"    want {len(want_lines)} lines, got {len(got_lines)}")


def test_error_after_partial_print_line(tmp_path=None):
    print("\nA fatal error after a partial PRINT line starts a new line")
    print("-" * 60)
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        bas = Path(d) / "partial.bas"
        bas.write_text('10 PRINT "AB";HEX$(-32769)\n')
        got = run_program(bas)
    check(got.startswith("AB\nOverflow in 10"), f"AB, line break, Overflow in 10 (got {got!r})")
    # PRINT USING, an empty PRINT and a later non-PRINT statement: output of
    # real MBASIC in fixtures/number_semantics_errcol (not run for the JS
    # backend, which words fatal errors differently).
    errcol = FIXTURES.parent / "number_semantics_errcol"
    for bas in sorted(errcol.glob("*.bas")):
        want = (errcol / (bas.stem + ".real")).read_text().rstrip("\n")
        check(run_program(bas).rstrip("\n") == want, f"{bas.name} matches real MBASIC")


def test_val():
    print("\nVAL")
    print("-" * 60)
    for text, want in [
        ("1D2", 100), ("1D+2", 100), ("1 E2", 100), ("1 2", 12), ("12 34 56", 123456),
        ("1 .5", 1.5), ("&H10", 16), ("&HFF", 255), ("&O17", 15), ("&10", 8),
        ("&H8000", -32768), ("&HFFFF", -1), ("&H1G", 1), ("  &H10", 16), ("& H10", 16),
        ("- 5", -5), ("12abc", 12), ("1.5.5", 1.5), ("1e", 1), ("1e+", 1), ("1+2", 1),
        ("1E2E3", 100), ("Infinity", 0), ("&H 10", 0), ("-&H10", 0), ("&H1 0", 1),
        ("", 0), ("\t7", 7), ("1\t2", 12), ("1.5%", 2), ("&O 17", 15), ("&7 7", 63),
        ("1,5", 1), (".E5", 0), ("--5", 0),
    ]:
        got = val_text(text)
        check(got == want, f"VAL({text!r}) = {got!r}")
    for text, error in [("&HFFFFF", OverflowError), ("&H00010", OverflowError),
                        ("&O200000", OverflowError), ("&O18", RuntimeError),
                        ("40000%", OverflowError)]:
        try:
            val_text(text)
            raised = None
        except (OverflowError, RuntimeError) as exc:
            raised = type(exc)
        check(raised is error, f"VAL({text!r}) raises {error.__name__}")
    check(val_text("1E400") == float("inf"), "VAL('1E400') is infinite here; the interpreter prints Overflow")


def test_hex_and_octal():
    print("\nHEX$ and OCT$")
    print("-" * 60)
    for value, want in [(-1, 0xFFFF), (-32768, 0x8000), (-2, 0xFFFE), (65535, 0xFFFF),
                        (32768, 0x8000), (0, 0), (2.5, 3), (-0.5, 0xFFFF), (65535.4, 0xFFFF),
                        (65535.5, 0xFFFF), (65535.6, 0), (-32768.4, 0x8000)]:
        check(radix_word(value) == want, f"radix_word({value!r}) = {want:#x}")
    for value in (65536, -32769, 32767.5, -32768.6, 1e10, float("inf")):
        try:
            radix_word(value)
            raised = False
        except OverflowError:
            raised = True
        check(raised, f"radix_word({value!r}) is Overflow")


def test_constants_in_the_lexer():
    print("\n&H, &O and & constants")
    print("-" * 60)

    def value_of(text):
        return Lexer(text).tokenize()[0].value

    for text, want in [("&HFFFF", -1), ("&H8000", -32768), ("&H7FFF", 32767), ("&HFFFE", -2),
                       ("&O177777", -1), ("&177777", -1), ("&O0177777", -1), ("&HFF", 255),
                       ("&H0FFF", 4095), ("&O100000", -32768), ("&H", 0), ("&O", 0)]:
        check(value_of(text) == want, f"{text} = {want}")
    for text in ("&H10000", "&H00010", "&HFFFFF", "&O200000", "&200000"):
        try:
            Lexer(text).tokenize()
            raised = False
        except LexerOverflow:
            raised = True
        check(raised, f"{text} is Overflow")
    token = Lexer("&HFFFF").tokenize()[0]
    check(token.literal_text == "&HFFFF", "the source text of the constant is kept")


def test_literals_that_overflow():
    print("\nA literal that is infinite in its precision")
    print("-" * 60)
    lexer = Lexer("PRINT 1E39;1D39;1E-39;1E38")
    values = [t.value for t in lexer.tokenize() if t.type.name == "NUMBER"]
    check(values[0] == machine_infinity(SINGLE_DIGITS), "1E39 becomes single machine infinity")
    check(values[1] == 1e39, "1D39 is a legal double here (the MBF range is not emulated)")
    check(values[3] == 1e38, "1E38 is untouched")
    check(lexer.overflow_literals == 1, "one literal was replaced")
    check(format_number(machine_infinity(SINGLE_DIGITS), SINGLE_DIGITS) == "1.70141E+38",
          "single machine infinity prints as 1.70141E+38")
    check(format_number(machine_infinity(DOUBLE_DIGITS), DOUBLE_DIGITS) == "1.701411834604693D+38",
          "double machine infinity prints as 1.701411834604693D+38")
    check(exceeds_range(1e39, SINGLE_DIGITS) and not exceeds_range(3e38, SINGLE_DIGITS),
          "single range is binary32")
    check(exceeds_range(float("inf"), DOUBLE_DIGITS) and not exceeds_range(1e300, DOUBLE_DIGITS),
          "double range is binary64")


def test_line_entry():
    print("\nTyping a line")
    print("-" * 60)
    program = ProgramManager({})
    ok, error = program.add_line(10, "10 PRINT 1E39")
    check(ok and program.take_notices() == ["Overflow"], "1E39 is stored, and Overflow is announced")
    ok, error = program.add_line(20, "20 PRINT 1E38")
    check(ok and program.take_notices() == [], "1E38 is stored in silence")
    ok, error = program.add_line(30, "30 PRINT &H10000")
    check(not ok and error == "Overflow in 30", f"&H10000 is refused with Overflow ({error!r})")
    ok, error = program.add_line(40, "40 PRINT &HFFFF")
    check(ok, "&HFFFF is stored")


if __name__ == "__main__":
    print("MBASIC 5.21 overflow, VAL and radix constants")
    print("=" * 60)
    test_programs_match_real_mbasic()
    test_error_after_partial_print_line()
    test_val()
    test_hex_and_octal()
    test_constants_in_the_lexer()
    test_literals_that_overflow()
    test_line_entry()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")
    if failed:
        print("Some tests failed")
        sys.exit(1)
    print("All tests passed!")
    sys.exit(0)
