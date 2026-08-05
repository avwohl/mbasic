# The MBASIC 5.21 sources - where they are, and when to reach for them

**Created:** 2026-08-05
**Location:** `/home/wohl/src/mbasic2025` - https://github.com/avwohl/mbasic2025

The original 5.21 sources were lost. That repository reconstructs them: the
nearest surviving 5.2 sources, adjusted until they assemble **byte-for-byte
identical** to the `mbasic.com` we test against. Changes made to get there are
marked `;5.21` in the code.

	mbasic_521/mbasic_src/   the reconstructed 5.21 sources (.mac, 8080 assembler)
	mbasic_521/com/          the reference mbasic.com
	mbasic_521/disasm/       a disassembly of it
	mbasic_52/               the original 5.2 sources it started from
	mbasicz/                 a later Z80-optimised version
	4k8k/                    4K and 8K BASIC, with the Altair manual

## When to use them

Whenever the question is "what does MBASIC actually do here". Reading the
routine is faster and more certain than disassembling the binary or inferring
behaviour from outputs - and a comment in the source often says *why*, which no
amount of measurement recovers.

Where the answers already used here came from:

	bintrp.mac    PEEK and POKE, the statement dispatch, expression evaluation
	f4.mac        the arithmetic and the maths library
	bimisc.mac    RND and RANDOMIZE
	bistrs.mac    string handling, VARPTR
	bio.mac       terminal I/O
	dcpm.mac      the CP/M interface

Grep for the keyword in lower case - the sources are written in lower case with
labels like `peek:` and `poke:`.

## What it does not replace

The binary under cpmemu is still the arbiter for anything observable, because
it is the thing users actually ran and because a reconstruction can only be as
right as its verification. The source says what the code does; the binary says
what happens. Use the source to find the answer and the binary to confirm it -
that is how `RND_ALGORITHM.md` was settled, and the two agreed.

See `tests/HOW_TO_RUN_REAL_MBASIC.md` for running the binary.
