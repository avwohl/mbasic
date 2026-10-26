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
    pc = backend.runtime.pc
    stopped = pc.line is not None and pc.stop_reason in ("STOP", "BREAK")
    backend._save_editor_to_program(reset_runtime=not stopped)
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


def test_chain_loads_the_file_and_runs_it(backend):
    # Real MBASIC 5.21: CHAIN "T" from the Ok prompt loads T.BAS and runs it.
    assert run(backend, 'SAVE "T"') == (True, "")
    backend.editor.value = "10 PRINT 99"
    assert run(backend, 'CHAIN "T"') == (True, "")
    assert backend.editor.value == PROGRAM.strip()
    assert backend.interpreter.has_work()


def test_chain_all_passes_variables(backend):
    # Real MBASIC 5.21: CHAIN "T",,ALL keeps every variable.
    run(backend, 'SAVE "T"')
    backend.runtime.set_variable_raw("a%", 7)
    backend.cmd_chain("T", all_flag=True)
    assert backend.runtime.get_variable_raw("a%") == 7


def test_chain_missing_file(backend):
    run(backend, 'CHAIN "NOPE"')
    assert backend.output == ["File not found\n"]


def test_chain_inside_a_running_program_is_an_error(backend):
    backend.running = True
    with pytest.raises(IOError):
        backend.cmd_chain("T")


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


def test_cont_without_a_stopped_program_is_an_error(backend):
    # Real MBASIC 5.21 prints "?Can't continue" for CONT before any RUN.
    run(backend, "CONT")
    assert any("Can't continue" in o for o in backend.output)
    assert not backend.running


def test_load_and_merge_report_a_read_abort_and_overflow(backend):
    # The same rules as the CLI (fix-load-merge): a line with no number stops
    # the read with the bare message and keeps the lines read before it; a
    # literal such as 1E39 prints Overflow while the file is read.
    handle = backend.sandboxed_fs.open("BAD.BAS", "w")
    handle.write("10 PRINT 1\nPRINT 2\n20 PRINT 3\n")
    handle.close()
    assert backend.cmd_load("BAD") is True
    assert backend.output == ["Direct statement in file\n"]
    assert backend.editor.value == "10 PRINT 1"
    backend.output.clear()
    assert backend.cmd_merge("BAD", quiet=True, from_program=True) is True
    assert backend.output == ["Direct statement in file\n"]
    handle = backend.sandboxed_fs.open("OVF.BAS", "w")
    handle.write("10 X=1E39\n")
    handle.close()
    backend.output.clear()
    assert backend.cmd_load("OVF") is None
    assert backend.output == ["Overflow\n"]


def test_merge_of_a_missing_file_in_a_program_raises(backend):
    # CLI cmd_merge raises so that ON ERROR can trap the error.
    with pytest.raises(RuntimeError, match="File not found"):
        backend.cmd_merge("NOPE", quiet=True, from_program=True)


# SYSTEM in the multi-user web UI: it must not stop the server (SystemExit) and
# it must not fail with an error.  The program of the session ends, as at END.
# Real MBASIC 5.21 leaves to the OS at SYSTEM, so no statement after SYSTEM runs.
def test_system_typed_ends_the_session_program_only(backend):
    backend.runtime.pc = backend.runtime.pc.stop("STOP")
    backend.cmd_system()
    assert backend.output == ["Goodbye\n"]
    assert backend.runtime.pc.line is None
    assert backend.runtime.cont_pc is None


def test_system_in_a_running_program_stops_it(backend):
    backend.editor.value = '10 PRINT "A"\n20 SYSTEM\n30 PRINT "B"\n'
    backend._save_editor_to_program()
    backend._sync_program_to_runtime()
    printed = []
    backend.interpreter.io.output = lambda text, end="\n": printed.append(text)
    state = backend.interpreter.start()
    assert not state.error_info
    for _ in range(20):
        if not backend.interpreter.has_work():
            break
        backend.interpreter.tick()
    assert printed[0] == "A"
    assert backend.output == ["Goodbye\n"]    # the backend prints it, not the program
    assert "B" not in printed
    assert not backend.interpreter.has_work()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
