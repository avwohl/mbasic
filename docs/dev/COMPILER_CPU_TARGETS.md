# MBASIC Compiler CPU Target Options

## Which toolchain serves which target

`--cpu` picks the instruction set the generated C is built for, and that choice
decides which C compiler can do the job:

	--cpu	C compiler	Notes
	z80 (default)	uc80 (preferred), or z88dk	uc80 emits Z80 code only
	8080	z88dk (alternate)	uc80 cannot emit 8080 code

uc80 is Z80-only by design: it always emits `.z80` assembly and freely uses `SBC HL,DE`,
`JR`, `LDIR`, and `IX` addressing. There is no 8080 mode and no flag to ask for one, so
an 8080 build routes to z88dk's `-clib=8080`. See
[TOOLCHAIN_POLICY.md](TOOLCHAIN_POLICY.md).

The emulator is a separate choice from the compiler. cpmemu has both CPU cores —
`--z80` (default) and `--8080` — so it can run and check either build; tnylpo is the
supported alternate.

## Z80 Target (default)

```bash
# Preferred: uc80 -> um80 -> ul80 (see COMPILER_SETUP.md for the full pipeline)
uc80 program.c ... -o program.mac

# Alternate: z88dk, whose +cpm target defaults to Z80
z88dk.zcc +cpm program.c -o program -create-app
```

- Smaller/faster code than an 8080 build
- **Only runs on Z80 systems**
- The default for `--cpu`, and what nearly every surviving CP/M machine runs

## 8080 Target

The 8080 target is built with z88dk (alternate):

```bash
z88dk.zcc +cpm -clib=8080 --math-mbf32 program.c -o program -create-app
```

**Key flags:**
- `-clib=8080` - Use the classic 8080 library
- `--math-mbf32` - Include Microsoft Binary Format 32-bit math (needed for floating point)

### Why 8080

1. **Original CP/M processor** - CP/M was designed for the Intel 8080
2. **Maximum compatibility** - Works on:
   - Intel 8080 (original)
   - Intel 8085 (enhanced 8080)
   - Zilog Z80 (superset of 8080)
   - Compatible clones (NEC V20, etc.)
3. **Historical accuracy** - MBASIC originally ran on 8080 systems
4. **Wider audience** - More systems can run the code

## CPU Architecture Differences

### Intel 8080 (1974)
- 8-bit processor
- 16-bit address bus (64KB memory)
- 8-bit I/O ports (IN/OUT instructions)
- Basic instruction set
- No index registers

### Intel 8085 (1976)
- Binary compatible with 8080
- Added SIM/RIM instructions
- Integrated clock generator
- Can run all 8080 code

### Zilog Z80 (1976)
- **Superset of 8080** - runs all 8080 code
- Additional registers (IX, IY, alternate set)
- More instructions (block moves, bit operations)
- 16-bit I/O addressing (extended IN/OUT)
- More addressing modes

## Hardware Access Implications

### I/O Port Access

Port I/O is one of the places the compiler choice shows through: BASIC `INP`, `OUT`,
and `WAIT` compile to `inp()`/`outp()`, which only z88dk provides. uc80's include tree
has no equivalent and no inline assembly to hand-roll one, so a program that touches
ports is a z88dk program regardless of CPU target.

#### 8080 Limitation
- Only 8-bit port addresses (0-255)
- Simple IN/OUT instructions

```asm
; 8080 IN instruction
IN port     ; port is 8-bit immediate

; 8080 OUT instruction
OUT port    ; port is 8-bit immediate
```

#### Z80 Extension
- 16-bit port addresses (0-65535)
- Register-indirect I/O

```asm
; Z80 extended IN
LD C,port_low
LD B,port_high
IN A,(C)    ; 16-bit port in BC

; Z80 extended OUT
OUT (C),A   ; 16-bit port in BC
```

### Our Implementation

The mb25_hw library provides both versions:

```c
/* Compile with default (8080) */
// Uses self-modifying code for port access
// Limited to ports 0-255

/* Compile with -DUSE_Z80 */
// Uses Z80 extended I/O instructions
// Supports ports 0-65535
```

## Recommendations

### For Modern Development
Use the default Z80 target with uc80:
- Smallest binaries
- Simplest install (`pip install uc80 um80`)
- Target is a known Z80 system or an emulator
- Need I/O ports > 255 (via the z88dk route, see above)

### For Maximum Compatibility
Use `--cpu 8080`, which builds with z88dk:
- Historical software preservation
- Educational purposes
- Wide distribution
- Unknown target systems

### Cases that decide the toolchain for you
- MBF float bit patterns (`MKS$`/`CVS`, random-access records) - z88dk `--math-mbf32`
- `INP`/`OUT`/`WAIT` - z88dk `inp()`/`outp()`
- 8080 output - z88dk `-clib=8080`

Everything else builds fine with uc80.

## Testing Compatibility

### Check Generated Assembly

A uc80 build leaves the assembly on disk already: `program.mac` is the translated
source, and it opens with `.z80` because uc80 targets Z80 only. For a z88dk `.com`,
disassemble it:

```bash
# Disassemble to verify 8080 compatibility
z88dk.z88dk-dis program.com > program.asm
grep -i "ix\|iy\|exx\|ldir" program.asm
# If found, code uses Z80-specific instructions
```

### Test on Emulators
- **cpmemu** - CP/M 2.2 emulator with both cores: `--z80` (default) and `--8080`.
  Running an 8080-target build under `cpmemu --8080` is the direct way to prove it
  really is 8080-clean.
- **tnylpo** - Z80-based CP/M emulator (alternate)
- **SIMH Altair** - 8080/Z80 emulation

## Library Compatibility

The mb25 runtime library is designed for 8080 compatibility:

	Component	8080	Z80	Notes
	mb25_string	yes	yes	Pure C, no assembly
	mb25_hw	yes	yes*	Z80 version with -DUSE_Z80; needs z88dk for inp()/outp()
	mb25_math	yes	yes	Uses standard C math
	mb25_io	yes	yes	CP/M BDOS calls (portable)

*Hardware functions use conditional compilation for CPU-specific code

## Future Enhancements

### Compiler Flag for CPU Target
Could add option to codegen:
```python
class Z88dkCBackend(CodeGenBackend):
    def __init__(self, symbols: SymbolTable, cpu='8080'):
        self.cpu_target = cpu  # '8080' or 'z80'
```

Selecting the *compiler* is a related open item: `--cpu z80` could dispatch to the
uc80 pipeline and fall back to z88dk when the program needs MBF floats or port I/O.

### Runtime CPU Detection
Could detect CPU at runtime:
```c
int is_z80() {
    /* Try Z80-specific instruction */
    /* Trap illegal instruction on 8080 */
    /* Return 1 if Z80, 0 if 8080 */
}
```

## Summary

- **Default: Z80**, built with uc80 - smallest code, simplest install
- **Option: 8080** via z88dk `-clib=8080` - runs on more historical systems
- uc80 cannot emit 8080 code; that target belongs to z88dk
- cpmemu runs either build and can emulate either CPU (`--z80` / `--8080`)
- Library supports both via conditional compilation
- User choice based on target environment
