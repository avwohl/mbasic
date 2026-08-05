#!/usr/bin/env python3
"""
Test that INPUT$(n) reads the keyboard the way MBASIC 5.21 does.

The keyboard path was the last stdin reader still on `sys.stdin.read(1)`, and
being cooked and buffered it was wrong four ways:

1. It waited for Enter. MBASIC returns the instant enough characters arrive -
   verified against the real 5.21 binary under cpmemu, where piping the two
   bytes "AB" with no newline satisfied two successive INPUT$(1) calls.
2. It echoed. MBASIC echoes nothing here, so a program that prints the key
   itself - `L$=INPUT$(1):PRINT X5$L$` in basic/games/hangman.bas - printed it
   twice.
3. The TextIOWrapper drained the whole kernel queue into a userspace buffer no
   other reader can see. Typing "AB" then Enter at INPUT$(1) gave the program
   "A" and stranded "B\\n" where neither the REPL nor the INPUT statement could
   reach it - and the *next* RUN's INPUT$ then picked it up as though freshly
   typed. Stale keystrokes crossed program runs.
4. Ctrl+C could neither reach the program nor stop it: ISIG turned it into a
   SIGINT, the break handler only set a flag, and PEP 475 restarted the blocked
   read. The break landed late and swallowed whatever key finally ended it.

Fixed with TCSANOW + os.read + latin-1, raw mode held for the whole read, and
an explicit Ctrl+C check. TCSANOW matters twice over: setraw()'s TCSAFLUSH
default would discard keys typed ahead of the statement, which worked before
and has to keep working.

Every test that types at an INPUT$ prompt waits for the program to print a
"RDY" marker first. Without that the keystroke can arrive while the terminal
is still cooked, and the line discipline gets it instead - most visibly for
Enter, which ICRNL rewrites to LF before INPUT$ ever switches to raw mode.

Needs a pty, so it is skipped where one cannot be allocated.
"""

import os
import pty
import select
import subprocess
import sys
import time

# Add project root to path (3 levels up from tests/regression/*/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))

# Printed by the test programs just before INPUT$, to synchronise on. No 'A' in
# it, so it cannot be mistaken for an echo of a typed 'A'.
READY = b'RDY'

# The marker is flushed a few hundred microseconds BEFORE INPUT$ reaches
# tty.setraw(), so a test that types the instant it sees RDY is racing the
# terminal mode: the keystroke lands in the cooked queue, gets echoed, and an
# Enter is rewritten to LF by ICRNL on the way in. A human cannot type inside
# that window; the tests should not either. (Keys typed genuinely early are a
# separate case with its own test - they survive, they just carry the cooked
# terminal's translations.)
RAW_MODE_SETTLE = 0.2

results = []


def check(condition, label):
    """Record one check; print pass/fail immediately."""
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}: {label}")


def drain(fd, seconds, until=None):
    """Read from the pty master until `until` appears, or it goes quiet.

    select() with a deadline rather than a bare os.read: the bugs under test
    are hangs, and a blocking read on the master would hang the test runner
    instead of reporting them. `until` is what keeps the whole file inside
    run_regression.py's 30-second budget - without it every step pays the full
    timeout, since a quiet interpreter is indistinguishable from a hung one
    until the deadline expires.
    """
    out = b''
    deadline = time.time() + seconds
    while True:
        if until is not None and until in out:
            break
        remaining = deadline - time.time()
        if remaining <= 0:
            break
        if not select.select([fd], [], [], remaining)[0]:
            break
        try:
            chunk = os.read(fd, 4096)
        except OSError:
            break               # child exited and the slave side closed
        if not chunk:
            break
        out += chunk
    return out


class Session:
    """An mbasic CLI running on a pty, driven one keystroke at a time."""

    def __init__(self, program=()):
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            try:
                os.chdir(PROJECT_ROOT)
                os.execv(sys.executable,
                         [sys.executable, 'mbasic', '--ui', 'cli'])
            finally:
                os._exit(1)
        drain(self.fd, 10.0, until=b'Ready')    # banner and the first prompt
        for line in program:
            self.type_line(line)

    def type_line(self, text):
        """Type a REPL line and wait for the terminal to echo it back."""
        os.write(self.fd, text.encode('latin-1') + b'\r')
        # The echo is the acknowledgement that the REPL has the line; waiting
        # for it keeps the next step's keystrokes from arriving early.
        return drain(self.fd, 5.0, until=text.encode('latin-1')[-4:] + b'\r\n')

    def run(self, until=READY, wait=8.0):
        """RUN, and wait until the program is at the INPUT$ in raw mode."""
        os.write(self.fd, b'RUN\r')
        out = drain(self.fd, wait, until=until)
        time.sleep(RAW_MODE_SETTLE)
        return out

    def send(self, data, wait=5.0, until=None):
        """Send raw bytes and return whatever comes back.

        Returns as soon as `until` appears; otherwise waits out `wait`, which
        is what a check for something that must NOT appear needs.
        """
        os.write(self.fd, data)
        return drain(self.fd, wait, until=until)

    def close(self):
        try:
            os.close(self.fd)
        except OSError:
            pass
        try:
            os.kill(self.pid, 9)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            os.waitpid(self.pid, 0)
        except (ChildProcessError, OSError):
            pass

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()
        return False


#: The common shape: announce, read one character, report its code.
ONE_KEY = ['10 PRINT "RDY";', '20 A$=INPUT$(1)', '30 PRINT "GOT";ASC(A$)']


def test_single_key_no_enter_no_echo():
    """One keystroke must satisfy INPUT$(1), unechoed."""
    print("\nINPUT$(1) returns on the keystroke and echoes nothing")
    print("-" * 60)
    with Session(ONE_KEY) as s:
        s.run()
        got = s.send(b'A', until=b'GOT65')

    check(b'GOT65' in got,
          f"a single 'A' completed INPUT$(1) with no Enter (got {got!r})")
    # A cooked terminal would echo an 'A' of its own before GOT.
    check(b'A' not in got,
          f"the keystroke was not echoed (got {got!r})")


def test_multiple_characters_in_one_burst():
    """INPUT$(3) collects three characters without an Enter."""
    print("\nINPUT$(3) collects three characters")
    print("-" * 60)
    with Session(['10 PRINT "RDY";',
                  '20 A$=INPUT$(3)',
                  '30 PRINT "GOT";ASC(MID$(A$,1,1));ASC(MID$(A$,2,1));ASC(MID$(A$,3,1))']) as s:
        s.run()
        got = s.send(b'ABC', until=b'GOT656667')
        after = s.send(b'PRINT "ZZZ"\r', until=b'ZZZ\r\n')

    check(b'GOT656667' in got,
          f"all three characters arrived in order (got {got!r})")
    check(b'ZZZ' in after,
          f"the REPL still works afterwards (got {after!r})")


def test_no_stale_keystroke_into_the_next_run():
    """Type-ahead beyond what INPUT$ asked for must not cross into a later RUN.

    This is the buffering bug proper. Before the fix: RUN #1 consumed the 'A'
    and hid "B\\n" in the TextIOWrapper, RUN #2 then printed GOT66 with nobody
    touching the keyboard, and RUN #3 printed GOT10 from the stranded newline.
    """
    print("\nleftover type-ahead does not leak into the next RUN")
    print("-" * 60)
    with Session(ONE_KEY) as s:
        s.run()
        first = s.send(b'AB\r', until=b'GOT65')
        s.send(b'PRINT "SYNC"\r', until=b'SYNC\r\n')
        s.run()
        untouched = s.send(b'', wait=0.8)       # nobody types anything here
        second = s.send(b'Q', until=b'GOT')

    check(b'GOT65' in first,
          f"RUN #1 got the 'A' that was typed (got {first!r})")
    check(b'GOT' not in untouched,
          f"RUN #2 read nothing until a key was typed (got {untouched!r})")
    check(b'GOT81' in second,
          f"RUN #2 received the 'Q' actually typed at it (got {second!r})")


def test_type_ahead_before_the_statement_is_honoured():
    """A key typed before INPUT$ runs must still be delivered.

    Guards TCSANOW: tty.setraw()'s TCSAFLUSH default discards input that has
    arrived but not been read, which would silently eat this.
    """
    print("\na key typed before INPUT$ runs is still delivered")
    print("-" * 60)
    with Session(['10 FOR I=1 TO 400:NEXT I',
                  '20 A$=INPUT$(1)',
                  '30 PRINT "GOT";ASC(A$)']) as s:
        # Deliberately no RDY sync: the 'Z' rides in with the RUN and has to
        # survive in the tty queue until line 20 gets there.
        got = s.send(b'RUN\rZ', wait=8.0, until=b'GOT90')

    check(b'GOT90' in got,
          f"the 'Z' typed during line 10 reached INPUT$ (got {got!r})")


def test_control_characters_pass_through():
    """Everything except Ctrl+C reaches the program, byte for byte."""
    print("\ncontrol characters and high bytes pass through")
    print("-" * 60)
    with Session(ONE_KEY) as s:
        s.run()
        ctrl_a = s.send(b'\x01', until=b'GOT1\r\n')
        s.run()
        enter = s.send(b'\r', until=b'GOT13\r\n')
        s.run()
        high = s.send(b'\x81', until=b'GOT129\r\n')

    check(b'GOT1\r\n' in ctrl_a, f"Ctrl+A arrives as CHR$(1) (got {ctrl_a!r})")
    check(b'^A' not in ctrl_a,
          f"and unechoed - a cooked terminal would show ^A (got {ctrl_a!r})")
    # Raw mode means no ICRNL: Enter is CR, which is what CP/M sends.
    check(b'GOT13' in enter, f"Enter arrives as CHR$(13) (got {enter!r})")
    check(b'GOT129' in high,
          f"a byte above 127 survives rather than being mangled (got {high!r})")


def test_ctrl_c_breaks_and_cont_resumes():
    """Ctrl+C interrupts INPUT$, as the 5.21 manual says, and CONT resumes.

    "all control characters are passed through except Control-C, which is used
    to interrupt the execution of the INPUT$ function." Raw mode clears ISIG,
    so the byte reaches the reader and this becomes the interpreter's decision
    to make; without it a program sitting in INPUT$ could not be interrupted
    from the keyboard at all.
    """
    print("\nCtrl+C breaks INPUT$, and CONT resumes it")
    print("-" * 60)
    with Session(ONE_KEY) as s:
        s.run()
        broke = s.send(b'\x03', until=b'Break in 20')
        s.send(b'CONT\r', until=b'CONT\r\n')
        resumed = s.send(b'K', until=b'GOT75')

    check(b'Break in 20' in broke,
          f"Ctrl+C reported a break at the INPUT$ line (got {broke!r})")
    # str(PC) is a debugging repr; MBASIC says "Break in 20".
    check(b'PC(' not in broke,
          f"the break names the line, not a PC repr (got {broke!r})")
    check(b'GOT3' not in broke,
          f"Ctrl+C was not handed to the program as CHR$(3) (got {broke!r})")
    check(b'^C' not in broke,
          f"raw mode meant the terminal did not echo it either (got {broke!r})")
    check(b'GOT75' in resumed,
          f"CONT re-entered the INPUT$ and it read the 'K' (got {resumed!r})")


def test_ctrl_c_in_immediate_mode():
    """The same break at the Ok prompt is a return to the prompt, not an error."""
    print("\nCtrl+C during an immediate-mode INPUT$")
    print("-" * 60)
    with Session() as s:
        os.write(s.fd, b'PRINT "RDY";:X$=INPUT$(1)\r')
        drain(s.fd, 5.0, until=READY)
        time.sleep(RAW_MODE_SETTLE)
        broke = s.send(b'\x03', until=b'Break\r\n')
        alive = s.send(b'PRINT "ALIVE"\r', until=b'ALIVE\r\n')

    check(b'Break\r\n' in broke, f"it reports a break (got {broke!r})")
    check(b'BreakException' not in broke,
          f"and not as an internal error (got {broke!r})")
    check(b'^C' not in broke,
          f"the read was raw, so the terminal did not echo ^C (got {broke!r})")
    check(b'ALIVE' in alive, f"the prompt still works afterwards (got {alive!r})")


def test_piped_stdin_still_works():
    """No terminal to put in raw mode: the cooked path must still deliver."""
    print("\npiped stdin still feeds INPUT$")
    print("-" * 60)
    script = ('10 A$=INPUT$(1)\n'
              '20 PRINT "GOT";ASC(A$)\n'
              '30 B$=INPUT$(2)\n'
              '40 PRINT "GOT2";ASC(LEFT$(B$,1));ASC(RIGHT$(B$,1))\n'
              'RUN\nABC\nSYSTEM\n')
    try:
        proc = subprocess.run(
            [sys.executable, 'mbasic', '--ui', 'cli'],
            input=script, capture_output=True, text=True,
            cwd=PROJECT_ROOT, timeout=20)
        out = proc.stdout
    except subprocess.TimeoutExpired:
        out = '<timed out>'

    check('GOT65' in out, f"the first character arrived (got {out!r})")
    check('GOT26667' in out,
          f"the next two arrived from the same line (got {out!r})")


if __name__ == "__main__":
    print("INPUT$ keyboard reading on POSIX")
    print("=" * 60)

    try:
        pid, fd = pty.fork()
        if pid == 0:
            os._exit(0)
        os.close(fd)
        os.waitpid(pid, 0)
    except OSError as exc:
        print(f"SKIP: cannot allocate a pty here ({exc})")
        sys.exit(2)

    test_single_key_no_enter_no_echo()
    test_multiple_characters_in_one_burst()
    test_no_stale_keystroke_into_the_next_run()
    test_type_ahead_before_the_statement_is_honoured()
    test_control_characters_pass_through()
    test_ctrl_c_breaks_and_cont_resumes()
    test_ctrl_c_in_immediate_mode()
    test_piped_stdin_still_works()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
