# Z80/CP/M Toolchain Policy

**This document is the source of truth for which Z80 C compiler and which CP/M emulator
this project prefers. Read it before editing any file that mentions either.**

Enforced by `python3 utils/check_toolchain_policy.py`, which runs from
`utils/checkpoint.sh` on every commit. If the check fails, fix the document — do not
weaken the check.

## The policy

	Role	Preferred	Supported alternate
	C compiler	uc80 (+ um80, ul80)	z88dk (zcc)
	CP/M emulator	cpmemu	tnylpo

- **uc80** — https://github.com/avwohl/uc80 — C compiler for Z80/CP/M, optimized for
  small code size. Uses the **um80** assembler and **ul80** linker.
- **cpmemu** — https://github.com/avwohl/cpmemu — CP/M 2.2 emulator with Z80 and 8080
  CPU cores. Translates BDOS/BIOS calls to the host file system, so no disk image is
  needed and test programs can live anywhere in the Linux tree.

z88dk and tnylpo are **not banished**. They remain supported, are still used for the
two things uc80 cannot do (below), and it is fine to build and test with both. They are
simply not the default, and must never be documented as "required".

### Why this document exists

This preference was set, reverted, and re-set many times. The docs kept drifting back to
"z88dk (required) / tnylpo (optional)" — describing a toolchain that is not even
installed on the maintainer's machine. The rule is now machine-checked so a regression
fails a commit instead of quietly surviving.

## What z88dk is still needed for

These are real capability gaps, not preferences:

1. **Microsoft Binary Format floats.** z88dk's `--math-mbf32` gives 4-byte MBF32 floats
   matching MBASIC's exact bit patterns. uc80 has no MBF support at all — its `float`,
   `double`, and `long double` are all 32-bit IEEE 754. Same 24-bit mantissa, so printed
   results generally agree, but the stored bit patterns do not. Anything that depends on
   MBASIC-compatible float *representation* (`MKS$`/`CVS`, random-access file records)
   must use z88dk.
2. **True Intel 8080 output.** uc80 is Z80-only: it always emits `.z80` and uses
   `SBC HL,DE`, `JR`, `LDIR`, and `IX` addressing. `--cpu 8080` must route to z88dk's
   `-clib=8080`. (cpmemu itself is fine either way — it has a real `--8080` CPU core.)
3. **Port I/O.** BASIC `INP`/`OUT`/`WAIT` compile to z88dk's `inp()`/`outp()`. uc80's
   include tree has no equivalent.

## The uc80 build pipeline

uc80 is a C-to-assembly translator only — it never invokes the assembler or linker, and
there is no driver mode that produces a `.COM`. The build must orchestrate three tools:

```bash
UCLIB=$(python3 -c "import uc80,os;print(os.path.join(os.path.dirname(uc80.__file__),'lib'))")

# 1. C -> .mac   (all translation units in ONE invocation; see gotcha 3)
uc80 -DMB25_NUM_STRINGS=$N -I runtime/strings \
     program.c runtime/strings/mb25_string.c \
     --printf int --printf float --no-embed-runtime -o program.mac

# 2. .mac -> .rel
um80 program.mac -o program.rel

# 3. assembly shim -> .rel   (SEPARATELY - see gotcha 2)
um80 runtime/strings/mb25_uc80_shim.mac -o shim.rel

# 4. link
ul80 program.rel shim.rel "$UCLIB/libc.lib" "$UCLIB/runtime.lib" -o program.com

# 5. run
cpmemu program.com
```

Verified end to end: a compiled BASIC program produces output identical to the z88dk
build, in a binary about 22% smaller (13,824 vs 17,643 bytes on the sample program).

## Gotchas found the hard way

Each of these cost real debugging time. They are recorded so nobody has to rediscover them.

**1. Inline assembly does not exist, and fails silently.**
uc80 has no `#asm`/`#endasm` and no `__naked`. Worse, GCC-style `asm("...")` *parses
cleanly and is then silently discarded* — no warning, no error, no code. Never write
inline asm for uc80. Put it in a `.mac` file.

**2. Never pass a hand-written `.mac` to `uc80` directly.**
`uc80 prog.c shim.mac` looks like it works and links, but uc80 strips the `CSEG`
directive and appends the file *after* its own BSS directive — so the hand-written code
lands in BSS and is zeroed by `crt0` at startup. The symptom is maddening: a routine that
returns a constant returns garbage (a function returning `0x1234` returned `0xFF01`).
Assemble the shim separately with `um80` and hand the `.rel` to `ul80`.

**3. uc80 merges all translation units.**
A `#define` that differs between two `.c` files is an ODR-style conflict, not two
independent compilations. mbasic's generated C used to emit `#define MB25_NUM_STRINGS 4`
before including the header while the runtime saw the default of 100 — fine under z88dk's
separate compilation, memory corruption under uc80. Pass it with `-D` so every unit agrees.

**4. `printf` supports `%f` but not `%e` or `%g`.**
Those two produce *empty output*, silently. Generated code must use `%f` on uc80.
Also pass `--printf int --printf float` — the flags accumulate, they do not replace, and
`--printf float` alone drops integer conversions.

**5. C symbol naming adds an underscore.**
uc80 prefixes C identifiers with `_`, so C's `_mb25_get_sp` is `__mb25_get_sp` in
assembly. A consequence: C cannot name the linker symbols `__END__` / `__BSS_START` /
`__BSS_END` directly (`extern char __END__[]` emits `EXTRN ___END__` and fails to link).
Reach them through an assembly shim.

**6. Hand-written `.mac` must start with `.z80`.**
Without it um80 assembles in 8080 mode. It rejects `ADD HL,BC` but accepts
`ADD HL,SP` while generating wrong code, and still writes an output file. Silent
miscompilation.

**7. `--no-embed-runtime` when linking `runtime.lib`.**
By default uc80 embeds the runtime *and* you link `runtime.lib`, which gives
"Multiply defined global `__FMUL`" and friends.

**8. `extern T a[N];` followed by `T a[N];` crashes uc80.**
Two-line reproducer:

```c
extern int arr[100];
int arr[100];
```

→ `uc80: internal error: '<' not supported between instances of 'Token' and 'Token'`
(`uc80/codegen.py:2769`, `_merge_array_size` comparing `Token` objects instead of ints).
This is the ordinary header-declares/source-defines C idiom, so it blocks most real
projects. Worked around here by declaring the array unsized in the header
(`extern mb25_string_t mb25_strings[];`), which is valid C and works with both compilers.

**9. A label may not sit directly before `}`.**
uc80 correctly enforces C17 here; GCC and z88dk accept `label: }` as an extension.
Generated code must emit `label: ;`.

**10. Library location is not discoverable, and the libraries may not exist.**
`libc.lib` and `runtime.lib` are *build artifacts*. The pip package does not ship them,
and in a source checkout they land in the repo's top-level `lib/`, not beside the Python
package in `src/uc80/lib/`. There is no flag or environment variable for the path, so
mbasic derives it from the installed module and checks both locations
(`uc80_lib_dir()` in `src/mbasic_main.py`); `MBASIC_UC80_LIB` overrides. If they are
missing, generate them with `python3 -m uc80.lib.build_libs`.

**11. Stack size is set by replacing crt0, not by a pragma.**
z88dk's `#pragma output CRT_STACK_SIZE = N` has no uc80 equivalent. The uc80 way is
`--startup-lib` with a modified `crt0.mac`. mbasic does not currently do this — it takes
uc80's default stack and applies `stack_reserve` at run time when sizing the pool.

**12. `__END__` and `__BSS_END` are the same address.**
ul80 predefines `__END__`, `__BSS_START`, and `__BSS_END`, and sets
`__END__ = __BSS_END = common_base + total_common`. Either name works as the analogue of
z88dk's `__BSS_tail`; the shim uses `__bss_end` because `crt0.mac` already does.

**13. `malloc`'s heap does not start at `__END__`.**
Not currently a problem — the string pool is placed explicitly — but worth knowing before
anyone mixes `malloc` into CP/M builds.

**14. Line endings differ: uc80 emits bare LF, z88dk emits CRLF.**
Real CP/M and real MBASIC end console lines with CRLF, so z88dk is the faithful one here;
uc80's libc does not translate `\n` on the way to the console. Byte-comparing the output
of the two builds therefore reports a difference on every single line. Normalize `\r`
before diffing, and be aware that uc80-built output on a real CP/M terminal will stair-step
rather than return the carriage.

## Rules for editing docs

1. Where both are named, **uc80 before z88dk** and **cpmemu before tnylpo**.
2. Never write "z88dk is required", "requires z88dk", or "**z88dk** (required)". Same for
   tnylpo. Label them "(alternate)".
3. `docs/history/` and `docs/future/` are exempt — they are a record of
   what was true at the time.
4. Docs whose subject *is* the alternate toolchain (`docs/dev/TNYLPO_SETUP.md`,
   `docs/dev/COMPILER_Z88DK_PATH_CHANGE.md`) may lead with it, but still may not call it
   required.

## Current status

- Documentation, policy, and the checker: done.
- `cpmemu` as the default emulator: works today for binaries from **either** compiler —
  it is a drop-in replacement for tnylpo.
- `uc80` as the default compiler: the pipeline is proven end to end, and requires the
  codegen changes listed above. Programs using `INP`/`OUT`/`WAIT`, MBF-format float I/O,
  or `--cpu 8080` still route to z88dk.
