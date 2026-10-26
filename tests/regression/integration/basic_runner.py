"""Run a BASIC program in the interpreter and in the JavaScript backend (helper for tests).

Not a test file. The test modules next to it import it with
sys.path.insert(0, str(Path(__file__).parent)).
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")


def run_interpreter(directory, source, name="e.bas"):
    """The text that the program prints, as the interpreter prints it (no banner, no Ok)."""
    (directory / name).write_text(source)
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(directory / name), "--ui", "cli"],
        input="RUN\nSYSTEM\n", cwd=directory, capture_output=True, text=True, timeout=60)
    lines = result.stdout.replace("\r", "").split("\n")
    start = lines.index("Ok") + 1 if "Ok" in lines else 0     # skip the banner
    out = []
    for line in lines[start:]:
        if line in ("Ok", "Goodbye") or re.fullmatch(r"\d+ ", line):
            break               # the prompt, or the edit prompt that follows a Syntax error
        out.append(line)
    return "\n".join(out).rstrip("\n") + "\n" if out else ""


def run_javascript(directory, source, name="e.bas"):
    """The text that the compiled program prints under Node."""
    (directory / name).write_text(source)
    js = directory / (name + ".js")
    compiled = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(directory / name), "--compile-js", str(js)],
        cwd=directory, capture_output=True, text=True, timeout=60)
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    result = subprocess.run([NODE, str(js)], cwd=directory, capture_output=True, text=True,
                            timeout=60, input="")
    return (result.stdout + result.stderr).replace("\r", "")
