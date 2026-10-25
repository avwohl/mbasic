"""The generated JavaScript gives the browser time to run (issue 25).

Before the fix a long loop or an INKEY$ polling loop never gave control back to the page, so the page froze
and a keydown handler could not run. The tests run the generated file in a Node vm context with a stub
document and window (the browser branch of the runtime), and in plain Node (with a pipe for INKEY$).
"""
import shutil
import subprocess
import sys
import time
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: JavaScript execution tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")

# Runs the generated file with a stub document and window. argv: file, delay of the key press (ms, 0 = no
# key), key, give-up time (ms). Prints a JSON line: output of the program, number of timer ticks and key
# events that ran while the program was still running, and whether the output was complete.
RUNNER = r"""
const fs = require('fs'), vm = require('vm');
const [file, keyDelay, key, giveUp] = [process.argv[2], +process.argv[3], process.argv[4], +process.argv[5]];
const element = {textContent: ''};
let handler = null, ticks = 0, keysSeen = 0, finished = false;
const context = {console, setTimeout, clearTimeout, window: {},
  document: {getElementById: () => element, addEventListener: (t, h) => { if (t === 'keydown') handler = h; }}};
setInterval(() => { if (!finished) ticks++; }, 5);
if (keyDelay > 0) setTimeout(() => { if (handler) { if (!finished) keysSeen++; handler({key}); } }, keyDelay);
const t0 = Date.now();
try {
  vm.runInNewContext(fs.readFileSync(file, 'utf8'), context, {timeout: 20000});
} catch (e) { element.textContent += 'SCRIPT ERROR ' + e.message; }
const started = Date.now() - t0;
const poll = () => {
  const done = /\bEND\b|\?[A-Z]/.test(element.textContent) || Date.now() - t0 > giveUp;
  if (done) {
    finished = true;
    console.log(JSON.stringify({out: element.textContent, ticks, keysSeen, startMs: started, ms: Date.now() - t0}));
    process.exit(0);
  }
  setTimeout(poll, 5);
};
poll();
"""


def compile_js(tmp_path, source):
    basic = tmp_path / "prog.bas"
    basic.write_text(source)
    output = tmp_path / "prog.js"
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic), "--compile-js", str(output)],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return output


def run_in_page(tmp_path, source, key_delay=0, key="x", give_up=8000):
    """Run the compiled program in the browser branch; return the decoded result of the runner."""
    import json
    output = compile_js(tmp_path, source)
    runner = tmp_path / "page.cjs"
    runner.write_text(RUNNER)
    result = subprocess.run([NODE, str(runner), str(output), str(key_delay), key, str(give_up)],
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


# The program ends with PRINT "END" so that the runner knows when it is done
KEY_POLL = '10 A$=INKEY$:IF A$="" THEN 10\n20 PRINT "GOT ";A$\n25 PRINT "END"\n30 SYSTEM\n'


def test_inkey_polling_loop_sees_keydown_in_page(tmp_path):
    result = run_in_page(tmp_path, KEY_POLL, key_delay=200)
    assert result["out"] == "GOT x\nEND\n"
    assert result["keysSeen"] == 1  # the key press ran while the program was polling


def test_key_press_before_any_poll_is_not_lost(tmp_path):
    # INKEY$ in a loop that also does other work; the key arrives in the middle
    source = ('10 N=0\n20 A$=INKEY$\n30 N=N+1\n40 IF A$="" THEN 20\n50 PRINT "GOT ";A$;" after polls"\n'
              '55 PRINT "END"\n60 SYSTEM\n')
    result = run_in_page(tmp_path, source, key_delay=100, key="q")
    assert result["out"] == "GOT q after polls\nEND\n"


LONG_LOOP = '10 FOR I=1 TO 400000\n20 A=A+1\n30 NEXT I\n40 PRINT "done"\n45 PRINT "END"\n50 SYSTEM\n'


def test_long_loop_lets_timers_and_key_events_run(tmp_path):
    result = run_in_page(tmp_path, LONG_LOOP, key_delay=20)
    assert result["out"] == "done\nEND\n"
    # The loop runs for several hundred ms in the stub; a program that never yields has 0 ticks
    assert result["ticks"] >= 3
    assert result["keysSeen"] == 1


def test_goto_loop_lets_timers_run(tmp_path):
    source = '10 K=0\n20 K=K+1\n30 IF K<300000 THEN 20\n40 PRINT "done"\n45 PRINT "END"\n50 SYSTEM\n'
    result = run_in_page(tmp_path, source)
    assert result["out"] == "done\nEND\n"
    assert result["ticks"] >= 3


def test_same_line_while_loop_lets_timers_run(tmp_path):
    source = '10 I=0:WHILE I<300000:I=I+1:WEND\n20 PRINT "done"\n25 PRINT "END"\n30 SYSTEM\n'
    result = run_in_page(tmp_path, source)
    assert result["out"] == "done\nEND\n"
    assert result["ticks"] >= 3


def test_gosub_recursion_loop_lets_timers_run(tmp_path):
    source = ('10 N=0\n20 GOSUB 100\n30 PRINT "done"\n35 PRINT "END"\n40 SYSTEM\n'
              '100 N=N+1\n110 IF N<200000 THEN GOSUB 100\n120 RETURN\n')
    result = run_in_page(tmp_path, source)
    assert result["out"] == "done\nEND\n"


@pytest.mark.parametrize("name,source,expected", [
    ("for_loops", '10 FOR I=1 TO 3:FOR J=1 TO 2:PRINT I;J;:NEXT J,I:PRINT\n20 PRINT "END"\n30 SYSTEM\n',
     " 1  1  1  2  2  1  2  2  3  1  3  2 \nEND\n"),
    ("gosub", '10 GOSUB 100:PRINT "back"\n20 PRINT "END"\n30 SYSTEM\n100 PRINT "sub":RETURN\n', "sub\nback\nEND\n"),
    ("goto_loop", '10 K=0\n20 K=K+1\n30 IF K<5 THEN 20\n40 PRINT K\n50 PRINT "END"\n60 SYSTEM\n', " 5 \nEND\n"),
    ("next_in_if", '10 FOR I=1 TO 3:IF I<3 THEN PRINT "lt";I:NEXT I\n20 PRINT "end"\n25 PRINT "END"\n30 SYSTEM\n',
     "lt 1 \nlt 2 \nend\nEND\n"),
    ("on_goto_back", '10 N=N+1\n20 ON N GOTO 10,10,40\n30 PRINT "no"\n40 PRINT N\n50 PRINT "END"\n60 SYSTEM\n',
     " 3 \nEND\n"),
])
def test_page_copy_gives_same_output(tmp_path, name, source, expected):
    assert run_in_page(tmp_path, source)["out"] == expected


def test_resume_loop_in_page(tmp_path):
    source = ('10 ON ERROR GOTO 100\n20 N=N+1\n30 IF N<3 THEN ERROR 5\n40 PRINT "done";N\n50 PRINT "END"\n60 SYSTEM\n'
              '100 RESUME 20\n')
    assert run_in_page(tmp_path, source)["out"] == "done 3 \nEND\n"


# ---- Node

def test_node_inkey_reads_piped_stdin(tmp_path):
    output = compile_js(tmp_path, '10 A$=INKEY$:IF A$="" THEN 10\n20 PRINT "GOT ";A$\n30 SYSTEM\n')
    proc = subprocess.Popen([NODE, str(output)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    time.sleep(0.4)  # the program is polling by now
    out, _ = proc.communicate("x", timeout=20)
    assert out == "GOT x\n"
    assert proc.returncode == 0


def test_node_inkey_without_input_does_not_block(tmp_path):
    # No key: INKEY$ returns "" at once, so the loop counts. A blocking read would hang until the timeout.
    source = ('10 A$=INKEY$:N=N+1:IF N<200000 THEN 10\n20 PRINT "polled";N\n30 SYSTEM\n')
    output = compile_js(tmp_path, source)
    proc = subprocess.Popen([NODE, str(output)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    out, _ = proc.communicate(timeout=20)  # stdin stays open and empty until communicate closes it
    assert out == "polled 200000 \n"


def test_node_copy_of_the_program_has_no_yield_check(tmp_path):
    output = compile_js(tmp_path, LONG_LOOP)
    text = output.read_text()
    main = text[text.index("function main()"):text.index("function _run(")]
    assert "_budget" not in main  # Node runs this copy: its speed is the speed of the program before issue 25
    run = text[text.index("function _run("):text.index("function _main_page(")]
    assert "_budget" in run


def test_program_without_loop_has_no_driver(tmp_path):
    text = compile_js(tmp_path, '10 PRINT "A"\n20 PRINT "B"\n30 SYSTEM\n').read_text()
    assert "_run(" not in text and "_main_page" not in text
    assert "async function main" not in text


def test_def_fn_is_async_only_when_it_waits_for_a_key(tmp_path):
    source = ('10 DEF FNA(X)=X*2\n20 DEF FNK$=INKEY$\n30 DEF FNB$=FNK$+"!"\n40 PRINT FNA(2)\n50 A$=FNB$\n60 PRINT "ok"\n70 SYSTEM\n')
    text = compile_js(tmp_path, source).read_text()
    assert "\n  function _fn_a(" in text
    assert "async function _fn_k(" in text
    assert "async function _fn_b(" in text
    run = subprocess.run([NODE, str(tmp_path / "prog.js")], capture_output=True, text=True, timeout=20, input="")
    assert run.returncode == 0, run.stderr
    assert run.stdout == " 4 \nok\n"


if __name__ == "__main__":
    if NODE is None:
        print("Node.js unavailable: JavaScript execution tests skipped")
        sys.exit(2)
    sys.exit(pytest.main([__file__, "-q", "-p", "no:cacheprovider"]))
