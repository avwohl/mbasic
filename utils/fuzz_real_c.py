#!/usr/bin/env python3
"""Differential random test: real MBASIC 5.21 against the C backend.

    python3 utils/fuzz_real_c.py SEED [SEED ...] [--count N] [--mode MODE] [--out DIR]

The program from utils/fuzz_real.py, less its CDBL lines (a uc80 double is 32
bits), is c_SEED.bas.  It runs on real MBASIC and as a .com built by the C
backend under cpmemu.  When the C backend refuses it (most often a FOR whose
NEXT it cannot pair, which is an error the binary finds when it runs), the
program is run on the binary first to find the lines that give an error, and
the 10-line block of each such line is removed (a FOR and its NEXT, or an ON
GOTO and its targets, stay together).  Exit status 1 when the output differs.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fuzz_real import MODES, c_output, default_out, generate, printable, real_output, report  # noqa: E402


def without_doubles(src: str) -> str:
    """Remove the CDBL lines: a uc80 double is 32 bits, printed with 7 digits
    (docs/dev/UC80_BUGS_TODO.md)."""
    return '\n'.join(line for line in src.split('\n') if line and 'CDBL' not in line) + '\n'


def without_error_blocks(src: str) -> str:
    """Remove each 10-line block with a line that gives an error on the binary."""
    lines = [line for line in src.split('\n') if line]
    errs = {int(m.group(1)) for line in real_output(src)
            for m in [re.search(r'E \d+ +(\d+) *$', line)] if m}
    bad_blocks = {e // 10 for e in errs}
    keep = [line for line in lines if line.startswith(('1 ON ERROR', '30000 '))
            or int(line.split(' ')[0]) // 10 not in bad_blocks]
    return '\n'.join(keep) + '\n'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('seeds', nargs='+', type=int)
    ap.add_argument('--count', type=int, default=60,
                    help='statements per program (60 keeps a program with ON ERROR inside 64K)')
    ap.add_argument('--mode', choices=MODES, default='misc')
    ap.add_argument('--out', type=Path, default=default_out(), help='folder for the programs')
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    bad = 0
    for seed in args.seeds:
        src = without_doubles(generate(seed, args.count, args.mode))
        bas = args.out / f'c_{seed}.bas'
        bas.write_text(src)
        cout = c_output(bas)
        if cout is None:
            src = without_error_blocks(src)
            bas.write_text(src)
            cout = c_output(bas)
        if cout is None:
            print(f'--- seed {seed}: C backend refused {bas}')
            continue
        bad += report(seed, 'c', printable(real_output(src)), printable(cout))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
