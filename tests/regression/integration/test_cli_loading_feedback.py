"""Regressions for numbered source loading and CLI startup feedback."""
import subprocess
import sys
from pathlib import Path

import pytest

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


def test_startup_reports_loaded_file_and_prompt(tmp_path):
    source = tmp_path / "hello world.bas"
    source.write_text('10PRINT "executed"\n20END\n')
    result = cli(source, commands="RUN\nSYSTEM\n")
    assert result.returncode == 0, result.stderr
    assert f"Loaded from {source}" in result.stdout
    assert "Type RUN to execute" in result.stdout
    assert "MBASIC> " in result.stdout
    assert "executed" in result.stdout


def test_empty_startup_has_prompt_without_loaded_notice():
    result = cli()
    assert result.returncode == 0, result.stderr
    assert "MBASIC> " in result.stdout
    assert "Loaded from" not in result.stdout


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


def test_missing_startup_file_is_reported_separately(tmp_path):
    source = tmp_path / "missing.bas"
    result = cli(source)
    assert result.returncode != 0
    assert f"File not found: {source}" in result.stderr


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q", "-p", "no:cacheprovider"]))
