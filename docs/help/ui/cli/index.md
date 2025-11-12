---
title: MBASIC CLI Help
type: guide
ui: cli
description: Help system for the MBASIC command-line interface
keywords: [help, cli, command-line, repl, interface]
---

# MBASIC CLI Help

Command-line interface for MBASIC-2025. Type `HELP <topic>` for specific help or `HELP SEARCH <keyword>` to search all content.

## 🎮 Games Library

Browse and run classic BASIC games:

- **[Games Library](../../../library/games/index.md)** - 113 classic CP/M era games ready to run!

## 📘 CLI Interface

The CLI provides a classic MBASIC command-line interface with direct mode and program mode.

**Common Commands:**
- LIST - Show program
- RUN - Execute program
- LOAD "file.bas" - Load program
- SAVE "file.bas" - Save program
- NEW - Clear program
- AUTO - Auto line numbering
- RENUM - Renumber lines
- SYSTEM - Exit MBASIC

**Debugging:**
- Use the Tk or Curses UI for full debugging support (breakpoints, stepping, stack viewing)
- CLI supports basic program execution and direct mode testing

## 📗 MBASIC Interpreter

About the BASIC interpreter:

- [MBASIC Index](../../mbasic/index.md) - Overview and navigation
- [Getting Started](../../mbasic/getting-started.md) - Your first BASIC program
- [Features](../../mbasic/features.md) - What's implemented
- [Compatibility](../../mbasic/compatibility.md) - MBASIC 5.21 differences
- [Architecture](../../mbasic/architecture.md) - How MBASIC works

## 📙 MBASIC Compiler

Compile BASIC programs to native CP/M executables:

- **[Compiler Guide](../../common/compiler/index.md)** - Generate .COM files for 8080 or Z80 systems (100% complete!)
- [Features](../../common/compiler/features.md) - What the compiler supports
- [Getting Started](../../common/compiler/getting-started.md) - Compile your first program
- [Generated Code](../../common/compiler/generated-code.md) - Understanding compiler output

## 📕 BASIC-80 Language Reference

Complete BASIC language documentation:

- [Language Overview](../../common/language/index.md)
- [Statements](../../common/language/statements/index.md) - All 63 statements
- [Functions](../../common/language/functions/index.md) - All 40 functions
- [Operators](../../common/language/operators.md)
- [Error Codes](../../common/language/appendices/error-codes.md) - All 68 error codes
- [ASCII Table](../../common/language/appendices/ascii-codes.md) - Character codes

---

## Using CLI Help

**Show main help:**
```
HELP
```

**Get help on specific topic:**
```
HELP PRINT
HELP FOR
HELP architecture
```

**Search all help:**
```
HELP SEARCH loop
HELP SEARCH file
```

## Quick Start

**Run MBASIC in CLI mode:**
```bash
mbasic --ui cli
```

**Note:** MBASIC supports multiple interfaces (CLI, Curses, Tk, Web). See [Features](../../mbasic/features.md) for details on all available UIs.

**Load and run a program:**
```
Ok
LOAD "MYPROGRAM.BAS"
RUN
```

**Direct mode (no line numbers):**
```
Ok
PRINT "Hello, World!"
Hello, World!
Ok
```

**Program mode (with line numbers):**
```
Ok
10 PRINT "Hello"
20 PRINT "World"
30 END
RUN
Hello
World
Ok
```

---

## Beyond the Interpreter

The CLI runs programs in **interpreter mode**. To compile BASIC programs to native CP/M executables:

**[MBASIC Compiler →](../../common/compiler/index.md)** - Generate native .COM files for 8080 or Z80 systems (100% complete!)

---

Type `HELP <topic>` for more information on any topic listed above.
