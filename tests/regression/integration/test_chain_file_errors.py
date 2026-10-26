"""CHAIN and CHAIN MERGE of a file that MBASIC 5.21 stops reading (issues 34, 35, 36),
and LOAD/MERGE in the curses and Tk backends returning True on such a file.

Measured on com/mbasic.com under cpmemu (program: 10 PRINT "s", then a CHAIN
statement; RUN, then LIST):

- CHAIN "za" for za = 10 PRINT "A" / a line with no number / 20 PRINT "B":
  prints s, then "Direct statement in file", then Ok. LIST shows 10 only.
  Nothing of the chained program runs.
- CHAIN "zl" for a file with a 300 byte first line: s, "Line buffer overflow
  in 10", Ok. LIST shows nothing (the old program is gone).
- CHAIN MERGE "zb" for zb = 10 PRINT "A" / 20 GOTO 30 / 30 / 40 PRINT "B":
  s, "Undefined line number", Ok. LIST shows 10 and 20 of the file (the lines
  merged before the bad line stay). Ours used to print A and loop.
- CHAIN MERGE "za": "Direct statement in file"; LIST shows 10 PRINT "A" and the
  CHAIN line 20.
- CHAIN MERGE "zl": "Line buffer overflow in 10"; LIST shows the old 10 and 20.
- The message is bare and the program stops: nothing after the CHAIN runs.
"""
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: CHAIN file error tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

FILES = {
    "za": ['10 PRINT "A"', 'PRINT "X"', '20 PRINT "B"'],
    "zl": ["10 REM " + "X" * 300, '20 PRINT "hi"'],
    "zb": ['10 PRINT "A"', "20 GOTO 30", "30", '40 PRINT "B"'],
}

# (chain statement, bad file, real message, lines LIST shows afterwards)
CASES = [
    ('CHAIN "za.bas"', "za", "Direct statement in file", [10]),
    ('CHAIN "zl.bas"', "zl", "Line buffer overflow in 10", []),
    ('CHAIN MERGE "zb.bas"', "zb", "Undefined line number", [10, 20]),
    ('CHAIN MERGE "za.bas"', "za", "Direct statement in file", [10, 20]),
    ('CHAIN MERGE "zl.bas"', "zl", "Line buffer overflow in 10", [10, 20]),
]


def listed(output):
    return [int(row.split()[0]) for row in output.splitlines()
            if row[:1].isdigit()]


@pytest.mark.parametrize("statement,name,message,kept", CASES)
def test_chain_stops_at_the_bad_line(tmp_path, statement, name, message, kept):
    for file_name, lines in FILES.items():
        (tmp_path / (file_name + ".bas")).write_bytes(
            "".join(line + "\r\n" for line in lines).encode())
    (tmp_path / "main.bas").write_bytes(
        ('10 PRINT "s"\r\n20 ' + statement + '\r\n').encode())
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), "--ui", "cli"],
        input='LOAD "main.bas"\nRUN\nLIST\nSYSTEM\n', cwd=tmp_path,
        capture_output=True, text=True, timeout=60)
    out = result.stdout
    assert out.count(message + "\n") == 1, out + result.stderr
    assert "\nA\n" not in out and "\nB\n" not in out
    after_run = out[out.index(message):]
    assert listed(after_run) == kept


def _stub_urwid():
    return mock.patch.dict(sys.modules, {"urwid": mock.MagicMock()})


def _bad_file(tmp_path):
    path = tmp_path / "bad.bas"
    path.write_bytes(b'10 PRINT "A"\r\nPRINT "X"\r\n')
    return str(path)


def _backend(output):
    from src.editing.manager import ProgramManager
    backend = SimpleNamespace(program=ProgramManager({}), output=output)
    backend._add_output = output.append
    backend._append_to_output = output.append
    backend._refresh_editor = lambda: None
    backend._validate_editor_syntax = lambda: None
    backend._set_status = lambda text: None
    backend._update_output = lambda: None
    backend._sync_program_to_editor = lambda: None
    backend.output_buffer = output
    return backend


def test_tk_load_and_merge_return_true_on_a_read_abort(tmp_path):
    tk_ui = pytest.importorskip("src.ui.tk_ui")
    backend = _backend([])
    path = _bad_file(tmp_path)
    assert tk_ui.TkBackend.cmd_load(backend, path, from_program=True) is True
    assert any("Direct statement in file" in text for text in backend.output)
    assert backend.program.get_lines() == [(10, '10 PRINT "A"')]
    backend.output.clear()
    assert tk_ui.TkBackend.cmd_merge(backend, path, quiet=True, from_program=True) is True
    assert any("Direct statement in file" in text for text in backend.output)


def test_curses_load_and_merge_return_true_on_a_read_abort(tmp_path):
    with _stub_urwid():
        sys.modules.pop("src.ui.curses_ui", None)
        curses_ui = pytest.importorskip("src.ui.curses_ui")
        backend = _backend([])
        backend._load_program_file = lambda name, from_program=False: \
            curses_ui.CursesBackend._load_program_file(backend, name, from_program)
        path = _bad_file(tmp_path)
        assert curses_ui.CursesBackend.cmd_load(backend, path, from_program=True) is True
        assert backend.output == ["Direct statement in file"]
        backend.output.clear()
        assert curses_ui.CursesBackend.cmd_merge(
            backend, path, quiet=True, from_program=True) is True
        assert backend.output == ["Direct statement in file"]
    sys.modules.pop("src.ui.curses_ui", None)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
