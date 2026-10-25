"""Run compiled JavaScript under Node with piped stdin: INPUT, LINE INPUT, INPUT$ and file input.

Fixes GitHub issue #8: INPUT and LINE INPUT used to give the variable a Promise under Node.
The expected text was checked against real MBASIC 5.21 (cpmemu) and the Python interpreter.
Numbers are tested with IF, not PRINT, because the JS PRINT of a number is a separate topic.
"""
import shutil
import subprocess
import sys
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
needs_node = pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")


def compile_js(tmp_path, source):
    basic = tmp_path / "prog.bas"
    basic.write_text(source)
    output = tmp_path / "prog.js"
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic), "--compile-js", str(output)],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    return output


def run_node(tmp_path, source, stdin):
    output = compile_js(tmp_path, source)
    return subprocess.run([NODE, str(output)], input=stdin, capture_output=True, text=True,
                          cwd=tmp_path, timeout=30)


@needs_node
def test_issue_8_repro(tmp_path):
    result = run_node(tmp_path, '''10 INPUT "N";N
20 IF N = 21 THEN PRINT "n ok"
30 LINE INPUT "S";S$
40 PRINT "[";S$;"]"
50 END
''', "21\nhello\n")
    assert result.returncode == 0, result.stderr
    assert result.stdout == "N? n ok\nS[hello]\n"
    assert "Promise" not in result.stdout


@needs_node
def test_prompt_rules(tmp_path):
    # semicolon after the prompt keeps "? ", comma drops it, no prompt shows "? "
    result = run_node(tmp_path, '''10 INPUT "P";A$
20 INPUT "Q",B$
30 INPUT C$
40 PRINT A$;B$;C$
''', "a\nb\nc\n")
    assert result.returncode == 0, result.stderr
    assert result.stdout == "P? Q? abc\n"


@needs_node
def test_input_semicolon_after_keyword_still_asks(tmp_path):
    # Real MBASIC: INPUT;"S";X keeps the cursor after the answer, but "? " is still shown.
    result = run_node(tmp_path, '10 INPUT;"S";A$\n20 PRINT A$\n', "a\n")
    assert result.stdout == "S? a\n"


@needs_node
def test_several_variables_quotes_and_commas(tmp_path):
    result = run_node(tmp_path, '''10 INPUT "X";A$,N,B$,I%
20 PRINT A$;"|";B$
30 IF N = 4.5 AND I% = -3 THEN PRINT "nums ok"
''', '"x,y", 4.5 ,  z  ,-2.6\n')
    assert result.returncode == 0, result.stderr
    assert result.stdout == "X? x,y|z\nnums ok\n"


@needs_node
def test_redo_from_start(tmp_path):
    # bad number, too few values, too many values, unquoted text after a closing quote
    result = run_node(tmp_path, '''10 INPUT "N";N
20 IF N = 12 THEN PRINT "n ok"
30 INPUT "T";A,B
40 IF A = 1 AND B = 2 THEN PRINT "ab ok"
50 INPUT "S";S$
60 PRINT "[";S$;"]"
''', "abc\n 1 2 \n5\n3,4,5\n1,2\n\"a\"b\na,b\n\"q,r\"\n")
    assert result.returncode == 0, result.stderr
    assert result.stdout == (
        "N? ?Redo from start\nN? n ok\n"
        "T? ?Redo from start\nT? ?Redo from start\nT? ab ok\n"
        "S? ?Redo from start\nS? ?Redo from start\nS? [q,r]\n")


@needs_node
def test_input_number_forms(tmp_path):
    # blanks inside a number are ignored, empty is 0, hex is accepted, 2.5 rounds up for INTEGER
    result = run_node(tmp_path, '''10 INPUT A
20 INPUT B
30 INPUT C
40 INPUT I%
50 IF A = 12 AND B = 0 AND C = -1 AND I% = 3 THEN PRINT "ok" ELSE PRINT "bad"
''', "1 2\n\n&HFFFF\n2.5\n")
    assert result.stdout == "? ? ? ? ok\n"


@needs_node
def test_input_percent_and_ampersand_forms(tmp_path):
    result = run_node(tmp_path, '''10 INPUT A
20 PRINT A
30 INPUT B
40 PRINT B
50 INPUT C
60 PRINT C
70 INPUT D
80 PRINT D
''', "1.5%\n1E5%\n3\n&10\n&O 17\n")
    assert result.stdout == "?  2 \n? ?Redo from start\n?  3 \n?  8 \n?  15 \n"


@needs_node
def test_line_input_keeps_commas_quotes_and_spaces(tmp_path):
    result = run_node(tmp_path, '''10 LINE INPUT "L";L$
20 PRINT "[";L$;"]"
30 LINE INPUT M$
40 PRINT "[";M$;"]"
''', ' a, "b"  \r\nplain\n')
    assert result.returncode == 0, result.stderr
    assert result.stdout == 'L[ a, "b"  ]\n[plain]\n'


@needs_node
def test_array_element_targets(tmp_path):
    result = run_node(tmp_path, '''10 DIM A$(3), N(3)
20 INPUT A$(2), N(1)
30 IF N(1) = 7 THEN PRINT A$(2)
''', "hi,7\n")
    assert result.returncode == 0, result.stderr
    assert result.stdout == "? hi\n"


@needs_node
def test_mixed_input_line_input_and_input_dollar_share_stdin(tmp_path):
    # One read from fd 0 returns the whole piped text; every statement must continue where
    # the previous one stopped, including INPUT$ taking characters from the middle of a line.
    result = run_node(tmp_path, '''10 INPUT N
20 LINE INPUT L$
30 C$ = INPUT$(3)
40 INPUT T$
50 LINE INPUT E$
60 D$ = INPUT$(2)
70 PRINT N * 2; "|"; L$; "|"; C$; "|"; T$; "|"; E$; "|"; D$
''', "5\nabc, def\nXYZtail\n last \nQR!\n")
    assert result.returncode == 0, result.stderr
    out = result.stdout
    assert out.endswith("|abc, def|XYZ|tail| last |QR\n"), out
    assert out.startswith("? "), out


@needs_node
def test_input_dollar_first_then_input(tmp_path):
    result = run_node(tmp_path, '''10 A$ = INPUT$(2)
20 INPUT B$
30 PRINT A$;"|";B$
''', "xyrest\nmore\n")
    assert result.stdout == "? xy|rest\n"


@needs_node
def test_end_of_stdin_stops_with_error_instead_of_hanging(tmp_path):
    result = run_node(tmp_path, '''10 INPUT "A";A$
20 PRINT "[";A$;"]"
30 INPUT "B";B$
40 PRINT "never"
''', "one\n")
    assert result.returncode == 1
    assert result.stdout == "A? [one]\nB? ?Input past end\n"


@needs_node
def test_last_line_without_newline(tmp_path):
    result = run_node(tmp_path, '10 LINE INPUT A$\n20 PRINT "[";A$;"]"\n', "tail")
    assert result.returncode == 0, result.stderr
    assert result.stdout == "[tail]\n"


@needs_node
def test_integer_overflow_is_an_error(tmp_path):
    result = run_node(tmp_path, '10 INPUT I%\n20 PRINT "never"\n', "40000\n")
    assert result.returncode == 1
    assert "?Overflow" in result.stdout and "never" not in result.stdout


@needs_node
def test_file_input_and_line_input_are_synchronous(tmp_path):
    result = run_node(tmp_path, '''10 OPEN "O",#1,"t.dat"
20 PRINT #1,"hello, world"
30 PRINT #1,"12,34"
40 PRINT #1,CHR$(34);"q,r";CHR$(34);",  7"
50 PRINT #1,"last line"
60 CLOSE #1
70 OPEN "I",#2,"t.dat"
80 LINE INPUT #2,A$
90 PRINT "[";A$;"]"
100 INPUT #2,X,Y
110 IF X = 12 AND Y = 34 THEN PRINT "xy ok"
120 INPUT #2,Q$,Z
130 PRINT "[";Q$;"]"
140 IF Z = 7 THEN PRINT "z ok"
150 LINE INPUT #2,L$
160 PRINT "[";L$;"]"
170 CLOSE #2
180 END
''', "")
    assert result.returncode == 0, result.stderr
    assert result.stdout == "[hello, world]\nxy ok\n[q,r]\nz ok\n[last line]\n"


BROWSER_RUNNER = """const fs = require('fs'), vm = require('vm');
const element = {textContent: ''};
const handlers = {};
const context = {console, setTimeout, clearTimeout,
 window: {prompt: () => { throw new Error('window.prompt must not be used'); }},
 document: {getElementById: () => element, addEventListener: (t, f) => { handlers[t] = f; }}};
vm.runInNewContext(fs.readFileSync(process.argv[2], 'utf8'), context);
// steps: [{wait: text}] snapshots the page output, strings are typed key by key
const steps = JSON.parse(process.argv[3]);
const snaps = [];
let prevented = 0;
function key(k) {
  const e = typeof k === 'string' ? {key: k} : k;
  e.preventDefault = () => { prevented++; };
  handlers.keydown(e);
}
function run(i) {
  if (i >= steps.length) { setTimeout(() => process.stdout.write(JSON.stringify({snaps, out: element.textContent, prevented, keypress: !!handlers.keypress})), 20); return; }
  const st = steps[i];
  if (st === 'snap') { snaps.push(element.textContent); return setTimeout(() => run(i + 1), 10); }
  for (const k of st) key(k === '\\n' ? 'Enter' : k === '\\b' ? 'Backspace' : k);
  setTimeout(() => run(i + 1), 10);
}
setTimeout(() => run(0), 20);
"""


def run_browser(tmp_path, source, steps):
    import json
    output = compile_js(tmp_path, source)
    runner = tmp_path / "browser.cjs"
    runner.write_text(BROWSER_RUNNER)
    result = subprocess.run([NODE, str(runner), str(output), json.dumps(steps)],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@needs_node
def test_browser_input_waits_for_keydown_events(tmp_path):
    # Issue #11: the browser used window.prompt (stubbed to throw here). INPUT must echo the typed
    # characters, handle Backspace, end at Enter, and leave the earlier output visible while waiting.
    data = run_browser(tmp_path, '''10 PRINT "start"
20 INPUT "N";N
30 IF N = 12 THEN PRINT "n ok"
40 LINE INPUT "S";S$
50 PRINT "[";S$;"]"
60 A$ = INPUT$(2)
70 PRINT A$
''', ["snap", "ab\n", "snap", "13\b2\n", "snap", "x, y\n", "snap", "kl"])
    assert data["snaps"][0] == "start\nN? "
    assert data["snaps"][1] == "start\nN? ab\n?Redo from start\nN? "
    assert data["snaps"][2] == "start\nN? ab\n?Redo from start\nN? 12\nn ok\nS"
    assert data["snaps"][3].endswith("Sx, y\n[x, y]\n")  # INPUT$ shows no echo yet
    assert data["out"].endswith("[x, y]\nkl\n")
    assert "kl" not in data["snaps"][3]
    assert data["prevented"] > 0
    assert data["keypress"] is False


@needs_node
def test_browser_input_dollar_takes_keys_without_echo_or_enter(tmp_path):
    data = run_browser(tmp_path, '''10 A$ = INPUT$(3)
20 PRINT "<";A$;">"
30 DEF FNK(X) = ASC(INPUT$(1)) + X
40 IF FNK(1) = 91 THEN PRINT "fn ok"
''', ["snap", "a", "b", "snap", "c", "snap", "Z"])
    assert data["snaps"] == ["", "", "<abc>\n"]
    assert data["out"] == "<abc>\nfn ok\n"


@needs_node
def test_browser_inkey_stays_non_blocking(tmp_path):
    data = run_browser(tmp_path, '''10 A$ = INKEY$
20 IF A$ = "" THEN PRINT "none"
30 PRINT "done"
''', [])
    assert data["out"] == "none\ndone\n"



if __name__ == "__main__":
    if NODE is None:
        print("Node.js unavailable: JavaScript execution tests skipped")
        sys.exit(2)
    sys.exit(pytest.main([__file__, "-q", "-p", "no:cacheprovider"]))


@needs_node
def test_non_ascii_text_round_trips_as_utf8(tmp_path):
    result = run_node(tmp_path, '''10 LINE INPUT A$
20 INPUT B$
30 PRINT A$;"|";B$
''', "café €\nnaïve\n")
    assert result.returncode == 0, result.stderr
    assert "café €|naïve" in result.stdout
    assert "�" not in result.stdout


@needs_node
def test_multibyte_character_split_across_reads(tmp_path):
    # INPUT$(1) reads one byte per readSync, so the two-byte e-acute and the three-byte euro sign
    # arrive split across chunks; the decoder must hold the partial bytes until the character is whole.
    result = run_node(tmp_path, '''10 A$ = INPUT$(1)
20 B$ = INPUT$(1)
30 C$ = INPUT$(1)
40 PRINT A$;"|";B$;"|";C$
''', "é€z")
    assert result.returncode == 0, result.stderr
    assert result.stdout == "é|€|z\n"


@needs_node
def test_hex_over_16_bits_is_overflow_not_redo(tmp_path):
    # Measured on real MBASIC 5.21: &H12345 stops the program with "Overflow", it does not ask again.
    result = run_node(tmp_path, '10 INPUT A\n20 PRINT "after"\n', "&H12345\n")
    assert result.returncode != 0
    assert "Redo" not in result.stdout
    assert "after" not in result.stdout
    assert "Overflow" in result.stdout + result.stderr
