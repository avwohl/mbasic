---
title: MBASIC Compatibility Guide
type: reference
category: mbasic
keywords:
- compatibility
- differences
- limitations
- what works
- cpm
- mbasic 5.21
- portability
description: Complete guide to MBASIC 5.21 compatibility and differences from CP/M MBASIC
---

# MBASIC Compatibility Guide

## Our MBASIC vs Original 8080 MBASIC-80

This document describes compatibility between **MBASIC-2025** (this implementation) and the original MBASIC 5.21 for CP/M-80 (Intel 8080/Z80).

## Compatibility Level

This interpreter provides **100% compatibility** for standard MBASIC 5.21 programs, plus [modern extensions](extensions.md) for development.

### What This Means

- ✓ All language features work identically to MBASIC 5.21
- ✓ All statements and functions produce the same results
- ✓ All error codes and messages match the original
- ✓ File I/O behavior is consistent
- ✓ Numeric precision matches CP/M MBASIC
- ✓ String handling is identical

## Fully Compatible Features

### Core Language

**All statements work exactly as in MBASIC 5.21:**

- Variable types and type suffixes ($, %, !, #)
- All operators (arithmetic, relational, logical)
- Control flow (IF/THEN/ELSE, FOR/NEXT, WHILE/WEND, GOTO, GOSUB)
- Arrays and DIM statement
- DATA/READ/RESTORE
- DEF FN user-defined functions
- Error handling (ON ERROR, RESUME, ERR, ERL)

**All 50+ built-in functions:**

- Mathematical: SIN, COS, TAN, ATN, LOG, EXP, SQR, ABS, INT, SGN, etc.
- String: LEFT$, RIGHT$, MID$, LEN, CHR$, ASC, INSTR, etc.
- Type conversion: CINT, CSNG, CDBL, STR$, VAL
- System: INKEY$, FRE, POS

### File I/O

**Sequential files:** Fully compatible
- OPEN "O", #1, "FILE.TXT"
- PRINT #1, data
- INPUT #1, variables
- LINE INPUT #1, string$
- CLOSE #1

**Line ending support:** More permissive than MBASIC 5.21
- CP/M MBASIC 5.21: Only recognizes CRLF (`\r\n`)
- This implementation: Recognizes CRLF, LF (`\n`), and CR (`\r`)
- CRLF treated as one line ending (not two)
- Empty lines preserved (e.g., `\n\n` = two lines)
- Cross-platform: Reads files from Linux, Windows, Mac

**CP/M ^Z EOF handling:** Exactly matches MBASIC 5.21
- ^Z (Control-Z, ASCII 26) marks end of file
- Reading stops at first ^Z encountered
- Partial lines before ^Z are returned
- Data after ^Z is ignored
- Tested and verified against real MBASIC 5.21

See [Sequential Files Guide](../../user/sequential-files.md) for complete details.

**Random access files:** Fully compatible
- OPEN "R", #1, "FILE.DAT", record_length
- FIELD #1, width AS field$, ...
- GET #1, record_number
- PUT #1, record_number
- LSET field$ = value$
- RSET field$ = value$

**Binary I/O:** Fully compatible
- MKI$/MKS$/MKD$ - Create binary representations
- CVI/CVS/CVD - Convert from binary
- LOC, LOF, EOF - File position queries

### Program Format

- Line numbers (0-65529)
- Multiple statements per line with `:`
- Line continuation not supported (MBASIC 5.21 behavior)
- Comments with REM or `'`
- All line ending formats (CR, LF, CRLF)

## Intentional Differences

These features differ from CP/M MBASIC by design:

### 1. Hardware-Specific Features

**PEEK/POKE** - Emulated for compatibility

MBASIC 5.21:
```basic
10 POKE 1000, 42      ' Write to memory address 1000
20 X = PEEK(1000)     ' Read from memory address 1000
```

This implementation:
- POKE: Parsed and executes successfully, but performs no operation (no-op)
- PEEK: Returns random integer 0-255 (for RNG seeding compatibility)
- **PEEK does NOT return values written by POKE** - no memory state is maintained
- No access to actual system memory

**Why:** Programs often used `RANDOMIZE PEEK(0)` to seed random numbers. Since we cannot access real memory, PEEK returns random values to support this common pattern.

**Rationale:** Direct memory access is not portable across modern operating systems.

**INP/OUT** - Not implemented

```basic
10 X = INP(255)       ' Read from I/O port - NOT SUPPORTED
20 OUT 128, 42        ' Write to I/O port - NOT SUPPORTED
```

Error: "Illegal function call"

**Rationale:** I/O ports are CP/M hardware-specific and don't exist on modern systems.

**USR** - Not implemented

```basic
10 X = USR0(ARG)      ' Call machine code - NOT SUPPORTED
```

Error: "Illegal function call"

**Rationale:** Machine code calls are architecture-specific (Z80) and not portable.

### 2. File System Differences

**IMPORTANT:** File handling differs between UIs:

**CLI, Tk, and Curses UIs** - Real filesystem access:

MBASIC 5.21 (CP/M):
```basic
OPEN "O", #1, "B:FILE.TXT"    ' Drive letter
```

CLI/Tk/Curses UIs:
```basic
OPEN "O", #1, "FILE.TXT"           ' Current directory
OPEN "O", #1, "/path/to/file.txt"  ' Absolute path
OPEN "O", #1, "../data/file.txt"   ' Relative path
```

**File names:**
- CP/M: 8.3 format required (FILENAME.EXT)
- CLI/Tk/Curses: Any valid OS filename (long names OK)

**Drive letters:**
- CP/M: A:, B:, C:, etc.
- CLI/Tk/Curses: OS-specific paths (/path, C:\path, etc.)

---

**Web UI** - In-memory virtual filesystem:

The Web UI uses a sandboxed in-memory filesystem for security:

```basic
OPEN "O", #1, "DATA.TXT"      ' Simple filename only
OPEN "O", #1, "GAME.BAS"      ' No paths allowed
```

**Storage and persistence:**
- Files stored in server-side memory (sandboxed filesystem per session)
- Files are lost on page refresh or when the session ends
- Settings (not files) persist in browser localStorage by default, or via Redis if configured - see [Web UI Settings](../ui/web/settings.md)
- Note: Session persistence means files survive multiple page operations within the same session, but a page refresh clears the session memory
- No persistent file storage across browser sessions
- 50 file limit, 1MB per file

**File naming:**
- Must be simple names (no slashes, no paths)
- Automatically uppercased by the virtual filesystem (CP/M style)
- 8.3 format recommended but not required
- Examples: DATA.TXT, PROGRAM.BAS, OUTPUT.DAT
- The uppercasing is a programmatic transformation for CP/M compatibility, not evidence of persistent storage

**Limitations:**
- No path support - simple filenames only
- No directories (paths like "folder/file.txt" not supported)
- Cannot save/load files to user's local disk (security restriction)

**Why different:**
- Security: No access to user's real filesystem
- Multi-user: Per-session isolation
- Portability: Works in any browser without filesystem API

### 3. Terminal Differences

**Screen control:**

MBASIC 5.21 was originally written for ASR33 teletypes and had no built-in terminal control codes.

This implementation:
- PRINT uses modern terminal or UI output
- No cursor positioning in program output (not in original MBASIC 5.21)
- No screen control commands available in BASIC programs

**Width statement:**

```basic
10 WIDTH 80              ' Accepted (no-op)
```

Note: WIDTH is parsed for compatibility but performs no operation. Terminal width is controlled by the UI or OS. The "WIDTH LPRINT" syntax is not supported.

### 4. Memory Model

**Memory management:**

MBASIC 5.21:
- Fixed memory allocation (CP/M TPA)
- FRE(0) returns available bytes
- CLEAR statement sets string space

This implementation:
- Dynamic memory allocation (Python)
- FRE(0) returns a reasonable value
- CLEAR works but memory management is automatic

**Practical impact:** None. Programs that ran in CP/M's limited memory will work fine.

### 5. Numeric Precision

**Floating point:**

Both use:
- Single precision: ~7 decimal digits (Microsoft Binary Format)
- Double precision: ~16 decimal digits

Minor differences may occur in the least significant digits due to:
- Z80 vs. modern CPU floating point
- Rounding differences in transcendental functions

**Practical impact:** Negligible for typical BASIC programs.

## Known Limitations

### Not Implemented

1. **Graphics statements** (not in MBASIC 5.21)
   - PSET, LINE, CIRCLE, etc. - These are from GW-BASIC, not MBASIC 5.21

2. **Sound statements** (not in MBASIC 5.21)
   - SOUND, PLAY, BEEP - These are from GW-BASIC, not MBASIC 5.21

3. **Machine language interface**
   - USR, CALL, VARPTR - Architecture-specific

4. **Hardware I/O**
   - INP, OUT, WAIT - Hardware-specific

## Testing Against Real MBASIC

You can verify behavior against authentic MBASIC 5.21 using the included CP/M emulator:

```bash
cd tests/
(cat test.bas && echo "RUN") | timeout 10 tnylpo ../com/mbasic.com
```

See `tests/HOW_TO_RUN_REAL_MBASIC.md` for details.

## Porting Programs to This MBASIC

### From CP/M MBASIC 5.21

**No changes needed** for programs that use:
- Standard BASIC statements and functions
- File I/O (sequential or random)
- Error handling
- Arrays and calculations

**Minor changes needed** for programs that use:
- PEEK/POKE - Remove or replace with variables
- INP/OUT - Remove hardware-specific code
- Drive letters - Update to OS paths
- Terminal control codes - Use UI features instead

### From GW-BASIC or BASICA

GW-BASIC added many features not in MBASIC 5.21:

**Not supported:**
- Graphics (PSET, LINE, CIRCLE, DRAW, etc.)
- Sound (SOUND, PLAY, BEEP)
- ON TIMER/ON KEY
- Many extended statements

**Workaround:** Stick to features common to both:
- Core language (IF/FOR/GOSUB/etc.)
- File I/O
- Math and string functions

### From QuickBASIC

QuickBASIC is significantly more advanced:

**Not supported:**
- Procedures (SUB/FUNCTION with DECLARE)
- Block IF/THEN/ELSEIF/END IF
- SELECT CASE
- DO/LOOP
- Many advanced features

**Workaround:** Translate to MBASIC 5.21 style:
- Use GOSUB instead of SUB
- Use IF/THEN/ELSE instead of SELECT CASE
- Use WHILE/WEND instead of DO/LOOP

## Modern Extensions

**MBASIC-2025** includes optional modern features that are **NOT in MBASIC 5.21**:

- **Debugging Commands**: BREAK, STEP, STACK (CLI only)
- **GUI Interfaces**: Curses, Tk, Web UIs
- **Visual Debugging**: Breakpoints, variable inspection, step visualization
- **Editor Features**: Syntax highlighting, find/replace, undo/redo
- **Enhanced File Handling**: Long filenames, paths, Unicode

See [Extensions Guide](extensions.md) for complete details.

**Important**: Using these extensions makes your program incompatible with original MBASIC 5.21.

## Error Messages

All error messages match MBASIC 5.21:

- "Syntax error"
- "Type mismatch"
- "Overflow"
- "Out of data"
- "Illegal function call"
- "Division by zero"
- "Subscript out of range"
- "File not found"
- And 50+ more...

Error codes (ERR) match MBASIC 5.21 exactly.

## Line Number Limits

Both MBASIC 5.21 and this implementation:
- **Valid range:** 0 to 65529
- **Line 65530+:** Not allowed
- **Renumbering:** RENUM command available

## String Limits

- **Maximum string length:** 255 characters (MBASIC 5.21 limit maintained)
- **String space:** Dynamic allocation (no practical limit)

## Array Limits

- **Maximum dimensions:** Limited by available memory
- **Maximum subscript:** 32767 per dimension
- **OPTION BASE:** 0 or 1 (fully supported)

## File Limits

- **Maximum files open:** 15 (files #1 through #15)
- **File number 0:** Reserved for terminal
- **Record length:** 1 to 32767 bytes for random files

## See Also

- [Features](features.md) - Complete feature list
- [Getting Started](getting-started.md) - Installation and setup
- [Architecture](architecture.md) - Implementation details
- [Language Reference](../common/language/statements/index.md) - BASIC-80 language syntax
