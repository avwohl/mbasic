# MBASIC Compiler CPU Target Options

## Current Status: Z80 Default

The MBASIC compiler currently generates **Z80 code by default** due to z88dk's +cpm target defaulting to Z80.

### Known Issue with 8080 Target

The `-m8080` flag has linking problems with printf functions in current z88dk versions, producing errors like:
```
error: undefined symbol: __printf_get_flags_impl
error: undefined symbol: fputc_cons_native
```

Until this is resolved, we use the default Z80 target.

### Why We Wanted 8080

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

## Compiler Options

### Default (8080)
```bash
z88dk.zcc +cpm -m8080 program.c -o program
```
- Most compatible
- Works everywhere
- Slightly larger/slower code

### Z80 Optimized
```bash
z88dk.zcc +cpm -mz80 program.c -o program
```
- Uses Z80-specific features
- Smaller/faster code
- **Only works on Z80 systems**

## Hardware Access Implications

### I/O Port Access

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

### For Maximum Compatibility
Use default 8080 mode:
- Historical software preservation
- Educational purposes
- Wide distribution
- Unknown target systems

### For Modern Development
Consider Z80 mode if:
- Target is known Z80 system
- Need I/O ports > 255
- Want smaller/faster code
- Using Z80-specific hardware

## Testing Compatibility

### Check Generated Assembly
```bash
# Disassemble to verify 8080 compatibility
z88dk.z88dk-dis program.com > program.asm
grep -i "ix\|iy\|exx\|ldir" program.asm
# If found, code uses Z80-specific instructions
```

### Test on Emulators
- **8080 emulator** - Test 8080 compatibility
- **tnylpo** - Z80-based CP/M emulator
- **SIMH Altair** - 8080/Z80 emulation

## Library Compatibility

The mb25 runtime library is designed for 8080 compatibility:

| Component | 8080 | Z80 | Notes |
|-----------|------|-----|-------|
| mb25_string | ✓ | ✓ | Pure C, no assembly |
| mb25_hw | ✓ | ✓* | Z80 version with -DUSE_Z80 |
| mb25_math | ✓ | ✓ | Uses standard C math |
| mb25_io | ✓ | ✓ | CP/M BDOS calls (portable) |

*Hardware functions use conditional compilation for CPU-specific code

## Future Enhancements

### Compiler Flag for CPU Target
Could add option to codegen:
```python
class Z88dkCBackend(CodeGenBackend):
    def __init__(self, symbols: SymbolTable, cpu='8080'):
        self.cpu_target = cpu  # '8080' or 'z80'
```

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

- **Default: 8080** for maximum compatibility
- **Option: Z80** for enhanced features
- Code runs on more systems with 8080 target
- Library supports both via conditional compilation
- User choice based on target environment