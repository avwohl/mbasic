#!/usr/bin/env python3
"""Run real MBASIC 5.21 under cpmemu with typed input, keeping stdin open.

    python3 utils/run_real_mbasic.py [TIMEOUT] < input

cpmemu ends a running program when its input reaches end of file (MBASIC polls
the console for ^C while a program runs), so a long program needs stdin to stay
open until the program ends with SYSTEM.  This script writes the input, keeps
the pipe open, waits up to TIMEOUT seconds (default 60) and prints MBASIC's
output.  See tests/HOW_TO_RUN_REAL_MBASIC.md.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_real(text: str, timeout: float = 60) -> str:
    """Type text into real MBASIC and return what it printed (CRs removed)."""
    with tempfile.TemporaryFile() as out:
        p = subprocess.Popen(['cpmemu', '../com/mbasic'], stdin=subprocess.PIPE, stdout=out,
                             stderr=subprocess.DEVNULL, cwd=ROOT / 'tests')
        p.stdin.write(text.encode('latin-1'))
        p.stdin.flush()
        try:
            p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()
        out.seek(0)
        return out.read().decode('latin-1').replace('\r', '')


def main() -> None:
    limit = float(sys.argv[1]) if len(sys.argv) > 1 else 60
    sys.stdout.write(run_real(sys.stdin.buffer.read().decode('latin-1'), limit))


if __name__ == '__main__':
    main()
