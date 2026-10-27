"""Compile BASIC to CP/M with --compile-c, run it, and compare with the interpreter.

Each program is compiled with the preferred toolchain (uc80, um80, ul80), run
under the CP/M emulator cpmemu, and the output is compared byte for byte with
`python3 mbasic prog.bas --ui cli` (RUN piped in).  CP/M ends a line with CR LF
and the interpreter with LF, so the compiled output is normalised first.

The tests skip when the toolchain or the emulator is missing.  The emulator is
found through the MBASIC_CPMEMU environment variable (a path to the cpmemu
binary) or on PATH.  The toolchain libraries are found as --compile-c finds
them (MBASIC_UC80_LIB, or the uc80 package).

The tests that need no toolchain check what the backend refuses to compile.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: C backend tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


def cpmemu_path():
    """The cpmemu binary: MBASIC_CPMEMU, else the first cpmemu on PATH."""
    env = os.environ.get("MBASIC_CPMEMU")
    if env and os.access(env, os.X_OK):
        return env
    return shutil.which("cpmemu")


def toolchain_missing():
    """Why the compile-and-run tests cannot run here, or None."""
    for tool in ("uc80", "um80", "ul80"):
        if shutil.which(tool) is None:
            return f"{tool} is needed to build the compiled program"
    from src.mbasic_main import uc80_lib_dir
    if uc80_lib_dir() is None:
        return "uc80's libc.lib is not built (python3 -m uc80.lib.build_libs)"
    if cpmemu_path() is None:
        return "cpmemu is needed to run the compiled program (set MBASIC_CPMEMU)"
    return None


NEEDS_TOOLCHAIN = pytest.mark.skipif(toolchain_missing() is not None,
                                     reason=toolchain_missing() or "")


def compile_c(tmp_path, source, name="prog"):
    """Run --compile-c; return the CompletedProcess."""
    basic = tmp_path / f"{name}.bas"
    basic.write_text(source)
    return subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic), "--compile-c", str(tmp_path / name)],
        cwd=ROOT, capture_output=True, text=True, timeout=300)


def run_compiled(tmp_path, stdin, name="prog"):
    result = subprocess.run([cpmemu_path(), str(tmp_path / f"{name}.com")],
                            input=stdin.encode(), capture_output=True, timeout=120,
                            cwd=tmp_path)
    return result.stdout.decode("latin1").replace("\r\n", "\n")


def run_interpreted(tmp_path, stdin, name="prog"):
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / f"{name}.bas"), "--ui", "cli"],
        cwd=tmp_path, input=("RUN\n" + stdin + "SYSTEM\n").encode(),
        capture_output=True, timeout=120)
    out = result.stdout.decode("latin1")
    out = out[out.index("Ok\n") + len("Ok\n"):]
    # Ok follows RUN, then SYSTEM says Goodbye.
    for tail in ("Goodbye\n", "Ok\n"):
        if out.endswith(tail):
            out = out[:-len(tail)]
    return out


def check_same(tmp_path, source, stdin=""):
    result = compile_c(tmp_path, source)
    assert result.returncode == 0, result.stdout + result.stderr
    assert run_compiled(tmp_path, stdin) == run_interpreted(tmp_path, stdin)


# --- Issue 29: numbers -------------------------------------------------------

@NEEDS_TOOLCHAIN
def test_issue_29_example(tmp_path):
    """-3 was dropped, 1/3 was 0, and no number had MBASIC's blanks."""
    source = '10 PRINT "HI";2+3\n20 PRINT -3;1/3;8.7\n30 X%=7:PRINT X%\n40 END\n'
    assert compile_c(tmp_path, source).returncode == 0
    assert run_compiled(tmp_path, "") == "HI 5 \n-3  .333333  8.7 \n 7 \n"
    assert run_compiled(tmp_path, "") == run_interpreted(tmp_path, "")


@NEEDS_TOOLCHAIN
def test_number_format_and_operators(tmp_path):
    check_same(tmp_path, """10 PRINT 1;2;-3
20 PRINT 100000;1000000;1E6
30 PRINT .5;.05;.000012;1.5E-9;-.25
40 PRINT 5/2;7\\2;-7\\2;7 MOD 3;-7 MOD 3;2^10;2^0.5
50 PRINT 200*200;32767+1;-32768-1
60 PRINT 3=3;3=4;1<2;NOT 0;NOT -1;5 AND 3;5 OR 3;5 XOR 3
70 PRINT "A" < "B"; "B" < "A"; "A" = "A"
80 PRINT 123456.7;0.1+0.2;1/7
90 B%=10: C%=3: PRINT B%/C%;B%\\C%;B% MOD C%
100 PRINT SQR(2);INT(-2.5);FIX(-2.5);ABS(-3);SGN(-4)
110 PRINT 1.0;2.50;100;1E5;1E-5
120 PRINT STR$(5);STR$(-5);STR$(1/3);"|";LEN(STR$(12))
130 PRINT CINT(2.5);CINT(-2.5);CINT(3.49)
140 X=1.5: Y%=X: PRINT Y%
150 PRINT 999999;9999999;0.9999995;99999.95;16777216!
160 END
""")


@NEEDS_TOOLCHAIN
def test_print_zones_tab_and_wrap(tmp_path):
    check_same(tmp_path, """10 PRINT "x";TAB(10);"y";TAB(5);"z"
20 PRINT "a","b","c","d","e","f"
30 PRINT 1;"A";2;"B"
40 PRINT SPC(3);"s";SPC(2);"t"
50 PRINT 1,2,3
60 PRINT "x",
70 PRINT "y"
80 FOR I=1 TO 30: PRINT I;: NEXT I: PRINT
90 PRINT "THIS IS A LONG STRING OF TEXT THAT FILLS MOST OF A LINE ";"AND THIS WRAPS"
100 END
""")


@NEEDS_TOOLCHAIN
def test_control_flow_and_loops(tmp_path):
    check_same(tmp_path, """10 FOR I=10 TO 1 STEP -3: PRINT I;: NEXT I: PRINT
20 FOR I=1 TO 3: FOR J=1 TO 2: PRINT I*J;: NEXT J,I: PRINT
30 S=-1: FOR I=3 TO 1 STEP S: PRINT I;: NEXT: PRINT
40 N=0
50 N=N+1: IF N<4 THEN 50
60 PRINT N
70 GOSUB 100: PRINT "back": END
100 PRINT "sub": RETURN
""")


# --- Issue 28: string arrays -------------------------------------------------

@NEEDS_TOOLCHAIN
def test_issue_28_example(tmp_path):
    """INPUT and LINE INPUT into an element, and PRINT of elements."""
    source = ('10 DIM A$(3),N(3)\n20 A$(1)="x":A$(2)="y"\n30 N(1)=5\n40 INPUT A$(3)\n'
              '50 PRINT A$(1);A$(2);A$(3);N(1)\n60 LINE INPUT "P";A$(1)\n70 PRINT A$(1)\n')
    check_same(tmp_path, source, "hello\nsecond line\n")


@NEEDS_TOOLCHAIN
def test_string_arrays(tmp_path):
    check_same(tmp_path, """10 DIM A$(5), B$(2,3), N(4), M%(3)
20 FOR I=0 TO 5: A$(I)=CHR$(65+I)+STR$(I): NEXT I
30 FOR I=0 TO 5: PRINT A$(I);: NEXT I: PRINT
40 FOR I=0 TO 2: FOR J=0 TO 3: B$(I,J)=A$(I)+"-"+A$(J): NEXT J,I
50 PRINT B$(2,3), B$(0,1)
60 PRINT B$(1,2);"|";B$(2,0)
70 SWAP A$(1),A$(4)
80 PRINT A$(1);A$(4)
90 MID$(A$(2),2,1)="Z"
100 PRINT A$(2)
110 READ A$(0),A$(5),N(2),M%(1)
120 DATA first,last,3.5,7
130 PRINT A$(0);A$(5);N(2);M%(1)
140 IF A$(0)="first" THEN PRINT "eq" ELSE PRINT "ne"
150 IF A$(0)<A$(5) THEN PRINT "lt" ELSE PRINT "ge"
160 PRINT LEN(A$(2)), LEFT$(A$(5),2), A$(5)+A$(0)
170 I=2: PRINT A$(I+1);A$(I*2-1)
180 A$(3)=LEFT$(A$(3),1)+MID$(A$(4),2)+RIGHT$("xyz",2)
190 PRINT A$(3);INSTR(A$(3),"y");ASC(A$(0));VAL(A$(2))
200 ERASE A$
210 PRINT "[";A$(1);"]";LEN(A$(2))
220 N(1)=1/3: N(3)=-N(1)*2: PRINT N(1);N(3);N(1)+N(3)
230 M%(2)=7: M%(3)=M%(2)*3: PRINT M%(3)
240 END
""")


@NEEDS_TOOLCHAIN
def test_string_array_garbage_collection(tmp_path):
    """6000 concatenations into 20 elements fill the pool many times over."""
    check_same(tmp_path, """10 DIM W$(20)
20 FOR I=1 TO 6000
30 J=I MOD 20
40 W$(J)=STR$(I)+"abc"+W$((J+7) MOD 20)
50 IF LEN(W$(J))>60 THEN W$(J)=LEFT$(W$(J),30)
60 A$=A$+"x": IF LEN(A$)>100 THEN A$=MID$(A$,50)
70 NEXT I
80 FOR J=0 TO 19: PRINT J;W$(J): NEXT J
90 PRINT LEN(A$)
""")


@NEEDS_TOOLCHAIN
def test_option_base_and_undimensioned_arrays(tmp_path):
    check_same(tmp_path, """10 OPTION BASE 1
20 DIM W$(3), T(2,2)
30 W$(1)="one": W$(3)="three"
40 T(1,1)=11: T(2,2)=22: T(1,2)=12
50 PRINT W$(1);W$(3);T(1,1);T(1,2);T(2,2)
60 C$(10)="ten": C$(1)="one"
70 PRINT C$(10);C$(1);LEN(C$(5))
80 A=5: A(2)=7: PRINT A;A(2)
90 END
""")


@NEEDS_TOOLCHAIN
def test_strings_in_expressions(tmp_path):
    check_same(tmp_path, """10 A$="hello": B$="world"
20 PRINT A$+" "+B$;LEN(A$+B$)
30 PRINT LEFT$(A$,2);RIGHT$(A$,2);MID$(A$,2,3);MID$(A$,4)
40 PRINT HEX$(255);OCT$(8);HEX$(-1);ASC("A");VAL("12.5");VAL(" 7abc")
50 PRINT INSTR("hello","ll");INSTR(3,"hello","l");INSTR("abc","z");CHR$(72);CHR$(105)
60 PRINT SPACE$(3);"|";STRING$(3,"*");STRING$(2,65)
70 SWAP A$,B$: PRINT A$;B$
80 MID$(A$,1,1)="W": PRINT A$
90 IF A$>B$ THEN PRINT "gt" ELSE PRINT "le"
100 END
""")


@NEEDS_TOOLCHAIN
def test_input_numbers_and_strings(tmp_path):
    check_same(tmp_path, """10 INPUT "Name";N$
20 INPUT "Age";A%
30 INPUT X
40 INPUT "two";P$,Q$
50 PRINT N$;A%;X;P$;Q$
60 END
""", "Ann\n41\n2.5\nu,v\n")


@NEEDS_TOOLCHAIN
def test_numeric_arrays(tmp_path):
    """Two subscripts, OPTION BASE 1, no DIM, and a variable that shares its name."""
    check_same(tmp_path, """10 OPTION BASE 1
20 DIM T(2,3), M%(3)
30 FOR I=1 TO 2: FOR J=1 TO 3: T(I,J)=I*10+J: NEXT J,I
40 PRINT T(1,1);T(2,3);T(1,3);T(2,1)
50 M%(1)=7: M%(3)=M%(1)*3: PRINT M%(1);M%(3)
60 C(10)=2.5: C(1)=-1: PRINT C(10);C(1);C(5)
70 A=5: A(2)=7: PRINT A;A(2)
80 I=2: PRINT T(I,I+1);T(I-1,I)
90 SWAP T(1,1),T(2,2): PRINT T(1,1);T(2,2)
100 ERASE T: PRINT T(1,1);T(2,3)
110 END
""")


@NEEDS_TOOLCHAIN
def test_sequential_file_round_trip(tmp_path):
    check_same(tmp_path, """10 OPEN "O",#1,"TEST.DAT"
20 PRINT #1,"hello";1.5;"x"
30 WRITE #1,"a",2,"b"
40 CLOSE #1
50 OPEN "I",#1,"TEST.DAT"
60 LINE INPUT #1,A$
70 PRINT A$
80 INPUT #1,B$,C,D$
90 PRINT B$;C;D$
100 PRINT EOF(1)
110 CLOSE #1
120 KILL "TEST.DAT"
130 END
""")


@NEEDS_TOOLCHAIN
def test_negative_floats_compare_correctly(tmp_path):
    """uc80 compared two negative floats the wrong way round; FOR hung on it."""
    check_same(tmp_path, """10 FOR X=-30 TO -27 STEP 1.5: PRINT X;: NEXT X: PRINT
20 A=-30: B=-27: PRINT A<B;A>B;A<=B;A>=B;A=B;A<>B
30 IF -1.5 > -2.5 THEN PRINT "ok" ELSE PRINT "wrong"
40 FOR I=1 TO 3: Z=INT(25+I*8-.7*I): PRINT 8*I;Z;: NEXT I: PRINT
50 PRINT 3^8;SQR(9);SQR(144)
""")


@NEEDS_TOOLCHAIN
def test_strings_with_backslash_and_near(tmp_path):
    """uc80 drops the word near and halves backslashes in string literals."""
    check_same(tmp_path, '10 PRINT "10 \\ 3 =";10\\3;"(a near b)";"nearly";"x\\\\y"\n'
                         '20 A$="near": PRINT A$;"\\";CHR$(92);"z"\n')


@NEEDS_TOOLCHAIN
def test_on_index_rounds_and_data_numbers_skip_blanks(tmp_path):
    """ON 1.5 GOTO takes the second line and ON 2.5 falls through; READ of DATA 1 2
    is 12 and &H10 is 16 (measured on MBASIC 5.21; the C backend truncated and
    stopped at the blank)."""
    source = ('10 ON 1.5 GOTO 20,30\n20 PRINT "a":GOTO 40\n30 PRINT "b"\n'
              '40 ON 2.5 GOSUB 60,70:PRINT "f"\n50 READ A,B%,C:PRINT A;B%;C:GOTO 80\n'
              '60 PRINT "s1":RETURN\n70 PRINT "s2":RETURN\n80 DATA 1 2,3 4,&H10\n90 SYSTEM\n')
    assert compile_c(tmp_path, source).returncode == 0
    assert run_compiled(tmp_path, "") == "b\nf\n 12  34  16 \n"


@NEEDS_TOOLCHAIN
def test_on_gosub_and_if_else_line(tmp_path):
    check_same(tmp_path, """10 FOR I=1 TO 3
20 ON I GOSUB 100,200,300
30 NEXT I
40 N=3
50 IF N>2 THEN PRINT "big"; ELSE 70
60 PRINT " end": END
70 PRINT "small"
100 PRINT "one": RETURN
200 PRINT "two": RETURN
300 PRINT "three": IF I=3 THEN GOSUB 400
310 RETURN
400 PRINT "nested": RETURN
""")


@NEEDS_TOOLCHAIN
def test_subscript_out_of_range_stops_the_program(tmp_path):
    source = '10 DIM A$(2)\n20 PRINT "before"\n30 A$(3)="x"\n40 PRINT "after"\n'
    assert compile_c(tmp_path, source).returncode == 0
    # CP/M has one console, so the error message arrives on the same stream
    assert run_compiled(tmp_path, "") == "before\nSubscript out of range in 30\n"


@NEEDS_TOOLCHAIN
def test_runtime_errors_name_the_line_and_start_a_new_line(tmp_path):
    """MBASIC starts a new line when the cursor is not in column 1, then says
    ?message in LINE.  A negative subscript is Illegal function call."""
    source = '10 DIM A$(5)\n20 PRINT "x";\n30 GOSUB 100: A$(-1)="z"\n40 END\n100 RETURN\n'
    assert compile_c(tmp_path, source).returncode == 0
    assert run_compiled(tmp_path, "") == "x\nIllegal function call in 30\n"


@NEEDS_TOOLCHAIN
def test_string_too_long_stops_the_program(tmp_path):
    source = ('10 A$=STRING$(200,"a")\n20 PRINT "go"\n30 B$=A$+A$\n40 PRINT LEN(B$)\n'
              '50 A=LEN(A$+A$+"x")\n')
    assert compile_c(tmp_path, source).returncode == 0
    assert run_compiled(tmp_path, "") == "go\nString too long in 30\n"


@NEEDS_TOOLCHAIN
def test_string_too_long_in_an_expression(tmp_path):
    source = '10 A$=STRING$(200,"a")\n20 PRINT LEN(A$+A$+"x")\n'
    assert compile_c(tmp_path, source).returncode == 0
    assert run_compiled(tmp_path, "") == "String too long in 20\n"


@NEEDS_TOOLCHAIN
def test_bare_close_after_open(tmp_path):
    """A bare CLOSE walked off the end of the file tables and hung."""
    source = ('10 OPEN "O",#1,"T.DAT":PRINT #1,"A":CLOSE\n'
              '20 OPEN "I",#1,"T.DAT":INPUT #1,Q$:CLOSE\n30 PRINT "after";Q$\n')
    assert compile_c(tmp_path, source).returncode == 0
    assert run_compiled(tmp_path, "") == "afterA\n"


@NEEDS_TOOLCHAIN
def test_bare_close_without_open_links(tmp_path):
    assert compile_c(tmp_path, '10 CLOSE\n20 PRINT "ok"\n').returncode == 0
    assert run_compiled(tmp_path, "") == "ok\n"


# --- Nothing compiles to wrong code silently ---------------------------------

def test_unsupported_construct_is_a_compile_error(tmp_path):
    """INKEY$ cannot be compiled; the compiler says so and writes no C."""
    result = compile_c(tmp_path, '10 A$=INKEY$\n20 PRINT A$\n')
    assert result.returncode == 1
    assert "Cannot compile to C" in result.stderr
    assert "INKEY$" in result.stderr
    assert not (tmp_path / "prog.c").exists()


def test_error_names_the_line(tmp_path):
    result = compile_c(tmp_path, '10 PRINT 1\n20 TRON\n30 PRINT 2\n')
    assert result.returncode == 1
    assert "line 20" in result.stderr


def test_a_string_in_a_number_is_a_compile_error(tmp_path):
    result = compile_c(tmp_path, '10 A$="x"\n20 X=A$\n')
    assert result.returncode == 1
    assert "Type mismatch" in result.stderr


def test_warnings_are_shown(tmp_path):
    """Advice from the backend reaches the user (it was thrown away before).

    The warning is printed before the toolchain runs, so this needs no toolchain.
    """
    result = compile_c(tmp_path, '10 WIDTH 40\n20 PRINT 1\n')
    assert "Warning: WIDTH" in result.stderr


@pytest.mark.skipif(shutil.which("cc") is None, reason="a host C compiler is needed")
def test_runtime_number_formatter_matches_number_format(tmp_path):
    """mb25_fmt_num() against number_format.format_number(), on the host.

    This needs no Z80 toolchain: the formatter is plain C.
    """
    import random
    from src.number_format import format_number, to_single

    driver = tmp_path / "fmt.c"
    driver.write_text('''#include "mb25_string.h"
#include <stdio.h>
#include <stdlib.h>
int main(int argc, char **argv) {
    char buf[64];
    int i;
    for (i = 1; i < argc; i++) {
        float f = (float)atof(argv[i]);
        mb25_fmt_num(buf, (double)f, 0);
        printf("%s\\n", buf);
    }
    return 0;
}
''')
    exe = tmp_path / "fmt"
    runtime = ROOT / "runtime" / "strings"
    build = subprocess.run(["cc", "-I", str(runtime), "-o", str(exe), str(driver),
                            str(runtime / "mb25_string.c"), "-lm"],
                           capture_output=True, text=True, timeout=120)
    assert build.returncode == 0, build.stderr

    rng = random.Random(7)
    values = [0.1, 1 / 3, 8.7, 999999.0, 1000000.0, 1e-7, 1e-8, 0.00012345, 123456.5,
              16777216.0, 1e38, 1e-38, 99999.95, 0.999999, 0.9999995, 9.999995, -3.0, 0.0]
    for _ in range(400):
        kind = rng.random()
        if kind < 0.4:
            values.append(rng.uniform(-1000, 1000))
        elif kind < 0.7:
            values.append(rng.choice([1, -1]) * 10 ** rng.uniform(-12, 12))
        elif kind < 0.85:
            values.append(float(rng.randint(-2000000, 2000000)))
        else:
            values.append(rng.choice([1, -1]) * 10 ** rng.uniform(-37, 37))
    result = subprocess.run([str(exe)] + [repr(v) for v in values],
                            capture_output=True, text=True, timeout=60)
    got = result.stdout.split("\n")
    for value, text in zip(values, got):
        assert text == format_number(to_single(value), 6), value


def test_generated_c_formats_numbers_in_the_runtime(tmp_path):
    from src.lexer import Lexer
    from src.parser import Parser
    from src.semantic_analyzer import SemanticAnalyzer
    from src.codegen_backend import Z88dkCBackend
    ast = Parser(Lexer('10 PRINT -3;1/3;8.7\n').tokenize()).parse()
    analyzer = SemanticAnalyzer()
    assert analyzer.analyze(ast)
    backend = Z88dkCBackend(analyzer.symbols, {"dialect": "uc80"})
    code = backend.generate(ast)
    assert "printf" not in code.replace("fprintf", "")
    assert "mb25_print_num" in code
    assert not backend.errors


def test_error_handling_compiles_to_c(tmp_path):
    """ON ERROR GOTO, RESUME, ERROR, ERR and ERL compile (they used to be refused).

    What they do is checked against the binary in test_c_backend_on_error_using.py.
    """
    from src.lexer import Lexer
    from src.parser import Parser
    from src.semantic_analyzer import SemanticAnalyzer
    from src.codegen_backend import Z88dkCBackend
    for source in ('10 ON ERROR GOTO 100\n20 END\n100 RESUME NEXT\n',
                   '10 PRINT ERR\n', '10 PRINT ERL\n', '10 ERROR 5\n',
                   '10 ON ERROR GOTO 100\n20 A=1/0\n30 END\n100 PRINT ERR;ERL:RESUME NEXT\n',
                   '10 PRINT USING "##.##";3.14159\n'):
        ast = Parser(Lexer(source).tokenize()).parse()
        analyzer = SemanticAnalyzer()
        assert analyzer.analyze(ast), source
        backend = Z88dkCBackend(analyzer.symbols, {"dialect": "uc80"})
        backend.generate(ast)
        assert not backend.errors, (source, backend.errors)


def test_on_error_goto_0_still_compiles_to_c(tmp_path):
    """ON ERROR GOTO 0 only switches handling off; the backend accepts it."""
    from src.lexer import Lexer
    from src.parser import Parser
    from src.semantic_analyzer import SemanticAnalyzer
    from src.codegen_backend import Z88dkCBackend
    ast = Parser(Lexer('10 ON ERROR GOTO 0\n20 PRINT 1\n').tokenize()).parse()
    analyzer = SemanticAnalyzer()
    assert analyzer.analyze(ast)
    backend = Z88dkCBackend(analyzer.symbols, {"dialect": "uc80"})
    backend.generate(ast)
    assert not backend.errors


def test_integer_overflow_warning(tmp_path):
    result = compile_c(tmp_path, '80 I%=1000:PRINT I%*I%\n')
    assert "wraps at 16 bits" in result.stderr
    assert "line 80" in result.stderr
    # a sum of constants is worked out by the compiler: no warning
    result = compile_c(tmp_path, '10 PRINT 200*200\n20 X=1.5*2\n')
    assert "wraps at 16 bits" not in result.stderr


# --- Review round 2 ----------------------------------------------------------

@NEEDS_TOOLCHAIN
def test_for_loop_with_a_variable_start_ends(tmp_path):
    """uc80's AST optimizer read the wrong variable after K=J, so FOR K=J TO 3
    never ended.  The backend passes --no-ast-optimize."""
    check_same(tmp_path, """10 I=1: N=6
20 J=I: PRINT J
30 FOR K=J TO 3: PRINT K;: NEXT K: PRINT
40 FOR I=0 TO 2: FOR J=I TO 2: PRINT I;J;: NEXT J: NEXT I: PRINT
50 FOR K=N TO 8: PRINT K;: NEXT K: PRINT
""")


@NEEDS_TOOLCHAIN
def test_sort_with_next_j_i(tmp_path):
    check_same(tmp_path, """10 DIM A(5): FOR I=0 TO 5: A(I)=(I*7) MOD 6: NEXT I
20 FOR I=0 TO 4: FOR J=I+1 TO 5
30 IF A(J)<A(I) THEN T=A(I): A(I)=A(J): A(J)=T
40 NEXT J,I
50 FOR I=0 TO 5: PRINT A(I);: NEXT I: PRINT
""")


@NEEDS_TOOLCHAIN
@pytest.mark.parametrize("source", [
    '10 DIM A$(3)\n20 A$(4)="x"\n',
    '10 OPTION BASE 1\n20 DIM A$(2)\n30 A$(1)="a": PRINT A$(1)\n40 A$(0)="z"\n',
    '10 RETURN\n',
    '10 READ A\n',
])
def test_runtime_error_text_matches_the_interpreter(tmp_path, source):
    """No ? in front, and OPTION BASE 1 with subscript 0 is out of range."""
    check_same(tmp_path, source)


@NEEDS_TOOLCHAIN
def test_int_and_fix_of_large_numbers(tmp_path):
    check_same(tmp_path, '10 PRINT INT(2.7E9);FIX(-2.7E9);INT(-2.5);FIX(-2.5);INT(3E10)\n')


def test_literal_outside_the_float_range_warns(tmp_path):
    result = compile_c(tmp_path, '10 PRINT 3E38\n')
    assert "range of a uc80 float" in result.stderr


@NEEDS_TOOLCHAIN
def test_negative_subscript_is_illegal_function_call(tmp_path):
    """Real MBASIC 5.21 says Illegal function call (the interpreter says
    Subscript out of range, so this does not compare with the interpreter)."""
    source = '10 DIM A$(3)\n20 PRINT "abc";\n30 A$(-1)="x"\n'
    assert compile_c(tmp_path, source).returncode == 0
    assert run_compiled(tmp_path, "") == "abc\nIllegal function call in 30\n"
    source = '10 OPTION BASE 1\n20 DIM A$(2)\n30 A$(-1)="z"\n'
    assert compile_c(tmp_path, source).returncode == 0
    assert run_compiled(tmp_path, "") == "Illegal function call in 30\n"


@NEEDS_TOOLCHAIN
def test_append_to_shared_and_self_concat(tmp_path):
    """Real MBASIC 5.21 prints ab|abx, xyxy, aaq, aq, aqaq."""
    source = ('10 DIM S$(3)\n20 S$(1)="ab":S$(2)=S$(1):S$(1)=S$(1)+"x":PRINT S$(2);"|";S$(1)\n'
              '30 S$(3)="xy":S$(3)=S$(3)+S$(3):PRINT S$(3)\n'
              '40 A$="a":B$=A$:A$=A$+"q":PRINT B$;A$:C$=A$:PRINT C$:A$=A$+A$:PRINT A$\n')
    assert compile_c(tmp_path, source).returncode == 0
    assert run_compiled(tmp_path, "") == "ab|abx\nxyxy\naaq\naq\naqaq\n"
