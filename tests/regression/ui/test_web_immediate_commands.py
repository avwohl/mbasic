"""Commands typed in the web UI immediate line (issue 50).

On MBASIC 5.21 RENUM, DELETE, LOAD, SAVE, MERGE and FILES typed as direct
commands work, and RENUM and DELETE print nothing when they succeed (measured:
RENUM renumbers the program and the next line is Ok). The web backend had no
cmd_renum, cmd_delete, cmd_load, cmd_save, cmd_merge or cmd_files, and did not
set interpreter.interactive_mode before the first step, so RENUM answered
"Illegal function call".

nicegui is not installed everywhere, so it is replaced by a mock; the backend
is built for real and its cmd_* methods are called through ImmediateExecutor,
as the immediate line does.
"""
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: web immediate command tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

PROGRAM = "5 PRINT 1\n7 PRINT 2\n9 GOTO 5\n"
# RENUM with no arguments: 10, 20, 30 and the GOTO follows the renumbering.
RENUMBERED = "10 PRINT 1\n20 PRINT 2\n30 GOTO 10"


@pytest.fixture
def backend(monkeypatch):
    for name in ("nicegui", "nicegui.ui", "nicegui.app", "nicegui.events"):
        monkeypatch.setitem(sys.modules, name, MagicMock())
    monkeypatch.delitem(sys.modules, "src.ui.web.nicegui_backend", raising=False)
    from src.ui.web import nicegui_backend as nb
    from src.editing.manager import ProgramManager
    from src.iohandler.console import ConsoleIOHandler

    b = nb.NiceGUIBackend(ConsoleIOHandler(), ProgramManager({}))
    b.editor = SimpleNamespace(value=PROGRAM)
    b.output = []
    b._append_output = b.output.append
    b._set_status = lambda message: None
    yield b
    monkeypatch.delitem(sys.modules, "src.ui.web.nicegui_backend", raising=False)


def run(backend, command):
    from src.immediate_executor import ImmediateExecutor, OutputCapturingIOHandler
    io = OutputCapturingIOHandler()
    backend._save_editor_to_program()
    backend._sync_program_to_runtime()
    return ImmediateExecutor(backend.runtime, backend.interpreter, io).execute(command)


def test_interactive_mode_set_at_start(backend):
    assert backend.interpreter.interactive_mode is backend


def test_renum_renumbers_and_prints_nothing(backend):
    assert run(backend, "RENUM") == (True, "")
    assert backend.editor.value == RENUMBERED
    assert backend.output == []


def test_renum_with_arguments(backend):
    assert run(backend, "RENUM 100,5,50") == (True, "")
    assert backend.editor.value.split("\n")[0] == "100 PRINT 1"
    assert backend.editor.value.split("\n")[-1] == "200 GOTO 100"


def test_delete_range(backend):
    assert run(backend, "DELETE 5-7") == (True, "")
    assert backend.editor.value == "9 GOTO 5"
    assert backend.output == []


def test_save_files_load_merge_round_trip(backend):
    assert run(backend, 'SAVE "T"') == (True, "")
    assert backend.sandboxed_fs.exists("T.BAS")
    # FILES is the interpreter's own statement, listing the in-memory files.
    from src.immediate_executor import OutputCapturingIOHandler
    backend.interpreter.io = OutputCapturingIOHandler()
    run(backend, "FILES")
    assert "T.BAS" in backend.interpreter.io.get_output()
    backend.editor.value = "100 PRINT 100"
    assert run(backend, 'MERGE "T"') == (True, "")
    assert backend.editor.value.split("\n") == [
        "5 PRINT 1", "7 PRINT 2", "9 GOTO 5", "100 PRINT 100"]
    assert run(backend, 'LOAD "T"') == (True, "")
    assert backend.editor.value == PROGRAM.strip()


def test_load_missing_file(backend):
    run(backend, 'LOAD "NOPE"')
    assert backend.output == ["File not found\n"]
    assert backend.editor.value == PROGRAM


def test_chain_gives_an_error_not_a_crash(backend):
    ok, text = run(backend, 'CHAIN "T"')
    assert not ok and text


def test_list_range(backend):
    run(backend, "LIST 7-9")
    assert backend.output == ["7 PRINT 2\n", "9 GOTO 5\n"]


def test_numbered_line_edits_program(backend):
    assert run(backend, "20 PRINT 20") == (True, "")
    assert "20 PRINT 20" in backend.editor.value


def test_run_and_cont_set_the_interpreter_going(backend):
    backend.editor.value = "10 PRINT 1\n20 STOP\n30 PRINT 3"
    assert run(backend, "RUN") == (True, "")
    assert backend.interpreter.has_work()
    while backend.interpreter.has_work():
        backend.interpreter.tick(max_statements=100)
    assert not backend.runtime.pc.is_running()
    assert run(backend, "CONT") == (True, "")
    assert backend.interpreter.has_work()


def test_run_and_cont_set_the_interpreter_going(backend):
    backend.editor.value = "10 PRINT 1\n20 STOP\n30 PRINT 3"
    assert run(backend, "RUN") == (True, "")
    assert backend.interpreter.has_work()
    while backend.interpreter.has_work():
        backend.interpreter.tick(max_statements=100)
    assert not backend.runtime.pc.is_running()
    assert run(backend, "CONT") == (True, "")
    assert backend.interpreter.has_work()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
