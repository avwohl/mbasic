# GOSUB Stack Depth Test Results for MBASIC 5.21

## Test Date
2025-10-25

## Testing Environment
- MBASIC 5.21 Rev (CP/M Version)
- Running under tnylpo CP/M emulator
- Test files in `tests/` directory

## Test Methodology
Created nested GOSUB tests at various depths to determine if there's a circular buffer limit or maximum stack depth.

## Test Results

| Depth | Result | Notes |
|-------|--------|-------|
| 5     | ✓ PASS | All GOSUBs and RETURNs executed correctly |
| 8     | ✓ PASS | All GOSUBs and RETURNs executed correctly |
| 10    | ✓ PASS | All GOSUBs and RETURNs executed correctly |
| 15    | ✓ PASS | All GOSUBs and RETURNs executed correctly |
| 20    | ✓ PASS | All GOSUBs and RETURNs executed correctly |
| 30    | ✓ PASS | All GOSUBs and RETURNs executed correctly |
| 40    | ✓ PASS | All GOSUBs and RETURNs executed correctly |

## Test Files Generated
- `circ5.bas` through `circ15.bas` - Explicit chain tests
- `s15.bas`, `s20.bas`, `s25.bas`, `s30.bas`, `s35.bas`, `s40.bas` - Compact tests
- `stacktst.bas` - 10-level explicit test with labeled output
- `rec10.bas` - Recursive GOSUB test

## Observations
1. **No 8-level limit found**: Contrary to the initial hypothesis of an 8-level circular buffer, MBASIC 5.21 successfully handles at least 40 levels of nested GOSUBs.

2. **All returns correct**: In all tests, the RETURN statements correctly unwound the stack in reverse order (LIFO).

3. **No overflow errors**: No "out of memory" or "stack overflow" errors were encountered up to depth 40.

4. **Correct execution flow**: Each test showed proper nesting going down (1→2→3...→N) and proper unwinding (RN→...→R3→R2→R1).

## Conclusions
MBASIC 5.21 under tnylpo does not exhibit a hard 8-level GOSUB stack limit. The stack can handle at least 40 levels of nesting without errors or circular buffer behavior. The actual limit may be higher or constrained only by available memory.

## Note
The perceived 8-level limit may have been:
- Specific to different BASIC implementations
- A limitation of certain CP/M systems with limited memory
- Improved in MBASIC 5.21 compared to earlier versions
- Not present when running under tnylpo emulation with modern memory

## Test Utilities Created
- `utils/test_gosub_circular.py` - Generate circular buffer tests
- `utils/gen_compact_stack.py` - Generate compact nested GOSUB tests
- `utils/gen_deep_stack.py` - Generate deep stack tests with large line numbers
