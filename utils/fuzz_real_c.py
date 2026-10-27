#!/usr/bin/env python3
"""Differential random test: real MBASIC 5.21 against the C backend.

    python3 utils/fuzz_real_c.py SEED [SEED ...] [--count N] [--mode MODE] [--out DIR]

The C backend has no ON ERROR and no PRINT USING, so the program from
utils/fuzz_real.py is first run on real MBASIC to find the lines that give an
error.  The 10-line block of each such line is removed (a FOR and its NEXT, or
an ON GOTO and its targets, stay together), and so are the error handler, the
PRINT USING lines and the CDBL lines (a uc80 double is 32 bits).  The rest,
c_SEED.bas, runs on real MBASIC and as a .com built by the C backend under
cpmemu.  Exit status 1 when the output differs.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fuzz_real import MODES, c_output, default_out, generate, printable, real_output, report  # noqa: E402


def c_safe(src: str) -> str:
    """Remove the error handler, PRINT USING, CDBL and each block with a line that errs on the binary."""
    lines = [line for line in src.split('\n') if line]
    first = real_output(src)
    errs = {int(m.group(1)) for line in first for m in [re.search(r'E \d+ +(\d+) *$', line)] if m}
    bad_blocks = {e // 10 for e in errs}
    keep = [line for line in lines if int(line.split(' ')[0]) // 10 not in bad_blocks
            and not line.startswith(('1 ON ERROR', '30000 ')) and 'USING' not in line
            # a uc80 double is 32 bits, printed with 7 digits (docs/dev/UC80_BUGS_TODO.md)
            and 'CDBL' not in line]
    return '\n'.join(keep) + '\n'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('seeds', nargs='+', type=int)
    ap.add_argument('--count', type=int, default=120, help='statements per program')
    ap.add_argument('--mode', choices=MODES, default='misc')
    ap.add_argument('--out', type=Path, default=default_out(), help='folder for the programs')
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    bad = 0
    for seed in args.seeds:
        src = c_safe(generate(seed, args.count, args.mode))
        bas = args.out / f'c_{seed}.bas'
        bas.write_text(src)
        cout = c_output(bas)
        if cout is None:
            print(f'--- seed {seed}: C backend refused {bas}')
            continue
        bad += report(seed, 'c', printable(real_output(src)), printable(cout))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
