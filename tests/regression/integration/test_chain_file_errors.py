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


def _run_cli(tmp_path, main_lines, files, commands, timeout=20):
    for file_name, lines in files.items():
        (tmp_path / file_name).write_bytes(
            "".join(line + "\r\n" for line in lines).encode())
    (tmp_path / "main.bas").write_bytes(
        "".join(line + "\r\n" for line in main_lines).encode())
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), "--ui", "cli"],
        input='LOAD "main.bas"\nRUN\n' + commands + "SYSTEM\n", cwd=tmp_path,
        capture_output=True, text=True, timeout=timeout)
    return result.stdout


def test_aborted_chain_clears_variables_and_blocks_cont(tmp_path):
    """Measured on the binary: main = 5 A=3 / 10 PRINT "s" / 20 CHAIN "za.bas";
    RUN, PRINT A, CONT gives s, Direct statement in file, Ok, " 0 ", Ok,
    Can't continue, Ok."""
    out = _run_cli(tmp_path, ["5 A=3", '10 PRINT "s"', '20 CHAIN "za.bas"'],
                   {"za.bas": FILES["za"]}, "PRINT A\nCONT\n")
    after = out[out.index("Direct statement in file"):]
    assert " 0 " in after and " 3 " not in after
    assert "Can't continue" in after


def test_chain_start_line(tmp_path):
    """Measured: CHAIN "g.bas",20 with g = 10 PRINT "G10" / 20 PRINT "G20"
    prints s, G20 (not G10). A start line the file lacks (25) prints a bare
    Undefined line number and the file stays loaded."""
    files = {"g.bas": ['10 PRINT "G10"', '20 PRINT "G20"']}
    out = _run_cli(tmp_path, ['10 PRINT "s"', '20 CHAIN "g.bas",20'], files, "")
    assert "G20" in out and "G10" not in out
    out = _run_cli(tmp_path, ['10 PRINT "s"', '20 CHAIN "g.bas",25'], files, "LIST\n")
    assert out.count("Undefined line number\n") == 1
    assert '10 PRINT "G10"' in out


def test_chain_merge_with_delete_range(tmp_path):
    """Measured: main = 10 PRINT "s" / 20 CHAIN MERGE "h.bas",200,DELETE 100-110
    / 100 PRINT "o100" / 110 PRINT "o110", h = 200 PRINT "G200" / 210 END:
    prints s, G200 and stops; LIST shows 10, 20, 200, 210."""
    out = _run_cli(
        tmp_path,
        ['10 PRINT "s"', '20 CHAIN MERGE "h.bas",200,DELETE 100-110',
         '100 PRINT "o100"', '110 PRINT "o110"'],
        {"h.bas": ['200 PRINT "G200"', "210 END"]}, "LIST\n")
    assert out.count("\ns\n") == 1 and "G200\n" in out
    assert listed(out[out.index("G200"):]) == [10, 20, 200, 210]


def test_chain_merge_of_a_missing_file_deletes_nothing(tmp_path):
    """Measured: 10 PRINT "s" / 20 ON ERROR GOTO 100 / 30 CHAIN MERGE
    "noexist.bas",,DELETE 10-20 / 40 END / 100 PRINT "err";ERR:RESUME 40 prints
    s, "err 53 "; LIST still shows 10, 20, 30, 40, 100 (MBASIC opens the file
    before it deletes)."""
    out = _run_cli(
        tmp_path,
        ['10 PRINT "s"', "20 ON ERROR GOTO 100",
         '30 CHAIN MERGE "noexist.bas",,DELETE 10-20', "40 END",
         '100 PRINT "err";ERR:RESUME 40'], {}, "LIST\n")
    assert "err 53 \n" in out
    assert listed(out[out.index("err 53"):]) == [10, 20, 30, 40, 100]


def test_chain_merge_delete_with_a_missing_end_line(tmp_path):
    """Measured: lines 5, 10, 20, 40 CHAIN MERGE "zb3.bas",60,ALL,DELETE 10-15,
    50 prints s, t, "Illegal function call in 40"; LIST keeps 5, 10, 20, 40, 50.
    DELETE 10-20 with line 20 absent gives the same."""
    out = _run_cli(
        tmp_path,
        ["5 A=7", '10 PRINT "s"', '20 PRINT "t"',
         '40 CHAIN MERGE "zb3.bas",60,ALL,DELETE 10-15', "50 END"],
        {"zb3.bas": ['60 PRINT "N";A', "70 END"]}, "LIST\n")
    assert "Illegal function call in 40\n" in out
    assert "N 7" not in out
    assert listed(out[out.index("Illegal function"):]) == [5, 10, 20, 40, 50]


def test_chain_merge_clears_variables_without_all(tmp_path):
    """Measured: 5 A=7 / 40 CHAIN MERGE "zb3.bas",60 (zb3 = 60 PRINT "N";A /
    70 END) prints "N 0 " and then PRINT A gives " 0 ". With ALL it prints
    "N 7 "."""
    files = {"zb3.bas": ['60 PRINT "N";A', "70 END"]}
    out = _run_cli(tmp_path, ["5 A=7", '40 CHAIN MERGE "zb3.bas",60', "50 END"],
                   files, "PRINT A\n")
    assert "N 0 \n" in out and "N 7" not in out
    out = _run_cli(tmp_path, ["5 A=7", '40 CHAIN MERGE "zb3.bas",60,ALL', "50 END"],
                   files, "")
    assert "N 7 \n" in out


def _chain_backend(lines):
    from src.editing.manager import ProgramManager
    from src.runtime import Runtime
    program = ProgramManager({})
    for number, text in lines:
        program.add_line(number, text)
    backend = SimpleNamespace(program=program, runtime=Runtime({}, {}), runs=[])
    backend.cmd_run = lambda start=None: backend.runs.append(start)
    return backend


def test_chain_helper_for_tk_and_curses_follows_the_binary(tmp_path, monkeypatch):
    """The Tk and curses CHAIN (chain_into_program) obeys the measurements above:
    a missing end line of DELETE is an Illegal function call that deletes
    nothing, a missing file changes nothing, a bad file line returns True."""
    from src.ui.ui_helpers import chain_into_program
    monkeypatch.chdir(tmp_path)
    (tmp_path / "zb3.bas").write_bytes(b'60 PRINT "N"\r\n70 END\r\n')
    (tmp_path / "za.bas").write_bytes(b'10 PRINT "A"\r\nPRINT "X"\r\n')
    backend = _chain_backend([(5, '5 A=7'), (10, '10 PRINT "s"'), (40, '40 END')])
    out = []
    args = (backend, backend.program)
    with pytest.raises(ValueError, match="Illegal function call"):
        chain_into_program(*args, "zb3.bas", 60, True, True, (10, 15), out.append, lambda: None)
    assert sorted(backend.program.lines) == [5, 10, 40]
    with pytest.raises(RuntimeError, match="File not found"):
        chain_into_program(*args, "none.bas", None, True, True, (5, 10), out.append, lambda: None)
    assert sorted(backend.program.lines) == [5, 10, 40]
    assert chain_into_program(*args, "za", None, False, False, None, out.append, lambda: None) is True
    assert out == ["Direct statement in file"] and backend.runs == []
    assert chain_into_program(*args, "zb3", None, True, False, (10, 10), out.append,
                              lambda: None) is None
    assert backend.runs == [None]
