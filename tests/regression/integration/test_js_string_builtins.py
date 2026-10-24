"""Compile real BASIC source and execute the string builtins in JavaScript."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")


def compile_js(tmp_path, source):
    basic = tmp_path / "strings.bas"
    basic.write_text(source)
    output = tmp_path / "strings.js"
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic), "--compile-js", str(output)],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    return output


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
@pytest.mark.parametrize("browser", [False, True])
def test_string_builtins_use_runtime_helpers(tmp_path, browser):
    output = compile_js(tmp_path, '''10 PRINT MID$("ABCDE",2,3)
15 PRINT MID$("ABCDE",3)
20 PRINT LEFT$("ABCDE",2)
30 PRINT RIGHT$("ABCDE",2)
40 PRINT CHR$(65)
50 PRINT SPACE$(2);"!"
60 PRINT STRING$(3,"X")
70 PRINT HEX$(255)
80 PRINT OCT$(8)
90 PRINT LEN(MKI$(123))
100 END
''')
    if browser:
        # Exercise the browser runtime branch without requiring a browser install.
        runner = tmp_path / "browser.cjs"
        runner.write_text("""const fs = require('fs'), vm = require('vm');
const element = {textContent: ''};
const context = {console, setTimeout, clearTimeout, window: {},
 document: {getElementById: () => element, addEventListener: () => {}}};
vm.runInNewContext(fs.readFileSync(process.argv[2], 'utf8'), context);
setTimeout(() => process.stdout.write(element.textContent), 20);
""")
        args = [NODE, str(runner), str(output)]
    else:
        args = [NODE, str(output)]
    result = subprocess.run(args, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert not result.stderr
    lines = result.stdout.splitlines()
    for expected in ["BCD", "CDE", "AB", "DE", "A", "  !", "XXX", "FF", "10"]:
        assert expected in lines
    assert any(line.strip() == "2" for line in lines)


if __name__ == "__main__":
    if NODE is None:
        print("Node.js unavailable: JavaScript execution tests skipped")
        sys.exit(2)
    sys.exit(pytest.main([__file__, "-q", "-p", "no:cacheprovider"]))
