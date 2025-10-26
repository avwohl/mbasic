---
title: MBASIC CLI Help
type: guide
ui: cli
description: Help system for the MBASIC command-line interface
keywords: [help, cli, command-line, repl, interface]
---

# MBASIC CLI Help

Command-line interface for MBASIC 5.21. Type `HELP <topic>` for specific help or `HELP SEARCH <keyword>` to search all content.

## 📘 CLI Interface

How to use the command-line interface:

- [Commands](commands.md) - All CLI commands (LIST, RUN, LOAD, SAVE, etc.)
- [Line Editing](editing.md) - AUTO, DELETE, EDIT, RENUM
- [Running Programs](running.md) - Direct mode and program mode
- [File Operations](files.md) - Loading and saving programs

## 📗 MBASIC Interpreter

About the BASIC interpreter:

- [Getting Started](../../mbasic/getting-started.md) - Your first BASIC program
- [Architecture](../../mbasic/architecture.md) - How MBASIC works
- [Features](../../mbasic/features.md) - What's implemented
- [Compatibility](../../mbasic/compatibility.md) - MBASIC 5.21 differences
- [Examples](../../mbasic/examples/index.md) - Sample programs

## 📕 BASIC-80 Language Reference

Complete BASIC language documentation:

- [Language Overview](../../language/index.md)
- [Statements](../../language/statements/index.md) - All 63 statements
- [Functions](../../language/functions/index.md) - All 40 functions
- [Operators](../../language/operators.md)
- [Appendices](../../language/appendices/index.md) - Error codes, ASCII, math functions

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

**Run MBASIC:**
```bash
python3 mbasic.py
```

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

Type `HELP <topic>` for more information on any topic listed above.
