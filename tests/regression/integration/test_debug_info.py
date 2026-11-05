"""--compile-c -g: debug information for the compiled program (docs/dev/DEBUG_INFO.md).

With -g the C backend writes '#line N "prog.bas"' before the C code of each BASIC
line, in the uc80 dialect only, and the build runs uc80 -g, um80 --debug-info and
ul80 --debug-info.  prog.dbg then maps the code to lines of the BASIC file.

The tests that need no toolchain look at the C text.  The tests that build need
uc80, um80, ul80 and the uc80 libraries; they skip without them.  The live test
needs a cpmemu with --gdb and an um80 with udb80 as well.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: debug information tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

# BASIC line number -> physical line of the file, for the program below
SOURCE = """10 REM Debug demo
20 LET A = 5
30 FOR I = 1 TO 3
40 A = A + I
50 PRINT "A ="; A
60 NEXT I
70 GOSUB 100
80 PRINT "Done"
90 END
100 PRINT "In sub"
110 RETURN
"""
PHYSICAL = {int(text.split()[0]): number
            for number, text in enumerate(SOURCE.splitlines(), 1)}


def c_text(dialect, debug_info, name="prog.bas", c_file="prog.c", source=SOURCE):
    """The C text the backend writes for a BASIC program (SOURCE)."""
    from src.lexer import Lexer
    from src.parser import Parser
    from src.semantic_analyzer import SemanticAnalyzer
    from src.codegen_backend import Z88dkCBackend
    tokens = Lexer(source, defer_errors=True).tokenize()
    ast = Parser(tokens, defer_syntax_errors=True).parse()
    analyzer = SemanticAnalyzer()
    assert analyzer.analyze(ast)
    backend = Z88dkCBackend(analyzer.symbols, {
        'source_file': name, 'dialect': dialect, 'array_base': analyzer.array_base,
        'debug_info': debug_info, 'debug_source': name, 'debug_c_file': c_file})
    text = backend.generate(ast)
    assert not backend.errors, backend.errors
    return text


def test_no_line_directives_without_g():
    assert "#line" not in c_text("uc80", False)


def test_z88dk_gets_no_line_directives():
    """z88dk does not read the markers that uc80 writes."""
    assert "#line" not in c_text("z88dk", True)


def test_uc80_gets_a_directive_before_each_c_line_of_a_basic_line():
    lines = c_text("uc80", True).split("\n")
    seen = set()
    for index, line in enumerate(lines):
        m = re.match(r'#line (\d+) "prog.bas"$', line)
        if m:
            seen.add(int(m.group(1)))
    assert seen == set(PHYSICAL.values())
    # Every C line of the program body is under a directive for its BASIC line:
    # the line after "mb25_line = 40u;" belongs to the same BASIC line as that store
    for index, line in enumerate(lines):
        m = re.match(r'\s*mb25_line = (\d+)u;', line)
        if m:
            assert lines[index - 1] == f'#line {PHYSICAL[int(m.group(1))]} "prog.bas"', \
                (index, lines[index - 1:index + 1])


def test_code_after_the_basic_lines_goes_back_to_the_c_file():
    lines = c_text("uc80", True, c_file="out.c").split("\n")
    backs = [i for i, line in enumerate(lines) if line.endswith('"out.c"')]
    assert len(backs) == 1
    # The directive names the line that follows it: line number = index + 2
    assert lines[backs[0]] == f'#line {backs[0] + 2} "out.c"'
    # and nothing of the BASIC lines comes after it
    assert not any(line.startswith('#line') and 'prog.bas' in line
                   for line in lines[backs[0]:])


def test_a_label_before_a_close_brace_still_gets_its_null_statement():
    """A #line directive between 'line_60:' and the '}' that NEXT writes is not
    a statement, so uc80 would reject the label (C17)."""
    source = ("10 FOR I = 1 TO 3\n20 IF I = 2 THEN 40\n30 PRINT I\n40 NEXT I\n50 END\n")
    lines = c_text("uc80", True, source=source).split("\n")
    labels = 0
    for index, line in enumerate(lines):
        if re.match(r'^\s*[A-Za-z_]\w*:\s*$', line):
            following = next(c for c in lines[index + 1:]
                             if c.strip() and not c.startswith('#line'))
            assert not following.lstrip().startswith('}'), (line, following)
            labels += 1
    assert labels > 0


# --- builds ------------------------------------------------------------------

def toolchain_missing():
    for tool in ("uc80", "um80", "ul80"):
        if shutil.which(tool) is None:
            return f"{tool} is needed to build the compiled program"
    from src.mbasic_main import uc80_lib_dir
    if uc80_lib_dir() is None:
        return "uc80's libc.lib is not built (python3 -m uc80.lib.build_libs)"
    return None


NEEDS_TOOLCHAIN = pytest.mark.skipif(toolchain_missing() is not None,
                                     reason=toolchain_missing() or "")


def compile_c(tmp_path, name, *flags):
    (tmp_path / "prog.bas").write_text(SOURCE)
    return subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), "prog.bas", "--compile-c", name] + list(flags),
        cwd=tmp_path, capture_output=True, text=True, timeout=300)


@NEEDS_TOOLCHAIN
def test_g_gives_the_same_program_bytes(tmp_path):
    plain = compile_c(tmp_path, "plain")
    debug = compile_c(tmp_path, "debug", "-g")
    assert plain.returncode == 0, plain.stdout + plain.stderr
    assert debug.returncode == 0, debug.stdout + debug.stderr
    assert (tmp_path / "debug.dbg").exists()
    assert not (tmp_path / "plain.dbg").exists()
    digest = lambda p: hashlib.sha256((tmp_path / p).read_bytes()).hexdigest()  # noqa: E731
    assert digest("plain.com") == digest("debug.com")


@NEEDS_TOOLCHAIN
def test_dbg_rows_name_the_basic_file_and_its_lines(tmp_path):
    result = compile_c(tmp_path, "debug", "-g")
    assert result.returncode == 0, result.stdout + result.stderr
    dbg = json.loads((tmp_path / "debug.dbg").read_text())
    index = [i for i, name in enumerate(dbg["files"]) if os.path.basename(name) == "prog.bas"]
    assert len(index) == 1, dbg["files"]
    lines = {group[1] for row in dbg["lines"] for group in row[2] if group[0] == index[0]}
    # Every BASIC line that has code has a row.  REM (physical line 1) has none.
    assert lines == set(PHYSICAL.values()) - {PHYSICAL[10]}, sorted(lines)


@NEEDS_TOOLCHAIN
def test_live_break_on_a_basic_line(tmp_path):
    cpmemu = os.environ.get("MBASIC_CPMEMU") or shutil.which("cpmemu")
    if cpmemu is None:
        pytest.skip("cpmemu is needed (set MBASIC_CPMEMU)")
    usage = subprocess.run([cpmemu], capture_output=True, text=True)
    if "--gdb" not in usage.stdout + usage.stderr:
        pytest.skip("this cpmemu has no --gdb")
    if subprocess.run([sys.executable, "-c", "import um80.udb80"]).returncode:
        pytest.skip("this um80 has no udb80")
    result = compile_c(tmp_path, "debug", "-g")
    assert result.returncode == 0, result.stdout + result.stderr
    line = PHYSICAL[40]
    run = subprocess.run(
        [sys.executable, "-m", "um80.udb80", "debug.dbg", "--run", f"{cpmemu} debug.com",
         "--batch", "-ex", f"break prog.bas:{line}", "-ex", "continue", "-ex", "list",
         "-ex", "quit"],
        cwd=tmp_path, capture_output=True, text=True, timeout=120)
    out = run.stdout + run.stderr
    assert run.returncode == 0, out
    assert f"Breakpoint 1, _main () at prog.bas:{line}" in out, out
    assert f"{line}\t40 A = A + I" in out, out


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q", "-rs"]))
