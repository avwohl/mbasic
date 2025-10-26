# Not Implemented Features

Features from MBASIC 5.21 that are not implemented or have compatibility implementations.

## Hardware/System Access (Not Applicable)

These features access physical hardware or memory and cannot be implemented in a Python interpreter:

### Functions

**PEEK(addr)** - Read byte from memory address
- **Status**: Compatibility implementation
- **Behavior**: Returns random value 0-255
- **Note**: Most programs use PEEK to seed RNG, so random values provide reasonable compatibility
- **Help**: [docs/help/common/language/functions/peek.md] - needs implementation note

**INP(port)** - Read byte from I/O port
- **Status**: Not implemented
- **Behavior**: Always returns 0
- **Note**: Cannot access hardware ports from Python
- **Help**: [docs/help/common/language/functions/inp.md] - needs implementation note

**USR(x)** - Call machine language routine
- **Status**: Not implemented
- **Behavior**: Always returns 0
- **Note**: Cannot execute machine code from Python
- **Help**: [docs/help/common/language/functions/usr.md] - needs implementation note

### Statements

**POKE addr, value** - Write byte to memory address
- **Status**: Not implemented
- **Behavior**: Parsed but does nothing
- **Note**: Cannot write to memory from Python
- **Help**: [docs/help/common/language/statements/poke.md] - needs implementation note

**OUT port, value** - Send byte to I/O port
- **Status**: Not implemented
- **Behavior**: Parsed but does nothing
- **Note**: Cannot access hardware ports from Python
- **Help**: [docs/help/common/language/statements/out.md] - needs implementation note

**CALL addr[(args)]** - Call machine language subroutine
- **Status**: Not implemented
- **Behavior**: Parsed but does nothing
- **Note**: Cannot execute machine code from Python
- **Help**: [docs/help/common/language/statements/call.md] - needs implementation note

**WAIT port, mask[, xor]** - Wait for I/O port condition
- **Status**: Not implemented
- **Behavior**: Parsed but does nothing
- **Note**: Cannot access hardware ports from Python
- **Help**: [docs/help/common/language/statements/wait.md] - needs implementation note

**DEF USR** - Define machine language function address
- **Status**: Not implemented
- **Note**: Related to USR() function
- **Help**: May need note in relevant docs

## Printer Output (UI-Specific)

**LPRINT** - Print to line printer
- **Status**: Partially implemented
- **Behavior**: Parses and may output to stdout or file depending on UI
- **Note**: No physical printer support; output redirectable
- **Help**: [docs/help/common/language/statements/lprint-lprint-using.md] - needs note

**LPRINT USING** - Formatted print to printer
- **Status**: Partially implemented
- **Behavior**: Same as LPRINT
- **Help**: Same file as LPRINT

**LPOS(x)** - Get printer head position
- **Status**: May not be implemented
- **Behavior**: Check basic_builtins.py
- **Help**: [docs/help/common/language/functions/lpos.md] - may need note

**LLIST** - List program to printer
- **Status**: Check if implemented
- **Help**: [docs/help/common/language/statements/llist.md] - may need note

## Cassette Tape (Obsolete)

**CLOAD** - Load from cassette tape
- **Status**: Not implemented (obsolete hardware)
- **Note**: Explicitly noted as "NOT INCLUDED IN DEC VT180 VERSION" in manual
- **Help**: [docs/help/common/language/statements/cload.md] - already notes VT180

**CSAVE** - Save to cassette tape
- **Status**: Not implemented (obsolete hardware)
- **Note**: Explicitly noted as "NOT INCLUDED IN DEC VT180 VERSION" in manual
- **Help**: [docs/help/common/language/statements/csave.md] - already notes VT180

**CLOAD?** - Verify cassette load
- **Status**: Not implemented (obsolete)

**CLOAD*** - Merge from cassette
- **Status**: Not implemented (obsolete)

**CSAVE*** - Save to cassette in ASCII
- **Status**: Not implemented (obsolete)

## Special Functions

**VARPTR** - Get variable memory address
- **Status**: Check if implemented
- **Behavior**: If implemented, returns placeholder value
- **Note**: Memory addresses not meaningful in Python
- **Help**: [docs/help/common/language/functions/varptr.md] - may need note

## UI-Specific Commands (CLI Only)

These are specific to the command-line UI and not applicable to curses/tk/visual UIs:

**AUTO** - Automatic line numbering
- **Status**: CLI-only
- **Note**: Curses UI has different editor
- **Help**: Already marked as CLI-only in categorization

**DELETE** - Delete line range
- **Status**: CLI-only
- **Help**: Already marked as CLI-only

**EDIT** - Line editor
- **Status**: CLI-only
- **Help**: Already marked as CLI-only

**RENUM** - Renumber lines
- **Status**: Implemented in curses UI (Ctrl+E)
- **Note**: Different invocation in different UIs
- **Help**: Should note UI differences

## Documentation Status

### ✅ Completed: Implementation Notes Added

All hardware/system function help files now have implementation notes:

1. ✅ **peek.md** - Compatibility implementation note (returns random 0-255)
2. ✅ **inp.md** - Not implemented note (returns 0)
3. ✅ **usr.md** - Not implemented note (returns 0)
4. ✅ **poke.md** - Not implemented note (no operation)
5. ✅ **out.md** - Not implemented note (no operation)
6. ✅ **call.md** - Not implemented note (no operation)
7. ✅ **wait.md** - Not implemented note (no operation)

### ✅ All Documentation Complete

All printer and special function help files now have implementation notes:

1. ✅ **lprint-lprint-using.md** - Printer output not implemented
2. ✅ **lpos.md** - Printer head position not implemented
3. ✅ **varptr.md** - Memory address access not implemented (file rewritten)
4. ✅ **llist.md** - Printer listing not implemented

### Historical Reference
Cassette functions already noted as VT180-excluded, keep as historical reference.

## Summary

All required implementation notes have been added to help documentation. Users will now see clear explanations for features that are not implemented due to:
- Obsolete hardware (printers, cassette tapes, I/O ports)
- Incompatibility with Python (memory addresses, machine code)
- Modern alternatives available

## Template for Implementation Notice

Add to top of affected help files:

```markdown
## Implementation Note

⚠️ **Not Implemented**: This feature requires direct hardware/memory access
and is not implemented in this Python-based interpreter.

**Behavior**: [Returns 0 / Returns random value / No operation performed]

**Why**: [Cannot access hardware ports / Cannot write to memory / etc.]

**Historical Reference**: The documentation below is preserved from the
original MBASIC 5.21 manual for historical reference.

---
```

For compatibility implementations like PEEK:

```markdown
## Implementation Note

ℹ️ **Compatibility Implementation**: PEEK returns a random value between 0-255.

**Why**: Most BASIC programs use PEEK to seed random number generators. This
compatibility implementation provides suitable random values for that purpose.

**Note**: Does not read actual memory addresses (not applicable in Python).

---
```
