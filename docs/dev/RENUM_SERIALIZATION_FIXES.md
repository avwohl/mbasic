# RENUM could not rewrite most programs, and corrupted the arithmetic in the rest

**Created:** 2026-08-05
**Status:** Fixed - `src/ui/ui_helpers.py`
**Regression test:** `tests/regression/serializer/test_position_serializer.py`

Found while clearing the seven long-standing failures in
`tests/run_regression.py`. The serializer test was reporting

	✅ Unchanged: 3
	⚠️  Changed:   70
	❌ Errors:    462
	📊 Total:     535
	❌ FAIL: Only 13.6% success rate

which is not a stale expectation - it is 462 of 535 shipped programs failing to
round-trip. `serialize_statement()` is what RENUM uses to write a program back
out after renumbering, so RENUM refused to run on any program containing a
statement it did not know.

## What was missing

Seventeen statement types were handled. Forty were not, and the list is not
exotic:

	INPUT  DIM  READ  DATA  RESTORE  CLEAR  DEFINT/DEFSNG/DEFDBL/DEFSTR
	DEF FN  OPEN  CLOSE  FIELD  GET  PUT  LSET  RSET  LINE INPUT  PRINT USING
	LPRINT  WIDTH  RANDOMIZE  SWAP  ERASE  MID$=  POKE  OUT  WAIT  OPTION BASE
	RESUME  TRON  TROFF  SYSTEM  RUN  SAVE  LOAD  MERGE  CHAIN  KILL  NAME
	FILES  RESET  WRITE  CALL  COMMON  NEW  CONT

`INPUT` alone accounted for 94 of the failures and `DIM` for 87. The error was
at least explicit rather than silent - "Unhandled statement type ... cannot
serialize during RENUM", raised deliberately so a half-written program is never
saved - but the effect was that RENUM did not work on real code.

All forty are implemented now, and no `.bas` file in the repo fails for that
reason.

## The import that broke another 75

	from tokens import TokenType

in `token_to_operator()`. The flat name only resolves when `src/` happens to be
on `sys.path`, which is true when `mbasic` launches a UI and false for anything
importing `src.*` directly - so serializing any expression containing an
operator raised `ModuleNotFoundError: No module named 'tokens'`. It is
`src.tokens` now.

## The parentheses

This is the one that mattered most, and it was not what the test was measuring.

The AST does not record parentheses - the parser builds the tree they imply -
so a serializer has to put them back wherever precedence would otherwise say
something different. It did not:

	10 Y=(12*Y0+M)/12     RENUM ->    10 Y = 12 * Y0 + M / 12

Different arithmetic, written silently into the user's program by a documented
command. `_serialize_operand()` now brackets a sub-expression whose operator
binds more loosely than its parent, and at equal precedence brackets the side
that associativity would otherwise change:

	A-(B-C)     keeps its brackets      (A-B)-C     does not need them
	A/(B/C)     keeps its brackets      (A/B)/C     does not need them
	(S^T)^U     keeps its brackets      S^(T^U)     does not need them

`^` is the odd one: `parse_power()` recurses on the right and `2^3^2` evaluates
to 512, so it is right-associative, and at equal precedence it is the LEFT
operand that has to keep its brackets - the opposite of every other operator
here. Twelve cases are pinned in the test.

## What the test now measures

	bas_files = [f for f in all_bas_files if 'bad_syntax' not in f.parts]

`basic/dev/bad_syntax/` holds programs that are deliberately broken so the
parser's error handling has something to chew on (CLAUDE.md: "basic/ (working),
basic/bad_syntax/ (broken)"). Counting the parser's correct refusal of them as a
serializer failure made the number meaningless - 222 of the 229 remaining
errors were files that are *supposed* to fail. They are excluded and reported
separately, and the pass bar went from 50% to 95%, which is a bar that now
means something:

	✅ Unchanged: 3
	⚠️  Changed:   301
	❌ Errors:    7
	📊 Total:     311
	97.7%

"Changed" is expected: the serializer normalises spacing, which the test has
always documented.

## The seven that remain

Five are in `basic/incompatible/`, which is what that directory is for. The
other two are worth naming:

- `basic/games/startrek.bas` uses `CLS`, which this parser does not have.
  `CLS` is GW-BASIC/BASICA, not MBASIC 5.21 - so the parser is arguably right
  and the program is the odd one out - but `IOHandler.clear_screen()` is
  documented as "the CLS statement", so the intent is contradictory. Left
  alone: adding a statement to the language is a fidelity decision, not a
  serializer fix.
- `basic/dev/bas_tests/hanoi.bas` line 960 is `FOR 1  TO 100 ... NEXT J` - a
  `FOR` with no loop variable. The program is corrupt; the parser is right to
  refuse it.

## Known limitations

**Serializing is not idempotent for leading whitespace.** `10  REM x` comes
back as `10   REM x`, gaining a space per pass, so repeated RENUMs slowly
indent a program. This is in the position serializer rather than in the
statement serializers, and predates all of the above.

**Explicit `LET` is not preserved**, by an existing design decision recorded in
`src/position_serializer.py`: the AST does not distinguish `LET A=5` from
`A=5`, and the serializer always writes the short form.
