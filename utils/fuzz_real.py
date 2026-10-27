#!/usr/bin/env python3
"""Differential random test: real MBASIC 5.21 against the interpreter, JS and C.

    python3 utils/fuzz_real.py SEED [SEED ...] [--count N] [--mode MODE] [--js] [--c]
                               [--gen-only] [--out DIR]

For each seed, writes a random program fz_SEED.bas in DIR, runs the program on
real MBASIC 5.21 (com/mbasic.com under cpmemu) and on the interpreter, and
prints a diff for each implementation whose output differs.  --js and --c add
the JS and C backends (the C backend has no ON ERROR, so most programs are
refused; use utils/fuzz_real_c.py for C).  Exit status 1 when anything differs.

Every line prints "@n" first, so a diff shows which line it came from.  An
error handler prints E;ERR;ERL and resumes at the next statement.

Modes:
  misc   expressions, string functions, conversions, PRINT USING (default)
  flow   ON GOTO/GOSUB, FOR/NEXT, WHILE/WEND, IF with GOSUB, string compares
  calls  built-in functions with edge-case and wrong-type arguments
  data   READ/DATA/RESTORE and PRINT USING formats

The values stay where MBF single precision and IEEE agree (small integers,
halves, short decimals), because MBF arithmetic is deliberately not emulated
(docs/dev/MBASIC_521_DIVERGENCES_TODO.md).  A difference that is a known MBF
or design difference is not a bug; add a guard here for the case instead.
"""
import argparse
import difflib
import random
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_real_mbasic import ROOT, run_real  # noqa: E402

MODES = ('misc', 'flow', 'calls', 'data')
rnd = random.Random(0)

INTS = [0, 1, -1, 2, 3, 7, 10, 15, 16, 100, 255, 256, 1000, 32767, -32768, 32768, -32769, 65535, 40000]
NUMS = INTS + [0.5, 1.5, 2.5, -0.5, -1.5, -2.5, 0.25, 3.75, 123.456, 1E6, 1E-3, 12345.6, -0.001]
STRS = ['""', '"A"', '"abc"', '"Hello"', '" x "', '"12"', '"-3.5"', '"&H1F"', '"1E3"', '"  7"', '"a,b"']


def num():
    v = rnd.choice(NUMS)
    return f'({v})' if str(v).startswith('-') else str(v)


def small():
    return str(rnd.choice([0, 1, 2, 3, 4, 5, 6, 10, 255, 256, -1]))


def string():
    k = rnd.random()
    if k < 0.6:
        return rnd.choice(STRS)
    if k < 0.8:
        return f'CHR$({rnd.choice([65, 97, 48, 32, 126])})'
    return f'STR$({num()})'


def int_expr(depth=0):
    if depth > 1 or rnd.random() < 0.4:
        return str(rnd.choice(INTS)) if rnd.random() < 0.8 else num()
    op = rnd.choice(['\\', 'MOD', 'AND', 'OR', 'XOR', 'EQV', 'IMP', '+', '-', '*', '=', '<', '>=', '<>'])
    a, b = int_expr(depth + 1), int_expr(depth + 1)
    a = f'({a})' if ' ' in a else a
    b = f'({b})' if ' ' in b else b
    if op in ('+', '-', '*', '=', '<', '>=', '<>', '\\'):
        return f'{a}{op}{b}'
    return f'{a} {op} {b}'


def str_expr():
    f = rnd.choice(['LEFT$', 'RIGHT$', 'MID$', 'MID3', 'INSTR', 'INSTR3', 'STRING$', 'STRINGS',
                    'SPACE$', 'ASC', 'LEN', 'HEX$', 'OCT$', 'VAL', 'CONCAT', 'CMP'])
    if f == 'LEFT$' or f == 'RIGHT$':
        return f'{f}({string()},{small()})'
    if f == 'MID$':
        return f'MID$({string()},{small()})'
    if f == 'MID3':
        return f'MID$({string()},{small()},{small()})'
    if f == 'INSTR':
        return f'INSTR({string()},{string()})'
    if f == 'INSTR3':
        return f'INSTR({small()},{string()},{string()})'
    if f == 'STRING$':
        return f'STRING$({small()},{small()})'
    if f == 'STRINGS':
        return f'STRING$({small()},{string()})'
    if f == 'SPACE$':
        return f'"["+SPACE$({small()})+"]"'
    if f in ('ASC', 'LEN', 'VAL'):
        return f'{f}({string()})'
    if f in ('HEX$', 'OCT$'):
        return f'{f}({num()})'
    if f == 'CONCAT':
        return f'{string()}+{string()}'
    return f'{string()}{rnd.choice(["<", "=", ">", "<>"])}{string()}'


def conv_expr():
    f = rnd.choice(['CINT', 'FIX', 'INT', 'SGN', 'ABS', 'CSNG', 'CDBL', 'STR'])
    if f == 'STR':
        return f'STR$({num()})'
    if f == 'CDBL':
        # a single that is not a binary fraction differs between MBF and IEEE in its low digits
        return f'CDBL({rnd.choice(INTS + [0.5, 2.5, -1.5, 0.25, 3.75])})'
    return f'{f}({num()})'


def using_expr():
    fmt = rnd.choice(['"###"', '"#.##"', '"##.##"', '"+##.#"', '"##.#-"', '"**##"', '"$$##.##"',
                      '"**$#.##"', '"#,###"', '"##.##^^^^"', '"!"', '"\\  \\"', '"&"', '"#"',
                      '"###.#"', '"-#.#"', '"x#y"', '"_##"'])
    if fmt in ('"!"', '"\\  \\"', '"&"'):
        return f'PRINT USING {fmt};{string()}'
    vals = ';'.join(num() for _ in range(rnd.choice([1, 1, 2])))
    return f'PRINT USING {fmt};{vals}'


def print_list():
    items = [rnd.choice([num, string, small])() for _ in range(rnd.randint(2, 4))]
    seps = [rnd.choice([';', ',']) for _ in items]
    tail = rnd.choice(['', ';', ','])
    return 'PRINT ' + ''.join(i + s for i, s in zip(items, seps))[:-1] + tail + ':PRINT'


VALS = ['"1E"', '" 1 2"', '"&H"', '"&HFFFF"', '"&O17"', '"1D2"', '"-.5E1"', '"+3"', '"1,5"',
        '"3 E 2"', '"  "', '"..5"', '"1.2.3"', '"&H8000"', '"12AB"', '"%5"', '"1e-2"']


def misc_stmt():
    k = rnd.randrange(11)
    if k == 0:
        return f'PRINT VAL({rnd.choice(VALS)})'
    if k == 1:
        return f'PRINT "a";TAB({rnd.choice([0, 1, 5, 20, 79, 80, 81, 255, 256, -1])});"b"'
    if k == 2:
        return f'PRINT "a";SPC({rnd.choice([0, 1, 5, 79, 80, 81, 255, 256, -1])});"b"'
    if k == 3:
        return f'WRITE {num()},{string()},{num()}'
    if k == 4:
        return f'Z$="abcdef":MID$(Z$,{small()},{small()})={string()}:PRINT Z$'
    if k == 5:
        base, power = rnd.choice(INTS[:12]), rnd.choice([0, 1, 2, 3, -1, 0.5, 15, 16])
        if abs(base) >= 10 and power >= 15:
            return 'PRINT 3'    # 10^16 is 9.99999E+15 in MBF: deliberately not emulated
        return f'PRINT {base}^{power}'
    if k == 6:
        return f'PRINT {rnd.choice(INTS[:12])} MOD {rnd.choice([1, -3, 7, 0, -7, 2.5])};-{rnd.choice(INTS[:10])} MOD 3'
    if k == 7:
        return f'PRINT {num()},{num()},{string()},{num()}'
    if k == 8:
        return f'PRINT {rnd.choice(["INT", "FIX", "CINT", "SGN"])}({rnd.choice(["-2.5", "-0.5", "2.5", "32767.5", "-32768.5", "-32768.4", "1E10"])})'
    if k == 9:
        return f'PRINT {string()}{rnd.choice(["<", ">", "="])}{string()};{num()}{rnd.choice(["<", ">", "="])}{num()}'
    return f'PRINT {rnd.choice(["HEX$", "OCT$"])}({rnd.choice(["-1", "-32768", "65535", "65536", "-32769", "1.5", "0"])})'


DATA_ITEMS = ['1', '-2.5', '"a,b"', 'abc', ' x y ', '', '1E3', '&H10', '"q"', '.5', '1 2', '+7',
              '"', '3D2', '12%', 'A$', '-', '1e', '"a"b']
USING_FMTS = ['"##.##"', '"###,.##"', '"$$###.##"', '"**$##.##"', '"+###"', '"###-"', '"#.#^^^^"',
              '"##.##^^^^^"', '"$$-##"', '"!x!"', '"\\ \\"', '"&&"', '"#"', '"ab"', '"%"',
              '"##.##  ###"', '"_#"', '"#_#"', '"*##"', '"$##"', '"**#"', '"##,"', '".##"', '"+.##"']
USING_VALS = ['0', '1', '-1', '.5', '-.5', '12.345', '-12.345', '999.995', '1E6', '-1E6', '1E-3',
              '123456', '0.005', '99.995', '-0.004', '1E10', '32767']


def data_stmt():
    items = [rnd.choice(DATA_ITEMS) for _ in range(rnd.randint(1, 4))]
    reads = ','.join(rnd.choice(['R$', 'R', 'R%']) for _ in items)
    return 'RESTORE {line}:READ ' + reads + ':PRINT "[";R$;"]";R;R%', 'DATA ' + ','.join(items)


def using_stmt():
    fmt = rnd.choice(USING_FMTS)
    if any(c in fmt for c in '!\\&'):
        return f'PRINT USING {fmt};{string()};{string()}'
    vals = ';'.join(rnd.choice(USING_VALS) for _ in range(rnd.randint(1, 3)))
    return f'PRINT USING {fmt};{vals}' + rnd.choice(['', ';'])


ARGS_N = ['0', '1', '-1', '2.5', '255', '256', '-32768', '32767', '32768', '40000', '1E10', '-0.5', '"a"', '""']
ARGS_S = ['""', '"abc"', '"A"', '" 12"', '"&H41"', '1', '-1']
FUNCS = [('ABS', 'n'), ('ASC', 's'), ('ATN', 'n'), ('CDBL', 'n'), ('CHR$', 'n'), ('CINT', 'n'), ('COS', 'n'),
         ('CSNG', 'n'), ('CVI', 's'), ('CVS', 's'), ('CVD', 's'), ('EXP', 'n'), ('FIX', 'n'), ('HEX$', 'n'),
         ('INT', 'n'), ('LEN', 's'), ('LOG', 'n'), ('MKI$', 'n'), ('MKS$', 'n'), ('OCT$', 'n'),
         ('SGN', 'n'), ('SIN', 'n'), ('SPACE$', 'n'), ('SQR', 'n'), ('STR$', 'n'), ('TAN', 'n'), ('VAL', 's'),
         ('LEFT$', 'sn'), ('RIGHT$', 'sn'), ('MID$', 'sn'), ('MID$', 'snn'), ('STRING$', 'nn'), ('STRING$', 'ns'),
         ('INSTR', 'ss'), ('INSTR', 'nss'), ('SPC', 'n'), ('TAB', 'n'), ('POS', 'n'), ('FRE', 'n'), ('ABS', ''),
         ('LEFT$', 's'), ('MID$', 'snnn'), ('CHR$', 'nn'), ('INSTR', 's')]


def call_stmt():
    name, kinds = rnd.choice(FUNCS)
    args = [rnd.choice(ARGS_S if k == 's' else ARGS_N) if rnd.random() < 0.85
            else rnd.choice(ARGS_N if k == 's' else ARGS_S) for k in kinds]
    call = f'{name}({",".join(args)})' if kinds else f'{name}()'
    if name in ('SPC', 'TAB') and args and args[0] == '-32768':
        return 'PRINT 1'    # TAB(-32768) lands on column 47 on the binary, no rule found
    if name in ('SQR', 'TAN', 'SIN', 'COS', 'ATN', 'LOG', 'EXP') and args and args[0] not in ('0', '1', '-1', '"a"', '""', '2.5', '-0.5'):
        return 'PRINT 2'    # MBF maths differs in the last digits: deliberately not emulated
    if name in ('SPC', 'TAB'):
        return f'PRINT "<";{call};">"'
    if name in ('SIN', 'COS', 'TAN') and args and args[0] in ('-32768', '32767', '32768', '40000', '1E10'):
        args[0] = '2.5'     # MBF reduces a big argument with its own pi: deliberately not emulated
        call = f'{name}({",".join(args)})'
    if name in ('LOG', 'SQR', 'EXP', 'SIN', 'COS', 'TAN', 'ATN'):
        return f'PRINT INT({call}*1000)'   # whole thousandths: MBF and IEEE agree here
    if name in ('CVS', 'CVD', 'FRE'):
        return f'X={call}:PRINT "ok"'
    if name.startswith('MK'):
        return f'PRINT LEN({call})'
    return f'PRINT {call}'


ONK = ['0', '1', '2', '3', '-1', '256', '1.5', '2.5', '"a"', '255', '1E5']
FORV = ['1', '0', '-1', '2.5', '10', '-2.5', '32766', '32767', '-32768', '0.1', '1E10']
STEPS = ['1', '-1', '2', '0.5', '-0.5', '3', '-2', '32767', '1.5']


def flow_block(n):
    k = rnd.randrange(5)
    if k == 0:
        return [f'{n} PRINT "@{n}":ON {rnd.choice(ONK)} {rnd.choice(["GOTO", "GOSUB"])} {n + 1},{n + 2}:PRINT "f":GOTO {n + 4}',
                f'{n + 1} PRINT "a":GOTO {n + 4}', f'{n + 2} PRINT "b":GOTO {n + 4}', f'{n + 4} REM']
    if k == 1:
        var = rnd.choice(['I', 'I%', 'I#'])
        while True:
            a, b, st = rnd.choice(FORV), rnd.choice(FORV), rnd.choice(STEPS)
            trips = (float(b) - float(a)) / float(st)
            if var == 'I' and abs(float(a)) >= 2 ** 24 and trips >= 0:
                continue    # the step is lost in a single this big: the loop never ends
            if trips <= 2000:     # a loop the emulator ends soon
                break
        return [f'{n} PRINT "@{n}":C=0:FOR {var}={a} TO {b} STEP {st}:'
                f'C=C+1:IF C<12 THEN PRINT {var};', f'{n + 1} NEXT:PRINT "/";{var}']
    if k == 2:
        return [f'{n} PRINT "@{n}":W={rnd.choice(["3", "0", "-1", "2.5"])}:WHILE W{rnd.choice([">0", "", "<>0"])}:'
                f'PRINT W;:W=W-1:IF W<-3 THEN W=0', f'{n + 1} WEND:PRINT']
    if k == 3:
        return [f'{n} PRINT "@{n}":IF {rnd.choice(ONK[:6])} THEN GOSUB {n + 3}:PRINT "t" ELSE PRINT "e"',
                f'{n + 1} GOTO {n + 4}', f'{n + 3} PRINT "s":RETURN', f'{n + 4} REM']
    a, b = rnd.choice(STRS), rnd.choice(STRS)
    return [f'{n} PRINT "@{n}":IF {a}{rnd.choice(["<", ">", "=", "<=", "<>"])}{b} THEN PRINT "y" ELSE PRINT "n"']


def generate(seed: int, count: int = 150, mode: str = 'misc') -> str:
    """Return the source of a random program for seed, ending in SYSTEM."""
    global rnd
    rnd = random.Random(seed)
    lines = ['1 ON ERROR GOTO 30000']
    n = 10
    for _ in range(count):
        k = rnd.random()    # drawn in every mode, so a seed gives the same program as before
        if mode == 'flow':
            lines.extend(flow_block(n))
        elif mode == 'calls':
            lines.append(f'{n} PRINT "@{n}":{call_stmt()}')
        elif mode == 'data':
            if rnd.random() < 0.5:
                read, data = data_stmt()
                lines.append(f'{n} PRINT "@{n}":R$="":R=0:R%=0:' + read.format(line=n + 5))
                lines.append(f'{n + 5} {data}')
            else:
                lines.append(f'{n} PRINT "@{n}":{using_stmt()}')
        else:
            if k < 0.25:
                stmt = misc_stmt()
            elif k < 0.4:
                stmt = f'PRINT {int_expr()}'
            elif k < 0.6:
                stmt = f'PRINT {str_expr()}'
            elif k < 0.75:
                stmt = f'PRINT {conv_expr()}'
            elif k < 0.9:
                stmt = using_expr()
            else:
                stmt = print_list()
            lines.append(f'{n} PRINT "@{n}":{stmt}')
        n += 10
    lines.append(f'{n} SYSTEM')
    lines.append('30000 PRINT "E";ERR;ERL:RESUME NEXT')
    return '\n'.join(lines) + '\n'


def real_output(src: str) -> list:
    """Run src on real MBASIC; return the lines printed after RUN."""
    out = run_real(src + 'RUN\n', 120).split('\n')
    return [line for line in out[out.index('RUN') + 1:] if line != 'Ok']


def interp_output(bas: Path) -> list:
    try:
        p = subprocess.run([sys.executable, str(ROOT / 'mbasic'), str(bas), '--ui', 'cli'],
                           input=b'RUN\nSYSTEM\n', cwd=bas.parent, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return ['TIMEOUT']
    out = p.stdout.decode('utf-8', 'replace').replace('\r', '').split('\n')
    out = out[out.index('Ok') + 1:]
    # the CLI prints Goodbye on SYSTEM, right after the last output (documented)
    out = [line[:-len('Goodbye')] if line.endswith('Goodbye') and line != 'Goodbye' else line
           for line in out]
    return [line for line in out if line not in ('Ok', 'Goodbye')]


def js_output(bas: Path) -> list:
    jsf = bas.with_suffix('.js')
    c = subprocess.run([sys.executable, str(ROOT / 'mbasic'), str(bas), '--compile-js', str(jsf)],
                       capture_output=True, timeout=120)
    if c.returncode:
        return ['COMPILE FAILED: ' + (c.stdout + c.stderr).decode()[-300:]]
    try:
        p = subprocess.run(['node', str(jsf)], capture_output=True, timeout=120, input=b'')
    except subprocess.TimeoutExpired:
        return ['TIMEOUT']
    return (p.stdout + p.stderr).decode('utf-8', 'replace').replace('\r', '').split('\n')


def c_output(bas: Path):
    """Build bas with the C backend and run the .com; None when the backend refuses it."""
    c = subprocess.run([sys.executable, str(ROOT / 'mbasic'), str(bas), '--compile-c',
                        str(bas.with_suffix('.c'))],
                       capture_output=True, timeout=900, cwd=bas.parent)
    com = bas.with_suffix('.com')
    if c.returncode or not com.exists():
        return None
    try:
        p = subprocess.run(['cpmemu', str(com)], capture_output=True, timeout=300, input=b'',
                           cwd=bas.parent)
    except subprocess.TimeoutExpired:
        return ['TIMEOUT']
    return p.stdout.decode('latin-1').replace('\r', '').split('\n')


def printable(lines: list) -> list:
    """The cpmemu console strips bit 7 and drops what it cannot show: keep printable text only."""
    v = [''.join(chr(ord(c) & 0x7F) for c in line if 32 <= (ord(c) & 0x7F) < 127)
         for line in lines]
    while v and v[-1] == '':
        v.pop()
    return v


def report(seed, name: str, real: list, other: list) -> bool:
    """Print a diff when other differs from real; return True when it differs."""
    if other == real:
        return False
    print(f'--- seed {seed}: {name} differs')
    for d in list(difflib.unified_diff(real, other, 'real', name, lineterm='', n=0))[:40]:
        print(d)
    return True


def default_out() -> Path:
    return Path(tempfile.gettempdir()) / 'mbasic_fuzz'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('seeds', nargs='+', type=int)
    ap.add_argument('--count', type=int, default=150, help='statements per program')
    ap.add_argument('--mode', choices=MODES, default='misc')
    ap.add_argument('--js', action='store_true', help='also compare the JS backend')
    ap.add_argument('--c', action='store_true', help='also compare the C backend')
    ap.add_argument('--gen-only', action='store_true', help='write the programs, run nothing')
    ap.add_argument('--out', type=Path, default=default_out(), help='folder for the programs')
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    bad = 0
    for seed in args.seeds:
        src = generate(seed, args.count, args.mode)
        bas = args.out / f'fz_{seed}.bas'
        bas.write_text(src)
        if args.gen_only:
            print(bas)
            continue
        real = printable(real_output(src))
        others = [('interp', printable(interp_output(bas)))]
        if args.js:
            others.append(('js', printable(js_output(bas))))
        if args.c:
            cout = c_output(bas)
            if cout is None:
                print(f'--- seed {seed}: C backend refused the program')
            else:
                others.append(('c', printable(cout)))
        bad += sum(report(seed, name, real, o) for name, o in others)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
