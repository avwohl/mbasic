"""RENUM after RUN in the CLI prints nothing (no spurious Illegal function call)."""
import os
import subprocess
import sys

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
inp = '10 PRINT "A"\nRUN\nRENUM 5\nLIST\nSYSTEM\n'
out = subprocess.run([sys.executable, 'mbasic', '--ui', 'cli'], input=inp,
                     capture_output=True, text=True, cwd=root, timeout=60).stdout
if 'Illegal function call' in out or '5 PRINT "A"' not in out:
    print(out)
    sys.exit(1)
print('ok')
