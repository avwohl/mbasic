# Help System Reorganization - Concrete Example

This document shows exactly how existing content would be reorganized into the three-tier structure.

## Current File Mapping

### Files That Move to `docs/help/language/`

**Already in correct location!**
- `docs/help/common/language/` → `docs/help/language/`
  - ✅ `index.md` - Language reference landing page
  - ✅ `operators.md` - Operators reference
  - ✅ `functions/` - 40 function references (already migrated)
  - ✅ `statements/` - 63 statement references (already migrated)
  - ✅ `appendices/` - 3 appendices (error codes, ASCII, math)

**Action**: Just rename directory
```bash
mv docs/help/common/language docs/help/language
```

### Files That Move to `docs/help/mbasic/`

**Currently in `docs/help/common/`**, need to move:

1. **getting-started.md** → `docs/help/mbasic/getting-started.md`
   - About using MBASIC interpreter
   - File formats, running programs
   - Currently mixes UI and implementation

2. **examples.md** → `docs/help/mbasic/examples/index.md`
   - Sample programs to run
   - Implementation-specific examples

**New files to create**:
- `docs/help/mbasic/index.md` - MBASIC overview
- `docs/help/mbasic/architecture.md` - ✅ **CREATED** Interpreter vs compiler
- `docs/help/mbasic/features.md` - What's implemented
- `docs/help/mbasic/compatibility.md` - Compatibility implementations
- `docs/help/mbasic/not-implemented.md` - What's not implemented
- `docs/help/mbasic/file-formats.md` - .BAS files, encoding
- `docs/help/mbasic/optimizations.md` - Semantic analyzer guide

### Files That Stay in `docs/help/ui/{backend}/`

**Already in correct location!**
- `docs/help/ui/curses/` - All curses UI docs (8 files)
- `docs/help/ui/cli/` - CLI docs (to be created)
- `docs/help/ui/tk/` - Tk docs (to be created)

### Files That Are Removed/Consolidated

1. **`docs/help/common/editor-commands.md`** - DELETE
   - UI-specific, doesn't belong in common
   - Content already in `ui/curses/keyboard-commands.md`

2. **`docs/help/common/shortcuts.md`** - DELETE
   - UI-specific, doesn't belong in common
   - Content already in `ui/curses/quick-reference.md`

3. **`docs/help/common/language.md`** - DELETE
   - Duplicate of `language/index.md`
   - Outdated quick reference

4. **`docs/help/common/index.md`** - DELETE
   - Just a redirect, not needed
   - Each UI has its own index

5. **`docs/help/language/functions/`** (old location) - DELETE
   - Orphaned duplicate
   - Real content is in `common/language/functions/`

## Example Content Transformation

### Example 1: getting-started.md (Split into Two Tiers)

**BEFORE** (`docs/help/common/getting-started.md`):
```markdown
# Getting Started with MBASIC

## What is BASIC?
BASIC (Beginner's All-purpose Symbolic Instruction Code)...

## Your First Program
10 PRINT "Hello, World!"
20 END

## How to Enter Programs
See your UI-specific help for how to type programs:
- [Curses UI](ui/curses/editing.md) - Terminal interface
- [Tkinter UI](ui/tk/index.md) - Graphical interface

## Basic Concepts
### Line Numbers
Every line starts with a number...

### Variables
A = 5...
```

**AFTER** - Split into two files:

**Tier 2**: `docs/help/mbasic/getting-started.md` (Implementation)
```markdown
# Getting Started with MBASIC

Welcome! MBASIC is a Python-based interpreter for MBASIC-80.

## What is MBASIC?

MBASIC is a faithful implementation of MBASIC-80 (version 5.21),
the BASIC interpreter used on CP/M systems in the 1980s.

## Features

- ✅ Full BASIC-80 language support
- ✅ Multiple user interfaces (CLI, Curses, Tk)
- ✅ File I/O (.BAS format)
- ⚠️ Compatibility implementations for some features
- ❌ No hardware access (PEEK, POKE, INP, OUT)

See [Features](../help/mbasic/features.md) for complete list.

## Your First Program

Create a file `hello.bas`:
```basic
10 PRINT "Hello, World!"
20 END
```

Run it:
```bash
python3 mbasic hello.bas
```

## Choose Your Interface

MBASIC supports multiple interfaces:
- [CLI](../help/ui/cli/index.md) - Command-line REPL
- [Curses](../help/ui/curses/index.md) - Terminal IDE
- [Tk](../help/ui/tk/index.md) - Graphical IDE

## Learning BASIC

For BASIC language basics, see:
- BASIC-80 Tutorial - Learn the language (tutorial content in help/common/language/)
- [Language Reference](../help/common/language/index.md) - Complete syntax reference
- Example Programs - Working examples (in basic/ directory)

## Next Steps

1. [Choose your interface](../help/ui/cli/index.md)
2. Learn BASIC syntax (see help/common/language/)
3. Try example programs (in basic/ directory)
```

**Tier 1**: `docs/help/language/tutorial/basics.md` (New - Language)
```markdown
# BASIC Language Basics

Learn fundamental BASIC programming concepts.

## Program Structure

BASIC programs consist of numbered lines:
```basic
10 REM This is a comment
20 PRINT "Hello, World!"
30 END
```

## Line Numbers

- Every line starts with a number (1-65535)
- Lines execute in numerical order
- Common practice: increment by 10

## Variables

```basic
10 A = 5          ' Numeric variable
20 B$ = "Hello"   ' String variable ($ suffix)
30 PRINT A, B$
```

### Variable Types

- **Numeric**: A, COUNT, X1
  - Integer: A% (% suffix)
  - Single precision: A! (! suffix, default)
  - Double precision: A# (# suffix)
- **String**: A$, NAME$, TEXT$ ($ suffix required)

See [Data Types](../help/common/language/data-types.md) for details.

## Your First Program

```basic
10 PRINT "Hello, World!"
20 END
```

- Line 10: Outputs text to screen
- Line 20: Ends program

## Next Steps

- Control Flow - IF, FOR, WHILE (see help/common/language/statements/)
- Input/Output - INPUT, PRINT (see help/common/language/statements/)
- Subroutines - GOSUB, DEF FN (see help/common/language/statements/)
```

### Example 2: Curses Index (Add Cross-Tier Links)

**BEFORE** (`docs/help/ui/curses/index.md`):
```markdown
# MBASIC Curses UI Help

## Getting Started
- [Quick Reference](quick-reference.md)
- [Getting Started](getting-started.md)

## Language Reference
- [BASIC Language](../help/common/language/index.md)
- [Examples](../help/common/examples.md)
```

**AFTER** (`docs/help/ui/curses/index.md`):
```markdown
# MBASIC Curses UI Help

Welcome to the MBASIC terminal-based IDE!

## 📘 Curses UI Guide

Learn how to use the curses interface:
- [Quick Reference](quick-reference.md) - All keyboard shortcuts
- [Getting Started](getting-started.md) - First time using curses UI
- [Keyboard Commands](keyboard-commands.md) - Complete keyboard reference
- [Editing Programs](editing.md) - How to write and edit
- [Running Programs](running.md) - Execute and debug
- [File Operations](files.md) - Save and load

## 📗 MBASIC Interpreter

About this BASIC interpreter:
- [About MBASIC](../help/mbasic/index.md) - What is MBASIC?
- [Getting Started](../help/mbasic/getting-started.md) - First steps
- [Features](../help/mbasic/features.md) - What's implemented
- Example Programs - Working examples (in basic/ directory)
- Tutorial - Learn BASIC (see help/common/language/)

## 📕 BASIC-80 Language Reference

Complete BASIC-80 language documentation:
- [Language Overview](../help/common/language/index.md) - Language reference home
- [Statements](../help/common/language/statements/index.md) - 63 statements
- [Functions](../help/common/language/functions/index.md) - 40 functions
- [Operators](../help/common/language/operators.md) - Arithmetic, logical, relational
- [Appendices](../help/common/language/appendices/index.md) - Error codes, ASCII, math

## Help Navigation

| Key | Action |
|-----|--------|
| **↑/↓** | Scroll |
| **Tab** | Next link |
| **Enter** | Follow link |
| **U** | Go back |
| **ESC/Q** | Close help |
```

### Example 3: Language Function with Cross-Tier Link

**BEFORE** (`docs/help/common/language/functions/peek.md`):
```markdown
# PEEK

## Implementation Note

ℹ️ **Compatibility Implementation**: PEEK returns random value 0-255.

**Historical Reference**: Documentation below is from MBASIC 5.21 manual.

---

## Syntax
PEEK(I)
...
```

**AFTER** (`docs/help/language/functions/peek.md`):
```markdown
# PEEK

## Implementation Note

ℹ️ **Compatibility Implementation**: This Python-based interpreter cannot
access memory addresses. PEEK returns a random value (0-255) to support
programs that use PEEK for random number seeding.

See [MBASIC Compatibility Notes](../help/mbasic/compatibility.md#peek) for details.

**Historical Reference**: The documentation below is preserved from the
original MBASIC 5.21 manual for historical reference.

---

## Syntax

PEEK(I)

## Purpose

To examine a memory location.
...
```

### Example 4: New MBASIC Compatibility Docs

**NEW FILE**: `docs/help/mbasic/compatibility.md`
```markdown
# MBASIC Compatibility Notes

This Python-based interpreter cannot access hardware directly. Some BASIC-80
features have compatibility implementations or are not implemented.

## Compatibility Implementations

Features that work differently but provide reasonable compatibility:

### PEEK(addr) {#peek}

**Original behavior**: Read byte from memory address

**MBASIC behavior**: Returns random value (0-255)

**Why**: Most BASIC programs use PEEK to seed random number generators
(e.g., `RANDOMIZE PEEK(0)`). Returning random values provides reasonable
compatibility for this use case.

**Example**:
```basic
10 RANDOMIZE PEEK(0)    ' Seed RNG with "random" value
20 PRINT RND
```

See also: [PEEK function reference](../help/common/language/functions/peek.md)

### RANDOMIZE

**Original behavior**: Seed with real-time clock or user input

**MBASIC behavior**: Seeds with system time

**Why**: Provides reasonable random seeding without user interaction.

## Not Implemented Features

Features that are parsed but perform no operation:

### Hardware Access

Cannot access hardware from Python interpreter:

- **POKE addr, value** - Write to memory (no-op)
- **OUT port, value** - Write to I/O port (no-op)
- **WAIT port, mask[, xor]** - Wait on I/O port (no-op)
- **INP(port)** - Read from I/O port (returns 0)

See also: [Not Implemented Features](../help/mbasic/not-implemented.md)

### Machine Code

Cannot execute machine code from Python:

- **CALL addr[(args)]** - Call machine code subroutine (no-op)
- **USR(x)** - Call machine code function (returns 0)

### Cassette Tape

Obsolete hardware not implemented:

- **CLOAD** - Load from cassette tape
- **CSAVE** - Save to cassette tape

These were explicitly excluded in some MBASIC 5.21 variants (e.g., DEC VT180).

## Partially Implemented

Features with limited implementation:

### LPRINT

**Original behavior**: Print to line printer (parallel port)

**MBASIC behavior**: Prints to stdout or file (depending on UI)

**Note**: No actual printer support, but output can be redirected.

## Full Compatibility

Most BASIC-80 features work exactly as in the original:

- ✅ All control flow (FOR, WHILE, IF, GOSUB)
- ✅ All mathematical functions
- ✅ String manipulation
- ✅ File I/O (sequential and random)
- ✅ Arrays and variables
- ✅ Error handling (ON ERROR GOTO, RESUME)

See [Features](../help/mbasic/features.md) for complete list.
```

## File Organization After Reorganization

```
docs/help/
├── language/                      # TIER 1: Language Reference
│   ├── index.md                  # ✅ Already exists (move from common/language/)
│   ├── operators.md              # ✅ Already exists
│   ├── functions/                # ✅ Already exists (40 files)
│   ├── statements/               # ✅ Already exists (63 files)
│   └── appendices/               # ✅ Already exists (3 files)
│
├── mbasic/                        # TIER 2: MBASIC Implementation
│   ├── index.md                  # 🆕 Create new
│   ├── getting-started.md        # ✏️ Move from common/, rewrite
│   ├── architecture.md           # ✅ CREATED - Interpreter vs compiler
│   ├── features.md               # 🆕 Create new
│   ├── compatibility.md          # 🆕 Create new (content from NOT_IMPLEMENTED.md)
│   ├── not-implemented.md        # ✏️ Move from docs/dev/NOT_IMPLEMENTED.md
│   ├── file-formats.md           # 🆕 Create new
│   ├── optimizations.md          # 🆕 Create new (from compiler docs)
│   ├── examples/
│   │   └── index.md              # ✏️ Move from common/examples.md
│   └── tutorial/
│       ├── index.md              # 🆕 Create new
│       ├── basics.md             # 🆕 Create new (content from getting-started.md)
│       ├── control-flow.md       # 🆕 Create new
│       └── input-output.md       # 🆕 Create new
│
└── ui/                            # TIER 3: UI-Specific
    ├── cli/                       # 🆕 Create directory
    │   ├── index.md              # 🆕 Create new
    │   ├── commands.md           # 🆕 Create new
    │   └── editing.md            # 🆕 Create new
    │
    ├── curses/                    # ✅ Already exists
    │   ├── index.md              # ✏️ Update with 3-tier links
    │   ├── getting-started.md    # ✅ Keep
    │   ├── keyboard-commands.md  # ✅ Keep
    │   ├── editing.md            # ✅ Keep
    │   ├── running.md            # ✅ Keep
    │   ├── debugger.md           # ✅ Keep
    │   ├── files.md              # ✅ Keep
    │   └── quick-reference.md    # ✅ Keep
    │
    └── tk/                        # 🆕 Create directory
        ├── index.md              # 🆕 Create new
        ├── menu-reference.md     # 🆕 Create new
        └── toolbar.md            # 🆕 Create new
```

**Legend**:
- ✅ Already exists, no changes needed
- ✏️ Move and update
- 🆕 Create new
- ❌ Delete

## Files to Delete

```bash
# Delete UI-specific content from common/
rm docs/help/common/editor-commands.md
rm docs/help/common/shortcuts.md
rm docs/help/common/language.md
rm docs/help/common/index.md

# Delete orphaned old structure
rm -rf docs/help/language/  # Old location, duplicate

# Delete examples directory (move to mbasic/)
rm -rf docs/help/examples/
```

## Migration Script

```bash
#!/bin/bash
# migrate_help_structure.sh

# 1. Move language reference to top level
mv docs/help/common/language docs/help/language

# 2. Create MBASIC docs directory
mkdir -p docs/help/mbasic/{examples,tutorial}

# 3. Move implementation-specific content
mv docs/help/common/getting-started.md docs/help/mbasic/getting-started.md.old
mv docs/help/common/examples.md docs/help/mbasic/examples/index.md.old

# 4. Create CLI docs directory
mkdir -p docs/help/ui/cli

# 5. Delete duplicates and UI-specific content from common/
rm docs/help/common/editor-commands.md
rm docs/help/common/shortcuts.md
rm docs/help/common/language.md
rm docs/help/common/index.md

# 6. Delete orphaned directories
rm -rf docs/help/language/functions  # Old duplicate
rm -rf docs/help/examples/           # Move to mbasic/

# 7. Delete common/ directory (should be empty now)
rmdir docs/help/common/

echo "Migration complete! Now create new content files."
```

## Next Steps After Reorganization

1. **Create MBASIC tier content** (Tier 2):
   - Write `mbasic/index.md`
   - Write `mbasic/features.md`
   - Write `mbasic/compatibility.md`
   - Rewrite `mbasic/getting-started.md`
   - Create tutorial files

2. **Create CLI docs** (Tier 3):
   - Write `ui/cli/index.md`
   - Write `ui/cli/commands.md`
   - Write `ui/cli/editing.md`

3. **Update curses docs** (Tier 3):
   - Update `ui/curses/index.md` with 3-tier structure
   - Update links throughout

4. **Update HelpWidget**:
   - Add multi-context support
   - Test navigation between tiers

5. **Update all backends**:
   - Update CLI to use 3-tier help
   - Update curses to use 3-tier help
   - Update Tk to use 3-tier help

This reorganization provides clear separation while maintaining all existing content!
