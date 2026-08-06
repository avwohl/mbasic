#!/usr/bin/env python3
"""Cross-check basic/dev/tests_with_results/ against the real MBASIC 5.21 binary.

The .txt files beside each test are its expected output. They are only worth
anything if they came from the binary rather than from us - captured from our
own output they pin whatever we happened to print that day, and a formatting
bug gets frozen in as the answer. This runs each program both ways and reports
whether the two agree.

    python3 utils/crosscheck_tests.py                 # all tests
    python3 utils/crosscheck_tests.py test_for_next   # just these
    python3 utils/crosscheck_tests.py --write         # rewrite the .txt files

Each test comes back as one of:

    MATCH   the real binary and we produce the same thing, character for
            character. The .txt file is a genuine cross-check.
    DIFF    they disagree. Either we have a bug or the program uses something
            5.21 has not got - the diff is printed so you can tell which.
            docs/dev/TESTS_VERIFIED_AGAINST_BINARY.md lists the ones known to
            differ, and why.
    NORUN   the transcript could not be parsed, which usually means the program
            stopped somewhere unexpected while being typed in.

--write rewrites every .txt from our output. Only do that having read the DIFF
list: for a MATCH it makes no difference which side it is taken from, but for a
DIFF it pins our behaviour, and that is exactly the thing worth being
deliberate about.

Needs cpmemu (preferred) on PATH - see docs/dev/TOOLCHAIN_POLICY.md - and
com/mbasic.com in the repo. The procedure for driving the binary is
tests/HOW_TO_RUN_REAL_MBASIC.md; the one thing this does differently is to run
it in a scratch directory, because the file tests create files in the CP/M
working directory and a program that stops early leaves them behind.
"""

import difflib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TESTDIR = REPO / 'basic/dev/tests_with_results'
BINARY = REPO / 'com/mbasic.com'

BANNER = [
    'BASIC-80 Rev. 5.21',
    '[CP/M Version]',
    'Copyright 1977-1981 (C) by Microsoft',
    'Created: 28-Jul-81',
]

#: Lines our CLI prints around a program that are not the program's output.
CHROME_PREFIXES = ('MBASIC-', '100%', '(Tip:', 'Type HELP')
CHROME_EXACT = ('Ready', 'Goodbye')


def run_real(bas: Path, sandbox: Path):
    """Run bas under the real binary. Returns (output_lines, transcript).

    output_lines is None if the transcript did not have the shape expected.
    """
    source = bas.read_text()
    feed = source if source.endswith('\n') else source + '\n'
    feed += 'RUN\nSYSTEM\nSYSTEM\nSYSTEM\n'

    for stray in sandbox.iterdir():
        if stray.name != 'mbasic.com':
            stray.unlink()

    try:
        done = subprocess.run(['cpmemu', 'mbasic'], input=feed, capture_output=True,
                              text=True, timeout=30, cwd=str(sandbox))
    except subprocess.TimeoutExpired as expired:
        out = expired.stdout or ''
        if isinstance(out, bytes):
            out = out.decode('utf-8', 'replace')
        return None, '<<TIMEOUT>>\n' + out
    except FileNotFoundError:
        sys.exit('cpmemu not found on PATH - see docs/dev/TOOLCHAIN_POLICY.md')

    raw = done.stdout.replace('\r\n', '\n').replace('\r', '\n')
    lines = raw.split('\n')

    index = 0
    while index < len(lines) and lines[index].strip() == '':
        index += 1
    for expected in BANNER:
        if index < len(lines) and lines[index] == expected:
            index += 1
    if index < len(lines) and lines[index].endswith('Bytes free'):
        index += 1
    if index < len(lines) and lines[index] == 'Ok':
        index += 1

    # Skip the echo of the program as it is typed in. MBASIC echoes through its
    # own console driver, which breaks the line at the WIDTH column, so one
    # source line can come back as several - join until it matches.
    source_lines = source.split('\n')
    if source_lines and source_lines[-1] == '':
        source_lines.pop()
    for wanted in source_lines:
        wanted = wanted.replace('\x1a', '')     # CP/M end-of-file padding
        joined = ''
        while index < len(lines):
            joined += lines[index]
            index += 1
            if joined == wanted:
                break
            if not wanted.startswith(joined):
                return None, raw
        else:
            return None, raw

    if index < len(lines) and lines[index] == 'RUN':
        index += 1
    else:
        return None, raw

    out = lines[index:]
    while out and out[-1].strip() == '':
        out.pop()
    while out and out[-1] in ('SYSTEM', 'Ok'):
        out.pop()
    return out, raw


def run_ours(bas: Path):
    done = subprocess.run(['python3', 'mbasic', '--ui', 'cli', str(bas)],
                          input='RUN\nSYSTEM\n', capture_output=True, text=True,
                          timeout=120, cwd=str(REPO))
    keep = [line for line in done.stdout.split('\n')
            if not line.startswith(CHROME_PREFIXES) and line not in CHROME_EXACT]
    while keep and keep[-1].strip() == '':
        keep.pop()
    return keep


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    write = '--write' in sys.argv[1:]

    if not BINARY.exists():
        sys.exit(f'{BINARY} not found')

    names = args or sorted(t.stem for t in TESTDIR.glob('*.bas'))
    counts = {'MATCH': [], 'DIFF': [], 'NORUN': []}

    with tempfile.TemporaryDirectory(prefix='mbasic-crosscheck-') as tmp:
        sandbox = Path(tmp)
        shutil.copy(BINARY, sandbox / 'mbasic.com')

        for name in names:
            bas = TESTDIR / f'{name}.bas'
            if not bas.exists():
                sys.exit(f'no such test: {name}')

            real, _ = run_real(bas, sandbox)
            ours = run_ours(bas)

            if real is None:
                state = 'NORUN'
            elif real == ours:
                state = 'MATCH'
            else:
                state = 'DIFF'
            counts[state].append(name)
            print(f'{name:32s} {state}')

            if state == 'DIFF':
                for line in difflib.unified_diff(real, ours, 'real 5.21', 'ours',
                                                 lineterm='', n=1):
                    print('   ' + line)

            if write:
                (TESTDIR / f'{name}.txt').write_text('\n'.join(ours) + '\n')

    print('\n' + '=' * 60)
    for state in ('MATCH', 'DIFF', 'NORUN'):
        print(f'{state}: {len(counts[state])}')
        if state != 'MATCH':
            for name in counts[state]:
                print(f'    {name}')
    if write:
        print(f'\nrewrote {len(names)} expected-output files')

    return 1 if counts['NORUN'] else 0


if __name__ == '__main__':
    sys.exit(main())
