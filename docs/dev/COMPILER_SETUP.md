# MBASIC Compiler Setup

The MBASIC compiler emits C. That C is built into a CP/M `.COM` file by a Z80 C
toolchain and run under a CP/M emulator. Two of each are supported:

	Role	Preferred	Supported alternate
	C compiler	uc80 (+ um80, ul80)	z88dk (zcc)
	CP/M emulator	cpmemu	tnylpo

Install the preferred pair first — it is the shorter setup and produces smaller
binaries. z88dk and tnylpo remain supported and are still the route for Microsoft
Binary Format floats (`--math-mbf32`), true Intel 8080 output, and `INP`/`OUT`/`WAIT`
port I/O. See [TOOLCHAIN_POLICY.md](TOOLCHAIN_POLICY.md) for which tool covers what.

## Requirements

### 1. uc80, um80, ul80 (preferred compiler)

uc80 is a C compiler for Z80/CP/M optimized for small code size. It is a
C-to-assembly translator only — it never invokes an assembler or linker — so a build
runs three tools: `uc80` writes a `.mac`, `um80` assembles it to `.rel`, and `ul80`
links the `.rel` files into a `.COM`.

```bash
pip install uc80 um80
```

`ul80` ships inside the `um80` package, so those two installs give all three
binaries. Project page: https://github.com/avwohl/uc80

**Important**: `uc80`, `um80`, and `ul80` must be in your PATH. `pip install --user`
puts them in `~/.local/bin`, which is not on the default PATH on every distribution.

Know these limits before you pick uc80 for a program:

- Z80 only — it always emits `.z80` code, so it cannot serve `--cpu 8080`.
- `float`, `double`, and `long double` are all 32-bit IEEE 754. There is no MBF
  support, so anything depending on MBASIC's exact float *bit patterns*
  (`MKS$`/`CVS`, random-access record layouts) needs z88dk.
- No inline assembly and no `inp()`/`outp()`, so BASIC `INP`/`OUT`/`WAIT` needs z88dk.

### 2. cpmemu (preferred emulator)

cpmemu is a CP/M 2.2 emulator with Z80 (`--z80`, the default) and 8080 (`--8080`) CPU
cores. It translates BDOS/BIOS calls straight to the host file system, so there is no
disk image to build and test programs can sit anywhere in the Linux tree. It runs
`.COM` files from **either** compiler.

Install the `.deb` or `.rpm` from the releases page, or build from source:
https://github.com/avwohl/cpmemu

**Important**: `cpmemu` must be in your PATH for test scripts to find it.

### 3. z88dk (alternate compiler)

z88dk's `zcc` driver compiles, assembles, and links in one command, and is what the
built-in `--compile-c` backend shells out to today.

**Important**: `z88dk.zcc` must be in your PATH for that backend to work.

#### Option 1: Snap (Ubuntu/Debian)
```bash
sudo snap install z88dk

# Add snap binaries to PATH (add to ~/.bashrc or ~/.profile)
export PATH="$PATH:/snap/bin"
```

#### Option 2: Build from Source
```bash
git clone https://github.com/z88dk/z88dk.git
cd z88dk
./build.sh
export PATH="$PATH:$HOME/z88dk/bin"
```

#### Option 3: Docker
```bash
docker pull z88dk/z88dk
# Create wrapper script in PATH
echo '#!/bin/bash
docker run --rm -v "$PWD":/src -w /src z88dk/z88dk z88dk.zcc "$@"' > ~/bin/z88dk.zcc
chmod +x ~/bin/z88dk.zcc
```

### 4. tnylpo (alternate emulator)

See [TNYLPO_SETUP.md](TNYLPO_SETUP.md) for detailed installation instructions.

Quick install:
```bash
# Clone and build
git clone https://gitlab.com/gbrein/tnylpo.git
cd tnylpo
make
sudo make install  # Or copy to ~/bin and add to PATH
```

## Verify Installation

### Check uc80 and cpmemu
```bash
# All four binaries should resolve
which uc80 um80 ul80 cpmemu

# uc80 prints its usage; cpmemu prints its CPU mode
uc80 -h
cpmemu
```

### Check z88dk
```bash
# Check that z88dk.zcc is in PATH
which z88dk.zcc

# Test with our utility
python3 utils/check_z88dk.py

# Test compilation
z88dk.zcc --version
```

### Check tnylpo (if installed)
```bash
# Check that tnylpo is in PATH
which tnylpo

# Test with our utility
python3 utils/check_tnylpo.py
```

## Compiling BASIC Programs

### Step 1: Generate C Code
```bash
python3 mbasic --compile-c program program.bas
# Writes program.c
```

### Step 2: Build with uc80 (preferred)

uc80 has no driver mode that produces a `.COM`, so the build orchestrates all three
tools. `$N` is the string-descriptor count the generated C was built for, and `$UCLIB`
is the uc80 package's `lib/` directory — there is no flag or environment variable for
it, so derive it from the installed module path:

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

Four details in there are load-bearing, and each one cost real debugging time. Pass
every translation unit to a single `uc80` invocation — it merges them, so a `#define`
that differs between two `.c` files is an ODR conflict, not two independent
compilations. Assemble the hand-written shim *separately*: handing a `.mac` to `uc80`
looks like it works but lands the code in BSS, where `crt0` zeroes it. Pass both
`--printf int` and `--printf float` — the flags accumulate rather than replace.
And `--no-embed-runtime` is what stops `runtime.lib` colliding with uc80's built-in
copy ("Multiply defined global `__FMUL`"). The full list, including the uc80 bugs
worked around in codegen, is in [TOOLCHAIN_POLICY.md](TOOLCHAIN_POLICY.md).

On the sample program this produces byte-identical output to the z88dk build in a
binary about 22% smaller (13,824 vs 17,643 bytes).

### Step 3: Build with z88dk (alternate)

Use this route for MBF floats, `--cpu 8080`, or port I/O. `zcc` does everything in
one command:

```bash
# For programs without strings
z88dk.zcc +cpm program.c -create-app -lm -o program

# For programs with strings (need mb25_string runtime)
z88dk.zcc +cpm program.c runtime/strings/mb25_string.c -create-app -lm -o program
```

Either route creates `PROGRAM.COM`, which runs on CP/M systems — and under cpmemu:

```bash
cpmemu program.com
```

### The built-in `--compile-c` path

`python3 mbasic --compile-c program program.bas` drives the whole pipeline for you,
using the preferred toolchain by default — it runs `uc80`, then `um80`, then `ul80`,
assembling `runtime/strings/mb25_uc80_shim.mac` separately along the way. `--run`
launches cpmemu.

	Flag	Default	Alternate
	--toolchain	uc80	z88dk
	--emulator	cpmemu	tnylpo
	--cpu	z80	8080 (forces z88dk)

```bash
# preferred: uc80 + cpmemu
python3 mbasic --compile-c program program.bas --run

# alternate toolchain, still run under cpmemu
python3 mbasic --compile-c program program.bas --toolchain z88dk --run

# 8080 output - uc80 is Z80-only, so this switches to z88dk and says so
python3 mbasic --compile-c program program.bas --cpu 8080 --run
```

`--cpu 8080`, Microsoft Binary Format floats, and `INP`/`OUT`/`WAIT` all need z88dk.
Either toolchain's `.COM` runs under cpmemu. To check that both agree on a program,
use `utils/compare_toolchains.sh`.

## String Runtime Library

Programs that use strings need the mb25_string runtime library:

1. Copy `runtime/strings/mb25_string.h` and `runtime/strings/mb25_string.c` to your
   build directory
2. Include both files in the build:
   ```bash
   # uc80: one invocation, both units, and -D so every unit agrees on the count
   uc80 -DMB25_NUM_STRINGS=$N -I. program.c mb25_string.c \
        --printf int --printf float --no-embed-runtime -o program.mac

   # z88dk: separate compilation, so the header default is fine
   z88dk.zcc +cpm program.c mb25_string.c -create-app -lm -o program
   ```

## Troubleshooting

### "uc80: command not found" (or um80/ul80/cpmemu)
- Confirm the pip install landed on your PATH: `python3 -m pip show uc80`
- `pip install --user` installs to `~/.local/bin` — add it:
  `export PATH="$HOME/.local/bin:$PATH"`
- cpmemu is not a pip package; install the `.deb`/`.rpm` or build from source

### "ul80: cannot open libc.lib"
- The library path is not discoverable by flag. Recompute `$UCLIB` from the module
  path as shown in Step 2.

### A uc80-built program returns garbage from a hand-written routine
- The `.mac` was passed to `uc80` instead of `um80`. Assemble it separately and link
  the `.rel` (gotcha 2 in [TOOLCHAIN_POLICY.md](TOOLCHAIN_POLICY.md)).

### A uc80-built program prints nothing for a float
- `printf` supports `%f` but not `%e` or `%g` — those produce empty output silently.

### "z88dk.zcc: command not found"
- z88dk is not installed or not in PATH
- Run `echo $PATH` to check your PATH
- Run `find / -name z88dk.zcc 2>/dev/null` to locate the binary
- Add the directory containing z88dk.zcc to your PATH

### z88dk compilation errors
- Check that you're using the correct z88dk target: `+cpm` for CP/M
- For floating point, ensure `-lm` is included
- For strings, ensure mb25_string.c is included in compilation

## Compiler Implementation Note

The `--compile-c` backend uses `/usr/bin/env z88dk.zcc` to find z88dk in PATH. That
approach is portable across installation methods (snap, source build, docker) as long
as the binary is accessible in PATH, and it is how the uc80 tools will be located too
once the backend can drive them.

See `src/codegen_backend.py:get_compiler_command()` for the implementation, and
[PATH_BASED_TOOLS.md](PATH_BASED_TOOLS.md) for why the toolchain is found through
PATH rather than hardcoded paths.
