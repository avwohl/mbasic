# Undoing a statement that has to be run again

**Created:** 2026-08-05
**Status:** Fixed - `src/statement_attempt.py` (new), `src/interpreter.py`,
`src/basic_builtins.py`, `src/runtime.py`
**Regression test:** `tests/regression/interpreter/test_statement_attempt.py`

A statement that pauses for a key is re-executed from the start
([WEB_PROGRAM_KEYBOARD.md](WEB_PROGRAM_KEYBOARD.md)), so whatever the abandoned
attempt already did happens twice. This is the rest of that story: what a
second attempt repeats, and what is now put back first.

## What actually repeats

Measured rather than assumed, and the first version of this list - written into
WEB_PROGRAM_KEYBOARD.md before anything was measured - was wrong on its
headline claim:

	PRINT "A";INPUT$(1)      A is printed ONCE, not once per attempt
	X$=INPUT$(1)+INPUT$(1)   a key eaten per attempt - never completed
	X$=STR$(RND)+INPUT$(1)   a random number drawn per attempt
	X$=INPUT$(1,1)+INPUT$(1) a file byte read per attempt

Output does not duplicate because `execute_print` evaluates its expressions
into a list and writes at the end - an attempt that pauses mid-expression has
written nothing. The other three are real, and the first of them was the worst:
the program ate every key it was given and never reached the next line.

Keys were fixed by `KeyReadTransaction` (see WEB_PROGRAM_KEYBOARD.md). The
other two are what this document is about.

## RND

	10 X$=STR$(RND)+INPUT$(1)

Pausing three times drew four random numbers and used the last. The value the
program got was fine; the *sequence* was not, and a sequence is the only thing
a random number generator is for. A program that waited for the user skipped
forward by however many times it happened to pause - which is neither
reproducible nor visible.

`StatementAttempt.note_random` snapshots `random.getstate()` and
`runtime.rnd_last` before the first draw of an attempt, and a rollback restores
both. Once per attempt, not once per draw: the state to go back to is the one
the attempt started from, however many numbers it drew.

## INPUT$ from a file

	10 X$=INPUT$(1,1)+INPUT$(1)

The file read succeeded and advanced the handle; the keyboard read paused; the
retry read the *next* byte and paired it with the key. The file was left one
byte further on than the program had ever seen, so its next read was short.

`note_file_position` records `tell()` the first time each file is read in an
attempt, and a rollback seeks back. Per file, because one statement can read
two.

## What is deliberately not undone

`EOF` sets `file_info['eof']` when it reaches the end of a file. Setting it
twice is the same as setting it once, and a BASIC program cannot tell the
difference.

Variable assignment happens after the expression is evaluated, so a statement
that pauses has not assigned anything. `INPUT`, `GET`, `PUT` and `POKE` are
statements of their own - a statement that pauses for a key contains a keyboard
read, and those do not.

## The cost, and who pays it

Nothing, unless the I/O handler can pause a statement:

	deferring = getattr(self.io, 'defers_key_reads', False)
	if deferring:
	    self.io.begin_key_transaction()
	    ...
	    self.runtime.statement_attempt = self._statement_attempt

Only the web backend sets that flag. On a terminal the attribute lookup is the
whole cost, and `runtime.statement_attempt` stays `None`, so `RND` and the file
read skip their recording with one `getattr` each. Measured: 180,000
statements run in the same 7-8 seconds before and after, with the difference
well inside the run-to-run variance of this machine.

The attempt object is built once per interpreter and reset per statement rather
than allocated each time.

## A bug found on the way

`INPUT$(n,#f)` returned a *bytes* object. Mode `I` files are opened `'rb'` so
`EOF` can spot a CP/M `^Z`, and the read was handed to the program unchanged:

	PRINT INPUT$(3,#1)              b'ABC'
	PRINT ASC(INPUT$(1,#1))         98      <- the 'b' of the repr

98 is `ASC("b")`. The help page's own example for `INPUT$` is
`PRINT HEX$(ASC(INPUT$(1, #1)));`, so the documented use of the function was
broken. It decodes `latin-1` now - byte-transparent, the same as every other
read in this family - and answers 65.

## Verifying

	python3 tests/regression/interpreter/test_statement_attempt.py

14 checks. Four drive `StatementAttempt` directly (the generator snapshotted
once per attempt and not per draw, `RND(0)`'s value restored, file positions
rewound, a committed attempt not undone by the next one). Four run real
programs through the interpreter with a handler that pauses: the same random
number whether it paused three times or none, a file read that is not repeated,
the bytes fix, and a control showing a non-deferring handler never gets an
attempt at all - a regression that switched this on everywhere would otherwise
be invisible.
