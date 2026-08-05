# There is no memory model, and PEEK, POKE and VARPTR reflect that

**Created:** 2026-08-05
**Status:** Decided - not a gap, not a TODO. Do not "fix" these.
**Code:** `BuiltinFunctions.PEEK` in `src/basic_builtins.py`,
`Interpreter.execute_poke` in `src/interpreter.py`

	PEEK(X)      returns a random byte, 0-255, different every call
	POKE X,Y     is accepted and discarded
	VARPTR(X)    is not implemented

All three look like stubs and get reported as such. They are one decision, and
this file exists so the next review finds the reasoning instead of an apparent
oversight.

## The decision

**This interpreter has no memory model, and is not going to get one.**

On the real machine these three are trivial. PEEK is one instruction, `MOV A,M`
(`bintrp.mac`, `peek:`); POKE is `STAX D`; VARPTR hands back the address of a
variable in the table. They are trivial *because* everything - the interpreter,
the program text, the variables, the string space - lives in one 64K address
space. Here a variable is a Python object in a dictionary. There is no address
to return, nothing to read, nothing to write.

Simulating that space - laying variables out at MBASIC's addresses, loading the
interpreter image underneath, making VARPTR return real pointers - is a
different project, and the wrong one. **If you need that level of
compatibility, run the real thing under an 8080 emulator**: `com/mbasic.com`
under cpmemu, which this project already uses as its reference (see
`tests/HOW_TO_RUN_REAL_MBASIC.md`). A reimplementation that pretended to be a
machine it is not would be answering for memory it does not have.

## Why PEEK is random rather than 0

Given that there is nothing to read, PEEK has to return *something*, and the
choice is not arbitrary. The commonest thing a BASIC program does with PEEK is
seed a random number generator from whatever happens to be lying around in
memory:

	RANDOMIZE PEEK(&H4000)

A fixed 0 would be deterministic and would defeat the only reason that line is
there. A random byte is what memory the program has no business knowing about
would look like to it, and it makes the idiom work. So PEEK is random, and
stays random.

This fits with RND, which went the other way for the same underlying reason:
RND now reproduces MBASIC's own sequence and is repeatable every run, exactly
as on the real machine (`RND_ALGORITHM.md`). Determinism where MBASIC is
deterministic; an unpredictable byte where the real machine's answer was never
predictable either. A program that wants variety asks for it - with RANDOMIZE,
or by seeding from PEEK.

## The consequence, stated plainly

A program that POKEs an address and PEEKs it back does not get its byte. A
program that walks a string through `VARPTR` and `PEEK` cannot work here at
all. Such programs are rare, were machine-specific even in 1981, and have a
better home: the real binary under an emulator.
