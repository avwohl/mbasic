#!/usr/bin/env python3
"""
JavaScript Code Generation Backend

Generates JavaScript code from BASIC programs that runs in:
- Browser (via <script> tag or standalone HTML)
- Node.js (command-line execution)

Generated code uses a switch-based control flow system for GOTO/GOSUB.
"""

import json
from typing import List, Dict, Set, Optional, Any
from src.ast_nodes import *
from src.semantic_analyzer import SymbolTable, VarType
from src.codegen_backend import CodeGenBackend
from src.tokens import TokenType
from src.error_codes import ERROR_CODES
from src.string_temps import string_temps, STRING_TEMPORARIES
from src.number_format import (numeric_digits, to_single, INTEGER_DIGITS,
                               SINGLE_DIGITS, DOUBLE_DIGITS, machine_infinity)


JS_NUMBER_RUNTIME = r'''
// ===== MBASIC number formatting (port of src/number_format.py) =====
// digits: 0 = INTEGER, 6 = single, 16 = double. The caller knows the type of
// the expression; the value alone cannot say.
function _round_digits(ds, exp, n) {
    // Round a decimal digit string half up to n significant digits.
    if (ds.length > n) {
        const up = ds.charCodeAt(n) >= 53;
        const head = ds.slice(0, n).split("").map(Number);
        if (up) {
            let i = n - 1;
            while (i >= 0) {
                if (head[i] === 9) { head[i] = 0; i--; } else { head[i]++; break; }
            }
            if (i < 0) { head.unshift(1); head.pop(); exp++; }
        }
        ds = head.join("");
    }
    ds = ds.replace(/0+$/, "");
    return [ds === "" ? "0" : ds, exp];
}
function _sig_digits(a, digits) {
    // The digits of a > 0 rounded to 6 (single) or 16 (double) significant figures, as [digit string, exponent].
    // A single is rounded twice - to the 7 digits MBASIC's conversion makes, then to the 6 printed - starting
    // from its shortest decimal form. A double is rounded once, from its exact binary value.
    const m = /^(\d)(?:\.(\d+))?e([+-]\d+)$/.exec(digits === 6 ? a.toExponential() : a.toExponential(digits - 1));
    let ds = m[1] + (m[2] || ""), exp = parseInt(m[3], 10);
    if (digits === 6) [ds, exp] = _round_digits(ds, exp, 7);
    return _round_digits(ds, exp, digits);
}
function _fmt_num(v, digits) {
    if (v === true) v = -1; else if (v === false) v = 0;
    if (digits === 0) return String(Math.trunc(v) + 0);
    if (v !== v || v === Infinity || v === -Infinity) return String(v);
    if (v === 0) return "0";
    const neg = v < 0;
    const [ds, exp] = _sig_digits(Math.abs(v), digits);
    const sig = ds.length;
    const unscaled = exp >= 0 ? exp + 1 <= digits : (-exp - 1) + sig <= digits + 1;
    let text;
    if (unscaled) {
        if (exp >= 0) {
            text = sig <= exp + 1 ? ds + "0".repeat(exp + 1 - sig) : ds.slice(0, exp + 1) + "." + ds.slice(exp + 1);
        } else {
            text = "." + "0".repeat(-exp - 1) + ds;
        }
    } else {
        text = ds[0] + (sig > 1 ? "." + ds.slice(1) : "") + (digits > 6 ? "D" : "E") +
            (exp >= 0 ? "+" : "-") + String(Math.abs(exp)).padStart(2, "0");
    }
    return neg ? "-" + text : text;
}
function _fmt_print(v, digits) {
    // As printed in a PRINT list: a leading space unless negative, a trailing space always.
    const t = _fmt_num(v, digits);
    return (t[0] === "-" ? "" : " ") + t + " ";
}
function _pstr(v, digits) {
    return typeof v === "string" ? v : _fmt_print(v, digits);
}
const _MAX_SINGLE = 1.7014117331926443e38, _MAX_DOUBLE = 1.7014118346046927e38, _SINGLE_LIMIT = 3.4028235677973366e38;
function _sg(x) {
    // Result of single-precision arithmetic: rounded to binary32. Whole numbers are left alone, as the interpreter does.
    // A result that binary32 cannot hold is Overflow (the MBF range is not emulated).
    if (typeof x !== "number") return x;
    if (x >= _SINGLE_LIMIT || x <= -_SINGLE_LIMIT) return _overflow(x < 0, 6);
    return Number.isInteger(x) ? x : Math.fround(x);
}
function _dg(x) {
    // Result of double-precision arithmetic: infinite is Overflow.
    return x === Infinity || x === -Infinity ? _overflow(x < 0, 16) : x;
}
function _round_half_away(n) {
    return n < 0 ? -Math.floor(-n + 0.5) : Math.floor(n + 0.5);
}
'''

JS_ARITH_RUNTIME = r'''
// ===== Arithmetic: overflow, division by zero, domain errors =====
function _armed() {
    // ON ERROR GOTO is set: the non-fatal messages become ordinary errors.
    return typeof _error_handler !== "undefined" && !!_error_handler;
}
function _notice(text) {
    // The message goes through the width logic of PRINT, one character at a time: next to the right edge
    // the word is split (measured on MBASIC 5.21: "Overflo" and "w"). A screen of width 255 never wraps.
    _print(_wrap_text(_col, _width >= 255 ? 1e9 : _width, text, false));
}
function _overflow(negative, digits) {
    // A result too big for its precision: MBASIC prints Overflow, substitutes machine infinity and carries on.
    if (_armed()) _error("Overflow");
    _notice("Overflow");
    const m = digits > 6 ? _MAX_DOUBLE : _MAX_SINGLE;
    return negative ? -m : m;
}
function _divzero(dividend, digits) {
    if (_armed()) _error("Division by zero");
    _notice("Division by zero");
    const m = digits > 6 ? _MAX_DOUBLE : _MAX_SINGLE;
    return dividend < 0 ? -m : m;
}
function _div(a, b, digits) {
    return b === 0 ? _divzero(a, digits) : a / b;
}
function _pow(a, b, digits) {
    if (a === 0 && b < 0) return _divzero(1, digits);
    if (a < 0 && b !== Math.floor(b)) _error("Illegal function call");
    return Math.pow(a, b);
}
function _sqr(x) {
    if (x < 0) _error("Illegal function call");
    return Math.sqrt(x);
}
function _log(x) {
    if (!(x > 0)) _error("Illegal function call");
    return Math.log(x);
}
function _val_radix(s) {
    // VAL of text that starts with &: &H takes hex digits (no blanks), &O and & take octal digits (blanks skipped).
    // More than four hex digits, or an octal number above 65535, is Overflow; an 8 or 9 in an octal number is a Syntax error.
    let i = 1;
    while (s[i] === " " || s[i] === "\t") i++;
    const kind = (s[i] || "").toUpperCase();
    let v;
    if (kind === "H") {
        const digits = /^[0-9A-Fa-f]*/.exec(s.slice(i + 1))[0];
        if (digits.length > 4) _error("Overflow");
        v = digits === "" ? 0 : parseInt(digits, 16);
    } else if (kind === "O" || (kind >= "0" && kind <= "9")) {
        let run = "";
        for (const ch of s.slice(kind === "O" ? i + 1 : i)) {
            if (ch === " " || ch === "\t") continue;
            if (ch >= "0" && ch <= "9") run += ch; else break;
        }
        if (/[89]/.test(run)) _error("Syntax error");
        v = run === "" ? 0 : parseInt(run, 8);
        if (v > 65535) _error("Overflow");
    } else {
        return 0;
    }
    return v >= 32768 ? v - 65536 : v;
}
function _val(str) {
    // MBASIC's VAL (same rules as input_fields.val_text): blanks and tabs are skipped inside the number, E and D
    // are exponent letters, an exponent without digits is 0, and the number ends at the first other character.
    let s = String(str).replace(/^[ \t\n]+/, "");
    if (s[0] === "&") return _val_radix(s);
    s = s.replace(/[ \t\n]/g, "");
    const m = /^([+-]?)(\d*)(\.?)(\d*)/.exec(s);
    if (m[2] === "" && m[4] === "") return 0;
    let rest = s.slice(m[0].length), exp = "0", hasExp = false;
    const e = /^[EeDd]([+-]?)(\d*)/.exec(rest);
    if (e) { hasExp = true; if (e[2] !== "") exp = e[1] + e[2]; rest = rest.slice(e[0].length); }
    let v = Number(m[1] + (m[2] || "0") + "." + (m[4] || "0") + "e" + exp);
    if (!hasExp && rest[0] === "%") {
        v = _round_half_away(v);
        if (v > 32767 || v < -32768) _error("Overflow");
    }
    return v === Infinity || v === -Infinity ? _overflow(v < 0, 16) : v;
}
function _int16(n) {
    // The operand of \\ and MOD: rounded to an integer, and it must fit 16 bits.
    n = _round_half_away(n);
    if (!(n >= -32768 && n <= 32767)) _error("Overflow");
    return n;
}
function _idiv(a, b) {
    a = _int16(a); b = _int16(b);
    if (b === 0) _error("Division by zero");
    return Math.trunc(a / b) + 0;
}
function _mod(a, b) {
    a = _int16(a); b = _int16(b);
    if (b === 0) _error("Division by zero");
    return (a % b) + 0;
}
'''


JS_LOGICAL_RUNTIME = r'''
// AND, OR, XOR, EQV, IMP and NOT work on 16-bit integers. An operand is rounded to the nearest
// integer (halves away from zero); outside -32768..32767 it is an Overflow, as in MBASIC 5.21.
function _ci(n) {
    if (n >= -32768 && n <= 32767 && n === Math.floor(n)) return n;  // the usual case: no work
    if (typeof n !== "number" || n !== n) _error("Type mismatch");
    return _toInt(n);
}
function _and(a, b) { return _ci(a) & _ci(b); }
function _or(a, b) { return _ci(a) | _ci(b); }
function _xor(a, b) { return _ci(a) ^ _ci(b); }
function _eqv(a, b) { return ~(_ci(a) ^ _ci(b)); }
function _imp(a, b) { return ~_ci(a) | _ci(b); }
function _not(a) { return ~_ci(a); }
'''

JS_INKEY_RUNTIME = r'''
// INKEY$ - get a key without waiting. Browser: every INKEY$ call that finds no key gives the page time
// to run (_yield), so the keydown handler can fill _inkey_buffer. Node: read what waits on stdin, never block.
let _inkey_buffer = "";
let _key_waiter = null;  // browser: resolver of the Promise an INPUT is waiting on
const _browser = typeof window !== "undefined";
let _slice_start = 0;  // clock reading when main() last gave the page time to run
function _now() { return typeof performance !== "undefined" ? performance.now() : Date.now(); }
function _yield() {
    // A macrotask: the page repaints and handles key events before the program goes on
    return new Promise((resolve) => setTimeout(resolve, 0));
}
let _poll_fd = -2;  // Node: -2 not opened yet, -1 nothing more to read
let _poll_buf = null;
let _poll_decoder = null;
function _poll_stdin() {
    const fs = require("fs");
    if (_poll_fd === -2) {
        _poll_fd = -1;
        try {
            // A file is read through fd 0. A pipe or a terminal is opened again with O_NONBLOCK, so a read
            // that finds nothing fails with EAGAIN and does not wait.
            if (fs.fstatSync(0).isFile()) _poll_fd = 0;
            else _poll_fd = fs.openSync("/dev/stdin", fs.constants.O_RDONLY | fs.constants.O_NONBLOCK);
        } catch (e) { _poll_fd = -1; }
        _poll_buf = Buffer.alloc(256);
        _poll_decoder = new (require("string_decoder").StringDecoder)("utf8");
    }
    if (_poll_fd < 0) return;
    let got = 0;
    try {
        got = fs.readSync(_poll_fd, _poll_buf, 0, 256, null);
    } catch (e) {
        if (e.code !== "EAGAIN") _poll_fd = -1;
        return;
    }
    if (got === 0) { _poll_fd = -1; return; }  // end of input
    _inkey_buffer += _poll_decoder.write(_poll_buf.subarray(0, got));
}
async function _inkey() {
    if (_inkey_buffer.length === 0) {
        if (_browser) { await _yield(); _slice_start = _now(); }
        else _poll_stdin();
        if (_inkey_buffer.length === 0) return "";
    }
    const key = _inkey_buffer[0];
    _inkey_buffer = _inkey_buffer.slice(1);
    return key;
}
'''

JS_PRINT_RUNTIME = r'''
// ===== PRINT: columns, zones, TAB, SPC and the line wrap (port of src/print_column.py) =====
let _col = 0;  // cursor column on the screen, 0-based
let _width = 80;  // line width of the screen, set by WIDTH
function _advance(col, s) {
    // The column after sending s: a newline or CR goes to 0, a tab to the next multiple of 8,
    // a backspace one left; the other control characters do not move the cursor.
    for (let i = 0; i < s.length; i++) {
        const ch = s.charCodeAt(i);
        if (ch === 10 || ch === 13) col = 0;
        else if (ch === 9) col = (Math.floor(col / 8) + 1) * 8;
        else if (ch === 8) col = col > 0 ? col - 1 : 0;
        else if (ch >= 32) col++;
    }
    return col;
}
function _wrap_text(col, width, text, whole) {
    // MBASIC wraps lazily: a full line stays until the next printable character comes. A PRINT
    // item that does not fit in the rest of the line starts a new line first; one longer than
    // the width is split at the width. SPC (whole false) wraps one character at a time.
    let out = "";
    if (whole && col > 0 && col + text.length > width) { out += "\n"; col = 0; }
    for (let i = 0; i < text.length; i++) {
        const ch = text[i];
        if (ch >= " " && col >= width) { out += "\n"; col = 0; }
        out += ch;
        col = _advance(col, ch);
    }
    return out;
}
function _set_width(n) {
    n = _round_half_away(n);
    if (n < 1 || n > 255) _error("Illegal function call");
    return n;
}
function _width_of(f) { return f === null || f === undefined ? _width : 255; }
// items: [0, value, digits] | [1, tabColumn] | [2, count]; seps: ";" "," or "\n" after each item.
// On the screen an item that does not fit goes whole to the next line and a comma in the last
// zone starts a new line; a file splits at its width of 255 and pads. A value may be a function (an item that reads POS), called when its turn comes.
function _print_list(f, items, seps) {
    const w = _width_of(f), isScreen = f === null || f === undefined;
    // A screen of width 255 is infinite: nothing wraps, TAB and SPC counts are bytes.
    const inf = isScreen && w >= 255, ww = inf ? 1e9 : w, md = inf ? 256 : w;
    for (let i = 0; i < items.length; i++) {
        const it = items[i], sep = seps[i];
        let out = "";
        if (it[0] === 1) {
            // TAB(n): column n; a cursor already past it starts a new line first
            const n = _round_half_away(it[1]), col = _cur_col(f);
            const target = n < 1 ? 0 : (n - 1) % md;
            if (col > target) out = "\n" + " ".repeat(target);
            else out = " ".repeat(target - col);
        } else if (it[0] === 2) {
            // SPC(n): n spaces, n wrapping at the width
            out = _wrap_text(_cur_col(f), ww, " ".repeat(Math.max(0, _round_half_away(it[1])) % md), false);
        } else {
            const v = typeof it[1] === "function" ? it[1]() : it[1];
            out = _wrap_text(_cur_col(f), ww, _pstr(v, it[2]), isScreen);
        }
        if (out !== "") _emit(f, out);
        if (sep === ",") {
            // next 14-column zone; the last zone starts a new line
            const c = _cur_col(f), zone = (Math.floor(c / 14) + 1) * 14;
            // under width 14 no zone fits and there is no last-zone limit: pad, and the spaces wrap;
            // the column of an infinite screen stops at 255 and then pads too
            if (isScreen && w >= 14 && zone + 14 > w && !(inf && c >= 255)) _emit(f, "\n");
            else _emit(f, _wrap_text(c, ww, " ".repeat(zone - c), false));
        }
    }
    const last = seps.length ? seps[seps.length - 1] : "\n";
    if (last !== ";" && last !== ",") _emit(f, "\n");
}
'''

JS_PRINT_FILES = r'''
function _cur_col(f) {
    if (f === null || f === undefined) return _width >= 255 ? Math.min(_col, 255) : _col;
    const file = _files[f];
    if (!file || typeof file.content !== "string") return 0;
    return _advance(0, file.content.slice(file.content.lastIndexOf("\n") + 1));
}
function _emit(f, s) {
    if (f === null || f === undefined) _print(s, false); else _fprint(f, s, false);
}
'''

JS_PRINT_SCREEN = r'''
function _cur_col(f) { return _width >= 255 ? Math.min(_col, 255) : _col; }
function _emit(f, s) { _print(s, false); }
'''

JS_USING_RUNTIME = r'''
// ===== PRINT USING (port of UsingFormatter in src/basic_builtins.py) =====
function _using_parse_numeric(fmt, start) {
    const spec = {digit_count: 0, has_decimal: false, digits_after_decimal: 0, leading_sign: false,
        trailing_sign: false, trailing_minus_only: false, dollar_sign: false, asterisk_fill: false,
        comma: false, exponential: false, end_pos: start};
    let i = start;
    if (fmt.substr(i, 3) === "**$") { spec.asterisk_fill = true; spec.dollar_sign = true; spec.digit_count += 3; i += 3; }
    else if (fmt.substr(i, 2) === "**") { spec.asterisk_fill = true; spec.digit_count += 2; i += 2; }
    else if (fmt.substr(i, 2) === "$$") { spec.dollar_sign = true; spec.digit_count += 2; i += 2; }
    else if (fmt[i] === "+") { spec.leading_sign = true; i += 1; }
    let decimal_found = false;
    while (i < fmt.length) {
        const ch = fmt[i];
        if (ch === "#") { spec.digit_count++; if (decimal_found) spec.digits_after_decimal++; i++; }
        else if (ch === ".") { if (!decimal_found) { spec.has_decimal = true; decimal_found = true; i++; } else break; }
        else if (ch === ",") { spec.comma = true; spec.digit_count++; i++; }
        else break;
    }
    if (fmt.substr(i, 4) === "^^^^") { spec.exponential = true; i += 4; }
    if (i < fmt.length && !spec.leading_sign) {
        if (fmt[i] === "+") { spec.trailing_sign = true; i++; }
        else if (fmt[i] === "-") { spec.trailing_minus_only = true; i++; }
    }
    spec.end_pos = i;
    spec.lead = spec.digit_count - spec.digits_after_decimal + (spec.leading_sign ? 1 : 0);
    spec.trail = spec.has_decimal ? spec.digits_after_decimal + 1 : 0;
    return spec;
}
function _using_parse(fmt) {
    const fields = [];
    let i = 0;
    while (i < fmt.length) {
        const ch = fmt[i];
        if (ch === "_" && i + 1 < fmt.length) { fields.push({kind: "literal", text: fmt[i + 1]}); i += 2; continue; }
        if (ch === "!") { fields.push({kind: "string", type: "first"}); i++; continue; }
        if (ch === "&") { fields.push({kind: "string", type: "full"}); i++; continue; }
        if (ch === "\\") {
            let j = i + 1, spaces = 0;
            while (j < fmt.length && fmt[j] === " ") { spaces++; j++; }
            if (j < fmt.length && fmt[j] === "\\") {
                fields.push({kind: "string", type: "fixed", width: 2 + spaces});
                i = j + 1;
            } else {
                fields.push({kind: "literal", text: ch});
                i++;
            }
            continue;
        }
        if ("#.+-".includes(ch) || (ch === "*" && i + 1 < fmt.length && "*$".includes(fmt[i + 1])) ||
            (ch === "$" && i + 1 < fmt.length && fmt[i + 1] === "$")) {
            const spec = _using_parse_numeric(fmt, i);
            if (spec.digit_count) { spec.kind = "numeric"; fields.push(spec); i = spec.end_pos; continue; }
            fields.push({kind: "literal", text: ch});
            i++;
            continue;
        }
        fields.push({kind: "literal", text: ch});
        i++;
    }
    return fields;
}
// The magnitude of v as [digits, exp10] (digits[0] has weight 10^exp), rounded the way PRINT rounds.
function _using_magnitude(v, digits) {
    const a = Math.abs(digits === 0 ? Math.trunc(v) : v);
    if (a === 0) return ["0", 0];
    if (digits === 0) {
        const m = /^(\d)(?:\.(\d+))?e([+-]\d+)$/.exec(a.toExponential());
        return [(m[1] + (m[2] || "")).replace(/0+$/, ""), parseInt(m[3], 10)];
    }
    if (digits === 16) {
        // Start from the shortest decimal form of the double, as the interpreter does (1D-11 must not carry).
        const m = /^(\d)(?:\.(\d+))?e([+-]\d+)$/.exec(a.toExponential());
        return _round_digits(m[1] + (m[2] || ""), parseInt(m[3], 10), 16);
    }
    return _sig_digits(a, digits);
}
// Round [ds, exp] to `decimals` places: returns [int digits without leading zeros, fraction digits].
function _using_fixed(ds, exp, decimals) {
    let ip, fp;
    if (exp >= 0) { ip = ds.slice(0, exp + 1).padEnd(exp + 1, "0"); fp = ds.slice(exp + 1); }
    else { ip = "0"; fp = "0".repeat(-exp - 1) + ds; }
    if (fp.length > decimals) {
        const up = fp.charCodeAt(decimals) >= 53;
        fp = fp.slice(0, decimals);
        if (up) {
            let all = (BigInt(ip + fp) + 1n).toString().padStart(ip.length + decimals, "0");
            ip = all.slice(0, all.length - decimals);
            fp = all.slice(all.length - decimals);
        }
    } else {
        fp = fp.padEnd(decimals, "0");
    }
    return [ip.replace(/^0+/, ""), fp];
}
function _using_commas(s) {
    let out = "";
    for (let i = 0; i < s.length; i++) {
        if (i > 0 && (s.length - i) % 3 === 0) out += ",";
        out += s[i];
    }
    return out;
}
function _using_number(v, spec, digits) {
    const lead = spec.lead, trail = spec.trail, decimals = trail ? trail - 1 : 0;
    if (lead + trail > 24) _error("Illegal function call");
    if (v !== v || v === Infinity || v === -Infinity) return String(v);
    const negative = v < 0;
    let [ds, exp] = _using_magnitude(v, digits);
    // 16 digits or more overflow the fixed layout into '%' and the PRINT form of the number, sign dropped.
    if (!spec.exponential && exp >= 16) return "% " + _fmt_num(Math.abs(v), digits);
    let int_str, frac_str, suffix = "";
    if (spec.exponential) {
        const trailing = spec.trailing_sign || spec.trailing_minus_only;
        const int_digits = trailing ? lead : lead - 1;
        let exponent = 0;
        if (ds !== "0") {
            exponent = exp + 1 - int_digits;
            [int_str, frac_str] = _using_fixed(ds, exp - exponent, decimals);
        } else {
            [int_str, frac_str] = _using_fixed("0", 0, decimals);
        }
        suffix = (digits > 6 ? "D" : "E") + (exponent >= 0 ? "+" : "-") + String(Math.abs(exponent)).padStart(2, "0");
    } else {
        [int_str, frac_str] = _using_fixed(ds, exp, decimals);
        if (spec.comma) int_str = _using_commas(int_str);
    }
    // Lay the digits, sign, dollar and fill into the field.
    const trailing_sign = spec.trailing_sign || spec.trailing_minus_only;
    const sign_slot = !trailing_sign && (negative || spec.leading_sign);
    let needed = int_str.length + (spec.dollar_sign ? 1 : 0) + (sign_slot ? 1 : 0);
    if (!int_str && (needed + 1 <= lead || !trail)) { int_str = "0"; needed += 1; }
    const body = int_str + (trail ? "." + frac_str : "") + suffix;
    const sign = sign_slot ? (negative ? "-" : "+") : "";
    let out;
    if (needed > lead) {
        out = "%" + sign + (spec.dollar_sign ? "$" : "") + body;
    } else {
        const content = sign + (spec.dollar_sign ? "$" : "") + body;
        out = (spec.asterisk_fill ? "*" : " ").repeat(Math.max(0, lead + trail + suffix.length - content.length)) + content;
    }
    if (spec.trailing_sign) out += negative ? "-" : "+";
    else if (spec.trailing_minus_only) out += negative ? "-" : " ";
    return out;
}
function _using_string(v, f) {
    v = String(v);
    if (f.type === "first") return v ? v[0] : " ";
    if (f.type === "full") return v;
    return v.length >= f.width ? v.slice(0, f.width) : v.padEnd(f.width, " ");
}
function _print_using(fmt, values, digits) {
    if (!fmt) _error("Illegal function call");
    const fields = _using_parse(fmt);
    const has_field = fields.some(f => f.kind !== "literal");
    let result = "", idx = 0;
    outer:
    for (;;) {
        for (const f of fields) {
            if (f.kind === "literal") { result += f.text; continue; }
            if (idx >= values.length) break outer;
            if (f.kind === "string") {
                result += _using_string(values[idx], f);
            } else {
                let v = values[idx];
                if (typeof v === "string") { v = parseFloat(v); if (v !== v) v = 0; }
                else if (v === true) v = -1; else if (v === false) v = 0;
                result += _using_number(v, f, digits[idx] === undefined ? 6 : digits[idx]);
            }
            idx++;
        }
        if (idx >= values.length || !has_field) break;
    }
    return [result, values.length > 0 && !has_field];
}
function _print_using_stmt(f, fmt, values, digits, trailing) {
    const [text, bad] = _print_using(fmt, values, digits);
    _emit(f, text + (trailing ? "" : "\n"));
    if (bad) _error("Illegal function call");
}
'''

def _js_number(value) -> str:
    """JavaScript source for a numeric literal; Python writes inf and nan, JavaScript does not."""
    if isinstance(value, float):
        if value != value:
            return 'NaN'
        if value in (float('inf'), float('-inf')):
            # Never write an infinity: MBASIC has none, only machine infinity.
            return repr(machine_infinity(DOUBLE_DIGITS, value < 0))
        return repr(value)
    return str(value)


# BASIC logical operator -> runtime function (JS_LOGICAL_RUNTIME)
LOGICAL_HELPERS = {'AND': '_and', 'OR': '_or', 'XOR': '_xor', 'EQV': '_eqv', 'IMP': '_imp'}

# The browser build gives the page time to run. A program that can loop is written as _run(pc), which
# runs until the end or until it has to give the page time, and the driver main(), which calls _run again
# at the pc it returned. The check counts jumps back and looks at the clock only when JS_YIELD_BUDGET
# jumps have gone by; under Node _browser is false and _run never returns early. Why not an await in
# the loop: an await point inside a hot loop makes V8 compile the loop slower, even when it never runs.
JS_YIELD_BUDGET = 2000
JS_YIELD_MS = 12


def yield_check(target: str) -> str:
    """Code before a jump back to target (a JavaScript expression): return to the driver now and then."""
    return (f'if (--_budget < 0) {{ _budget = {JS_YIELD_BUDGET}; '
            f'if (_browser && _now() - _slice_start >= {JS_YIELD_MS}) return {target}; }}')


# A same-line WHILE loop is a JavaScript loop and cannot return to the driver: _run is async then
JS_YIELD_CHECK_AWAIT = (f'if (--_budget < 0) {{ _budget = {JS_YIELD_BUDGET}; '
                        f'if (_browser && _now() - _slice_start >= {JS_YIELD_MS}) {{ await _yield(); _slice_start = _now(); }} }}')

# Case labels for the statements in the middle of a line. BASIC line numbers end at 65529.
CONT_LABEL_BASE = 100000

# Statements that must be able to continue with the statement after them
_RESUME_STATEMENTS = (ForStatementNode, GosubStatementNode, OnGosubStatementNode)
# Statements after which the rest of the line is not reached in order
_JUMP_STATEMENTS = (GotoStatementNode, GosubStatementNode, ReturnStatementNode,
                    EndStatementNode, SystemStatementNode, ResumeStatementNode, WendStatementNode)


class LinePlan:
    """The steps of one program line and the case labels inside the line."""

    def __init__(self, line_number: int):
        self.line_number = line_number
        self.steps: List[tuple] = []
        self.labels: Dict[int, int] = {}   # step index -> case label
        self.targets: Dict[int, Optional[int]] = {}  # step index of an 'if' or 'jump' -> where to continue


def walk_statements(statements):
    """Every statement in text order, including the ones inside IF ... THEN ... ELSE."""
    for stmt in statements:
        yield stmt
        if isinstance(stmt, IfStatementNode):
            yield from walk_statements(stmt.then_statements or [])
            yield from walk_statements(stmt.else_statements or [])


JS_FILL_KEYS = r'''
function _fill_keys(want, soft) {
    // Add keys to _inkey_buffer. Returns false only at end of input, and only when soft is set.
    // The caller awaits the result. Browser: a Promise that the keydown handler resolves with the
    // next key, so the page keeps running while the program waits. Node: a plain value (blocking read).
    if (typeof window !== "undefined") {
        return new Promise((resolve) => { _key_waiter = resolve; });
    }
    // Node: block on fd 0. A chunk may hold several lines; the rest stays in _inkey_buffer.
    const fs = require("fs");
    // Decode as UTF-8 (StringDecoder keeps a multi-byte character split across reads whole), so text
    // read here prints back unchanged. Consequence: INPUT$(n) counts characters, not bytes.
    if (typeof _stdin_decoder === "undefined") globalThis._stdin_decoder = new (require("string_decoder").StringDecoder)("utf8");
    const buf = Buffer.alloc(want);
    for (;;) {
        let got = 0;
        try {
            got = fs.readSync(0, buf, 0, want, null);
        } catch (e) {
            if (e.code === "EAGAIN") continue;  // stdin not ready yet: keep waiting
            if (e.code === "EOF") got = 0; else throw e;
        }
        if (got === 0) {
            if (soft) return false;
            _error("Input past end");
        }
        const txt = _stdin_decoder.write(buf.subarray(0, got));
        if (txt === "") continue;  // only part of a multi-byte character so far
        _inkey_buffer += txt;
        return true;
    }
}
'''

JS_INPUT_RUNTIME = r'''
// INPUT and LINE INPUT. The generated main() is async. Node reads stdin with a blocking
// fs.readSync (through _fill_keys, one buffer shared with INPUT$). The browser waits for keydown
// events, echoes the typed characters into the page and ends the line at Enter.
// At end of stdin Node stops with "?Input past end" (exit 1) instead of waiting or looping.
async function _read_line(prompt, keep) {
    // keep (INPUT; with no newline after the answer): the cursor stays after the typed text
    _print(prompt, false);
    if (typeof window !== "undefined") {
        let typed = "";
        for (;;) {
            if (_inkey_buffer.length === 0) await _fill_keys(1);
            const ch = _inkey_buffer[0];
            _inkey_buffer = _inkey_buffer.slice(1);
            if (ch === "\r" || ch === "\n") { if (!keep) _print(""); return typed; }
            if (ch === "\x03") _error("Break");
            if (ch === "\b" || ch === "\x7f") {
                if (typed.length > 0) { typed = typed.slice(0, -1); _unprint_char(); }
                continue;
            }
            typed += ch;
            _print(ch, false);
        }
    }
    for (;;) {
        const nl = _inkey_buffer.indexOf("\n");
        if (nl >= 0) {
            let line = _inkey_buffer.slice(0, nl);
            _inkey_buffer = _inkey_buffer.slice(nl + 1);
            if (line.endsWith("\r")) line = line.slice(0, -1);
            if (keep) _col += line.length; else _col = 0;  // the Enter that ended the line
            return line;
        }
        if (!(await _fill_keys(4096, true))) {
            if (_inkey_buffer.length === 0) _error("Input past end");
            const rest = _inkey_buffer;
            _inkey_buffer = "";
            if (keep) _col += rest.length; else _col = 0;
            return rest;
        }
    }
}

async function _line_input(prompt) {
    return await _read_line(prompt);
}

function _input_fields(line) {
    // Split an INPUT line at commas. A field may be "quoted" (commas allowed inside).
    // Returns null when the line is malformed, as MBASIC then prints ?Redo from start.
    const out = [];
    const n = line.length;
    let i = 0;
    for (;;) {
        while (i < n && (line[i] === " " || line[i] === "\t")) i++;
        let s, q = false;
        if (line[i] === '"') {
            q = true;
            i++;
            const j = line.indexOf('"', i);
            if (j < 0) { s = line.slice(i); i = n; } else { s = line.slice(i, j); i = j + 1; }
            while (i < n && (line[i] === " " || line[i] === "\t")) i++;
            if (i < n && line[i] !== ",") return null;
        } else {
            let j = line.indexOf(",", i);
            if (j < 0) j = n;
            s = line.slice(i, j).replace(/[ \t]+$/, "");
            i = j;
        }
        out.push({s: s, q: q});
        if (i >= n) break;
        i++;  // the comma
    }
    return out;
}

function _input_number(text, type) {
    // type: "I" integer, "F" single, "N" double. Returns null for ?Redo from start.
    const t = text.replace(/^[ \t]+|[ \t]+$/g, "");
    let s = text.replace(/[ \t]/g, "");  // MBASIC ignores blanks inside a number: "1 2" is 12
    if (s === "") return 0;
    let v;
    if (t[0] === "&") {
        // &H: hex digits, no blanks. & and &O: octal digits, blanks ignored; 8 or 9 is a Syntax error.
        const hex = t[1] === "H" || t[1] === "h";
        let digits;
        if (hex) {
            digits = t.slice(2);
            if (!/^[0-9A-Fa-f]*$/.test(digits)) return null;
        } else {
            digits = s.slice(t[1] === "O" || t[1] === "o" ? 2 : 1);
            const lead = /^[0-9]*/.exec(digits)[0];
            if (/[89]/.test(lead)) _error("Syntax error");
            if (lead !== digits) return null;
        }
        v = digits === "" ? 0 : parseInt(digits, hex ? 16 : 8);
        if (v > 65535) _error("Overflow");
        if (v >= 32768) v -= 65536;
    } else {
        // A suffix is allowed only after a number without an exponent; % rounds to an integer.
        const m = /^([+-]?)(\d*\.?\d*)(?:[EeDd]([+-]?\d*)|([%!#]))?$/.exec(s);
        if (!m) return null;
        let digits = m[2] === "." ? "" : m[2];
        let exp = m[3] === undefined || m[3] === "" || m[3] === "+" || m[3] === "-" ? "0" : m[3];
        v = Number(m[1] + (digits === "" ? "0" : digits) + "e" + exp);
        if (m[4] === "%") {
            v = v < 0 ? -Math.round(-v) : Math.round(v);
            if (v > 32767 || v < -32768) _error("Overflow");
        }
    }
    if (type === "I") {
        v = v < 0 ? -Math.round(-v) : Math.round(v);  // INPUT rounds, half away from zero
        if (v > 32767 || v < -32768) _error("Overflow");
    } else if (type === "F") {
        v = Math.fround(v);
        if (!isFinite(v)) { _print("Overflow"); return null; }
    } else if (!isFinite(v)) {
        _print("Overflow");
        return null;
    }
    return v === 0 ? 0 : v;
}

function _input_parse(line, types) {
    const fields = _input_fields(line);
    if (fields === null || fields.length !== types.length) return null;
    const vals = [];
    for (let k = 0; k < types.length; k++) {
        if (types[k] === "S") {
            vals.push(fields[k].s);
        } else {
            if (fields[k].q) return null;
            const v = _input_number(fields[k].s, types[k]);
            if (v === null) return null;
            vals.push(v);
        }
    }
    return vals;
}

async function _input_vals(prompt, types, keep) {
    // types has one letter per variable: S string, I integer, F single, N double.
    for (;;) {
        const vals = _input_parse(await _read_line(prompt, keep), types);
        if (vals !== null) return vals;
        _print("?Redo from start");
    }
}
'''


JS_FINPUT_BODY = r'''
// Read one value: leading blanks and line ends are skipped, a "quoted" value may hold commas,
// an unquoted value ends at a comma or line end. Past the last value: ?Input past end.
const text = file.content;
let p = file.pos;
while (p < text.length && " \t\r\n".indexOf(text[p]) >= 0) p++;
if (p >= text.length) { file.pos = p; _error("Input past end"); }
let value = "";
if (text[p] === '"') {
    p++;
    while (p < text.length && text[p] !== '"') value += text[p++];
    if (p < text.length) p++;
    while (p < text.length && (text[p] === " " || text[p] === "\t")) p++;
} else {
    while (p < text.length && text[p] !== "," && text[p] !== "\n") value += text[p++];
    value = value.trim();
}
if (text[p] === ",") p++;
else if (text[p] === "\r" && text[p + 1] === "\n") p += 2;
else if (text[p] === "\n") p++;
file.pos = p;
return value;
'''

JS_KEYDOWN_BODY = r'''  let ch = "";
  if (e.key === "Enter") ch = "\r";
  else if (e.key === "Backspace") ch = "\b";
  else if ((e.ctrlKey || e.metaKey) && !e.altKey) { if (e.key === "c" || e.key === "C") ch = "\x03"; }
  else if (e.key && e.key.length === 1) ch = e.key;
  if (ch === "") return;
  _inkey_buffer += ch;
  if (_key_waiter) {
    if (e.preventDefault) e.preventDefault();  // no page scroll on Space, no history Back on Backspace
    const w = _key_waiter;
    _key_waiter = null;
    w(true);
  }'''


class JavaScriptBackend(CodeGenBackend):
    """
    JavaScript code generator for browser and Node.js execution.

    Features:
    - Switch-based control flow (PC variable)
    - Variable-indexed FOR loops
    - Built-in BASIC functions
    - Environment detection (browser vs Node.js)
    - Self-contained runtime
    """

    def __init__(self, symbols: SymbolTable, config: Optional[Dict[str, Any]] = None):
        super().__init__(symbols)
        self.indent_level = 0
        self.line_labels: Set[int] = set()  # Line numbers that need case statements
        self.next_line_map: Dict[int, Optional[int]] = {}  # Map line -> next line
        self.config = config or {}

        # Track what features are used
        self.uses_input = False
        self.uses_line_input = False
        self.uses_write = False
        self.uses_lprint = False
        self.uses_gosub = False
        self.uses_data = False
        self.uses_random = False
        self.uses_error_handling = False
        self.uses_file_io = False
        self.uses_input_func = False  # INPUT$(n) / INPUT$(n, #f) function
        self.uses_inkey = False  # INKEY$ function
        self.can_loop = False  # the program has a FOR, a WHILE or a jump to the same or an earlier line
        self.async_fns: Set[str] = set()  # DEF FN names (without FN) whose body can wait for the keyboard

        # DATA/READ/RESTORE support
        self.data_values: List[Any] = []
        self.data_types: List[str] = []  # 'number' or 'string'

        # DEF FN functions
        self.def_fn_functions: List[DefFnStatementNode] = []

        # FOR/NEXT matching, keyed by id() of the statement node:
        # for_to_next: FOR -> the NEXT that closes it; next_line_of: NEXT -> its line number
        self.for_to_next: Dict[int, Any] = {}
        self.next_line_of: Dict[int, int] = {}
        self.matched_next: Set[int] = set()
        # Bare NEXT -> JS name of the variable of the FOR it closes
        self.next_var_map: Dict[int, str] = {}
        # WHILE/WEND matching, keyed by id(): while_to_wend: WHILE -> its WEND; wend_to_while: WEND -> its WHILE;
        # while_target: WHILE -> line or label of the WHILE step itself (where WEND jumps back to)
        self.while_to_wend: Dict[int, Any] = {}
        self.wend_to_while: Dict[int, Any] = {}
        self.while_target: Dict[int, int] = {}

        # Mid-line resume points. FOR, GOSUB, ON GOSUB and a NEXT that closes a FOR must be
        # able to continue with the statement after them, so that statement gets its own case
        # label (a number from CONT_LABEL_BASE up) when more statements follow on the line.
        self.line_plans: Dict[int, Any] = {}
        self.after_target: Dict[int, Optional[int]] = {}  # id(statement) -> line or label to continue at
        self._next_label = CONT_LABEL_BASE
        self._cur_line = 0  # number of the line whose code is being written
        self.yield_checks = False  # True while the browser copy of the program is written

    def get_file_extension(self) -> str:
        """JavaScript files use .js extension"""
        return '.js'

    def get_compiler_command(self, source_file: str, output_file: str) -> List[str]:
        """
        No compilation needed for JavaScript - it's interpreted.
        For Node.js, can make executable with shebang and chmod.
        """
        return []  # No compilation step

    @property
    def node_async(self) -> bool:
        """True when main() (the copy of the program that Node runs) has an await: INPUT, LINE INPUT, INPUT$ or INKEY$."""
        return self.uses_input or self.uses_line_input or self.uses_input_func or self.uses_inkey

    @property
    def page_async(self) -> bool:
        """True when _run() (the browser copy) has an await: the same as main()."""
        return self.node_async

    def indent(self) -> str:
        """Return current indentation"""
        return '  ' * self.indent_level

    def _token_to_operator(self, token: TokenType) -> str:
        """Convert TokenType to operator string"""
        operator_map = {
            TokenType.PLUS: '+',
            TokenType.MINUS: '-',
            TokenType.MULTIPLY: '*',
            TokenType.DIVIDE: '/',
            TokenType.POWER: '^',
            TokenType.BACKSLASH: '//',  # Integer division (JavaScript doesn't have this, use Math.floor)
            TokenType.MOD: '%',
            TokenType.EQUAL: '=',
            TokenType.LESS_THAN: '<',
            TokenType.GREATER_THAN: '>',
            TokenType.LESS_EQUAL: '<=',
            TokenType.GREATER_EQUAL: '>=',
            TokenType.NOT_EQUAL: '<>',
            TokenType.AND: 'AND',
            TokenType.OR: 'OR',
            TokenType.NOT: 'NOT',
            TokenType.XOR: 'XOR',
            TokenType.EQV: 'EQV',
            TokenType.IMP: 'IMP',
        }
        return operator_map.get(token, str(token))

    def generate(self, program: ProgramNode) -> str:
        """Generate JavaScript code for the program"""
        # Analysis passes
        self._collect_line_labels(program)
        self._collect_data_values(program)
        self._collect_def_fn(program)
        self._analyze_features(program)
        self._match_for_next(program)
        self._match_while_wend(program)
        self._plan_lines(program)

        code = []

        # Header
        code.append('#!/usr/bin/env node')
        code.append('// Generated by MBASIC-2025 JavaScript Backend')
        code.append(f'// Source: {self.config.get("source_file", "program.bas")}')
        code.append('')
        code.append('(function() {')
        code.append("  'use strict';")
        code.append('')

        self.indent_level = 1

        # Runtime library
        code.append(self.indent() + '// ===== Runtime Library =====')
        code.extend(self._generate_runtime())
        code.append('')

        # Variables
        code.append(self.indent() + '// ===== Variables =====')
        code.extend(self._generate_variables())
        code.append('')

        # DEF FN functions
        if self.def_fn_functions:
            code.append(self.indent() + '// ===== DEF FN Functions =====')
            code.extend(self._generate_def_fn_functions())
            code.append('')

        # Main program
        code.append(self.indent() + '// ===== Program =====')
        first_line = min(line.line_number for line in program.lines) if program.lines else 10
        code.extend(self._generate_program(program, first_line, page=False))
        if self.can_loop:
            # The same program again, for the browser: its jumps back give the page time to run
            # (yield_check). Node runs the copy above, which has no check at all and is as fast as before.
            code.append('')
            code.extend(self._generate_program(program, first_line, page=True))
        code.append('')

        # Run the program
        code.append(self.indent() + '// ===== Execute =====')
        code.append(self.indent() + 'try {')
        self.indent_level += 1
        node_start = 'main().catch(_fatal);' if self.node_async else 'main();'
        if self.can_loop:
            code.append(self.indent() + f'if (_browser) {{ _main_page().catch(_fatal); }} else {{ {node_start} }}')
        else:
            code.append(self.indent() + node_start)
        self.indent_level -= 1
        code.append(self.indent() + '} catch (e) {')
        self.indent_level += 1
        code.append(self.indent() + '_fatal(e);')
        self.indent_level -= 1
        code.append(self.indent() + '}')

        self.indent_level = 0
        code.append('})();')
        code.append('')

        return '\n'.join(code)

    def _generate_program(self, program: ProgramNode, first_line: int, page: bool) -> List[str]:
        """The switch loop of the program.

        page=False: main(), which runs the program to its end. page=True (browser, programs that can
        loop): _run(pc), which returns the pc of a jump back when the page needs time, and the driver
        _main_page(), which waits for the page and calls _run again at that pc.
        """
        code = []
        self.yield_checks = page
        prefix = 'async ' if (self.page_async if page else self.node_async) else ''
        if page:
            code.append(self.indent() + '// _run(pc) runs the program from line pc until it ends or until a jump back at which')
            code.append(self.indent() + '// the browser needs time. It then returns the pc of that jump (see yield_check).')
            code.append(self.indent() + f'{prefix}function _run(_pc) {{')
            self.indent_level += 1
            code.append(self.indent() + f'let _budget = {JS_YIELD_BUDGET};  // jumps back left before the next look at the clock')
        else:
            code.append(self.indent() + f'{prefix}function main() {{')
            self.indent_level += 1
            # Initialize PC to first line
            code.append(self.indent() + f'let _pc = {first_line};')
            code.append('')

        # Main execution loop with switch statement
        code.append(self.indent() + 'while (_pc !== null) {')
        self.indent_level += 1
        # A run-time error (Overflow, Division by zero, ...) is caught here to note the BASIC line that
        # was running (_fatal prints it). With ON ERROR armed it jumps to the handler, with ERR and ERL set.
        code.append(self.indent() + 'try {')
        self.indent_level += 1
        code.append(self.indent() + 'switch (_pc) {')
        self.indent_level += 1

        # Generate code for each line
        for line in program.lines:
            code.extend(self._generate_line(line))

        # Default case - unknown line
        code.append(self.indent() + 'default:')
        self.indent_level += 1
        code.append(self.indent() + '_error(`Undefined line number ${_pc}`);')
        code.append(self.indent() + 'return;')
        self.indent_level -= 1

        self.indent_level -= 1
        code.append(self.indent() + '}')  # End switch
        self.indent_level -= 1
        code.append(self.indent() + '} catch (e) {')
        self.indent_level += 1
        code.append(self.indent() + 'if (e && e.basicLine === undefined) e.basicLine = _line_of(_pc);')
        if self.uses_error_handling:
            code.append(self.indent() + 'if (e && e.basicCode && _error_handler && !_in_error_handler) { _pc = _trigger_error(e.basicCode, e.basicLine); continue; }')
        code.append(self.indent() + 'throw e;')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        self.indent_level -= 1
        code.append(self.indent() + '}')  # End while
        if self.uses_error_handling:
            # Ran off the end of the program inside a handler (END returns above)
            code.append(self.indent() + 'if (_in_error_handler) _error("No RESUME");')

        self.indent_level -= 1
        code.append(self.indent() + '}')  # End main() or _run()
        if page:
            code.append('')
            code.append(self.indent() + 'async function _main_page() {')
            code.append(self.indent() + f'    let _pc = {first_line};')
            code.append(self.indent() + '    while (_pc != null) {')
            code.append(self.indent() + f'        _pc = {"await " if self.page_async else ""}_run(_pc);')
            code.append(self.indent() + '        if (_pc != null) { await _yield(); _slice_start = _now(); }  // _run asked for time')
            code.append(self.indent() + '    }')
            code.append(self.indent() + '}')
        self.yield_checks = False
        return code

    def _collect_line_labels(self, program: ProgramNode):
        """Collect all line numbers that are referenced"""
        # All lines need labels in switch statement
        for i, line in enumerate(program.lines):
            self.line_labels.add(line.line_number)

            # Build next line map
            if i + 1 < len(program.lines):
                self.next_line_map[line.line_number] = program.lines[i + 1].line_number
            else:
                self.next_line_map[line.line_number] = None  # Last line

    def _collect_data_values(self, program: ProgramNode):
        """Collect all DATA values"""
        for line in program.lines:
            for stmt in line.statements:
                if isinstance(stmt, DataStatementNode):
                    for value in stmt.values:
                        # Extract actual values from AST nodes
                        if isinstance(value, StringNode):
                            self.data_values.append(value.value)
                            self.data_types.append('string')
                        elif isinstance(value, NumberNode):
                            self.data_values.append(value.value)
                            self.data_types.append('number')
                        elif isinstance(value, str):
                            self.data_values.append(value)
                            self.data_types.append('string')
                        else:
                            # For other types, try to get the value
                            self.data_values.append(value)
                            self.data_types.append('number')

    def _collect_def_fn(self, program: ProgramNode):
        """Collect all DEF FN statements"""
        for line in program.lines:
            for stmt in line.statements:
                if isinstance(stmt, DefFnStatementNode):
                    self.def_fn_functions.append(stmt)

    def _match_for_next(self, program: ProgramNode):
        """Match FOR statements with their corresponding NEXT statements (by position in the text)"""
        for_stack = []  # Stack of (FOR statement, lower-case BASIC name, JS name) for nested loops

        for line in program.lines:
            for stmt in walk_statements(line.statements):
                if isinstance(stmt, ForStatementNode):
                    var_name = stmt.variable.name.lower()
                    # JS name of the loop variable (type suffix and DEFINT type included), as _generate_for writes it
                    js_name = self._mangle_var_name(stmt.variable.name + (stmt.variable.type_suffix or ''))
                    for_stack.append((stmt, var_name, js_name))
                elif isinstance(stmt, NextStatementNode):
                    self.next_line_of[id(stmt)] = line.line_number
                    if stmt.variables:
                        # NEXT J,I closes the J loop, then the I loop
                        for var in stmt.variables:
                            var_name = var.name.lower()
                            for j in range(len(for_stack) - 1, -1, -1):
                                if for_stack[j][1] == var_name:
                                    self._pair_for_next(for_stack.pop(j)[0], stmt)
                                    break
                    elif for_stack:
                        # NEXT without variable - closes the most recent FOR
                        for_stmt, var_name, js_name = for_stack.pop()
                        self._pair_for_next(for_stmt, stmt)
                        # The JS name of the FOR variable, not the BASIC name
                        self.next_var_map[id(stmt)] = js_name

    def _match_while_wend(self, program: ProgramNode):
        """Match WHILE statements with their WEND statements (by position in the text, like NEXT)"""
        stack = []
        for line in program.lines:
            for stmt in walk_statements(line.statements):
                if isinstance(stmt, WhileStatementNode):
                    stack.append(stmt)
                elif isinstance(stmt, WendStatementNode):
                    self.next_line_of[id(stmt)] = line.line_number
                    if not stack:
                        continue
                    while_stmt = stack.pop()
                    self.while_to_wend[id(while_stmt)] = stmt
                    self.wend_to_while[id(stmt)] = while_stmt

    def _pair_for_next(self, for_stmt, next_stmt):
        self.for_to_next[id(for_stmt)] = next_stmt
        self.matched_next.add(id(next_stmt))

    def _needs_resume_point(self, stmt) -> bool:
        return (isinstance(stmt, _RESUME_STATEMENTS) or id(stmt) in self.matched_next
                or id(stmt) in self.wend_to_while)

    def _if_needs_flat(self, stmt: IfStatementNode, tail: bool) -> bool:
        """True when a statement inside the IF needs a resume point after itself.

        The statements of such an IF cannot stay in a JavaScript if block, because a case label
        cannot stand inside a block. The IF is written as jumps and labels instead.
        """
        def inner(statements, tail):
            for i, s in enumerate(statements):
                last = tail and i == len(statements) - 1
                if (self._needs_resume_point(s) and not last) or id(s) in self.while_to_wend:
                    return True
                if isinstance(s, IfStatementNode):
                    if inner(s.then_statements or [], last) or inner(s.else_statements or [], last):
                        return True
            return False
        return inner(stmt.then_statements or [], tail) or inner(stmt.else_statements or [], tail)

    def _plan_lines(self, program: ProgramNode):
        """Cut each line into steps and find the places where execution must be able to resume.

        A step is ('stmt', statement), ('if', IF statement, position to jump to when false),
        ('goto', line) or ('jump', position). A position is a step index; the code generator puts
        a case label there when it is not the end of the line.
        """
        for line in program.lines:
            plan = LinePlan(line.line_number)
            statements = line.statements
            for i, stmt in enumerate(statements):
                if isinstance(stmt, IfStatementNode) and self._if_needs_flat(stmt, i == len(statements) - 1):
                    self._flatten_if(stmt, plan)
                else:
                    plan.steps.append(('stmt', stmt))
            self.line_plans[line.line_number] = plan
            # Ask for the resume points now, so that every label exists before code is written
            for j, step in enumerate(plan.steps):
                if step[0] == 'stmt' and self._needs_resume_point(step[1]):
                    self.after_target[id(step[1])] = self._position_target(plan, j + 1)
                if step[0] == 'stmt' and id(step[1]) in self.while_to_wend:
                    # WEND jumps back to the WHILE step itself, to test the condition again
                    self.while_target[id(step[1])] = (line.line_number if j == 0
                                                      else self._position_target(plan, j))
                elif step[0] in ('if', 'jump'):
                    plan.targets[j] = self._position_target(plan, step[2] if step[0] == 'if' else step[1])

    def _flatten_if(self, stmt: IfStatementNode, plan: 'LinePlan'):
        """Write IF cond THEN a ELSE b as steps: test, a, jump to end, b."""
        steps = plan.steps
        test = len(steps)
        steps.append(('if', stmt, None))  # the jump position is set below
        if stmt.then_line_number is not None:
            steps.append(('goto', stmt.then_line_number))
        else:
            self._flatten_statements(stmt.then_statements or [], plan)
        has_else = bool(stmt.else_statements) or stmt.else_line_number is not None
        jump = None
        if has_else:
            jump = len(steps)
            steps.append(('jump', None))
            else_pos = len(steps)
            if stmt.else_line_number is not None:
                steps.append(('goto', stmt.else_line_number))
            else:
                self._flatten_statements(stmt.else_statements, plan)
        end_pos = len(steps)
        steps[test] = ('if', stmt, else_pos if has_else else end_pos)
        if has_else:
            steps[jump] = ('jump', end_pos)

    def _flatten_statements(self, statements, plan: 'LinePlan'):
        for stmt in statements:
            if isinstance(stmt, IfStatementNode):
                self._flatten_if(stmt, plan)
            else:
                plan.steps.append(('stmt', stmt))

    def _position_target(self, plan: 'LinePlan', pos: int) -> Optional[int]:
        """Where to continue to run the step at index pos: a label, or the next line at the end of the line."""
        if pos >= len(plan.steps):
            return self.next_line_map.get(plan.line_number)
        if pos not in plan.labels:
            plan.labels[pos] = self._next_label
            self._next_label += 1
        return plan.labels[pos]

    def _after(self, stmt, line_number: int) -> Optional[int]:
        """Line or label that follows a statement (the next line when the statement ends its line)."""
        if id(stmt) in self.after_target:
            return self.after_target[id(stmt)]
        return self.next_line_map.get(line_number)

    def _analyze_features(self, program: ProgramNode):
        """Analyze which features the program uses"""
        for line in program.lines:
            for stmt in walk_statements(line.statements):
                if isinstance(stmt, InputStatementNode):
                    if stmt.file_number:
                        self.uses_file_io = True
                    else:
                        self.uses_input = True
                elif isinstance(stmt, LineInputStatementNode):
                    if stmt.file_number:
                        self.uses_file_io = True
                    else:
                        self.uses_line_input = True
                elif isinstance(stmt, (PrintStatementNode, PrintUsingStatementNode)):
                    if stmt.file_number:
                        self.uses_file_io = True
                elif isinstance(stmt, WriteStatementNode):
                    if stmt.file_number:
                        self.uses_file_io = True
                    else:
                        self.uses_write = True
                elif isinstance(stmt, LprintStatementNode):
                    if stmt.file_number:
                        self.uses_file_io = True
                    else:
                        self.uses_lprint = True
                elif isinstance(stmt, (OpenStatementNode, CloseStatementNode, ResetStatementNode)):
                    self.uses_file_io = True
                elif isinstance(stmt, (GosubStatementNode, OnGosubStatementNode)):
                    self.uses_gosub = True
                elif isinstance(stmt, ReadStatementNode):
                    self.uses_data = True
                elif isinstance(stmt, RestoreStatementNode):
                    self.uses_data = True
                elif isinstance(stmt, (OnErrorStatementNode, ErrorStatementNode, ResumeStatementNode)):
                    self.uses_error_handling = True
                if self._can_loop(stmt, line.line_number):
                    self.can_loop = True
                # Check for RND function in expressions
                self._check_for_rnd(stmt, set())
        self._find_async_fns()

    @staticmethod
    def _can_loop(stmt, line_number: int) -> bool:
        """True for a statement that can start a loop: FOR, WHILE, an error handler, or a jump back."""
        if isinstance(stmt, (ForStatementNode, NextStatementNode, WhileStatementNode, WendStatementNode,
                             OnErrorStatementNode, ResumeStatementNode)):
            return True
        targets = []
        if isinstance(stmt, (GotoStatementNode, GosubStatementNode)):
            targets = [stmt.line_number]
        elif isinstance(stmt, (OnGotoStatementNode, OnGosubStatementNode)):
            targets = list(stmt.line_numbers)
        elif isinstance(stmt, IfStatementNode):
            targets = [t for t in (stmt.then_line_number, stmt.else_line_number) if t is not None]
        return any(t <= line_number for t in targets)

    @staticmethod
    def _called_functions(node, found=None, visited=None):
        """Names (lower case) of all functions called anywhere inside an expression."""
        found = set() if found is None else found
        visited = set() if visited is None else visited
        if id(node) in visited:
            return found
        visited.add(id(node))
        if isinstance(node, FunctionCallNode):
            found.add(node.name.lower())
        if hasattr(node, '__dict__'):
            for attr_name, value in node.__dict__.items():
                if attr_name in ('line_num', 'column', 'original_case', 'explicit_type_suffix'):
                    continue
                for item in (value if isinstance(value, list) else [value]):
                    if hasattr(item, '__dict__'):
                        JavaScriptBackend._called_functions(item, found, visited)
        return found

    @staticmethod
    def _fn_key(name: str) -> str:
        name = name.lower()
        return name[2:] if name.startswith('fn') else name

    def _find_async_fns(self):
        """A DEF FN is async when its body calls INPUT$ or INKEY$, or calls an async DEF FN."""
        calls = {self._fn_key(d.name): self._called_functions(d.expression) for d in self.def_fn_functions}
        waits = ('input$', 'input', 'inkey$', 'inkey')
        changed = True
        while changed:
            changed = False
            for key, names in calls.items():
                if key not in self.async_fns and (
                        any(n in waits for n in names)
                        or any(n.startswith('fn') and self._fn_key(n) in self.async_fns for n in names)):
                    self.async_fns.add(key)
                    changed = True

    def _check_for_rnd(self, node, visited):
        """Recursively check for RND function usage (with cycle detection)"""
        # Avoid infinite recursion on circular references
        node_id = id(node)
        if node_id in visited:
            return
        visited.add(node_id)

        if isinstance(node, FunctionCallNode):
            fname = node.name.lower()
            if fname == 'rnd':
                self.uses_random = True
            elif fname in ('inkey$', 'inkey'):
                self.uses_inkey = True
            elif fname in ('input$', 'input'):
                self.uses_input_func = True
                # INPUT$(n, #f) reads an open file, so it needs the file helpers
                if len(node.arguments) > 1:
                    self.uses_file_io = True
            elif fname in ('eof', 'lof', 'loc'):
                self.uses_file_io = True

        # Recursively check children
        if hasattr(node, '__dict__'):
            for attr_name, attr_value in node.__dict__.items():
                # Skip certain attributes that create cycles (like parent pointers, line_num, column, etc.)
                if attr_name in ('line_num', 'column', 'original_case', 'explicit_type_suffix'):
                    continue

                if isinstance(attr_value, list):
                    for item in attr_value:
                        if hasattr(item, '__dict__'):
                            self._check_for_rnd(item, visited)
                elif hasattr(attr_value, '__dict__') and not isinstance(attr_value, (str, int, float, bool)):
                    self._check_for_rnd(attr_value, visited)

    def _generate_runtime(self) -> List[str]:
        """Generate runtime library functions"""
        code = []

        # Error handling
        code.append(self.indent() + 'const _ERR_CODES = ' + json.dumps({m: c for c, (_, m) in ERROR_CODES.items()}) + ';')
        code.append(self.indent() + 'function _error(msg) {')
        self.indent_level += 1
        code.append(self.indent() + 'const e = new Error(msg);')
        code.append(self.indent() + 'e.basicCode = _ERR_CODES[msg];  // ON ERROR traps the error by this number')
        code.append(self.indent() + 'throw e;')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent() + 'function _fatal(e) {')
        code.append(self.indent() + '    if (_col > 0) _print("");  // the message starts on a new line')
        code.append(self.indent() + '    // MBASIC stops a program with "<message> in <line>"')
        code.append(self.indent() + '    _print(e.basicLine === undefined ? e.message : e.message + " in " + e.basicLine);')
        code.append(self.indent() + '    if (typeof process !== "undefined") process.exit(1);')
        code.append(self.indent() + '}')
        code.append(self.indent() + 'function _unprint_char() {')
        code.append(self.indent() + '    // Backspace while typing INPUT text in the browser: drop the last echoed character')
        code.append(self.indent() + '    const output = typeof document !== "undefined" ? document.getElementById("output") : null;')
        code.append(self.indent() + '    if (output) output.textContent = output.textContent.slice(0, -1);')
        code.append(self.indent() + '}')
        code.append('')

        for line in (JS_NUMBER_RUNTIME + JS_ARITH_RUNTIME + JS_PRINT_RUNTIME + (JS_PRINT_FILES if self.uses_file_io else JS_PRINT_SCREEN)).strip('\n').split('\n'):
            code.append(self.indent() + line if line else '')
        code.append('')

        # Print function
        code.append(self.indent() + 'function _print(str, newline = true) {')
        self.indent_level += 1
        code.append(self.indent() + 'const s = String(str);')
        code.append(self.indent() + '_col = newline ? 0 : _advance(_col, s);')
        code.append(self.indent() + 'if (typeof window !== "undefined") {')
        self.indent_level += 1
        code.append(self.indent() + '// Browser')
        code.append(self.indent() + 'const output = document.getElementById("output");')
        code.append(self.indent() + 'if (output) {')
        self.indent_level += 1
        code.append(self.indent() + 'output.textContent += s;')
        code.append(self.indent() + 'if (newline) output.textContent += "\\n";')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        self.indent_level -= 1
        code.append(self.indent() + '} else if (typeof process !== "undefined") {')
        self.indent_level += 1
        code.append(self.indent() + '// Node.js')
        code.append(self.indent() + 'if (newline) {')
        self.indent_level += 1
        code.append(self.indent() + 'console.log(s);')
        self.indent_level -= 1
        code.append(self.indent() + '} else {')
        self.indent_level += 1
        code.append(self.indent() + 'process.stdout.write(s);')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append('')

        # PRINT USING
        for line in JS_USING_RUNTIME.strip('\n').split('\n'):
            code.append(self.indent() + line if line else '')
        code.append('')

        # Math functions
        code.append(self.indent() + '// Math functions')
        code.append(self.indent() + 'const _abs = Math.abs;')
        code.append(self.indent() + 'const _int = Math.floor;')
        code.append(self.indent() + 'const _sin = Math.sin;')
        code.append(self.indent() + 'const _cos = Math.cos;')
        code.append(self.indent() + 'const _tan = Math.tan;')
        code.append(self.indent() + 'const _atn = Math.atan;')
        code.append(self.indent() + 'const _exp = Math.exp;')
        code.append(self.indent() + 'function _sgn(n) { return n > 0 ? 1 : n < 0 ? -1 : 0; }')
        code.append(self.indent() + 'function _fix(n) { return n >= 0 ? Math.floor(n) : Math.ceil(n); }')
        code.append(self.indent() + 'function _csng(n) { return _toSingle(n); }  // Single precision via ES6; too big is Overflow')
        code.append(self.indent() + 'function _cdbl(n) { return n; }  // Double precision (already JS number)')
        code.append('')
        code.append(self.indent() + '// Type coercion for DEFINT/DEFSNG/DEFDBL variable assignment')
        code.append(self.indent() + 'function _toInt(n) {')
        self.indent_level += 1
        code.append(self.indent() + '// BASIC INTEGER: round to nearest (halves away from zero); outside -32768..32767 is Overflow')
        code.append(self.indent() + 'n = _round_half_away(n);')
        code.append(self.indent() + 'if (n > 32767 || n < -32768) _error("Overflow");')
        code.append(self.indent() + 'return n + 0;')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent() + 'function _cint(n) { return _toInt(n); }')
        for line in JS_LOGICAL_RUNTIME.strip('\n').split('\n'):
            code.append(self.indent() + line if line else '')
        code.append(self.indent() + 'function _toSingle(n) { return (n >= _SINGLE_LIMIT || n <= -_SINGLE_LIMIT) ? _overflow(n < 0, 6) : Math.fround(n); }  // ES6 single-precision')
        code.append(self.indent() + 'function _toDouble(n) { return n; }  // JS Number is already 64-bit double')
        code.append('')

        # RND function
        if self.uses_random:
            code.append(self.indent() + 'let _rnd_last = 0.5;')
            code.append(self.indent() + 'function _rnd(x) {')
            self.indent_level += 1
            code.append(self.indent() + 'if (x === undefined || x > 0) {')
            self.indent_level += 1
            code.append(self.indent() + '_rnd_last = Math.random();')
            self.indent_level -= 1
            code.append(self.indent() + '} else if (x < 0) {')
            self.indent_level += 1
            code.append(self.indent() + '// Seed (can\'t truly seed Math.random)')
            code.append(self.indent() + '_rnd_last = Math.abs(Math.sin(x) * 43758.5453);')
            code.append(self.indent() + '_rnd_last = _rnd_last - Math.floor(_rnd_last);')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append(self.indent() + 'return _rnd_last;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

        # String functions
        code.append(self.indent() + '// String functions')
        code.append(self.indent() + 'function _left(str, n) { return String(str).substring(0, n); }')
        code.append(self.indent() + 'function _right(str, n) { const s = String(str); return s.substring(s.length - n); }')
        code.append(self.indent() + 'function _mid(str, start, len) {')
        self.indent_level += 1
        code.append(self.indent() + 'const s = String(str);')
        code.append(self.indent() + 'if (len === undefined) return s.substring(start - 1);')
        code.append(self.indent() + 'return s.substring(start - 1, start - 1 + len);')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent() + 'function _len(str) { return String(str).length; }')
        code.append(self.indent() + 'function _chr(n) { return String.fromCharCode(n); }')
        code.append(self.indent() + 'function _asc(str) { return String(str).charCodeAt(0) || 0; }')
        code.append(self.indent() + 'function _str(n, d = 6) { const t = _fmt_num(n, d); return n >= 0 ? " " + t : t; }')
        code.append(self.indent() + 'function _instr(start, str1, str2) {')
        self.indent_level += 1
        code.append(self.indent() + '// INSTR with optional start position')
        code.append(self.indent() + 'if (str2 === undefined) {')
        self.indent_level += 1
        code.append(self.indent() + '// Two argument form: INSTR(str1, str2)')
        code.append(self.indent() + 'str2 = str1;')
        code.append(self.indent() + 'str1 = start;')
        code.append(self.indent() + 'start = 1;')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent() + 'const pos = String(str1).indexOf(String(str2), start - 1);')
        code.append(self.indent() + 'return pos === -1 ? 0 : pos + 1;')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent() + 'function _space(n) { return " ".repeat(n); }')
        code.append(self.indent() + 'function _string(n, ch) {')
        self.indent_level += 1
        code.append(self.indent() + '// STRING$(n, code) or STRING$(n, string)')
        code.append(self.indent() + 'const char = typeof ch === "number" ? String.fromCharCode(ch) : String(ch).charAt(0);')
        code.append(self.indent() + 'return char.repeat(n);')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent() + 'function _radix_word(n) {')
        self.indent_level += 1
        code.append(self.indent() + '// HEX$ and OCT$ show the 16-bit pattern: 65536 and more is Overflow, 32768..65535 move down by 65536,')
        code.append(self.indent() + '// then the value rounds like any integer and must fit -32768..32767')
        code.append(self.indent() + 'if (typeof n === "string") _error("Type mismatch");')
        code.append(self.indent() + 'if (n !== n || n >= 65536) _error("Overflow");')
        code.append(self.indent() + 'if (n >= 32768) n -= 65536;')
        code.append(self.indent() + 'n = _round_half_away(n);')
        code.append(self.indent() + 'if (!(n >= -32768 && n <= 32767)) _error("Overflow");')
        code.append(self.indent() + 'return n & 0xFFFF;')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent() + 'function _hex(n) { return _radix_word(n).toString(16).toUpperCase(); }')
        code.append(self.indent() + 'function _oct(n) { return _radix_word(n).toString(8); }')
        code.append(self.indent() + 'let _print_pos = 0;  // Track print position for POS()')
        code.append(self.indent() + 'function _pos() {')
        self.indent_level += 1
        code.append(self.indent() + '// POS(0) - current print position (1-based)')
        code.append(self.indent() + '// Note: Simplified - would need to track actual cursor position')
        code.append(self.indent() + 'return ((_width >= 255 ? Math.min(_col, 255) : _col) + 1) % 256;')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append('')

        # Print formatting functions
        code.append(self.indent() + '// Print formatting')
        code.append(self.indent() + 'function _tab(n) {')
        self.indent_level += 1
        code.append(self.indent() + '// TAB(n) - move to column n (1-based)')
        code.append(self.indent() + '// Note: Simplified - just returns spaces')
        code.append(self.indent() + 'return " ".repeat(Math.max(0, n - 1));')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent() + 'function _spc(n) {')
        self.indent_level += 1
        code.append(self.indent() + '// SPC(n) - print n spaces')
        code.append(self.indent() + 'return " ".repeat(Math.max(0, n));')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append('')

        # INPUT / LINE INPUT functions
        if self.uses_input or self.uses_line_input:
            for line in JS_INPUT_RUNTIME.strip('\n').split('\n'):
                code.append(self.indent() + line if line else '')
            code.append('')

        # WRITE function
        if True:  # small, and WRITE can hide in an IF clause the scan does not enter
            code.append(self.indent() + '// WRITE function - format values for CSV output')
            code.append(self.indent() + 'function _write_format(value, digits = 6) {')
            self.indent_level += 1
            code.append(self.indent() + '// Strings are quoted, numbers are unquoted and unpadded')
            code.append(self.indent() + 'if (typeof value === "string") return \'"\' + value + \'"\';')
            code.append(self.indent() + 'return _fmt_num(value, digits);')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

        # LPRINT function
        if self.uses_lprint:
            code.append(self.indent() + '// LPRINT function - print to line printer (console.log)')
            code.append(self.indent() + 'function _lprint(str, newline = true) {')
            self.indent_level += 1
            code.append(self.indent() + 'const s = String(str);')
            code.append(self.indent() + 'if (newline) {')
            self.indent_level += 1
            code.append(self.indent() + 'console.log(s);')
            self.indent_level -= 1
            code.append(self.indent() + '} else {')
            self.indent_level += 1
            code.append(self.indent() + '// Node.js and modern browsers support this')
            code.append(self.indent() + 'if (typeof process !== "undefined" && process.stdout) {')
            self.indent_level += 1
            code.append(self.indent() + 'process.stdout.write(s);')
            self.indent_level -= 1
            code.append(self.indent() + '} else {')
            self.indent_level += 1
            code.append(self.indent() + '// Browser fallback - no good way to avoid newline')
            code.append(self.indent() + 'console.log(s);')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

        # File I/O support
        if self.uses_file_io:
            code.append(self.indent() + '// File I/O support')
            code.append(self.indent() + 'const _files = {};  // Map file number -> file object')
            code.append('')

            # File operations wrapper
            code.append(self.indent() + '// File operations')
            code.append(self.indent() + 'const _fileOps = {')
            self.indent_level += 1

            # Node.js file operations
            code.append(self.indent() + 'nodejs: {')
            self.indent_level += 1
            code.append(self.indent() + 'open: (filenum, filename, mode, reclen) => {')
            self.indent_level += 1
            code.append(self.indent() + 'const fs = require("fs");')
            code.append(self.indent() + 'if (mode === "I") {')
            self.indent_level += 1
            code.append(self.indent() + '// Input mode - read entire file')
            code.append(self.indent() + 'const content = fs.readFileSync(filename, "utf8");')
            code.append(self.indent() + '_files[filenum] = { mode: "I", content, pos: 0, filename };')
            self.indent_level -= 1
            code.append(self.indent() + '} else if (mode === "O") {')
            self.indent_level += 1
            code.append(self.indent() + '// Output mode - write to file')
            code.append(self.indent() + '_files[filenum] = { mode: "O", content: "", filename };')
            self.indent_level -= 1
            code.append(self.indent() + '} else if (mode === "A") {')
            self.indent_level += 1
            code.append(self.indent() + '// Append mode')
            code.append(self.indent() + 'let content = "";')
            code.append(self.indent() + 'try { content = fs.readFileSync(filename, "utf8"); } catch(e) {}')
            code.append(self.indent() + '_files[filenum] = { mode: "A", content, filename };')
            self.indent_level -= 1
            code.append(self.indent() + '} else if (mode === "R") {')
            self.indent_level += 1
            code.append(self.indent() + '// Random access mode')
            code.append(self.indent() + 'if (reclen !== undefined && (reclen < 0 || reclen > 128)) _error("Illegal function call");')
            code.append(self.indent() + 'const recordLength = reclen === undefined ? 128 : reclen;')
            code.append(self.indent() + 'let content = "";')
            code.append(self.indent() + 'try { content = fs.readFileSync(filename, "binary"); } catch(e) {}')
            code.append(self.indent() + '_files[filenum] = {')
            self.indent_level += 1
            code.append(self.indent() + 'mode: "R",')
            code.append(self.indent() + 'content,')
            code.append(self.indent() + 'filename,')
            code.append(self.indent() + 'recordLength,')
            code.append(self.indent() + 'currentRecord: 1,')
            code.append(self.indent() + 'buffer: " ".repeat(recordLength),')
            code.append(self.indent() + 'fields: {}  // Map field variable name -> {start, width}')
            self.indent_level -= 1
            code.append(self.indent() + '};')
            self.indent_level -= 1
            code.append(self.indent() + '} else {')
            self.indent_level += 1
            code.append(self.indent() + '_error("Unsupported file mode: " + mode);')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '},')

            code.append(self.indent() + 'close: (filenum) => {')
            self.indent_level += 1
            code.append(self.indent() + 'const file = _files[filenum];')
            code.append(self.indent() + 'if (file && (file.mode === "O" || file.mode === "A")) {')
            self.indent_level += 1
            code.append(self.indent() + 'const fs = require("fs");')
            code.append(self.indent() + 'fs.writeFileSync(file.filename, file.content, "utf8");')
            self.indent_level -= 1
            code.append(self.indent() + '} else if (file && file.mode === "R") {')
            self.indent_level += 1
            code.append(self.indent() + '// Save random file')
            code.append(self.indent() + 'const fs = require("fs");')
            code.append(self.indent() + 'fs.writeFileSync(file.filename, file.content, "binary");')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append(self.indent() + 'delete _files[filenum];')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '},')

            # Browser file operations (using localStorage)
            code.append(self.indent() + 'browser: {')
            self.indent_level += 1
            code.append(self.indent() + 'open: (filenum, filename, mode, reclen) => {')
            self.indent_level += 1
            code.append(self.indent() + 'const key = "mbasic_file_" + filename;')
            code.append(self.indent() + 'if (mode === "I") {')
            self.indent_level += 1
            code.append(self.indent() + 'const content = localStorage.getItem(key) || "";')
            code.append(self.indent() + '_files[filenum] = { mode: "I", content, pos: 0, filename };')
            self.indent_level -= 1
            code.append(self.indent() + '} else if (mode === "O") {')
            self.indent_level += 1
            code.append(self.indent() + '_files[filenum] = { mode: "O", content: "", filename };')
            self.indent_level -= 1
            code.append(self.indent() + '} else if (mode === "A") {')
            self.indent_level += 1
            code.append(self.indent() + 'const content = localStorage.getItem(key) || "";')
            code.append(self.indent() + '_files[filenum] = { mode: "A", content, filename };')
            self.indent_level -= 1
            code.append(self.indent() + '} else if (mode === "R") {')
            self.indent_level += 1
            code.append(self.indent() + '// Random access mode')
            code.append(self.indent() + 'if (reclen !== undefined && (reclen < 0 || reclen > 128)) _error("Illegal function call");')
            code.append(self.indent() + 'const recordLength = reclen === undefined ? 128 : reclen;')
            code.append(self.indent() + 'const content = localStorage.getItem(key) || "";')
            code.append(self.indent() + '_files[filenum] = {')
            self.indent_level += 1
            code.append(self.indent() + 'mode: "R",')
            code.append(self.indent() + 'content,')
            code.append(self.indent() + 'filename,')
            code.append(self.indent() + 'recordLength,')
            code.append(self.indent() + 'currentRecord: 1,')
            code.append(self.indent() + 'buffer: " ".repeat(recordLength),')
            code.append(self.indent() + 'fields: {}  // Map field variable name -> {start, width}')
            self.indent_level -= 1
            code.append(self.indent() + '};')
            self.indent_level -= 1
            code.append(self.indent() + '} else {')
            self.indent_level += 1
            code.append(self.indent() + '_error("Unsupported file mode: " + mode);')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '},')

            code.append(self.indent() + 'close: (filenum) => {')
            self.indent_level += 1
            code.append(self.indent() + 'const file = _files[filenum];')
            code.append(self.indent() + 'if (file && (file.mode === "O" || file.mode === "A" || file.mode === "R")) {')
            self.indent_level += 1
            code.append(self.indent() + 'const key = "mbasic_file_" + file.filename;')
            code.append(self.indent() + 'localStorage.setItem(key, file.content);')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append(self.indent() + 'delete _files[filenum];')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '};')
            code.append('')

            # Helper functions
            code.append(self.indent() + 'function _fopen(filenum, filename, mode, reclen) {')
            self.indent_level += 1
            code.append(self.indent() + 'if (typeof process !== "undefined") {')
            self.indent_level += 1
            code.append(self.indent() + '_fileOps.nodejs.open(filenum, filename, mode, reclen);')
            self.indent_level -= 1
            code.append(self.indent() + '} else {')
            self.indent_level += 1
            code.append(self.indent() + '_fileOps.browser.open(filenum, filename, mode, reclen);')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

            code.append(self.indent() + 'function _fclose(filenum) {')
            self.indent_level += 1
            code.append(self.indent() + 'if (filenum === undefined) {')
            self.indent_level += 1
            code.append(self.indent() + '// CLOSE with no arguments - close all files')
            code.append(self.indent() + 'for (const fn in _files) {')
            self.indent_level += 1
            code.append(self.indent() + '_fclose(parseInt(fn));')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '} else {')
            self.indent_level += 1
            code.append(self.indent() + 'if (typeof process !== "undefined") {')
            self.indent_level += 1
            code.append(self.indent() + '_fileOps.nodejs.close(filenum);')
            self.indent_level -= 1
            code.append(self.indent() + '} else {')
            self.indent_level += 1
            code.append(self.indent() + '_fileOps.browser.close(filenum);')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

            code.append(self.indent() + 'function _fprint(filenum, str, newline = true) {')
            self.indent_level += 1
            code.append(self.indent() + 'const file = _files[filenum];')
            code.append(self.indent() + 'if (!file) _error("File #" + filenum + " not open");')
            code.append(self.indent() + 'if (file.mode !== "O" && file.mode !== "A") _error("File #" + filenum + " not open for output");')
            code.append(self.indent() + 'file.content += String(str);')
            code.append(self.indent() + 'if (newline) file.content += "\\n";')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

            code.append(self.indent() + 'function _finput(filenum) {')
            self.indent_level += 1
            code.append(self.indent() + 'const file = _files[filenum];')
            code.append(self.indent() + 'if (!file) _error("File #" + filenum + " not open");')
            code.append(self.indent() + 'if (file.mode !== "I") _error("File #" + filenum + " not open for input");')
            for line in JS_FINPUT_BODY.strip('\n').split('\n'):
                code.append(self.indent() + line)
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

            code.append(self.indent() + 'function _fline_input(filenum) {')
            self.indent_level += 1
            code.append(self.indent() + 'const file = _files[filenum];')
            code.append(self.indent() + 'if (!file) _error("File #" + filenum + " not open");')
            code.append(self.indent() + 'if (file.mode !== "I") _error("File #" + filenum + " not open for input");')
            code.append(self.indent() + '// Read one line (CR LF ends it too)')
            code.append(self.indent() + 'if (file.pos >= file.content.length) _error("Input past end");')
            code.append(self.indent() + 'let line = "";')
            code.append(self.indent() + 'while (file.pos < file.content.length) {')
            self.indent_level += 1
            code.append(self.indent() + 'const ch = file.content[file.pos++];')
            code.append(self.indent() + 'if (ch === "\\n") break;')
            code.append(self.indent() + 'line += ch;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append(self.indent() + 'return line.endsWith("\\r") ? line.slice(0, -1) : line;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

            # File position functions
            code.append(self.indent() + 'function _eof(filenum) {')
            self.indent_level += 1
            code.append(self.indent() + '// EOF() - Test for end of file')
            code.append(self.indent() + 'const file = _files[filenum];')
            code.append(self.indent() + 'if (!file) _error("File #" + filenum + " not open");')
            code.append(self.indent() + 'if (file.mode !== "I") _error("File #" + filenum + " not open for input");')
            code.append(self.indent() + 'return file.pos >= file.content.length ? -1 : 0;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

            code.append(self.indent() + 'function _lof(filenum) {')
            self.indent_level += 1
            code.append(self.indent() + '// LOF() - Length of file in bytes')
            code.append(self.indent() + 'const file = _files[filenum];')
            code.append(self.indent() + 'if (!file) _error("File #" + filenum + " not open");')
            code.append(self.indent() + 'return file.content.length;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

            code.append(self.indent() + 'function _loc(filenum) {')
            self.indent_level += 1
            code.append(self.indent() + '// LOC() - Current position in file')
            code.append(self.indent() + 'const file = _files[filenum];')
            code.append(self.indent() + 'if (!file) _error("File #" + filenum + " not open");')
            code.append(self.indent() + 'return file.pos || 0;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

            # File management functions
            code.append(self.indent() + 'function _fkill(filename) {')
            self.indent_level += 1
            code.append(self.indent() + '// KILL - Delete file')
            code.append(self.indent() + 'if (typeof process !== "undefined") {')
            self.indent_level += 1
            code.append(self.indent() + 'const fs = require("fs");')
            code.append(self.indent() + 'try {')
            self.indent_level += 1
            code.append(self.indent() + 'fs.unlinkSync(filename);')
            self.indent_level -= 1
            code.append(self.indent() + '} catch (e) {')
            self.indent_level += 1
            code.append(self.indent() + '_error("Cannot delete file: " + filename);')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '} else {')
            self.indent_level += 1
            code.append(self.indent() + '// Browser - remove from localStorage')
            code.append(self.indent() + 'const key = "mbasic_file_" + filename;')
            code.append(self.indent() + 'if (localStorage.getItem(key) !== null) {')
            self.indent_level += 1
            code.append(self.indent() + 'localStorage.removeItem(key);')
            self.indent_level -= 1
            code.append(self.indent() + '} else {')
            self.indent_level += 1
            code.append(self.indent() + '_error("File not found: " + filename);')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

            code.append(self.indent() + 'function _fname(oldname, newname) {')
            self.indent_level += 1
            code.append(self.indent() + '// NAME - Rename file')
            code.append(self.indent() + 'if (typeof process !== "undefined") {')
            self.indent_level += 1
            code.append(self.indent() + 'const fs = require("fs");')
            code.append(self.indent() + 'try {')
            self.indent_level += 1
            code.append(self.indent() + 'fs.renameSync(oldname, newname);')
            self.indent_level -= 1
            code.append(self.indent() + '} catch (e) {')
            self.indent_level += 1
            code.append(self.indent() + '_error("Cannot rename file: " + oldname);')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '} else {')
            self.indent_level += 1
            code.append(self.indent() + '// Browser - rename in localStorage')
            code.append(self.indent() + 'const oldkey = "mbasic_file_" + oldname;')
            code.append(self.indent() + 'const newkey = "mbasic_file_" + newname;')
            code.append(self.indent() + 'const content = localStorage.getItem(oldkey);')
            code.append(self.indent() + 'if (content !== null) {')
            self.indent_level += 1
            code.append(self.indent() + 'localStorage.setItem(newkey, content);')
            code.append(self.indent() + 'localStorage.removeItem(oldkey);')
            self.indent_level -= 1
            code.append(self.indent() + '} else {')
            self.indent_level += 1
            code.append(self.indent() + '_error("File not found: " + oldname);')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

            code.append(self.indent() + 'function _ffiles(filespec) {')
            self.indent_level += 1
            code.append(self.indent() + '// FILES - List directory')
            code.append(self.indent() + 'if (typeof process !== "undefined") {')
            self.indent_level += 1
            code.append(self.indent() + 'const fs = require("fs");')
            code.append(self.indent() + 'try {')
            self.indent_level += 1
            code.append(self.indent() + 'const files = fs.readdirSync(".");')
            code.append(self.indent() + '// Simple pattern matching (* and ?)')
            code.append(self.indent() + 'const pattern = filespec.replace(/\\*/g, ".*").replace(/\\?/g, ".");')
            code.append(self.indent() + 'const regex = new RegExp("^" + pattern + "$", "i");')
            code.append(self.indent() + 'const matches = files.filter(f => regex.test(f));')
            code.append(self.indent() + 'if (matches.length > 0) {')
            self.indent_level += 1
            code.append(self.indent() + 'console.log(matches.join("  "));')
            self.indent_level -= 1
            code.append(self.indent() + '} else {')
            self.indent_level += 1
            code.append(self.indent() + 'console.log("File not found");')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '} catch (e) {')
            self.indent_level += 1
            code.append(self.indent() + '_error("Cannot list directory");')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '} else {')
            self.indent_level += 1
            code.append(self.indent() + '// Browser - list files in localStorage')
            code.append(self.indent() + 'const prefix = "mbasic_file_";')
            code.append(self.indent() + 'const files = [];')
            code.append(self.indent() + 'for (let i = 0; i < localStorage.length; i++) {')
            self.indent_level += 1
            code.append(self.indent() + 'const key = localStorage.key(i);')
            code.append(self.indent() + 'if (key.startsWith(prefix)) {')
            self.indent_level += 1
            code.append(self.indent() + 'files.push(key.substring(prefix.length));')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append(self.indent() + 'if (files.length > 0) {')
            self.indent_level += 1
            code.append(self.indent() + 'console.log(files.join("  "));')
            self.indent_level -= 1
            code.append(self.indent() + '} else {')
            self.indent_level += 1
            code.append(self.indent() + 'console.log("File not found");')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

        # Random file access functions
        if self.uses_file_io:
            code.append(self.indent() + '// Random file access functions')
            code.append(self.indent() + 'function _ffield(filenum, fields) {')
            self.indent_level += 1
            code.append(self.indent() + '// FIELD - Define buffer layout for random file')
            code.append(self.indent() + 'const file = _files[filenum];')
            code.append(self.indent() + 'if (!file) _error("File #" + filenum + " not open");')
            code.append(self.indent() + 'if (file.mode !== "R") _error("File #" + filenum + " not open for random access");')
            code.append(self.indent() + '// The widths must fit in the record length of OPEN; nothing changes when they do not')
            code.append(self.indent() + 'let total = 0;')
            code.append(self.indent() + 'for (const [width] of fields) {')
            code.append(self.indent() + '    if (width < 0) _error("Illegal function call");')
            code.append(self.indent() + '    total += width;')
            code.append(self.indent() + '    if (total > file.recordLength) _error("FIELD overflow");')
            code.append(self.indent() + '}')
            code.append(self.indent() + 'let pos = 0;')
            code.append(self.indent() + 'for (const [width, varname] of fields) {')
            self.indent_level += 1
            code.append(self.indent() + 'file.fields[varname] = { start: pos, width: width };')
            code.append(self.indent() + 'pos += width;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

            code.append(self.indent() + 'function _flset(varname, value) {')
            self.indent_level += 1
            code.append(self.indent() + '// LSET - Left-justify string in field variable')
            code.append(self.indent() + '// Find which file has this field variable')
            code.append(self.indent() + 'for (const filenum in _files) {')
            self.indent_level += 1
            code.append(self.indent() + 'const file = _files[filenum];')
            code.append(self.indent() + 'if (file.mode === "R" && file.fields[varname]) {')
            self.indent_level += 1
            code.append(self.indent() + 'const field = file.fields[varname];')
            code.append(self.indent() + 'const str = String(value).substring(0, field.width).padEnd(field.width, " ");')
            code.append(self.indent() + 'file.buffer = file.buffer.substring(0, field.start) + str + file.buffer.substring(field.start + field.width);')
            code.append(self.indent() + 'return;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append(self.indent() + '_error("Field variable not found: " + varname);')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

            code.append(self.indent() + 'function _frset(varname, value) {')
            self.indent_level += 1
            code.append(self.indent() + '// RSET - Right-justify string in field variable')
            code.append(self.indent() + 'for (const filenum in _files) {')
            self.indent_level += 1
            code.append(self.indent() + 'const file = _files[filenum];')
            code.append(self.indent() + 'if (file.mode === "R" && file.fields[varname]) {')
            self.indent_level += 1
            code.append(self.indent() + 'const field = file.fields[varname];')
            code.append(self.indent() + 'const str = String(value).substring(0, field.width).padStart(field.width, " ");')
            code.append(self.indent() + 'file.buffer = file.buffer.substring(0, field.start) + str + file.buffer.substring(field.start + field.width);')
            code.append(self.indent() + 'return;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append(self.indent() + '_error("Field variable not found: " + varname);')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

            code.append(self.indent() + 'function _fget(filenum, recnum) {')
            self.indent_level += 1
            code.append(self.indent() + '// GET - Read record from random file into buffer')
            code.append(self.indent() + 'const file = _files[filenum];')
            code.append(self.indent() + 'if (!file) _error("File #" + filenum + " not open");')
            code.append(self.indent() + 'if (file.mode !== "R") _error("File #" + filenum + " not open for random access");')
            code.append(self.indent() + 'const recordNum = recnum !== undefined ? recnum : file.currentRecord;')
            code.append(self.indent() + 'const pos = (recordNum - 1) * file.recordLength;')
            code.append(self.indent() + 'if (pos < 0) _error("Invalid record number");')
            code.append(self.indent() + '// Read record from file content')
            code.append(self.indent() + 'if (pos >= file.content.length) {')
            self.indent_level += 1
            code.append(self.indent() + '// Beyond end of file - fill buffer with spaces')
            code.append(self.indent() + 'file.buffer = " ".repeat(file.recordLength);')
            self.indent_level -= 1
            code.append(self.indent() + '} else {')
            self.indent_level += 1
            code.append(self.indent() + 'file.buffer = file.content.substring(pos, pos + file.recordLength).padEnd(file.recordLength, " ");')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append(self.indent() + '// Update field variables from buffer')
            code.append(self.indent() + 'for (const varname in file.fields) {')
            self.indent_level += 1
            code.append(self.indent() + 'const field = file.fields[varname];')
            code.append(self.indent() + 'const value = file.buffer.substring(field.start, field.start + field.width);')
            code.append(self.indent() + 'if (typeof window !== "undefined") window[varname] = value;')
            code.append(self.indent() + 'else global[varname] = value;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append(self.indent() + 'file.currentRecord = recordNum + 1;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

            code.append(self.indent() + 'function _fput(filenum, recnum) {')
            self.indent_level += 1
            code.append(self.indent() + '// PUT - Write buffer to record in random file')
            code.append(self.indent() + 'const file = _files[filenum];')
            code.append(self.indent() + 'if (!file) _error("File #" + filenum + " not open");')
            code.append(self.indent() + 'if (file.mode !== "R") _error("File #" + filenum + " not open for random access");')
            code.append(self.indent() + 'const recordNum = recnum !== undefined ? recnum : file.currentRecord;')
            code.append(self.indent() + 'const pos = (recordNum - 1) * file.recordLength;')
            code.append(self.indent() + 'if (pos < 0) _error("Invalid record number");')
            code.append(self.indent() + '// Extend file content if necessary')
            code.append(self.indent() + 'if (pos + file.recordLength > file.content.length) {')
            self.indent_level += 1
            code.append(self.indent() + 'file.content = file.content.padEnd(pos + file.recordLength, " ");')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append(self.indent() + '// Write buffer to file content')
            code.append(self.indent() + 'file.content = file.content.substring(0, pos) + file.buffer + file.content.substring(pos + file.recordLength);')
            code.append(self.indent() + 'file.currentRecord = recordNum + 1;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

        # GOSUB/RETURN
        if self.uses_gosub:
            code.append(self.indent() + '// GOSUB/RETURN stack')
            code.append(self.indent() + 'const _gosub_stack = [];')
            code.append(self.indent() + 'function _gosub(return_line) {')
            self.indent_level += 1
            code.append(self.indent() + '_gosub_stack.push(return_line);')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append(self.indent() + 'function _return() {')
            self.indent_level += 1
            code.append(self.indent() + 'if (_gosub_stack.length === 0) _error("RETURN without GOSUB");')
            code.append(self.indent() + 'return _gosub_stack.pop();')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

        # FOR/NEXT loop state (variable-indexed approach)
        code.append(self.indent() + '// FOR/NEXT loop state')
        code.append(self.indent() + 'const _for_loops = {};  // Map var name -> {end, step, line}')
        code.append(self.indent() + '// MBASIC ends a loop when sign(var - end) equals sign(step): with STEP 0 only when var equals end')
        code.append(self.indent() + 'function _for_done(v, end, step) { return Math.sign(v - end) === Math.sign(step); }')
        # Case labels inside a line (see _plan_lines) and the line they belong to, for the line of an error
        labels = {label: plan.line_number for plan in self.line_plans.values() for label in plan.labels.values()}
        code.append(self.indent() + 'const _LABEL_LINE = ' + json.dumps({str(k): v for k, v in labels.items()}) + ';')
        code.append(self.indent() + f'function _line_of(pc) {{ return pc >= {CONT_LABEL_BASE} ? _LABEL_LINE[pc] : pc; }}')
        code.append('')

        # Error handling
        if self.uses_error_handling:
            code.append(self.indent() + '// Error handling')
            code.append(self.indent() + 'let _error_handler = null;  // Line number of error handler (0 = disabled)')
            code.append(self.indent() + 'let _error_handler_is_gosub = false;  // True if ON ERROR GOSUB')
            code.append(self.indent() + 'let _error_line = 0;  // Line where error occurred (ERL)')
            code.append(self.indent() + 'let _error_code = 0;  // Error code (ERR)')
            code.append(self.indent() + 'let _in_error_handler = false;  // Prevent recursive errors')
            code.append(self.indent() + 'const _ERR_MSGS = ' + json.dumps({str(c): m for c, (_, m) in ERROR_CODES.items()}) + ';')
            code.append(self.indent() + 'const _next_lines = ' + json.dumps({str(k): v for k, v in self.next_line_map.items()}) + ';  // for RESUME NEXT')
            code.append(self.indent() + 'function _trigger_error(code, line) {')
            self.indent_level += 1
            code.append(self.indent() + 'if (_in_error_handler) {')
            self.indent_level += 1
            code.append(self.indent() + '_error(_ERR_MSGS[code] || "Illegal function call");  // an error in a handler is not trapped')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append(self.indent() + '_error_code = code;')
            code.append(self.indent() + '_error_line = line;')
            code.append(self.indent() + 'if (_error_handler === null) {')
            self.indent_level += 1
            code.append(self.indent() + '_error(_ERR_MSGS[code] || "Unprintable error");')
            self.indent_level -= 1
            code.append(self.indent() + '} else if (_error_handler === 0) {')
            self.indent_level += 1
            code.append(self.indent() + '_error(_ERR_MSGS[code] || "Unprintable error");')
            self.indent_level -= 1
            code.append(self.indent() + '} else {')
            self.indent_level += 1
            code.append(self.indent() + '_in_error_handler = true;')
            code.append(self.indent() + 'if (_error_handler_is_gosub) {')
            self.indent_level += 1
            code.append(self.indent() + '_gosub(line);  // Return to line that caused error')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append(self.indent() + 'return _error_handler;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append(self.indent() + 'function _erl() { return _error_line; }')
            code.append(self.indent() + 'function _err() { return _error_code; }')
            code.append('')

        # DATA/READ/RESTORE
        if self.uses_data or self.data_values:
            code.append(self.indent() + '// DATA/READ/RESTORE')
            code.append(self.indent() + f'const _data = {self._format_data_array()};')
            code.append(self.indent() + 'let _data_ptr = 0;')
            code.append(self.indent() + 'function _read() {')
            self.indent_level += 1
            code.append(self.indent() + 'if (_data_ptr >= _data.length) _error("Out of DATA");')
            code.append(self.indent() + 'return _data[_data_ptr++];')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append(self.indent() + 'function _restore() {')
            self.indent_level += 1
            code.append(self.indent() + '_data_ptr = 0;')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append('')

        # Binary data conversion functions (MKI$/MKS$/MKD$, CVI/CVS/CVD)
        code.append(self.indent() + '// Binary data conversion functions')
        code.append(self.indent() + 'function _mki(n) {')
        self.indent_level += 1
        code.append(self.indent() + '// MKI$ - Convert integer to 2-byte string')
        code.append(self.indent() + 'n = _toInt(n);')
        code.append(self.indent() + 'if (n < 0) n = 65536 + n;  // Two\'s complement')
        code.append(self.indent() + 'return String.fromCharCode(n & 0xFF, (n >> 8) & 0xFF);')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent() + 'function _mks(n) {')
        self.indent_level += 1
        code.append(self.indent() + '// MKS$ - Convert single to 4-byte string')
        code.append(self.indent() + 'const buf = new ArrayBuffer(4);')
        code.append(self.indent() + 'new DataView(buf).setFloat32(0, n, true);  // little-endian')
        code.append(self.indent() + 'const arr = new Uint8Array(buf);')
        code.append(self.indent() + 'return String.fromCharCode(...arr);')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent() + 'function _mkd(n) {')
        self.indent_level += 1
        code.append(self.indent() + '// MKD$ - Convert double to 8-byte string')
        code.append(self.indent() + 'const buf = new ArrayBuffer(8);')
        code.append(self.indent() + 'new DataView(buf).setFloat64(0, n, true);  // little-endian')
        code.append(self.indent() + 'const arr = new Uint8Array(buf);')
        code.append(self.indent() + 'return String.fromCharCode(...arr);')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent() + 'function _cvi(s) {')
        self.indent_level += 1
        code.append(self.indent() + '// CVI - Convert 2-byte string to integer')
        code.append(self.indent() + 'let n = s.charCodeAt(0) | (s.charCodeAt(1) << 8);')
        code.append(self.indent() + 'if (n >= 32768) n = n - 65536;  // Two\'s complement')
        code.append(self.indent() + 'return n;')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent() + 'function _cvs(s) {')
        self.indent_level += 1
        code.append(self.indent() + '// CVS - Convert 4-byte string to single')
        code.append(self.indent() + 'const buf = new ArrayBuffer(4);')
        code.append(self.indent() + 'const arr = new Uint8Array(buf);')
        code.append(self.indent() + 'for (let i = 0; i < 4; i++) arr[i] = s.charCodeAt(i) || 0;')
        code.append(self.indent() + 'return new DataView(buf).getFloat32(0, true);')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent() + 'function _cvd(s) {')
        self.indent_level += 1
        code.append(self.indent() + '// CVD - Convert 8-byte string to double')
        code.append(self.indent() + 'const buf = new ArrayBuffer(8);')
        code.append(self.indent() + 'const arr = new Uint8Array(buf);')
        code.append(self.indent() + 'for (let i = 0; i < 8; i++) arr[i] = s.charCodeAt(i) || 0;')
        code.append(self.indent() + 'return new DataView(buf).getFloat64(0, true);')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append('')

        # Memory and system functions (stubs - no direct hardware in JS)
        code.append(self.indent() + '// Memory/system functions (stubs - no hardware access in JavaScript)')
        code.append(self.indent() + 'function _fre(n) {')
        self.indent_level += 1
        code.append(self.indent() + '// FRE - Returns free memory (stub: always returns 32767)')
        code.append(self.indent() + 'return 32767;')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent() + 'function _peek(addr) {')
        self.indent_level += 1
        code.append(self.indent() + '// PEEK - Read memory location (returns random byte like interpreter)')
        code.append(self.indent() + 'return (Math.random() * 256) | 0;')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent() + 'function _inp(port) {')
        self.indent_level += 1
        code.append(self.indent() + '// INP - Read I/O port (stub: returns 0)')
        code.append(self.indent() + 'console.warn("INP not supported in JavaScript - returning 0");')
        code.append(self.indent() + 'return 0;')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent() + 'function _varptr(v) {')
        self.indent_level += 1
        code.append(self.indent() + '// VARPTR - Get variable address (stub: returns 0)')
        code.append(self.indent() + 'console.warn("VARPTR not supported in JavaScript - returning 0");')
        code.append(self.indent() + 'return 0;')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append(self.indent() + 'function _usr(n) {')
        self.indent_level += 1
        code.append(self.indent() + '// USR - Call machine code routine (stub: returns argument)')
        code.append(self.indent() + 'console.warn("USR not supported in JavaScript - returning argument");')
        code.append(self.indent() + 'return n;')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append('')

        # INKEY$ function
        for line in JS_INKEY_RUNTIME.strip('\n').split('\n'):
            code.append(self.indent() + line if line else '')
        code.append(self.indent() + '// Setup keyboard handler for browser')
        code.append(self.indent() + 'if (typeof window !== "undefined") {')
        self.indent_level += 1
        code.append(self.indent() + '// keydown, not keypress: Backspace and Enter do not fire keypress in every browser.')
        code.append(self.indent() + '// Printable keys give their character, Enter gives CR, Backspace gives BS, Ctrl+C gives ETX.')
        code.append(self.indent() + 'document.addEventListener("keydown", (e) => {')
        for key_line in JS_KEYDOWN_BODY.split('\n'):
            code.append(self.indent() + key_line)
        code.append(self.indent() + '});')
        self.indent_level -= 1
        code.append(self.indent() + '}')
        code.append('')

        # INPUT$ function
        if self.uses_input_func:
            code.append(self.indent() + '// INPUT$(n) / INPUT$(n, #f) - read n characters, no echo, no Enter')
            code.append(self.indent() + '// Keyboard: characters already in _inkey_buffer come first, then the host is asked.')
            code.append(self.indent() + '// main() is async. Node reads stdin with fs.readSync (it blocks); a browser waits for keydown events.')
            code.append(self.indent() + 'async function _input_chars(n, filenum) {')
            code.append(self.indent() + '    n = Math.trunc(n);')
            code.append(self.indent() + '    if (n < 1 || n > 255) _error("Illegal function call");')
            code.append(self.indent() + '    if (filenum !== undefined) {')
            code.append(self.indent() + '        const file = _files[filenum];')
            code.append(self.indent() + '        if (!file) _error("File #" + filenum + " not open");')
            code.append(self.indent() + '        if (file.mode !== "I") _error("Bad file mode");')
            code.append(self.indent() + '        if (file.pos + n > file.content.length) {')
            code.append(self.indent() + '            file.pos = file.content.length;')
            code.append(self.indent() + '            _error("Input past end");')
            code.append(self.indent() + '        }')
            code.append(self.indent() + '        const text = file.content.substr(file.pos, n);')
            code.append(self.indent() + '        file.pos += n;')
            code.append(self.indent() + '        return text;')
            code.append(self.indent() + '    }')
            code.append(self.indent() + '    let out = "";')
            code.append(self.indent() + '    while (out.length < n) {')
            code.append(self.indent() + '        if (_inkey_buffer.length === 0) await _fill_keys(n - out.length);')
            code.append(self.indent() + '        const take = _inkey_buffer.slice(0, n - out.length);')
            code.append(self.indent() + '        _inkey_buffer = _inkey_buffer.slice(take.length);')
            code.append(self.indent() + '        if (take.indexOf("\\x03") >= 0) _error("Break");')
            code.append(self.indent() + '        out += take;')
            code.append(self.indent() + '    }')
            code.append(self.indent() + '    return out;')
            code.append(self.indent() + '}')
            code.append('')

        # Keyboard fill, shared by INPUT$, INPUT and LINE INPUT (one stdin buffer: _inkey_buffer)
        if self.uses_input_func or self.uses_input or self.uses_line_input:
            for line in JS_FILL_KEYS.strip('\n').split('\n'):
                code.append(self.indent() + line)
            code.append('')

        return code

    def _format_data_array(self) -> str:
        """Format DATA values as JavaScript array literal"""
        if not self.data_values:
            return '[]'

        items = []
        for value, vtype in zip(self.data_values, self.data_types):
            if vtype == 'string':
                items.append(f'"{self._escape_string(value)}"')
            else:
                items.append(_js_number(value))

        return '[' + ', '.join(items) + ']'

    def _escape_string(self, s: str) -> str:
        """Escape string for JavaScript"""
        # Handle StringNode if passed by mistake
        if isinstance(s, StringNode):
            s = s.value
        return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')

    def _generate_variables(self) -> List[str]:
        """Generate variable declarations"""
        code = []

        for var_name, var_info in sorted(self.symbols.variables.items()):
            # Use simple lowercase name - type coercion happens at assignment time
            js_name = self._mangle_var_name(var_name)

            # Skip arrays - they're handled separately
            if var_info.is_array:
                # Generate array initialization
                dimensions = var_info.dimensions or [10]  # Default size
                if var_info.var_type == VarType.STRING:
                    init_value = '""'
                else:
                    init_value = '0'
                code.append(self.indent() + f'let {js_name} = {self._create_array_init(dimensions, init_value)};')
            else:
                # Regular variable
                if var_info.var_type == VarType.STRING:
                    code.append(self.indent() + f'let {js_name} = "";')
                elif var_info.var_type == VarType.INTEGER:
                    code.append(self.indent() + f'let {js_name} = 0;')
                else:  # SINGLE or DOUBLE
                    code.append(self.indent() + f'let {js_name} = 0;')

        return code

    def _create_array_init(self, dimensions: List[int], init_value: str) -> str:
        """Create nested array initialization"""
        if len(dimensions) == 1:
            size = dimensions[0] + 1  # BASIC arrays are 0-based with OPTION BASE
            return f'new Array({size}).fill({init_value})'
        else:
            size = dimensions[0] + 1
            inner = self._create_array_init(dimensions[1:], init_value)
            return f'Array.from({{length: {size}}}, () => {inner})'

    def _mangle_var_name(self, name: str) -> str:
        """Convert BASIC variable name to JavaScript identifier.

        In BASIC, FOO%, FOO!, FOO#, FOO$ are all DIFFERENT variables.
        We add type suffixes to distinguish them:
        - FOO (SINGLE/default) -> foo
        - FOO% (INTEGER) -> foo_int
        - FOO# (DOUBLE) -> foo_dbl
        - FOO$ (STRING) -> foo_str
        """
        # Remove type suffix to get base name
        base_name = name.rstrip('$%!#')

        # Make lowercase for consistency
        js_name = base_name.lower()

        # Add type suffix to distinguish different typed variables
        if name.endswith('$'):
            js_name = js_name + '_str'
        elif name.endswith('%'):
            js_name = js_name + '_int'
        elif name.endswith('#'):
            js_name = js_name + '_dbl'
        # SINGLE (! or no suffix) gets no suffix - it's the default

        # Prefix to avoid JS keyword conflicts
        if js_name in ('if', 'for', 'while', 'return', 'function', 'var', 'let', 'const',
                       'class', 'new', 'delete', 'typeof', 'void', 'this', 'with',
                       'switch', 'case', 'default', 'break', 'continue', 'throw', 'try',
                       'catch', 'finally', 'do', 'in', 'of', 'import', 'export', 'null'):
            js_name = 'v_' + js_name

        return js_name

    def _generate_def_fn_functions(self) -> List[str]:
        """Generate DEF FN functions"""
        code = []

        for def_fn in self.def_fn_functions:
            # Function name - DEF FNA becomes _fn_a
            fn_base = def_fn.name.lower()
            func_name = '_fn_' + (fn_base[2:] if fn_base.startswith('fn') else fn_base)  # calls use FNA -> _fn_a

            # Parameters
            params = [self._mangle_var_name(p.name + (p.type_suffix or '')) for p in def_fn.parameters]
            param_str = ', '.join(params)

            # Function body
            expr_code = self._generate_expression(def_fn.expression)

            # A DEF FN whose body can reach INPUT$ or INKEY$ is async
            prefix = 'async ' if self._fn_key(fn_base) in self.async_fns else ''
            code.append(self.indent() + f'{prefix}function {func_name}({param_str}) {{')
            self.indent_level += 1
            code.append(self.indent() + f'return {expr_code};')
            self.indent_level -= 1
            code.append(self.indent() + '}')

        return code

    def _generate_line(self, line: LineNode) -> List[str]:
        """Generate code for one line"""
        code = []
        plan = self.line_plans[line.line_number]
        self._cur_line = line.line_number

        # Case label for this line
        code.append(self.indent() + f'case {line.line_number}:')
        self.indent_level += 1

        reachable = True
        for j, step in enumerate(plan.steps):
            if j in plan.labels:
                # Resume point inside the line (see _plan_lines)
                self.indent_level -= 1
                code.append(self.indent() + f'case {plan.labels[j]}:  // line {line.line_number}, step {j + 1}')
                self.indent_level += 1
                reachable = True
            if not reachable:
                continue  # No jump or label can reach this step
            kind = step[0]
            if kind == 'stmt':
                code.extend(self._generate_statement(step[1], line.line_number))
                if isinstance(step[1], _JUMP_STATEMENTS):
                    reachable = False
            elif kind == 'if':
                # Flat IF: jump over the THEN part when the condition is false
                code.append(self.indent() + f'if (!({self._generate_expression(step[1].condition)})) {{ {self._jump_code(plan.targets[j])} }}')
            elif kind == 'goto':
                code.append(self.indent() + self._jump_code(step[1]))
                reachable = False
            elif kind == 'jump':
                code.append(self.indent() + self._jump_code(plan.targets[j]))
                reachable = False

        # Default: continue to next line
        if reachable:
            code.append(self.indent() + self._jump_code(self.next_line_map.get(line.line_number)))

        self.indent_level -= 1

        return code

    def _jump_code(self, target: Optional[int]) -> str:
        """Set the program counter to a line or label (None: end of program) and leave the switch.

        A jump to the same or an earlier line first lets the browser run now and then.
        """
        check = f'{yield_check(str(target))} ' if self.yield_checks and self._is_back_jump(target) else ''
        return f'{check}_pc = {"null" if target is None else target}; break;'

    def _is_back_jump(self, *targets) -> bool:
        return any(t is not None and t <= self._cur_line for t in targets)

    def _generate_statement(self, stmt, line_number: int) -> List[str]:
        """Generate code for a statement"""
        code = []

        if isinstance(stmt, PrintStatementNode):
            code.extend(self._generate_print(stmt))
        elif isinstance(stmt, PrintUsingStatementNode):
            code.extend(self._generate_print_using(stmt))
        elif isinstance(stmt, LetStatementNode):
            code.extend(self._generate_let(stmt))
        elif isinstance(stmt, (EndStatementNode, SystemStatementNode)):
            if self.uses_error_handling:
                code.append(self.indent() + '_in_error_handler = false;  // END in a handler just ends')
            code.append(self.indent() + '_pc = null;')
            code.append(self.indent() + 'return;')
        elif isinstance(stmt, GotoStatementNode):
            code.extend(self._generate_goto(stmt))
        elif isinstance(stmt, OnGotoStatementNode):
            code.extend(self._generate_on_goto(stmt))
        elif isinstance(stmt, OnGosubStatementNode):
            # RETURN continues with the statement after the ON GOSUB
            code.extend(self._generate_on_gosub(stmt, self._after(stmt, line_number)))
        elif isinstance(stmt, GosubStatementNode):
            # RETURN continues with the statement after the GOSUB
            code.extend(self._generate_gosub(stmt, self._after(stmt, line_number)))
        elif isinstance(stmt, ReturnStatementNode):
            code.extend(self._generate_return(stmt))
        elif isinstance(stmt, ForStatementNode):
            # NEXT loops back to the statement after the FOR
            code.extend(self._generate_for(stmt, line_number, self._after(stmt, line_number)))
        elif isinstance(stmt, NextStatementNode):
            code.extend(self._generate_next(stmt))
        elif isinstance(stmt, WhileStatementNode):
            code.extend(self._generate_while(stmt, line_number))
        elif isinstance(stmt, WendStatementNode):
            code.extend(self._generate_wend(stmt))
        elif isinstance(stmt, IfStatementNode):
            code.extend(self._generate_if(stmt, line_number))
        elif isinstance(stmt, InputStatementNode):
            code.extend(self._generate_input(stmt))
        elif isinstance(stmt, LineInputStatementNode):
            code.extend(self._generate_line_input(stmt))
        elif isinstance(stmt, WriteStatementNode):
            code.extend(self._generate_write(stmt))
        elif isinstance(stmt, LprintStatementNode):
            code.extend(self._generate_lprint(stmt))
        elif isinstance(stmt, ReadStatementNode):
            code.extend(self._generate_read(stmt))
        elif isinstance(stmt, RestoreStatementNode):
            code.extend(self._generate_restore(stmt))
        elif isinstance(stmt, RandomizeStatementNode):
            code.extend(self._generate_randomize(stmt))
        elif isinstance(stmt, StopStatementNode):
            code.extend(self._generate_stop(stmt))
        elif isinstance(stmt, SwapStatementNode):
            code.extend(self._generate_swap(stmt))
        elif isinstance(stmt, MidAssignmentStatementNode):
            code.extend(self._generate_mid_assignment(stmt))
        elif isinstance(stmt, EraseStatementNode):
            code.extend(self._generate_erase(stmt))
        elif isinstance(stmt, OpenStatementNode):
            code.extend(self._generate_open(stmt))
        elif isinstance(stmt, CloseStatementNode):
            code.extend(self._generate_close(stmt))
        elif isinstance(stmt, ResetStatementNode):
            code.extend(self._generate_reset(stmt))
        elif isinstance(stmt, KillStatementNode):
            code.extend(self._generate_kill(stmt))
        elif isinstance(stmt, NameStatementNode):
            code.extend(self._generate_name(stmt))
        elif isinstance(stmt, FilesStatementNode):
            code.extend(self._generate_files(stmt))
        elif isinstance(stmt, FieldStatementNode):
            code.extend(self._generate_field(stmt))
        elif isinstance(stmt, LsetStatementNode):
            code.extend(self._generate_lset(stmt))
        elif isinstance(stmt, RsetStatementNode):
            code.extend(self._generate_rset(stmt))
        elif isinstance(stmt, GetStatementNode):
            code.extend(self._generate_get(stmt))
        elif isinstance(stmt, PutStatementNode):
            code.extend(self._generate_put(stmt))
        elif isinstance(stmt, ChainStatementNode):
            code.extend(self._generate_chain(stmt))
        elif isinstance(stmt, OnErrorStatementNode):
            code.extend(self._generate_on_error(stmt))
        elif isinstance(stmt, ErrorStatementNode):
            code.extend(self._generate_error(stmt, line_number))
        elif isinstance(stmt, ResumeStatementNode):
            code.extend(self._generate_resume(stmt, line_number))
        elif isinstance(stmt, DataStatementNode):
            # DATA statements are processed during initialization
            pass
        elif isinstance(stmt, DimStatementNode):
            # DIM statements are processed during variable generation
            pass
        elif isinstance(stmt, RemarkStatementNode):
            # Comments are skipped
            pass
        elif isinstance(stmt, PokeStatementNode):
            code.extend(self._generate_poke(stmt))
        elif isinstance(stmt, OutStatementNode):
            code.extend(self._generate_out(stmt))
        elif isinstance(stmt, WaitStatementNode):
            code.extend(self._generate_wait(stmt))
        elif isinstance(stmt, CallStatementNode):
            code.extend(self._generate_call(stmt))
        elif isinstance(stmt, WidthStatementNode):
            code.extend(self._generate_width(stmt))
        elif isinstance(stmt, ClearStatementNode):
            code.extend(self._generate_clear(stmt))
        elif isinstance(stmt, CommonStatementNode):
            code.extend(self._generate_common(stmt))
        elif isinstance(stmt, DefTypeStatementNode):
            # DEF type statements are processed during variable analysis
            pass
        else:
            code.append(self.indent() + f'// Unsupported: {type(stmt).__name__}')

        return code

    @staticmethod
    def _js_digits(expr) -> int:
        """Digits argument of the JS number formatters: 0 for INTEGER, else 6 or 16."""
        digits = numeric_digits(expr)
        return 0 if digits == INTEGER_DIGITS else digits

    def _generate_print(self, stmt: PrintStatementNode) -> List[str]:
        """Generate PRINT statement.

        The whole item list goes to the _print_list runtime function, which
        formats numbers the MBASIC way and tracks the cursor column for the
        comma zones, TAB and SPC.
        """
        items = []
        seps = []
        for i, expr in enumerate(stmt.expressions):
            sep = stmt.separators[i] if i < len(stmt.separators) else '\n'
            seps.append(sep or '\n')
            name = getattr(expr, 'name', '').lower() if isinstance(expr, FunctionCallNode) else ''
            if name in ('tab', 'spc') and len(expr.arguments) == 1:
                kind = 1 if name == 'tab' else 2
                items.append(f'[{kind}, {self._generate_expression(expr.arguments[0])}]')
            else:
                value = self._generate_expression(expr)
                if '(' in value:
                    # Evaluated when its turn comes: POS sees the items printed
                    # before it, and "A=" is on the screen before 10^40 prints
                    # Overflow, as in MBASIC.
                    value = f'() => {value}'
                items.append(f'[0, {value}, {self._js_digits(expr)}]')
        filenum = self._generate_expression(stmt.file_number) if stmt.file_number else 'null'
        sep_js = '[' + ', '.join(json.dumps(x) for x in seps) + ']'
        return [self.indent() + f'_print_list({filenum}, [{", ".join(items)}], {sep_js});']

    def _generate_print_using(self, stmt: PrintUsingStatementNode) -> List[str]:
        """Generate PRINT USING statement"""
        filenum = self._generate_expression(stmt.file_number) if stmt.file_number else 'null'
        format_expr = self._generate_expression(stmt.format_string)
        values = ', '.join(self._generate_expression(expr) for expr in stmt.expressions)
        digits = ', '.join(str(self._js_digits(expr)) for expr in stmt.expressions)
        trailing = 'true' if getattr(stmt, 'trailing_separator', False) else 'false'
        return [self.indent() + f'_print_using_stmt({filenum}, {format_expr}, [{values}], [{digits}], {trailing});']

    def _generate_let(self, stmt: LetStatementNode) -> List[str]:
        """Generate LET statement (assignment)"""
        code = []

        # Get variable type for coercion
        var_key = stmt.variable.name + (stmt.variable.type_suffix or '')
        var_type = self._get_var_type(var_key)

        # Check if assigning to array element
        if stmt.variable.subscripts:
            var_name = self._mangle_var_name(var_key)
            access = var_name
            for idx_expr in stmt.variable.subscripts:
                idx = self._generate_expression(idx_expr)
                access = f'{access}[{idx}]'
            expr_code = self._generate_expression(stmt.expression)
            expr_code = self._apply_type_coercion(expr_code, var_type)
            code.append(self.indent() + f'{access} = {expr_code};')
        else:
            var_name = self._mangle_var_name(var_key)
            expr_code = self._generate_expression(stmt.expression)
            expr_code = self._apply_type_coercion(expr_code, var_type)
            code.append(self.indent() + f'{var_name} = {expr_code};')

        return code

    def _get_var_type(self, var_key: str) -> Optional[VarType]:
        """Look up variable type from symbol table.

        Symbol table uses uppercase names, so we uppercase the lookup key.
        """
        # Symbol table uses uppercase
        upper_key = var_key.upper()
        var_info = self.symbols.variables.get(upper_key)
        if var_info:
            return var_info.var_type
        # Check without suffix (might be stored differently)
        base_name = upper_key.rstrip('$%!#')
        var_info = self.symbols.variables.get(base_name)
        if var_info:
            return var_info.var_type
        return None

    def _apply_type_coercion(self, expr_code: str, var_type) -> str:
        """Wrap expression with type coercion function based on target variable type.

        Note: We compare by .name attribute rather than identity to handle the case
        where VarType is imported from different module paths (e.g., 'semantic_analyzer'
        vs 'src.semantic_analyzer'). This can happen due to Python's module caching
        when the same file is imported via different paths.
        """
        if var_type is None:
            return expr_code
        # Compare by name to handle cross-module enum comparison
        type_name = var_type.name if hasattr(var_type, 'name') else str(var_type)
        if type_name == 'INTEGER':
            return f'_toInt({expr_code})'
        elif type_name == 'SINGLE':
            return f'_toSingle({expr_code})'
        elif type_name == 'DOUBLE':
            # No coercion needed - JS Number is already 64-bit double
            return expr_code
        elif type_name == 'STRING':
            # String assignments handled separately
            return expr_code
        return expr_code

    #: True while the code of a string expression that is too complex is made,
    #: so the check is made once, at the outermost node.
    _in_complex_string = False

    def _generate_expression(self, expr) -> str:
        """Generate JavaScript expression

        An expression that needs more than ten string temporaries stops with
        String formula too complex (error 16) when it is reached, as MBASIC does.
        """
        if (not self._in_complex_string and isinstance(expr, (BinaryOpNode, FunctionCallNode))
                and string_temps(expr)[0] > STRING_TEMPORARIES):
            self._in_complex_string = True
            try:
                code = self._generate_expression_plain(expr)
            finally:
                self._in_complex_string = False
            return f'(_error("String formula too complex"), {code})'
        return self._generate_expression_plain(expr)

    def _generate_expression_plain(self, expr) -> str:
        """Generate JavaScript expression"""
        if isinstance(expr, NumberNode):
            value = expr.value
            lit = expr.literal if isinstance(expr.literal, str) else ''
            if lit[:1] == '&' and isinstance(value, (int, float)) and 32768 <= value <= 65535:
                value -= 65536    # MBASIC reads &HFFFF as -1 and &H8000 as -32768
            if isinstance(value, float) and numeric_digits(expr) == SINGLE_DIGITS:
                value = to_single(value)    # a single-precision literal holds 24 bits
            return _js_number(value)
        elif isinstance(expr, StringNode):
            return f'"{self._escape_string(expr.value)}"'
        elif isinstance(expr, VariableNode):
            # Check if it's an array access
            if expr.subscripts:
                var_name = self._mangle_var_name(expr.name + (expr.type_suffix or ''))
                access = var_name
                for idx_expr in expr.subscripts:
                    idx = self._generate_expression(idx_expr)
                    access = f'{access}[{idx}]'
                return access
            elif expr.name.lower() in ('err', 'erl') and expr.type_suffix in (None, '', '%'):
                # ERR and ERL are read-only values, not variables
                return f'_{expr.name.lower()}()'
            else:
                return self._mangle_var_name(expr.name + (expr.type_suffix or ''))
        elif isinstance(expr, BinaryOpNode):
            left = self._generate_expression(expr.left)
            right = self._generate_expression(expr.right)
            op = self._token_to_operator(expr.operator)

            # Map BASIC operators to JavaScript
            if op == '^':
                digits = numeric_digits(expr)
                wrap = '_sg' if digits == SINGLE_DIGITS else '_dg'
                return f'{wrap}(_pow({left}, {right}, {digits}))'
            elif op == '//':
                # Integer division truncates toward zero in MBASIC, so -10 \ 3
                # is -3. Both operands are rounded to 16-bit integers first,
                # and a zero divisor is Division by zero (_idiv).
                return f'_idiv({left}, {right})'
            elif op in ['+', '-', '*', '/', '<', '>', '<=', '>=', '=', '<>']:
                if op == '=':
                    js_op = '==='
                elif op == '<>':
                    js_op = '!=='
                else:
                    js_op = op
                if op in ('+', '-', '*', '/'):
                    digits = numeric_digits(expr)
                    if digits is not None:
                        wrap = '_sg' if digits == SINGLE_DIGITS else '_dg'
                        if op == '/':
                            return f'{wrap}(_div({left}, {right}, {digits}))'
                        return f'{wrap}({left} {js_op} {right})'
                if op not in ('+', '-', '*', '/'):
                    # A comparison is -1 for true and 0 for false in BASIC
                    return f'(({left} {js_op} {right}) ? -1 : 0)'
                return f'({left} {js_op} {right})'
            elif op in LOGICAL_HELPERS:
                # AND, OR, XOR, EQV and IMP are 16-bit integer operators in MBASIC
                return f'{LOGICAL_HELPERS[op]}({left}, {right})'
            elif op == '%':  # MOD
                return f'_mod({left}, {right})'
            else:
                return f'({left} {op} {right})'
        elif isinstance(expr, UnaryOpNode):
            operand = self._generate_expression(expr.operand)
            op = self._token_to_operator(expr.operator)
            if op == 'NOT':
                return f'_not({operand})'  # bitwise on a 16-bit integer: -1 for 0, 0 for -1
            return f'({op}({operand}))'
        elif isinstance(expr, FunctionCallNode):
            return self._generate_function_call(expr)
        else:
            return f'/* Unknown expr: {type(expr).__name__} */'

    def _generate_function_call(self, func: FunctionCallNode) -> str:
        """Generate function call"""
        func_name = func.name.lower()
        args = [self._generate_expression(arg) for arg in func.arguments]

        # Check if it's a DEF FN function (starts with 'fn')
        # User-defined functions from DEF FN
        if func_name.startswith('fn'):
            # FNA -> _fn_a, FNFOO -> _fn_foo
            call = f'_fn_{func_name[2:]}({", ".join(args)})'
            return f'(await {call})' if func_name[2:] in self.async_fns else call

        # Map BASIC function names to JavaScript
        js_func_map = {
            # Math functions
            'abs': '_abs',
            'int': '_int',
            'sqr': '_sqr',
            'sin': '_sin',
            'cos': '_cos',
            'tan': '_tan',
            'atn': '_atn',
            'log': '_log',
            'exp': '_exp',
            'rnd': '_rnd',
            'sgn': '_sgn',
            'fix': '_fix',
            'cint': '_cint',
            'csng': '_csng',
            'cdbl': '_cdbl',
            # String functions
            'left$': '_left',
            'right$': '_right',
            'mid$': '_mid',
            'len': '_len',
            'chr$': '_chr',
            'asc': '_asc',
            'str$': '_str',
            'val': '_val',
            'instr': '_instr',
            'space$': '_space',
            'string$': '_string',
            'hex$': '_hex',
            'oct$': '_oct',
            'pos': '_pos',
            # Print formatting
            'tab': '_tab',
            'spc': '_spc',
            # Error handling
            'erl': '_erl',
            'err': '_err',
            # File I/O functions
            'eof': '_eof',
            'lof': '_lof',
            'loc': '_loc',
            # Binary data conversion
            'mki$': '_mki',
            'mks$': '_mks',
            'mkd$': '_mkd',
            'cvi': '_cvi',
            'cvs': '_cvs',
            'cvd': '_cvd',
            # Memory/system functions
            'fre': '_fre',
            'peek': '_peek',
            'inp': '_inp',
            'varptr': '_varptr',
            'usr': '_usr',
            # Input
            'inkey$': '_inkey',
            'input$': '_input_chars',
        }

        # Lexer token names can omit the BASIC string-function suffix.
        js_func = js_func_map.get(func_name, js_func_map.get(func_name + "$", func_name))
        if js_func == '_str' and func.arguments:
            # STR$ formats like PRINT, so it needs the argument's type
            args.append(str(self._js_digits(func.arguments[0])))
        call = f'{js_func}({", ".join(args)})'
        if js_func in ('_input_chars', '_inkey'):
            return f'(await {call})'
        if func_name in ('sqr', 'sin', 'cos', 'tan', 'atn', 'log', 'exp', 'rnd'):
            digits = numeric_digits(func)
            if digits == SINGLE_DIGITS:
                # MBASIC's maths functions return single precision
                return f'_sg({call})'
            if digits is not None and func_name != 'rnd':
                return f'_dg({call})'
        return call

    def _generate_goto(self, stmt: GotoStatementNode) -> List[str]:
        """Generate GOTO statement"""
        code = []
        code.append(self.indent() + self._jump_code(stmt.line_number))
        return code

    def _generate_on_goto(self, stmt: OnGotoStatementNode) -> List[str]:
        """Generate ON...GOTO statement"""
        code = []
        expr = self._generate_expression(stmt.expression)
        code.append(self.indent() + f'{{')
        self.indent_level += 1
        code.append(self.indent() + f'const _idx = Math.floor({expr});')
        code.append(self.indent() + f'const _targets = [{", ".join(str(t) for t in stmt.line_numbers)}];')
        code.append(self.indent() + f'if (_idx >= 1 && _idx <= _targets.length) {{')
        self.indent_level += 1
        if self.yield_checks and self._is_back_jump(*stmt.line_numbers):
            code.append(self.indent() + yield_check('_targets[_idx - 1]'))
        code.append(self.indent() + f'_pc = _targets[_idx - 1];')
        code.append(self.indent() + f'break;')
        self.indent_level -= 1
        code.append(self.indent() + f'}}')
        code.append(self.indent() + f'// Fall through if index out of range')
        self.indent_level -= 1
        code.append(self.indent() + f'}}')
        return code

    def _generate_on_gosub(self, stmt: OnGosubStatementNode, return_address: Optional[int]) -> List[str]:
        """Generate ON...GOSUB statement"""
        code = []
        expr = self._generate_expression(stmt.expression)
        code.append(self.indent() + f'{{')
        self.indent_level += 1
        code.append(self.indent() + f'const _idx = Math.floor({expr});')
        code.append(self.indent() + f'const _targets = [{", ".join(str(t) for t in stmt.line_numbers)}];')
        code.append(self.indent() + f'if (_idx >= 1 && _idx <= _targets.length) {{')
        self.indent_level += 1
        if return_address is not None:
            code.append(self.indent() + f'_gosub({return_address});')
        else:
            code.append(self.indent() + f'_gosub(null);  // End of program')
        if self.yield_checks and self._is_back_jump(*stmt.line_numbers):
            code.append(self.indent() + yield_check('_targets[_idx - 1]'))
        code.append(self.indent() + f'_pc = _targets[_idx - 1];')
        code.append(self.indent() + f'break;')
        self.indent_level -= 1
        code.append(self.indent() + f'}}')
        code.append(self.indent() + f'// Fall through if index out of range')
        self.indent_level -= 1
        code.append(self.indent() + f'}}')
        return code

    def _generate_gosub(self, stmt: GosubStatementNode, return_address: Optional[int]) -> List[str]:
        """Generate GOSUB statement"""
        code = []
        if return_address is not None:
            code.append(self.indent() + f'_gosub({return_address});')
        else:
            code.append(self.indent() + f'_gosub(null);  // End of program')
        code.append(self.indent() + self._jump_code(stmt.line_number))
        return code

    def _generate_return(self, stmt: ReturnStatementNode) -> List[str]:
        """Generate RETURN statement"""
        code = []
        code.append(self.indent() + '_pc = _return();')
        code.append(self.indent() + 'break;')
        return code

    def _generate_for(self, stmt: ForStatementNode, for_line: int, return_line: Optional[int]) -> List[str]:
        """Generate FOR statement - variable-indexed approach"""
        code = []
        var_key = stmt.variable.name + (stmt.variable.type_suffix or '')
        var_name = self._mangle_var_name(var_key)
        var_type = self._get_var_type(var_key)
        start_expr = self._generate_expression(stmt.start_expr)
        end_expr = self._generate_expression(stmt.end_expr)

        if stmt.step_expr:
            step_expr = self._generate_expression(stmt.step_expr)
        else:
            step_expr = '1'

        # Apply type coercion to initial value
        start_expr = self._apply_type_coercion(start_expr, var_type)

        # Initialize loop variable and store state
        code.append(self.indent() + f'{{')
        self.indent_level += 1
        code.append(self.indent() + f'const _end = {end_expr};')
        code.append(self.indent() + f'const _step = {step_expr};')
        code.append(self.indent() + f'{var_name} = {start_expr};')

        # Check initial condition before entering loop
        code.append(self.indent() + f'if (!_for_done({var_name}, _end, _step)) {{')
        self.indent_level += 1

        # Determine type coercion function name for NEXT increment
        type_coerce_fn = 'null'
        if var_type == VarType.INTEGER:
            type_coerce_fn = '_toInt'
        elif var_type == VarType.SINGLE:
            type_coerce_fn = '_toSingle'

        code.append(self.indent() + f'_for_loops["{var_name}"] = {{')
        self.indent_level += 1
        code.append(self.indent() + f'end: _end,')
        code.append(self.indent() + f'step: _step,')
        code.append(self.indent() + f'coerce: {type_coerce_fn},')
        if return_line is not None:
            code.append(self.indent() + f'line: {return_line}')
        else:
            code.append(self.indent() + f'line: null  // End of program')
        self.indent_level -= 1
        code.append(self.indent() + f'}};')

        self.indent_level -= 1
        code.append(self.indent() + f'}} else {{')
        self.indent_level += 1
        code.append(self.indent() + f'// Skip loop - condition not met')
        # Jump to the statement after the matching NEXT if we know where it is
        next_stmt = self.for_to_next.get(id(stmt))
        if next_stmt is not None:
            code.append(self.indent() + self._jump_code(self._after(next_stmt, self.next_line_of[id(next_stmt)])))
        else:
            code.append(self.indent() + f'// Continue to next statement (NEXT not found)')
        self.indent_level -= 1
        code.append(self.indent() + f'}}')
        self.indent_level -= 1
        code.append(self.indent() + f'}}')

        return code

    def _generate_next(self, stmt: NextStatementNode) -> List[str]:
        """Generate NEXT statement - check condition and loop back"""
        code = []

        # Get variable names
        variables = stmt.variables
        if not variables:
            # NEXT without variable - look up which variable to use
            var_name_base = self.next_var_map.get(id(stmt))
            if var_name_base:
                # next_var_map holds the JS name of the FOR variable, used as it is
                variables = [var_name_base]
            else:
                # No matching FOR found
                code.append(self.indent() + '_error("NEXT without FOR");')
                return code

        # Handle each variable (NEXT can have multiple variables: NEXT I, J, K)
        for var in variables:
            if isinstance(var, str):
                var_name = var
            else:
                var_name = self._mangle_var_name(var.name + (getattr(var, 'type_suffix', '') or ''))

            # Increment variable and check condition
            code.append(self.indent() + f'if (_for_loops["{var_name}"]) {{')
            self.indent_level += 1
            code.append(self.indent() + f'const _loop = _for_loops["{var_name}"];')
            code.append(self.indent() + f'{var_name} = _loop.coerce ? _loop.coerce({var_name} + _loop.step) : ({var_name} + _loop.step);')
            code.append(self.indent() + f'const _continue = !_for_done({var_name}, _loop.end, _loop.step);')
            code.append(self.indent() + f'if (_continue) {{')
            self.indent_level += 1
            if self.yield_checks:
                code.append(self.indent() + yield_check('_loop.line'))
            code.append(self.indent() + f'_pc = _loop.line;')
            code.append(self.indent() + f'break;')
            self.indent_level -= 1
            code.append(self.indent() + f'}} else {{')
            self.indent_level += 1
            code.append(self.indent() + f'delete _for_loops["{var_name}"];')
            self.indent_level -= 1
            code.append(self.indent() + f'}}')
            self.indent_level -= 1
            code.append(self.indent() + f'}}')

        return code

    def _generate_while(self, stmt: WhileStatementNode, line_number: int) -> List[str]:
        """Generate WHILE: leave the loop to the statement after the WEND when the condition is false"""
        code = []
        condition = self._generate_expression(stmt.condition)
        wend = self.while_to_wend.get(id(stmt))
        if wend is None:
            # The real binary looks for the WEND when the WHILE runs, whatever the condition is
            return [self.indent() + '_error("WHILE without WEND");']
        else:
            leave = self._jump_code(self._after(wend, self.next_line_of[id(wend)]))
        code.append(self.indent() + f'if (!({condition})) {{ {leave} }}')
        return code

    def _generate_wend(self, stmt: WendStatementNode) -> List[str]:
        """Generate WEND: jump back to the WHILE step"""
        while_stmt = self.wend_to_while.get(id(stmt))
        if while_stmt is None:
            return [self.indent() + '_error("WEND without WHILE");']
        target = self.while_target[id(while_stmt)]
        # The label of a WHILE later on the same line is above CONT_LABEL_BASE: always look at the clock
        check = f'{yield_check(str(target))} ' if self.yield_checks else ''
        return [self.indent() + f'{check}_pc = {target}; break;']

    def _generate_if(self, stmt: IfStatementNode, current_line: int) -> List[str]:
        """Generate IF statement"""
        code = []
        condition = self._generate_expression(stmt.condition)

        if stmt.then_statements or stmt.then_line_number:
            code.append(self.indent() + f'if ({condition}) {{')
            self.indent_level += 1
            if stmt.then_statements:
                for s in stmt.then_statements:
                    code.extend(self._generate_statement(s, current_line))
            else:
                # IF...THEN line_number (GOTO)
                code.append(self.indent() + self._jump_code(stmt.then_line_number))
            self.indent_level -= 1

            if stmt.else_statements or stmt.else_line_number is not None:
                code.append(self.indent() + '} else {')
                self.indent_level += 1
                if stmt.else_statements:
                    for s in stmt.else_statements:
                        code.extend(self._generate_statement(s, current_line))
                else:
                    code.append(self.indent() + self._jump_code(stmt.else_line_number))
                self.indent_level -= 1

            code.append(self.indent() + '}')

        return code

    def _generate_input(self, stmt: InputStatementNode) -> List[str]:
        """Generate INPUT statement"""
        code = []

        # Check for file I/O
        if stmt.file_number:
            filenum_expr = self._generate_expression(stmt.file_number)
            # Generate input for each variable from file
            for var in stmt.variables:
                var_key = var.name + (var.type_suffix or '')
                var_name = self._input_lvalue(var)
                var_type = self._get_var_type(var_key)

                if var_type == VarType.STRING:
                    # String input from file
                    code.append(self.indent() + f'{var_name} = _finput({filenum_expr});')
                elif var_type == VarType.INTEGER:
                    # Integer input from file - use _toInt for proper truncation
                    code.append(self.indent() + f'{var_name} = _toInt(parseFloat(_finput({filenum_expr})) || 0);')
                elif var_type == VarType.SINGLE:
                    # Single precision input from file
                    code.append(self.indent() + f'{var_name} = _toSingle(parseFloat(_finput({filenum_expr})) || 0);')
                else:
                    # Double precision or unknown - no coercion needed
                    code.append(self.indent() + f'{var_name} = parseFloat(_finput({filenum_expr})) || 0;')
        else:
            # Interactive input. A comma after the prompt string drops the "? " (real MBASIC 5.21);
            # a semicolon after INPUT only keeps the cursor on the line, which a script cannot show.
            if stmt.prompt:
                prompt_str = self._escape_string(stmt.prompt)
                if not stmt.prompt_comma:
                    prompt_str += "? "
            else:
                prompt_str = "? "

            letters = []
            targets = []
            for var in stmt.variables:
                var_key = var.name + (var.type_suffix or '')
                type_name = self._type_name(self._get_var_type(var_key))
                letters.append({'STRING': 'S', 'INTEGER': 'I', 'SINGLE': 'F'}.get(type_name, 'N'))
                targets.append(self._input_lvalue(var))
            # One _input_vals call reads the whole line for all variables (Redo covers them together)
            assigns = ' '.join(f'{t} = _iv[{k}];' for k, t in enumerate(targets))
            code.append(self.indent() + f'{{ const _iv = await _input_vals("{prompt_str}", "{"".join(letters)}"{", true" if stmt.suppress_question else ""}); {assigns} }}')

        return code

    @staticmethod
    def _type_name(var_type) -> str:
        return var_type.name if hasattr(var_type, 'name') else str(var_type)

    def _input_lvalue(self, var) -> str:
        """JavaScript assignment target for an INPUT variable (plain variable or array element)."""
        access = self._mangle_var_name(var.name + (var.type_suffix or ''))
        for idx_expr in (var.subscripts or []):
            access = f'{access}[{self._generate_expression(idx_expr)}]'
        return access

    def _generate_line_input(self, stmt: LineInputStatementNode) -> List[str]:
        """Generate LINE INPUT statement - reads entire line without parsing"""
        code = []

        # LINE INPUT always reads into a string variable
        var_name = self._input_lvalue(stmt.variable)

        # Check for file I/O
        if stmt.file_number:
            filenum_expr = self._generate_expression(stmt.file_number)
            code.append(self.indent() + f'{var_name} = _fline_input({filenum_expr});')
        else:
            # Interactive input
            # Build prompt string
            if stmt.prompt:
                prompt_expr = self._generate_expression(stmt.prompt)
            else:
                prompt_expr = '""'  # LINE INPUT shows no "? "

            code.append(self.indent() + f'{var_name} = await _line_input({prompt_expr});')

        return code

    def _generate_write(self, stmt: WriteStatementNode) -> List[str]:
        """Generate WRITE statement - CSV formatted output"""
        code = []

        # Determine output function
        if stmt.file_number:
            filenum_expr = self._generate_expression(stmt.file_number)
            print_func = f'_fprint({filenum_expr}, '
        else:
            print_func = '_print('

        # WRITE outputs: strings quoted, numbers in MBASIC format without
        # padding spaces, comma separated
        trailing = getattr(stmt, 'trailing_separator', None)
        bad = getattr(stmt, 'bad_separator', False)
        if stmt.file_number and not stmt.expressions and not getattr(stmt, 'file_comma', True):
            # WRITE #n alone is a Syntax error when it runs
            code.append(self.indent() + '_error("Syntax error");')
        elif bad and not stmt.expressions:
            code.append(self.indent() + '_error("Syntax error");')
        elif not stmt.expressions:
            # Empty WRITE - just newline
            code.append(self.indent() + f'{print_func}"");')
        else:
            parts = []
            for expr in stmt.expressions:
                expr_code = self._generate_expression(expr)
                parts.append(f'_write_format({expr_code}, {self._js_digits(expr)})')

            # Join with commas and print
            output = ' + "," + '.join(parts)
            if trailing or bad:
                # Items and a ',' with no end of line, then the error
                code.append(self.indent() + f'{print_func}{output} + ",", false);')
                code.append(self.indent() + ('_error("Syntax error");' if bad
                                             else '_error("Missing operand");'))
            else:
                code.append(self.indent() + f'{print_func}{output});')

        return code

    def _generate_lprint(self, stmt: LprintStatementNode) -> List[str]:
        """Generate LPRINT statement - print to line printer (console.log)"""
        code = []

        # Skip file I/O for now
        if stmt.file_number:
            code.append(self.indent() + '// LPRINT #file not supported')
            return code

        # LPRINT is like PRINT but outputs to console.log instead of output div
        if not stmt.expressions:
            # Empty LPRINT - just newline
            code.append(self.indent() + 'console.log("");')
        else:
            for i, expr in enumerate(stmt.expressions):
                is_last = (i == len(stmt.expressions) - 1)
                separator = stmt.separators[i] if i < len(stmt.separators) else None

                expr_code = self._generate_expression(expr)

                # Determine if we should add a newline
                # Newline if last item and no separator (None or '\n' means end of statement)
                newline = 'true' if (is_last and separator in (None, '\n')) else 'false'

                code.append(self.indent() + f'_lprint(_pstr({expr_code}, {self._js_digits(expr)}), {newline});')

                # Handle separator (comma for tab, semicolon for no space)
                if separator == ',':
                    code.append(self.indent() + '_lprint("\\t", false);')
                elif separator == ';':
                    # Semicolon means no space - already handled
                    pass

        return code

    def _generate_read(self, stmt: ReadStatementNode) -> List[str]:
        """Generate READ statement"""
        code = []
        for var in stmt.variables:
            var_name = self._mangle_var_name(var.name + (var.type_suffix or ''))
            code.append(self.indent() + f'{var_name} = _read();')
        return code

    def _generate_restore(self, stmt: RestoreStatementNode) -> List[str]:
        """Generate RESTORE statement"""
        code = []
        code.append(self.indent() + '_restore();')
        return code

    def _generate_randomize(self, stmt: RandomizeStatementNode) -> List[str]:
        """Generate RANDOMIZE statement"""
        code = []
        if stmt.seed:
            # RANDOMIZE with seed
            seed_expr = self._generate_expression(stmt.seed)
            code.append(self.indent() + f'_rnd(-{seed_expr});  // Seed random generator')
        else:
            # RANDOMIZE without seed - use current time
            code.append(self.indent() + '_rnd(-(new Date().getTime()));  // Seed with current time')
        return code

    def _generate_stop(self, stmt: StopStatementNode) -> List[str]:
        """Generate STOP statement - halts execution"""
        code = []
        code.append(self.indent() + '_pc = null;')
        code.append(self.indent() + 'return;')
        return code

    def _generate_swap(self, stmt: SwapStatementNode) -> List[str]:
        """Generate SWAP statement - swaps two variables"""
        code = []
        var1_name = self._mangle_var_name(stmt.var1.name + (stmt.var1.type_suffix or ''))
        var2_name = self._mangle_var_name(stmt.var2.name + (stmt.var2.type_suffix or ''))

        # Use destructuring assignment for clean swap
        code.append(self.indent() + f'[{var1_name}, {var2_name}] = [{var2_name}, {var1_name}];')
        return code

    def _generate_mid_assignment(self, stmt: MidAssignmentStatementNode) -> List[str]:
        """Generate MID$ assignment - modifies substring in place

        Syntax: MID$(string_var, start, length) = value
        Replaces 'length' characters starting at 'start' (1-based) with 'value'
        """
        code = []

        # Generate the variable reference (can be simple variable or array element)
        var_expr = self._generate_expression(stmt.string_var)
        start_expr = self._generate_expression(stmt.start)
        length_expr = self._generate_expression(stmt.length)
        value_expr = self._generate_expression(stmt.value)

        # MID$ assignment in JavaScript:
        # var = var.substring(0, start-1) + value.substring(0, length) + var.substring(start-1+length)
        # Need to handle the case where value is shorter/longer than length

        code.append(self.indent() + '{')
        self.indent_level += 1

        # Save the expressions to temporary variables to avoid re-evaluation
        code.append(self.indent() + f'const _mid_start = {start_expr};')
        code.append(self.indent() + f'const _mid_len = {length_expr};')
        code.append(self.indent() + f'const _mid_val = String({value_expr}).substring(0, _mid_len);')
        code.append(self.indent() + f'const _mid_str = String({var_expr});')

        # Build the new string
        code.append(self.indent() +
                   f'{var_expr} = _mid_str.substring(0, _mid_start - 1) + ' +
                   f'_mid_val + _mid_str.substring(_mid_start - 1 + _mid_len);')

        self.indent_level -= 1
        code.append(self.indent() + '}')

        return code

    def _generate_erase(self, stmt: EraseStatementNode) -> List[str]:
        """Generate ERASE statement - resets arrays to default values"""
        code = []
        for array_name in stmt.array_names:
            # Look up the array in the symbol table to get its type and dimensions
            var_info = self.symbols.variables.get(array_name)
            if var_info and var_info.is_array:
                js_name = self._mangle_var_name(array_name)
                dimensions = var_info.dimensions or [10]

                # Determine default value based on type
                if var_info.var_type == VarType.STRING:
                    init_value = '""'
                else:
                    init_value = '0'

                # Recreate the array with default values
                code.append(self.indent() + f'{js_name} = {self._create_array_init(dimensions, init_value)};')
        return code

    def _generate_open(self, stmt: OpenStatementNode) -> List[str]:
        """Generate OPEN statement - open file for I/O"""
        code = []
        filenum_expr = self._generate_expression(stmt.file_number)
        filename_expr = self._generate_expression(stmt.filename)
        mode = stmt.mode  # "I", "O", "A", or "R"

        # For random files, include record length (default 128 if not specified)
        if stmt.record_length:
            reclen_expr = self._generate_expression(stmt.record_length)
            code.append(self.indent() + f'_fopen({filenum_expr}, {filename_expr}, "{mode}", {reclen_expr});')
        else:
            code.append(self.indent() + f'_fopen({filenum_expr}, {filename_expr}, "{mode}");')
        return code

    def _generate_close(self, stmt: CloseStatementNode) -> List[str]:
        """Generate CLOSE statement - close file(s)"""
        code = []
        if not stmt.file_numbers:
            # CLOSE with no arguments - close all files
            code.append(self.indent() + '_fclose();')
        else:
            # CLOSE #1, #2, ...
            for file_number in stmt.file_numbers:
                filenum_expr = self._generate_expression(file_number)
                code.append(self.indent() + f'_fclose({filenum_expr});')
        return code

    def _generate_reset(self, stmt: ResetStatementNode) -> List[str]:
        """Generate RESET statement - close all open files"""
        code = []
        code.append(self.indent() + '_fclose();  // RESET - close all files')
        return code

    def _generate_kill(self, stmt: KillStatementNode) -> List[str]:
        """Generate KILL statement - delete file"""
        code = []
        filename_expr = self._generate_expression(stmt.filename)
        code.append(self.indent() + f'_fkill({filename_expr});')
        return code

    def _generate_name(self, stmt: NameStatementNode) -> List[str]:
        """Generate NAME statement - rename file"""
        code = []
        old_filename_expr = self._generate_expression(stmt.old_filename)
        new_filename_expr = self._generate_expression(stmt.new_filename)
        code.append(self.indent() + f'_fname({old_filename_expr}, {new_filename_expr});')
        return code

    def _generate_files(self, stmt: FilesStatementNode) -> List[str]:
        """Generate FILES statement - list directory"""
        code = []
        if stmt.filespec:
            filespec_expr = self._generate_expression(stmt.filespec)
            code.append(self.indent() + f'_ffiles({filespec_expr});')
        else:
            code.append(self.indent() + '_ffiles("*");')
        return code

    def _generate_field(self, stmt: FieldStatementNode) -> List[str]:
        """Generate FIELD statement - define random-access file buffer layout"""
        code = []
        filenum_expr = self._generate_expression(stmt.file_number)

        # Build array of field definitions: [[width1, var1], [width2, var2], ...]
        fields_array = []
        for width, var in stmt.fields:
            width_expr = self._generate_expression(width)
            var_name = var.name  # Variable name (string variable)
            fields_array.append(f'[{width_expr}, "{var_name}"]')

        fields_str = '[' + ', '.join(fields_array) + ']'
        code.append(self.indent() + f'_ffield({filenum_expr}, {fields_str});')
        return code

    def _generate_lset(self, stmt: LsetStatementNode) -> List[str]:
        """Generate LSET statement - left-justify string in field variable"""
        code = []
        var_name = stmt.variable.name
        value_expr = self._generate_expression(stmt.expression)
        code.append(self.indent() + f'_flset("{var_name}", {value_expr});')
        return code

    def _generate_rset(self, stmt: RsetStatementNode) -> List[str]:
        """Generate RSET statement - right-justify string in field variable"""
        code = []
        var_name = stmt.variable.name
        value_expr = self._generate_expression(stmt.expression)
        code.append(self.indent() + f'_frset("{var_name}", {value_expr});')
        return code

    def _generate_get(self, stmt: GetStatementNode) -> List[str]:
        """Generate GET statement - read record from random-access file"""
        code = []
        filenum_expr = self._generate_expression(stmt.file_number)
        if stmt.record_number:
            rec_expr = self._generate_expression(stmt.record_number)
            code.append(self.indent() + f'_fget({filenum_expr}, {rec_expr});')
        else:
            code.append(self.indent() + f'_fget({filenum_expr});')
        return code

    def _generate_put(self, stmt: PutStatementNode) -> List[str]:
        """Generate PUT statement - write record to random-access file"""
        code = []
        filenum_expr = self._generate_expression(stmt.file_number)
        if stmt.record_number:
            rec_expr = self._generate_expression(stmt.record_number)
            code.append(self.indent() + f'_fput({filenum_expr}, {rec_expr});')
        else:
            code.append(self.indent() + f'_fput({filenum_expr});')
        return code

    def _generate_chain(self, stmt: ChainStatementNode) -> List[str]:
        """Generate CHAIN statement - chain to another program

        Browser: Navigate to new HTML page (window.location.href)
        Node.js: Spawn new process and exit (child_process.spawn)

        Note: Like the Z80 backend, we only support basic CHAIN "filename"
        MERGE, line number, ALL, and DELETE options are not supported.
        """
        code = []

        # Warn about unsupported options
        if stmt.merge:
            code.append(self.indent() + '// MERGE option not supported in compiled code')
        if stmt.start_line:
            code.append(self.indent() + '// Start line not supported in compiled code')
        if stmt.all_flag:
            code.append(self.indent() + '// ALL option not supported - no COMMON in MBASIC 5.21')
        if stmt.delete_range:
            code.append(self.indent() + '// DELETE option not supported in compiled code')

        filename_expr = self._generate_expression(stmt.filename)

        code.append(self.indent() + '// CHAIN to another program')
        code.append(self.indent() + 'if (typeof window !== "undefined") {')
        self.indent_level += 1
        code.append(self.indent() + '// Browser: Navigate to new HTML page')
        code.append(self.indent() + f'window.location.href = {filename_expr} + ".html";')
        self.indent_level -= 1
        code.append(self.indent() + '} else if (typeof process !== "undefined") {')
        self.indent_level += 1
        code.append(self.indent() + '// Node.js: Spawn new program and exit')
        code.append(self.indent() + 'const { spawn } = require("child_process");')
        code.append(self.indent() + f'const newProgram = {filename_expr} + ".js";')
        code.append(self.indent() + 'spawn("node", [newProgram], {')
        self.indent_level += 1
        code.append(self.indent() + 'stdio: "inherit",  // Pass through stdin/stdout/stderr')
        code.append(self.indent() + 'detached: false')
        self.indent_level -= 1
        code.append(self.indent() + '});')
        code.append(self.indent() + 'process.exit(0);  // Exit current program')
        self.indent_level -= 1
        code.append(self.indent() + '}')

        return code

    def _generate_on_error(self, stmt: OnErrorStatementNode) -> List[str]:
        """Generate ON ERROR GOTO/GOSUB statement"""
        code = []
        if stmt.line_number == 0:
            # ON ERROR GOTO 0 - disable error handling
            code.append(self.indent() + '_error_handler = 0;')
            # Inside a handler it also raises the pending error again
            code.append(self.indent() + 'if (_in_error_handler) _error(_ERR_MSGS[_error_code] || "Illegal function call");')
        elif stmt.line_number not in self.line_labels:
            # The binary looks the line up when the statement runs
            code.append(self.indent() + '_error("Undefined line number");')
        else:
            # ON ERROR GOTO line or ON ERROR GOSUB line
            code.append(self.indent() + f'_error_handler = {stmt.line_number};')
            code.append(self.indent() + f'_error_handler_is_gosub = {str(stmt.is_gosub).lower()};')
        return code

    def _generate_error(self, stmt: ErrorStatementNode, current_line: int) -> List[str]:
        """Generate ERROR statement - simulate an error"""
        code = []
        error_code = self._generate_expression(stmt.error_code)
        code.append(self.indent() + f'{{')
        self.indent_level += 1
        code.append(self.indent() + f'const _next = _trigger_error({error_code}, {current_line});')
        code.append(self.indent() + f'if (_next !== undefined) {{')
        self.indent_level += 1
        code.append(self.indent() + f'_pc = _next;')
        code.append(self.indent() + f'break;')
        self.indent_level -= 1
        code.append(self.indent() + f'}}')
        self.indent_level -= 1
        code.append(self.indent() + f'}}')
        return code

    def _generate_resume(self, stmt: ResumeStatementNode, current_line: int) -> List[str]:
        """Generate RESUME statement"""
        code = []
        code.append(self.indent() + '_in_error_handler = false;')

        # ERR reads 0 after RESUME; ERL keeps the line number.
        code.append(self.indent() + '_error_code = 0;')
        if stmt.line_number is None or stmt.line_number == 0:
            # RESUME (or RESUME 0) - return to line that caused error
            if self.yield_checks:
                code.append(self.indent() + yield_check('_error_line'))
            code.append(self.indent() + '_pc = _error_line;')
            code.append(self.indent() + 'break;')
        elif stmt.line_number == -1:
            # RESUME NEXT (the parser's -1) - continue at next line after error
            code.append(self.indent() + 'const _next_line = _next_lines[_error_line] === undefined ? null : _next_lines[_error_line];')
            code.append(self.indent() + 'if (_next_line !== null) {')
            self.indent_level += 1
            code.append(self.indent() + '_pc = _next_line;')
            self.indent_level -= 1
            code.append(self.indent() + '} else {')
            self.indent_level += 1
            code.append(self.indent() + '_pc = null;  // End of program')
            self.indent_level -= 1
            code.append(self.indent() + '}')
            code.append(self.indent() + 'break;')
        else:
            # RESUME line_number - continue at specific line
            code.append(self.indent() + self._jump_code(stmt.line_number))

        return code

    def _generate_poke(self, stmt: PokeStatementNode) -> List[str]:
        """Generate POKE statement - write to memory address (stub: warning only)"""
        code = []
        addr = self._generate_expression(stmt.address)
        val = self._generate_expression(stmt.value)
        code.append(self.indent() + f'console.warn("POKE " + ({addr}) + "," + ({val}) + " - not supported in JavaScript");')
        return code

    def _generate_out(self, stmt: OutStatementNode) -> List[str]:
        """Generate OUT statement - write to I/O port (stub: warning only)"""
        code = []
        port = self._generate_expression(stmt.port)
        val = self._generate_expression(stmt.value)
        code.append(self.indent() + f'console.warn("OUT " + ({port}) + "," + ({val}) + " - not supported in JavaScript");')
        return code

    def _generate_wait(self, stmt: WaitStatementNode) -> List[str]:
        """Generate WAIT statement - wait for I/O port (stub: returns immediately)"""
        code = []
        port = self._generate_expression(stmt.port)
        and_mask = self._generate_expression(stmt.and_mask)
        code.append(self.indent() + f'console.warn("WAIT " + ({port}) + "," + ({and_mask}) + " - not supported in JavaScript, returning immediately");')
        return code

    def _generate_call(self, stmt: CallStatementNode) -> List[str]:
        """Generate CALL statement - call machine code (stub: warning only)"""
        code = []
        addr = self._generate_expression(stmt.address)
        code.append(self.indent() + f'console.warn("CALL " + ({addr}) + " - not supported in JavaScript");')
        return code

    def _generate_width(self, stmt: WidthStatementNode) -> List[str]:
        """Generate WIDTH statement - set the screen line width

        PRINT wraps at _width and measures TAB and the comma zones against it.
        A form with a device (WIDTH n, device) is accepted and ignored, as in
        the interpreter.
        """
        width = self._generate_expression(stmt.width)
        if stmt.device is not None:
            return [self.indent() + f'// WIDTH {width}, device - ignored']
        return [self.indent() + f'_width = _set_width({width});']

    def _generate_clear(self, stmt: ClearStatementNode) -> List[str]:
        """Generate CLEAR statement - clear variables and set memory limits (stub)

        In MBASIC, CLEAR resets all variables and optionally sets string/stack space.
        In JavaScript, we just reinitialize variables (without actually doing anything
        since JS handles memory automatically).
        """
        code = []
        code.append(self.indent() + '// CLEAR - JavaScript manages memory automatically')
        return code

    def _generate_common(self, stmt: CommonStatementNode) -> List[str]:
        """Generate COMMON statement - share variables between CHAINed programs (stub)

        COMMON declares variables to be shared between CHAINed programs.
        In JavaScript browser, we could use sessionStorage/localStorage.
        For now, just warn that it's not fully supported.
        """
        code = []
        var_names = ', '.join(v.name for v in stmt.variables)
        code.append(self.indent() + f'// COMMON {var_names} - variable sharing not supported in JavaScript')
        return code
