# uc80 / um80 Bugs Found While Making Them the Preferred Toolchain

**Created:** 2026-08-03
**Status:** Not Started - these are upstream bugs in the sister projects
**Priority:** Medium - all have workarounds in place, none currently block a build
**Upstream:** https://github.com/avwohl/uc80 and https://github.com/avwohl/um80_and_friends

Found while switching mbasic's Z80/CP/M build over to uc80 + cpmemu (see
[TOOLCHAIN_POLICY.md](TOOLCHAIN_POLICY.md)). Every item below was reproduced directly;
each has a minimal standalone repro that can be pasted into a uc80 test.

Ranked by how much damage each does. The first four fail *silently* - they produce a
clean exit and a working-looking binary that does the wrong thing - which is what makes
them worth fixing ahead of anything that merely errors out.

---

## 1. `asm("...")` is parsed and then silently discarded

**Severity: high - silent miscompile.** No error, no warning, no code. Anyone porting
SDCC or GCC-flavoured Z80 code gets a binary where the assembly simply is not there.

```c
int marker;
void f(void) { asm("ld hl,1234\n\tld (_marker),hl"); }
int main(void){ f(); return marker; }
```

```
$ uc80 -P a.c -o a.mac    # exit 0, no diagnostic
$ grep -c 1234 a.mac
0
```

The grammar accepts `asm` / `__asm__` (including `volatile` and operand lists), and
codegen has no handler, so the node is dropped. Either implement it or make it a hard
error - anything is better than emitting nothing quietly.

Related: `#asm`/`#endasm` and `__naked` *do* error out, which is correct behaviour.

---

## 2. A `.mac` passed to `uc80` is placed in BSS and zeroed at startup

**Severity: high - silent miscompile.** `uc80 prog.c helper.mac` is the documented way
to supply hand-written assembly. It compiles, links, and runs - and the routine returns
garbage.

```
; helper.mac
	.z80
	CSEG
	PUBLIC	_kconst
_kconst:
	LD	HL,4660      ; 0x1234
	RET
	END
```

```c
#include <stdio.h>
extern unsigned int kconst(void);
static int big[64];                 /* force the program to have BSS */
int main(void){ big[0]=1; printf("kconst=%u (want 4660)\n", kconst()); return 0; }
```

```
$ uc80 p.c helper.mac --printf int --no-embed-runtime -o p.mac
$ um80 p.mac -o p.rel && ul80 p.rel $UCLIB/libc.lib $UCLIB/runtime.lib -o p.com
$ cpmemu p.com
kconst=65281        <-- 0xFF01, not 4660
```

Cause: uc80 strips the `CSEG` directive from an appended `.mac` (it is in the
skip-headers set) and appends the file *after* its own `common //` BSS directive, so the
code lands in the COMMON block and `crt0`'s zeroing loop wipes it before `main`. It only
appears to work when the C program has no BSS at all.

Workaround in use: assemble the shim separately with `um80` and hand the `.rel` to
`ul80`. mbasic ships `runtime/strings/mb25_uc80_shim.mac` and does exactly that.

Suggested fix: preserve the segment directive, or append `.mac` content before the BSS
directive, or simply reject `.mac` inputs and point at the separate-assembly route.

---

## 3. um80 assembles Z80 mnemonics as 8080 without `.z80`, and writes output anyway

**Severity: high - silent miscompile, plus a broken exit contract.**

```
	CSEG
	PUBLIC	TSTOP
TSTOP:
	LD	HL,0
	ADD	HL,SP
	ADD	HL,BC
	RET
	END
```

```
$ um80 opc.mac -o opc.rel
Error at line 6: ADD requires one operand      <-- ADD HL,BC
```

`ADD HL,BC` is rejected but `ADD HL,SP` is *accepted* and assembled to something other
than `39`, so `LD HL,0 / ADD HL,SP` silently returns 0 instead of the stack pointer.
Adding `.z80` fixes it. Two separate problems:

- Inconsistent handling: one `ADD HL,rr` form errors, another is quietly mis-assembled.
- **um80 still writes an output file after reporting errors.** A build script that
  checks for the output rather than the exit status proceeds with a corrupt `.rel`.
  Errors should suppress the output file and force a non-zero exit.

---

## 4. `printf` `%e` and `%g` produce empty output

**Severity: medium - silent wrong output.** `%f` works; the other two float conversions
emit nothing at all, not even a fallback.

```c
#include <stdio.h>
int main(void){ float a=28.0; printf("f=[%f]\n",a); printf("e=[%e]\n",a); printf("g=[%g]\n",a); return 0; }
```

```
f=[28.000000]
e=[]
g=[]
```

Built with `--printf int --printf float`. `%g` matters here because it is the natural
choice for BASIC's `PRINT` - it drops trailing zeros the way MBASIC does. mbasic's uc80
path emits `%f` and accepts the cosmetic difference.

Note the flags accumulate rather than replace: `--printf float` on its own silently
drops `%d`, which is its own small trap.

---

## 5. Internal error on `extern T a[N];` followed by `T a[N];`

**Severity: medium - hard failure, but blocks the standard C idiom.** A header declaring
an array and a source file defining it is ordinary C, so this stops most real projects.

```c
extern int arr[100];
int arr[100];
```

```
$ uc80 -P arr.c -o arr.mac
uc80: internal error: '<' not supported between instances of 'Token' and 'Token'
```

`uc80/codegen.py:2769`, in `_merge_array_size`:

```python
and cur_size.value < prev_size.value):
```

Both `.value`s are `Token` objects rather than ints, so the comparison raises. The sizes
need evaluating (or the tokens' numeric values extracting) before comparison.

An unsized extern (`extern int arr[];`) avoids it - that is the workaround now in
`runtime/strings/mb25_string.h`.

---

## 6. Console output uses bare LF instead of CRLF

**Severity: low - wrong on real hardware.** Real CP/M and real MBASIC end console lines
with CRLF; uc80's libc does not translate `\n` on the way out.

```
$ cpmemu uc80-built.com  | cat -A | head -1
Testing IF/THEN/ELSE with A=10 and B=20$        <-- LF only
$ cpmemu z88dk-built.com | cat -A | head -1
Testing IF/THEN/ELSE with A=10 and B=20^M$      <-- CRLF
```

Harmless under an emulator that is writing to a Unix terminal; on a real CP/M terminal
the output stair-steps. `utils/compare_toolchains.sh` strips CR before diffing because
of this.

---

## 7. The `.lib` files are not shipped and not discoverable

**Severity: low - packaging.** `libc.lib` and `runtime.lib` are build artifacts. The pip
package does not ship them, and in a source checkout they land in the repo's top-level
`lib/`, not beside the Python package in `src/uc80/lib/`. There is no flag, environment
variable, or API that reports the path, so every consumer has to guess.

mbasic guesses in `uc80_lib_dir()` (`src/mbasic_main.py`), checking both locations and
honouring `MBASIC_UC80_LIB`. It would be better upstream as either shipped `.lib` files
or a `uc80 --print-lib-dir`.

---

## Not uc80 bugs - recorded so nobody re-reports them

- **Last-digit float differences vs z88dk.** uc80 is 32-bit IEEE 754; mbasic builds
  z88dk with `--math-mbf32`. Same 24-bit mantissa, different rounding, so results can
  differ by one ULP (`5.859874` vs `5.859875`). Working as designed.
- **`MKS$`/`CVS` round-trips producing garbage under uc80.** These depend on MBASIC's
  float *bit patterns*, which only MBF gives. Such programs must use `--toolchain z88dk`.
  Not fixable in uc80 short of adding MBF support.
- **`label: }` rejected.** uc80 is right and mbasic was wrong - a label must precede a
  statement in C17. Fixed on our side in `_finalize_lines()`, which emits `label: ;`.

## Open question, not yet attributed

- **`FRE(A$)` returns a wrong value in uc80 builds** (23808 where z88dk reports 47043,
  and 0 in a reduced case). The pool bootstrap is *not* the cause: an instrumented build
  showed `bss=16208 sp=64760 size=47530`, which matches z88dk's pool almost exactly. So
  the fault is downstream in `mb25_get_free_space()` or in how the comma expression
  `(mb25_garbage_collect(), (double)mb25_get_free_space())` is compiled. A direct
  `uint16_t`-to-`double` conversion test passed, so it is not the cast alone. Needs
  isolating before it can be filed against either project.
