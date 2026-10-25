"""Run INPUT$(n) and INPUT$(n,#f) from the JavaScript compiler in Node.js.

INPUT$ reads raw characters: no echo and no Enter. The generated program is
synchronous, so Node waits for keys with fs.readSync on stdin.
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

pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")


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


def run_node(tmp_path, source, stdin=""):
    output = compile_js(tmp_path, source)
    return subprocess.run([NODE, str(output)], cwd=tmp_path, input=stdin,
                          capture_output=True, text=True, timeout=30)


def test_keyboard_reads_n_characters_without_enter(tmp_path):
    # No newline anywhere in stdin: INPUT$ must not wait for Enter.
    result = run_node(tmp_path, '10 A$=INPUT$(3)\n20 B$=INPUT$(2)\n30 PRINT A$;"|";B$\n40 END\n',
                      stdin="abcde")
    assert result.returncode == 0, result.stderr
    assert result.stdout == "abc|de\n"  # no echo of the typed characters


def test_keyboard_newline_is_a_character(tmp_path):
    result = run_node(tmp_path, '10 A$=INPUT$(3)\n20 PRINT ASC(MID$(A$,2,1))\n30 END\n', stdin="a\nb")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "10"


def test_keyboard_end_of_input_is_input_past_end(tmp_path):
    result = run_node(tmp_path, '10 A$=INPUT$(4)\n20 PRINT A$\n30 END\n', stdin="ab")
    assert result.returncode != 0
    assert "Input past end" in result.stdout + result.stderr


def test_bad_length_is_illegal_function_call(tmp_path):
    result = run_node(tmp_path, '10 N=0\n20 A$=INPUT$(N)\n30 END\n', stdin="ab")
    assert result.returncode != 0
    assert "Illegal function call" in result.stdout + result.stderr


FILE_PROGRAM = '''10 OPEN "O",#1,"t.txt"
20 PRINT #1,"HELLO";
30 CLOSE #1
40 OPEN "I",#1,"t.txt"
50 A$=INPUT$(3,#1)
60 B$=INPUT$(2,1)
70 PRINT A$;"|";B$
80 IF EOF(1) THEN PRINT "EOF"
90 CLOSE #1
100 END
'''


def test_file_form_reads_n_characters(tmp_path):
    result = run_node(tmp_path, FILE_PROGRAM)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ["HEL|LO", "EOF"]


def test_file_form_past_end_is_an_error(tmp_path):
    result = run_node(tmp_path, FILE_PROGRAM.replace("90 CLOSE #1", "85 C$=INPUT$(1,#1)\n90 CLOSE #1"))
    assert result.returncode != 0
    assert "Input past end" in result.stdout + result.stderr


def test_file_form_on_output_file_is_bad_file_mode(tmp_path):
    result = run_node(tmp_path, '10 OPEN "O",#1,"t.txt"\n20 A$=INPUT$(1,#1)\n30 END\n')
    assert result.returncode != 0
    assert "Bad file mode" in result.stdout + result.stderr


def test_browser_branch_takes_keys_from_keydown_buffer(tmp_path):
    output = compile_js(tmp_path, '10 A$=INPUT$(3)\n20 B$=INPUT$(2)\n30 PRINT A$;"|";B$\n40 END\n')
    runner = tmp_path / "browser.cjs"
    runner.write_text("""const fs = require('fs'), vm = require('vm');
const element = {textContent: ''};
const handlers = {};
const context = {console, setTimeout, clearTimeout,
 window: {prompt: () => { throw new Error('window.prompt must not be used'); }},
 document: {getElementById: () => element, addEventListener: (t, f) => { handlers[t] = f; }}};
vm.runInNewContext(fs.readFileSync(process.argv[2], 'utf8'), context);
// Five keys arrive at once: "hel" feed the first INPUT$, "lo" stay buffered for the second.
setTimeout(() => { for (const k of 'hello') handlers.keydown({key: k}); }, 10);
setTimeout(() => process.stdout.write(element.textContent), 30);
""")
    result = subprocess.run([NODE, str(runner), str(output)], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert result.stdout == "hel|lo\n"


if __name__ == "__main__":
    if NODE is None:
        print("Node.js unavailable: JavaScript execution tests skipped")
        sys.exit(2)
    sys.exit(pytest.main([__file__, "-q", "-p", "no:cacheprovider"]))
