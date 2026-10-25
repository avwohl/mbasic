"""RENUM in the Tk UI prints nothing when it works (issue 51).

Measured on MBASIC 5.21: after RENUM the next thing on the screen is Ok.
TkBackend.cmd_renum used to add "Renumbered (10 to 30)" to the output pane.
A reference to a missing line is still reported ("Undefined line n in m").

The backend is built without a display (no __init__): cmd_renum needs only
the program, _refresh_editor and _add_output.
"""
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: Tk RENUM test skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))


def make_backend(text):
    pytest.importorskip("tkinter")
    from src.ui.tk_ui import TkBackend
    from src.editing.manager import ProgramManager

    backend = TkBackend.__new__(TkBackend)
    backend.program = ProgramManager({})
    for line in text.splitlines():
        backend.program.add_line(int(line.split()[0]), line)
    backend.output = []
    backend._add_output = backend.output.append
    backend._refresh_editor = lambda: None
    return backend


def test_renum_prints_nothing():
    backend = make_backend("5 PRINT 1\n7 PRINT 2\n9 GOTO 5")
    backend.cmd_renum("")
    assert backend.output == []
    assert [num for num, _ in backend.program.get_lines()] == [10, 20, 30]


def test_renum_still_reports_an_undefined_line():
    backend = make_backend("5 GOTO 99")
    backend.cmd_renum("")
    assert len(backend.output) == 1 and backend.output[0].startswith("Undefined line 99")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
