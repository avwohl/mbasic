# Making startrek.bas run, and the two interpreter bugs it was hiding

**Created:** 2026-08-05
**Status:** Fixed - `basic/games/startrek.bas`, `basic/games/STINSTR.TXT` (new),
`src/interpreter.py`, `src/runtime.py`
**Regression test:** `tests/regression/interpreter/test_gosub_in_then.py`

`basic/games/startrek.bas` would not run. Getting it to run took four changes to
the program and two to the interpreter, and the interpreter ones matter far more
than the game does: between them they were silently breaking 35 of the shipped
programs.

## The program was GW-BASIC, not MBASIC

Checked against the 5.21 reference manual (recoverable at
`git show cfa65e76^:doc/external/basic_ref.txt`) and against the real binary
under cpmemu:

- **`CLS`** (lines 5, 162, 280) appears nowhere in the manual, and the real
  binary answers `Syntax error`. It arrived with IBM BASICA/GW-BASIC. A CP/M
  console is a serial terminal, so clearing it means sending whatever that
  terminal wants - which is why the language has no statement for it. Replaced
  with `PRINT CHR$(26);`, the CP/M screen clear that `basic/games/spacewar.bas`
  already uses. cpmemu renders it as `ESC[2J ESC[H`.
- **`OPEN "STINSTR.TXT" FOR INPUT AS #1`** (line 30) is the GW-BASIC form.
  5.21 is `OPEN <mode>,[#]<file number>,<filename>` (manual §3), so it becomes
  `OPEN "I", #1, "STINSTR.TXT"`.
- **`TIMER`** (line 165) is not in the manual either - the only occurrence of
  the word is a filename in a `CSAVE` example. The program already asks the
  user for a random number, which is what now seeds `RANDOMIZE`.
- **The instructions file did not exist.** Opening a missing file is
  `File not found` on the real binary too, so line 30 is guarded with
  `ON ERROR GOTO 1540` and resumes at 90 - the game runs from any directory.
  `STINSTR.TXT` is now shipped alongside, written from what the program itself
  does: its six commands, the course dial, the display symbols, docking.

`CLEAR 1000` was left alone. The manual's syntax summary suggests a leading
comma, but the real binary accepts `CLEAR 1000` and rejects `CLEAR ,1000` with
`Out of memory` - the comma form is the memory-size variant.

The fixed program runs on real MBASIC 5.21 under cpmemu, which is the strongest
check available that the dialect is right.

## Bug 1: a GOSUB inside THEN dropped the rest of the clause

	30 IF I > 0 THEN GOSUB 100: PRINT "NEVER PRINTED"

Real 5.21 prints it. This interpreter did not.

A THEN clause is not addressable by PC - the statement table holds one entry for
the whole `IF`, and the clause's statements hang off it in a list - so a `GOSUB`
inside one had nowhere to point its return address except the statement *after*
the `IF`. `execute_if` then broke out of its loop the moment `npc` was set, and
everything after the `GOSUB` was gone.

startrek fills its quadrant entirely in that shape:

	350 FOR I = 0 TO 7: K3(I) = 0: X = 8: IF I < K THEN GOSUB 540: S(X,Y) = 3: K3(I) = S9
	370 IF B > 0 THEN GOSUB 540: S(X, Y) = 4
	380 IF I > 0 THEN GOSUB 540: S(X, Y) = 5: I = I - 1: GOTO 380

`GOSUB 540` picks an empty sector into `X,Y`, and the statements that *use* it
never ran. The map came up as nothing but dots and the Enterprise while the
status panel said `CONDITION: RED` and `KLINGONS LEFT = 21`.

The fix gives the clause tail to the GOSUB frame:
`execute_clause_statements()` hands the remaining statements to
`runtime.set_gosub_continuation()`, and `RETURN` runs them before the return
address takes effect - so a `GOTO` at the end of the clause still wins, which is
what makes line 380's loop terminate.

Two details that cost a debugging round each:

- A `GOSUB` *inside* a continuation computes its return address from wherever
  the interpreter is standing, which by then is the subroutine that just
  returned. `set_gosub_return()` corrects it to where the clause was going to
  end up. Without this, `THEN GOSUB 100: GOSUB 200: PRINT` returns into the
  middle of subroutine 200 and eventually dies with `RETURN without GOSUB`.
- Only a `GOSUB` gets a continuation. Any other jump out of a clause - `GOTO`,
  `THEN <line>` - is a departure, and what follows it is unreachable, which is
  what MBASIC does too.

**This affects 180 lines across 35 of the shipped programs**, not just
startrek - `asm2mac.bas:530` is
`IF OPC$="LDAX" THEN OPC$="LD":GOSUB 1630:OPD$="A,("+OPD$+")"`, where the
assignment that produces the output was being dropped.

## Bug 2: NEXT with no variable

	580 FOR I = 0 TO 7: IF K3(I) <= 0 THEN 605
	...
	605 NEXT: RETURN

`_find_most_recent_for_variable()` scanned *backwards through the source* for a
`FOR`, and called `statement_table.get_statement()` - a method that has never
existed - so the first bare `NEXT` reached this way died with `AttributeError`,
and after that was fixed, with `NEXT without FOR`: the scan starts from the
`NEXT` and line 580 jumps *forward* over its own body to get there.

Which `FOR` a bare `NEXT` belongs to is a question about what is running, not
about the text. `runtime.for_loop_states` is keyed by variable and, being a
dict, preserves the order the loops were entered - so the innermost active loop
is simply the last one still in it.

## Verifying

	python3 tests/regression/interpreter/test_gosub_in_then.py

10 checks: statements after a GOSUB in THEN and in ELSE, a false condition
running none of the clause, the `THEN GOSUB: ...: GOTO self` loop, nested
GOSUBs from clauses, two GOSUBs in one clause, a bare NEXT reached by a jump,
nested bare NEXTs, and startrek itself drawing a quadrant that contains
something. Each behavior was compared against real MBASIC 5.21 under cpmemu
before being written down.

## Known limitation, unrelated but visible here

The game prints `ENERGY = 3934.027898842015`. Real 5.21 stores that as single
precision and would print `3934.03`. This implementation prints Python's full
double-precision repr for computed values, which is a general numeric-formatting
gap rather than anything to do with startrek - but this is a good place to see
it.
