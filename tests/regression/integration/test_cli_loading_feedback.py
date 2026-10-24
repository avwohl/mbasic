"""Regressions for numbered source loading and CLI startup feedback."""
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: CLI loading feedback tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

try:
    import pexpect
except ImportError:
    pexpect = None

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.editing.manager import ProgramManager


def cli(*args, commands="SYSTEM\n"):
    return subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), *map(str, args), "--ui", "cli"],
        input=commands, text=True, capture_output=True, cwd=ROOT, timeout=30,
    )


@pytest.mark.parametrize("operation", ["load_from_file", "merge_from_file"])
def test_compact_numbered_source(tmp_path, operation):
    source = tmp_path / "compact.bas"
    source.write_text('10PRINT "hello"\n20END\n')
    program = ProgramManager({})
    result = getattr(program, operation)(str(source))
    assert result[:2] == (True, [])
    assert sorted(program.lines) == [10, 20]
    assert len(program.line_asts) == 2


def test_piped_startup_has_no_prompt_or_banner(tmp_path):
    source = tmp_path / "hello world.bas"
    source.write_text('10PRINT "executed"\n20END\n')
    result = cli(source, commands="RUN\nSYSTEM\n")
    assert result.returncode == 0, result.stderr
    assert "MBASIC> " not in result.stdout
    assert "Loaded from" not in result.stdout
    assert "Type RUN to execute" not in result.stdout
    assert "executed" in result.stdout


def test_piped_empty_startup_has_no_prompt():
    result = cli()
    assert result.returncode == 0, result.stderr
    assert "MBASIC> " not in result.stdout
    assert "Loaded from" not in result.stdout


@pytest.mark.skipif(pexpect is None, reason="pexpect is needed for pty tests")
def test_tty_startup_shows_banner_and_prompt(tmp_path):
    source = tmp_path / "hello.bas"
    source.write_text('10PRINT "executed"\n20END\n')
    child = pexpect.spawn(sys.executable, ["mbasic", "--ui", "cli", str(source)],
                          cwd=str(ROOT), encoding="utf-8", timeout=20)
    try:
        child.expect("MBASIC> ")
        assert f"Loaded from {source}" in child.before
        assert "Type RUN to execute" in child.before
        child.sendline("RUN")
        child.expect("executed")
        child.expect("MBASIC> ")
        child.sendline("SYSTEM")
        child.expect(pexpect.EOF)
    finally:
        child.close()


@pytest.mark.skipif(pexpect is None, reason="pexpect is needed for pty tests")
def test_tty_edit_key_still_enters_edit_mode_with_prompt(tmp_path):
    source = tmp_path / "edit.bas"
    source.write_text('10PRINT "A"\n')
    child = pexpect.spawn(sys.executable, ["mbasic", "--ui", "cli", str(source)],
                          cwd=str(ROOT), encoding="utf-8", timeout=20)
    try:
        child.expect("MBASIC> ")
        child.send("\x01")    # the default edit key, ^A
        child.send("\r")
        child.expect("10")     # EDIT prints the line number, then reads subcommands
        child.send("L")        # L lists the rest of the line
        child.expect("PRINT")
        child.send("Q")
        child.expect("MBASIC> ")
        child.sendline("SYSTEM")
        child.expect(pexpect.EOF)
    finally:
        child.close()


@pytest.mark.parametrize("text", ["\n", "PRINT 1\n", "10 PRINT (\n"])
def test_failed_startup_explains_reason(tmp_path, text):
    source = tmp_path / "bad.bas"
    source.write_text(text)
    result = cli(source)
    assert result.returncode != 0
    assert str(source) in result.stderr
    if text.strip():
        assert "file line 1" in result.stderr
    else:
        assert "No numbered program lines" in result.stderr


def test_load_command_does_not_call_parse_failure_file_not_found(tmp_path):
    source = tmp_path / "bad.bas"
    source.write_text("10 PRINT (\n")
    result = cli(commands=f'LOAD "{source}"\nSYSTEM\n')
    assert "file line 1" in result.stdout
    assert "BASIC line 10" in result.stdout
    assert "File not found" not in result.stdout


def test_mandelbrot_fixture_runs_with_compact_line_numbers(tmp_path):
    import re
    source = tmp_path / "mand.bas"
    original = (Path(__file__).parent / "fixtures" / "mand.bas").read_text()
    source.write_text(re.sub(r"(?m)^(\d+) +", r"\1", original))
    result = cli(source, commands="RUN\nSYSTEM\n")
    assert result.returncode == 0, result.stderr
    assert not result.stderr
    rows = [line for line in result.stdout.splitlines()
            if len(line) == 79 and set(line) <= set(".,'~=+:;*%&$OXB#@ ")]
    assert len(rows) == 25
    assert rows == rows[::-1]
    assert "Finished" in result.stdout


@pytest.mark.parametrize("operation", ["load_from_file", "merge_from_file"])
def test_partial_load_reports_each_rejected_physical_line(tmp_path, operation):
    source = tmp_path / "partial.bas"
    source.write_text('\n10PRINT "kept"\nnot numbered\n20 PRINT (\n30END\n')
    program = ProgramManager({})
    result = getattr(program, operation)(str(source))
    assert result[0] is True
    assert sorted(program.lines) == [10, 30]
    assert len(result[1]) == 2
    assert "file line 3" in result[1][0][1]
    assert "expected a BASIC line number" in result[1][0][1]
    assert "file line 4, BASIC line 20" in result[1][1][1]


@pytest.mark.parametrize("operation", ["load_from_file", "merge_from_file"])
@pytest.mark.parametrize("bare", ["20", "20 "])
def test_bare_line_number_deletes_line(tmp_path, operation, bare):
    source = tmp_path / "bare.bas"
    source.write_text(f'10 PRINT "a"\n20 PRINT "b"\n{bare}\n30 PRINT "c"\n99\n')
    program = ProgramManager({})
    if operation == "merge_from_file":
        program.add_line(20, '20 PRINT "old"')
    result = getattr(program, operation)(str(source))
    assert result[0] is True
    assert result[1] == []
    assert sorted(program.lines) == [10, 30]
    assert sorted(program.line_asts) == [10, 30]


def test_missing_startup_file_is_reported_separately(tmp_path):
    source = tmp_path / "missing.bas"
    result = cli(source)
    assert result.returncode != 0
    assert f"File not found: {source}" in result.stderr


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q", "-p", "no:cacheprovider"]))


@pytest.mark.parametrize("operation", ["load", "merge"])
def test_file_of_only_bare_line_numbers_succeeds(tmp_path, operation):
    from src.editing.manager import ProgramManager
    import inspect
    source = tmp_path / "onlybare.bas"
    source.write_text("10\n20\n")
    manager = _make_manager() if "_make_manager" in globals() else None
    assert manager is not None
