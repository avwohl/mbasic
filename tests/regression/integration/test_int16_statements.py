"""Statement-level FRCINT/CONINT checks (issues 42 and 43), measured on MBASIC 5.21.

ERROR n, the MID$ statement, FIELD widths, GET/PUT record numbers, OPEN ... LEN and
the double-to-single step in FRCINT. Each program was run on real MBASIC 5.21
(cpmemu, tests/HOW_TO_RUN_REAL_MBASIC.md); the expected text is what the binary printed.
Error 5 is Illegal function call, 6 is Overflow, 63 is Bad record number.
"""
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: int16 statement tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ROOT = Path(__file__).resolve().parents[3]

HANDLER = '100 PRINT "E";ERR;" ";: RESUME NEXT'

# (statement, output on real MBASIC 5.21); the statement runs under ON ERROR
CASES = [
    ('ERROR 0', 'E 5'),
    ('ERROR 256', 'E 5'),
    ('ERROR 40000', 'E 6'),
    ('ERROR -1', 'E 5'),
    ('ERROR 5.6', 'E 6'),
    ('ERROR 255', 'E 255'),
    ('ERROR 24.5', 'E 25'),
    ('A$="ABC":MID$(A$,1,1.5)="XYZ":PRINT A$', 'XYC'),
    ('A$="ABC":MID$(A$,1,-1)="XYZ":PRINT A$', 'E 5  ABC'),
    ('A$="ABC":MID$(A$,0,1)="X":PRINT A$', 'E 5  ABC'),
    ('A$="ABC":MID$(A$,2,300)="X":PRINT A$', 'E 5  ABC'),
    ('A$="ABC":MID$(A$,40000,1)="X":PRINT A$', 'E 6  ABC'),
    ('A$="ABC":MID$(A$,1,40000)="X":PRINT A$', 'E 6  ABC'),
    ('OPEN "R",#1,"zz2.dat",128:CLOSE:PRINT "ok"', 'ok'),
    ('OPEN "R",#1,"zz2.dat",129', 'E 5'),
    ('OPEN "R",#1,"zz2.dat",300', 'E 5'),
    ('OPEN "R",#1,"zz2.dat",40000', 'E 6'),
    ('OPEN "R",#1,"zz2.dat",-1', 'E 5'),
    ('OPEN "R",#1,"zz2.dat",-0.4:CLOSE:PRINT "ok"', 'ok'),
    ('OPEN "R",#1,"zz2.dat",128:FIELD #1,300 AS B$', 'E 5'),
    ('OPEN "R",#1,"zz2.dat",128:FIELD #1,40000 AS B$', 'E 6'),
    ('OPEN "R",#1,"zz2.dat",128:FIELD #1,10 AS B$:GET #1,40000', 'E 6'),
    ('OPEN "R",#1,"zz2.dat",128:FIELD #1,10 AS B$:GET #1,70000', 'E 6'),
    ('OPEN "R",#1,"zz2.dat",128:FIELD #1,10 AS B$:LSET B$="X":PUT #1,40000', 'E 6'),
    ('OPEN "R",#1,"zz2.dat",128:FIELD #1,10 AS B$:GET #1,0', 'E 63'),
    ('OPEN "R",#1,"zz2.dat",128:FIELD #1,10 AS B$:LSET B$="X":PUT #1,0', 'E 63'),
    ('PRINT 2.49999999# AND 3', ' 3'),
    ('PRINT 32767.49999# OR 0', 'E 6'),
    ('PRINT CINT(2.4999999#)', ' 3'),
]


def run_case(tmp_path, statement):
    lines = ["10 ON ERROR GOTO 100", "20 " + statement, "30 CLOSE", "40 SYSTEM", HANDLER]
    (tmp_path / "case.bas").write_text("\n".join(lines) + "\n")
    result = subprocess.run(
        [sys.executable, str(ROOT / "mbasic"), str(tmp_path / "case.bas"), "--ui", "cli"],
        input="RUN\nSYSTEM\n", cwd=tmp_path, capture_output=True, text=True, timeout=60)
    text = result.stdout.replace("\r", "").split("Ready\n", 1)[-1].split("Goodbye")[0]
    return text.strip("\n").strip()


@pytest.mark.parametrize("statement,expected", CASES)
def test_statement_matches_real_mbasic(tmp_path, statement, expected):
    assert run_case(tmp_path, statement) == expected.strip()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
