"""Static check: every helper the generated JavaScript calls is defined in it.

This test does not need Node.js. It compiles BASIC programs that call every
built-in function the parser can produce, then checks that each function name
called in the generated JavaScript is defined in the same file (or is a
standard JavaScript/Node/browser global). INPUT$ once compiled to a call of an
undefined input$() because js_func_map had no entry for the name.
"""
import re
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: JavaScript static tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.parser import Parser  # noqa: E402
from src.tokens import TokenType  # noqa: E402

# One sample call for each built-in function token the parser can produce.
# test_every_parser_builtin_has_a_sample fails when the parser gains a
# built-in that is missing here.
SAMPLES = {
    "ABS": "ABS(-1)", "ATN": "ATN(1)", "COS": "COS(1)", "SIN": "SIN(1)",
    "TAN": "TAN(1)", "EXP": "EXP(1)", "LOG": "LOG(2)", "SQR": "SQR(4)",
    "INT": "INT(1.5)", "FIX": "FIX(1.5)", "RND": "RND(1)", "SGN": "SGN(-3)",
    "ASC": 'ASC("A")', "VAL": 'VAL("12")', "LEN": 'LEN("AB")',
    "PEEK": "PEEK(1)", "INP": "INP(1)", "USR": "USR(1)",
    "VARPTR": "VARPTR(Q)", "EOF_FUNC": "EOF(1)", "FRE": "FRE(0)",
    "LOC": "LOC(1)", "LOF": "LOF(1)", "POS": "POS(0)",
    "LEFT": 'LEFT$("ABC",2)', "RIGHT": 'RIGHT$("ABC",2)',
    "MID": 'MID$("ABC",2,1)', "CHR": "CHR$(65)", "STR": "STR$(5)",
    "INKEY": "INKEY$", "INPUT_FUNC": "INPUT$(1)", "SPACE": "SPACE$(2)",
    "STRING_FUNC": 'STRING$(2,"X")', "INSTR": 'INSTR("ABC","B")',
    "HEX": "HEX$(255)", "OCT": "OCT$(8)", "CINT": "CINT(1.5)",
    "CSNG": "CSNG(1.5)", "CDBL": "CDBL(1.5)", "CVI": 'CVI("AB")',
    "CVS": 'CVS("ABCD")', "CVD": 'CVD("ABCDEFGH")', "MKI": "MKI$(1)",
    "MKS": "MKS$(1)", "MKD": "MKD$(1)",
    # Only valid inside PRINT; handled below.
    "TAB": "TAB(5)", "SPC": "SPC(2)",
}

# Extra forms of the same functions: INPUT$ with a file number (with and
# without '#'), and the file functions without an OPEN statement.
EXTRA_LINES = [
    "S$ = INPUT$(2, #1)",
    "S$ = INPUT$(2, 1)",
    "S$ = INPUT$(LEN(S$) + 1)",
    "N = EOF(1) + LOF(1) + LOC(1)",
]

# Names that appear as calls in generated code but are not runtime helpers.
JS_KEYWORDS = {
    "if", "for", "while", "switch", "catch", "function", "return", "typeof",
    "new", "throw", "else", "do", "in", "of", "case", "await", "async",
    "void", "delete", "try",
}
JS_GLOBALS = {
    # Language and standard library
    "Math", "String", "Number", "Array", "Object", "Date", "Error", "Buffer",
    "Promise", "Boolean", "Symbol", "JSON", "RegExp", "Map", "Set", "Uint8Array",
    "Float32Array", "Float64Array", "DataView", "ArrayBuffer",
    "parseFloat", "parseInt", "isNaN", "isFinite", "setTimeout",
    "clearTimeout", "setInterval", "clearInterval", "BigInt", "Int32Array",
    # Host (Node.js, browser)
    "require", "alert", "prompt", "confirm",
}


def compile_js(tmp_path, source, name):
    basic = tmp_path / (name + ".bas")
    basic.write_text(source)
    output = tmp_path / (name + ".js")
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(basic), "--compile-js", str(output)],
        cwd=ROOT, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stderr
    return output.read_text()


def strip_literals(js):
    """Remove comments and string/template literals so names inside them are ignored."""
    out = []
    i, n = 0, len(js)
    while i < n:
        c = js[i]
        two = js[i:i + 2]
        if two == "//":
            while i < n and js[i] != "\n":
                i += 1
        elif two == "/*":
            end = js.find("*/", i + 2)
            i = n if end < 0 else end + 2
        elif c in "\"'":
            i += 1
            while i < n and js[i] != c:
                i += 2 if js[i] == "\\" else 1
            i += 1
            out.append('""')
        elif c == "`":
            # Keep ${...} expressions: they hold real code.
            i += 1
            while i < n and js[i] != "`":
                if js[i] == "\\":
                    i += 2
                elif js[i:i + 2] == "${":
                    depth, j = 1, i + 2
                    while j < n and depth:
                        depth += {"{": 1, "}": -1}.get(js[j], 0)
                        j += 1
                    out.append(strip_literals(js[i + 2:j - 1]) + ";")
                    i = j
                else:
                    i += 1
            i += 1
            out.append('""')
        else:
            out.append(c)
            i += 1
    return "".join(out)


def undefined_calls(js):
    code = strip_literals(re.sub(r"\A#![^\n]*", "", js))  # drop the shebang line
    defined = set(re.findall(r"\bfunction\s+([A-Za-z_$][\w$]*)", code))
    defined |= set(re.findall(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)", code))
    # Destructuring and parameter names: any name that is a parameter of a
    # function or arrow function counts as defined (it may be called).
    for params in re.findall(r"function\s*[\w$]*\s*\(([^)]*)\)", code):
        defined |= set(re.findall(r"[A-Za-z_$][\w$]*", params))
    for params in re.findall(r"\(([^()]*)\)\s*=>", code):
        defined |= set(re.findall(r"[A-Za-z_$][\w$]*", params))
    defined |= set(re.findall(r"\b([A-Za-z_$][\w$]*)\s*=>", code))
    defined |= set(re.findall(r"\bcatch\s*\(\s*([A-Za-z_$][\w$]*)", code))
    called = set()
    for match in re.finditer(r"(?<![\w$.])([A-Za-z_$][\w$]*)\s*\(", code):
        called.add(match.group(1))
    # Object-literal methods such as  open: (a, b) => ...  are properties and
    # are only reached through "." so they are not plain calls.
    return sorted(called - defined - JS_KEYWORDS - JS_GLOBALS)


def all_builtin_token_names():
    parser = Parser.__new__(Parser)
    return sorted(t.name for t in TokenType if Parser.is_builtin_function(parser, t))


def program(extra_lines, with_open):
    lines = []
    if with_open:
        lines.append('OPEN "I", #1, "data.txt"')
    for name, call in sorted(SAMPLES.items()):
        if name in ("TAB", "SPC"):
            lines.append(f'PRINT {call}; "x"')
        elif name in ("LEFT", "RIGHT", "MID", "CHR", "STR", "INKEY", "INPUT_FUNC",
                      "SPACE", "STRING_FUNC", "HEX", "OCT", "MKI", "MKS", "MKD"):
            lines.append(f"S$ = {call}")
        else:
            lines.append(f"N = {call}")
    lines.extend(extra_lines)
    if with_open:
        lines.append("CLOSE #1")
    lines.append("END")
    return "".join(f"{10 * (i + 1)} {text}\n" for i, text in enumerate(lines))


def test_every_parser_builtin_has_a_sample():
    assert sorted(SAMPLES) == all_builtin_token_names()


def test_checker_finds_an_undefined_helper():
    # Guards the checker itself: the INPUT$ bug must be visible to it.
    js = "(function(){ function _a(){} _a(); input$(1); x.y(2); 'z(1)'; })();"
    assert undefined_calls(js) == ["input$"]


@pytest.mark.parametrize("with_open", [True, False])
def test_all_called_helpers_are_defined(tmp_path, with_open):
    js = compile_js(tmp_path, program(EXTRA_LINES, with_open), "all")
    assert undefined_calls(js) == []


@pytest.mark.parametrize("call", sorted(SAMPLES.values()) + EXTRA_LINES)
def test_each_builtin_alone_calls_only_defined_helpers(tmp_path, call):
    if call.startswith(("TAB", "SPC")):
        source = f'10 PRINT {call}; "x"\n20 END\n'
    elif "=" in call:
        source = f"10 {call}\n20 END\n"
    else:
        source = f"10 Z = {call}\n20 END\n"
    if "$" in call and "=" not in call and not call.startswith(("TAB", "SPC")):
        source = f"10 Z$ = {call}\n20 END\n"
    js = compile_js(tmp_path, source, "one")
    assert undefined_calls(js) == []


def test_input_dollar_emits_helper_and_file_support(tmp_path):
    js = compile_js(tmp_path, '10 OPEN "I", #1, "x"\n20 S$ = INPUT$(1, #1)\n30 END\n', "f")
    assert "function _input_chars(" in js
    assert "_input_chars(1.0, 1.0)" in js or re.search(r"_input_chars\(1(\.0)?, 1(\.0)?\)", js)
    assert "const _files" in js
    # The file form needs the file helpers even without any OPEN statement.
    js = compile_js(tmp_path, "10 S$ = INPUT$(1, #1)\n20 END\n", "g")
    assert "const _files" in js and "function _input_chars(" in js


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q", "-p", "no:cacheprovider"]))
