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

A test that types at an INPUT$ prompt waits for the program to print a CHR$(6)
marker and then settles, except where it is deliberately testing type-ahead
(test_type_ahead_before_the_statement_is_honoured) or has no marker to wait for
(the CONT resume, which re-enters the INPUT$ without re-running line 10, and so
settles on the clock alone). Without that wait the keystroke arrives while the
terminal is still cooked and the line discipline gets it instead - most visibly
for Enter, which ICRNL rewrites to LF before INPUT$ switches to raw mode.

Needs a pty, so it is skipped where one cannot be allocated.
"""

import os
import pty
import select
import signal
import subprocess
import sys
import termios
import time

# Add project root to path (3 levels up from tests/regression/*/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))

# Printed by the test programs just before INPUT$, to synchronise on. A control
# byte, produced with CHR$(6), because the CLI echoes a typed-ahead program line
# twice - once by the line discipline, once by readline when it finally reads
# it - and a printable marker matches the echo of its own source line. With
# READY = b'RDY' the sync landed on `10 PRINT "RDY";` instead of on the running
# program, which flaked 2 runs in 13 under load. CHR$(6) cannot appear in the
# echo, because the source says the digit 6.
READY = b'\x06'

# The whole file must finish inside tests/run_regression.py's 30-second
# per-test timeout, whose TimeoutExpired arm discards the captured output. A
# FAILING run is the one at risk - every drain whose marker never appears waits
# out its full timeout - and a failing run that prints nothing is the one case
# where this file most needs to speak.
BUDGET_SECONDS = 20.0
_deadline = time.time() + BUDGET_SECONDS

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
    # Never wait past the file's overall budget - see BUDGET_SECONDS.
    deadline = min(time.time() + seconds, _deadline)
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


#: The common shape: announce, read one character, report its code. Note that
#: no line contains a 'Q', so an echo of the source can never be mistaken for
#: an echo of the 'Q' the echo test types.
ONE_KEY = ['10 PRINT CHR$(6);', '20 V$=INPUT$(1)', '30 PRINT "GOT";ASC(V$)']


def test_single_key_no_enter_no_echo():
    """One keystroke must satisfy INPUT$(1), unechoed."""
    print("\nINPUT$(1) returns on the keystroke and echoes nothing")
    print("-" * 60)
    with Session(ONE_KEY) as s:
        s.run()
        got = s.send(b'Q', until=b'GOT81')

    check(b'GOT81' in got,
          f"a single 'Q' completed INPUT$(1) with no Enter (got {got!r})")
    # A cooked terminal would echo a 'Q' of its own before GOT. 'Q' appears
    # nowhere in the program listing, so this cannot misfire on an echo of the
    # source arriving late.
    check(b'Q' not in got,
          f"the keystroke was not echoed (got {got!r})")


def test_multiple_characters_in_one_burst():
    """INPUT$(3) collects three characters without an Enter."""
    print("\nINPUT$(3) collects three characters")
    print("-" * 60)
    with Session(['10 PRINT CHR$(6);',
                  '20 V$=INPUT$(3)',
                  '30 PRINT "GOT";ASC(MID$(V$,1,1));ASC(MID$(V$,2,1));ASC(MID$(V$,3,1))']) as s:
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
        # CONT resumes *at* the INPUT$, so line 10's marker does not print
        # again and there is nothing to sync on but the clock. Without this
        # the 'K' goes in while the terminal is still cooked and the check
        # passes for the wrong reason - exercising type-ahead, which has its
        # own test, rather than the blocking raw read.
        time.sleep(RAW_MODE_SETTLE)
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


def test_ctrl_c_interrupts_a_multi_character_read():
    """One Ctrl+C must end an INPUT$(3) - not wait for two more keys.

    Checking the finished string instead of each byte made this worse than the
    cooked read it replaced: raw mode had already taken ISIG away, so nothing
    became a SIGINT either, and the program could not be interrupted at all
    until the user supplied the remaining n-1 characters, which the break then
    threw away.
    """
    print("\none Ctrl+C ends INPUT$(3) without further typing")
    print("-" * 60)
    with Session(['10 PRINT CHR$(6);',
                  '20 V$=INPUT$(3)',
                  '30 PRINT "GOT";LEN(V$)']) as s:
        s.run()
        broke = s.send(b'\x03', until=b'Break in 20')
        alive = s.send(b'PRINT "ALIVE"\r', until=b'ALIVE\r\n')

    check(b'Break in 20' in broke,
          f"a single Ctrl+C broke the three-character read (got {broke!r})")
    check(b'GOT' not in broke,
          f"and the program did not get a partial string (got {broke!r})")
    check(b'ALIVE' in alive,
          f"the REPL is responsive afterwards (got {alive!r})")


def test_break_keeps_type_ahead_typed_after_it():
    """A key typed after the Ctrl+C belongs to whatever reads next.

    The break aborts the read, so the characters before it are gone - but the
    ones after it were never part of this read and must stay queued. Reading
    the whole remainder in one os.read consumed them too, and the break then
    destroyed them.
    """
    print("\na key typed after the Ctrl+C is not consumed by the break")
    print("-" * 60)
    with Session(['10 PRINT CHR$(6);',
                  '20 V$=INPUT$(3)',
                  '30 PRINT "GOT";LEN(V$)']) as s:
        s.run()
        broke = s.send(b'A\x03B', until=b'Break in 20')
        # The queued 'B' is now type-ahead at the Ok prompt; Enter submits it,
        # and the REPL says what it made of it. Waiting for that reply rather
        # than for the first newline, which is only the echo of the Enter.
        after = s.send(b'\r', wait=3.0, until=b"'b'")

    check(b'Break in 20' in broke,
          f"the Ctrl+C broke mid-read (got {broke!r})")
    check(b'B' in after or b"'b'" in after,
          f"the 'B' typed after it survived for the next reader (got {after!r})")


def test_terminal_is_restored_if_the_process_is_killed():
    """SIGTERM while blocked in INPUT$ must not leave the tty raw.

    Raw mode is held for the whole blocking wait now, and the restoring
    tcsetattr lives in a finally that a signal never reaches - so `timeout 5
    python3 mbasic ...`, a CI kill or a closed window would have left the
    user's terminal with no echo and no Ctrl+C, needing `stty sane`.
    """
    print("\nkilling a program blocked in INPUT$ leaves the terminal usable")
    print("-" * 60)
    s = Session(ONE_KEY)
    try:
        s.run()
        blocked = termios.tcgetattr(s.fd)
        os.kill(s.pid, signal.SIGTERM)
        deadline = time.time() + 3.0
        while time.time() < deadline:
            try:
                if os.waitpid(s.pid, os.WNOHANG)[0]:
                    break
            except ChildProcessError:
                break
            time.sleep(0.05)
        restored = termios.tcgetattr(s.fd)
    finally:
        s.close()

    check(not blocked[3] & termios.ICANON,
          "the read really was in raw mode (control check)")
    check(bool(restored[3] & termios.ICANON) and bool(restored[3] & termios.ECHO),
          f"ICANON and ECHO are back after the kill (lflag {restored[3]:#x})")


def test_ctrl_c_in_immediate_mode():
    """The same break at the Ok prompt is a return to the prompt, not an error."""
    print("\nCtrl+C during an immediate-mode INPUT$")
    print("-" * 60)
    with Session() as s:
        os.write(s.fd, b'PRINT CHR$(6);:X$=INPUT$(1)\r')
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


def test_piped_control_c_breaks():
    """0x03 breaks whether it was typed or piped, as it does under cpmemu.

    Real 5.21 aborts an INPUT$ on a piped 0x03 exactly as it does on a typed
    one - piped input is the only console it has - and matching that was a
    deliberate call. What follows the 0x03 must still survive for the next
    reader, the same as on a terminal.
    """
    print("\na 0x03 byte in piped input breaks, like cpmemu")
    print("-" * 60)
    script = ('10 A$=INPUT$(1)\n'
              '20 PRINT "GOT";ASC(A$)\n'
              'RUN\n\x03\nPRINT "AFTER"\nSYSTEM\n')
    try:
        proc = subprocess.run(
            [sys.executable, 'mbasic', '--ui', 'cli'],
            input=script, capture_output=True, text=True,
            cwd=PROJECT_ROOT, timeout=20)
        out = proc.stdout
    except subprocess.TimeoutExpired:
        out = '<timed out>'

    check('Break in 10' in out, f"the run broke at the INPUT$ (got {out!r})")
    check('GOT' not in out,
          f"and the program did not receive CHR$(3) (got {out!r})")
    check('AFTER' in out,
          f"the rest of the piped input still reached the REPL (got {out!r})")


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
    test_ctrl_c_interrupts_a_multi_character_read()
    test_break_keeps_type_ahead_typed_after_it()
    test_terminal_is_restored_if_the_process_is_killed()
    test_ctrl_c_in_immediate_mode()
    test_piped_stdin_still_works()
    test_piped_control_c_breaks()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
