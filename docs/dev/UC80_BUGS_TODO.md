# uc80 / um80 Bugs Found While Making Them the Preferred Toolchain

**Created:** 2026-08-03
**Status:** RESOLVED 2026-08-04 - all seven fixed upstream and verified end to end.
See [Fix status](#fix-status-verified-2026-08-04) at the end for what mbasic can now
stop working around, and for what the verification pass found on top.
**Priority:** Was medium - all had workarounds, none blocked a build
**Upstream:** https://github.com/avwohl/uc80 and https://github.com/avwohl/um80_and_friends

Found while switching mbasic's Z80/CP/M build over to uc80 + cpmemu (see
[TOOLCHAIN_POLICY.md](TOOLCHAIN_POLICY.md)). Every item below was reproduced directly;
each has a minimal standalone repro that can be pasted into a uc80 test.

Ranked by how much damage each does. The first four fail *silently* - they produce a
clean exit and a working-looking binary that does the wrong thing - which is what makes
them worth fixing ahead of anything that merely errors out.

---

## Corrections from the upstream triage (2026-08-03)

uc80 reproduced and root-caused every item. Two findings change how the text below should be
read, and are recorded here so the original wording is not taken at face value. Per-item fix
status is appended at the end of this file once the upstream work is verified.

**Item 3 does not reproduce, and never did.** um80 rejects `ADD HL,BC` and `ADD HL,SP`
*identically*, exits non-zero, and writes no output file:

```
$ um80 opc.mac -o opc.rel
Error at line 4: Unknown instruction or directive: LD
Error at line 5: ADD requires one operand
Error at line 6: ADD requires one operand
EXIT=1
$ ls opc.rel
ls: cannot access 'opc.rel': No such file or directory
```

Three errors, not one - the report quoted only the line-6 error and omitted the other two.
The `len(ops) != 1` guard has been present since um80's first commit, so um80 never behaved
as described. What item 3 describes is genuine **MACRO-80 3.44** behaviour (M80 emits `0x84`
with a `Q` warning and writes the `.REL` anyway); um80 is already stricter and safer. Nothing
in um80's `ADD HL,rr` handling should be "fixed". The same false claim was corrected in
`runtime/strings/mb25_uc80_shim.mac`.

There *is* a real um80 bug next door, which is presumably what was actually being chased: in
8080 mode, a Z80 mnemonic that spells an 8080 no-operand instruction **silently drops its
operand**, with a warning only and exit 0 - `RET NZ` assembles as an unconditional `RET`.
That one is being fixed, as a hard error.

**The open `FRE(A$)` question is attributed: it is a uc80 miscompile.** uc80 never inferred the
*result type* of a comma expression, so `(mb25_garbage_collect(), (double)mb25_get_free_space())`
was treated as `int` - a bogus `int`-to-`double` conversion was emitted on top of the correct
one, and in variadic-argument position only 2 of the `double`'s 4 bytes were pushed. Every
`(a, b)` yielding `double`/`float`/`long`/`long long` was silently wrong. The instinct that it
was "not the cast alone" was right; it was not the cast at all.

The reported `23808` vs z88dk's `47043` was a red herring - no transformation relates the two
numbers, they are simply different string-pool sizes in two different builds. The reproducible
symptom was the reduced case returning 0.

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

## Fix status (verified 2026-08-04)

**All seven items are fixed.** Upstream re-verified every one end to end -- built,
linked and run under cpmemu -- using verifiers working from this document rather than
from the fixes, then fixed what that pass turned up as well. uc80 is at 630 passing
tests, um80/ul80 at 190.

Two of the fixes below are for regressions introduced in uc80 0.6.0 itself, so treat
0.6.0 as superseded rather than merely improved on. Build against uc80 after
`1fb6474` and um80 after `54e9a20`.

| # | Item | Status | Commit(s) |
|---|------|--------|-----------|
| 1 | `asm("...")` discarded | Fixed | `cfeed03`, `44487a7` |
| 2 | Appended `.mac` lands in BSS | Fixed | `e422207`, `ee5ef8e` |
| 3 | um80 operand handling | Report was wrong; a real bug next door is fixed | um80 `a38cc15` |
| 4 | `printf` `%e` and `%g` empty | Fixed, and in the rest of the family too | `215b864`, `ea8b824` |
| 5 | `extern T a[N];` internal error | Fixed | `f96c829`, `744c3f2`, `f90c57a` |
| 6 | Console `LF` instead of `CRLF` | Fixed | `96d866f` |
| 7 | `.lib` files unshipped | Fixed | `bc0463e`, `84ca138` |
| - | `FRE(A$)` (was unattributed) | Fixed; it was a uc80 miscompile | `11cbd0d`, `c000f4c` |

### What mbasic can stop doing

- **Item 2 - the separate-assembly shim.** `uc80 program.c mb25_uc80_shim.mac` now
  places the code in CSEG ahead of the BSS block, so it survives crt0. It is also
  fenced from the peephole, which until `1563862` rewrote hand-written assembly (it
  fused `LD A,(HL)` + `LD C,A` with A still live, and deleted a label caught between
  them). Assembling the shim separately still works and remains a perfectly good
  choice; it is no longer a workaround for anything. `mb25_uc80_shim.mac` still has to
  exist for `__bss_end`, which C cannot name.

- **Item 5 - the unsized extern in `mb25_string.h`.** `extern int arr[100];` followed
  by `int arr[100];` compiles, and a genuine size conflict is now diagnosed instead of
  crashing. Confirm with:

      printf 'extern int a[100];\nint a[100];\n' > t.c && uc80 t.c -o t.mac

  One caveat before changing the header: if the bound is spelled with an enum
  constant, that only started working in `f90c57a`. Before it, `enum {N=8}; extern int
  a[N]; int a[];` allocated **zero bytes** and the next global was written through it.

- **Item 4 - `%f` in generated `PRINT`.** `%g` works, in every printf-family entry
  point, so BASIC `PRINT` can use it and get MBASIC's trailing-zero behaviour. Two
  things to know first: `%lg` is **not** registered by auto-detection or
  `--printf float` (see Still open), so spell it `%g` or pass `--printf all`; and
  `%f` itself was wrong for every value >= 65536 until `9306503` -- `1000000.0`
  printed as `3906.00///`. If mbasic ever printed a large number and got something
  that was not even digits, that was this.

### Confirm any of it yourself

    LIB=$(uc80 --print-lib-dir)
    uc80 t.c -o t.mac && um80 t.mac -o t.rel \
      && ul80 t.rel $LIB/libc.lib $LIB/runtime.lib -o t.com && cpmemu t.com

| Item | One-line check |
|------|----------------|
| 1 | `void f(void){ asm("ld hl,1234\n\tld (_marker),hl"); }` -> prints 1234 |
| 2 | the `kconst` helper from this document -> prints 4660, not 65281 |
| 3 | `um80` on `LD HL,0` / `ADD HL,SP` with no `.z80` -> three errors, exit 1, no output |
| 4 | `printf("[%e][%g]", 28.0, 28.0)` -> `[2.800000e+01][28]`, and the same from `sprintf` |
| 5 | `extern int a[100]; int a[100];` -> compiles; `int a[200];` -> diagnosed |
| 6 | `cpmemu prog.com \| cat -A` -> lines end `^M$` |
| 7 | `uc80 --print-lib-dir` -> one line, exit 0, holds `libc.lib` |

### Corrections to this document, confirmed

Both corrections recorded in the earlier triage section hold up:

- **Item 3 does not reproduce and never did.** The `len(ops) != 1` guard has been in
  um80 since its first commit. What item 3 describes is MACRO-80 3.44 behaviour.
  There *was* a real operand-dropping bug beside it, and checking that one turned up
  two more, all now fixed: a Z80 mnemonic spelling an 8080 no-operand instruction
  dropped its operand (`RET NZ` -> `RET`); `SUB`/`AND`/`XOR`/`OR`/`CP` dropped the
  operand of their `A,` form, so **`CP A,5` assembled as `CP A`** -- a comparison that
  always compares equal, exit 0, no diagnostic; and `.Z80` anywhere in a file
  retroactively assembled every line above it as Z80 on the second pass.

- **`FRE(A$)` was a uc80 miscompile**, as the triage concluded. Two further defects in
  that same work were found afterwards: a comma yielding a 64-bit *literal*
  (`(f(), 42LL)`) evaluated to whatever the 64-bit accumulator last held -- a
  regression introduced by the FRE fix itself -- and struct-valued commas produced
  garbage and silently skipped the left operand in argument position.

### Still open

Nothing here blocks mbasic, and nothing here is one of the seven reported items.
Full list with repros in `uc80/todo.txt`. The ones most likely to matter to mbasic:

- **`%lf`, `%le` and `%lg` are not registered** by auto-detection or `--printf float`.
  Silent: the conversion is echoed verbatim and every later one in that call reads the
  wrong argument. mbasic's generated C emits `%lg`. Use `%g`, or `--printf all`.
- **`%.*f` and `%*f` are unsupported**, with the same silent argument desync.
- **Field width and the `-`, `+` and ` ` flags do nothing on a float conversion.**
  `%10.2f` prints `1.50`. Not float-specific -- the format parser discards those
  flags for every conversion, so they have never worked.
- **`printf` in a `default:` label or an initializer list is invisible** to
  auto-detection, so its conversions go unregistered. Silent.
- Under `--no-whole-program`, the printf dispatch table is emitted by the unit
  defining `main()`. A unit that prints conversions `main`'s unit does not now warns
  and tells you to pass an explicit `--printf`. mbasic compiles both its files in one
  invocation, so this does not apply to it.
