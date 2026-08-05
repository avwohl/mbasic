# RND was Python's, and now it is MBASIC's

**Created:** 2026-08-05
**Status:** Fixed - `src/mbasic_rnd.py` (new), `src/basic_builtins.py`,
`src/interpreter.py`, `src/runtime.py`, `src/statement_attempt.py`,
`src/ui/web/nicegui_backend.py`, `src/number_format.py`
**Regression test:** `tests/regression/interpreter/test_rnd_sequence.py`

RND was `random.random()`, seeded from the clock. That is wrong twice over:

	PRINT RND;RND;RND     real 5.21  .245121  .305003  .311866   every run
	                      here       whatever the clock gave, different each time

MBASIC's sequence is fixed. A program that does not say RANDOMIZE deals the
same hand, lays out the same board, and picks the same word every time it is
run - which is what makes a 1979 game reproducible, and what made ours not.

## Finding it

The routine is at 0x37DD in `com/mbasic.com`. It is *not* the RND from the 6502
Microsoft BASICs, and the constants published for those (11879546.0 and
3.92767778E-8) are not in this image - the first thing tried, and it failed.

What worked was asking the interpreter about its own memory. Dumping
0x0100-0x6000 with `PEEK` before and after a single `RND` leaves 25 bytes
changed, and four of them at 0x3869 are the value RND had just returned, in
Microsoft Binary Format. That pins the seed; searching the image for
references to 0x3869 pins the routine; and from there it disassembles.

	0x37DD  the routine            0x3846  a counter that runs to 171
	0x3847  the addend index       0x3848  the multiplier index
	0x3849  eight multipliers, four bytes each
	0x3869  the seed               0x386D  three addends
	0x37C8  the seed RUN loads     0x25DA  the normaliser
	0x24AD  RANDOMIZE

## What it does

	seed = seed * MULTIPLIER[i8] + ADDEND[i3]        in single precision

`i8` steps 0..7 through the multipliers, `i3` cycles 1,2,3 through the addends
(index 0 is skipped because that slot *is* the seed). Then the three mantissa
bytes of the product are put back in a different order, one of them
exclusive-ORed:

	high' = low XOR 0x4F        mid' = mid        low' = high, sign bit and all

the exponent is forced to 0x80 so the value lands in [0.5,1), the sign is
cleared, and the result is normalised.

The one part nobody would guess is the byte the normaliser shifts in from
below. It is not zero and it is not a constant: `MOV B,M` at 0x3824 loads the
*old exponent* and the normaliser uses it as its guard byte. Get that wrong and
the values are right to about seven digits and wrong after - which looks like a
rounding bug and is not one.

Every 171 calls a third counter wraps and nudges three bytes of the result by
one. A sequence checked only a few dozen values deep would look perfect and
then diverge forever, so this is checked out to 200.

## The arguments, measured

	RND, RND(x>0)   the next value. The magnitude is ignored - only the sign is
	                looked at - so RND(1) and RND(5) do the same thing.
	RND(0)          the last value again. Draws nothing.
	RND(x<0)        restart from x itself: the argument's own bytes go through
	                the scramble. Only its mantissa matters, so RND(-1) and
	                RND(-2) give the same number and RND(-1000) does not.

`RANDOMIZE n` writes n's two bytes over the *middle two* bytes of the seed and
draws one value. It leaves the low byte and the exponent alone, which is why
`RANDOMIZE 1` twice in one run gives two different numbers - and why
`basic/dev/tests_with_results/test_randomize.bas`, which asserts that the same
seed gives the same sequence, prints FAIL on the real machine too. Its expected
output was corrected rather than the interpreter.

`RANDOMIZE` with no argument prints `Random number seed (-32768 to 32767)? `
and waits, using the same pause the INPUT statement uses. Seeding from the
clock instead would have made a program that says RANDOMIZE unrepeatable, and
MBASIC's is repeatable.

RUN, CLEAR and NEW share one routine (0x4358) that reloads the seed and zeroes
the counters, so all three restart the sequence.

## Also fixed: single-precision printing rounded once where MBASIC rounds twice

Found while checking `RANDOMIZE`: the first value came out `.043496` here and
`.0434961` on the real binary. MBASIC's conversion produces seven decimal
digits for a 24-bit mantissa and the six it prints are rounded from those, so a
seventh digit that rounds up into a five carries:

	.04349604...    seven digits .04349605    prints .0434961, not .043496
	12.3456497      seven digits 12.34565     prints 12.3457, not 12.3456
	.0999999493     seven digits .09999995    prints .1, not .0999999
	.00434960462    seven digits .004349605   prints 4.34961E-03 - six
	                significant digits no longer fit unscaled

Doubles are left rounding once: measured against the binary, rounding them
twice makes more values wrong rather than fewer.

## Verifying

	python3 tests/regression/interpreter/test_rnd_sequence.py

28 checks: the first sixteen values, values 168-176 and 200 (either side of the
perturbation), that two runs agree, that RUN starts over, the three argument
forms, RANDOMIZE five ways, and RND through PRINT.

End to end, `basic/games/poetry.bas` - which draws three random numbers per
line for pages - now produces output byte-identical to the real binary.

What is checked is the *values*, not their sixteen printed digits: MBASIC's own
binary-to-decimal conversion rounds the sixteenth digit up where correct
rounding rounds it down, for about one value in eight. That is a difference in
its printing, and it is the gap `NUMBER_FORMATTING.md` already records.

## PEEK stays random, and that is deliberate

`BuiltinFunctions.PEEK` returns `random.randint(0, 255)`, which looks like the
last unfixed thing in this area and is not. There is no memory model here for
it to read, and what programs use PEEK for is seeding a generator from whatever
is lying about in memory - so a random byte is the useful answer and a fixed 0
would not be. POKE and VARPTR are the same decision. Recorded in
`NO_MEMORY_MODEL.md`; byte-level fidelity belongs in an 8080 emulator running
the real binary.

The two sit together: RND is deterministic exactly where MBASIC is
deterministic, and a program that wants variety asks for it, with RANDOMIZE or
by seeding from PEEK.

## Not done

The two code generators emit their own RND (`codegen_js_backend.py` uses
`Math.random()`). Compiled output is a separate target and was left alone.
